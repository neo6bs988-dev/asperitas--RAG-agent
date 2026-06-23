---
name: asperitas-mcp-expansion
description: Use when planning MCP-style connectors, external source acquisition, live APIs, PubMed/Crossref/patent/regulatory connectors, or tool allowlists.
---

# Asperitas MCP Expansion Skill

## Purpose
Prepare future external source connectors with source governance and approval gates.

## Benchmark References
- Model Context Protocol: standard connector architecture.
- OpenAI MCP/connectors docs: tool integration patterns.
- Anthropic MCP docs: Claude Code connector usage.
- LlamaIndex MCP docs: RAG connector integration references.

## Future Connector Candidates
```text
PubMed / NCBI E-utilities
Europe PMC
Crossref
USPTO / EPO / WIPO / Google Patents public pages
SEC EDGAR
Government/regulatory sites
Company official sites
Internal GitHub/Drive only with permission
```

## Required Connector Gate
Before enabling any connector:
1. Source legality reviewed.
2. Connector is read-only by default.
3. Tool schema is typed.
4. Returned content preserves URL/source/date.
5. Rate limits and retries are controlled.
6. Returned content is treated as untrusted input.
7. Outputs are logged.
8. State-changing tools require explicit human approval.

## Workflow
1. Start with a source manifest entry, not code.
2. Define connector scope and allowed operations.
3. Design typed request/response schemas.
4. Add disabled-by-default behavior.
5. Add documentation and decision log entry.
6. Only then implement minimal connector code.

## Output Requirements
Report:
1. Connector objective
2. Source status
3. Read/write scope
4. Schema design
5. Access gates
6. Files changed
7. Tests run
8. Remaining approval needs

## Stop Rules
- Do not enable live connectors by default.
- Do not collect full external text unless license/terms allow it or a human approves.
- Do not put private access material in repo.
- Do not bypass source registry or compliance gates.
