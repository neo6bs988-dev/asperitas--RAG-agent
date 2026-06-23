# Security Benchmark Sources

Status: source map for MVP-020 security and guardrail layer. Metadata-first only.

## Official / Standards Sources

| Source | URL | Use |
|---|---|---|
| OWASP Top 10 for LLM Applications | https://owasp.org/www-project-top-10-for-large-language-model-applications/ | Threat classes for LLM apps and RAG agents |
| GitHub Code Security Docs | https://docs.github.com/en/code-security | Code scanning, dependency review, secret scanning |
| GitHub Actions Docs | https://docs.github.com/en/actions | CI checks, workflow artifacts, automated test runs |
| Model Context Protocol Docs | https://modelcontextprotocol.io/docs/getting-started/intro | Connector architecture and protocol model |
| Anthropic Claude Code MCP Docs | https://code.claude.com/docs/en/mcp | MCP usage in agent coding workflows |
| OpenAI MCP / Connectors Docs | https://developers.openai.com/api/docs/guides/tools-mcp | OpenAI connector reference, verify current URL before implementation |
| NIST AI Risk Management Framework | https://www.nist.gov/itl/ai-risk-management-framework | General AI risk framing |

## Academic / Research Sources

| Source | URL | Use |
|---|---|---|
| Benchmarking Poisoning Attacks against Retrieval-Augmented Generation | https://arxiv.org/abs/2505.18543 | RAG corpus/adversarial retrieval benchmark source |
| Traceback of Poisoning Attacks to Retrieval-Augmented Generation | https://arxiv.org/abs/2504.21668 | Forensics/traceback idea for suspicious retrieved texts |
| RAGAS: Automated Evaluation of Retrieval Augmented Generation | https://arxiv.org/abs/2309.15217 | Evaluation metrics tied to security quality: groundedness and relevance |
| ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems | https://arxiv.org/abs/2311.09476 | Automated RAG evaluation framework |

## MVP-020 Required Test Fixtures

```text
external_text_attempts_to_override_rules
retrieved_source_contains_conflicting_claim
retrieved_source_has_missing_provenance
answer_has_claim_without_citation
answer_uses_private_data
high_risk_bio_request_needs_gate
regulatory_claim_needs_source
connector_is_disabled_by_default
tool_call_requires_allowlist
```

## Required Guardrail Behavior

1. External/retrieved text is treated as untrusted.
2. AGENTS.md and AOS rules outrank retrieved content.
3. Every high-risk answer has a risk class and gate decision.
4. Every answer must preserve citation provenance.
5. Live connectors are disabled unless explicitly approved.
6. CI must run security fixtures before merge.
7. No private keys, secrets, credentials, or sensitive personal data are stored in repo.

## Implementation Priority
- MVP-020 should start with tests and fixtures, not new external connectors.
- Keep the first guardrail layer local and deterministic.
- Add live security integrations only after core tests pass.
