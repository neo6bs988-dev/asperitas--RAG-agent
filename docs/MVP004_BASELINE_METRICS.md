# MVP-004 Baseline Metrics

Status: active quality gate for MVP-004 structure-aware chunking and retrieval stabilization.

This document turns the retrieval-eval-quality-gate skill into an executable checkpoint. The baseline is not a failure state. It is the reference point before embeddings, vector DB, hybrid retrieval, reranking, UI, or LLM answer generation are added.

## Required Commands

Run these commands from the repository root before claiming that an MVP-004 retrieval/chunking task is complete.

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/audit_chunk_sections.py --json
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
```

Use the JSON mode for machine-readable review when needed:

```bash
python scripts/run_retrieval_eval.py --retriever baseline --limit 5 --json
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5 --json
```

## Baseline Table

| Gate | Baseline / Expected State |
|---|---:|
| Unit tests | 41 passed |
| Artifact verification | `ok: true` |
| Source registry records | 48 |
| Chunks | 2,821 |
| Eval questions | 32 |
| Current retriever | deterministic TF-IDF baseline |
| Source file match @3 | 34.4% |
| Source file match @5 | 43.8% |
| Source priority match | 43.8% |
| Evidence label match | 43.8% |
| Section match | 31.2% |
| Overall pass rate | 31.2% |

## MVP-004 Interpretation

MVP-004 is about structure-aware chunking and section metadata. The main goal is to preserve and exploit section context without breaking existing source traceability.

A good MVP-004 change should improve or preserve:

- section metadata coverage
- section heading/path/context stability
- source ID traceability
- expected source file retrieval at top 5
- source priority and evidence label retention
- deterministic reproducibility

## Regression Rules

Hard fail if any of the following happen without an explicit, approved reason:

- `python -m pytest` fails.
- `python scripts/verify_artifacts.py` returns `ok: false`.
- Retrieval eval cannot run.
- Source IDs, source files, source priorities, or evidence labels are dropped.
- `source_file_match_at_5` decreases by more than 2 percentage points.
- `source_priority_match` decreases.
- `evidence_label_match` decreases.
- `section_match` decreases when the task claims section-awareness improvement.
- Compliance or confidentiality risk is introduced and not escalated.

Conditional pass if:

- metrics are neutral but chunk section metadata coverage improves;
- a small metric dip is explained by a deliberate eval fixture change;
- the change is documentation-only and no executable behavior changed.

Improvement if:

- section match improves without lowering source/evidence traceability;
- source file match @5 improves without lowering evidence label or source priority match;
- audit results show better section coverage and no schema regression.

## Required Report Format

Every MVP-004 retrieval/chunking task must report:

```text
MVP:
Objective:
Files changed:
Commands run:
Unit tests:
Artifact verification:
Chunk section audit:
Retrieval eval baseline mode:
Retrieval eval mvp003 mode:
Metric deltas:
Regressions:
Source-grounding impact:
Compliance impact:
Decision: pass / conditional pass / fail
Next task:
```

## Owner Decision Needed

Before moving from MVP-004 to MVP-005, confirm whether the acceptance criterion is:

1. Preserve baseline and complete structure metadata plumbing; or
2. Improve retrieval metrics before embeddings/vector DB; or
3. Move to MVP-005 once deterministic section metadata is stable, even if TF-IDF metrics remain baseline-level.

Default recommendation: close MVP-004 when section metadata is stable, audited, and non-regressive, then move to MVP-005 embeddings + vector DB.