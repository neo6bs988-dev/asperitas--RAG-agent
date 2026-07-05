# 02_SOURCE_REGISTRY

## Executive Bottom Line

This folder defines the V11.1 source registry contract for approved-only Asperitas RAG/agent development.

A source registry is not a production database. It is the control layer that prevents unreviewed, unlicensed, confidential, stale, or compliance-sensitive sources from being treated as approved retrieval, KG, training, or public-output material.

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
| Ingested source entry | Legal approval for public output or training |
| License note | Counsel/legal review complete unless approval reference exists |

## Minimum Required Fields

Every registry entry must include:

```text
source_id
title
path_or_url
priority
source_type
confidentiality
license_status
collection_status
verification_status
registry_status
owner
updated_at
allowed_use
compliance_tags
evidence_span_policy
decision_implication
ingestion_allowed
embedding_allowed
kg_allowed
external_output_allowed
```

## Gate Rules

- `candidate` sources cannot be ingested, embedded, or KG-linked.
- `unknown`, `pending_review`, or `blocked` license status cannot be embedded or externally output.
- `ingested` status requires an ingestion run ID and decision log reference.
- `P6_BENCHMARK_DOCTRINE` sources can influence operating patterns but must not be cited as Asperitas internal implementation proof.
- `CITES`, `Nagoya/ABS`, `LMO/GMO`, biosafety, biosecurity, IP, privacy, investor/public claim, or legal-review tags require human approval gates.

## How Future Code Should Use This Contract

1. Load registry entries.
2. Validate against `source_registry.schema.json`.
3. Reject or quarantine invalid entries.
4. Allow retrieval fixtures only from `approved` or `ingested` entries.
5. Allow production ingestion only when license, confidentiality, verification, and decision-log evidence pass.
6. Preserve `source_id`, `priority`, `path_or_url`, `evidence_span_policy`, and `compliance_tags` into chunks, citations, eval fixtures, traces, and answer contracts.

## Current Status

This folder currently provides the schema contract and example only. It does not claim that the full source registry, ingestion pipeline, vector DB, KG, eval suite, legal review, or production retrieval system is complete.
