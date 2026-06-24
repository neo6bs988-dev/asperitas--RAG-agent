---
name: decision-log-maintainer
description: Use when recording or reviewing decision logs, metric provenance, release decisions, or task closeout evidence.
---

# Decision Log Maintainer

## When To Use

- A task records a decision, closeout, milestone result, or performance baseline.
- Metrics need provenance labels.
- A report must preserve issue, PR, files, commands, risks, and next action.

## When Not To Use

- Temporary scratch notes that will not guide future work.
- Source code implementation without a decision or metric record.
- Rewriting historical logs.

## Required Inputs

- Date.
- Task and issue or PR.
- Files changed or inspected.
- Commands run.
- Metrics with `Fresh Run`, `Historical`, or `Not Run` labels.
- Risks, decision, and next action.

## Workflow Steps

1. Identify whether the entry is new, a correction, or a closeout.
2. Use append-only updates for historical logs.
3. Preserve old entries; do not overwrite historical decisions.
4. Include date, task, issue/PR, files, commands, metrics, risks, decision, and next action.
5. Label every metric as `Fresh Run`, `Historical`, or `Not Run`.
6. Prefer JSON-auditable structure: stable field names, one task per entry, exact command strings, and explicit metric provenance.
7. Record fail-closed decisions explicitly when a gate blocks or defers source-grounding, compliance, metadata, safety, or quality behavior.
8. If `00_ADMIN/decision_log.md` is needed, first check whether it is plain text.
9. Treat the current `00_ADMIN/decision_log.md` binary-content anomaly as a risk.
10. Do not delete or rewrite `00_ADMIN/decision_log.md` unless explicitly approved.

## Quality Gates

- Decision entries are traceable to commands or cited historical reports.
- Historical data is not silently changed.
- Binary or unreadable logs are flagged, not repaired without approval.
- Confidential P0/P1 material is not exposed in public-facing summaries.
- Quality-gate decisions preserve source-grounding, compliance, metadata, and safety stop rules.

## Report Format

- Date:
- Task:
- Issue/PR:
- Files:
- Commands:
- Metrics:
- Risks:
- Decision:
- Next action:

## Failure Conditions

- Historical logs are overwritten.
- Metrics lack Fresh Run / Historical / Not Run labels.
- `00_ADMIN/decision_log.md` is rewritten despite the binary-content anomaly and without explicit approval.
- A decision is recorded without risks or next action.

## Next-Step Recommendation Format

- Next decision entry:
- Required evidence:
- Safe location:
- Approval needed:
