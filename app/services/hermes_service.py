"""Hermes Agent Adapter Service for Aegis AI.

Integrates Hermes Agent CLI as an optional agent reasoning backend.
Communicates via isolated subprocess executing:
  hermes chat --query-file <file> --format stream-json --oneshot --in <workspace>

Enforces:
1. Sandboxed execution within the configured workspace.
2. Direct connection to Ollama Nemotron (http://127.0.0.1:11434/v1) or Cloud provider.
3. Strict isolation: zero silent fallback from local to cloud.
4. Human approval lifecycle: toolsets are constrained, forcing actions to be
   proposed via structured <<<PROPOSE_PATCH>>> and <<<PROPOSE_COMMAND>>> tags.
5. Comprehensive timeout and cancellation handling.
"""

import json
import logging
import os
import subprocess
import tempfile
import time
from typing import Any, Dict, Iterator, List, Optional, Tuple

import httpx

from app.config import settings

logger = logging.getLogger("aegis.hermes")


class HermesService:
    """Manages Hermes Agent invocation, configuration, and JSONL stream decoding."""

    def __init__(self) -> None:
        self.cached_version: Optional[str] = None
        self._last_version_check: float = 0.0

    def get_status(self) -> Dict[str, Any]:
        """Inspect and report the live availability of the Hermes Agent binary and inference backend."""
        bin_path = settings.hermes_bin_path
        exists = os.path.exists(bin_path)

        version = self.cached_version
        now = time.time()
        if exists and (version is None or (now - self._last_version_check > 300)):
            try:
                res = subprocess.run(
                    [bin_path, "--version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5.0,
                    encoding="utf-8",
                    errors="replace",
                )
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        if "Hermes Agent" in line or "v" in line:
                            version = line.strip()
                            break
                    if not version and res.stdout.strip():
                        version = res.stdout.strip().splitlines()[0]
                    self.cached_version = version
                    self._last_version_check = now
            except Exception as e:
                logger.warning(f"Failed to query Hermes version: {e}")

        # Check if Ollama is accessible
        ollama_ready = False
        try:
            r = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=1.5)
            if r.status_code == 200:
                tags = r.json().get("models", [])
                ollama_ready = any(
                    settings.ollama_model in m.get("name", "") for m in tags
                ) or len(tags) > 0
        except Exception:
            ollama_ready = False

        is_available = exists and settings.hermes_enabled
        msg = None
        if not exists:
            msg = f"Hermes binary not found at '{bin_path}'."
        elif not settings.hermes_enabled:
            msg = "Hermes Agent backend is disabled in configuration."
        elif settings.active_provider == "ollama" and not ollama_ready:
            msg = f"Hermes is ready, but local Ollama model '{settings.ollama_model}' is unreachable."
        else:
            msg = f"Hermes Agent is ready using {settings.active_provider} inference."

        return {
            "enabled": settings.hermes_enabled,
            "available": is_available,
            "binary_path": bin_path,
            "version": version or "0.22.5",
            "active_provider": settings.active_provider,
            "ollama_ready": ollama_ready,
            "message": msg,
        }

    def _compose_prompt(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """Compose system directives and conversation turns into a coherent query for Hermes."""
        parts: List[str] = []
        if system_prompt:
            parts.append(f"### SYSTEM INSTRUCTIONS & CONSTRAINTS\n{system_prompt.strip()}\n")

        parts.append("### CONVERSATION HISTORY\n")
        for m in messages:
            role = m.get("role", "user").capitalize()
            content = m.get("content", "").strip()
            parts.append(f"**{role}**: {content}\n")

        parts.append("\n### YOUR DIRECTIVE\nProvide the next assistant response conforming strictly to the system directives above. If proposing changes, use <<<PROPOSE_PATCH>>> or <<<PROPOSE_COMMAND>>> tags.")
        return "\n".join(parts)

    def _build_command(self, query_file_path: str, provider: str) -> List[str]:
        """Assemble the hermes chat command arguments with workspace confinement and anti-fallback settings."""
        bin_path = settings.hermes_bin_path
        cmd = [
            bin_path,
            "chat",
            "--query-file",
            query_file_path,
        ]

        if provider == "ollama":
            ollama_v1 = f"{settings.ollama_base_url.rstrip('/')}/v1"
            cmd.extend([
                "--provider", "custom",
                "--base-url", ollama_v1,
                "-m", settings.ollama_model,
            ])
        else:
            cmd.extend([
                "--provider", "custom",
                "--base-url", settings.base_url,
                "-m", settings.model_id,
            ])
            if settings.api_key:
                cmd.extend(["--api-key", settings.api_key])

        # Execution constraints
        cmd.extend([
            "--format", "stream-json",
            "--oneshot",
            "--in", str(settings.workspace_path),
            "--toolsets", "",  # Restrict tool execution so actions flow through Aegis approvals
            "--ignore-user-config",
        ])
        return cmd

    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        provider: str = "ollama",
        timeout: Optional[float] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Non-streaming generation via Hermes Agent subprocess.

        Returns:
            Tuple[Optional[str], Optional[str]]: (response_text, error_message)
        """
        if not os.path.exists(settings.hermes_bin_path):
            return None, f"Hermes binary not found at '{settings.hermes_bin_path}'."

        timeout_sec = timeout or settings.hermes_timeout
        composed = self._compose_prompt(messages, system_prompt)

        # Write prompt safely to temporary file to avoid shell escaping issues
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt", encoding="utf-8") as tf:
                tf.write(composed)
                temp_file = tf.name

            cmd = self._build_command(temp_file, provider)
            logger.info(f"Invoking Hermes Agent (provider={provider}, timeout={timeout_sec}s)")

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(settings.workspace_path),
            )

            tokens: List[str] = []
            final_text: Optional[str] = None
            start_time = time.time()

            try:
                if proc.stdout is not None:
                    for line in proc.stdout:
                        if time.time() - start_time > timeout_sec:
                            proc.terminate()
                            try:
                                proc.wait(timeout=2.0)
                            except Exception:
                                proc.kill()
                            return None, f"Hermes Agent timed out after {timeout_sec:.0f}s."

                        line_str = line.strip() if isinstance(line, str) else line.decode("utf-8", errors="replace").strip()
                        if not line_str:
                            continue
                        try:
                            data = json.loads(line_str)
                            evt_type = data.get("type")
                            if evt_type == "text":
                                tokens.append(data.get("text", ""))
                            elif evt_type == "result":
                                final_text = data.get("text")
                        except Exception:
                            pass

                proc.wait(timeout=5.0)
            except Exception as e:
                if hasattr(proc, "terminate"):
                    proc.terminate()
                try:
                    if hasattr(proc, "wait"):
                        proc.wait(timeout=2.0)
                except Exception:
                    if hasattr(proc, "kill"):
                        proc.kill()
                return None, f"Hermes subprocess communication error: {str(e)}"

            if proc.returncode != 0:
                stderr_output = ""
                if proc.stderr and hasattr(proc.stderr, "read"):
                    stderr_output = proc.stderr.read()
                err_msg = str(stderr_output).strip() or f"Hermes exited with status {proc.returncode}."
                # Anti-fallback guarantee: return explicit error
                return None, f"Hermes execution error: {err_msg}"

            result = final_text if final_text is not None else "".join(tokens)
            if not result.strip():
                return None, "Hermes Agent completed without generating response text."

            return result, None

        except Exception as e:
            logger.error(f"Failed to execute Hermes Agent: {e}")
            return None, f"Hermes invocation failed: {str(e)}"
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass

    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        provider: str = "ollama",
        timeout: Optional[float] = None,
    ) -> Iterator[str]:
        """Streaming generator yielding text token chunks via Hermes Agent subprocess.

        Yields:
            str: Token chunks emitted by Hermes.
        """
        if not os.path.exists(settings.hermes_bin_path):
            yield f"⚠️ Hermes Agent error: Binary not found at '{settings.hermes_bin_path}'."
            return

        timeout_sec = timeout or settings.hermes_timeout
        composed = self._compose_prompt(messages, system_prompt)

        temp_file = None
        proc = None
        try:
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt", encoding="utf-8") as tf:
                tf.write(composed)
                temp_file = tf.name

            cmd = self._build_command(temp_file, provider)
            logger.info(f"Streaming Hermes Agent (provider={provider}, timeout={timeout_sec}s)")

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(settings.workspace_path),
            )

            start_time = time.time()
            if proc.stdout is not None:
                for line in proc.stdout:
                    if time.time() - start_time > timeout_sec:
                        proc.terminate()
                        yield f"\n\n*(Hermes generation timed out after {timeout_sec:.0f}s)*"
                        return

                    line_str = line.strip() if isinstance(line, str) else line.decode("utf-8", errors="replace").strip()
                    if not line_str:
                        continue
                    try:
                        data = json.loads(line_str)
                        if data.get("type") == "text":
                            chunk = data.get("text", "")
                            if chunk:
                                yield chunk
                    except Exception:
                        pass

            proc.wait(timeout=5.0)
            if proc.returncode != 0:
                stderr_output = ""
                if proc.stderr and hasattr(proc.stderr, "read"):
                    stderr_output = proc.stderr.read()
                err_msg = str(stderr_output).strip() or f"Hermes exited with status {proc.returncode}"
                yield f"\n\n*(Hermes execution notice: {err_msg})*"

        except GeneratorExit:
            # Client disconnected or AbortController fired
            logger.info("Hermes stream aborted by client.")
            if proc and hasattr(proc, "poll") and proc.poll() is None:
                if hasattr(proc, "terminate"):
                    proc.terminate()
                try:
                    if hasattr(proc, "wait"):
                        proc.wait(timeout=1.0)
                except Exception:
                    if hasattr(proc, "kill"):
                        proc.kill()
            raise
        except Exception as e:
            logger.error(f"Hermes stream error: {e}")
            yield f"\n\n*(Hermes stream error: {str(e)})*"
        finally:
            if proc and hasattr(proc, "poll") and proc.poll() is None:
                if hasattr(proc, "terminate"):
                    proc.terminate()
                try:
                    if hasattr(proc, "wait"):
                        proc.wait(timeout=1.0)
                except Exception:
                    if hasattr(proc, "kill"):
                        proc.kill()
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass


# Singleton instance
hermes_service = HermesService()
