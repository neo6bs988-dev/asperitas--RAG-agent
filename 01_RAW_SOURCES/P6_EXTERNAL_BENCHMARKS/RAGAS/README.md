# RAGAS / ARES Benchmark Notes

Priority: P6 External Benchmark
Use: RAG evaluation layer for MVP-017.

## Sources
1. RAGAS paper
   - URL: https://arxiv.org/abs/2309.15217
2. RAGAS docs
   - URL: https://docs.ragas.io
3. ARES paper
   - URL: https://arxiv.org/abs/2311.09476

## Evaluation Concepts
- Faithfulness: whether answer claims are supported by retrieved context.
- Answer relevance: whether the answer directly addresses the question.
- Context precision: whether retrieved contexts are focused and useful.
- Context recall: whether necessary supporting context was retrieved.

## Asperitas V1 Application
Current eval should be extended from top-k retrieval/evidence checks into:

```text
retrieval_recall
context_precision
context_recall
faithfulness
answer_relevance
citation_coverage
unsupported_claim_rate
```

## Stop Rule
Do not use LLM-generated evaluation scores as final truth. Treat them as diagnostic signals that require calibration with hand-labeled eval questions.
