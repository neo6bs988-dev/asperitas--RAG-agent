# V1.1B Streamlit Internal Dogfood UI Decision Log

## Decision

Add a minimal local/internal Streamlit dogfood UI for the existing chat workflow dry-run path.

## Rationale

V1.0.0 internal verification passed and V1.1A added the failure log collector. V1.1B needs a small operator-facing surface to submit questions, inspect dry-run/security/workflow/audit status, and optionally save failure log JSONL records without wiring a real answer provider.

## Guardrails

- Internal/local only.
- Dry-run only.
- No real answer provider wired.
- Not public SaaS.
- Not production deployment.
- No external API calls.
- No source ingestion.
- No registry or chunk artifact mutation.
- No retrieval, embedding, vector, reranker, answer generation, or default runtime behavior changes.

## Implementation Notes

The app imports existing modules:

- `asperitas_agent.chat_workflow`
- `asperitas_agent.failure_log`

Failure log writing is explicit and requires redaction acknowledgement before save. The default output path is `09_LOGS/failure_logs/v1_1b_dogfood_failures.jsonl`.

Streamlit was not added as a required dependency because it is not currently declared in project dependencies. The app helper functions and tests work without launching a browser or starting a Streamlit server.

## Next Step

V1.1C real RAG answer provider integration.
