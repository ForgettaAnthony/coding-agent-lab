"""Optional OpenAI Responses API adapter."""

import os


class OpenAIClient:
    """Adapt the optional OpenAI Responses API to the model port."""

    def __init__(self, model=None):
        """Select an API model, with an environment-configurable default."""
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5-nano")

    def chat(self, messages):
        """Submit the conversation to OpenAI and return its output text."""
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI requires OPENAI_API_KEY.")
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError("Install optional OpenAI support: pip install -r requirements-openai.txt") from error
        response = OpenAI().responses.create(model=self.model, input=messages)
        return response.output_text
