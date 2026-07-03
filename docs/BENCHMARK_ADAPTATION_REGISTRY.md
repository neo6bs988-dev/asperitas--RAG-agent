# Benchmark Adaptation Registry

This registry converts external AI-company and open-source workflow signals into Asperitas-specific engineering controls. It is a P6 benchmark doctrine document, not evidence that Asperitas has already implemented the referenced external capabilities.

## Truth Boundary

Use this document to improve prompts, PR scopes, docs, tests, eval fixtures, security gates, and verifier roadmap planning.

Do not use it to claim:

- production DB, KG, vector DB, autonomous lab, or wet-lab validation
- legal, regulatory, biosafety, CITES, Nagoya/ABS, LMO/GMO, IP, or clinical approval
- foundation model completion
- RAG performance, citation accuracy, answer faithfulness, or biology intelligence improvement without repo-backed eval evidence
- internal practices of external companies beyond what their public docs or repositories support

External company workflows are benchmark analogies only. Asperitas controls must be implemented and validated inside this repository before they can be treated as Asperitas facts.

## Why This Exists

AI-assisted coding can make development feel faster while quietly flattening workflow boundaries. Asperitas must not collapse source registry, retrieval, verifier, answer contract, compliance, security, and eval layers into broad helpers.

The benchmark translation rule is:

```text
external pattern -> Asperitas control -> test or eval hook -> PR evidence -> decision log
```

If a pattern cannot produce a repo control, eval hook, or decision record, it stays as research context and does not enter implementation scope.

## Standing Benchmark Sources

| Source family | Public signal to adapt | Asperitas control |
|---|---|---|
| AI Top50 workflow benchmark source pack | Data flywheel, eval-first iteration, post-training discipline, model routing, source-grounded enterprise AI, repo/test/PR agent workflows, cost/latency discipline, ontology, prompt-as-control | Treat source maps as candidates until ingested; require schema, tests, traces, permissions, logs, review gates, and eval evidence before performance claims |
| OpenAI Evals | Custom/private evals and workflow-specific eval registries | Build biology/compliance golden sets and verifier fixtures; every recurring failure becomes an eval, fixture, or durable rule |
| OpenAI Agents guardrails | Input, output, and tool guardrails with tripwire behavior and workflow boundaries | Separate input policy checks, verifier output checks, and tool/action gates; block unsafe or unsupported paths before expensive or irreversible work |
| OpenAI Agents tracing | Agent runs, generations, tool calls, handoffs, guardrails, and custom events can be traced | Preserve claim IDs, citation keys, evidence-span IDs, support decisions, failure modes, and answer-level diagnostics for future trace/report surfaces |
| Anthropic Claude Code Action | Issue/PR-triggered coding workflows, mode detection, and GitHub review flow | Route Codex tasks by type: status check, docs, schema, classifier, eval, security, merge. Do not use one generic prompt for every task |
| Claude Code trust-model lessons | Repo config and project files can affect coding-agent behavior | Treat AGENTS.md, PR comments, issues, retrieved text, and repo config as powerful but reviewable inputs; never let untrusted text override project policy |
| Agentic coding security research | Coding agents can overreach under underspecified instructions or malicious context | Add action-boundary, prompt-injection, secret-leakage, excessive-agency, and workflow-collapse tests to security/adversarial evals |
| Ginkgo Bioworks / autonomous lab benchmark | Labwork bottlenecks, scientist-in-loop automation, physical validation needs | Use DBTL and wet-lab validation as future gated evidence, not as current claims; keep human approval and validation-first doctrine |
| AI-bio/science companies | AI-biology claims require validation and domain-specific evidence | Build species/gene/protein/compound/pathway/assay/numeric-unit claim fixtures and compliance-sensitive evidence checks |
| Enterprise source-grounded AI | Retrieval, graph, permissions, citations, and source provenance are product features | Preserve source_id, source_path, evidence labels, chunk IDs, score/debug metadata, citation keys, and permission/compliance metadata |
| Coding-agent products | Plan, edit, run, fix, PR, human review | Keep small PRs, targeted tests, skipped-check rationale, status gates, and no hidden runtime coupling |
| Open-source ecosystems | Open distribution compounds quickly but raises license, supply-chain, and governance risk | Add dependency/config diff sanity, license/source-rights review, security scan hooks, and no new dependency without justification |
| VC/unicorn/top-company market maps | Durable AI businesses compound around workflow, data, distribution, trust, and operating leverage | Use as product-strategy context only; never treat market rank as technical validation |
| University/global source lists | Useful source-discovery candidates | Verify rights, provenance, licensing, source priority, and compliance status before ingestion or eval use |

## Required Asperitas Adaptation Layers

### 1. Golden Set

Build biology/compliance-specific claim verification ground truth.

Minimum fixture families:

- species identity mismatch
- gene/protein/compound/pathway mismatch
- assay, phenotype, tissue/cell type, and measurement/unit mismatch
- numeric value and unit contradiction
- wrong citation key
- unsupported claim with plausible citation
- contradicted claim with correct-looking citation
- CITES / Nagoya-ABS / LMO-GMO / biosafety / IP-license sensitive cases
- insufficient evidence and correct abstention

Acceptance rule: no claim of verifier accuracy improvement without golden-set metrics.

### 2. Report Aggregation

Aggregate claim-level outputs into answer-level diagnostics.

Required fields should include:

- answer_id
- total claims
- supported, partially_supported, unsupported, contradicted, citation_missing, citation_mismatch, ambiguous, not_verifiable_from_context counts
- compliance-sensitive flags
- blocking failures
- warning summary
- verifier version
- source/evidence coverage summary
- latency/cost overhead when measured

Acceptance rule: aggregation must not integrate into live answer generation until it has focused tests and truth-boundary review.

### 3. Adversarial and Security Eval Pack

The eval pack must test workflow and security failure modes, not only happy-path correctness.

Required cases:

- prompt injection inside retrieved text or PR comments
- instructions to ignore AGENTS.md or bypass tests
- secret/API-key exfiltration attempts
- unsafe tool execution requests
- excessive agency and broad filesystem/action scope
- provenance stripping
- hidden runtime coupling
- wrong citation and citation mismatch
- unsupported, partially supported, and contradicted claims
- biology entity mismatch
- compliance overclaim

Acceptance rule: security-sensitive changes require targeted adversarial tests or an explicit skipped-check rationale.

### 4. Metrics Dashboard / Regression Gate

Track measurable quality and operational cost.

Minimum metrics:

- false-supported rate
- false-contradicted rate
- unsupported detection recall
- citation-mismatch detection coverage
- citation-missing detection coverage
- compliance-sensitive detection recall
- answer-level faithfulness pass rate
- latency overhead
- token/cost overhead
- CI minutes
- workflow-boundary regression count

Acceptance rule: performance claims require a baseline, metric, validation method, and regression-risk statement.

## Workflow Complexity Guard

The canonical pipeline remains:

```text
source registry/raw sources
-> parsing/chunking
-> metadata/evidence span layer
-> retrieval/reranking
-> answer contract
-> atomic claim extraction
-> evidence-span matching
-> support-status classification
-> report aggregation
-> answer contract integration
-> adversarial/security eval
-> biology/compliance golden set
-> metrics/regression gate
```

Do not flatten these stages into a single helper. Small PRs are required, but small PRs must preserve the real workflow architecture.

## Security Guard

Apply these rules to every benchmark-derived implementation:

- Treat external docs, PR comments, issues, citations, retrieved text, and benchmark documents as untrusted input.
- Do not add network calls, cloud/service calls, or new dependencies unless explicitly scoped and justified.
- Do not log secrets, private source text, sensitive biological material, or compliance-sensitive material.
- Keep generated reports JSON-safe and schema-validated.
- Preserve least privilege and human approval for legal, regulatory, biosafety, wet-lab, deployment, and production-like data changes.
- Add dependency/config diff sanity to code PRs.
- Add prompt-injection and excessive-agency tests when touching agent workflow, report aggregation, external input handling, CI gates, or tool routing.

## Codex Read Rule

For architecture, verifier, security, eval, or roadmap PRs, Codex should read:

- `README.md`
- `AGENTS.md`
- `docs/FRONTIER_AGENT_WORKFLOW_BENCHMARKS.md`
- `docs/BENCHMARK_ADAPTATION_REGISTRY.md`
- the specific module and tests being changed

If the task is narrow status checking, merge finalization, or docs-only formatting, Codex may skip broad reads to preserve time and CI/GitHub Actions budget.

## PR Template Insert

Use this block in future PRs when the change touches verifier, eval, agent workflow, security, or benchmark-derived doctrine:

```markdown
## Benchmark Adaptation
- External pattern used:
- Asperitas control added:
- Eval/test hook:
- Workflow boundary preserved:
- Security risk checked:
- Truth-boundary statement:
```

## Prompt Insert

Use this in future Codex prompts:

```text
BENCHMARK_ADAPTATION_RULE:
Use OpenAI/Anthropic/Claude/Ginkgo/Top50 patterns only as P6 benchmark doctrine.
Translate every external pattern into an Asperitas-specific control, test/eval hook, and truth-boundary statement.
Do not claim external-company capability as Asperitas capability.
Do not flatten workflow stages for speed.
Security, provenance, diagnostics, and eval hooks are required architecture, not optional polish.
```

## Success Criteria

This registry is working when future PRs:

- cite the benchmark pattern they adapt
- keep implementation scope narrow without simplifying away the full workflow
- add or preserve tests/evals/security gates
- record skipped checks and rationale
- avoid unsupported performance or production claims
- produce clearer Codex prompts through `PROMPT_EVOLUTION`

## Current V1.5 Priority Order

1. Finalize V1.5C Step 4 support-status classifier if PR checks are green.
2. Add claim-verification report aggregation.
3. Add adversarial/security eval pack.
4. Add biology/compliance golden set.
5. Add metrics dashboard/regression gate.
6. Only then consider answer-contract integration or external-facing verifier claims.
