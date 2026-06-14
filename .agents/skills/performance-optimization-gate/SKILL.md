---
name: performance-optimization-gate
description: Use whenever a task claims retrieval, ranking, latency, groundedness, compliance safety, or developer workflow performance improvement.
---

# Performance Optimization Gate

## When To Use

- A task claims performance improvement.
- Retrieval, chunking, embeddings, vector search, hybrid scoring, reranking, or answer generation changes.
- CI, eval, testing, or developer workflow changes are intended to improve velocity or reliability.
- Open-source adoption is justified by performance.

## When Not To Use

- Pure wording changes with no behavioral or workflow impact.
- Planning discussions with no implementation or measurable claim.
- Cosmetic docs edits that do not claim improved quality.

## Required Inputs

- Performance dimension under improvement.
- Baseline metric or current behavior.
- Expected improvement.
- Command or test used to measure the change.
- Files affected.
- Known regression risks.

## Workflow Steps

1. Name the exact performance dimension.
2. Identify the current baseline.
3. Define the expected improvement before editing.
4. Make the smallest safe change.
5. Run the relevant test or eval command.
6. Compare before/after results.
7. Check source-grounding and compliance invariants.
8. Decide: accept, conditional, reject, or defer.
9. Record the result and next experiment.

## Quality Gates

- No performance claim without measurement or explicit caveat.
- No retrieval optimization without eval output.
- No ranking optimization without top-k comparison.
- No answer quality claim without source-grounding check.
- No compliance safety claim without risk case coverage.
- No developer velocity claim without CI/test/workflow evidence.

## Report Format

- Performance dimension:
- Baseline:
- After:
- Delta:
- Command/test:
- Files changed:
- Regression check:
- Source-grounding impact:
- Compliance impact:
- Decision:
- Next experiment:

## Failure Conditions

- Claimed improvement is not measured.
- Metrics are invented or selectively reported.
- Source-grounding metadata regresses.
- Compliance risk increases without escalation.
- CI/test reliability worsens without justification.
- Heavy dependency is added before proving need.

## Next-Step Recommendation Format

- Next performance task:
- Target metric:
- Required command:
- Blocking risk:
- Expected decision point:
