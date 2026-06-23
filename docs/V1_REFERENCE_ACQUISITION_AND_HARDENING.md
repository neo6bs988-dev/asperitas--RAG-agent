# V1 Reference Acquisition and Hardening Guide

Status: docs-only architecture hardening
Scope: V1 development governance, reference intake, skills/workflow/eval/audit/security planning

## Executive Bottom Line

Asperitas Agent V1 must be developed as source-grounded, auditable, compliance-aware internal AI infrastructure rather than a generic chatbot or unverified research-agent demo.

This guide hardens the post-MVP-015 path by turning the latest user direction into a concrete V1 development policy:

- prioritize official and peer-reviewed reference sources only;
- store reference metadata before any production ingestion;
- separate architecture benchmarking from Asperitas capability claims;
- strengthen the next MVP sequence around Skills, Evaluation, Workflow, Audit, and Security layers;
- preserve all existing retrieval, source-grounding, compliance, and no-overclaim boundaries.

This file does **not** implement ingestion, retrieval changes, vector DB, RAGAS integration, external API integration, or production deployment.

## V1 Architecture Layers

Asperitas Agent V1 is defined as:

```text
Knowledge Layer
+ Skills Layer
+ Workflow Layer
+ Evaluation Layer
+ Audit Layer
+ Security Layer
```

Every new feature must improve at least one layer. Features that do not improve any layer should be rejected, deferred, or reframed.

| Layer | V1 purpose | Allowed near-term work |
| --- | --- | --- |
| Knowledge Layer | Source registry, chunks, metadata, provenance, citation targets | metadata hardening, source-status reporting, reference manifest |
| Skills Layer | Reusable task contracts and tool-independent operating recipes | local skill registry, skill contract, skill validation |
| Workflow Layer | Preflight, plan, approve/block, run/read-only, verify, log, review | non-executing planner/runner flow |
| Evaluation Layer | RAG/retrieval/citation/answer quality measurement | RAGAS-inspired metric map, baseline report, regression gates |
| Audit Layer | JSON/JSONL traceability and decision memory | usage/eval/safety/decision logs |
| Security Layer | Prompt-injection, source poisoning, overclaim, leakage prevention | adversarial fixtures, fail-closed policy tests |

## Knowledge Acquisition Rule

When identifying new reference sources for V1 development, prioritize only:

1. official OpenAI documentation;
2. official Anthropic documentation;
3. official LangGraph documentation;
4. official LlamaIndex documentation;
5. peer-reviewed RAG evaluation papers;
6. official GitHub repositories.

Do not ingest unofficial blogs, social posts, newsletters, YouTube summaries, or derivative summaries into the production knowledge base.

Unofficial material may be used as human brainstorming context only if clearly labeled as non-authoritative and excluded from production source registry ingestion.

## Allowed Reference Metadata Schema

Store only metadata first:

```json
{
  "source_title": "",
  "source_url": "",
  "source_type": "official_docs | peer_reviewed_paper | official_github_repo",
  "publisher_or_org": "",
  "version_or_date": "",
  "retrieved_date": "",
  "summary": "",
  "architecture_principles": [],
  "implementation_patterns": [],
  "provenance_metadata": {
    "authority_level": "official | peer_reviewed | official_repo",
    "license_or_terms_status": "unknown | review_needed | cleared",
    "intended_use": "architecture_reference | evaluation_reference | implementation_reference",
    "production_ingestion_allowed": false,
    "notes": ""
  }
}
```

## Initial V1 Reference Candidates

These are candidate metadata entries only. They are not production-ingested sources.

| Source | Type | V1 pattern to benchmark | Production ingestion status |
| --- | --- | --- | --- |
| OpenAI Structured Outputs / Agents / Codex documentation | official_docs | schema-first outputs, tools, guardrails, agent workflows, Codex worktrees/skills | metadata-only candidate |
| Anthropic Claude Code Skills documentation | official_docs | `SKILL.md` structure, skill descriptions, reusable project recipes, verification skills | metadata-only candidate |
| LangGraph documentation | official_docs | workflow state, human-in-the-loop gates, graph orchestration | metadata-only candidate |
| LlamaIndex documentation | official_docs | context augmentation, data connectors, indexes, retrievers, query/chat engines, observability/evals | metadata-only candidate |
| RAGAS documentation and paper | peer_reviewed_paper / official_docs | context precision/recall, faithfulness, answer relevancy, RAG eval loops | metadata-only candidate |
| Official GitHub repositories | official_github_repo | implementation patterns, licenses, repo structure, tests | metadata-only candidate |

## Benchmarking Interpretation Rules

Use references as architecture benchmarks only.

Do not claim that Asperitas has the same capability as OpenAI, Anthropic, LangGraph, LlamaIndex, RAGAS, Ginkgo, Recursion, or Benchling.

| Reference | Use as | Do not claim |
| --- | --- | --- |
| OpenAI Codex / Agents | structured outputs, agent evals, guardrails, Codex workflow discipline | OpenAI-equivalent agent platform |
| Anthropic Skills / MCP | modular skills, MCP-ready future connector discipline | Anthropic-equivalent tool ecosystem |
| LangGraph | stateful workflow and human approval gate pattern | autonomous workflow execution |
| LlamaIndex | knowledge-layer and context-augmentation architecture | production LlamaIndex deployment |
| RAGAS | systematic RAG evaluation and metric taxonomy | full RAGAS integration until implemented |
| Ginkgo/OpenAI autonomous lab paper | schema validation and workflow-boundary philosophy | autonomous wet-lab or cloud-lab capability |
| Recursion | data flywheel philosophy | proprietary wet-lab data flywheel |
| Benchling | metadata/audit/traceability philosophy | ELN/LIMS-equivalent product |

## MVP-016 to MVP-019 Reframed Priorities

### MVP-016 — Skills Framework

Goal: define a local, testable Skills Framework for reusable Asperitas agent capabilities.

Minimum expected objects:

- `SkillSpec`
- `SkillInputContract`
- `SkillOutputContract`
- `SkillRiskPolicy`
- `SkillVerificationPlan`
- `SkillRegistry`

Required properties:

- JSON-compatible metadata;
- source-grounding policy;
- risk category and approval gates;
- deterministic default behavior;
- no external execution by default;
- no production claims.

### MVP-017 — RAGAS-Inspired Evaluation Layer

Goal: map existing retrieval/eval harness to a RAGAS-inspired evaluation taxonomy without changing default retrieval behavior unless explicitly approved.

Minimum metric map:

- retrieval@k;
- context precision;
- context recall;
- faithfulness / groundedness;
- answer relevancy;
- citation accuracy;
- abstention accuracy;
- unsupported-claim rate;
- regression count.

### MVP-018 — Workflow / Planner Architecture

Goal: connect preflight decisions, skills, and evaluation into a read-only planner state machine.

Minimum states:

```text
request_received
-> source_status_checked
-> skill_selected
-> risk_preflight
-> allowed | blocked | requires_human_approval
-> read_only_plan_generated
-> verification_plan_attached
-> audit_record_written
```

No autonomous execution, external API calls, wet-lab actions, or production deployment.

### MVP-019 — Audit, Security, and V1 Baseline Closeout

Goal: close V1 with structured audit trail, prompt-injection/security fixtures, baseline metrics, limitations, and V1.1 roadmap.

Required closeout sections:

- V1 architecture summary;
- metrics baseline;
- known limitations;
- security tests;
- source-grounding review;
- no-overclaim review;
- deployment-readiness status;
- V1.1 performance-hardening plan.

## Performance Hardening Rule

Any performance improvement must follow:

```text
baseline -> failure taxonomy -> root-cause isolation -> smallest safe change -> focused tests -> eval before/after -> regression protection -> promotion decision
```

No retrieval, chunking, scoring, metadata filtering, embeddings, vector DB, reranking, or answer-generation behavior should change without explicit scope and retrieval eval.

## Hard Constraints

- Preserve `mvp003` as protected deterministic default retriever.
- Keep hybrid explicit/manual/experimental unless eval-proven.
- Keep deterministic-test reranker explicit opt-in/non-default unless eval-proven.
- Do not ingest sources without approval.
- Do not mutate registry/chunks/eval fixtures without explicit scope.
- Do not claim production RAG/KG/eval/deployment unless implemented and verified.
- Do not claim wet-lab validation, autonomous lab capability, legal approval, regulatory approval, customer traction, or production readiness without evidence.
- Escalate CITES, Nagoya, LMO, biosafety, biosecurity, privacy, security, legal, IP, investor, and public-communication risks.

## Verification Policy

For docs-only changes:

```bash
git status --short --branch
git diff --check
```

For source-code changes:

```bash
python -m pytest -q
python scripts/verify_artifacts.py
git diff --check
```

For retrieval/eval behavior changes:

```bash
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5 --json
```

Additional eval commands must be specified by the implementing MVP.

## Definition of Done for This Guide

This guide is complete when it provides a clear, non-executing policy for:

- V1 reference-source acquisition;
- reference metadata schema;
- official-source priority;
- MVP-016 to MVP-019 reframing;
- performance-hardening rule;
- no-overclaim and no-unapproved-ingestion constraints.
