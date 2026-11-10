"""Local Ollama chat client for optional live repair demonstrations."""

import json
import math
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_OLLAMA_MODEL = "qwen2.5-coder:7b"
OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/chat"


class OllamaClient:
    """Return chat responses from a local Ollama server."""

    def __init__(
        self,
        model: str | None = None,
        temperature: float = 0.0,
        timeout: float = 300.0,
    ) -> None:
        selected_model = model or os.environ.get("OLLAMA_MODEL")
        self.model = selected_model or DEFAULT_OLLAMA_MODEL
        if not math.isfinite(temperature) or temperature < 0:
            raise ValueError("Temperature must be a finite non-negative number")
        self.temperature = temperature
        self.timeout = timeout

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Send prepared messages and return the unvalidated reply text."""
        payload = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "format": "json",
                "options": {"temperature": self.temperature},
            }
        ).encode("utf-8")
        request = Request(
            OLLAMA_CHAT_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                envelope = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise RuntimeError(
                f"Ollama returned HTTP {error.code}: {error.reason}"
            ) from error
        except URLError as error:
            raise RuntimeError(
                f"Could not reach the local Ollama server: {error.reason}"
            ) from error
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RuntimeError("Ollama returned an invalid response envelope") from error

        message = envelope.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise RuntimeError("Ollama response did not contain message content")
        return content
