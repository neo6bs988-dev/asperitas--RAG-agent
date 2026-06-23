# GINKGO Benchmark Notes

Priority: P6 External Benchmark
Use: DBTL, autonomous-lab, cloud-lab, schema validation, and biology operating-system benchmark.

## Sources
1. Ginkgo Bioworks official site
   - URL: https://www.ginkgo.bio
2. GPT-5 autonomous lab / CFPS optimization paper
   - Local uploaded file in project context; verify public URL/license before redistributing.

## Patterns to Absorb
- DBTL loop discipline: Design -> Build -> Test -> Learn.
- Programmatic experiment specification before lab execution.
- Schema validation before experiment execution.
- Automated data capture and analysis.
- Human approval gates for wet-lab and biosafety-sensitive actions.

## Asperitas V1 Application
For V1 RAG Agent, apply only the software architecture lessons:

```text
question/task specification
-> schema validation
-> source retrieval
-> evidence validation
-> answer/output generation
-> audit log
-> next action recommendation
```

Do not implement autonomous wet-lab execution in V1.
