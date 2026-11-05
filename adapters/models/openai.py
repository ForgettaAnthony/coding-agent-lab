"""Optional OpenAI Responses API adapter."""

import os


class OpenAIClient:
    """Adapt the optional OpenAI Responses API to the model port."""

    def __init__(self, model=None, temperature=None):
        """Select an API model, with an environment-configurable default."""
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5-nano")
        self.temperature = temperature

    def chat(self, messages):
        """Submit the conversation to OpenAI and return its output text."""
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI requires OPENAI_API_KEY.")
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError("Install optional OpenAI support: pip install -r requirements-openai.txt") from error
        request_arguments = {"model": self.model, "input": messages}
        if self.temperature is not None:
            request_arguments["temperature"] = self.temperature
        response = OpenAI().responses.create(**request_arguments)
        return response.output_text
