# Deep Research to Registry Workflow

## Executive Bottom Line

External research and benchmark material enters the repo as a source candidate first. It can support retrieval, eval fixtures, KG extraction, training, or public output only after registry review.

## State Flow

```text
candidate -> needs_review -> approved -> ingested
```

Terminal or inactive states:

```text
blocked
archived
```

## Promotion Gates

| Promotion | Required evidence |
|---|---|
| `candidate` -> `needs_review` | source pointer, relevance note, owner |
| `needs_review` -> `approved` | license, confidentiality, authority, freshness, and compliance review |
| `approved` -> `ingested` | ingestion run ID, collection status, and decision log reference |
| any state -> `blocked` | reason, owner, date, and affected allowed uses |

## Output Contract

```text
workflow_run_id:
source_candidates_reviewed:
new_registry_entries:
status_changes:
blocked_sources:
open_review_items:
compliance_flags:
owner:
date:
decision_log_ref:
```

## Current Status

Workflow documentation only. No crawler, ingestion engine, vector DB, KG, or automated approval system is implemented here.
