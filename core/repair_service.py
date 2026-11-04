"""Use case: repair one instructor-provided project in a disposable workspace."""

from dataclasses import replace
from pathlib import Path

from core.ports import ToolsFactory, WorkspaceFactory


class RepairService:
    """Application use case for repairing one selected instructor-provided project."""

    def __init__(self, agent, workspace_factory: WorkspaceFactory, tools_factory: ToolsFactory):
        """Receive the policy and outer factories required by this use case."""
        self.agent = agent
        self.workspace_factory = workspace_factory
        self.tools_factory = tools_factory

    def repair(self, project_path):
        """Create a workspace for one approved project path and invoke the repair harness."""
        workspace = self.workspace_factory(project_path)
        files = sorted(str(path.relative_to(workspace)) for path in Path(workspace).rglob("*.py"))
        project_name = Path(project_path).name
        result = self.agent.run(project_name, files, self.tools_factory(workspace))
        return replace(result, workspace=str(workspace))
