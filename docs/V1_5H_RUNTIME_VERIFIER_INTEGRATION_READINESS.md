# V1.5H Runtime Verifier Integration Readiness

Date: 2026-07-04

Status: readiness review and future integration gate only. This document does not integrate the verifier into runtime RAG, change answer generation, change retrieval, change reranking, change chunking, change metadata handling, change embeddings, change vector database behavior, change the compliance router, change dependencies, change configuration, change CI, or claim production citation accuracy, answer faithfulness, RAG performance, legal approval, regulatory approval, wet-lab validation, autonomous lab capability, production DB/KG/vector DB completion, or foundation model completion.

Baseline: `main` at `384c94e40645bbe6d1bb103ca646ffc2cbc5703b`.

## Objective

V1.5H defines readiness gates for a future, narrowly scoped runtime integration PR that connects the existing claim-to-citation verifier pipeline to the runtime answer flow.

The target future integration is:

```text
runtime answer payload
+ passive verifier metadata
+ diagnostics and trace hooks
```

The target is not:

```text
new answer generation behavior
new retrieval behavior
new compliance routing behavior
automatic answer rewriting
production accuracy claim
```

## Current Implemented Chain

The current verifier chain is already staged:

```text
schema/taxonomy
-> claim extraction
-> evidence-span matching
-> support-status classification
-> report aggregation
-> answer-level verification metadata
-> adversarial/security eval pack
-> biology/compliance golden set
-> metrics/regression gate
```

The runtime readiness decision must preserve those boundaries. A future runtime PR must call these stages explicitly or through narrow adapters that keep each stage observable. It must not collapse extraction, matching, classification, aggregation, and metadata exposure into one broad helper.

## Current Metadata Attachment Point

The existing passive attachment surface is:

```text
GroundedAnswer.to_json()["metadata"]["answer_verification"]
```

The current helper contract is:

```text
expose_answer_verification_metadata(answer, summary, metadata_key="answer_verification")
```

This helper copies an answer payload and adds verifier metadata under the existing `metadata` hook. It must not mutate the input answer, rewrite `answer_text`, change `answer_status`, change `citations_used`, change citation coverage, change guardrail decisions, or change retrieved evidence records.

Future runtime integration should use this hook first. If the runtime surface returns `AgentResponse` or another wrapper, the verifier metadata should remain nested under the answer payload's `metadata.answer_verification` field or be mirrored into the wrapper metadata with the same key only after targeted answer contract tests prove no existing consumer breaks.

## What Runtime Integration Must Not Change Initially

The first runtime integration PR must not change:

- generated answer text;
- answer status values;
- citation rendering or citation keys;
- citation coverage calculations;
- limitations text;
- guardrail or truth/compliance router decisions;
- retrieval mode, top-k defaults, rank scores, reranking, chunking, source metadata, embeddings, vector DB behavior, or evidence selection;
- source registry, raw source files, processed chunks, generated indexes, or eval fixture semantics;
- dependency, config, CI, service, model, tool, or cloud behavior.

The first PR may only attach verifier outputs as passive metadata after the answer is generated and after the existing retrieval, guardrail, answer generation, and truth/compliance router behavior has already completed.

## Expected Failure Behavior

Initial runtime behavior must be metadata-only. The verifier may expose warnings and blocking diagnostics, but it must not rewrite, suppress, or regenerate answer text in the first runtime PR.

| Verifier result | Initial runtime behavior | Required metadata signal |
|---|---|---|
| `unsupported` | Preserve answer text; mark answer-level faithfulness as `fail`; require human review or downstream blocking outside this first PR | `status_counts.unsupported`, `blocking_failures`, `warnings`, claim detail with `failure_mode` |
| `contradicted` | Preserve answer text; mark as severe blocker; require human review before external/public use | `status_counts.contradicted`, `blocking_failures`, `span_signal:contradiction` when available |
| `citation_missing` | Preserve answer text; expose missing-citation blocker; do not invent a citation | `status_counts.citation_missing`, `failure_mode:no_citation` |
| `citation_mismatch` | Preserve answer text; expose wrong-source or wrong-span blocker; do not repair citation automatically | `status_counts.citation_mismatch`, matcher diagnostics such as `unresolved`, `ambiguous`, or `malformed_citation_key` |
| `ambiguous` | Preserve answer text; mark as caution or blocker according to aggregate summary; require clarification or later atomization work | `status_counts.ambiguous`, `failure_mode:verifier_not_applicable` or equivalent |
| `not_verifiable_from_context` | Preserve answer text; mark as missing-evidence condition; do not treat the claim as false or supported | `status_counts.not_verifiable_from_context`, `warnings`, evidence-span diagnostics |
| compliance-sensitive claim | Preserve answer text; surface compliance tags as metadata and warnings only; do not convert tags into legal, regulatory, biosafety, or approval conclusions | `compliance_tags`, `compliance_flag:<tag>`, claim detail compliance metadata |
| `compliance_blocked` | Preserve answer text; expose human-review blocker; do not claim approval or permission | `status_counts.compliance_blocked`, `blocking_failures`, compliance tags when available |

## Answer Text Rewrite Policy

No answer text rewrite is allowed in the first runtime integration PR.

Future rewrite behavior requires a separate scoped PR with:

- explicit rewrite policy;
- answer contract tests;
- unsupported, contradicted, citation-missing, and citation-mismatch fixtures;
- truth/compliance router review;
- human-review policy for compliance-sensitive and public/investor-facing claims;
- before/after examples that do not claim production accuracy improvement;
- rollback plan for disabling rewrite while preserving metadata exposure.

Until then, verifier metadata is diagnostic only. It can inform downstream review, UI warnings, QA gates, or human approval, but it cannot silently alter the model answer.

## Latency And Cost Risk Boundary

Runtime integration must measure overhead before it can become default.

The future PR must report:

- verifier stage timings when available;
- total added runtime or a clear `Not Measured` label;
- token/cost proxy only if model calls are introduced in a later approved PR;
- timeout/fail-closed policy;
- max answer size or claim count boundary if needed;
- behavior when verifier execution fails.

Initial policy:

- do not add external model calls;
- do not add network calls;
- do not add background services;
- do not add dependencies;
- do not block existing local answer generation on an unbounded verifier run;
- do not claim latency improvement, cost improvement, citation accuracy improvement, answer faithfulness improvement, or RAG performance improvement.

## Failure And Fallback Policy

If the verifier cannot run, the runtime answer should remain available with explicit metadata indicating that verification was not completed, provided the existing guardrail and compliance router already allowed the answer.

Required fallback metadata:

```json
{
  "answer_verification": {
    "answer_faithfulness_status": "not_scored",
    "warnings": ["runtime_verifier_not_completed"],
    "diagnostics": ["metadata_only_runtime_integration_fallback"]
  }
}
```

The fallback must not upgrade the answer to supported. Missing verifier output is not evidence of answer faithfulness.

## Human Review And Blocking Diagnostics

The initial runtime PR should expose blockers, not autonomously adjudicate external use.

Human review is required before external, public, investor-facing, legal, regulatory, biosafety, wet-lab, or compliance-sensitive use when metadata includes:

- any `blocking_failures`;
- `answer_faithfulness_status: fail`;
- any `contradicted` claim;
- any `citation_mismatch` claim;
- any `citation_missing` material claim;
- any `compliance_blocked` claim;
- compliance tags for CITES, Nagoya/ABS, LMO/GMO, biosafety, biosecurity/export-sensitive biology, IP/license, human/clinical sensitivity, public/investor claims, production status, approval status, validation status, autonomous lab status, or foundation model completion.

The first runtime PR should not add autonomous external actions or tool execution based on these diagnostics.

## Compliance Tag Behavior

Compliance tags are metadata and warnings only.

Compliance tags must not mean:

- legal approval;
- regulatory approval;
- biosafety approval;
- source-country permission;
- freedom to operate;
- public communication approval;
- investor communication approval;
- wet-lab validation;
- permission to execute biological protocols.

Compliance tags should help route human review and preserve auditability. They must not weaken or replace the truth/compliance router.

## Tracing And Observability Boundary

The future runtime PR may add trace metadata, but it must not add Agents SDK, LangGraph, CrewAI, AutoGen, MCP automation, multi-agent orchestration, or new tracing services.

### Workflow Name

Recommended `workflow_name`:

```text
v1_5h_runtime_verifier_metadata_exposure
```

If the future PR is metadata-only, the workflow name must make that explicit. Do not use names that imply production verification completion.

### Group ID Strategy

Recommended `group_id`:

```text
answer_id:<answer_id>
```

Fallback when `answer_id` is unavailable:

```text
query_hash:<stable_query_hash>
```

The group ID should link retrieval, answer generation, verifier stages, and metadata exposure for one answer attempt. It must not contain raw confidential source text, secrets, credentials, or sensitive biological material.

### Trace Metadata

Allowed trace metadata:

- `workflow_name`;
- `group_id`;
- `answer_id`;
- verifier schema/version names;
- claim count and status counts;
- citation keys;
- evidence span IDs;
- source IDs;
- failure modes;
- compliance tags;
- deterministic flag;
- elapsed time per verifier stage when measured;
- warnings and diagnostics after redaction.

Disallowed trace metadata:

- raw secrets, credentials, tokens, API keys, private keys, or passwords;
- raw confidential source text;
- sensitive biological operational instructions;
- legal or regulatory conclusions not supported by approved review;
- production-readiness claims.

### Expected Spans

Future runtime tracing should preserve separate spans or audit events for:

1. retrieval and evidence packaging;
2. answer generation;
3. truth/compliance routing when present;
4. claim extraction;
5. evidence-span matching;
6. support-status classification;
7. report aggregation;
8. answer verification metadata exposure;
9. runtime fallback if verifier metadata cannot be produced.

These spans should carry IDs and counts, not raw sensitive text, unless a later approved audit policy explicitly allows bounded excerpts.

## Required Eval Gates Before Runtime Merge

A future runtime integration PR must pass or explicitly justify skipped gates:

| Gate | Required evidence before merge |
|---|---|
| Adversarial/security pack | Targeted tests covering prompt injection as data, malicious citation keys, wrong citation, unsupported, contradicted, not-verifiable, metadata JSON safety, and no input mutation |
| Biology/compliance golden set | Targeted tests preserving biology entities, compliance tags as metadata/warnings only, fixture provenance, and deterministic serialization |
| Metrics/regression gate | Targeted metrics test showing status counts, diagnostics, compliance/license tag counts, provenance coverage, JSON safety, deterministic ordering, and runtime-bounded imports |
| Targeted answer contract tests | Tests proving answer text, answer status, citations, citation coverage, limitations, guardrail summary, and existing metadata remain unchanged except for `metadata.answer_verification` |
| Runtime surface sanity | Static/diff review proving no runtime RAG, retrieval, reranking, chunking, embedding, vector DB, answer generation, compliance router, dependency, config, or CI changes slipped in |
| Truth-boundary scan | Review proving the PR claims metadata readiness only, not production verifier completion or metric improvement |

Retrieval eval is required only if retrieval, evidence selection, chunking, metadata filtering, embeddings, vector DB behavior, reranking, answer generation, or eval semantics change. Those changes are out of scope for the first runtime metadata PR.

## Rollback Plan

The first runtime integration must be easy to disable.

Required rollback properties:

- verifier metadata attachment is isolated behind a narrow call site;
- disabling the call returns the previous answer payload shape, except for the absence of `metadata.answer_verification`;
- no persisted source registry, chunk, index, vector DB, KG, or eval artifact is modified;
- no dependency/config/CI rollback is needed;
- fallback status uses `not_scored`, not `pass`;
- rollback does not alter truth/compliance router behavior.

## Runtime Surface Review Checklist

Before opening the future runtime PR:

- identify the exact runtime answer object or mapping receiving metadata;
- prove `answer_text` is unchanged;
- prove `citations_used` is unchanged;
- prove `answer_status` is unchanged;
- prove `metadata.answer_verification` is the only intended payload addition;
- prove retrieval modules are not changed;
- prove answer generation modules are not changed, except a narrow post-generation metadata attachment if explicitly scoped;
- prove compliance router modules are not changed;
- prove dependency/config/CI files are not changed;
- prove no new service, framework, model call, or tool automation is added.

## Truth Boundary Constraints

This document defines readiness gates only.

Do not claim:

- production verifier completion;
- citation accuracy improvement;
- answer faithfulness improvement;
- RAG performance improvement;
- production database, KG, or vector DB completion;
- wet-lab validation;
- legal or regulatory approval;
- autonomous lab capability;
- foundation model completion.

Permitted claim:

```text
V1.5H defines metadata-only readiness gates for a future scoped runtime verifier integration PR.
```

## Acceptance Criteria

This readiness review is acceptable when:

- the future attachment surface is identified as `metadata.answer_verification`;
- initial integration is metadata-only;
- answer text rewrite is explicitly out of scope;
- runtime behavior that must not change is listed;
- support-status failure behavior is defined;
- compliance tags remain metadata and warnings only;
- latency/cost boundaries are defined without performance claims;
- human-review and blocking diagnostic policy is explicit;
- tracing and observability fields are scoped without new frameworks or services;
- required eval gates are listed before runtime merge;
- rollback behavior is narrow and reversible;
- truth-boundary constraints are explicit.

## Recommended Next Step

After this readiness review is merged, open one future scoped runtime PR that attaches `metadata.answer_verification` to the runtime answer payload after answer generation. That future PR should include targeted answer contract tests and run the adversarial/security, biology/compliance golden set, and metrics/regression gates before merge.
