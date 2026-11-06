# Task 8: Final demonstration

[Back to the activity overview](../README.md)

Demonstrate these five points:

1. Start from the original `evals/arithmetic` project and show its sandboxed failing test.
2. Run a scripted or live repair through the terminal and show the trace: read, reproduce, edit, verify.
3. Show that the repaired files are in a copied workspace and that the original evaluation project is unchanged.
4. Show your deterministic tests for safe paths and the repair loop.
5. Explain why the repair loop does not directly import the web page, Docker command, or Ollama client.

## Submission checklist

- [ ] All source files in the target structure were created by your group.
- [ ] `python -m pytest -q` passes.
- [ ] Evaluation-project code runs only in Docker.
- [ ] The agent requires test reproduction before editing.
- [ ] The agent accepts only strict JSON actions and has a fixed stop budget.
- [ ] `python main.py repair evals/arithmetic --provider scripted` completes a repair.
- [ ] The original `evals/` projects are unchanged after every repair.
- [ ] `python main.py ui` exposes only the five supplied projects.
- [ ] Your Git history has a commit after each completed task.

When you are finished, you will have practiced a central software-engineering idea for AI systems: the model proposes a next step, while ordinary, testable program code controls what can happen, records evidence, and decides whether the result is accepted.

## Where to go next

Return to the [activity overview](../README.md), complete the submission
checklist, and prepare your demonstration.
