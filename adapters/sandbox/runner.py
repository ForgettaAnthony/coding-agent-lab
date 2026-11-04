"""Create disposable eval-project workspaces and run their tests in Docker only."""

import json
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVALS_ROOT = ROOT / "evals"
IMAGE = "coding-agent-lab-runner"
INSPECTION_COMMANDS = frozenset({"find", "grep", "ls"})
MAX_COMMAND_LENGTH = 300
MAX_DISPLAY_OUTPUT = 8_000


def resolve_eval_project(project_path):
    """Return one direct project folder under evals and reject every other host path."""
    requested = Path(project_path)
    if requested.is_absolute():
        source = requested.resolve()
    elif requested.parts and requested.parts[0] == "evals":
        source = (ROOT / requested).resolve()
    else:
        source = (EVALS_ROOT / requested).resolve()
    if source.parent != EVALS_ROOT.resolve() or not source.is_dir():
        raise ValueError("Project must be a direct directory under evals/, for example evals/arithmetic.")
    return source


def list_eval_projects():
    """Return the direct instructor-provided project folders available to the UI."""
    return sorted(path.name for path in EVALS_ROOT.iterdir() if path.is_dir())


def create_workspace(project_path):
    """Copy one approved evals project into a disposable workspace for repair."""
    source = resolve_eval_project(project_path)
    destination = Path(tempfile.mkdtemp(prefix="repair-agent-")) / "project"
    shutil.copytree(source, destination)
    return destination


def safe_path(workspace, relative_path):
    """Resolve a path and reject any path that escapes the workspace."""
    workspace = Path(workspace).resolve()
    candidate = (workspace / relative_path).resolve()
    if candidate != workspace and workspace not in candidate.parents:
        raise ValueError("Path must stay inside the project workspace")
    return candidate


def run_pytest(workspace):
    """Run supplied project tests without running project code on the host."""
    workspace = Path(workspace).resolve()
    command = ["docker", "run", "--rm", "--network", "none", "--read-only",
               "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m", "--pids-limit", "128",
               "--memory", "256m", "--cpus", "1", "--cap-drop", "ALL",
               "--security-opt", "no-new-privileges", "-v", f"{workspace}:/workspace:ro",
               "-w", "/workspace", IMAGE, "pytest", "-q", "-p", "no:cacheprovider"]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=30)
        return {"passed": completed.returncode == 0, "output": completed.stdout + completed.stderr,
                "returncode": completed.returncode}
    except FileNotFoundError:
        return {"passed": False, "output": "Docker is not installed. Follow README setup step 4.", "returncode": 127}
    except subprocess.TimeoutExpired:
        return {"passed": False, "output": "Test run timed out after 30 seconds.", "returncode": 124}


def run_command(workspace, command):
    """Run one allowlisted inspection command inside the same restricted container.

    The command is parsed into arguments; it is never sent to a host shell.
    It can inspect the read-only project but cannot replace edit_file or run_tests.
    """
    if not isinstance(command, str) or not command.strip():
        return {"ok": False, "output": "Command must be a non-empty string.", "returncode": 2}
    if len(command) > MAX_COMMAND_LENGTH:
        return {"ok": False, "output": "Command is too long.", "returncode": 2}
    try:
        argv = shlex.split(command)
    except ValueError as error:
        return {"ok": False, "output": f"Invalid command syntax: {error}", "returncode": 2}
    if not argv or argv[0] not in INSPECTION_COMMANDS:
        allowed = ", ".join(sorted(INSPECTION_COMMANDS))
        return {"ok": False, "output": f"Only inspection commands are allowed: {allowed}.", "returncode": 2}
    if argv[0] == "find" and any(argument in {"-exec", "-execdir", "-ok", "-okdir", "-delete"} for argument in argv[1:]):
        return {"ok": False, "output": "That find action is not allowed.", "returncode": 2}

    workspace = Path(workspace).resolve()
    docker_command = ["docker", "run", "--rm", "--network", "none", "--read-only",
                      "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m", "--pids-limit", "128",
                      "--memory", "256m", "--cpus", "1", "--cap-drop", "ALL",
                      "--security-opt", "no-new-privileges", "-v", f"{workspace}:/workspace:ro",
                      "-w", "/workspace", IMAGE, *argv]
    try:
        completed = subprocess.run(docker_command, capture_output=True, text=True, timeout=10)
        output = (completed.stdout + completed.stderr)[:MAX_DISPLAY_OUTPUT]
        if len(completed.stdout + completed.stderr) > MAX_DISPLAY_OUTPUT:
            output += "\n[output truncated for the trace]"
        return {"ok": completed.returncode == 0, "output": output, "returncode": completed.returncode}
    except FileNotFoundError:
        return {"ok": False, "output": "Docker is not installed. Follow README setup step 4.", "returncode": 127}
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "Command timed out after 10 seconds.", "returncode": 124}


def result_text(result):
    """Format a runner result for display in a trace or user interface."""
    return json.dumps(result, indent=2)
