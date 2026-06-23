# V1 External Benchmark Source Manifest

Status: metadata-first source manifest. Do not treat this as full ingestion.

| Domain | Source | URL | Source Type | V1 Use |
|---|---|---|---|---|
| OpenAI | Codex Agent Skills | https://developers.openai.com/codex/skills | Official docs | Repository-scoped skills, progressive disclosure, SKILL.md format |
| OpenAI | OpenAI Skills GitHub | https://github.com/openai/skills | Official repo | Skill examples and folder anatomy |
| OpenAI | OpenAI Evals | https://github.com/openai/evals | Official repo | Evaluation harness design |
| Anthropic | Agent Skills article | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills | Official engineering article | Skill design, progressive disclosure, safety notes |
| Anthropic | Agent Skills open standard | https://agentskills.io | Open standard site | Cross-agent skill portability |
| Anthropic | Model Context Protocol | https://modelcontextprotocol.io | Official protocol site | Future external tool/source connector layer |
| LangGraph | Workflows and agents docs | https://docs.langchain.com/oss/python/langgraph/workflows-agents | Official docs | Planner/retriever/reranker/validator workflow |
| LangGraph | LangGraph GitHub | https://github.com/langchain-ai/langgraph | Official repo | Graph/state/persistence implementation reference |
| LlamaIndex | RAG guide | https://developers.llamaindex.ai/python/framework/understanding/rag/ | Official docs | Ingestion, indexing, retrieval, synthesis architecture |
| LlamaIndex | Evaluation docs | https://developers.llamaindex.ai/python/framework/module_guides/evaluating/ | Official docs | RAG evaluation patterns |
| RAGAS | RAGAS paper | https://arxiv.org/abs/2309.15217 | Paper | Faithfulness, answer relevance, context precision/recall |
| RAGAS | RAGAS docs | https://docs.ragas.io | Official docs | Metrics integration reference |
| ARES | ARES paper | https://arxiv.org/abs/2311.09476 | Paper | Automated RAG evaluation reference |
| Ginkgo/OpenAI | GPT-5 autonomous lab / CFPS paper | Local uploaded PDF + public source when verified | Paper/preprint | DBTL validation philosophy, schema checks, autonomous experiment loop |
| Ginkgo | Ginkgo Bioworks official site | https://www.ginkgo.bio | Official company site | Foundry/DBTL operating benchmark |
| Recursion | Recursion official site | https://www.recursion.com | Official company site | Data flywheel benchmark |
| Benchling | Benchling official site/docs | https://www.benchling.com | Official company site | Registry, metadata, audit trail, R&D cloud benchmark |
| GitHub | Actions docs | https://docs.github.com/en/actions | Official docs | CI / artifact verification |
| GitHub | Code security docs | https://docs.github.com/en/code-security | Official docs | Dependency review, code scanning, static analysis |
| Agent Security | OWASP LLM Top 10 | https://owasp.org/www-project-top-10-for-large-language-model-applications/ | Standards/security guidance | Prompt injection and unsafe-output test cases |

## Metadata Fields Required for Future Ingestion
- source_id
- title
- publisher
- authors_or_org
- url
- source_type
- publication_date_or_version
- retrieved_at
- license_status
- terms_status
- priority = P6
- disclosure = public
- ingestion_status = metadata_only | approved_for_ingestion | ingested
- relevance_tags
- implementation_patterns
- risk_notes

## Stop Rules
- No full-text crawl without license/terms review.
- No code copying from external repositories without license review and attribution.
- No unofficial blog/social post ingestion unless explicitly approved as low-priority commentary.
- No claim that these materials are embedded or searchable until the ingestion pipeline logs it.
