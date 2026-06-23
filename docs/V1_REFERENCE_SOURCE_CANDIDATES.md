# V1 Official Reference Source Candidates

Status: metadata-only candidate manifest
Scope: V1 architecture benchmarking and future source-governance review

## Executive Bottom Line

This file records high-authority reference candidates for Asperitas Agent V1 development.

It stores metadata only and does not ingest full source content into the production knowledge base.

All entries require later license/terms/provenance review before any production ingestion, copying, long-form summarization, or dependency adoption.

## Intake Rules

Allowed source classes:

1. official OpenAI documentation;
2. official Anthropic documentation;
3. official Model Context Protocol documentation;
4. official LangGraph documentation;
5. official LlamaIndex documentation;
6. official RAGAS documentation and official repository;
7. RAG evaluation papers with peer-review or review-needed status;
8. official GitHub repositories.

Rejected from production KB:

- unofficial blogs;
- social posts;
- newsletters;
- YouTube summaries;
- derivative summaries;
- copied implementation snippets with unclear license;
- claims without provenance.

## Candidate Sources

### 1. OpenAI Structured Outputs

```json
{
  "source_title": "Structured model outputs | OpenAI API",
  "source_url": "https://platform.openai.com/docs/guides/structured-outputs",
  "source_type": "official_docs",
  "publisher_or_org": "OpenAI",
  "version_or_date": "retrieved_2026-06-23",
  "summary": "Official OpenAI guide for schema-adherent model outputs. Relevant to JSON-compatible V1 contracts and fail-closed structured responses.",
  "architecture_principles": [
    "schema-first output contracts",
    "strict JSON schema adherence",
    "distinguish valid JSON from schema adherence",
    "use evals to test output structures"
  ],
  "implementation_patterns": [
    "use explicit JSON schemas for skill outputs",
    "set required fields",
    "reject unspecified additional properties where possible",
    "test schema adherence before runtime integration"
  ],
  "provenance_metadata": {
    "authority_level": "official",
    "license_or_terms_status": "review_needed",
    "intended_use": "architecture_reference",
    "production_ingestion_allowed": false,
    "notes": "Use as design reference only until license/terms reviewed."
  }
}
```

### 2. OpenAI Codex Agent Skills

```json
{
  "source_title": "Agent Skills – Codex | OpenAI Developers",
  "source_url": "https://developers.openai.com/codex/skills/",
  "source_type": "official_docs",
  "publisher_or_org": "OpenAI",
  "version_or_date": "retrieved_2026-06-23",
  "summary": "Official OpenAI Codex guide for agent skills. Relevant to reusable workflows, SKILL.md-style task packaging, and progressive context disclosure.",
  "architecture_principles": [
    "skills as reusable workflows",
    "package instructions, resources, and optional scripts",
    "progressive disclosure to manage context",
    "clear name and description for routing"
  ],
  "implementation_patterns": [
    "define Asperitas SkillSpec metadata",
    "separate instructions from optional scripts/references/assets",
    "keep skill descriptions compact and trigger-specific",
    "validate skill contracts before execution"
  ],
  "provenance_metadata": {
    "authority_level": "official",
    "license_or_terms_status": "review_needed",
    "intended_use": "architecture_reference",
    "production_ingestion_allowed": false,
    "notes": "Do not copy implementation text into production KB without review."
  }
}
```

### 3. Anthropic Claude Code Skills

```json
{
  "source_title": "Extend Claude with skills - Claude Code Docs",
  "source_url": "https://docs.anthropic.com/en/docs/claude-code/skills",
  "source_type": "official_docs",
  "publisher_or_org": "Anthropic",
  "version_or_date": "retrieved_2026-06-23",
  "summary": "Official Anthropic Claude Code skills guide. Relevant to YAML-frontmatter skills, project-specific run/verify recipes, skill triggering, and disable/visibility controls.",
  "architecture_principles": [
    "skills as project or user reusable instructions",
    "YAML metadata plus markdown instructions",
    "supporting files for scripts, templates, and references",
    "run/verify recipes should be project-specific and recorded"
  ],
  "implementation_patterns": [
    "model Asperitas skills with explicit description and risk policy",
    "separate reference content from task/action content",
    "support disable-model-invocation style policies for risky skills",
    "record project verification recipes as skills after validation"
  ],
  "provenance_metadata": {
    "authority_level": "official",
    "license_or_terms_status": "review_needed",
    "intended_use": "architecture_reference",
    "production_ingestion_allowed": false,
    "notes": "Use to inform local SkillSpec/SkillRegistry, not to imply Anthropic-equivalent capability."
  }
}
```

### 4. Model Context Protocol Introduction

```json
{
  "source_title": "What is the Model Context Protocol (MCP)?",
  "source_url": "https://modelcontextprotocol.io/docs/getting-started/intro",
  "source_type": "official_docs",
  "publisher_or_org": "Model Context Protocol",
  "version_or_date": "retrieved_2026-06-23",
  "summary": "Official MCP introduction. Relevant to future external-source and tool integration architecture after V1.",
  "architecture_principles": [
    "standardized connection between AI applications and external systems",
    "tools, data sources, and workflows as external capabilities",
    "interoperability layer for agent systems"
  ],
  "implementation_patterns": [
    "keep V1 skills MCP-ready but non-executing by default",
    "separate connector metadata from connector execution",
    "require approval and security review before external tool access"
  ],
  "provenance_metadata": {
    "authority_level": "official",
    "license_or_terms_status": "review_needed",
    "intended_use": "architecture_reference",
    "production_ingestion_allowed": false,
    "notes": "Future connector standard only; no external API integration in MVP-016."
  }
}
```

### 5. LangGraph Overview

```json
{
  "source_title": "LangGraph overview - Docs by LangChain",
  "source_url": "https://docs.langchain.com/oss/python/langgraph/overview",
  "source_type": "official_docs",
  "publisher_or_org": "LangChain",
  "version_or_date": "retrieved_2026-06-23",
  "summary": "Official LangGraph overview. Relevant to stateful workflow orchestration, human-in-the-loop, persistence, tracing, and agent workflow design.",
  "architecture_principles": [
    "low-level orchestration for long-running stateful agents",
    "durable execution and persistence",
    "human-in-the-loop state inspection and modification",
    "observability and evaluation for agent traces"
  ],
  "implementation_patterns": [
    "represent Asperitas workflows as explicit states",
    "separate allowed/blocked/approval-required transitions",
    "keep MVP-018 read-only until execution policy is approved",
    "log state transitions for auditability"
  ],
  "provenance_metadata": {
    "authority_level": "official",
    "license_or_terms_status": "review_needed",
    "intended_use": "architecture_reference",
    "production_ingestion_allowed": false,
    "notes": "Use workflow concepts only; do not claim LangGraph deployment until implemented."
  }
}
```

### 6. LlamaIndex Developer Documentation

```json
{
  "source_title": "Welcome to LlamaIndex | Developer Documentation",
  "source_url": "https://docs.llamaindex.ai/en/stable/",
  "source_type": "official_docs",
  "publisher_or_org": "LlamaIndex",
  "version_or_date": "retrieved_2026-06-23",
  "summary": "Official LlamaIndex documentation. Relevant to knowledge-layer concepts, context augmentation, data ingestion, indexing, retrieval, observability, and evaluation.",
  "architecture_principles": [
    "knowledge layer over private or domain data",
    "context augmentation for LLM applications",
    "data connectors, documents, nodes, indexes, retrievers, and query engines",
    "observability and evaluation support"
  ],
  "implementation_patterns": [
    "map Asperitas source registry/chunks to knowledge-layer objects",
    "preserve metadata and citation targets through retrieval",
    "separate source ingestion from retrieval/query runtime",
    "defer production ingestion until provenance/license review"
  ],
  "provenance_metadata": {
    "authority_level": "official",
    "license_or_terms_status": "review_needed",
    "intended_use": "architecture_reference",
    "production_ingestion_allowed": false,
    "notes": "Use as knowledge-layer benchmark; not proof of LlamaIndex integration."
  }
}
```

### 7. RAGAS Metrics Documentation

```json
{
  "source_title": "List of available metrics - Ragas",
  "source_url": "https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/",
  "source_type": "official_docs",
  "publisher_or_org": "RAGAS",
  "version_or_date": "retrieved_2026-06-23",
  "summary": "Official RAGAS metric documentation. Relevant to V1 Evaluation Layer and MVP-017 metric taxonomy.",
  "architecture_principles": [
    "objective evaluation of LLM applications",
    "RAG metrics for context precision, context recall, response relevancy, and faithfulness",
    "agent/tool-use metrics for tool accuracy and goal accuracy",
    "rubric-based general-purpose scoring"
  ],
  "implementation_patterns": [
    "add RAGAS-inspired metric names to eval reports",
    "do not install RAGAS package until explicitly scoped",
    "map existing retrieval eval outputs to context/relevance/faithfulness dimensions",
    "separate metric taxonomy from metric implementation"
  ],
  "provenance_metadata": {
    "authority_level": "official",
    "license_or_terms_status": "review_needed",
    "intended_use": "evaluation_reference",
    "production_ingestion_allowed": false,
    "notes": "Use metric taxonomy for MVP-017; implementation requires separate PR."
  }
}
```

### 8. RAGAS Paper

```json
{
  "source_title": "RAGAS: Automated Evaluation of Retrieval Augmented Generation",
  "source_url": "https://arxiv.org/abs/2309.15217",
  "source_type": "research_paper_review_needed",
  "publisher_or_org": "arXiv / authors",
  "version_or_date": "2023-09-26 / retrieved_2026-06-23",
  "summary": "Research paper introducing RAGAS as reference-free evaluation for RAG systems. Relevant to evaluation dimensions across retrieval quality, faithfulness, and generation quality.",
  "architecture_principles": [
    "evaluate both retrieval and generation modules",
    "measure whether retrieved context is relevant and focused",
    "measure whether generated answer is faithful to retrieved context",
    "support faster evaluation cycles"
  ],
  "implementation_patterns": [
    "separate retrieval metrics from generation metrics",
    "track faithfulness/groundedness independently from answer correctness",
    "use as evaluation benchmark after review status is clarified"
  ],
  "provenance_metadata": {
    "authority_level": "research_paper_review_needed",
    "license_or_terms_status": "review_needed",
    "intended_use": "evaluation_reference",
    "production_ingestion_allowed": false,
    "notes": "Do not label peer-reviewed until venue/review status is verified."
  }
}
```

### 9. Citation Faithfulness Paper Candidate

```json
{
  "source_title": "Correctness is not Faithfulness in RAG Attributions",
  "source_url": "https://arxiv.org/abs/2412.18004",
  "source_type": "research_paper_review_needed",
  "publisher_or_org": "arXiv / authors",
  "version_or_date": "2024-12-23 / retrieved_2026-06-23",
  "summary": "Research paper arguing that citation correctness and citation faithfulness should be distinguished in attributed RAG answers. Relevant to future citation-eval hardening.",
  "architecture_principles": [
    "citation correctness is not sufficient for trust",
    "faithfulness checks whether cited sources genuinely support the answer path",
    "post-rationalized citations are a risk"
  ],
  "implementation_patterns": [
    "track citation correctness and citation faithfulness separately",
    "add unsupported-claim and post-rationalization risk categories",
    "use as V1.1 citation-eval candidate after review"
  ],
  "provenance_metadata": {
    "authority_level": "research_paper_review_needed",
    "license_or_terms_status": "review_needed",
    "intended_use": "evaluation_reference",
    "production_ingestion_allowed": false,
    "notes": "Candidate only; peer-review status and license require verification."
  }
}
```

## Deletion / Cleanup Candidates

No deletion is recommended at this stage.

Reason:

- MVP-015 artifacts are merged, scoped, and documented.
- Ginkgo/OpenAI benchmark source is intentionally raw P5 and not ingested.
- Existing docs/logs are useful for auditability.
- Deleting without a precise file-level review would violate no-destructive-change policy.

Future cleanup should be handled through a separate cleanup PR with:

- exact file path;
- reason for deletion;
- replacement or migration path;
- proof that no tests, docs, citations, or decision logs depend on it;
- explicit user approval.
