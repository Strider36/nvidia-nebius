"""LLM client service supporting Dual-Provider Inference:
1. Local Ollama HTTP API (e.g. NVIDIA Nemotron 3.5 Bolt E4B)
2. Cloud inference (Nebius Token Factory / OpenRouter via OpenAI-compatible SDK)

Preserves exact response contracts, bounded token limits, explicit timeouts,
strict isolation (no silent fallbacks), and sanitized error handling.
"""

import json
from typing import Any, Dict, List, Optional, Tuple
import httpx
import openai
from openai import OpenAI
from app.config import settings

_UNSET = object()


class LLMService:
    """Service for interacting with Ollama and OpenRouter/Nebius inference."""

    def __init__(
        self,
        api_key: Any = _UNSET,
        base_url: Optional[str] = None,
        model_id: Optional[str] = None,
        timeout: Optional[float] = None,
        provider: Optional[str] = None,
        ollama_base_url: Optional[str] = None,
        ollama_model: Optional[str] = None,
        ollama_timeout: Optional[float] = None,
    ) -> None:
        self._explicit_key = api_key is not _UNSET
        self.api_key: Optional[str] = settings.api_key if api_key is _UNSET else api_key
        self.base_url: str = base_url if base_url is not None else settings.base_url
        self.model_id: str = model_id if model_id is not None else settings.model_id
        self.timeout: float = timeout if timeout is not None else settings.request_timeout

        self.provider: Optional[str] = provider
        self.ollama_base_url: str = (
            ollama_base_url if ollama_base_url is not None else settings.ollama_base_url
        ).rstrip("/")
        self.ollama_model: str = (
            ollama_model if ollama_model is not None else settings.ollama_model
        )
        self.ollama_timeout: float = (
            ollama_timeout if ollama_timeout is not None else settings.ollama_timeout
        )

        self._client: Optional[OpenAI] = None
        self._init_client()

    def _init_client(self) -> None:
        """Initialize OpenAI client with appropriate provider headers."""
        if self.api_key:
            headers = {}
            if "openrouter" in (self.base_url or "").lower():
                headers = {
                    "HTTP-Referer": "http://127.0.0.1:8000",
                    "X-Title": "Aegis AI",
                }
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=0,
                default_headers=headers or None,
            )
        else:
            self._client = None

    @property
    def is_available(self) -> bool:
        """Check if active or explicit provider is configured and ready."""
        target_provider = self.provider
        if not target_provider:
            if self._explicit_key:
                target_provider = "cloud"
            else:
                target_provider = settings.active_provider

        if target_provider == "ollama":
            return bool(self.ollama_base_url and self.ollama_model)
        return self._client is not None and bool(self.api_key)

    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.2,
        provider: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Generate response from the selected model provider.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            system_prompt: Optional system prompt to inject.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            provider: Optional explicit provider override ('ollama' or 'cloud').

        Returns:
            Tuple of (response_text, error_message).
            If successful: (text, None).
            If failure: (None, error_str). Never fabricates responses.
            Strict isolation: Local failures never trigger silent cloud fallbacks.
        """
        # Determine target provider for this invocation
        target_provider = provider or self.provider
        if not target_provider:
            if self._explicit_key:
                target_provider = "cloud"
            else:
                target_provider = settings.get_provider_snapshot()

        clean_provider = target_provider.strip().lower()

        if clean_provider == "ollama":
            return self._generate_ollama(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        else:
            return self._generate_cloud(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )

    def _prepare_payload_messages(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str],
    ) -> List[Dict[str, str]]:
        """Prepare message list with system prompt and bounded input length enforcement."""
        payload_messages: List[Dict[str, str]] = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})

        total_len = sum(len(m.get("content", "")) for m in messages)
        if total_len > settings.max_input_length:
            running_len = 0
            trimmed_messages: List[Dict[str, str]] = []
            for msg in reversed(messages):
                msg_len = len(msg.get("content", ""))
                if running_len + msg_len <= settings.max_input_length:
                    trimmed_messages.insert(0, msg)
                    running_len += msg_len
                else:
                    break
            payload_messages.extend(trimmed_messages)
        else:
            payload_messages.extend(messages)

        return payload_messages

    def _generate_ollama(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.2,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Execute local inference against Ollama /api/chat endpoint."""
        # Refresh dynamic settings if not explicitly configured on this instance
        if not self.ollama_base_url:
            self.ollama_base_url = settings.ollama_base_url.rstrip("/")
        if not self.ollama_model:
            self.ollama_model = settings.ollama_model

        if not self.ollama_base_url or not self.ollama_model:
            return None, "Ollama is not configured. Please set OLLAMA_BASE_URL and OLLAMA_MODEL in your .env file."

        payload_messages = self._prepare_payload_messages(messages, system_prompt)
        token_limit = min(max_tokens or settings.max_output_tokens, settings.max_output_tokens)

        request_body = {
            "model": self.ollama_model,
            "messages": payload_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": token_limit,
            },
        }

        url = f"{self.ollama_base_url}/api/chat"
        client_timeout = httpx.Timeout(self.ollama_timeout, connect=5.0)

        try:
            with httpx.Client(timeout=client_timeout) as client:
                resp = client.post(url, json=request_body)

            if resp.status_code == 404:
                return (
                    None,
                    f"Model Not Found: Model '{self.ollama_model}' not found in Ollama at {self.ollama_base_url}. Pull it using 'ollama pull {self.ollama_model}'.",
                )

            if resp.is_error:
                detail = ""
                try:
                    err_json = resp.json()
                    detail = err_json.get("error", resp.text[:200])
                except Exception:
                    detail = resp.text[:200]
                return None, f"Ollama HTTP Error {resp.status_code}: {detail}"

            try:
                data = resp.json()
            except Exception as json_err:
                return None, f"Malformed Response: Invalid JSON returned from Ollama ({str(json_err)})."

            msg = data.get("message", {})
            content = msg.get("content", "")
            if not content and "thinking" in msg:
                content = msg.get("thinking", "")

            if not content:
                return None, "Ollama returned an empty response."

            return content, None

        except httpx.ConnectError:
            return (
                None,
                f"Connection Error: Unable to reach Ollama at {self.ollama_base_url}. Ensure Ollama service is running.",
            )
        except httpx.ConnectTimeout:
            return (
                None,
                f"Connection Timeout: Could not connect to Ollama at {self.ollama_base_url} within 5.0s.",
            )
        except (httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout):
            return (
                None,
                f"Request Timeout: Ollama inference exceeded {self.ollama_timeout}s timeout limit.",
            )
        except httpx.HTTPError as e:
            return None, f"Ollama HTTP Error: {str(e)}."
        except Exception as e:
            return None, f"Unexpected Ollama Error: {str(e)}."

    def _generate_cloud(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.2,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Execute cloud inference using OpenAI-compatible SDK (Nebius/OpenRouter)."""
        # Only refresh from global settings if this instance wasn't explicitly constructed with custom key
        if not self._explicit_key and not self.api_key and settings.api_key:
            self.api_key = settings.api_key
            self.base_url = settings.base_url
            self.model_id = settings.model_id
            self._init_client()

        if not (self._client is not None and bool(self.api_key)):
            return (
                None,
                "LLM API key is not configured. Please set OPENROUTER_API_KEY or NEBIUS_API_KEY in your .env file.",
            )

        token_limit = min(max_tokens or settings.max_output_tokens, settings.max_output_tokens)
        payload_messages = self._prepare_payload_messages(messages, system_prompt)

        def _call_model(target_model: str):
            return self._client.chat.completions.create(
                model=target_model,
                messages=payload_messages,
                max_tokens=token_limit,
                temperature=temperature,
            )

        try:
            target_model = self.model_id
            try:
                response = _call_model(target_model)
            except openai.NotFoundError as nf_err:
                if ":free" in target_model:
                    fallback_model = target_model.replace(":free", "")
                    response = _call_model(fallback_model)
                else:
                    raise nf_err

            choice = response.choices[0]
            content = choice.message.content
            if not content and hasattr(choice.message, "reasoning"):
                content = choice.message.reasoning

            return content, None

        except openai.AuthenticationError as e:
            return None, f"Authentication Error: Invalid API key or unauthorized access ({str(e)})."
        except openai.RateLimitError as e:
            return None, f"Rate Limit Exceeded: Quota or rate limit exceeded ({str(e)})."
        except openai.APITimeoutError:
            return None, f"Request Timeout: Inference exceeded {self.timeout}s limit."
        except openai.APIConnectionError as e:
            return None, f"Connection Error: Unable to reach endpoint at {self.base_url} ({str(e)})."
        except openai.APIError as e:
            return None, f"API Error: {str(e)}."
        except Exception as e:
            return None, f"Unexpected Model Error: {str(e)}."


# Global singleton instance
llm_service = LLMService()

