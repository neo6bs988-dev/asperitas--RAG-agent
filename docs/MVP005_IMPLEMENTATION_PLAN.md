# MVP-005 Implementation Plan: Embeddings + Vector DB

Purpose: move from deterministic TF-IDF/metadata-aware retrieval toward embedding-backed retrieval without breaking source-grounding, evaluation, or compliance traceability.

## Entry Criteria

Before starting MVP-005:

- MVP-004 section metadata is stable or explicitly accepted as baseline.
- `python -m pytest` passes.
- `python scripts/verify_artifacts.py` passes.
- `python scripts/audit_chunk_sections.py --json` runs.
- Baseline and MVP-003 retrieval evals run.
- Current metrics are recorded in a decision log or task report.

## Non-Negotiables

- Do not remove deterministic TF-IDF retrieval.
- Do not replace MVP-003 retrieval silently.
- Add vector retrieval as a new mode or adapter.
- Preserve source IDs, source file, source priority, evidence label, section metadata, and heading context.
- Do not commit API keys, credentials, local index binaries, or paid-service secrets.
- Keep eval comparison possible across retrievers.

## Proposed MVP-005 Phases

### Phase 1: Embedding Schema

Create a schema for embedding records.

Required fields:

- `chunk_id`
- `source_id`
- `source_file`
- `source_priority`
- `evidence_label`
- `section`
- `section_heading`
- `section_path`
- `heading_context`
- `embedding_model`
- `embedding_dim`
- `embedding_version`
- `content_hash`

Acceptance:

- tests prove metadata is preserved from chunks into embedding records.

### Phase 2: Embedding Provider Boundary

Add an interface that supports:

- deterministic test embeddings;
- future external embeddings;
- no required API key for tests;
- reproducible fixture behavior.

Acceptance:

- tests run offline.
- no secrets are needed.

### Phase 3: Vector Store Adapter

Add a vector store boundary before selecting a production DB.

Initial recommendation:

- start with local in-memory or file-backed adapter for tests;
- delay Chroma/Qdrant/Weaviate choice until eval can compare retrieval modes.

Acceptance:

- vector search can return ranked chunks with metadata intact.

### Phase 4: Eval Mode

Extend retrieval eval with a new retriever mode such as:

```bash
python scripts/run_retrieval_eval.py --retriever vector --limit 5
```

If full vector mode is not ready, add a simulated/fixture-based vector eval first.

Acceptance:

- old baseline modes still work;
- vector mode is separately measurable;
- report includes metric deltas.

### Phase 5: Hybrid Retrieval Decision

Only after vector retrieval works, decide whether to combine:

- lexical TF-IDF;
- metadata-aware scoring;
- vector similarity;
- section-aware boosts;
- reranker candidate stage.

Acceptance:

- hybrid mode must beat or preserve source/evidence traceability.

## Quality Gate Commands

Run before closing MVP-005 tasks:

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/audit_chunk_sections.py --json
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
```

When vector mode exists, add:

```bash
python scripts/run_retrieval_eval.py --retriever vector --limit 5
```

## Codex Prompt For First MVP-005 Task

```text
Use AGENTS.md, .agents/skills/asperitas-rag-development/SKILL.md, .agents/skills/retrieval-eval-quality-gate/SKILL.md, and .agents/skills/embeddings-vector-db-mvp005/SKILL.md.

Task:
Implement Phase 1 of MVP-005: embedding record schema and metadata-preservation tests.

Constraints:
- Do not call external embedding APIs.
- Do not add API keys or secrets.
- Do not remove existing retrieval modes.
- Preserve all source-grounding metadata from chunks.
- Add tests for schema and metadata preservation.
- Run pytest and artifact verification.
- Run retrieval eval only if retrieval behavior changes.

Report:
1. files changed
2. schema fields added
3. metadata preservation proof
4. tests run
5. retrieval eval status
6. risks
7. next MVP-005 phase
```

## Decision Point

Before choosing a production vector DB, compare:

| Option | Good For | Risk |
|---|---|---|
| In-memory adapter | tests, simple baseline | not production-ready |
| Chroma | fast local prototyping | persistence/versioning discipline needed |
| Qdrant | production-grade vector search | operational setup needed |
| Weaviate | richer semantic DB features | heavier platform choice |
| FAISS | local high-performance indexing | metadata persistence must be built carefully |

Default recommendation: start with an interface + deterministic test embeddings + local adapter. Choose production vector DB only after eval mode exists.