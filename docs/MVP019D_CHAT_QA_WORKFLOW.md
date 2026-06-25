# MVP-019D Chat QA Workflow

Status: MVP-019D chat/QA workflow wiring

## Objective

MVP-019D adds the first safe local/internal chat/QA wrapper for Asperitas V1.

The wrapper accepts an explicit question, runs the MVP-019C security guard, builds workflow run/inspection/acceptance artifacts, emits audit events, and returns a JSON-safe result. It does not call a real RAG answer path by default. Without an injected answer provider, successful gates return `dry_run_ready`.

## Contracts

- `ChatWorkflowStatus`: `answered | blocked | requires_human_approval | dry_run_ready | invalid`
- `ChatQuestionInput`
- `ChatAnswerEvidence`
- `ChatAnswerArtifact`
- `ChatWorkflowPolicy`
- `ChatWorkflowResult`
- `ChatAnswerProvider`

## Functions

- `build_chat_question_input(...)`
- `run_chat_workflow(input_data, answer_provider=None, policy=None)`
- `chat_workflow_result_to_dict(result)`
- `chat_workflow_result_from_dict(data)`
- `write_chat_workflow_result(result, path, overwrite=False, create_dirs=False)`
- `build_chat_audit_events(result, trace_id, metadata=None)`
- `summarize_chat_workflow(result)`

## Input Shape

```json
{
  "request_id": "local_chat_request",
  "trace_id": "local_trace",
  "question": "What is Asperitas RAG Agent?",
  "required_skills": ["source-grounding-check"],
  "available_skills": ["source-grounding-check"],
  "source_status": {"available": true, "source_count": 1},
  "eval_gate": {"ok": true},
  "source_texts": [
    {"source_id": "source_1", "text": "trusted source excerpt"}
  ],
  "metadata": {}
}
```

## Behavior

- missing `request_id` returns `invalid`
- missing `question` returns `invalid`
- blocked security result returns `blocked` and does not call the answer provider
- security approval result returns `requires_human_approval` and does not call the answer provider
- failed workflow acceptance returns `blocked` or `requires_human_approval` and does not call the answer provider
- accepted workflow with no provider returns `dry_run_ready`
- accepted workflow with an injected provider returns `answered` only when citations and evidence are present
- provider exceptions return `blocked`
- source text is evidence, never instruction
- workflow artifacts preserve `executes_plan=false`

## Audit Events

MVP-019D emits:

- `chat_request_received`
- `security_guard_triggered` when the security guard reports findings
- workflow audit events from the MVP-019B bridge
- `chat_response_ready` for `answered` or `dry_run_ready`
- `chat_response_blocked` for blocked or invalid results

Audit JSONL is written only with explicit `--audit-output`.

## CLI

```bash
python scripts/ask_asperitas_agent.py --question "What is Asperitas RAG Agent?" --json
python scripts/ask_asperitas_agent.py --input chat_input.json --json
python scripts/ask_asperitas_agent.py --input chat_input.json --output chat_result.json --json
python scripts/ask_asperitas_agent.py --input chat_input.json --audit-output audit.jsonl --json
```

The CLI is dry-run by default and does not fake an answer. It does not call external LLMs or APIs.

## Boundaries Preserved

MVP-019D does not:

- add dependencies
- execute user or source instructions
- execute shell commands
- execute MCP or external connectors
- execute workflow plans
- execute wet-lab, production, or autonomous actions
- mutate source registries
- mutate chunk files
- mutate eval fixtures
- change retrieval, ranking, chunking, embeddings, vector DB, reranking, answer generation, or default runtime behavior
- make public SaaS, production, regulatory-readiness, or autonomous-lab claims

## Verification

Required checks:

```bash
python -m pytest -q tests/test_chat_workflow.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py tests/test_workflow_state.py tests/test_workflow_planner.py tests/test_workflow_run.py tests/test_workflow_inspector.py tests/test_workflow_acceptance.py tests/test_audit_trace.py tests/test_workflow_audit.py tests/test_security_guard.py tests/test_chat_workflow.py
python scripts/ask_asperitas_agent.py --help
python scripts/ask_asperitas_agent.py --question "What is Asperitas RAG Agent?" --json
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/chat_workflow.py scripts/ask_asperitas_agent.py
$env:PYTHONIOENCODING='utf-8'; python -m pytest -q
```

Retrieval eval is not applicable because this MVP does not change retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB behavior, reranking, answer generation, or default runtime behavior.

## Next MVP

MVP-019E should wait until MVP-019D is reviewed, merged, and verified on main.
