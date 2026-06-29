# V1.5 Performance Roadmap

This document defines the next operating stage after V1.4 optimization closeout. It is a planning and governance document. It does not claim implementation of production vector DB, KG, full source ingestion, legal approval, wet-lab validation, deployed autonomy, or a biological foundation model.

## Executive Bottom Line

V1.5 is the gap-closure and performance-hardening phase. The goal is to turn the V1.3/V1.4 RAG agent core into a stronger platform base before expanding into modular agents, vector DB/KG, ML/DL, or foundation-model-readiness work.

Default priority:

```text
Stabilize core -> prove with evals -> then modularize agents -> then add ML/DL optimization -> then foundation-model readiness
```

## V1.5 Objectives

1. Lock the V1.4 truth, retrieval, answer, compliance, and token-efficiency gains into repo docs, PR templates, and quality gates.
2. Close known documentation and operating gaps before new feature expansion.
3. Prepare claim-to-citation verification and adversarial evals.
4. Improve retrieval, answer, confidence, and compliance metrics without weakening source boundaries.
5. Define biology-specific golden tasks for DBTL, compliance, pathway/protein, IP, and biodiversity sourcing.
6. Keep GitHub as the execution source of truth.

## Current Known Gaps

| Gap | Why It Matters | V1.5 Action |
|---|---|---|
| Docs drift from current stage | Codex may follow stale MVP-004/MVP-005 wording | Sync README, AGENTS, workflow, quality gates, source policy, PR template |
| Claim-to-citation validation incomplete | Citations can look grounded without supporting exact claims | Design and implement atomic claim verifier |
| Adversarial/security eval coverage incomplete | Prompt injection, source poisoning, leakage, and excessive agency remain risk surfaces | Add adversarial eval pack |
| Biology-specific golden set incomplete | Generic RAG evals do not prove Asperitas decision quality | Add Nagoya/CITES/LMO/DBTL/pathway/IP tasks |
| Latency win unproven | Cache hits alone are not speed improvement | Measure p50/p95 and optimize real bottlenecks |
| Modular agent split not ready until shared core is stable | Premature agent split creates complex chatbots, not infrastructure | Require shared RAG core, evals, and compliance gates before expansion |

## Performance Gates

| Dimension | Required Evidence |
|---|---|
| Retrieval quality | Recall@k, Precision@k, MRR/nDCG when available, expected-source hit rate, source coverage |
| Answer quality | faithfulness, answer relevance, unsupported-claim rate, missing-evidence honesty |
| Citation quality | claim-to-source support, contradicted/unsupported claim detection, citation precision |
| Compliance safety | refusal/escalation accuracy, biosafety/legal/investor/public-claim risk detection |
| Security | prompt injection, malicious retrieved-document, source poisoning, PII/confidential leakage checks |
| Efficiency | retrieved-context tokens, answer tokens, cost proxy, p50/p95 latency, net runtime |
| Biology-specific usefulness | DBTL plan quality, mechanism boundary, validation-status honesty, IP/compliance boundary accuracy |

## Non-Negotiable Preservation During Optimization

Any optimization must preserve:

- source IDs;
- source paths/provenance;
- source priority;
- citation anchors;
- evidence labels;
- section metadata;
- registry keys;
- verification commands;
- truth-boundary fields;
- compliance constraints;
- negative scope.

Token reduction must remove useless context, not reasoning quality or critical evidence.

## V1.5 Work Packages

### V1.5A Documentation And Gate Sync

Scope:

- README;
- AGENTS;
- AI Development OS;
- Workflow;
- Quality Gates;
- Source Policy;
- PR template;
- this roadmap.

Gate:

- docs fetch/read sanity;
- no false production-status claim;
- no source code behavior change;
- PR merged to main.

### V1.5B Claim-To-Citation Verifier Design

Scope:

- define atomic claim schema;
- define support grades: supported, unsupported, contradicted, too vague, needs verification;
- define evidence span attachment;
- define output metrics.

Gate:

- design doc;
- test fixture plan;
- no answer behavior change until implementation PR.

### V1.5C Claim-To-Citation Verifier Implementation

Scope:

- implement deterministic or semi-deterministic verifier harness;
- add tests;
- integrate with answer contract checks.

Gate:

- targeted tests;
- answer contract checks;
- sample golden tasks.

### V1.5D Adversarial Eval Pack

Scope:

- prompt injection;
- malicious retrieved-document instructions;
- source poisoning;
- confidential/PII leakage;
- excessive agency;
- biosafety over-answer;
- public/investor overclaim.

Gate:

- adversarial fixtures;
- refusal/escalation metrics;
- no unsafe output path.

### V1.5E Biology-Specific Golden Set

Scope:

- biodiversity sourcing;
- CITES/Nagoya/LMO;
- DBTL design;
- pathway/protein hypothesis boundary;
- natural product/IP boundary;
- grant/regulatory interpretation.

Gate:

- source-backed tasks;
- expected evidence/source oracle;
- truth-boundary expectations.

### V1.5F Real Latency And Cost Optimization

Scope:

- measure p50/p95;
- profile retrieval/scoring bottlenecks;
- evaluate top-k, reranker, index, and parallel scoring options.

Gate:

- before/after runtime evidence;
- no retrieval/answer quality regression;
- no false cache-win claim.

## Later Phases

| Phase | Focus | Entry Gate |
|---|---|---|
| V2 | Vector DB/KG production pathway | approved ingestion, embeddings/index logs, KG link strategy, eval-ready evidence |
| V3 | Modular agent pack | stable shared RAG core, source registry, answer contract, compliance gate, eval suite |
| V4 | ML/DL optimization layer | enough labeled/golden data, benchmark evidence, safety and license review |
| V5 | Foundation-model readiness | proprietary, validated, metadata-rich biological data plus repeatable DBTL feedback loops |

## Default V1.5 Codex Prompt Contract

Every V1.5 Codex prompt should include:

```text
Reasoning Strength: Very High
Goal:
Scope:
Out of Scope:
Files to Read First:
Hard Constraints:
Validation:
Acceptance Criteria:
Truth Boundary:
Stop Conditions:
Final Report Format:
```

Do not let prompts become long because they are noisy. Keep them compact while preserving constraints, validation, source IDs, version/status numbers, and stop rules.
