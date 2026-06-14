# Open Source Adoption Matrix

Purpose: safely absorb best-practice patterns from high-quality open-source AI/RAG infrastructure without blindly copying code into the Asperitas RAG Agent.

## Policy

Do not vendor or copy external source code directly unless all of the following are true:

1. License is reviewed and compatible with Asperitas use.
2. Security and dependency risks are reviewed.
3. The copied code is necessary; a clean-room implementation or dependency boundary is not sufficient.
4. Tests are added.
5. Retrieval/source-grounding/compliance gates are run when relevant.
6. The adoption decision is recorded in a decision log.

Default approach: learn architecture and API patterns, then implement minimal internal adapters that preserve our source-grounding metadata and eval pipeline.

## Candidate Repositories

| Area | Candidate | Repository | Adopt Now? | Recommended Use |
|---|---|---|---|---|
| LLM app framework | LangChain | `langchain-ai/langchain` | No direct dependency yet | Study chain/tool abstraction, document-loader patterns, and integration boundaries. Avoid large dependency surface until needed. |
| Agent graph orchestration | LangGraph | `langchain-ai/langgraph` | Not yet | Study state-machine/graph concepts later for multi-agent workflows after RAG core stabilizes. |
| RAG/data framework | LlamaIndex | `run-llama/llama_index` | Not yet | Study node/index/query engine abstractions; avoid replacing existing deterministic pipeline prematurely. |
| Vector DB | Qdrant | `qdrant/qdrant` / `qdrant/qdrant-client` | Candidate for MVP-005/006 | Strong production candidate after local vector adapter and eval mode exist. |
| Local vector DB | Chroma | `chroma-core/chroma` | Candidate for prototype | Good prototyping candidate, but introduce only behind vector store interface. |
| Semantic vector DB | Weaviate | `weaviate/weaviate` | Later | Consider when schema-rich semantic DB features are needed. Higher operational weight. |
| Vector index | FAISS | `facebookresearch/faiss` | Later / optional | Consider for local high-performance indexing; metadata persistence must be handled by our code. |
| Prompt/program optimization | DSPy | `stanfordnlp/dspy` | Later | Study optimization/evaluation patterns after answer-generation exists. |
| RAG evaluation | Ragas | `vibrantlabsai/ragas` | Later | Study RAG eval metrics after internal deterministic eval is stable. Do not replace current eval yet. |

## Immediate Adoption For First Agent

The first Asperitas agent is the RAG core. The immediate adoption target is not a framework migration. It is the following safe pattern set:

1. Adapter boundaries before dependencies.
2. Deterministic offline test doubles before external APIs.
3. Vector retrieval as a new mode, not a replacement.
4. Metadata-preserving records for embeddings and vector results.
5. Eval comparability across `baseline`, `mvp003`, and future `vector` retrievers.
6. License/security review before adding any third-party dependency.

## MVP-005 Adoption Sequence

### Step 1: Clean Internal Schema

Implement embedding record schema and metadata preservation tests.

No external dependency required.

### Step 2: Provider Interface

Add an embedding provider boundary with deterministic offline embedding provider.

No external API required.

### Step 3: Local Vector Adapter

Implement local in-memory vector adapter for tests.

No production DB required.

### Step 4: Eval Mode

Add `--retriever vector` mode to the retrieval eval pipeline.

### Step 5: Choose Dependency

Only after vector eval exists, compare:

- Chroma for local prototype;
- Qdrant for production vector DB;
- FAISS for local index speed;
- Weaviate for schema-rich semantic search.

Decision rule: choose the lowest-operational-risk option that improves retrieval metrics without degrading source-grounding.

## Open Source Review Checklist

Before adding any dependency:

- Repository is active and not archived.
- License is compatible.
- Dependency tree is acceptable.
- Security advisories are checked.
- API can be wrapped behind our interface.
- Existing tests remain offline and deterministic.
- No secrets or API keys are required for tests.
- Source IDs, source priority, evidence labels, and section metadata are preserved.
- Retrieval eval can compare before/after metrics.
- Rollback path exists.

## Codex Instruction

When asked to apply open source patterns:

1. Do not clone or vendor code directly.
2. Inspect the relevant internal files first.
3. Identify the minimal pattern to adopt.
4. Implement an internal interface or adapter.
5. Add tests.
6. Run quality gates.
7. Report which external repo influenced the design.
8. State whether any external code was copied. Default should be no.

## Current Recommendation

For the next technical task, continue with MVP-005 Phase 1. It already follows the safest open-source-derived architecture pattern: schema first, provider boundary second, vector adapter third, dependency choice last.