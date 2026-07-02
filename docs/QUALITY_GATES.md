# Quality Gates

Apply these gates before reporting a task as done. A gate is not a suggestion; it is the minimum evidence needed to call a change complete.

The goal is not merely passing tests. The goal is benchmark-informed, source-grounded, compliance-native, regression-resistant progress.

## Gate Selection Matrix

| Change Type | Required Gates |
|---|---|
| Docs/governance only | Re-read edited files, Markdown/path sanity, truth-boundary review, PR review |
| Source code | Targeted tests, relevant lint/type/schema checks, artifact verification, PR review |
| Source registry/metadata/chunks | Schema/artifact verification, chunk audit if affected, source-policy review |
| Retrieval/ranking/scoring | Targeted tests, retrieval evals, threshold gates when applicable, regression review |
| Answer generation/citation | Answer contract checks, claim/citation checks, source-grounding review, compliance review |
| Compliance/security | Refusal/escalation tests, leakage/adversarial checks where available, human-risk review |
| Token/cost/latency | Before/after metric evidence, no quality regression, net runtime evidence for latency claims |
| CI/workflow | Workflow syntax/path review, targeted CI dispatch or next-best static review |
| Release/main | Full relevant suite, artifact readiness, retrieval/golden evals, metric gates, diff checks |

## Gate Execution Policy

Use the lightest gate set that protects the changed surface.

## V1.5A Risk And Changed-Area Selection

V1.5+ tasks must classify risk and changed surface before editing.

| Risk level | Typical examples | Verification posture |
|---|---|---|
| Low | Docs/templates wording, issue template fields, decision-log note, non-executable governance sync | Cheap QA plus GitHub review. Skip `pytest` and retrieval eval with rationale. |
| Medium | CI/config changes, executable scripts, source code with narrow behavior, eval report generator changes | Targeted tests for the changed area plus artifact verification when artifacts may be affected. |
| High | Core RAG/retrieval, chunking, metadata, embeddings, vector DB, reranking, answer generation, compliance/security behavior, release/main readiness | Full relevant local gates, retrieval/compliance evals as applicable, and GitHub Actions review. |

| Changed surface | Minimum V1.5A verification |
|---|---|
| Docs/templates | Re-read files, check headings/links/paths/code fences, inspect diff, run `git diff --check`. |
| CI/config | Inspect YAML/config diff, run `git diff --check`, and run targeted local command if the config can be exercised locally. |
| Source code | Add/update focused tests and run targeted `pytest`; run full `python -m pytest` for shared behavior or unclear blast radius. |
| Retrieval/chunking/metadata/embeddings/vector/reranking | Run targeted tests plus required retrieval/chunk gates. |
| Answer generation/citation | Run answer/citation tests and source-grounding review; run retrieval eval if evidence selection or retrieval is touched. |
| Compliance/security | Run targeted compliance/security tests and compliance/biosafety review. |
| Evals/fixtures/metrics | Run targeted eval tests or the affected eval command, and label metrics as `Fresh Run`, `Historical`, or `Not Run`. |

Conserve GitHub Actions minutes by running targeted checks by default. Run full suites, broad retrieval comparisons, release gates, or expanded CI only when risk justifies it.

GitHub Actions disconnections, cancellations, and timeouts are validation-scope evidence. Record what happened, rerun or narrow the gate when required, and do not call the timeout itself a product failure unless required gates remain unclear, fail, or cannot be rerun.

| Gate Class | Runs Where | Purpose |
|---|---|---|
| Targeted local checks | Developer/Codex workspace | Fast feedback on changed behavior |
| Required CI | GitHub Actions | Prevent unverified changes from entering `main` |
| Conditional retrieval gates | Local or CI | Protect retrieval, evidence, and source boundaries |
| Conditional answer gates | Local or CI | Protect answer contract, citation faithfulness, and truth routing |
| Conditional security gates | Local, CI, or manual | Protect secrets, leakage, prompt injection, and excessive agency surfaces |
| Release-only gates | Release branch or closeout | Produce complete milestone evidence |

If a run times out or disconnects, split validation by gate and report exact pass/fail evidence.

## Canonical Commands

Run from the repository root when available.

Core checks:

```bash
python -m pytest
python scripts/verify_artifacts.py
git diff --check
```

Retrieval/chunking/metadata checks:

```bash
python scripts/audit_chunk_sections.py --json
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever vector --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5
```

Threshold gates:

```bash
python scripts/run_retrieval_eval.py --retriever baseline --limit 5 --enforce-thresholds
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5 --enforce-thresholds
python scripts/run_retrieval_eval.py --retriever vector --limit 5 --enforce-thresholds
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5 --enforce-thresholds
```

Answer/truth/compliance checks when present:

```bash
python scripts/check_v1_3c_answer_contract.py
python scripts/check_v1_3d_truth_compliance_router.py
```

Use the latest milestone report, decision log, or `docs/V1_5_PERFORMANCE_ROADMAP.md` for current baselines and required metric interpretation.

## Documentation Gate

Required when docs, prompts, governance files, PR templates, workflow docs, or roadmap files change.

Pass condition:

- edited files can be fetched/read as UTF-8 Markdown or expected text;
- headings and code fences are intact;
- no false implementation status is introduced;
- source hierarchy and truth boundary remain intact;
- no confidential/private data is exposed;
- PR body states docs-only scope and skipped tests rationale.

Docs-only changes do not require pytest or retrieval eval unless they change executable commands, artifacts, source registry, chunks, eval fixtures, or code paths.

In GitHub Actions, docs/templates/decision-log-only pull requests may take the lightweight Quality Gates path. That path must still check changed surface, Markdown/code-fence sanity, issue-template shape when relevant, and truth-boundary/no-overclaim language, then report skipped pytest/retrieval evals as `Not Run` with rationale. Any source, runtime, artifact, retrieval, eval fixture, dependency, CI workflow, or generated-file change must use the full Quality Gates path.

The full Quality Gates job keeps a conservative runtime budget so unit tests, artifact checks, chunk audit, baseline retrieval eval, MVP-003 retrieval eval, and hybrid retrieval eval can complete when the changed surface requires them. Increasing this timeout is a CI runtime-policy change only; it does not weaken retrieval gates or claim retrieval performance improvement.

## Source Code Gate

Required when source code changes.

Pass condition:

- changed behavior is covered by targeted tests;
- `python -m pytest` or narrower justified test command passes;
- skipped tests have rationale and residual risk.

Hard fail:

- source code changed without tests or documented blocker;
- tests are claimed without being run;
- gates are relaxed to force a pass.

## Retrieval Gate

Required when retrieval, chunking, scoring, metadata filters, embeddings, vector DB, hybrid search, reranking, eval oracle, or answer evidence selection changes.

Pass condition:

- required retriever modes are evaluated;
- before/after metrics are reported when claiming improvement;
- no unexplained regression appears;
- source IDs, source priority, source paths, section metadata, and evidence labels are preserved;
- `mvp003` remains the protected deterministic reference unless explicitly changed by approved task.

Hard fail:

- metrics are invented or omitted;
- threshold gate fails and is ignored;
- a comparison mode is silently made default;
- retrieval improvement is claimed without evidence.

## Claim-To-Citation Gate

Required when answer generation, citation rendering, evidence labels, truth routing, or unsupported-claim handling changes.

Target state:

- split material answers into atomic claims;
- attach each claim to one or more source spans;
- grade claims as supported, unsupported, contradicted, too vague, or needs verification;
- report answer-level groundedness and unsupported-claim rate.

Until this is fully implemented, PRs must at least perform source-grounding review and preserve existing answer contract checks.

## Compliance And Biosafety Gate

Required when biological data, biodiversity access, CITES, Nagoya, LMO, K-BDS, privacy, security, regulatory, legal, IP, investor, partner, public-communication, or wet-lab-sensitive risk is affected.

Pass condition:

- risk domain is identified;
- missing approvals or evidence are explicit;
- unsafe outputs are blocked or escalated;
- internal, investor-facing, partner-facing, public, and restricted outputs are distinguished.

Hard fail:

- regulated biological, confidential, personal, legal, or investor-sensitive claims are exposed without review;
- wet-lab validation or regulatory approval is implied without evidence.

## Security And Adversarial Gate

Use when tools, external actions, retrieval sources, prompts, file ingestion, secrets, connectors, or agent autonomy are affected.

Check for:

- prompt injection;
- malicious retrieved-document instructions;
- source poisoning;
- PII or confidential leakage;
- over-privileged tools;
- excessive agency;
- insecure output handling;
- secret or credential exposure.

## Performance Gate

Performance claims require measured evidence.

| Claim | Required Evidence |
|---|---|
| Token reduction | Before/after answer or context token metrics |
| Cost reduction | Before/after cost estimate or token proxy |
| Latency improvement | Net runtime improvement, preferably p50/p95 when available |
| Retrieval improvement | Before/after retrieval metrics |
| Answer quality improvement | Faithfulness, citation, unsupported-claim, or golden task evidence |
| Compliance improvement | Refusal/escalation/adversarial pass evidence |

Cache hit count alone is not a latency win.

## GitHub Review Gate

Required before merge.

- Changed files match the objective.
- No source code changed for docs/governance-only work.
- No secrets, credentials, endpoints, generated indexes, or model binaries were added unexpectedly.
- No false production-status claim was introduced.
- Skipped checks and residual risks are documented.
- The PR is small enough to review.

## Merge Safety

A PR may merge only when scope, validation, truth boundary, and residual risks are clear.

A PR must remain blocked when:

- pass/fail evidence is unclear;
- CI failure is unexplained;
- retrieval/answer behavior changed without relevant evals;
- source provenance or evidence labels are dropped;
- compliance risk is hidden;
- docs and implementation disagree materially.
