# V1.3A Retrieval Diagnostics

This directory contains the deterministic V1.3A retrieval diagnostic baseline.

The baseline is diagnostic-only. It reads the V1.2 golden eval fixture, source registry, chunk artifact, and current read-only retrieval interface. It does not run answer generation, mutate retrieval behavior, mutate ranking, write embeddings, alter vector DB behavior, rerank, ingest sources, rewrite registry data, rewrite chunks, or mutate source artifacts.

Generated with:

```bash
python scripts/diagnose_v1_3a_retrieval_quality.py --overwrite --json
```
