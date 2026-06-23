# Decision Log Schema

Use this schema for future decision entries, task closeouts, release decisions, and metric baselines.

## Metric Provenance

Every metric must be labeled with one of:

- `Fresh Run`: produced during the current task by a reported command.
- `Historical`: copied from a prior report, issue, PR, or commit context.
- `Not Run`: intentionally skipped or unavailable, with a reason.

Do not mix fresh and historical metrics without labeling them separately.

## Required Fields

Each decision entry must include:

- Date
- Task
- Issue/PR
- Files changed or inspected
- Commands run
- Metrics, each labeled `Fresh Run`, `Historical`, or `Not Run`
- Risks and residual issues
- Decision
- Next action

## Auditability

Decision entries should be easy to convert into JSON or compare by script. Prefer stable field names, explicit dates, exact command strings, and metric labels. If a log target supports structured records, keep one decision entry per object or section and avoid mixing unrelated tasks in one entry.

## Log Handling Rules

- Use append-only updates for historical logs.
- Do not overwrite or silently revise historical entries.
- Corrections must be labeled as corrections and dated.
- Do not claim tests, evals, or metrics passed unless the command was actually run.
- If a task is docs-only, label tests and evals as `Not Run` and explain why.
- Record fail-closed decisions explicitly when a quality gate blocks, defers, or protects source-grounding, compliance, metadata, or safety behavior.

## Known Risk

`00_ADMIN/decision_log.md` currently has a binary-content signature rather than plain Markdown text. Treat this as a decision-log storage anomaly and report it as a risk when decision-log work touches that file.

Do not delete, rewrite, convert, or repair `00_ADMIN/decision_log.md` unless the user explicitly approves that operation.
