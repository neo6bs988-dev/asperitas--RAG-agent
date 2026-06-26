# V1.3B-1 Source Coverage Backfill

This directory contains the deterministic before/after source-coverage report for V1.3B-1.

The backfill is limited to existing repository governance/eval documents referenced by the V1.2 answer-quality fixture. It does not add external sources, tune retrieval ranking, change embeddings/vector DB behavior, change reranking, or change answer generation.

Generated with:

```bash
python scripts/backfill_v1_3b_source_coverage.py --overwrite --json
python scripts/diagnose_v1_3a_retrieval_quality.py --overwrite --json
```
