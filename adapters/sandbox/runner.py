"""Create disposable workspaces and test them inside Docker."""

from pathlib import Path
import shutil
import subprocess
import tempfile

from core.models import TestResult


DOCKER_IMAGE = "coding-agent-lab-runner"
WORKSPACE_ROOT = Path.home() / ".cache" / "coding-agent-lab"


def create_workspace(source: str | Path) -> Path:
    """Copy a project to a new disposable directory under the user's home."""
    source_path = Path(source).expanduser().resolve(strict=True)
    if not source_path.is_dir():
        raise ValueError(f"Project source is not a directory: {source_path}")

    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    workspace = Path(
        tempfile.mkdtemp(prefix=f"{source_path.name}-", dir=WORKSPACE_ROOT)
    )
    shutil.copytree(source_path, workspace, dirs_exist_ok=True, symlinks=True)
    workspace.chmod(workspace.stat().st_mode | 0o555)
    return workspace


def run_tests(workspace: str | Path) -> TestResult:
    """Run project tests in a network-disabled, read-only Docker mount."""
    workspace_path = Path(workspace).expanduser().resolve(strict=True)
    if not workspace_path.is_dir():
        raise ValueError(f"Workspace is not a directory: {workspace_path}")

    command = [
        "docker",
        "run",
        "--rm",
        "--network=none",
        "--user",
        "10001:10001",
        "--mount",
        f"type=bind,source={workspace_path},target=/workspace,readonly",
        "--workdir",
        "/workspace",
        DOCKER_IMAGE,
        "python",
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            shell=False,
        )
    except OSError as error:
        return TestResult(False, f"Could not start Docker: {error}", -1)

    output = "\n".join(
        part.rstrip() for part in (completed.stdout, completed.stderr) if part
    )
    return TestResult(completed.returncode == 0, output, completed.returncode)
