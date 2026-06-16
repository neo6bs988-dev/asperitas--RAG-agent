# Pull Request Review

## Objective

- [ ] The objective is stated clearly.
- [ ] The change matches the requested scope.
- [ ] Unrelated files are excluded.

## Change Type

- [ ] Docs/governance only
- [ ] Source code
- [ ] Tests
- [ ] Retrieval/chunking/scoring
- [ ] Answer generation/citation
- [ ] Compliance/biosafety/regulatory
- [ ] MVP release

## Always-Local Checks

- [ ] `python -m pytest`
- [ ] `python scripts/verify_artifacts.py`
- [ ] Not applicable because this is docs/governance only; reason:

## Conditional Local Checks

Run when the PR changes retrieval, chunking, metadata, embeddings, vector search, hybrid retrieval, reranking, eval fixtures, or answer-generation behavior.

- [ ] `python scripts/audit_chunk_sections.py --json`
- [ ] `python scripts/run_retrieval_eval.py --retriever baseline --limit 5`
- [ ] `python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5`
- [ ] `python scripts/run_retrieval_eval.py --retriever vector --limit 5`
- [ ] `python scripts/run_retrieval_eval.py --retriever hybrid --limit 5`
- [ ] Not applicable; reason:

Run when reranking code, reranker eval plumbing, or reranker docs/policy change.

- [ ] `python scripts/run_retrieval_eval.py --retriever mvp003 --reranker deterministic-test --limit 5`
- [ ] `python scripts/run_retrieval_eval.py --retriever hybrid --reranker deterministic-test --limit 5`
- [ ] Not applicable; reason:

## CI Checks

- [ ] GitHub Actions `Quality Gates` workflow ran on this PR branch.
- [ ] `Quality Gates` passed, or failure is linked and explained.
- [ ] CI covered `pytest`, artifact verification, chunk audit, baseline eval, and `mvp003` eval.
- [ ] Any local-only vector, hybrid, reranker, release, or compliance gates are reported below.

## Retrieval Metrics

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| Source file match @3 | | | |
| Source file match @5 | | | |
| Source priority match | | | |
| Evidence label match | | | |
| Section match | | | |
| Overall pass rate | | | |

## Source-Grounding / Citation Impact

- [ ] Source IDs are preserved.
- [ ] Source priority is preserved.
- [ ] Evidence labels are preserved.
- [ ] Unsupported claims are removed or labeled.
- [ ] Not applicable.

## Compliance / Biosafety Impact

- [ ] CITES/Nagoya/LMO/K-BDS risk reviewed if relevant.
- [ ] Privacy/security/IP/legal risk reviewed if relevant.
- [ ] No confidential, secret, or personal data added.
- [ ] Public/investor-facing claims are source-supported.
- [ ] Not applicable.

## Risk Summary

Known risks:

Deferred work:

Human approval needed:

## Merge Safety

- [ ] Branch is up to date with `main`.
- [ ] No source code changed for docs/governance-only work.
- [ ] No generated indexes, model binaries, secrets, credentials, endpoints, or cloud resources were added.
- [ ] Branch protection requires the `Quality Gates` workflow before merge, or repository admin follow-up is listed below.
- [ ] Remaining manual checks:

## Merge Decision

- [ ] Ready
- [ ] Conditional
- [ ] Blocked

Reason:
