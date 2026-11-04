"""Optional Langfuse adapter for recording one repair-agent trajectory."""

import logging


LOGGER = logging.getLogger(__name__)


class LangfuseTrajectoryObserver:
    """Translate generic harness events into a Langfuse agent observation tree."""

    def __init__(self, client=None):
        """Use an injected client for tests or create Langfuse's configured SDK client."""
        if client is None:
            try:
                from langfuse import get_client
            except ImportError as error:
                raise RuntimeError("Install requirements-langfuse.txt to enable Langfuse observability.") from error
            client = get_client()
        self.client = client
        self.root = None

    def record(self, event_name, payload):
        """Record one best-effort lifecycle event without affecting the repair workflow."""
        try:
            if event_name == "repair_started":
                self.root = self.client.start_observation(
                    name="python-repair-agent", as_type="agent", input=payload,
                    metadata={"component": "core.RepairAgent"},
                )
            elif self.root is None:
                return
            elif event_name == "model_response":
                child = self.root.start_observation(
                    name="model-response", as_type="generation", input={"step": payload["step"]},
                    output={"reply": payload["reply"]},
                )
                child.end()
            elif event_name == "tool_result":
                child = self.root.start_observation(
                    name=payload["tool_name"] or "unsupported-tool", as_type="tool",
                    input={"step": payload["step"], "action": payload["action"]},
                    output={"observation": payload["observation"]},
                )
                child.end()
            elif event_name == "repair_finished":
                self.root.update(output=payload)
                self.root.end()
                self.root = None
                self.client.flush()
        except Exception as error:  # Observability must not break a student repair run.
            LOGGER.warning("Langfuse event '%s' was not recorded: %s", event_name, error)
