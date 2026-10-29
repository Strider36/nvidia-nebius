"""LLM client service supporting OpenRouter and Nebius Token Factory.

Uses OpenAI-compatible SDK with bounded tokens, timeouts, and safe error handling.
"""

from typing import Any, Dict, List, Optional, Tuple
import openai
from openai import OpenAI
from app.config import settings

_UNSET = object()


class LLMService:
    """Service for interacting with OpenRouter / Nebius inference."""

    def __init__(
        self,
        api_key: Any = _UNSET,
        base_url: Optional[str] = None,
        model_id: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        self._explicit_key = api_key is not _UNSET
        self.api_key: Optional[str] = settings.api_key if api_key is _UNSET else api_key
        self.base_url: str = base_url if base_url is not None else settings.base_url
        self.model_id: str = model_id if model_id is not None else settings.model_id
        self.timeout: float = timeout if timeout is not None else settings.request_timeout

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
        """Check if client is initialized with an API key."""
        return self._client is not None and bool(self.api_key)

    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.2,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Generate response from the model.

        Returns:
            Tuple of (response_text, error_message).
            If successful, (text, None).
            If failure, (None, error_str). Never fabricates responses.
        """
        # Only refresh from global settings if this instance wasn't explicitly constructed with custom key
        if not self._explicit_key and not self.api_key and settings.api_key:
            self.api_key = settings.api_key
            self.base_url = settings.base_url
            self.model_id = settings.model_id
            self._init_client()

        if not self.is_available:
            return None, "LLM API key is not configured. Please set OPENROUTER_API_KEY or NEBIUS_API_KEY in your .env file."

        # Bounded token limits
        token_limit = min(max_tokens or settings.max_output_tokens, settings.max_output_tokens)

        # Prepare messages payload
        payload_messages: List[Dict[str, str]] = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})

        # Enforce bounded input lengths
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
