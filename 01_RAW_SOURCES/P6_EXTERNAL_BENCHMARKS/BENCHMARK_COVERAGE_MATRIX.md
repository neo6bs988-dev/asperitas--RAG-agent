# Final Benchmark Coverage Matrix

Status: final coverage check for MVP-016 readiness.
Purpose: prove that the benchmark set required for V1 is represented in repo-level source notes and Codex skills.

## Coverage Summary

| Required area | Repo coverage | Local files |
|---|---:|---|
| OpenAI Codex Skills Docs | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `OPENAI/README.md`, `.agents/skills/*` |
| OpenAI Skills GitHub | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `SOURCE_MANIFEST.md` |
| OpenAI Agent SDK Docs | Covered | `V1_FINAL_BENCHMARK_PACK.md` |
| OpenAI Evals Docs | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `RAGAS/README.md`, `asperitas-evaluation/SKILL.md` |
| OpenAI Function Calling Docs | Covered | `V1_FINAL_BENCHMARK_PACK.md` |
| Anthropic Skills Docs | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `ANTHROPIC/README.md` |
| Anthropic Skills GitHub | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `SOURCE_MANIFEST.md` |
| Anthropic MCP Docs | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `ANTHROPIC/README.md`, `asperitas-mcp-expansion/SKILL.md` |
| Anthropic Subagent Docs | Covered | `V1_FINAL_BENCHMARK_PACK.md` |
| LangGraph Workflows / Agents | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `LANGGRAPH/README.md`, `asperitas-workflow/SKILL.md` |
| LangGraph Persistence | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `LANGGRAPH/README.md`, `asperitas-audit-trace/SKILL.md` |
| LangGraph GitHub | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `SOURCE_MANIFEST.md` |
| LlamaIndex RAG Docs | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `LLAMAINDEX/README.md` |
| LlamaIndex Retriever Docs | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `LLAMAINDEX/README.md` |
| LlamaIndex Evaluation Docs | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `LLAMAINDEX/README.md`, `asperitas-evaluation/SKILL.md` |
| LlamaIndex GitHub | Covered | `V1_FINAL_BENCHMARK_PACK.md` |
| RAGAS Paper / PDF URL | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `RAGAS/README.md` |
| RAGAS Docs / GitHub | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `RAGAS/README.md` |
| ARES Paper / PDF URL | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `RAGAS/README.md` |
| Ginkgo GPT-5 Autonomous Lab paper | Covered by reference | `V1_FINAL_BENCHMARK_PACK.md`, `GINKGO/README.md` |
| Benchling architecture docs | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `BENCHLING/README.md` |
| Recursion data flywheel docs | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `RECURSION/README.md` |
| GitHub Actions Docs | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `GITHUB_SECURITY/README.md` |
| GitHub Code Security Docs | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `GITHUB_SECURITY/README.md` |
| OWASP GenAI / LLM Top 10 | Covered | `V1_FINAL_BENCHMARK_PACK.md`, `AGENT_SECURITY/README.md` |
| RAG adversarial / poisoning papers | Covered by URL map | `SECURITY_BENCHMARK_SOURCES.md`, `ADDITIONAL_PERFORMANCE_BENCHMARKS.md` |
| MCP security references | Covered by URL map | `SECURITY_BENCHMARK_SOURCES.md`, `asperitas-mcp-expansion/SKILL.md` |
| LangSmith eval lifecycle | Covered | `ADDITIONAL_PERFORMANCE_BENCHMARKS.md`, `LANGSMITH/README.md` |
| DeepEval local/CI eval | Covered | `ADDITIONAL_PERFORMANCE_BENCHMARKS.md`, `DEEPEVAL/README.md` |
| TruLens RAG triad | Covered | `ADDITIONAL_PERFORMANCE_BENCHMARKS.md`, `TRULENS/README.md` |
| Phoenix tracing | Covered | `ADDITIONAL_PERFORMANCE_BENCHMARKS.md`, `PHOENIX/README.md` |
| DSPy optimization | Covered as V1+ | `ADDITIONAL_PERFORMANCE_BENCHMARKS.md`, `DSPY/README.md` |
| Haystack modular pipeline | Covered as V1+ | `ADDITIONAL_PERFORMANCE_BENCHMARKS.md`, `HAYSTACK/README.md` |
| Guardrails / schema validation | Covered | `ADDITIONAL_PERFORMANCE_BENCHMARKS.md`, `GUARDRAILS/README.md` |

## V1 Layer Coverage

| V1 layer | Status | Driving files |
|---|---:|---|
| Knowledge Layer | Ready | `AGENTS.md`, source registry, P6 benchmark files |
| Skills Layer | Ready for MVP-016 | `.agents/skills/*`, `V1_FINAL_BENCHMARK_PACK.md` |
| Workflow Layer | Ready for MVP-018 | `asperitas-workflow/SKILL.md`, `LANGGRAPH/README.md` |
| RAGAS/Eval Layer | Ready for MVP-017 | `asperitas-evaluation/SKILL.md`, `RAGAS/README.md` |
| Audit Layer | Ready for MVP-019 | `asperitas-audit-trace/SKILL.md`, `LANGSMITH/README.md`, `PHOENIX/README.md` |
| Security/Guardrail Layer | Ready for MVP-020 | `asperitas-security/SKILL.md`, `AGENT_SECURITY/README.md`, `SECURITY_BENCHMARK_SOURCES.md` |
| MCP Expansion Layer | Ready for MVP-021 planning | `asperitas-mcp-expansion/SKILL.md`, `ANTHROPIC/README.md`, `V1_FINAL_BENCHMARK_PACK.md` |

## Final Status
The benchmark preparation layer is complete for MVP-016 start. Remaining work is implementation, tests, evals, and artifact verification.
