---
name: open-source-adoption-review
description: Use when evaluating, adapting, or integrating open-source AI/RAG/vector/eval libraries into the Asperitas RAG Agent.
---

# Open Source Adoption Review

## When To Use

- Considering any external open-source dependency.
- Adapting architecture patterns from public GitHub repositories.
- Adding vector DB, embedding, agent orchestration, eval, document parsing, or observability libraries.
- Reviewing whether an external repository should be copied, vendored, wrapped, or rejected.

## When Not To Use

- Pure internal refactor with no external dependency or external design influence.
- Docs-only edits that do not mention external repositories.
- Temporary brainstorming with no implementation decision.

## Required Inputs

- External repository name and URL.
- Intended use in the Asperitas RAG Agent.
- License and security status if known.
- Current internal files affected.
- Whether this is dependency use, clean-room pattern adoption, or code copy.
- Expected tests and eval gates.

## Workflow Steps

1. Identify the exact external repository and purpose.
2. Check whether the repository is active, archived, or risky.
3. Check license compatibility before copying code or adding dependency.
4. Prefer clean-room internal interface/adapter over direct code copy.
5. Preserve existing deterministic retrieval modes and source-grounding metadata.
6. Add or update tests for any behavior change.
7. Run source tests and artifact verification.
8. Run retrieval eval if retrieval, chunking, scoring, or answer behavior changes.
9. Report what was adopted: concept, dependency, or code.
10. Record unresolved license/security/compliance risks.

## Quality Gates

- No external code copied without license review.
- No new dependency added without justification.
- No API key or secret committed.
- Existing tests pass.
- Existing retrieval modes remain available.
- Source IDs, source priority, evidence labels, and section metadata are preserved.
- Regression risk is evaluated.

## Report Format

- External repo reviewed:
- Adoption type: concept / dependency / code copy / rejected
- Reason:
- License status:
- Security/dependency risk:
- Files changed:
- Tests/evals:
- Source-grounding impact:
- Compliance impact:
- Rollback path:
- Next step:

## Failure Conditions

- Code is copied from an external repo without license review.
- A heavy framework is added before internal interfaces exist.
- Existing eval comparability is broken.
- Existing retrieval modes are removed.
- Secrets or credentials are committed.
- Biological/compliance data risk is ignored.

## Next-Step Recommendation Format

- Candidate:
- Decision:
- Minimal safe adoption:
- Required gate:
- Blocking risk:
