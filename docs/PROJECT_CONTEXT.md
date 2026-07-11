# Project Context

## Current Execution Authority (2026-07-11)

Use [`docs/CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md`](docs/CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md) as the authoritative current-status and forward-performance control plane. For files already inside `docs/`, the path refers to `CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md` in the same directory.

Latest confirmed baseline before this documentation sync:

- `main`: `1e437c4515cc664f6acdb6e5bb197aaf576d34af`;
- PR #166 guard hardening: merged after CI #250 and Quality Gates #381 succeeded;
- V1.10B diagnostic answer-sample reporting: merged;
- V1.10C preflight: merged;
- V1.10C six-file implementation: preserved locally and pending publication; not on `main`.

If an older status table or “next step” conflicts with the current-state roadmap, treat the older status wording as historical. Preserve its technical contracts and acceptance criteria. Do not treat doctrine, plans, scaffolds, synthetic fixtures, or diagnostic reports as proof of runtime quality, production readiness, compliance approval, biological validation, vector DB/KG completion, or foundation-model capability.

Current mandatory sequence:

```text
V1.10C publication
-> V1.10 closure
-> representative biology/compliance eval reset
-> retrieval and reranker hardening
-> real grounded answer path and diagnostic verifier
-> compliance/security adversarial gates
-> trace, latency, token, and cost control plane
-> internal dogfood
-> approved data flywheel
-> web productization and production-readiness gates
```


Asperitas is building a source-grounded biological intelligence system that starts as an internal RAG/agent control plane and must ultimately become a web-productized, commercially deployable AI platform.

The active GitHub repository is `neo6bs988-dev/asperitas--RAG-agent`.

## Top Source Triad Baseline

Future development should use the latest Top Source Triad as the default operating baseline:

1. `ASPERITAS_PROJECT_SOURCE_CONSTITUTION_v11_0_KR.pdf` — project-level source constitution and router.
2. `Asperitas_AI_Lead_Expert_GPT_Training_Source_v1_0_KR.pdf` — AI Lead/CTO behavior, architecture ladder, RAG/KG/eval/control-plane doctrine.
3. `딥리서치를 통해 GPT 채팅 학습용 자료.pdf` — Deep Research, external benchmark, ML/DL/LLM routing, agent development, eval/tracing/guardrail doctrine.

These sources are operating doctrine. They are not evidence that production vector DB, production RAG, KG, eval suite, legal review, wet-lab validation, regulatory approval, autonomous lab execution, or foundation-model capability is complete.

## Current Repository Stage

The repository remains in a staged internal-development path. MVP-004 through MVP-010 build the internal RAG/agent foundation. MVP-011 through MVP-013 convert that internal system into a web-productization pathway.

## Completed Baseline Milestones

- MVP-001 Foundation.
- MVP-002 Retrieval structure.
- MVP-002.5 Evaluation baseline.
- MVP-003 Metadata-aware retrieval.

## Active Technical Focus

- MVP-004 Structure-aware chunking closure.
- MVP-005 Embeddings + Vector DB planning after MVP-004 quality gate evidence.
- V1.5/V1.6 performance hardening, claim-to-citation verifier, and security/adversarial eval readiness.

## Commercialization Direction

The final goal is not only a local/internal RAG tool. The intended progression is:

```text
internal source-grounded RAG core
-> verifier/compliance/eval hardening
-> internal API/UI
-> web productization foundation
-> authenticated web app MVP
-> production readiness gate
-> commercial AI product pathway
```

## Next Work

- Preserve Top Source Triad alignment in README, AGENTS, roadmap, and Codex prompts.
- Close MVP-004 only with recorded gate evidence.
- Keep deterministic retrieval and metadata-preservation baselines comparable while adding vector/hybrid/reranker layers.
- Add source-grounded answer generation only after retrieval/evidence packaging is reliable.
- Add compliance guardrails before public or investor-facing outputs.
- Add backend API, LLM adapter, auth, observability, deployment, cost/latency gates, and user-role boundaries before web-product claims.
