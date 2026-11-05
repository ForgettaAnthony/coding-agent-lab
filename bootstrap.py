"""Composition root: selects an outer model adapter and wires it to the core."""

import os

from core.repair_agent import RepairAgent
from core.repair_service import RepairService
from adapters.models.ollama import OllamaClient
from adapters.models.openai import OpenAIClient
from adapters.models.vertex_gemini import VertexGeminiClient
from adapters.research.github_research import GitHubResearch
from adapters.sandbox.runner import create_workspace
from adapters.sandbox.repair_tools import RepairTools


def load_model_temperature(temperature=None):
    """Load a CLI override or MODEL_TEMPERATURE before an adapter is constructed."""
    configured = temperature if temperature is not None else os.getenv("MODEL_TEMPERATURE")
    if configured is None:
        return None
    try:
        configured = float(configured)
    except (TypeError, ValueError) as error:
        raise ValueError("Model temperature must be a number from 0 to 2.") from error
    if not 0 <= configured <= 2:
        raise ValueError("Model temperature must be between 0 and 2.")
    return configured


def build_model_client(provider=None, model=None, temperature=None):
    """Create the configured outer model adapter without exposing it to the core."""
    provider = (provider or os.getenv("MODEL_PROVIDER", "ollama")).lower()
    temperature = load_model_temperature(temperature)
    if provider == "ollama":
        return OllamaClient(model=model, temperature=temperature)
    if provider in {"vertex", "vertex-gemini"}:
        return VertexGeminiClient(model=model, temperature=temperature)
    if provider == "openai":
        return OpenAIClient(model=model, temperature=temperature)
    raise ValueError("MODEL_PROVIDER must be 'ollama', 'vertex', or 'openai'.")


def build_github_research(enabled=None):
    """Create the opt-in GitHub research adapter when explicit consent is configured."""
    if enabled is None:
        enabled = os.getenv("ENABLE_GITHUB_RESEARCH", "").lower() in {"1", "true", "yes"}
    if not enabled:
        return None
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GitHub research requires GITHUB_TOKEN when research is enabled.")
    return GitHubResearch(token)


def build_trajectory_observer(enabled=None):
    """Create an opt-in Langfuse observer without making it a default dependency."""
    if enabled is None:
        enabled = os.getenv("ENABLE_LANGFUSE", "").lower() in {"1", "true", "yes"}
    if not enabled:
        return None
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        raise ValueError("Langfuse requires LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY when enabled.")
    from adapters.observability.langfuse import LangfuseTrajectoryObserver
    return LangfuseTrajectoryObserver()


def build_repair_service(model=None, provider=None, temperature=None, enable_github_research=None,
                         enable_langfuse=None):
    """Wire the agent use case to selected model, sandbox, research, and observability adapters."""
    research = build_github_research(enable_github_research)
    observer = build_trajectory_observer(enable_langfuse)
    agent = RepairAgent(
        build_model_client(provider, model, temperature), research_enabled=research is not None, observer=observer,
    )
    return RepairService(agent, create_workspace, lambda workspace: RepairTools(workspace, research))
