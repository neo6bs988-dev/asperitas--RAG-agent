# MVP-004 Final Quality Gate Report

Date: 2026-06-14

Issue: #1, MVP-004: Run quality gates and record final baseline before MVP-005.

## Objective

Run the full MVP-004 quality gate pipeline, record observed results, compare against `docs/MVP004_BASELINE_METRICS.md`, and decide whether MVP-004 can close before MVP-005.

## Commands Run

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/audit_chunk_sections.py --json
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
```

Note: `python -m pytest` and the MVP-003 retrieval eval each required a longer local timeout than the first attempt. The final runs completed successfully.

## Test Results

- Command: `python -m pytest`
- Result: pass
- Tests: 110 passed
- Runtime: 213.99 seconds

## Artifact Verification

- Command: `python scripts/verify_artifacts.py`
- Result: pass
- `ok`: true
- Source registry records: 48
- Chunks: 2,821
- Unsupported sources: 0
- Errors: 0
- Warnings: 0

## Chunk Section Audit

- Command: `python scripts/audit_chunk_sections.py --json`
- Total chunks: 2,821
- Chunks with section metadata: 2,097
- Chunks missing section metadata: 724
- Section metadata coverage: 74.3%

Sample preserved sections included:

- `SYSTEM ROLE`
- `MISSION`
- `NORTH STAR`
- `SINGLE SOURCE OF TRUTH`

## Retrieval Eval Results

### Baseline Retriever

- Command: `python scripts/run_retrieval_eval.py --retriever baseline --limit 5`
- Mode: `current-tfidf-baseline`
- Questions: 32
- Source file match @3: 34.4%
- Source file match @5: 43.8%
- Source priority match: 43.8%
- Evidence label match: 43.8%
- Section match: 34.4%
- Overall pass rate: 34.4%

### MVP-003 Retriever

- Command: `python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5`
- Mode: `mvp003-deterministic-metadata`
- Questions: 32
- Source file match @3: 96.9%
- Source file match @5: 100.0%
- Source priority match: 100.0%
- Evidence label match: 100.0%
- Section match: 90.6%
- Overall pass rate: 90.6%

Failed question IDs:

- `MVP0025-Q001`
- `MVP0025-Q004`
- `MVP0025-Q010`

## Baseline Comparison

Comparison target: `docs/MVP004_BASELINE_METRICS.md`.

| Gate | Expected / Prior Baseline | Observed Final Result | Decision |
|---|---:|---:|---|
| Unit tests | 41 passed | 110 passed | improvement |
| Artifact verification | `ok: true` | `ok: true` | pass |
| Source registry records | 48 | 48 | preserved |
| Chunks | 2,821 | 2,821 | preserved |
| Eval questions | 32 | 32 | preserved |
| Baseline source file match @3 | 34.4% | 34.4% | preserved |
| Baseline source file match @5 | 43.8% | 43.8% | preserved |
| Baseline source priority match | 43.8% | 43.8% | preserved |
| Baseline evidence label match | 43.8% | 43.8% | preserved |
| Baseline section match | 31.2% | 34.4% | improvement |
| Baseline overall pass rate | 31.2% | 34.4% | improvement |
| MVP-003 source file match @5 | not listed | 100.0% | recorded |
| MVP-003 source priority match | not listed | 100.0% | recorded |
| MVP-003 evidence label match | not listed | 100.0% | recorded |
| MVP-003 section match | not listed | 90.6% | recorded |
| MVP-003 overall pass rate | not listed | 90.6% | recorded |

## Regression Check

No unexplained regression was observed against `docs/MVP004_BASELINE_METRICS.md`.

- Unit tests passed.
- Artifact verification returned `ok: true`.
- Retrieval eval ran for both `baseline` and `mvp003`.
- Source file, source priority, and evidence label metrics were preserved or improved.
- Section match improved in baseline mode and reached 90.6% in MVP-003 mode.
- Chunk count and source registry count were preserved.

## Source-Grounding Impact

Source file, source priority, and evidence label metrics are preserved in baseline mode and materially improved in MVP-003 mode. The MVP-003 eval result supports moving forward with source-grounded retrieval as long as the remaining failed question IDs are tracked.

## Compliance Impact

No source code, biological content, source registry content, or public/investor-facing claims were changed by this report. No new compliance or biosafety risk was introduced.

## MVP-004 Decision

Decision: close MVP-004 and proceed to MVP-005.

Rationale:

- Required executable gates completed.
- Baseline metrics are preserved or improved.
- Structure-aware section metadata is present on 74.3% of chunks.
- MVP-003 deterministic metadata retrieval materially outperforms the TF-IDF baseline.
- Remaining MVP-003 failed questions should be tracked as follow-up work, not a blocker for MVP-005.

## Next Recommended Task

Start MVP-005 Phase 1: implement embedding record schema and metadata-preservation tests, while preserving source IDs, source file, source priority, evidence label, section metadata, and heading context.

