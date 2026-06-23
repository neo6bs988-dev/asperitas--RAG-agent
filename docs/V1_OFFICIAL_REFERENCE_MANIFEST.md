# V1 Official Reference Manifest

Status: docs-only reference manifest / no production ingestion
Branch: `v1-reference-acquisition-hardening`
Date: 2026-06-23
Scope: official and paper-based benchmarking sources for V1 architecture hardening.

## Purpose

This manifest records trusted reference metadata for V1 development. It is not source ingestion, dependency adoption, external API integration, MCP implementation, RAGAS integration, or production readiness.

## Storage Rule

Store only metadata first:

- source title
- source URL
- source type
- version/date or retrieved date
- summary
- architecture principles
- implementation patterns
- provenance metadata

Do not ingest unofficial blogs, social posts, newsletters, videos, or derivative summaries into the production knowledge base.

## Reference Set

| Source title | URL | Source type | Version/date | Summary | Architecture principles | Implementation patterns | V1 layer |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OpenAI Agent Skills for Codex | https://developers.openai.com/codex/skills | official_docs | retrieved 2026-06-23 | Codex skills are reusable workflow packages with `SKILL.md` and optional supporting files. | progressive disclosure, skill metadata, reusable workflow packages | `.agents/skills/*/SKILL.md`, skill descriptions, local skill registry | Skills Layer |
| OpenAI Agents SDK | https://openai.github.io/openai-agents-python/ | official_docs | retrieved 2026-06-23 | Agent SDK primitives include agents, handoffs/tools, guardrails, tracing, sessions, human-in-loop, MCP integration. | small primitives, guardrails, tracing, human approval, workflow coordination | preflight gates, trace IDs, skill handoffs, fail-closed validation | Workflow / Audit / Security |
| OpenAI Function Calling | https://developers.openai.com/api/docs/guides/function-calling | official_api_docs | retrieved 2026-06-23 | Schema-bound tool/function calling pattern. | explicit tool boundary, schema-first validation | JSON-compatible skill/tool contracts; no implicit execution | Skills / MCP Expansion |
| OpenAI Evals Docs | https://developers.openai.com/api/docs/guides/evals | official_docs | retrieved 2026-06-23 | Evaluation documentation for repeatable evaluation workflows. | eval-first improvement, graders, repeatable experiments | strict/report-only metric split, before-after evals | RAGAS Eval |
| openai/evals | https://github.com/openai/evals | official_github_repo | retrieved 2026-06-23 | Official OpenAI evaluation repository. | fixture-driven evals, benchmark registry | scorer separation, eval reports, regression gates | RAGAS Eval |
| Anthropic Claude Code Skills | https://code.claude.com/docs/en/skills | official_docs | retrieved 2026-06-23 | Claude skills use `SKILL.md`, frontmatter, supporting files, and invocation controls. | concise skill bodies, frontmatter, scoped invocation, optional support files | `SkillSpec`, allowed/disallowed operations, human-triggered workflows | Skills / Security |
| Anthropic Subagents | https://code.claude.com/docs/en/sub-agents | official_docs | retrieved 2026-06-23 | Specialized agent contexts for delegated work. | specialist context, scoped delegation | role validators, separate compliance/security review contexts | Workflow Layer |
| Model Context Protocol Intro | https://modelcontextprotocol.io/docs/getting-started/intro | official_docs | retrieved 2026-06-23 | MCP standardizes how AI apps connect to data, tools, and workflows. | connector standard, client-server separation, tool/resource boundaries | MCP-ready metadata only in V1; no MCP execution yet | MCP Expansion Layer |
| anthropics/skills | https://github.com/anthropics/skills | official_github_repo | retrieved 2026-06-23 | Public Agent Skills repository. | portable skill packaging | reference only; no copy/adoption without license/security review | Skills Layer |
| Agent Skills Standard | https://agentskills.io/ | official_docs | retrieved 2026-06-23 | Open standard for reusable agent skills. | cross-agent portability | future skill export compatibility | Skills / MCP Expansion |
| LangGraph Overview | https://docs.langchain.com/oss/python/langgraph/overview | official_docs | retrieved 2026-06-23 | LangGraph is an orchestration runtime for long-running, stateful agents. | durable execution, human-in-loop, persistence, tracing | read-only V1 workflow states and approval transitions | Workflow / Audit |
| LangGraph Workflows and Agents | https://docs.langchain.com/oss/python/langgraph/workflows-agents | official_docs | retrieved 2026-06-23 | Workflows are predetermined code paths; agents are dynamic tool-use systems. | deterministic workflow before dynamic agency | preflight -> retrieve -> validate -> answer -> log | Workflow / Evaluation |
| LangGraph Persistence | https://docs.langchain.com/oss/python/langgraph/persistence | official_docs | retrieved 2026-06-23 | Persistence supports checkpoints and stores. | state snapshots, durable memory, thread separation | trace_id, workflow_state, JSONL audit records | Audit Layer |
| langchain-ai/langgraph | https://github.com/langchain-ai/langgraph | official_github_repo | retrieved 2026-06-23 | Official LangGraph repository. | reference implementation and tests | reference only; no dependency adoption without scoped PR | Workflow Layer |
| LlamaIndex Framework Docs | https://developers.llamaindex.ai/python/framework/ | official_docs | retrieved 2026-06-23 | LlamaIndex framework documentation for RAG, agents, indexes, retrieval, evaluation, storage. | knowledge layer, indexing, retrievers, evaluation | source registry + chunks + retriever separation | Knowledge / Evaluation |
| LlamaIndex Retriever Docs | https://developers.llamaindex.ai/python/framework/module_guides/querying/retriever/ | official_docs | retrieved 2026-06-23 | Retriever module guidance. | retriever abstraction, query/retrieval separation | deterministic retriever protected; experimental retrievers explicit opt-in | Knowledge / Evaluation |
| LlamaIndex Evaluation Docs | https://developers.llamaindex.ai/python/framework/module_guides/evaluating/ | official_docs | retrieved 2026-06-23 | Evaluation module documentation. | retrieval and response evaluation separation | labelled golden set, citation/answer metric split | RAGAS Eval |
| run-llama/llama_index | https://github.com/run-llama/llama_index | official_github_repo | retrieved 2026-06-23 | Official LlamaIndex repository. | modular data framework | reference only; no code import without review | Knowledge Layer |
| Ragas Docs | https://docs.ragas.io/en/stable/ | official_docs | retrieved 2026-06-23 | Ragas documentation for RAG and agent evaluation metrics. | context precision, context recall, response relevancy, faithfulness | report-only RAGAS-inspired metrics before dependency adoption | RAGAS Eval |
| Ragas Paper | https://arxiv.org/abs/2309.15217 | peer_reviewed_or_preprint_paper | 2023-09-26 / revised 2025-04-28 | Ragas proposes reference-free evaluation of RAG retrieval, context use, and generation quality. | retrieval quality, faithfulness, generation quality | answer/evidence metric map | RAGAS Eval |
| Ragas GitHub | https://github.com/vibrantlabsai/ragas | official_github_repo | retrieved 2026-06-23 | Official Ragas repository. | open eval implementation | reference only until dependency/security review | RAGAS Eval |
| ARES Paper | https://arxiv.org/abs/2311.09476 | peer_reviewed_or_preprint_paper | 2023-11-15 | Automated RAG evaluation framework. | evaluator design, retrieval/generation assessment | V1.1 evaluator reference | RAGAS Eval |
| Ginkgo/OpenAI GPT-5 Autonomous Lab Paper | local P5 source | external_paper_local_metadata | local file | Used only for schema-first validation, metric contracts, decision logging, approval boundaries. | fail-closed validation, workflow contracts, human approval | benchmark workflow schema; no autonomous lab claim | Workflow / Audit |
| Benchling Developer Platform Docs | https://docs.benchling.com/docs | official_api_docs | retrieved 2026-06-23 | Benchling developer docs cover API, warehouse, apps, events, and audit/activity representation. | structured records, permissioning, audit/activity trace | JSONL audit and provenance schema; no ELN/LIMS claim | Audit / Knowledge |
| GitHub Actions Docs | https://docs.github.com/en/actions | official_docs | retrieved 2026-06-23 | Official workflow automation and CI documentation. | reproducible CI, workflow gates, artifact handling | quality gates, test/eval jobs, artifact verification | Audit / Security |
| GitHub Code Security Docs | https://docs.github.com/en/code-security | official_docs | retrieved 2026-06-23 | Official docs for secret scanning, code scanning, dependency review, and supply-chain security. | secret/security scanning, dependency review, supply-chain hygiene | security layer checks, CI hardening | Security Layer |
| MCPSecBench | https://arxiv.org/abs/2508.13220 | peer_reviewed_or_preprint_paper | 2025-08-17 | MCP security benchmark and taxonomy. | connector threat modeling, benchmark-driven hardening | MCP threat model before implementation | MCP Expansion / Security |
| MCPTox | https://arxiv.org/abs/2508.14925 | peer_reviewed_or_preprint_paper | 2025-08-19 | MCP tool-metadata risk benchmark. | tool metadata governance | metadata linting and allowlist discipline | MCP Expansion / Security |
| MCP-ITP | https://arxiv.org/abs/2601.07395 | peer_reviewed_or_preprint_paper | 2026-01-12 | Framework for indirect tool-risk evaluation in MCP settings. | least privilege, registry governance | no ambient tools; explicit approval for state-changing tools | MCP Expansion / Security |
| AgentDojo | https://arxiv.org/abs/2406.13352 | peer_reviewed_or_preprint_paper | 2024-06-19 | Benchmark for prompt-injection resilience in tool-using agents. | untrusted data isolation, defensive evaluation | source-instruction isolation tests | Security Layer |
| AgentHarm | https://arxiv.org/abs/2410.09024 | peer_reviewed_or_preprint_paper | 2024-10-11 | Benchmark for measuring harmfulness of LLM agents. | harmful task prevention, refusal quality | high-risk task gates and refusal regression tests | Security Layer |
| AgentDyn | https://arxiv.org/abs/2602.03117 | peer_reviewed_or_preprint_paper | 2026-02-03 | Dynamic benchmark for prompt-injection evaluation. | useful-task preservation plus safety | defensive prompt-injection regression suite | Security Layer |

## Layer Upgrade Rules

### Skills Layer

- Add local `SkillSpec` and `SkillRegistry`.
- Support `SKILL.md` compatibility.
- Require `allowed_operations`, `forbidden_operations`, `requires_human_approval`, `audit_required`, `source_grounding_required`, `external_call_allowed=false` by default.
- Unknown or unsafe skill requests must return `blocked` or `unsupported`, not silent success.

### Workflow Layer

- Model work as explicit states.
- V1 default is read-only planning.
- Required states: request received, source status checked, skill selected, risk preflight, allowed or blocked or human approval required, evidence ready, verification attached, audit record written.

### RAGAS Eval Layer

- Preserve strict retrieval metrics as regression gates.
- Add report-only answer/evidence metrics: context precision, context recall, groundedness, answer relevancy, citation accuracy, abstention accuracy, unsupported-claim rate, compliance trigger correctness.
- Do not add RAGAS package dependency until explicitly scoped.

### Audit Layer

- Add traceable JSON/JSONL records for query, retrieval, answer, safety decision, feedback, eval, and decision log.
- Minimum fields: `trace_id`, `timestamp_utc`, `skill_id`, `workflow_state`, `retriever`, `source_ids`, `citations`, `risk_flags`, `decision`, `human_approval_status`, `execution=false`, `ingested=false`, `external_call=false`.

### Security Layer

- Treat retrieved source text as evidence, not executable instruction.
- Add defensive fixtures for source instruction conflicts, metadata risk, restricted-source leakage, production-claim bait, autonomous-lab overclaim, and compliance evasion attempts.
- Fail closed on unknown connectors, unsafe skills, or high-risk biological/legal/regulatory requests.

### MCP Expansion Layer

- V1 does not implement MCP.
- Add only MCP-ready metadata and threat model.
- Before any MCP implementation, require allowlists, least privilege, tool metadata validation, human approval for state-changing operations, and local defensive fixtures.

## Updated V1 Sequence

1. PR #51 Eval Oracle Hardening review/merge.
2. PR #53 Reference Acquisition Hardening review/merge, including this manifest.
3. P0 Metadata Integrity Hardening.
4. P1 Skills Framework.
5. P2 RAGAS-Inspired Eval Layer.
6. P3 Workflow / Planner State Machine.
7. P4 Audit & Traceability JSONL Layer.
8. P5 Security / Prompt-Injection / MCP Threat Fixtures.
9. Answer / Citation / Abstention / Compliance closeout.
10. V1 release regression.

## Non-Claims

This manifest does not claim OpenAI-equivalent capability, Anthropic-equivalent skill ecosystem, LangGraph deployment, LlamaIndex deployment, RAGAS integration, Benchling/ELN/LIMS equivalence, MCP implementation, autonomous wet-lab capability, or production RAG/KG/vector DB/compliance readiness.
