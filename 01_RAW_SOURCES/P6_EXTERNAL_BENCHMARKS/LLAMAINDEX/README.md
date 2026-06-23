# LLAMAINDEX Benchmark Notes

Priority: P6 External Benchmark
Use: RAG architecture and evaluation reference.

## Sources
1. LlamaIndex RAG guide
   - URL: https://developers.llamaindex.ai/python/framework/understanding/rag/
2. LlamaIndex evaluation docs
   - URL: https://developers.llamaindex.ai/python/framework/module_guides/evaluating/

## Patterns to Absorb
- Separate ingestion, parsing, indexing, retrieval, reranking, synthesis, and evaluation.
- Treat retrieval quality and answer quality as separate measurable layers.
- Use metadata-aware retrieval and node/chunk-level provenance.
- Keep response synthesis grounded in retrieved context.

## Asperitas V1 Application
- Use current repo implementation as custom lightweight RAG.
- Benchmark against LlamaIndex concepts, not necessarily immediate dependency adoption.
- Improve metadata filters, citation mapping, and response evaluation before adding external live connectors.
