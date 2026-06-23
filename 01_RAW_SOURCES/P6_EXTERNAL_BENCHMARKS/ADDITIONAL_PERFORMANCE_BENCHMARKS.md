# Additional V1 Performance Benchmarks

Status: deep-research source map. Metadata and benchmark notes only. Not full ingestion.

## Why this file exists
The first benchmark pass covered OpenAI, Anthropic, LangGraph, LlamaIndex, RAGAS/ARES, Ginkgo, Recursion, Benchling, GitHub security, and agent security. This second pass adds performance, observability, CI evaluation, prompt optimization, and RAG hardening references needed for a stronger Asperitas Agent V1.

## Added Benchmark Domains

### 1. LangSmith Evaluation / Observability
Source: https://docs.langchain.com/langsmith/evaluation-concepts

Use for:
- Offline evaluation before deployment
- Online evaluation after deployment
- Datasets, examples, experiments, traces, evaluators
- Regression testing and production monitoring

Asperitas application:
- MVP-017 should persist eval runs as artifacts.
- MVP-019 should introduce trace-like records for query -> retrieval -> validation -> answer.
- V1 should separate offline eval datasets from online monitoring logs.

### 2. DeepEval
Source: https://deepeval.com/docs/getting-started

Use for:
- Local eval tests
- CI/CD eval checks
- RAG metrics
- Component-level agent tracing
- Regression comparison

Asperitas application:
- Consider DeepEval-style local tests after current custom evals stabilize.
- Add test files that can run in CI without requiring full production stack.
- Prefer JSON artifact output for reproducibility.

### 3. TruLens RAG Triad
Source: https://www.trulens.org/getting_started/core_concepts/rag_triad/

Use for:
- Context relevance
- Groundedness
- Answer relevance

Asperitas application:
- Map to Asperitas eval schema:
  - context_relevance
  - answer_groundedness
  - answer_relevance
- Use as conceptual benchmark even if not adopting TruLens dependency immediately.

### 4. Arize Phoenix
Source: https://arize.com/docs/phoenix/tracing/llm-traces

Use for:
- LLM traces
- Retrieval spans
- Observability of multi-step RAG/agent systems
- Debugging hallucination and retrieval failures

Asperitas application:
- V1 audit log should mimic tracing: query, retrieved contexts, rerank result, validation, answer, citations.
- Keep initial implementation lightweight and local before adding hosted observability.

### 5. DSPy
Source: https://dspy.ai/

Use for:
- Programmatic prompt/module optimization
- Metric-driven prompt improvement
- Pipeline-level optimization

Asperitas application:
- V1+ can use DSPy-style thinking to optimize retrieval prompts, query rewriting, and answer synthesis against eval metrics.
- Not MVP-016 scope; mark as V1+ optimization layer.

### 6. Haystack
Source: https://haystack.deepset.ai/overview/intro

Use for:
- Modular NLP/RAG pipelines
- Search, retrieval, generation, and evaluation architecture

Asperitas application:
- Use as architecture benchmark for modular components.
- Avoid dependency sprawl unless a clear engineering advantage appears.

### 7. Guardrails AI
Source: https://guardrailsai.com/guardrails/docs

Use for:
- Output validation
- Schema/format enforcement
- Guardrails around generated answers

Asperitas application:
- Compliance/audit answers should pass schema validation.
- High-risk outputs should include required fields: risk domain, evidence status, gate decision, human approval requirement.

### 8. OWASP GenAI Security / LLM Top 10
Source: https://owasp.org/www-project-top-10-for-large-language-model-applications/

Use for:
- Prompt injection
- Insecure output handling
- Supply chain vulnerabilities
- Sensitive information disclosure
- Insecure plugin/tool design
- Excessive agency
- Overreliance

Asperitas application:
- MVP-020 should add security fixtures and refusal/escalation tests.
- Any future connector/MCP should start disabled by default.

### 9. Biomedical RAG Retrieval Benchmarking
Source: https://arxiv.org/abs/2605.02520

Use for:
- Dense retrieval vs hybrid retrieval vs cross-encoder reranking vs multi-query expansion vs MMR
- Biomedical RAG evaluation metrics

Asperitas application:
- MVP-017/018 should compare current retrieval against at least one stronger baseline.
- Target future eval dimensions: contextual precision, contextual recall, faithfulness, answer relevance.

### 10. RAG Poisoning / Indirect Prompt Injection Benchmarks
Sources:
- https://arxiv.org/abs/2505.18543
- https://arxiv.org/abs/2511.15759
- https://arxiv.org/abs/2601.10923

Use for:
- RAG source poisoning tests
- Indirect prompt injection tests
- Retrieval-time and answer-time attack evaluation

Asperitas application:
- Create adversarial source fixtures.
- Ensure retrieved text cannot override AGENTS.md, AOS, or compliance gates.
- Add source sanitization and instruction-boundary tests.

## New Recommended V1 Benchmark Stack

Tier S - implement or directly model before V1:
1. Existing custom eval baseline
2. RAGAS / ARES concepts
3. LangGraph-style workflow decomposition
4. OpenAI/Anthropic-style skills
5. OWASP LLM security controls
6. GitHub CI/security controls

Tier A - use as design benchmark during V1:
1. LangSmith evaluation lifecycle
2. DeepEval local eval/CI pattern
3. TruLens RAG Triad
4. Phoenix tracing model
5. Guardrails output validation

Tier B - V1+ optimization:
1. DSPy optimization
2. Haystack modular pipeline comparison
3. Biomedical retrieval strategy benchmark
4. RAG poisoning/adversarial benchmark expansion

## V1 Acceptance Criteria Additions
- Eval artifacts are saved and comparable across MVPs.
- Each RAG answer can be traced to retrieved context and citations.
- Unsupported claims are measurable.
- Prompt injection and source poisoning fixtures exist.
- High-risk bio/compliance/legal outputs trigger gates.
- Skills are invoked for repeated development workflows.
- External benchmark sources remain metadata-only until ingestion/license review.
