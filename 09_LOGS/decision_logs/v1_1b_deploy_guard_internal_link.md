# V1.1B Deploy Guard Internal Link Decision Log

## Decision

Add an optional access gate and internal-link deployment documentation for the V1.1B Streamlit dogfood UI.

## Rationale

The dogfood UI is ready for controlled internal link sharing, but it must remain dry-run only and must warn operators not to enter secrets or sensitive private data. A configured `ASPERITAS_DOGFOOD_ACCESS_KEY` blocks access until the user enters the matching key. If no key is configured, the app allows local use while showing a strong local-only warning.

## Guardrails

- Dry-run only.
- No real answer provider wired.
- Not public SaaS.
- Not production deployment.
- No external API calls.
- Do not commit secrets, passwords, tokens, API keys, credentials, or `.streamlit/secrets.toml`.
- Deployment is controlled internal dogfood only.

## Dependency Decision

Add `requirements-streamlit.txt` with `streamlit` for demo-host deployment. Production/runtime dependencies in `pyproject.toml` are unchanged.

## Non-Change Statement

No retrieval, chunking, source-registry, eval-fixture, embedding, vector, reranker, answer, or default runtime behavior changed. No sources were ingested and registry/chunk artifacts were not mutated.

## Next Step

Deploy controlled internal dogfood link, collect 20-50 tests, then start V1.1C real RAG answer provider.
