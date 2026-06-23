---
name: asperitas-workflow
description: Use when designing or modifying planner/retriever/reranker/validator/answer workflows, LangGraph-style state machines, or V1 agent orchestration.
---

# Asperitas Workflow Skill

## Purpose
Move the system from simple RAG to auditable agent workflow.

## Benchmark Reference
LangGraph-style architecture: explicit state, nodes, transitions, validation gates, and stop conditions.

## Target V1 Flow
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

## Workflow
1. Identify the current execution path.
2. Separate hidden monolith steps into named stages.
3. Define each stage's input, output, errors, and stop rules.
4. Add tests for normal, missing-source, conflicting-source, and high-risk cases.
5. Log state transitions where useful for audit.
6. Keep the first implementation lightweight before adding new framework dependencies.

## Output Requirements
Report:
1. Objective
2. Workflow stages affected
3. State schema changes
4. Files changed
5. Tests run
6. Failure modes covered
7. Remaining architecture debt
8. Next MVP action

## Stop Rules
- Do not add framework complexity without clear need.
- Do not bypass citation or compliance gates.
- Do not merge planner/validator/output into one opaque step.
