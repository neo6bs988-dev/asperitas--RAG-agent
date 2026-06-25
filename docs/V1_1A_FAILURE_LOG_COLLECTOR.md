# V1.1A Failure Log Collector

V1.1A adds a local, JSONL-friendly failure evidence collector for internal dogfood and dry-run improvement work. It records observed failures without changing retrieval, chunking, embeddings, vector DB behavior, reranking, answer generation, or default runtime behavior.

## Scope

The collector is for structured evidence from:

- internal dogfood questions
- dry-run results
- security overblocks
- workflow failures
- deferred answer-provider gaps
- source, citation, format, and user-need gaps

It does not wire a real answer provider, call external APIs, ingest new sources, create tags, create releases, or mutate registry/chunk artifacts.

## Schema

Each JSONL line is one record with these fields:

- `schema_version`
- `failure_id`
- `created_at_utc`
- `session_id`
- `query`
- `expected_behavior`
- `actual_behavior`
- `category`
- `severity`
- `status`
- `source_context`
- `security_result`
- `workflow_result`
- `dry_run_result`
- `reproduction_steps`
- `proposed_fix`
- `redaction_notes`
- `metadata`

`failure_id` is deterministic when `query`, `category`, `created_at_utc`, and `session_id` are provided.

Allowed categories are `retrieval_miss`, `source_gap`, `citation_issue`, `unsupported_claim`, `security_overblock`, `workflow_overblock`, `dry_run_provider_needed`, `format_issue`, `internal_dogfood_feedback`, `user_need_unknown`, and `other`.

Allowed severities are `low`, `medium`, `high`, and `critical`. Allowed statuses are `open`, `triaged`, `in_progress`, `resolved`, and `wont_fix`.

## CLI

Print one JSON record without writing a file:

```powershell
python scripts/record_failure_log.py `
  --query "What is Asperitas RAG Agent?" `
  --expected-behavior "Should return dry-run status or source-grounded answer when provider exists." `
  --actual-behavior "dry_run_ready; no answer provider wired." `
  --category dry_run_provider_needed `
  --severity medium `
  --status open `
  --json
```

Append one JSONL record to an explicit path:

```powershell
python scripts/record_failure_log.py `
  --query "What is Asperitas RAG Agent?" `
  --expected-behavior "Should return dry-run status or source-grounded answer when provider exists." `
  --actual-behavior "dry_run_ready; no answer provider wired." `
  --category dry_run_provider_needed `
  --severity medium `
  --status open `
  --output 09_LOGS/failure_logs/v1_1a_dogfood_failures.jsonl `
  --create-dirs `
  --append `
  --json
```

No output file is written unless `--output` is provided. Existing output files require `--append`. Missing parent directories require `--create-dirs`.

## Redaction Expectations

Failure records must not contain secrets, private keys, credentials, raw confidential source text beyond what is necessary for diagnosis, personal data, or proprietary wet-lab details. Use summary-level context where possible, and explain removals in `redaction_notes`.

The helper `redact_failure_payload` redacts keys containing `secret`, `token`, `api_key`, `password`, `private_key`, or `credential`, but callers remain responsible for reviewing free-text fields before writing evidence.

## Limitations

The collector stores local evidence only. It does not triage, rank, or resolve failures automatically, and it does not prove public SaaS readiness, production deployment, autonomous wet-lab execution, regulatory readiness, clinical/commercial performance, or bio-model capability.
