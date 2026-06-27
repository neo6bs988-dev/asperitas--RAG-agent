# V1.4C Latency Eval Harness Caching Report

## Executive bottom line

V1.4C adds deterministic in-process caching for local eval and measurement harnesses only. Production answer behavior, retrieval scoring, source artifacts, embeddings, vector DB behavior, and reranking remain out of scope.

## Runtime delta

- V1.4A baseline runtime: 60567.527 ms -> 61635.099 ms (1067.572 ms, 1.763%)
- V1.4B compression check runtime: 119934.037 ms -> 119715.339 ms (-218.698 ms, -0.182%)
- Golden eval runtime: 29056.645 ms -> 30233.339 ms (1176.694 ms, 4.05%)
- Retrieval eval runtime: 101048.315 ms -> 101936.102 ms (887.787 ms, 0.879%)
- Cache hit count: 108
- Measurable latency improvement: False
- Documented no-op: True

## Cache targets

- source registry CSV reads
- chunks JSONL reads
- retrieval/golden fixture JSONL reads
- repeated evidence pack assembly in local measurement harnesses

## Invalidation

In-process cache keys include resolved path, file size, creation time, and mtime for file-backed data; evidence-pack cache keys include query, top_k, snippet config, and retrieval-result fingerprints.

## Scope lock

- eval_harness_only: True
- answer_behavior_changed: False
- retrieval_scoring_changed: False
- source_artifacts_mutated: False
- production_cache_claim: False

## Truth boundary

This check measures deterministic local eval-harness caching only. It does not change retrieval ranking, answer content, source ingestion, embeddings, vector DB behavior, reranking, or production caching.
