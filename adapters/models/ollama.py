"""Small adapter for the local Ollama HTTP API."""

import json
import os
from urllib import request


class OllamaClient:
    """Adapt Ollama's local HTTP chat API to the model port."""

    def __init__(self, model=None, base_url=None):
        """Select a configured model and base URL with local defaults."""
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
        self.base_url = (base_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")

    def chat(self, messages):
        """Send conversation messages to Ollama and return its text response."""
        payload = json.dumps({"model": self.model, "messages": messages, "stream": False}).encode()
        req = request.Request(self.base_url + "/api/chat", data=payload,
                              headers={"Content-Type": "application/json"})
        with request.urlopen(req, timeout=120) as response:
            return json.loads(response.read())["message"]["content"]
