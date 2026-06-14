# Quality Gates

Apply these gates before reporting a task as done.

## Source Code Tests

Required when source code changes.

- Add or update tests for changed behavior.
- Run `pytest`.
- Report command, result, failures, and skipped tests.

Pass condition: changed behavior is covered and tests pass, or the blocker is explicit.

## Artifact Verification

Required when generated files, schemas, docs, prompts, datasets, or configs change.

- Re-read created or edited files.
- Check paths, names, frontmatter, links, and required sections.
- Verify generated artifacts are in the intended location.

Pass condition: artifact exists and matches the requested contract.

## Retrieval Evaluation

Required when retrieval, chunking, scoring, metadata filters, embeddings, vector DB, hybrid search, reranking, or answer generation changes.

- Run the project retrieval eval command when available.
- Report dataset, settings, pass/fail count, metric deltas, and regressions.

Pass condition: no unexplained regression in required retrieval metrics.

## Citation / Source-Grounding Check

Required when answers, citations, evidence labels, source hierarchy, or hallucination controls change.

- Confirm answers trace claims to source IDs.
- Confirm unsupported claims are removed or labeled.
- Confirm evidence labels and confidence are preserved.

Pass condition: material claims are traceable or explicitly marked uncertain.

## Compliance / Biosafety Check

Required when biological data, biodiversity data, CITES, Nagoya Protocol, LMO, K-BDS, privacy, security, regulatory, legal, or public-communication risk is affected.

- Identify risk domain.
- Identify missing approvals or evidence.
- Block or escalate unsafe output.

Pass condition: risk is either cleared, mitigated, or explicitly escalated.

## Documentation Update Check

Required when behavior, workflow, commands, evals, milestones, or user-facing outputs change.

- Update relevant docs.
- Keep docs operational and current.
- Avoid vague status claims.

Pass condition: docs match the implemented state.

## GitHub Review Check

Required before commits, pushes, PRs, and merge decisions.

- Inspect changed files.
- Confirm no source code was changed for docs-only tasks.
- Confirm no secrets or confidential content were added.
- Summarize risks and review focus.

Pass condition: PR or commit scope is clear and reviewable.

