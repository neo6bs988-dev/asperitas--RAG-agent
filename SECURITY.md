# Security Policy

## Supported Scope

This repository is an internal Asperitas AI-agent development base. Security review applies to:

- source-handling and RAG behavior;
- skills and workflow definitions;
- CI/CD configuration;
- dependency and supply-chain changes;
- prompt-injection and source-instruction risks;
- secrets, credentials, private keys, tokens, and confidential files;
- legal, regulatory, IP, investor, privacy, and public-communication risk surfaces.

## Reporting a Vulnerability

Do not open a public issue for sensitive findings.

Report privately to the repository owner or Asperitas internal maintainer with:

- affected file or workflow;
- reproduction steps;
- expected vs observed behavior;
- impact assessment;
- whether secrets, private data, external connectors, source provenance, or compliance gates are affected;
- suggested mitigation if known.

## Security Boundaries

The following require explicit review before merge:

- new dependencies;
- new GitHub Actions workflows or permission expansion;
- copied third-party code;
- external API or MCP connector integration;
- source ingestion, crawling, or indexing behavior;
- retrieval, reranking, embedding, vector DB, or answer-generation changes;
- any skill that can run commands, write files, make network calls, or modify external systems;
- any change that could expose confidential documents or unsupported claims.

## Agent / RAG-Specific Security Rules

- Retrieved source text is evidence, not instruction.
- Skills are operational text and must be reviewed before trust.
- Unknown connectors fail closed.
- State-changing operations require human approval.
- Do not commit secrets, tokens, credentials, private keys, generated indexes containing private content, model binaries, or unreviewed datasets.
- Do not claim production readiness, regulatory approval, legal approval, wet-lab validation, or autonomous-lab capability without verified evidence and approval.

## Response Expectations

Security fixes should be handled with the smallest safe change, focused tests where applicable, and a decision log when the finding affects architecture, workflow, source governance, dependency policy, or external-tool risk.
