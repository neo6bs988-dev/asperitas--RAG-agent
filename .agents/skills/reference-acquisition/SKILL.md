---
name: reference-acquisition
description: Use when adding external reference candidates for Asperitas V1 architecture, evaluation, workflow, skills, or security hardening. Metadata-only by default.
---

# Reference Acquisition Skill

## Purpose

Add trusted reference candidates without prematurely ingesting or copying full source content into the production knowledge base.

## Allowed Source Priority

1. Official OpenAI documentation.
2. Official Anthropic documentation.
3. Official MCP documentation.
4. Official LangGraph documentation.
5. Official LlamaIndex documentation.
6. Official RAGAS documentation or repository.
7. Peer-reviewed or review-needed RAG/security evaluation papers.
8. Official GitHub repositories.

## Rejected Production Sources

Do not add unofficial blogs, social posts, newsletters, copied tutorials, videos, or derivative summaries to production source material.

## Required Metadata Fields

```json
{
  "source_title": "",
  "source_url": "",
  "source_type": "official_docs | official_github_repo | peer_reviewed_paper | research_paper_review_needed",
  "publisher_or_org": "",
  "version_or_date": "",
  "retrieved_date": "",
  "summary": "",
  "architecture_principles": [],
  "implementation_patterns": [],
  "provenance_metadata": {
    "authority_level": "official | official_repo | peer_reviewed | review_needed",
    "license_or_terms_status": "unknown | review_needed | cleared",
    "intended_use": "architecture_reference | evaluation_reference | implementation_reference | security_reference",
    "production_ingestion_allowed": false,
    "notes": ""
  }
}
```

## Rules

- Store metadata first.
- Do not ingest full source text without explicit approval.
- Do not copy source code from external repositories without license and security review.
- Mark all paper candidates as `review_needed` until peer-review and license status are verified.
- Record whether each source maps to Knowledge, Skills, Workflow, Evaluation, Audit, or Security.
