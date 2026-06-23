# P6_EXTERNAL_BENCHMARKS

Purpose: external/public benchmark sources for Asperitas Agent V1 architecture.

Priority: P6 - External Benchmark / Operating Analogy
Disclosure: Public metadata only unless manually reviewed.
Status: Source registry + benchmark notes. This folder does not mean production ingestion, license approval, embedding, vector DB deployment, KG deployment, or eval deployment is complete.

## Scope
Use these sources to improve V1 agent architecture:

1. OpenAI Codex Skills / Evals / GitHub workflow
2. Anthropic Agent Skills / MCP / Claude Code architecture
3. LangGraph workflows / stateful agent graphs
4. LlamaIndex RAG / ingestion / retrieval / evaluation
5. RAGAS / ARES evaluation metrics
6. Ginkgo autonomous-lab / DBTL validation philosophy
7. Recursion data flywheel / industrialized biology
8. Benchling R&D data platform / registry / audit trail
9. GitHub Actions / branch protection / security automation
10. Agent security / prompt injection / tool abuse / source poisoning

## Use Rules
- Treat these as external benchmarks, not Asperitas internal facts.
- Prefer official docs, peer-reviewed papers, official repositories, and public company materials.
- Do not ingest full webpages/PDFs unless license/terms allow it or a human approves.
- Store source metadata first: title, URL, publisher, date, source type, license status, relevance, intended use.
- Every implementation derived from this folder must update tests, docs, and decision logs.

## V1 Architecture Target
Asperitas Agent V1 = Knowledge Layer + Skills Layer + Workflow Layer + Evaluation Layer + Audit Layer + Security Layer.

## Folder Map
- OPENAI: Codex Skills, Evals, Agent SDK, GitHub automation patterns
- ANTHROPIC: Agent Skills, MCP, Claude Code, subagent/skill patterns
- LANGGRAPH: stateful workflow and planner architecture
- LLAMAINDEX: RAG ingestion, retrieval, response synthesis, evaluation
- RAGAS: faithfulness, answer relevance, context precision/recall
- GINKGO: DBTL/autonomous-lab validation philosophy
- RECURSION: data flywheel and industrialized biology operating principles
- BENCHLING: registry, metadata, versioning, audit-trail benchmarks
- GITHUB_SECURITY: CI, branch protection, dependency review, code scanning
- AGENT_SECURITY: prompt injection, source poisoning, tool abuse, secret leakage

## Current Action
Use this folder as the benchmark source-control layer for MVP-016 onward. Repository-scoped Codex skills live in `.agents/skills/` and reference this folder when needed.
