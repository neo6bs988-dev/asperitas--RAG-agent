# Ideal Repository Structure v11.1

## Executive Bottom Line

The ideal Asperitas repo is not a prompt warehouse. It is a technical memory and control plane for source-grounded biological intelligence infrastructure.

The repo should make five states impossible to confuse:

```text
source candidate != approved source
approved source != ingested production index
eval plan != passing eval suite
agent scaffold != deployed agent
foundation-model roadmap != foundation-model capability
```

## Target Directory Architecture

```text
.
├── README.md
├── AGENTS.md
├── SECURITY.md
├── docs/
│   ├── PROJECT_CONTEXT.md
│   ├── ROADMAP.md
│   ├── MVP_COMPLETION_MASTER_PLAN.md
│   ├── TOP_SOURCE_TRIAD_OPERATING_BASELINE.md
│   ├── V11_1_SUPERGAP_AGENT_BUILD_LEADER.md
│   ├── IDEAL_REPO_STRUCTURE_V11_1.md
│   ├── AI_DEVELOPMENT_OS.md
│   ├── WORKFLOW.md
│   ├── QUALITY_GATES.md
│   ├── AOS_SOURCE_POLICY.md
│   ├── WEB_PRODUCTIZATION_ROADMAP.md
│   └── ops/
├── 01_RAW_SOURCES/
│   ├── P0_ACTIVE_CONSTITUTION/
│   ├── P1_INTERNAL_COMPANY/
│   ├── P2_PUBLIC_POSITIONING/
│   ├── P3_SCIENCE_LITERATURE/
│   ├── P4_REGULATORY_GOVERNMENT/
│   ├── P5_MARKET_INDUSTRY/
│   └── P6_BENCHMARK_DOCTRINE/
├── 02_SOURCE_REGISTRY/
│   ├── source_registry.csv
│   ├── source_registry.schema.json
│   ├── license_confidentiality_review.md
│   └── registry_decisions/
├── 03_PROCESSED_KB/
│   ├── markdown/
│   ├── chunks/
│   ├── redacted/
│   └── manifests/
├── 04_RETRIEVAL_CORE/
│   ├── retrievers/
│   ├── rerankers/
│   ├── citation_packagers/
│   └── query_fixtures/
├── 05_ANSWER_CONTRACT/
│   ├── schemas/
│   ├── claim_verifier/
│   ├── compliance_router/
│   └── report_aggregation/
├── 06_AGENTS/
│   ├── shared_core/
│   ├── literature_agent/
│   ├── benchmark_agent/
│   ├── compliance_biosafety_agent/
│   ├── dbtl_planner/
│   └── investor_ir_agent/
├── 07_EVALS/
│   ├── retrieval/
│   ├── citation_fidelity/
│   ├── answer_contract/
│   ├── adversarial_security/
│   ├── biology_compliance_golden_set/
│   └── regression_reports/
├── 08_WORKFLOWS/
│   ├── deep_research_to_registry/
│   ├── source_ingestion_review/
│   ├── claim_audit/
│   ├── productization_readiness/
│   └── human_approval_gates/
├── 09_TRACES_LOGS/
│   ├── decision_logs/
│   ├── eval_runs/
│   ├── workflow_traces/
│   └── release_evidence/
├── src/
├── tests/
└── .github/
    ├── workflows/
    ├── ISSUE_TEMPLATE/
    └── PULL_REQUEST_TEMPLATE.md
```

## Repository State Policy

| Area | Allowed now | Not allowed to claim until verified |
|---|---|---|
| `docs/` | Operating doctrine, roadmaps, prompts, runbooks | Product shipped or production system complete |
| `01_RAW_SOURCES/` | Classified source candidates and approved source copies | Licensed ingestion complete |
| `02_SOURCE_REGISTRY/` | Registry schema and source status records | Legal review complete unless recorded |
| `03_PROCESSED_KB/` | Extracted/redacted/chunked artifacts | Production vector DB complete |
| `04_RETRIEVAL_CORE/` | Retrieval/rerank/citation code and fixtures | Production RAG quality without evals |
| `05_ANSWER_CONTRACT/` | Claim/citation/compliance schemas and verifier | Full hallucination elimination |
| `06_AGENTS/` | Scoped agent contracts and safe harnesses | Autonomous lab or commercial agent deployment |
| `07_EVALS/` | Offline evals, golden sets, regression outputs | Passing eval suite without run artifacts |
| `08_WORKFLOWS/` | Fixed/stateful workflow definitions | Unbounded autonomous execution |
| `09_TRACES_LOGS/` | Decision, eval, and workflow evidence | Production observability without trace coverage |

## MVP-Gated Upgrade Path

### Phase A — Governance Alignment

- `README.md` and `AGENTS.md` reflect v11.1 doctrine.
- `docs/V11_1_SUPERGAP_AGENT_BUILD_LEADER.md` exists.
- PR template requires `Codex reasoning level` and truth-boundary check.

### Phase B — Registry Hardening

- `source_registry.schema.json` includes source priority, license status, confidentiality, collection status, verification status, owner, updated date, allowed use, compliance tags.
- No unapproved source can enter retrieval fixtures.

### Phase C — Retrieval and Citation Fidelity

- Retrieval eval fixtures define expected source, section, evidence span, and failure mode.
- Citation mismatch and unsupported claim tests exist.

### Phase D — Answer Contract and Compliance Router

- Answer schema captures claim, evidence, confidence, source, uncertainty, compliance tags, and human approval triggers.
- CITES/Nagoya/LMO/biosafety/IP/privacy scenarios route to safe refusal/escalation.

### Phase E — Trace/Eval Control Plane

- Every RAG/agent workflow records run ID, model/tool calls, latency, token/cost metadata, guardrail result, eval outcome, and decision log pointer.

### Phase F — Modular Agents

- Only after shared core stability, add agent modules with explicit specialist contracts.
- No module bypasses retrieval, answer contract, compliance router, or eval hooks.

### Phase G — Web Productization

- Internal RAG app first.
- External/web product only after approved source boundary, secrets policy, abuse prevention, logging, user-data policy, and legal review.

### Phase H — Foundation-Model Readiness

- Requires proprietary, validated, diverse, metadata-rich biological data; DBTL learning records; dataset versioning; benchmark tasks; model/data governance.
- Until then, say `foundation-model-readiness roadmap`, not `foundation model built`.

## File Placement Rules

| Source type | Folder | Gate before ingestion |
|---|---|---|
| AOS / PRIME / project constitution | `01_RAW_SOURCES/P0_ACTIVE_CONSTITUTION/` | Confidentiality and version status |
| Company intro / IR / internal strategy | `01_RAW_SOURCES/P1_INTERNAL_COMPANY/` | Disclosure classification |
| Website / public positioning | `01_RAW_SOURCES/P2_PUBLIC_POSITIONING/` | Official source confirmation |
| Papers / patents / datasets | `01_RAW_SOURCES/P3_SCIENCE_LITERATURE/` | License, citation, reproducibility notes |
| Laws / grants / government docs | `01_RAW_SOURCES/P4_REGULATORY_GOVERNMENT/` | Jurisdiction, date, authority check |
| Market / conference / industry signals | `01_RAW_SOURCES/P5_MARKET_INDUSTRY/` | Source credibility and freshness check |
| OpenAI / Anthropic / LangGraph / benchmarks | `01_RAW_SOURCES/P6_BENCHMARK_DOCTRINE/` | Treat as operating analogy, not internal fact |

## PR Sizing Rule

A PR should touch one of these surfaces unless explicitly approved:

```text
docs/governance
registry/schema
ingestion/chunking
retrieval/rerank
answer contract/verifier
compliance/security
evals/golden sets
tracing/logging
agent contract
workflow/API/UI
```

Do not mix runtime behavior, eval thresholds, source ingestion, and productization claims in one PR unless it is a release-gate PR.

## Recommended Next Technical PRs

1. Add or harden `source_registry.schema.json` with v11.1 fields.
2. Add PR template fields for Codex reasoning level, source status, compliance review, and production-status boundary.
3. Add Deep Research -> Registry workflow skeleton.
4. Add citation-fidelity eval fixture format.
5. Add compliance-router golden cases for CITES/Nagoya/LMO/IP/privacy/public-claim escalation.

## Stop Rule

Do not move from docs/governance into runtime, ingestion, vector DB, KG, external product, or autonomous agent work until the PR has a separate scope lock and the relevant test/eval/approval gates are defined.
