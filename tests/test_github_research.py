"""Checkpoint tests for the optional GitHub research adapter."""

import json

from adapters.research.github_research import GitHubResearch


class FakeResponse:
    """Small context-manager response used instead of a real HTTP call."""

    def __init__(self, payload):
        """Store an API payload as encoded response bytes."""
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        """Return this fake response to the adapter's context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Do not suppress an exception raised inside the context manager."""
        return False

    def read(self):
        """Return the encoded API payload."""
        return self.payload


def test_github_research_returns_small_citable_evidence(monkeypatch):
    """Verify the adapter returns source URL, repository, path, and snippet."""
    captured_requests = []
    payload = {"incomplete_results": False, "items": [{
        "html_url": "https://github.com/example/project/blob/main/helpers.py",
        "repository": {"full_name": "example/project"},
        "path": "helpers.py",
        "text_matches": [{"fragment": "def normalize_name(value):"}],
    }]}
    monkeypatch.setattr("adapters.research.github_research.request.urlopen",
                        lambda api_request, timeout: (captured_requests.append(api_request) or FakeResponse(payload)))
    result = GitHubResearch("test-token", max_requests=1).search_code("normalize_name language:Python")
    assert result["ok"] is True
    assert result["sources"] == [{
        "url": "https://github.com/example/project/blob/main/helpers.py",
        "repository": "example/project",
        "path": "helpers.py",
        "snippet": "def normalize_name(value):",
    }]
    assert captured_requests[0].get_header("Authorization") == "Bearer test-token"


def test_github_research_enforces_its_request_budget():
    """Verify an exhausted research budget blocks another external request."""
    result = GitHubResearch("test-token", max_requests=0).search_code("normalize_name language:Python")
    assert result == {"ok": False, "output": "GitHub research request budget exhausted.", "sources": []}
