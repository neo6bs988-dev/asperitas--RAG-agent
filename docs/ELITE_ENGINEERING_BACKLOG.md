# Elite Engineering Backlog

Purpose: define the highest-leverage engineering upgrades for the first Asperitas RAG Agent, ordered by compounding value, safety, and evaluation leverage.

This backlog is intentionally conservative about dependencies. The goal is not to look sophisticated. The goal is to build a system that becomes harder to break, easier to evaluate, and more valuable with every MVP.

## Operating Principle

Do the work in this order:

1. Make behavior measurable.
2. Preserve source-grounding metadata.
3. Add interfaces before external dependencies.
4. Add deterministic tests before API integrations.
5. Add local adapters before production infrastructure.
6. Add production tools only after eval proves the need.
7. Record every architecture decision.

## Tier 0: Must Not Break

These are permanent invariants.

- Existing deterministic retrieval remains available.
- Source IDs survive every pipeline stage.
- Evidence labels survive every pipeline stage.
- Source priority survives every pipeline stage.
- Section metadata survives chunking, embedding, indexing, retrieval, reranking, and answer generation.
- No external API key is required for tests.
- No secret, credential, private endpoint, or large binary index is committed.
- Every retrieval-affecting change produces metrics.

## Tier 1: Immediate High-Leverage Tasks

### 1. Finalize MVP-004 Baseline

Run the full quality gate and record final observed metrics.

Why: embeddings/vector DB work is meaningless without a baseline.

Gate:

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/audit_chunk_sections.py --json
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
```

### 2. MVP-005 Phase 1: Embedding Record Schema

Why: vector search fails as a product if metadata is lost.

Adopted open-source pattern: vector systems store vectors separately from metadata payloads; Asperitas must treat metadata payload preservation as a first-class requirement.

### 3. MVP-005 Phase 2: Offline Embedding Provider Boundary

Why: tests must not depend on external APIs or paid services.

Adopted pattern: provider interface + deterministic test double.

### 4. MVP-005 Phase 3: Local Vector Store Adapter

Why: vector search semantics can be tested before choosing Chroma, Qdrant, FAISS, or Weaviate.

Adopted pattern: storage adapter boundary.

### 5. MVP-005 Phase 4: Vector Eval Mode

Why: vector retrieval must be measured separately from baseline and metadata-aware retrieval.

Adopted pattern: comparable retriever modes.

## Tier 2: Production Readiness Gates

### Dependency Security Gate

Add a dependency review process before any external package is added.

Candidate tooling later:

- `pip-audit` for dependency vulnerabilities.
- `ruff` for fast linting and formatting.
- `mypy` or `pyright` for type checks when the codebase stabilizes.
- GitHub Dependabot once dependency policy is stable.

Do not add all tools at once. Add one gate at a time and keep CI fast.

### Architecture Decision Records

Create one decision log per major irreversible choice:

- embedding model boundary;
- vector DB selection;
- reranker selection;
- answer-generation citation contract;
- compliance redaction policy.

### Eval Artifact Storage

Store machine-readable eval outputs from CI as artifacts.

Purpose: compare metrics over time instead of relying on screenshots or memory.

## Tier 3: External Open-Source Adoption Sequence

### Vector Backend

Candidates:

- Qdrant: production vector DB candidate.
- Chroma: local prototype candidate.
- FAISS: local high-performance index candidate.
- Weaviate: schema-rich semantic search candidate.

Decision only after internal vector adapter and vector eval mode exist.

### RAG Evaluation

Candidate: Ragas-style metrics.

Adopt after source-grounded answer generation exists. Do not replace current deterministic eval before answer generation is implemented.

### Prompt/Program Optimization

Candidate: DSPy-style optimization.

Adopt after there is a stable answer-generation module and an evaluation dataset large enough to optimize against.

### Agent Orchestration

Candidate: LangGraph-style state machine.

Adopt after one agent works reliably. Do not introduce multi-agent graph complexity before the first RAG agent has stable retrieval, citations, evals, and compliance gates.

### RAG Framework Abstractions

Candidates: LangChain and LlamaIndex.

Use as architecture references. Do not migrate the project into a framework unless the framework solves a demonstrated bottleneck.

## Tier 4: First Agent Completion Definition

The first Asperitas RAG Agent is not complete until it can:

1. ingest structured sources;
2. preserve metadata through chunking;
3. retrieve evidence deterministically;
4. compare retrieval modes through eval;
5. preserve source-grounding through answer generation;
6. cite source IDs and evidence labels;
7. refuse or label unsupported claims;
8. pass compliance/biosafety review gates;
9. produce reproducible quality reports;
10. run CI on every push/PR.

## What Not To Do

- Do not install LangChain just to look advanced.
- Do not install a production vector DB before local adapter tests exist.
- Do not add an LLM answer generator before citation contracts are defined.
- Do not optimize prompts before evaluation data exists.
- Do not build multi-agent orchestration before the first single-agent pipeline works.
- Do not treat a demo as infrastructure.

## Current Next Action

Execute Issue #1, then Issue #2.

If Issue #1 passes, move to MVP-005 Phase 1.

If Issue #1 fails, fix the quality gate before adding any external library or architecture complexity.