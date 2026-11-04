"""Gradio presentation adapter. Exercise 3 lives here."""

import shutil
import tempfile
from pathlib import Path
import gradio as gr

from bootstrap import build_repair_service
from adapters.sandbox.runner import list_eval_projects


def repair(project_path):
    """Run one repair and format its trace, files, tests, and download for Gradio."""
    # TODO 6: call build_repair_service().repair(project_path), then return FOUR values:
    # trace text, changed-code text, test output text, and a downloadable .zip path.
    raise NotImplementedError("TODO: connect the UI to the application service")


def create_demo():
    """Build and return the lab's Gradio presentation interface."""
    with gr.Blocks(title="Python Repair Agent Lab") as demo:
        gr.Markdown("# Python Repair Agent Lab\nSelect an instructor-provided buggy project and watch the agent work.")
        case = gr.Dropdown(list_eval_projects(), value="arithmetic", label="Instructor project (evals/)")
        run = gr.Button("Run repair", variant="primary")
        trace = gr.Textbox(label="Agent execution trace", lines=14)
        changed = gr.Textbox(label="Modified code", lines=14)
        tests = gr.Textbox(label="Sandboxed pytest result", lines=10)
        download = gr.File(label="Repaired project (.zip)")
        run.click(repair, inputs=case, outputs=[trace, changed, tests, download])
    return demo
