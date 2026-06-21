# MVP-014 Agent Role Registry

## Objective

MVP-014 Phase 1 adds a deterministic local role-contract registry for future Asperitas agents.
The registry defines role boundaries, allowed tasks, prohibited tasks, required inputs,
required outputs, retrieval policy, evidence policy, compliance policy, escalation triggers,
validation gates, output contracts, and risk notes.

## Scope

This phase is role contracts only. It provides a local Python registry module that can be
imported by future tools, tests, and agent orchestration work.

The implementation is deterministic and local-only:

- no file I/O is required by the registry;
- no network calls are made;
- no external API or LLM dependency is added;
- no retrieval ranking behavior changes;
- no agent runtime routing behavior changes.

## Non-Goals

MVP-014 Phase 1 does not implement:

- autonomous agent execution;
- runtime agent routing;
- UI or web server behavior;
- answer generation changes;
- retrieval ranking changes;
- ingestion;
- chunk, source registry, or eval fixture mutation;
- external APIs, model services, cloud resources, generated indexes, or vector DB changes;
- production hybrid or reranker claims.

## Role Schema

Each role contract includes:

- `role_id`
- `display_name`
- `mission`
- `allowed_tasks`
- `prohibited_tasks`
- `required_inputs`
- `required_outputs`
- `default_retriever`
- `allowed_retrievers`
- `source_policy`
- `evidence_policy`
- `compliance_policy`
- `escalation_triggers`
- `validation_gates`
- `output_contract`
- `risk_notes`

List-like fields are immutable tuples in Python and serialize to lists for deterministic JSON-ready output.

## Initial Role List

MVP-014 Phase 1 defines exactly ten role contracts:

1. `literature_intelligence_agent`
2. `experiment_design_agent`
3. `compliance_gatekeeper_agent`
4. `dbtl_planner_agent`
5. `market_intelligence_agent`
6. `ir_grant_agent`
7. `biofoundry_workflow_agent`
8. `technical_skeptic_agent`
9. `operations_optimizer_agent`
10. `digital_devil_advocate_agent`

## Retrieval Policy Boundary

The registry preserves the existing retrieval policy:

- default retriever: `mvp003`;
- allowed explicit retrievers: `baseline`, `mvp003`, `vector`, `hybrid`;
- `hybrid` is manual diagnostic only, non-default, and not a production-quality claim;
- no automatic hybrid promotion is allowed;
- no retrieval ranking behavior is changed by the role registry.

## Hybrid / Reranker Boundary

The registry records these policy constants:

- `manual_diagnostic_only_non_default_no_production_claim`
- `deterministic_test_reranker_explicit_opt_in_only_non_default`

The deterministic-test reranker remains explicit, opt-in, and non-default. MVP-014 Phase 1 does
not make reranking part of default agent behavior.

## Compliance And Human Approval Gates

High-risk roles are:

- `experiment_design_agent`
- `dbtl_planner_agent`
- `biofoundry_workflow_agent`
- `compliance_gatekeeper_agent`

These roles include explicit human approval gates for:

- biosafety-sensitive outputs;
- regulatory/CITES/Nagoya/LMO claims;
- legal/IP claims;
- investor-facing claims;
- wet-lab protocol execution;
- confidential/internal source sharing;
- unsupported production-quality claims.

The registry is a policy scaffold and does not provide legal, regulatory, biosafety, or wet-lab approval.

## Evidence / Source Policy

Role contracts require source-grounded behavior:

- preserve source ID, source priority, disclosure level, evidence label, and verification status;
- separate document-supported facts from inference, speculation, and needs-external-verification claims;
- avoid using restricted internal sources for external outputs without approval;
- abstain or escalate when evidence is insufficient for the requested claim.

## Validation Commands

Run:

```powershell
python -m pytest -q tests/test_role_registry.py
python -m pytest -q
python scripts/verify_artifacts.py
python scripts/evaluate_agent.py
python scripts/run_golden_agent_eval.py
git status --short
```

## Risks And Mitigations

| Risk | Mitigation |
|---|---|
| Role contracts are mistaken for autonomous agents | Document contracts-only scope and avoid runtime routing changes |
| Hybrid is interpreted as production retrieval | Keep `mvp003` as default and test that `hybrid` is never default |
| Reranker becomes implicit | Keep deterministic-test reranker explicit opt-in only |
| High-risk biology roles are too permissive | Require human approval gates for wet-lab, biosafety, regulatory, legal/IP, investor, confidential-sharing, and production-quality claims |
| Overclaiming agent readiness | State that this phase does not provide production autonomy, wet-lab validation, legal approval, or regulatory approval |

## Future MVP Handoff

Future work may connect role contracts to an agent router or workflow runner only after separate approval.
The next phase should decide whether role contracts remain static policy data or become selectable runtime
constraints for `ask_agent.py` and future agent interfaces.
