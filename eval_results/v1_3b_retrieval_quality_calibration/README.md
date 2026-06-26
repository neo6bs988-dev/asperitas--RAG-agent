# V1.3B-2 Retrieval Quality Calibration

This directory contains the deterministic before/after retrieval quality report for V1.3B-2.

The report compares the committed V1.3B-1 post-backfill diagnostic baseline with the current calibrated retriever. It measures retrieval ranking/selection only. It does not score answer quality, mutate source artifacts, run answer generation, change embeddings/vector DB behavior, or apply a reranker.

Generated with:

```bash
python scripts/calibrate_v1_3b_retrieval_quality.py --overwrite --json
```
