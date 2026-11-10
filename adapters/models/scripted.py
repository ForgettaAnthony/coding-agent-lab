"""Deterministic answer-card chat client for tests and demonstrations."""


class ScriptedClient:
    """Return predefined responses in their supplied order."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self._next_response = 0

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Return the next response, or fail when the script is exhausted."""
        if self._next_response >= len(self._responses):
            raise RuntimeError("ScriptedClient has no responses remaining")

        response = self._responses[self._next_response]
        self._next_response += 1
        return response
