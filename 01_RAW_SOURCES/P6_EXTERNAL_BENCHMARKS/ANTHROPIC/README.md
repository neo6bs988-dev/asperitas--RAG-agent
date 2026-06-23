# ANTHROPIC Benchmark Notes

Priority: P6 External Benchmark
Use: Agent Skills, progressive disclosure, MCP, Claude Code operating patterns.

## Sources
1. Agent Skills engineering article
   - URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
2. Agent Skills open standard
   - URL: https://agentskills.io
3. Model Context Protocol
   - URL: https://modelcontextprotocol.io

## Patterns to Absorb
- A skill is an organized folder of instructions, scripts, and resources.
- Skills are like onboarding guides for agents.
- Progressive disclosure reduces context load.
- Scripts can provide deterministic, repeatable operations.
- Start with evaluation: build skills to fix observed agent failures.
- Split long skill instructions into separate referenced files.
- Skills and MCP are complementary: skills teach workflows; MCP connects tools/data sources.

## Asperitas V1 Application
- Use Skills for internal workflows now.
- Reserve MCP for V1+ external-source connectors after security review.
- Treat MCP as future PubMed/Crossref/patent/regulatory connector layer, not as MVP-016 scope.
- Audit any external skill or connector before enabling it.
