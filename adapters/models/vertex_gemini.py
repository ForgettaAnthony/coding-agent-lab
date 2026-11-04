"""Optional Vertex AI Gemini adapter. Install requirements-vertex.txt to use it."""

import os


class VertexGeminiClient:
    """Adapt the optional Vertex AI Gemini SDK to the model port."""

    def __init__(self, model=None, project=None, location=None):
        """Select Vertex model and credential context from arguments or environment."""
        self.model = model or os.getenv("VERTEX_MODEL", "gemini-2.5-flash")
        self.project = project or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location or os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    def chat(self, messages):
        """Flatten harness messages and return a deterministic Gemini response."""
        if not self.project:
            raise ValueError("Vertex requires GOOGLE_CLOUD_PROJECT.")
        try:
            from google import genai
            from google.genai import types
        except ImportError as error:
            raise RuntimeError("Install optional Vertex support: pip install -r requirements-vertex.txt") from error
        system = "\n".join(message["content"] for message in messages if message["role"] == "system")
        contents = "\n\n".join(f"{message['role'].upper()}: {message['content']}"
                               for message in messages if message["role"] != "system")
        client = genai.Client(vertexai=True, project=self.project, location=self.location)
        response = client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system, temperature=0),
        )
        return response.text
