# Web Productization Roadmap

## Executive Bottom Line

The final goal is commercialization through a web-productized Asperitas AI platform. The current repo should still build internal RAG/agent correctness first; web productization begins only after source-grounding, verifier, compliance, eval, and internal API/UI gates are credible.

GitHub is the execution headquarters. The web product is created when this repository's code is deployed behind a backend/API, authenticated UI, LLM provider adapter, retrieval/vector store, verifier, compliance gate, observability layer, and release process.

## What GitHub Does And Does Not Do

GitHub is not the AI runtime by itself.

```text
GitHub repo
-> reviewed code, docs, tests, evals, CI, PR evidence
-> deployment pipeline
-> hosted backend/API
-> LLM provider + RAG/vector/KG infrastructure
-> authenticated web UI
-> monitoring, logs, audit, cost controls
-> commercial product
```

## Web Productization MVPs

| MVP | Name | Purpose | Exit condition |
|---|---|---|---|
| MVP-010 | Internal UI/API | Operate internal RAG pipeline with evidence/compliance visibility | internal API/UI runs with citations, retrieval scores, warnings, CI evidence |
| MVP-011 | Web Productization Foundation | Add production-shaped backend, LLM adapter, auth boundary, deployment plan, observability contract | backend/API contract, provider adapter, auth model, env/secrets policy, logs/tracing/cost plan documented and testable |
| MVP-012 | Web App MVP | Build authenticated web app for source-grounded AI workflows | web UI supports login, query, retrieved evidence, citations, verifier status, compliance warnings, operator review |
| MVP-013 | Production Readiness Gate | Block unsafe commercialization claims until security/compliance/reliability gates pass | security/privacy/license/compliance/cost/latency/rollback/release gates documented with evidence |

## Required Product Architecture

```text
Frontend
  Next.js / React or equivalent

Backend API
  FastAPI / Next.js API / equivalent
  request validation
  auth context
  workflow routing

LLM Provider Layer
  OpenAI / Anthropic / local model adapter
  provider-agnostic interface
  cost/latency/token telemetry
  fallback and refusal behavior

RAG Core
  source registry
  ingestion/chunking
  metadata and evidence spans
  retrieval/reranking
  vector store / hybrid retrieval

Verifier + Compliance
  claim extraction
  evidence-span matching
  support-status classification
  answer-level diagnostics
  CITES/Nagoya/LMO/biosafety/IP/privacy gates

Observability
  trace IDs
  retrieval payload logs
  answer contract logs
  guardrail events
  latency/cost metrics
  failure taxonomy

Deployment
  CI/CD
  secrets management
  environment separation
  rollback path
  release log
```

## Why LLM Use Does Not Destroy Asperitas Independence

Using an external LLM does not make the product non-proprietary if the proprietary layer is built around it.

External LLM role:

```text
language reasoning / synthesis / tool-call planning
```

Asperitas proprietary layer:

```text
approved source registry
-> biological metadata schema
-> biodiversity/compliance provenance
-> retrieval and reranking logic
-> grounded answer contract
-> claim-to-citation verifier
-> compliance and biosafety gate
-> eval and regression datasets
-> DBTL/failure learning records
-> IP/product decision logs
-> proprietary biological datasets
```

The LLM must remain replaceable. The moat should compound through data, metadata, validation, evals, compliance trust, workflow integration, and IP evidence.

## Stage Gates

### Gate A: Internal Correctness

Required before external users:

- source registry and approved-only ingestion path exists;
- retrieval evals are repeatable;
- grounded answer contract exists;
- unsupported claims are detected or blocked;
- compliance escalation behavior exists;
- internal UI/API exposes debug evidence.

### Gate B: Web Product Foundation

Required before web MVP:

- backend API contract;
- provider adapter contract;
- auth and role model;
- secrets and environment policy;
- observability schema;
- deployment target selected;
- rollback path documented.

### Gate C: Commercial Readiness

Required before commercialization claims:

- security review;
- privacy review;
- source license review;
- CITES/Nagoya/LMO/legal review where relevant;
- cost/latency budget;
- uptime/error handling;
- public-claims evidence review;
- human approval gate.

## Recommended Immediate Path

1. Close current MVP quality gates without overclaiming.
2. Build vector/hybrid/reranker/answer/compliance layers in order.
3. Add internal API/UI.
4. Create MVP-011 backend/API/provider/auth/observability contract.
5. Build MVP-012 web app only after Gate B is clear.
6. Treat MVP-013 as commercialization gate, not a docs exercise.
