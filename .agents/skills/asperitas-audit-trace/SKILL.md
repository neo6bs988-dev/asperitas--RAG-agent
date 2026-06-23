---
name: asperitas-audit-trace
description: Use when adding answer trace logs, audit schemas, citation coverage reports, decision logs, provenance logs, or V1 traceability features.
---

# Asperitas Audit Trace Skill

## Purpose
Make every important agent output traceable from user query to retrieved evidence to final answer.

## Benchmark References
- LangSmith: evaluation datasets, experiments, runs, traces.
- Phoenix: LLM/RAG tracing model.
- Benchling: audit-first R&D data governance.
- LangGraph: persisted workflow state.

## Required Trace Fields
```yaml
query_id: string
query: string
query_class: string
risk_class: string
workflow_stage: string
retrieved_contexts:
  - source_id
    chunk_id
    title
    priority
    disclosure
    score
    citation
validation_result: object
compliance_gate: object
answer_id: string
citations: list
warnings: list
eval_snapshot: object
created_at: timestamp
```

## Workflow
1. Read existing logging, eval, retrieval, and answer-generation modules.
2. Identify where query, retrieval, validation, and answer data already exist.
3. Add the smallest trace schema that can be serialized locally.
4. Preserve source provenance and citation metadata.
5. Add tests for trace creation, missing citations, and high-risk gate traces.
6. Save trace outputs as JSON or JSONL artifacts.

## Output Requirements
Report:
1. Objective
2. Trace fields added
3. Files changed
4. Tests run
5. Example artifact path
6. Risks
7. Remaining gaps
8. Next MVP action

## Stop Rules
- Do not log credentials, secrets, or private personal data.
- Do not claim production observability is complete unless deployed and verified.
- Do not make audit logs optional for high-risk outputs.
