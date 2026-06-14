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

## Required Checks

- [ ] `python -m pytest`
- [ ] `python scripts/verify_artifacts.py`
- [ ] `python scripts/audit_chunk_sections.py --json`
- [ ] `python scripts/run_retrieval_eval.py --retriever baseline --limit 5`
- [ ] `python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5`
- [ ] Not applicable because this is docs-only; reason:

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

## Merge Decision

- [ ] Ready
- [ ] Conditional
- [ ] Blocked

Reason:
