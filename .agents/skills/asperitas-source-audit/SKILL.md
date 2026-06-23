---
name: asperitas-source-audit
description: Use when adding sources, source manifests, source registry fields, license status, disclosure level, citation metadata, or ingestion approval gates.
---

# Asperitas Source Audit Skill

## Purpose
Keep every knowledge object source-grounded, license-aware, and audit-ready.

## Workflow
1. Identify source type: internal, official, peer-reviewed, government/regulatory, industry, benchmark, commentary.
2. Assign priority and disclosure level.
3. Record title, organization/authors, URL or file path, date/version, license_status, terms_status, ingestion_status, and relevance tags.
4. For external public sources, default to metadata_only until license/terms review.
5. Preserve raw source separately from processed markdown/chunks.
6. Add tests or validation rules for required metadata fields.
7. Update source registry or manifest.

## Required Metadata
- source_id
- title
- authors_or_org
- source_type
- priority
- disclosure
- url_or_path
- date_or_version
- license_status
- terms_status
- ingestion_status
- verification_status
- relevance_tags

## Stop Rules
- Do not claim ingestion completed unless the pipeline logs it.
- Do not store full external text without approval.
- Do not convert external benchmark materials into Asperitas internal facts.
