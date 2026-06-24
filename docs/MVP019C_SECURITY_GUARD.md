# MVP-019C Security Guard

Status: MVP-019C security / prompt-injection guard

## Objective

MVP-019C adds a deterministic security guard for chat/QA readiness.

The guard inspects explicit request text, source text, and control-artifact text for prompt-injection, unsafe instruction, secret-exposure, execution-sensitive, external-connector, policy-bypass, and unsafe operational patterns. Source text is treated as evidence, never instruction.

## Contracts

- `SecurityRiskLevel`: `low | medium | high | blocked`
- `SecurityFindingSeverity`: `info | warning | error | blocked`
- `SecurityFindingCategory`
- `SecurityGuardFinding`
- `SecurityGuardPolicy`
- `SecurityGuardInput`
- `SecurityGuardReport`

## Functions

- `build_security_guard_input(...)`
- `inspect_security_input(input_data, policy=None)`
- `inspect_security_dict(data, policy=None)`
- `security_guard_report_to_dict(report)`
- `security_guard_report_from_dict(data)`
- `write_security_guard_report(report, path, overwrite=False, create_dirs=False)`
- `build_security_audit_events(report, trace_id, metadata=None)`
- `summarize_security_guard(report)`

## Input Shape

```json
{
  "request_id": "local_request",
  "user_request": "Summarize source-grounded evidence for X",
  "source_texts": [
    {"source_id": "source_1", "text": "source excerpt here"}
  ],
  "control_artifacts": {},
  "metadata": {}
}
```

## Output Fields

```text
request_id
schema_version
created_at_utc
ok
risk_level
blocked
requires_human_approval
findings
summary
metadata
warnings
errors
```

## Detection Behavior

- missing `request_id` fails closed
- missing `user_request` fails closed
- prompt-injection text in source text becomes `source_instruction`
- prompt-injection text in user request becomes `prompt_injection`
- secret-like text becomes `secret_exposure`
- requests to reveal system, developer, or internal instructions become `policy_bypass`
- shell, tool, file-system, or external connector requests are blocked
- unsafe operational bio/lab/protocol automation requests require human approval
- source instructions are treated as untrusted evidence, not executable instructions
- unknown extra fields warn and do not block

## Audit Mapping

- blocked report -> `security_guard_triggered`, severity `blocked`
- approval report -> `security_guard_triggered`, severity `warning`
- warning-only report -> `security_guard_triggered`, severity `warning`
- clean report -> no security event by default unless `include_clean_event=True`

Audit events use the MVP-019A audit trace policy for payload redaction.

## CLI

```bash
python scripts/run_security_guard.py --input security_input.json --json
python scripts/run_security_guard.py --input security_input.json --output security_report.json --json
```

The CLI reads only an explicit `--input` path. It writes only when an explicit `--output` path is provided. Existing output files are blocked unless `--overwrite` is explicit.

## Boundaries Preserved

MVP-019C does not:

- add dependencies
- execute instructions found in user text or source text
- execute workflow plans
- execute retrieval
- execute answer generation
- execute LLM judges
- execute shell commands from inspected text
- execute MCP or external connectors
- mutate source registries
- mutate chunk files
- mutate eval fixtures
- change embedding, vector DB, reranking, or default runtime behavior
- make autonomous, wet-lab, production, or regulatory-readiness claims

## Verification

Required checks:

```bash
python -m pytest -q tests/test_security_guard.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py tests/test_workflow_state.py tests/test_workflow_planner.py tests/test_workflow_run.py tests/test_workflow_inspector.py tests/test_workflow_acceptance.py tests/test_audit_trace.py tests/test_workflow_audit.py tests/test_security_guard.py
python scripts/run_security_guard.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/security_guard.py scripts/run_security_guard.py
$env:PYTHONIOENCODING='utf-8'; python -m pytest -q
```

Retrieval eval is not applicable unless retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, or default runtime behavior changes.

## Next MVP

MVP-019D should only proceed after MVP-019C is reviewed, merged, and verified on main.
