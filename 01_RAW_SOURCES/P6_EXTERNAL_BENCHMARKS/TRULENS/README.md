# TRULENS Benchmark Notes

Priority: P6 External Benchmark
Use: RAG quality decomposition.

## Source
- TruLens RAG Triad
- URL: https://www.trulens.org/getting_started/core_concepts/rag_triad/

## Patterns to Absorb
RAG answer quality should be decomposed into:
- Context relevance
- Groundedness
- Answer relevance

## Asperitas V1 Application
Map into eval schema:
- context_relevance
- answer_groundedness
- answer_relevance
- citation_support

Use this as a conceptual benchmark for MVP-017, even without adding TruLens as a dependency.
