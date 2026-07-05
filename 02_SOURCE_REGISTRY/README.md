# 02_SOURCE_REGISTRY

## Executive Bottom Line

This folder defines the V11.1 source registry contract for approved-only Asperitas RAG/agent development.

A source registry is not a production database. It is the control layer that prevents unreviewed, unlicensed, confidential, stale, or sensitive sources from being treated as approved retrieval, KG, training, or public-output material.

## Files

| File | Purpose |
|---|---|
| `source_registry.schema.json` | JSON Schema contract for registry entries and status-gated source use |
| `source_registry.example.json` | Non-production example showing candidate vs approved registry states |

## Required Source State Separation

```text
candidate
-> needs_review
-> approved
-> ingested
```

Blocked sources must stay blocked:

```text
blocked != approved
blocked != ingested
```

## Truth Boundary

Do not confuse these states:

| Exists | Does not prove |
|---|---|
| Source registry schema | Production source registry is populated |
| Candidate source entry | Source is approved |
| Approved source entry | Source is ingested, embedded, indexed, or KG-linked |
| Ingested source entry | Public-output approval or training approval |
| License note | Review complete unless approval reference exists |

## Minimum Required Fields

Every registry entry must include the required fields in `source_registry.schema.json`.

## Gate Rules

- `candidate` sources cannot be ingested, embedded, or KG-linked.
- `unknown`, `pending_review`, or `blocked` license status cannot be embedded or externally output.
- `ingested` status requires an ingestion run ID and decision log reference.
- `P6_BENCHMARK_DOCTRINE` sources can influence operating patterns but must not be cited as Asperitas internal implementation proof.
- Sensitive source tags require human review gates.

## How Future Code Should Use This Contract

1. Load registry entries.
2. Validate against `source_registry.schema.json`.
3. Reject or quarantine invalid entries.
4. Allow retrieval fixtures only from `approved` or `ingested` entries.
5. Preserve `source_id`, `priority`, `path_or_url`, `evidence_span_policy`, and `compliance_tags` into chunks, citations, eval fixtures, traces, and answer contracts.

## Validation Plan

The next source-code PR should add a standard-library test fixture that checks:

```text
schema JSON parses
example JSON parses
example entries include all schema-required fields
candidate entries keep all downstream allowed-flags false
unreviewed license entries cannot be used for external output
```

Recommended local checks for the current docs/schema layer:

```bash
python -m json.tool 02_SOURCE_REGISTRY/source_registry.schema.json >/tmp/source_registry.schema.pretty.json
python -m json.tool 02_SOURCE_REGISTRY/source_registry.example.json >/tmp/source_registry.example.pretty.json
```

## Current Status

This folder currently provides the schema contract and example only. It does not claim that the full source registry, ingestion pipeline, vector DB, KG, eval suite, review process, or production retrieval system is complete.
