# AGENT_SECURITY Benchmark Notes

Priority: P6 External Benchmark
Use: V1 safety and adversarial testing.

## Sources
1. OWASP Top 10 for LLM Applications
   - URL: https://owasp.org/www-project-top-10-for-large-language-model-applications/
2. MCP and agent security advisories/articles
   - Use public security reports as low-priority risk intelligence unless official primary source is available.

## Risk Classes for Asperitas Agent
- Prompt injection in retrieved sources
- Source poisoning
- Unsupported claims presented as facts
- Unsafe citation behavior
- Secret or private-data exposure
- Tool misuse
- Overclaiming ingestion, eval, compliance, or deployment status
- Biological, legal, regulatory, or investor-sensitive output without human approval

## Asperitas V1 Application
- Add adversarial eval questions.
- Add unsafe-source fixtures.
- Add citation verification tests.
- Add refusal/escalation tests for high-risk bio/compliance/legal cases.
- Treat all external connectors as disabled until explicitly approved.
