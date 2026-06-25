# V1 Internal Dry-run

Status: internal dry-run packet only; `v1.0.0-internal` remains pending until this evidence passes on the intended release branch and a human creates any later tag or release.

## Purpose

This packet defines a reproducible internal dogfood only dry-run for the V1 control plane. It replaces pytest-created temp inputs with deterministic inputs generated inside `scripts/run_v1_internal_dry_run.py`.

## Scope

- release-readiness status check
- clean security guard check with valid internal-review input
- prompt-injection block check
- chat workflow dry-run check
- audit event serialization check
- explicit JSON report output when requested

## Non-Scope

- not public SaaS
- not production customer deployment
- not autonomous wet-lab execution
- not regulatory readiness
- not clinical or commercial performance proof
- not proven biological model capability
- not a real RAG answer provider integration

chat remains dry-run by default and no real answer provider wired. security/workflow/audit gates active means the dry-run verifies the control-plane gates, not production operation or answer quality.

## How to Run

Print JSON without writing files:

```bash
python scripts/run_v1_internal_dry_run.py --json
```

Write an explicit report:

```bash
python scripts/run_v1_internal_dry_run.py --output .tmp/v1_internal_dry_run.json --create-dirs --json
```

Existing output files are blocked unless `--overwrite` is passed. Missing parent directories are blocked unless `--create-dirs` is passed.

## Data to Collect

- command exit code
- top-level `status`
- `summary.check_count`, `summary.passed_count`, and `summary.failed_count`
- release-readiness check metadata
- clean security risk level and finding count
- prompt-injection blocked risk level and finding count
- chat dry-run status and warning count
- audit serialization status
- any warnings or errors

## Failure Log Use for V1.1

Failures should be copied into the V1.1 failure log collector with the command, stdout/stderr, report JSON when available, branch, HEAD SHA, and whether the failure is deterministic. V1.1 triage should separate control-plane defects from deferred product gaps such as real answer provider wiring, local/internal web dogfood UI, and retrieval/answer baseline work.
