# V1 Internal Deploy Guide

Status: internal release-candidate guide

## Scope

V1 is a local/internal chat-style RAG control wrapper. It provides:

- source-grounded workflow gates
- security guard checks
- audit trace events
- eval and regression artifacts
- dry-run CLI by default
- explicit output paths only

## Non-Scope

V1 is not:

- public SaaS
- production customer deployment
- web-productized commercial platform
- autonomous wet-lab execution
- MCP or external connector automation
- default vector DB, reranker, or embedding replacement
- real RAG answer provider default wiring
- regulatory, clinical, commercial, or biological model performance proof

## Internal Deploy Flow

1. Clone or pull `main`.
2. Create a virtual environment and install dependencies using the repo's current supported setup.
3. Run full pytest.
4. Run `python scripts/verify_artifacts.py`.
5. Run security guard smoke: `python scripts/run_security_guard.py --input security_input.json --json`.
6. Run chat dry-run smoke: `python scripts/ask_asperitas_agent.py --question "What is Asperitas RAG Agent?" --json`.
7. Run release readiness: `python scripts/check_v1_release_readiness.py --json`.
8. Collect failure logs during internal use.
9. Open V1.1 performance tickets from real failures.

## Smoke-Test Inputs

Use explicit local JSON files for security and chat workflow testing. Do not paste secrets, private keys, customer data, partner data, unpublished biological data, or personal data into smoke-test inputs.

## Failure Handling

Record:

- command run
- input path or question
- status returned
- warnings and errors
- audit events emitted
- whether the failure was security, workflow, eval, artifact, or operator setup

Do not treat a passing smoke test as production readiness.

## Web Productization Boundary

A successful V1 internal deploy only proves the local/internal wrapper. It does not prove web-product readiness.

Before any web-product or commercial claim, require the separate MVP-011 to MVP-013 path:

```text
MVP-011 Web Productization Foundation
-> MVP-012 Web App MVP
-> MVP-013 Production Readiness Gate
```

Required additional evidence includes:

- backend/API contract;
- LLM provider adapter and fallback policy;
- authentication and role model;
- secrets/environment policy;
- deployment target and rollback path;
- observability for request ID, trace ID, retrieval IDs, verifier status, compliance status, latency, token/cost metrics;
- security/privacy/source-license/compliance review;
- human approval for public, investor, regulatory, legal, or biological performance claims.
