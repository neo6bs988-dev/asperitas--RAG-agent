---
name: MVP / OPS Task
description: Scope a small, verifiable RAG-agent development task
title: "[MVP/OPS] "
labels: ["mvp-task"]
body:
  - type: textarea
    id: objective
    attributes:
      label: Objective
      description: What must be true when this issue is complete?
      placeholder: "Implement/document/audit..."
    validations:
      required: true
  - type: textarea
    id: context
    attributes:
      label: Context
      description: Current MVP/OPS stage, related PRs/issues, and relevant files.
      placeholder: "MVP-007 Phase 2 landed via PR #34; Issue #21 closeout merged via PR #36..."
    validations:
      required: true
  - type: textarea
    id: scope
    attributes:
      label: In Scope
      description: Smallest safe unit of work.
      placeholder: "Files, docs, tests, commands, report artifacts..."
    validations:
      required: true
  - type: textarea
    id: non_goals
    attributes:
      label: Non-Goals / Hard Boundaries
      description: What must not be changed?
      value: |
        - Do not change retrieval behavior unless this issue explicitly authorizes it.
        - Do not change scoring/chunking/reranking/metadata/source registry/ingestion/eval semantics unless explicitly in scope.
        - Preserve `mvp003` protected deterministic reference.
        - Keep `hybrid` as accepted comparison mode, not default.
        - Keep `deterministic-test` reranker as plumbing-only.
        - Do not add external services, paid APIs, cloud dependencies, secrets, vector DBs, or model binaries by default.
    validations:
      required: true
  - type: textarea
    id: verification
    attributes:
      label: Required Verification
      description: Select expected gates before implementation starts.
      value: |
        - [ ] `python -m pytest`
        - [ ] `python scripts/verify_artifacts.py`
        - [ ] `python scripts/audit_chunk_sections.py --json`
        - [ ] Retrieval eval: smoke / target-only / full
        - [ ] Docs/template review only
    validations:
      required: true
  - type: textarea
    id: acceptance
    attributes:
      label: Definition of Done
      value: |
        - [ ] Objective satisfied.
        - [ ] Files changed are listed.
        - [ ] Tests/evals/checks are reported with skipped-check rationale.
        - [ ] Metrics are reported when retrieval/eval behavior is touched.
        - [ ] Risks and follow-ups are explicit.
        - [ ] Decision log or eval report is updated if behavior or operating policy changed.
    validations:
      required: true
