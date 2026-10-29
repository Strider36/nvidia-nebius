"""Tests for LLM service and Nebius client."""

from unittest.mock import MagicMock, patch
import openai
import pytest
from app.services.llm_service import LLMService


def test_unconfigured_llm_service():
    """Verify LLMService returns a descriptive error when API key is missing."""
    service = LLMService(api_key=None)
    assert not service.is_available
    text, err = service.generate([{"role": "user", "content": "Hello"}])
    assert text is None
    assert "not configured" in err.lower()


def test_successful_inference_mocked():
    """Verify mock inference generation works with OpenAI response format."""
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Aegis AI standing by."
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    service = LLMService(api_key="mock-key", base_url="https://mock.nebius.com/v1/")
    service._client = mock_client

    text, err = service.generate([{"role": "user", "content": "Status report"}])
    assert err is None
    assert text == "Aegis AI standing by."
    mock_client.chat.completions.create.assert_called_once()


def test_llm_service_timeout_handling():
    """Verify timeouts are caught and reported cleanly."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = openai.APITimeoutError(request=MagicMock())

    service = LLMService(api_key="mock-key")
    service._client = mock_client

    text, err = service.generate([{"role": "user", "content": "Compute large task"}])
    assert text is None
    assert "timeout" in err.lower()


def test_llm_service_auth_error_handling():
    """Verify auth errors are caught cleanly."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = openai.AuthenticationError(
        message="Invalid credentials", response=MagicMock(status_code=401), body=None
    )

    service = LLMService(api_key="invalid-key")
    service._client = mock_client

    text, err = service.generate([{"role": "user", "content": "Test"}])
    assert text is None
    assert "authentication error" in err.lower()


def test_successful_inference_stream_mocked():
    """Verify mock inference stream yields tokens incrementally."""
    chunk1 = MagicMock()
    chunk1.choices = [MagicMock(delta=MagicMock(content="Hello "))]
    chunk2 = MagicMock()
    chunk2.choices = [MagicMock(delta=MagicMock(content="World!"))]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = iter([chunk1, chunk2])

    service = LLMService(api_key="mock-key", base_url="https://mock.nebius.com/v1/")
    service._client = mock_client

    tokens = list(service.generate_stream([{"role": "user", "content": "Hi"}], provider="cloud"))
    assert tokens == ["Hello ", "World!"]


def test_unconfigured_llm_service_stream():
    """Verify generate_stream raises descriptive error when API key is unconfigured."""
    service = LLMService(api_key=None, provider="cloud")
    with pytest.raises(RuntimeError) as exc_info:
        list(service.generate_stream([{"role": "user", "content": "Hi"}], provider="cloud"))
    assert "not configured" in str(exc_info.value).lower()


def test_llm_service_stream_auth_error_handling():
    """Verify auth errors during streaming raise descriptive RuntimeError."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = openai.AuthenticationError(
        message="Invalid credentials", response=MagicMock(status_code=401), body=None
    )

    service = LLMService(api_key="invalid-key")
    service._client = mock_client

    with pytest.raises(RuntimeError) as exc_info:
        list(service.generate_stream([{"role": "user", "content": "Hi"}], provider="cloud"))
    assert "authentication error" in str(exc_info.value).lower()


