# MVP-015 Ginkgo Benchmark Handoff

## Executive Bottom Line

MVP-015 should start as a read-only preflight for adapting the Ginkgo/OpenAI autonomous-lab paper into an Asperitas software benchmark pattern.

The target is not autonomous wet-lab execution. The target is to extract the reusable software architecture pattern:

- schema-first AI output validation
- deterministic workflow specification objects
- explicit human approval boundaries
- run/result metadata capture
- metrics-driven evaluation
- decision/hypothesis logging
- compliance-aware closed-loop planning

This file is a Codex handoff document only. It does not ingest the Ginkgo source, modify retrieval behavior, add embeddings, create a vector DB, create a knowledge graph, or claim production autonomous-lab capability.

## Current Project Boundary

MVP-001 through MVP-014 are treated as complete for the purpose of this handoff, with MVP-014 Agent Role Registry Phase 1 closed out through PR #45. MVP-015 must start from current `main` after verifying branch, HEAD, git status, and origin sync.

Non-negotiable continuity rules:

- `mvp003` remains the protected deterministic reference retriever.
- `hybrid` remains explicit/manual/experimental only.
- deterministic-test reranker remains explicit opt-in and non-default.
- no production hybrid claim.
- no autonomous wet-lab claim.
- no ingestion unless explicitly approved.
- no source registry, chunk, eval fixture, retrieval ranking, or runtime behavior change during preflight.

## Ginkgo Benchmark Pattern To Extract

Codex should inspect the Ginkgo/OpenAI source, if accessible, only to identify implementation-relevant architecture patterns:

1. iterative design -> validation -> execution -> data return -> analysis -> next-design loop
2. Pydantic-style validation schema for AI-designed experiment objects
3. programmatic workflow translation boundary
4. metadata and results capture
5. metrics-driven optimization loop
6. human intervention / human approval boundary
7. failure handling for invalid AI-generated designs
8. separation between benchmark claim, internal implementation, and verified capability

The Ginkgo paper's reported performance metrics must not be represented as Asperitas performance. They are benchmark context only.

## MVP-015 Recommended Scope

Recommended MVP-015 name:

`MVP-015 Ginkgo Benchmark Workflow Preflight & Schema Layer`

Recommended preflight deliverables:

1. Confirm whether the Ginkgo/OpenAI source is accessible in the repo/workspace.
2. Classify its status:
   - raw only
   - processed markdown
   - chunked
   - source-registry covered
   - eval-covered
3. Map the Ginkgo benchmark into Asperitas-safe software abstractions:
   - `BenchmarkWorkflowSpec`
   - `ExperimentDesignObject`
   - `ValidationSchema`
   - `WorkflowTranslationBoundary`
   - `RunLog`
   - `MetricObject`
   - `HypothesisLog`
   - `HumanApprovalGate`
4. Propose the smallest safe implementation plan.
5. Report GO/NO-GO before any code edit.

## Explicit Non-Goals

MVP-015 must not:

- execute wet-lab workflows
- generate actionable experimental protocols for execution
- connect to cloud labs, LIMS, ELN, robotics, or external execution systems
- claim autonomous biology capability
- change default retrieval behavior
- make hybrid retrieval the default
- make reranking the default
- ingest raw sources without approval
- mutate chunks, source registry, eval fixtures, or answer-generation behavior during preflight
- imply legal, IP, biosafety, or regulatory approval

## Preflight Inspection Order

Codex should inspect, in order:

1. `README.md` or `README`
2. `AGENTS.md` or `AGENTS`
3. `.agents/`
4. latest MVP-014 closeout docs and decision logs
5. `src/`
6. `tests/`
7. `eval/`
8. `data/`
9. `03_PROCESSED_KB/`
10. `01_RAW_SOURCES/` only as needed to confirm Ginkgo source accessibility

## Copy-Ready Codex Prompt

```text
Use AGENTS.md and the relevant .agents/skills instructions.

Task:
MVP-015 preflight only: Ginkgo/OpenAI autonomous-lab benchmark adaptation for Asperitas RAG Agent.
Do not implement yet.

Context:
- Repo: neo6bs988-dev/asperitas--RAG-agent
- Start from current main after verifying repo state.
- MVP-001~MVP-014 are complete for this handoff.
- MVP-014 Agent Role Registry Phase 1 closeout PR #45 is expected merged; verify it from repo state.
- Benchmark source: Ginkgo/OpenAI autonomous-lab paper on GPT-5-driven CFPS optimization, if accessible in repo/workspace.
- Purpose: benchmark Ginkgo's software process, not reproduce autonomous wet-lab execution.

Benchmark concepts to inspect:
1. iterative design -> validation -> execution -> data return -> analysis -> next design loop
2. Pydantic-style validation schema for AI-designed experiments
3. programmatic workflow translation layer
4. metadata/results capture
5. human approval / human intervention boundary
6. metrics-driven optimization loop

Constraints:
- Preflight only.
- Do not edit files.
- Do not ingest new sources.
- Do not call external services.
- Do not create wet-lab automation.
- Do not claim autonomous lab capability.
- Preserve mvp003 as protected deterministic reference retriever.
- hybrid = explicit/manual/experimental only.
- deterministic-test reranker = opt-in/non-default only.
- no production hybrid claim.
- no autonomous wet-lab claim.
- Any biosafety, protocol, wet-lab, legal, licensing, or IP issue must be flagged.

Required inspection:
1. Read README.md, AGENTS.md, .agents/skills if present.
2. Check branch, HEAD, git status, origin sync.
3. Inspect MVP-014 closeout docs/logs if present.
4. Confirm whether the Ginkgo/OpenAI PDF is accessible.
5. Inspect current docs, eval, tests, src, data only as needed.
6. Identify the smallest safe MVP-015 implementation plan.

Report:
1. current branch / HEAD / git status
2. whether Ginkgo source is accessible
3. source status: raw only / processed / chunked / eval-covered
4. Ginkgo benchmark patterns relevant to Asperitas
5. proposed MVP-015 scope
6. explicit non-goals
7. proposed files to create/edit
8. proposed schemas/data models
9. tests/eval commands to run
10. compliance/wet-lab/IP risks
11. GO or NO-GO for implementation
```

## Verification Expectation

Because this is a documentation/handoff update, no source-code tests are required for the handoff itself. If MVP-015 later changes code, Codex must run the relevant unit tests, artifact verification, and retrieval evals if retrieval/chunking/scoring/embedding/reranking/answer-generation behavior is affected.
