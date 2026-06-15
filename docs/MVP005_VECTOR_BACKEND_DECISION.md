# MVP-005 Vector Backend Decision

Date: 2026-06-15

Related issue: #6

## Decision

Defer adding an external vector database dependency. Improve the embedding strategy first, then prototype Qdrant behind the existing `VectorStore` boundary only if vector eval improves enough to justify a backend dependency.

Current measured retrieval quality:

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 34.4% | 34.4% | 43.8% | 43.8% | 43.8% | 34.4% |
| mvp003 | 90.6% | 96.9% | 100.0% | 100.0% | 100.0% | 90.6% |
| vector | 31.2% | 34.4% | 40.6% | 40.6% | 40.6% | 31.2% |

The external backend should not be selected until vector retrieval beats or complements the existing deterministic path. `mvp003` remains the production-quality internal retrieval reference for now.

## Candidate Matrix

| Candidate | License | Local/offline support | Metadata filtering | Hybrid search support | Operational complexity | Python integration | CI/test burden | Deployment burden | Asperitas fit | Boundary compatibility |
|---|---|---|---|---|---|---|---|---|---|---|
| Qdrant / qdrant-client | Apache-2.0 for server and client | Strong: client local mode can run in memory or persist locally; server can run by Docker | Strong payload filtering with JSON payloads and boolean clauses | Strong: dense, sparse, multivector, RRF/DBSF style fusion | Medium: local mode first, Docker/server later | Strong typed Python client | Medium: local mode can keep CI offline; server tests should be optional | Medium: Docker/server for deployment, local mode for prototype | Best later fit for source-grounded RAG with metadata payloads and hybrid path | Good: `EmbeddingRecord` maps cleanly to payload; adapter can implement `VectorStore` |
| FAISS | MIT | Strong local library | Weak natively: metadata store/filtering must remain in Asperitas code | Weak natively: vector index only; hybrid fusion must be built outside FAISS | Low to medium for local index; higher for metadata correctness | Strong Python wrappers with NumPy | Medium: compiled/native package can complicate Windows/CI | Low for local-only, higher for persistence and metadata store | Good for speed experiments, weak as source-grounded metadata store | Partial: vector search fits, metadata/citation payload must be sidecar-managed |
| Chroma | Apache-2.0 | Strong local prototype path with in-memory and persistent clients | Good metadata `where` filtering | Moderate: cloud advertises hybrid/full-text; local hybrid maturity must be verified before relying on it | Low for prototype; medium if server/cloud enters | Simple Python API | Medium: dependency tree and local persistence behavior need testing | Low to medium | Good developer prototype, less compelling than Qdrant for strict source-grounding and future production | Good: records map to ids, documents, and metadata |
| Weaviate | BSD-3-Clause | Medium: Docker local is solid; embedded mode exists but is experimental | Strong structured filtering | Strong built-in hybrid search with tunable vector/keyword weighting and filters | High: schema, server lifecycle, modules, Docker/Kubernetes options | Strong Python client | High: likely service/container tests unless embedded is accepted | High | Strong long-term semantic platform, too heavy for MVP-005 prototype decision | Good conceptually, but adapter and schema mapping are heavier |

## Why Vector Underperformed

The MVP-005 vector eval mode is intentionally offline and deterministic. It currently uses hash-derived test embeddings rather than a semantic embedding model. Hash vectors are stable and useful for plumbing tests, but they do not encode biological, strategic, compliance, or source-priority meaning.

The current vector mode also lacks the metadata-aware boosts that make `mvp003` strong:

- no source-priority ranking boost;
- no expected source filename/path hinting;
- no section-aware deterministic scoring;
- no evidence-label preference;
- no hybrid lexical signal strong enough to recover exact source matches.

Therefore the bottleneck is embedding quality and scoring strategy, not vector database storage. Replacing `InMemoryVectorStore` with Qdrant, FAISS, Chroma, or Weaviate would mostly preserve the same weak vectors and likely reproduce weak ranking.

## Recommended Embedding Strategy

1. Keep `baseline`, `mvp003`, and `vector` modes separate.
2. Keep `DeterministicOfflineEmbeddingProvider` as the CI/test double.
3. Add a pluggable local semantic embedding provider next, without external APIs or secrets.
4. Require generated vectors to include `embedding_model`, `embedding_dim`, `embedding_version`, and `content_hash`.
5. Compare semantic-vector eval against the current three modes before any backend dependency is installed.
6. Only prototype Qdrant after vector retrieval proves useful or after hybrid retrieval needs payload-filtered vector storage.

Minimum acceptance for backend prototype:

- existing `mvp003` metrics unchanged;
- vector or hybrid-vector mode improves over baseline on overall pass rate or explains why it is only a recall candidate;
- returned results preserve `source_id`, `source_file`, `source_priority`, `evidence_label`, `section`, `section_heading`, `section_path`, `heading_context`, `embedding_model`, `embedding_dim`, `embedding_version`, and `content_hash`;
- no API keys, endpoints, credentials, cloud resources, or binary indexes are committed.

## Dependency And Security Review

No dependency was added in this decision.

Before adding any backend:

- pin the smallest viable package scope;
- run dependency audit for known vulnerabilities and transitive package risk;
- keep tests offline by default;
- forbid committed server URLs, API keys, cloud credentials, and generated index directories;
- add `.gitignore` entries for local index/output paths before any persistence experiment;
- keep all backend code behind `VectorStore` or a compatible adapter boundary.

## Rollback Path

If a backend prototype regresses retrieval quality or complicates CI:

1. Remove the backend adapter and dependency from package manifests.
2. Keep `InMemoryVectorStore` as the default vector test implementation.
3. Keep `baseline`, `mvp003`, and current `vector` eval commands callable.
4. Delete only generated local indexes explicitly created by the prototype, never source files.
5. Re-run `python -m pytest`, `python scripts/verify_artifacts.py`, and all retrieval eval modes.

## Eval Plan

Required commands for any future backend or embedding change:

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever vector --limit 5
```

For a backend prototype, add a separately labeled retriever or adapter setting. Do not replace `mvp003`.

## Sources Checked

- [Qdrant repository](https://github.com/qdrant/qdrant), [Qdrant client repository](https://github.com/qdrant/qdrant-client), and [Qdrant license](https://raw.githubusercontent.com/qdrant/qdrant/master/LICENSE): Apache-2.0 license, payload filtering, dense/sparse/multivector search, hybrid search, and local Python client mode.
- [FAISS documentation](https://faiss.ai/index.html) and [FAISS license](https://raw.githubusercontent.com/facebookresearch/faiss/main/LICENSE): MIT license, efficient dense-vector similarity search, C++ core with Python wrappers.
- [Chroma repository](https://github.com/chroma-core/chroma), [Chroma metadata filtering docs](https://docs.trychroma.com/docs/querying-collections/metadata-filtering), and [Chroma license](https://raw.githubusercontent.com/chroma-core/chroma/main/LICENSE): Apache-2.0 license, in-memory prototype API, metadata filtering with `where`.
- [Weaviate repository](https://github.com/weaviate/weaviate), [Weaviate hybrid search docs](https://docs.weaviate.io/weaviate/search/hybrid), [Weaviate embedded docs](https://docs.weaviate.io/deploy/installation-guides/embedded), and [Weaviate license](https://raw.githubusercontent.com/weaviate/weaviate/master/LICENSE): BSD 3-Clause license, structured filtering, hybrid vector/keyword search, Docker and embedded deployment options.
