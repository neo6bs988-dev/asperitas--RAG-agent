# V1.0.0 Internal Dry-run Decision Log

Date: 2026-06-25

Decision: add a reproducible internal dry-run packet before considering `v1.0.0-internal`.

Reason: the previous dry-run depended on `.pytest_tmp/final_pre_rc_security_guard_input.json`, which can be removed by pytest cleanup and is not valid release evidence. The new packet generates deterministic inputs inside `scripts/run_v1_internal_dry_run.py` and writes nothing unless `--output` is explicit.

Scope:

- release readiness check
- clean security guard check
- prompt-injection block check
- chat dry-run check
- audit serialization check
- no `.pytest_tmp` dependency

Non-scope:

- no tag creation
- no GitHub release creation
- no public SaaS or production readiness claim
- no real answer provider wiring
- no retrieval, chunking, source registry, eval fixture, embedding, vector, reranker, answer, or default runtime behavior change

Deferred:

- V1.1A failure log collector
- V1.1B local/internal web dogfood UI
- V1.1C real RAG answer provider integration
- V1.1D retrieval/answer baseline
