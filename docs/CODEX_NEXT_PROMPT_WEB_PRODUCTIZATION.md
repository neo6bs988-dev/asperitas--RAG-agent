# Codex Next Prompt — Top Source Triad + Web Productization Sync

## Codex Reasoning Level

매우높음

## Role

You are the implementation agent for `neo6bs988-dev/asperitas--RAG-agent`. Build source-grounded, auditable, compliance-aware AI infrastructure for Asperitas, using the Top Source Triad as the active development baseline.

## Top Source Triad

Use these as operating doctrine, not implementation proof:

1. `ASPERITAS_PROJECT_SOURCE_CONSTITUTION_v11_0_KR.pdf`
2. `Asperitas_AI_Lead_Expert_GPT_Training_Source_v1_0_KR.pdf`
3. `딥리서치를 통해 GPT 채팅 학습용 자료.pdf`

Do not claim production RAG, vector DB, KG, eval suite, legal review, wet-lab validation, autonomous lab execution, or foundation-model capability exists unless repo evidence proves it.

## Goal

Synchronize the repository so the remaining development path clearly moves from internal source-grounded RAG/agent infrastructure to web-productized commercial AI product readiness.

## Success Criteria

- README/AGENTS/roadmap/context documents point to the Top Source Triad baseline.
- MVP-011 to MVP-013 web productization phases are represented without implying implementation completion.
- The LLM-provider role is separated from Asperitas proprietary control plane.
- The roadmap preserves the internal-first build order: source registry -> retrieval/eval -> grounded answer -> verifier -> compliance -> internal UI/API -> web productization.
- The final report includes changed files, verification, skipped checks, residual risk, and next implementation step.

## Constraints

- Do not edit runtime code unless explicitly asked.
- Do not add dependencies, services, cloud resources, API keys, or deployment config.
- Do not claim tests passed unless actually run.
- Preserve truth boundary and non-overclaim rules.
- Keep PR scope docs/governance only unless the user explicitly requests implementation.

## Development Loop

```text
Scope Lock
-> Source & Risk Preflight
-> Contract Design
-> Minimal Implementation
-> Eval Harness
-> Dry Run & Regression
-> Human Gate
-> Merge & Evidence Log
-> Learn Back
```

## Required Checks For Docs-Only Work

Run or perform the closest available equivalent:

```bash
git diff --check
git status --short
```

Then manually inspect changed Markdown headings, links, and truth-boundary statements.

## Required Output

```text
Changed files:
Verification:
Retrieval metrics:
Compliance/source-grounding review:
Web-productization impact:
Risks or skipped checks:
Recommended next step:
PROMPT_EVOLUTION:
  prompt_version:
  reasoning_strength_used:
  expected_improvement:
  metrics_to_watch:
  failure_taxonomy_updates:
  workflow_complexity_preserved:
  security_risks_checked:
  next_prompt_delta:
```

## Stop Rule

Stop after docs/governance sync and PR creation. Do not proceed to backend/API/web implementation without a separate user-approved scope lock.
