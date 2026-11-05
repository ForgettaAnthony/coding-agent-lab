"""Public checks for the temperature configuration used by the empirical extension."""

import argparse
import json

import pytest

import bootstrap
from adapters.models.ollama import OllamaClient
from main import temperature_argument


class FakeHTTPResponse:
    """Provide the small context-manager response surface used by the Ollama adapter."""

    def __enter__(self):
        """Return this fake response while the adapter reads it."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """End the fake response context without suppressing errors."""
        return False

    def read(self):
        """Return one successful Ollama chat response as bytes."""
        return b'{"message": {"content": "{}"}}'


def test_temperature_argument_accepts_the_shared_range():
    """Verify the CLI accepts a portable temperature used by the provider adapters."""
    assert temperature_argument("0") == 0.0
    assert temperature_argument("0.8") == 0.8
    assert temperature_argument("2") == 2.0


def test_temperature_argument_rejects_an_invalid_value():
    """Verify the CLI rejects values outside the documented experiment range."""
    with pytest.raises(argparse.ArgumentTypeError, match="between 0 and 2"):
        temperature_argument("2.1")


def test_bootstrap_passes_temperature_to_the_selected_adapter(monkeypatch):
    """Verify the composition root carries configuration to an outer model adapter."""
    captured = {}

    class CapturingOllamaClient:
        """Capture model construction arguments without contacting a provider."""

        def __init__(self, model=None, temperature=None):
            """Store the configuration that bootstrap supplies."""
            captured["model"] = model
            captured["temperature"] = temperature

    monkeypatch.setattr(bootstrap, "OllamaClient", CapturingOllamaClient)
    bootstrap.build_model_client(provider="ollama", model="test-model", temperature=0.8)
    assert captured == {"model": "test-model", "temperature": 0.8}


def test_ollama_client_sends_an_explicit_temperature(monkeypatch):
    """Verify the Ollama adapter includes temperature when the experiment sets it."""
    captured = {}

    def fake_urlopen(request, timeout):
        """Capture the outgoing JSON and return a minimal successful response."""
        captured["payload"] = json.loads(request.data.decode())
        captured["timeout"] = timeout
        return FakeHTTPResponse()

    monkeypatch.setattr("adapters.models.ollama.request.urlopen", fake_urlopen)
    response = OllamaClient(model="test-model", base_url="http://example.test", temperature=0.8).chat([])
    assert response == "{}"
    assert captured["payload"]["options"] == {"temperature": 0.8}
    assert captured["timeout"] == 120
