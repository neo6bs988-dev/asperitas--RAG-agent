# Roadmap

## MVP-001 Foundation

Establish the initial repository, development workflow, and baseline project structure for the Asperitas RAG agent.

## MVP-002 Retrieval Structure

Define the first retrieval pipeline structure, including document loading, indexing boundaries, and query-time retrieval flow.

## MVP-002.5 Evaluation Baseline

Create baseline retrieval evaluation so future changes can be measured against repeatable metrics.

## MVP-003 Metadata-Aware Retrieval

Use document and chunk metadata to improve filtering, attribution, retrieval quality, and source traceability.

## MVP-004 Structure-Aware Chunking

Improve chunking so document structure, biological context, headings, tables, methods, and source boundaries are preserved more effectively.

## MVP-005 Embeddings + Vector DB

Add production-oriented embedding generation and vector database storage for scalable semantic retrieval.

## MVP-006 Hybrid Retrieval

Combine semantic vector retrieval with lexical or metadata-aware retrieval to improve recall and precision.

## MVP-007 Reranker

Add a reranking stage to improve the ordering and relevance of retrieved evidence before answer generation.

## MVP-008 Source-Grounded Answer Generation

Generate answers only from retrieved source evidence, with citations and clear handling of insufficient evidence.

## MVP-009 Compliance Guardrails

Add guardrails for biological intelligence use cases, including source constraints, uncertainty handling, and compliance-aware refusal or escalation behavior.

## MVP-010 Internal UI/API

Provide an internal interface and API for testing, reviewing, and operating the RAG agent.
