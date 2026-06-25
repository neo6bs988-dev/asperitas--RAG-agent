# V1.1A Failure Log Collector Decision Log

## Decision

Add a local V1.1A failure log schema, builder, JSONL writer, loader, and CLI so internal dogfood questions, dry-run results, security blocks, workflow failures, and deferred answer-provider gaps can be captured as structured evidence.

## Rationale

V1.0.0 internal verification established a clean dry-run baseline, but chat remains dry-run only and no real answer provider is wired. V1.1 needs a deterministic way to collect improvement evidence without changing retrieval, ranking, embeddings, vector storage, chunking, source registry behavior, answer generation, or default runtime behavior.

## Guardrails

- No real answer provider was wired.
- No external API calls were added.
- No source ingestion was added.
- No registry or chunk artifacts were mutated.
- No tags or GitHub releases were created.
- Failure records are JSON-safe and support explicit redaction notes.

## Implementation

- `src/asperitas_agent/failure_log.py` defines the schema, allowed values, deterministic ids, redaction helper, JSONL writer, and loader.
- `scripts/record_failure_log.py` prints one JSON record or writes one explicit JSONL record.
- `tests/test_failure_log.py` verifies validation, deterministic ids, explicit append/create-dir behavior, CLI behavior, and that retrieval/vector/reranker/answer/default runtime modules are not imported.

## Next Step

V1.1B Streamlit internal dogfood UI.
