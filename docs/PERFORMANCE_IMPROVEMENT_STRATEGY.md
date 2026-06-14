# Performance Improvement Strategy

Purpose: define how retrieval quality, source-grounding, compliance safety, and developer velocity improve across MVP stages.

This document prevents vague claims such as "improved performance". Every improvement must map to a metric, test, quality gate, or decision log.

## Performance Dimensions

| Dimension | What It Means | Primary Gate |
|---|---|---|
| Retrieval quality | Correct source appears in top-k results | `scripts/run_retrieval_eval.py` |
| Metadata preservation | Source IDs, priorities, labels, sections survive every stage | unit tests + artifact verification |
| Section awareness | Headings/section paths improve evidence matching | `audit_chunk_sections.py` + section match metric |
| Semantic recall | Vector retrieval finds conceptually relevant evidence | future `--retriever vector` eval mode |
| Precision/order | Best evidence is ranked higher | reranker eval / top-k deltas |
| Groundedness | Answers cite retrieved evidence and avoid unsupported claims | source-grounding tests |
| Compliance safety | High-risk biological/regulatory outputs are blocked or escalated | compliance guardrail tests |
| Developer velocity | Quality gates catch regressions automatically | GitHub Actions + PR template |

## Current Baseline

Use `docs/MVP004_BASELINE_METRICS.md` as the current known baseline.

Known reference values:

- Unit tests: 41 passed
- Artifact verification: `ok: true`
- Source registry records: 48
- Chunks: 2,821
- Eval questions: 32
- Source file match @3: 34.4%
- Source file match @5: 43.8%
- Source priority match: 43.8%
- Evidence label match: 43.8%
- Section match: 31.2%
- Overall pass rate: 31.2%

These values are a reference point before embeddings, vector DB, hybrid retrieval, reranking, UI, or source-grounded answer generation.

## Improvement Ladder

### MVP-004: Structure Stability

Goal: preserve document structure and source metadata.

Primary improvements:

- better section metadata coverage;
- stable heading context;
- no source/evidence metadata regression.

### MVP-005: Semantic Retrieval Foundation

Goal: add embeddings and vector retrieval without breaking deterministic retrieval.

Primary improvements:

- embedding records preserve metadata;
- vector mode becomes separately measurable;
- semantic recall improves once vector backend is selected.

### MVP-006: Hybrid Retrieval

Goal: combine lexical, metadata, section, and vector signals.

Primary improvements:

- source file match @5 improves;
- overall pass rate improves;
- section match improves or remains stable;
- no traceability metric regresses.

### MVP-007: Reranking

Goal: improve ordering of retrieved evidence.

Primary improvements:

- source file match @3 improves;
- top result quality improves;
- answer-generation context becomes smaller and more relevant.

### MVP-008: Source-Grounded Answer Generation

Goal: answers become useful while staying evidence-bound.

Primary improvements:

- material claims trace to source IDs;
- unsupported claims are refused or labeled;
- insufficient evidence behavior is stable.

### MVP-009: Compliance Guardrails

Goal: prevent unsafe or misleading biological/regulatory outputs.

Primary improvements:

- compliance-risk classification coverage increases;
- high-risk outputs escalate;
- public/investor-facing claims require evidence.

### MVP-010: Internal UI/API

Goal: make the system usable by the Asperitas team.

Primary improvements:

- internal users can inspect evidence;
- retrieval mode, citations, scores, and compliance warnings are visible;
- agent operation does not require code edits.

## Metric Discipline

For every performance task, report:

```text
Performance dimension:
Baseline:
After:
Delta:
Command used:
Regression check:
Interpretation:
Risk:
Next experiment:
```

## Regression Thresholds

Hard regression unless explicitly approved:

- eval cannot run;
- source IDs are dropped;
- evidence labels are dropped;
- source priority is dropped;
- section metadata is lost;
- source file match @5 drops by more than 2 percentage points;
- source priority or evidence label match decreases;
- answer generator produces unsupported claims as facts;
- compliance guardrail allows high-risk unreviewed output.

## Performance Targets By Stage

These are directional targets, not claims of current performance.

| Stage | Target |
|---|---|
| MVP-004 | stable, audited structure-aware chunks |
| MVP-005 | vector mode exists and is comparable |
| MVP-006 | hybrid mode beats baseline on source match @5 or justifies deferral |
| MVP-007 | reranker improves top-3 ordering or is rejected with evidence |
| MVP-008 | answer claims are citation-traceable |
| MVP-009 | compliance risk cases are tested |
| MVP-010 | internal operating loop is usable without code edits |

## Open-Source Performance Policy

Adopt external libraries only when they improve one of the defined performance dimensions and can be isolated behind an interface.

Do not add frameworks for prestige. Add them only when they improve measurable throughput, retrieval quality, reliability, or safety.

## Immediate Next Experiment

Issue #1 records the actual MVP-004 baseline. Issue #2 begins MVP-005 Phase 1. Do not optimize embeddings, vector DB, reranking, or prompts before these two steps are complete.