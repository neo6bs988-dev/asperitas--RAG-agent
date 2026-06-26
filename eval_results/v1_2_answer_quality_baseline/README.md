# V1.2B Answer Quality Baseline Results

This folder stores the deterministic V1.2B fixture coverage baseline artifact.

Current artifact:

- `baseline_fixture_coverage.json`

The artifact is measurement-only. It is generated from `docs/evals/V1_2_GOLDEN_EVAL_SET.json` and does not run retrieval, ranking, embeddings, vector DB behavior, reranking, answer generation, source ingestion, model judging, or manual score assignment.

Current status: fixture coverage baseline, not answer-performance baseline.

Regenerate with:

```powershell
python scripts/run_v1_2_answer_quality_eval.py --overwrite
```
