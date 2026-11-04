"""Safe, workspace-scoped tools. Exercise 1 lives here."""

from pathlib import Path
from adapters.sandbox.runner import run_command, run_pytest, safe_path


class RepairTools:
    """Concrete, workspace-scoped tool adapter used by the repair harness."""

    def __init__(self, workspace, github_research=None):
        """Store the workspace, change list, and optional GitHub research adapter."""
        self.workspace = Path(workspace)
        self.changed_files = []
        self.github_research = github_research

    def read_file(self, path):
        """Read UTF-8 text from a path that stays inside the workspace."""
        # TODO 1: resolve path with safe_path(self.workspace, path), then return UTF-8 text.
        raise NotImplementedError("TODO: implement read_file")

    def edit_file(self, path, content):
        """Write UTF-8 text safely and record the changed relative path once."""
        # TODO 2: resolve safely, write UTF-8 text, and remember the relative path once.
        raise NotImplementedError("TODO: implement edit_file")

    def run_tests(self):
        """Delegate the complete test suite to the Docker-backed runner."""
        # TODO 3: return run_pytest(self.workspace). Do not use subprocess here.
        raise NotImplementedError("TODO: implement run_tests")

    def run_command(self, command):
        """Supplied advanced capability: sandboxed repository inspection only."""
        return run_command(self.workspace, command)

    def search_github(self, query):
        """Return bounded GitHub research evidence when the option is enabled."""
        if self.github_research is None:
            return {"ok": False, "output": "GitHub research is disabled for this repair.", "sources": []}
        return self.github_research.search_code(query)
