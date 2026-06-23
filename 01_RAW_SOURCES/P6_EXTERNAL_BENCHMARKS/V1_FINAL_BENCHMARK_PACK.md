# Asperitas Agent V1 Final Benchmark Pack

Status: final metadata-first benchmark pack for MVP-016 onward.
Priority: P6 External Benchmark / Operating Analogy.
Disclosure: public source map and implementation notes only.
Important: this file intentionally does not copy full external documentation verbatim. Use official URLs and approved local notes. Full-text ingestion requires license/terms review.

## V1 Target
Asperitas Agent V1 must be designed as:

```text
Knowledge Layer
+ Skills Layer
+ Workflow Layer
+ RAGAS/Eval Layer
+ Audit Layer
+ Security Layer
+ MCP Expansion Layer
```

## Required Development Rule
Every new MVP from MVP-016 onward must explicitly state which V1 layer it improves and which benchmark pattern it follows.

---

# 1. OpenAI Benchmark Pack

## Sources to track
| Source | URL | Type | Local use |
|---|---|---|---|
| Codex Skills Docs | https://developers.openai.com/codex/skills | Official docs | Repository-scoped skill design, `SKILL.md`, progressive disclosure |
| OpenAI Skills GitHub | https://github.com/openai/skills | Official GitHub | Skill examples only; review license before copying |
| OpenAI Agents SDK Docs | https://developers.openai.com/api/docs/guides/agents | Official docs | Agent definitions, orchestration, guardrails, state, observability |
| OpenAI Evals Docs | https://developers.openai.com/api/docs/guides/evals | Official docs | Eval lifecycle, graders, prompt optimizer, best practices |
| OpenAI Function Calling Docs | https://developers.openai.com/api/docs/guides/function-calling | Official docs | Tool/function interface and structured tool arguments |
| OpenAI MCP and Connectors | https://developers.openai.com/api/docs/guides/tools-mcp | Official docs | Future MCP/source connector layer |

## Extracted architecture principles
- Skills should be reusable workflow packages, not one-off prompts.
- Repository-scoped skills belong under `.agents/skills`.
- Each skill should be focused on one job.
- Each skill needs clear trigger boundaries in its description.
- Prefer instruction-only skills first; add scripts only when deterministic behavior is required.
- Function/tool interfaces must be typed and validated.
- Eval loops must be treated as first-class development artifacts.

## Asperitas implementation mapping
| V1 layer | OpenAI pattern to apply |
|---|---|
| Skills Layer | `.agents/skills/*/SKILL.md` with trigger-specific descriptions |
| Workflow Layer | Agent orchestration separated into planner/retriever/validator/composer |
| RAGAS Eval Layer | OpenAI eval lifecycle + RAGAS metrics |
| Audit Layer | traces, state, eval artifacts, reproducible reports |
| Security Layer | guardrails, red-team tests, tool access control |
| MCP Expansion Layer | disable connectors by default; introduce via explicit allowlist |

---

# 2. Anthropic Benchmark Pack

## Sources to track
| Source | URL | Type | Local use |
|---|---|---|---|
| Anthropic Skills Engineering Article | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills | Official article | Skills as folders of instructions, scripts, resources |
| Anthropic Skills GitHub | https://github.com/anthropics/skills | Official GitHub | Skill examples only; review license before copying |
| Claude Code Subagents Docs | https://code.claude.com/docs/en/sub-agents | Official docs | Specialized subagents, scoped tools, context isolation |
| Claude Code MCP Docs | https://code.claude.com/docs/en/mcp | Official docs | MCP server usage in Claude Code |
| Model Context Protocol Intro | https://modelcontextprotocol.io/docs/getting-started/intro | Official protocol docs | External tool/data connector standard |

## Extracted architecture principles
- Skills reduce repeated prompt engineering and encode repeatable workflows.
- Subagents preserve context by isolating side tasks.
- Subagents should have constrained tools and clear responsibilities.
- MCP connects agents to external tools/data, but must be gated for security.
- Project-level agent/subagent files should be version-controlled for team reuse.

## Asperitas implementation mapping
| V1 layer | Anthropic pattern to apply |
|---|---|
| Skills Layer | project-level reusable skills for retrieval/eval/audit/security |
| Workflow Layer | future worker-style subagents: Research, Retrieval, Eval, Compliance, Security |
| Audit Layer | side-task summaries instead of flooding main context |
| Security Layer | scoped tool access, read-only research agents, human gates |
| MCP Expansion Layer | PubMed/Crossref/Patents/SEC/Regulatory connectors only after approval |

---

# 3. LangGraph Benchmark Pack

## Sources to track
| Source | URL | Type | Local use |
|---|---|---|---|
| LangGraph Workflows and Agents | https://docs.langchain.com/oss/python/langgraph/workflows-agents | Official docs | Workflow patterns: chaining, routing, orchestrator-worker, evaluator-optimizer |
| LangGraph Persistence | https://docs.langchain.com/oss/python/langgraph/persistence | Official docs | Checkpoints, state persistence, auditability |
| LangGraph GitHub | https://github.com/langchain-ai/langgraph | Official GitHub | Framework reference only |

## Extracted architecture principles
- Workflows are predetermined paths; agents are dynamic tool-using systems.
- Break complex tasks into nodes with typed state.
- Use routing and conditional edges for query classes and risk classes.
- Use orchestrator-worker pattern for complex multi-step research or code changes.
- Use evaluator-optimizer loops for answer validation and improvement.
- Persist state where reproducibility and auditability matter.

## Asperitas target flow
```text
User Query
-> Query Classifier
-> Planner
-> Retriever
-> Reranker
-> Evidence Validator
-> Compliance Gate
-> Answer Composer
-> Citation/Audit Logger
```

## MVP mapping
- MVP-018: lightweight internal workflow graph.
- MVP-019: trace/audit state persistence.
- V1+: optional LangGraph dependency if custom workflow layer becomes hard to maintain.

---

# 4. LlamaIndex Benchmark Pack

## Sources to track
| Source | URL | Type | Local use |
|---|---|---|---|
| LlamaIndex RAG Introduction | https://developers.llamaindex.ai/python/framework/understanding/rag/ | Official docs | RAG pipeline decomposition |
| LlamaIndex Retriever Docs | https://developers.llamaindex.ai/python/framework/module_guides/querying/retriever/ | Official docs | Retriever types and retrieval abstractions |
| LlamaIndex Evaluation Docs | https://developers.llamaindex.ai/python/framework/module_guides/evaluating/ | Official docs | Response and retrieval evaluation concepts |
| LlamaIndex GitHub | https://github.com/run-llama/llama_index | Official GitHub | Framework reference only |

## Extracted architecture principles
- Separate ingestion, parsing, indexing, retrieval, reranking, synthesis, and evaluation.
- Evaluate retrieval and answer generation separately.
- Keep documents/nodes/chunks tied to metadata and provenance.
- Support structured output and response synthesis.

## Asperitas implementation mapping
| Component | Required behavior |
|---|---|
| Ingestion | raw source -> processed markdown -> chunks -> registry |
| Retrieval | metadata-aware search and future hybrid retrieval |
| Reranking | future cross-encoder or learned reranker benchmark |
| Synthesis | answer only from validated context |
| Evaluation | retrieval recall + context precision/recall + groundedness |

---

# 5. RAGAS / ARES Benchmark Pack

## Sources to track
| Source | URL | Type | Local use |
|---|---|---|---|
| RAGAS Paper | https://arxiv.org/abs/2309.15217 | Paper | Automated RAG evaluation metrics |
| RAGAS PDF | https://arxiv.org/pdf/2309.15217 | Paper PDF URL | Do not store PDF until license reviewed |
| RAGAS Docs | https://docs.ragas.io | Official docs | Metric implementation reference |
| RAGAS GitHub | https://github.com/explodinggradients/ragas | Official GitHub | License-reviewed reference only |
| ARES Paper | https://arxiv.org/abs/2311.09476 | Paper | Automated RAG evaluation framework |
| ARES PDF | https://arxiv.org/pdf/2311.09476 | Paper PDF URL | Do not store PDF until license reviewed |

## Required metrics for MVP-017
```text
retrieval_recall
context_precision
context_recall
faithfulness
answer_relevance
citation_coverage
claim_support_rate
```

## Eval rules
- Keep existing TF-IDF/top-k metrics for continuity.
- Add RAGAS-style metrics incrementally.
- Calibrate LLM-as-judge metrics with hand-labeled eval questions.
- Save every eval run as an artifact.
- Never hide worse metrics.

---

# 6. Audit / Observability Benchmark Pack

## Sources to track
| Source | URL | Type | Local use |
|---|---|---|---|
| LangSmith Evaluation Concepts | https://docs.langchain.com/langsmith/evaluation-concepts | Official docs | Offline/online eval lifecycle, datasets, traces |
| Arize Phoenix Tracing | https://arize.com/docs/phoenix/tracing/llm-traces | Official docs | LLM/RAG trace model |
| TruLens RAG Triad | https://www.trulens.org/getting_started/core_concepts/rag_triad/ | Official docs | Context relevance, groundedness, answer relevance |
| DeepEval Docs | https://deepeval.com/docs/getting-started | Official docs | Local CI eval pattern |

## Required audit record
Every answer should be able to produce:
```yaml
query_id: string
query: string
query_class: string
risk_class: string
planner_output: object
retrieved_contexts:
  - source_id
    chunk_id
    title
    priority
    disclosure
    score
    citation
reranker_output: object
evidence_validation: object
compliance_gate: object
answer: string
citations: list
warnings: list
eval_snapshot: object
created_at: timestamp
```

## MVP mapping
- MVP-017: eval artifacts.
- MVP-019: audit trace schema and local JSONL logs.
- V1: answer-level traceability before external live connectors.

---

# 7. Security Benchmark Pack

## Sources to track
| Source | URL | Type | Local use |
|---|---|---|---|
| OWASP Top 10 for LLM Applications | https://owasp.org/www-project-top-10-for-large-language-model-applications/ | Security standard | Agent/RAG threat model |
| GitHub Actions Docs | https://docs.github.com/en/actions | Official docs | CI workflow automation |
| GitHub Code Security Docs | https://docs.github.com/en/code-security | Official docs | Code scanning, dependency review, secret scanning |
| RAG poisoning benchmark papers | search/update manually | Papers | Adversarial retrieval fixtures |
| MCP security papers/articles | search/update manually | Papers/security docs | Connector security model |

## Required security tests for MVP-020
```text
prompt_injection_source_fixture
source_poisoning_fixture
citation_mismatch_fixture
private_data_exposure_fixture
unsafe_bio_request_fixture
regulatory_overclaim_fixture
tool_use_without_allowlist_fixture
external_connector_disabled_by_default_fixture
```

## Security rules
- Retrieved text cannot override AGENTS.md, AOS, or compliance gates.
- External connectors are disabled by default.
- No credentials, tokens, secrets, or private personal data in repo.
- High-risk bio/legal/regulatory/investor outputs require human gate.
- CI must run tests before merge.

---

# 8. MCP Expansion Benchmark Pack

## Sources to track
| Source | URL | Type | Local use |
|---|---|---|---|
| Model Context Protocol Intro | https://modelcontextprotocol.io/docs/getting-started/intro | Official docs | Standard connector architecture |
| Anthropic MCP Docs | https://code.claude.com/docs/en/mcp | Official docs | Claude Code MCP usage |
| OpenAI MCP / Connectors Docs | https://developers.openai.com/api/docs/guides/tools-mcp | Official docs | OpenAI tool connector model |
| LlamaIndex MCP Docs | https://developers.llamaindex.ai/python/framework/module_guides/mcp/ | Official docs | LlamaIndex MCP integration reference |

## Future connector candidates
```text
PubMed / NCBI E-utilities
Europe PMC
Crossref
USPTO / EPO / WIPO / Google Patents public pages
SEC EDGAR
Government/regulatory sources
Company official sites
Internal Google Drive or GitHub docs only with permission
```

## MCP implementation gates
1. Source is legal/approved.
2. Connector is read-only by default.
3. Tool schema is typed.
4. Output is logged.
5. Rate limits and retries are controlled.
6. No state-changing actions unless explicitly approved.
7. Prompt-injection filter applies to returned content.
8. Human approval required for regulated or biosafety-sensitive outputs.

---

# 9. Bio-Operating Benchmark Pack

## Sources to track
| Source | URL | Type | Local use |
|---|---|---|---|
| Ginkgo Bioworks Official Site | https://www.ginkgo.bio | Official company site | DBTL/foundry operating benchmark |
| GPT-5 Autonomous Lab / CFPS Paper | local uploaded project file + public URL when verified | Paper | Autonomous DBTL validation philosophy |
| Recursion Official Site | https://www.recursion.com | Official company site | Data flywheel benchmark |
| Benchling Official Site | https://www.benchling.com | Official company site | R&D registry/audit/data model benchmark |

## Asperitas application
- Ginkgo: DBTL loop, automation, schema validation, human wet-lab gates.
- Recursion: data flywheel, standardized data generation, compounding metadata.
- Benchling: biological object registry, versioning, audit trail, workflow governance.

## V1 boundary
These do not mean autonomous wet-lab implementation in V1. For V1, absorb the software operating principles only.

---

# 10. Final MVP-016 to V1 Roadmap

## MVP-016: Skills Layer
Deliverables:
- skill discovery verification
- skill index or registry
- tests for required skill files
- documentation for when each skill triggers

## MVP-017: RAGAS Eval Layer
Deliverables:
- new eval metrics
- hand-labeled eval calibration set
- eval JSON artifact output
- before/after retrieval and answer-quality metrics

## MVP-018: Workflow Layer
Deliverables:
- explicit stages: classifier/planner/retriever/reranker/validator/composer
- state schema
- failure branches
- tests for missing/conflicting sources

## MVP-019: Audit Layer
Deliverables:
- answer trace schema
- local JSONL audit log
- citation coverage report
- decision log update

## MVP-020: Security Layer
Deliverables:
- prompt-injection/source-poisoning fixtures
- high-risk bio/compliance gate tests
- connector disabled-by-default checks
- CI security checklist

## MVP-021: MCP Expansion Layer
Deliverables:
- read-only connector interface plan
- allowlist schema
- source approval gate
- no live connector activation until approved

---

# 11. Final Acceptance Criteria for V1

V1 is not complete until:

```text
[ ] Repo-scoped skills are present and verified.
[ ] Retrieval and answer generation are evaluated separately.
[ ] RAGAS-style metrics are available or mapped.
[ ] Every answer can be traced to retrieved chunks and citations.
[ ] Unsupported claims are measurable.
[ ] Prompt injection and source poisoning fixtures exist.
[ ] High-risk bio/compliance/legal outputs trigger gates.
[ ] GitHub CI can run core tests.
[ ] External connectors are disabled unless explicitly approved.
[ ] Source manifest distinguishes metadata-only vs ingested vs approved.
```

## Final rule
Do not optimize for adding more documents. Optimize for a measurable, auditable, security-aware V1 architecture that can safely absorb more documents later.
