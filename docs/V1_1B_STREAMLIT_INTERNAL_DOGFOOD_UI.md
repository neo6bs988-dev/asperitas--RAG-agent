# V1.1B Streamlit Internal Dogfood UI

## Scope

V1.1B adds a minimal Streamlit UI for local/internal dogfood testing of the existing chat workflow in dry-run mode.

The UI is internal/local only, dry-run only, has no real answer provider wired, is not public SaaS, and is not production deployment.

## Files

- `apps/internal_dogfood_app.py`
- `tests/test_internal_dogfood_app.py`
- `09_LOGS/decision_logs/v1_1b_streamlit_internal_dogfood_ui.md`

## Behavior

The app lets an internal user enter:

- `question`
- `session_id`
- optional expected behavior
- optional notes

When the user clicks the run button, the app calls `asperitas_agent.chat_workflow.run_chat_workflow` with no answer provider. The expected successful dry-run state is `dry_run_ready` with the existing warning that no answer provider is wired.

The app displays status, warnings, a security summary, workflow acceptance detail, and audit event count where available.

## Failure Logging

Failure logging uses the existing V1.1A `asperitas_agent.failure_log` collector.

The default output path is:

`09_LOGS/failure_logs/v1_1b_dogfood_failures.jsonl`

No failure log is written during import, form editing, or dry-run execution. A JSONL record is saved only when the user clicks the save button and acknowledges the redaction warning for free-text fields.

The UI exposes the V1.1A category, severity, and status enumerations. Actual behavior is auto-filled from the dry-run result and remains editable before explicit save.

## Redaction Boundary

Any free-text field can contain sensitive material. Before saving, the UI requires explicit acknowledgement that the user reviewed and redacted secrets, raw private files, environment variables, credentials, and sensitive data.

The UI does not display environment variables, secrets, or raw private files.

## Dependency Note

Streamlit was not present in `pyproject.toml` at implementation time. V1.1B does not add a required dependency. The app file imports cleanly without Streamlit and prints a clear message if run directly without Streamlit installed.

If Streamlit is available in the local environment, run:

```powershell
streamlit run apps/internal_dogfood_app.py --server.address 127.0.0.1 --server.port 8501
```

## Non-Change Statement

V1.1B does not change retrieval, chunking, source registry, evaluation fixtures, embeddings, vector database behavior, reranking, answer generation, or default runtime behavior. It does not ingest new sources and does not mutate registry or chunk artifacts.

## Remaining Limitation

The app remains a dry-run dogfood surface only. Real RAG answer provider integration is intentionally deferred to V1.1C.
