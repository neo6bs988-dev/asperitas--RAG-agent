# Quality Gates

Apply these gates before reporting a task as done. A gate is not a suggestion; it is the minimum evidence needed to call a change complete.

## Gate Selection Matrix

| Change type | Required gates |
|---|---|
| Docs/governance only | Artifact verification + GitHub review |
| Source code | Source code tests + artifact verification + GitHub review |
| Chunking/retrieval/scoring | Source code tests + artifact verification + chunk audit + retrieval evaluation + GitHub review |
| Answer generation/citation | Source code tests + source-grounding check + retrieval evaluation if retrieval is touched + GitHub review |
| Biological/compliance/public claim | Compliance/biosafety check + source-grounding check + GitHub review |
| MVP release | All relevant gates + MVP release manager review |

## Canonical Commands

Run from the repository root.

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/audit_chunk_sections.py --json
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
```

Use `docs/MVP004_BASELINE_METRICS.md` for the current retrieval baseline, regression rules, and report format.

## Source Code Tests

Required when source code changes.

- Add or update tests for changed behavior.
- Run `python -m pytest`.
- Report command, result, failures, and skipped tests.

Pass condition: changed behavior is covered and tests pass, or the blocker is explicit.

Hard fail: source code changed but tests were not run and no blocker was documented.

## Artifact Verification

Required when generated files, schemas, docs, prompts, datasets, configs, or governance files change.

- Re-read created or edited files.
- Check paths, names, frontmatter, links, and required sections.
- Verify generated artifacts are in the intended location.
- Run `python scripts/verify_artifacts.py` when executable artifacts, datasets, schemas, source registry, chunks, or project outputs may be affected.

Pass condition: artifact exists and matches the requested contract.

Hard fail: artifact path is wrong, generated file is missing, or the task claims implementation that does not exist.

## Chunk Section Audit

Required when chunking, section metadata, heading detection, schemas, or chunk artifacts change.

- Run `python scripts/audit_chunk_sections.py --json`.
- Report total chunks, chunks with section metadata, chunks missing section metadata, and notable section values.

Pass condition: section metadata behavior is reported and no unexplained schema regression appears.

## Retrieval Evaluation

Required when retrieval, chunking, scoring, metadata filters, embeddings, vector DB, hybrid search, reranking, or answer generation changes.

- Run `python scripts/run_retrieval_eval.py --retriever baseline --limit 5`.
- Run `python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5`.
- Report dataset, settings, pass/fail count, metric deltas, and regressions.

Pass condition: no unexplained regression in required retrieval metrics.

Hard fail:

- eval cannot run;
- metrics are invented or omitted;
- source IDs, source priority, or evidence labels are dropped;
- a claimed retrieval improvement does not report before/after metrics.

## Citation / Source-Grounding Check

Required when answers, citations, evidence labels, source hierarchy, or hallucination controls change.

- Confirm answers trace claims to source IDs.
- Confirm unsupported claims are removed or labeled.
- Confirm evidence labels and confidence are preserved.
- Confirm insufficient evidence produces uncertainty instead of fabrication.

Pass condition: material claims are traceable or explicitly marked uncertain.

Hard fail: an output path can produce unsupported claims as facts.

## Compliance / Biosafety Check

Required when biological data, biodiversity data, CITES, Nagoya Protocol, LMO, K-BDS, privacy, security, regulatory, legal, IP, investor, partner, or public-communication risk is affected.

- Identify risk domain.
- Identify missing approvals or evidence.
- Block or escalate unsafe output.
- Distinguish internal, investor-facing, partner-facing, public, and restricted outputs.

Pass condition: risk is either cleared, mitigated, or explicitly escalated.

Hard fail: regulated biological, confidential, personal, legal, or investor-sensitive claims are exposed without review.

## Documentation Update Check

Required when behavior, workflow, commands, evals, milestones, or user-facing outputs change.

- Update relevant docs.
- Keep docs operational and current.
- Avoid vague status claims.
- Link to concrete commands when the document describes executable gates.

Pass condition: docs match the implemented state.

## GitHub Review Check

Required before commits, pushes, PRs, and merge decisions.

- Inspect changed files.
- Confirm no source code was changed for docs-only tasks.
- Confirm no secrets or confidential content were added.
- Use `.github/pull_request_template.md` for PRs.
- Summarize risks and review focus.

Pass condition: PR or commit scope is clear and reviewable.

## CI Status

The executable CI gate is `.github/workflows/quality-gates.yml`.

CI should run on:

- push to `main`;
- pull requests to `main`;
- manual workflow dispatch.

CI passing does not automatically mean a PR is strategically correct. It means the minimum executable checks passed.