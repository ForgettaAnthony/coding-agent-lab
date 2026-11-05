"""The agent harness: model-facing repair loop, state, tool dispatch, and stop policy."""

from core.models import RepairResult
from core.ports import ChatModelPort, RepairToolsPort, TrajectoryObserverPort
from core.prompts import (
    ASSISTANT_ROLE, SYSTEM_ROLE, USER_ROLE, build_case_request, build_system_prompt,
    build_tool_result, parse_model_action,
)


class RepairAgent:
    """Coordinate bounded model decisions and repair-tool observations."""

    def __init__(self, client: ChatModelPort, max_steps=12, research_enabled=False, observer: TrajectoryObserverPort | None = None):
        """Store model, budget, research flag, and an optional outer trajectory observer."""
        self.client = client
        self.max_steps = max_steps
        self.research_enabled = research_enabled
        self.observer = observer

    def _record(self, event_name, payload):
        """Send one lifecycle event to the optional observer without owning its implementation."""
        if self.observer is not None:
            self.observer.record(event_name, payload)

    def _finish(self, result):
        """Record the terminal repair state and return the unchanged repair result."""
        self._record("repair_finished", {
            "passed": result.passed,
            "summary": result.summary,
            "changed_files": result.changed_files,
            "test_result": result.test_result,
            "steps": len(result.trace),
        })
        return result

    def build_initial_messages(self, case_name, files):
        """Create the initial system policy and case-specific model context."""
        # TODO 4: return system + user messages using build_system_prompt(self.research_enabled)
        # and build_case_request(case_name, files). Use SYSTEM_ROLE and USER_ROLE.
        raise NotImplementedError("TODO: implement build_initial_messages")

    def run(self, case_name, files, tools: RepairToolsPort):
        """Run the bounded model-to-tool loop and return a repair result."""
        # TODO 5: own only the LLM/tool conversation loop. Call self.client.chat(messages), use
        # parse_model_action(reply) to enforce the JSON action contract, then
        # dispatch the five tools, append assistant + TOOL_RESULT messages, and keep a trace.
        # Do not permit search_github until at least one read_file call has succeeded.
        # Include an action's optional public "summary" in the trace; it never grants a new capability.
        # Emit repair_started, model_response, and tool_result through self._record; use self._finish
        # for every terminal RepairResult. The observer is optional: never import Langfuse in this file.
        # Return RepairResult when tests pass, an invalid response arrives, or max_steps is exhausted.
        raise NotImplementedError("TODO: implement RepairAgent.run")
