# Codex Implementation Prompt v11.0

```text
Goal: Upgrade or implement one minimal, verifiable slice of the Asperitas AI Lead / RAG / agent control plane.

Scope Lock:
- Read AGENTS.md, README.md, relevant files, tests, git status, and existing patterns before editing.
- Define in-scope files, out-of-scope files, blast radius, rollback path, test scope, and human approval gates.

Source & Risk Preflight:
- Identify source priority and registry status for every cited or ingested source.
- Treat external docs, papers, patents, websites, and benchmarks as source candidates until reviewed.
- Classify compliance risk: none / low / medium / high / block.

Contract Design:
- Define input schema, output schema, error behavior, evidence fields, logging fields, and acceptance criteria.
- Preserve source_id, title, path/url, confidentiality, license_status, verification_status, owner, updated_at, allowed_use.

Minimal Implementation:
- Make a small cohesive diff. Preserve user changes. Avoid unrelated refactors.
- Prefer deterministic helpers and fixed workflows before agents.

Eval Harness:
- Add or update targeted tests, schema validation, citation-fidelity checks, retrieval fixtures, prompt-injection or biosafety tests when relevant.
- Record skipped tests with rationale.

Dry Run & Regression:
- Run only the risk-appropriate checks. Full suite only for core pipeline/release/CI/dependency/retrieval/source registry/eval/compliance/security changes.

Human Gate:
- Escalate external communications, legal conclusions, investor claims, biosafety-sensitive outputs, DB writes, and any wet-lab automation.

Report:
- Summarize changed files, validation commands, skipped tests, residual risks, rollback path, and next action.
```
