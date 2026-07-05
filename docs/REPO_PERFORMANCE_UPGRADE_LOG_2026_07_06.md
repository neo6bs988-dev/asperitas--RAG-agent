# Repo Performance Upgrade Log — 2026-07-06

## Executive Bottom Line

This update improves repository-level development performance, not runtime RAG speed. The goal is to reduce future execution drift by synchronizing source baseline, roadmap, Codex prompt, web-productization path, and truth boundaries.

## Scope

Changed surface: documentation and governance only.

Out of scope:

- runtime code changes;
- retrieval scoring changes;
- embedding/vector DB implementation;
- hosted backend/API implementation;
- web UI implementation;
- production deployment;
- legal/compliance approval;
- wet-lab validation.

## Performance Improvement Target

| Performance dimension | Upgrade |
|---|---|
| Context precision | Top Source Triad made explicit as baseline |
| Codex execution clarity | Next Codex prompt added with reasoning level and stop rule |
| Roadmap clarity | MVP-011 to MVP-013 web-productization stages added |
| Non-overclaim safety | Production and commercial readiness boundaries restated |
| Tooling leverage | GitHub remains execution evidence; ChatGPT/Codex roles separated |
| Commercialization alignment | Internal RAG path now explicitly leads to web productization gates |

## Source-Grounded Development Control Plane

The proprietary Asperitas layer is not the external LLM. It is the control plane around the model:

```text
approved source registry
-> license/confidentiality pass
-> ingestion/chunking/metadata
-> retrieval/reranking
-> grounded answer contract
-> claim-to-citation verifier
-> compliance/biosafety/IP gate
-> audit trace/failure log
-> eval regression loop
-> DBTL/product/IP decision workflow
```

## Risk Review

| Risk | Control |
|---|---|
| Treating docs as implementation | Non-confusion rules repeated in context/roadmap/productization docs |
| Starting web product too early | MVP-011 blocked until MVP-010 internal UI/API evidence exists |
| LLM provider lock-in | Provider adapter and replaceability required |
| Commercial overclaim | MVP-013 production readiness gate added |
| Agent theater | Architecture ladder and minimal-sufficient implementation preserved |

## Verification

GitHub contents API wrote the docs to a feature branch. No runtime tests were run because this is documentation/governance work only.

Required next-best checks after checkout:

```bash
git diff --check
git status --short
```

Recommended review files:

```text
docs/PROJECT_CONTEXT.md
docs/TOP_SOURCE_TRIAD_OPERATING_BASELINE.md
docs/WEB_PRODUCTIZATION_ROADMAP.md
docs/CODEX_NEXT_PROMPT_WEB_PRODUCTIZATION.md
docs/ROADMAP.md
docs/MVP_COMPLETION_MASTER_PLAN.md
docs/AI_DEVELOPMENT_OS.md
docs/V1_INTERNAL_DEPLOY_GUIDE.md
```

## Next Action

Open/review the PR, then decide whether to merge this docs/governance sync. After merge, the next technical task remains MVP-004 closure unless the user explicitly authorizes a separate web-productization implementation scope.
