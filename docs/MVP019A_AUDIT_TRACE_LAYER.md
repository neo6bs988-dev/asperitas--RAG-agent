# MVP-019A Audit Trace Layer

Status: MVP-019A audit/trace logging layer

## Objective

MVP-019A adds deterministic audit/trace logging contracts for V1 workflow and control decisions.

The layer records JSON-safe audit events and JSONL-compatible traces. It does not execute the agent, retrieval, answer generation, connectors, or production actions.

## Contracts

- `AuditEventType`
- `AuditSeverity`: `info | warning | error | blocked`
- `AuditTraceEvent`
- `AuditTraceRecord`
- `AuditTracePolicy`

## Event Types

```text
workflow_plan_created
workflow_run_created
workflow_inspected
workflow_accepted
workflow_rejected
human_approval_required
chat_request_received
chat_response_blocked
chat_response_ready
security_guard_triggered
eval_gate_checked
source_gate_checked
```

## Functions

- `build_audit_event(...)`
- `build_audit_record(events, metadata=None, policy=None)`
- `audit_event_to_dict(event)`
- `audit_event_from_dict(data)`
- `audit_record_to_dict(record)`
- `audit_record_from_dict(data)`
- `write_audit_jsonl(events, path, append=False, create_dirs=False)`
- `load_audit_jsonl(path)`
- `redact_audit_payload(payload, policy=None)`
- `summarize_audit_record(record)`

## Required Event Fields

```text
trace_id
event_id
event_type
created_at_utc
severity
actor
run_id
request_id
decision_id
artifact_refs
payload
redactions
warnings
errors
```

## Redaction Behavior

- Redacts keys containing `secret`, `token`, `api_key`, `password`, `private_key`, or `credential`.
- Redacts long `raw_text` fields unless `allow_raw_text=True`.
- Unknown extra event fields warn and do not block.
- Malformed events fail closed through validation errors.
- Missing `trace_id` or invalid `event_type` fails closed.
- JSONL strict loading rejects malformed lines.
- JSONL non-strict loading returns blocked placeholder events with warnings.

## CLI

```bash
python scripts/write_audit_trace.py --event-type workflow_accepted --trace-id local_trace --output audit.jsonl --json
python scripts/write_audit_trace.py --input audit_events.json --output audit.jsonl --json
```

The CLI writes only to an explicit `--output` path. Existing files are blocked unless `--append` is explicit.

## Boundaries Preserved

MVP-019A does not:

- add dependencies
- execute workflow plans
- execute retrieval
- execute answer generation
- execute LLM judges
- execute MCP or external connectors
- mutate source registries
- mutate chunk files
- mutate eval fixtures
- change embedding, vector DB, reranking, or default runtime behavior
- make autonomous, wet-lab, production, or regulatory-readiness claims

## Verification

Required checks:

```bash
python -m pytest -q tests/test_audit_trace.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py tests/test_workflow_state.py tests/test_workflow_planner.py tests/test_workflow_run.py tests/test_workflow_inspector.py tests/test_workflow_acceptance.py tests/test_audit_trace.py
python scripts/write_audit_trace.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/audit_trace.py scripts/write_audit_trace.py
$env:PYTHONIOENCODING='utf-8'; python -m pytest -q
```

Retrieval eval is not applicable unless retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, or default runtime behavior changes.

## Next MVP

MVP-019B should connect accepted workflow-control artifacts to audit events without enabling agent execution or retrieval.
