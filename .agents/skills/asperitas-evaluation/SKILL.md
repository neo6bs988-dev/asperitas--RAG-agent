---
name: asperitas-evaluation
description: Use when adding or modifying evals, RAGAS-style metrics, retrieval baselines, answer faithfulness checks, or MVP performance reporting.
---

# Asperitas Evaluation Skill

## Purpose
Convert agent quality from subjective impressions into repeatable metrics.

## Benchmark References
- RAGAS: faithfulness, answer relevance, context precision, context recall.
- ARES: automated RAG evaluation concepts.
- Existing Asperitas eval baseline: preserve continuity with current metrics.

## Workflow
1. Read existing eval scripts, fixtures, and baseline metric files.
2. Keep existing metrics working before adding new metrics.
3. Add metrics incrementally:
   - retrieval_recall
   - context_precision
   - context_recall
   - faithfulness
   - answer_relevance
   - citation_coverage
   - claim_support_rate
4. Add hand-labeled eval questions for calibration.
5. Save before/after metrics in a reproducible artifact.
6. Document metric limitations clearly.

## Output Requirements
Report:
1. Objective
2. Eval files changed
3. Metrics added or changed
4. Commands run
5. Before and after results
6. Failure cases discovered
7. Calibration risks
8. Next eval improvement

## Stop Rules
- Do not treat LLM evaluation as ground truth.
- Do not remove existing metrics without replacement and explanation.
- Do not compare metrics across incompatible eval sets without saying so.
