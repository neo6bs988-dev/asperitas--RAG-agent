# Contributing to Asperitas AI RAG Agent

> **Status:** ACTIVE CONTRIBUTION BASELINE  
> **Scope:** Human contributors, maintainers, coding agents, automation, documentation, source governance, evaluation, and repository changes  
> **Owner:** Asperitas COO / AI Lead  
> **Classification:** PUBLIC-SAFE GOVERNANCE  
> **Repository:** `neo6bs988-dev/asperitas--RAG-agent`  
> **Authority:** This guide is subordinate to [`gitcore.md`](gitcore.md), [`SECURITY.md`](SECURITY.md), the applicable [`AGENTS.md`](AGENTS.md), live GitHub rulesets, and explicit maintainer approval.  
> **Truth boundary:** Contribution acceptance, passing CI, or merge into `main` does not establish deployment, production readiness, legal clearance, scientific validation, wet-lab validation, security completeness, or product-market fit.

Thank you for contributing to the Asperitas biological-intelligence development repository.

This repository develops deterministic, source-grounded, compliance-aware infrastructure for biological evidence workflows. Contributions are evaluated not only for code quality, but also for provenance, rights, security, evaluation integrity, scientific truth, reversibility, and operational clarity.

---

## 1. Contribution Principles

A high-quality contribution should maximize:

```text
correct scope
+ smallest sufficient change
+ source fidelity
+ measurable verification
+ preserved security and rights boundaries
+ clear rollback
+ maintainable implementation
```

A contribution is not improved merely by adding:

- more frameworks;
- more agents;
- more abstractions;
- more dependencies;
- more prompts;
- more documentation volume;
- more benchmark claims;
- more files than required.

Prefer the lowest-complexity implementation that satisfies a falsifiable requirement.

```text
deterministic helper
-> single model, retrieval, or tool call
-> fixed workflow
-> stateful workflow
-> agent
-> multi-agent or graph
```

Higher-complexity designs require evidence that a simpler baseline failed.

---

## 2. Read Before Contributing

Before editing the repository, read the applicable current versions of:

1. [`README.md`](README.md)
2. [`AGENTS.md`](AGENTS.md)
3. [`gitcore.md`](gitcore.md)
4. [`SECURITY.md`](SECURITY.md)
5. [`pyproject.toml`](pyproject.toml)
6. relevant nested `AGENTS.md` files
7. relevant schemas, tests, workflows, and decision records

Live repository evidence takes precedence over a stale document.

Resolve current implementation state from:

```text
checked-out code and configuration
-> current branch and exact commit SHA
-> current worktree diff
-> merged pull requests and commit history
-> exact-head CI and Quality Gates
-> tests, evaluations, and generated artifacts
-> deployment and runtime evidence
-> named approvals
```

Do not rely on roadmap language, architecture diagrams, benchmark descriptions, issue text, or generated reports as proof of implementation.

---

## 3. Non-Negotiable Boundaries

### 3.1 Never commit sensitive material

Do not commit, paste, attach, quote, or expose:

- API keys, tokens, cookies, credentials, or private keys;
- customer, partner, personal, or confidential business data;
- unpublished sequences, assays, specimens, or research results;
- sensitive species or collection-location data;
- private contracts, permits, PIC/MAT, CITES, Nagoya/ABS, DSI, LMO/GMO, IP, or FTO records;
- private source-registry contents;
- private embeddings, indexes, traces, prompts, memories, or model data;
- protected evaluation answer keys or holdouts;
- exploit details that materially enable abuse.

For sensitive security findings, follow [`SECURITY.md`](SECURITY.md). Do not disclose sensitive details through a public issue, pull request, review, commit, screenshot, or discussion.

### 3.2 Public visibility is not a license grant

This repository does not currently establish an open-source license grant.

Do not assume that repository visibility grants permission to:

- reuse code;
- redistribute files;
- train models;
- ingest source content;
- commercialize derived data;
- sublicense biological information;
- publish third-party material.

Do not add third-party code, data, documents, media, model weights, prompts, or datasets unless the contribution records a valid basis for inclusion and permitted use.

This guide does not create contribution-license terms. Maintainers may reject a contribution or require separate written terms before acceptance.

### 3.3 Models and agents do not grant approval

Model output, generated code, retrieval results, automated reports, or agent decisions cannot grant:

- legal approval;
- regulatory clearance;
- rights clearance;
- biosafety or biosecurity approval;
- scientific validation;
- wet-lab authorization;
- release approval;
- deployment approval;
- permission to transmit confidential information.

### 3.4 Preserve evaluation integrity

Do not:

- expose answer keys to runtime retrieval;
- optimize directly against protected holdouts;
- weaken tests after observing a failure;
- lower thresholds to make a change pass;
- relabel `FAIL`, `PARTIAL`, or `NOT_TESTABLE` as `PASS`;
- remove negative cases without an approved replacement;
- change fixtures and implementation in a way that conceals regression;
- use grader metadata as model input;
- claim benchmark equivalence without comparable evidence.

### 3.5 Preserve scientific truth

Do not present:

- computational prediction as experimental validation;
- sequence similarity as confirmed biological function;
- one assay as replicated evidence;
- literature plausibility as product validation;
- source possession as research or commercialization rights;
- registry inclusion as lawful downstream use;
- software output as legal or regulatory judgment.

---

## 4. Choose the Correct Contribution Path

### Documentation-only correction

Suitable for:

- broken links;
- typographical errors;
- formatting defects;
- clarification that does not alter authority, policy, or capability claims.

A documentation change is not “documentation-only” when it changes:

- security requirements;
- permissions;
- source authority;
- evaluation meaning;
- rights interpretation;
- compliance status;
- implementation claims;
- release or production status.

### Bounded code or test change

Suitable for:

- deterministic bug fixes;
- bounded validation logic;
- isolated tests;
- small CLI improvements;
- local error handling;
- type or schema consistency.

### Material architecture or governance change

Open an issue or draft PR before broad implementation when changing:

- retrieval or reranking;
- source registries or schemas;
- evaluation fixtures or thresholds;
- compliance routing;
- agent permissions;
- workflows or CI;
- dependencies;
- ingestion;
- packaging;
- security controls;
- confidential-data handling;
- public capability claims.

### High-impact change

Explicit maintainer approval is required before:

- deployment;
- release;
- package publication;
- external transmission;
- source ingestion with unresolved rights;
- production-like data mutation;
- legal or scientific status promotion;
- wet-lab execution;
- high-risk biological work.

---

## 5. Repository Preflight

Before making a material change, record:

```text
TASK:
MODE:
CHANGE_CLASS:
CURRENT_BRANCH:
CURRENT_HEAD:
WORKTREE_STATUS:
APPLICABLE_INSTRUCTIONS:
IN_SCOPE:
OUT_OF_SCOPE:
AFFECTED_FILES:
BASELINE:
SUCCESS_CRITERIA:
PROHIBITED_BEHAVIOR:
VERIFICATION:
ROLLBACK:
STOP_CONDITIONS:
```

Inspect at minimum:

```bash
git status --short --branch
git rev-parse HEAD
git branch --show-current
```

Also inspect:

- the repository root;
- applicable `AGENTS.md` files;
- relevant implementation files;
- relevant tests;
- relevant schemas;
- relevant GitHub workflows;
- recent overlapping commits or pull requests;
- generated artifacts affected by the change;
- rollback options.

Do not discard or overwrite unrelated work.

Do not use destructive Git commands unless explicitly authorized.

---

## 6. Local Development Setup

### 6.1 Requirements

- Python 3.10 or newer
- Git
- an isolated virtual environment
- a clean working tree before material verification

### 6.2 Create a virtual environment

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

Upgrade packaging tools:

```bash
python -m pip install --upgrade pip
```

### 6.3 Install the development baseline

```bash
python -m pip install -e ".[dev,parsers]"
```

For local quality and packaging checks:

```bash
python -m pip install -e ".[dev,parsers,quality,packaging]"
```

For explicit dependency-security review:

```bash
python -m pip install -e ".[dev,parsers,security]"
```

Security scanner output is review evidence, not proof that the repository is vulnerability-free.

### 6.4 Verify the installation

```bash
python -c "import asperitas_agent; print(asperitas_agent.__version__)"
python -m asperitas_agent.cli --help
asperitas-agent --help
```

The canonical package implementation is under:

```text
src/asperitas_agent/
```

The root `asperitas_agent/` path is a compatibility surface and must not silently become a second implementation authority.

---

## 7. Change Classification

Use the highest applicable class.

| Class | Typical contribution | Minimum verification |
|---|---|---|
| `C0` | Typo, formatting, non-semantic documentation | Diff review, link/path check, `git diff --check` |
| `C1` | Bounded deterministic code or tests | Targeted tests, static/schema checks, artifact review |
| `C2` | Retrieval, reranking, evaluation, registries, schemas, answer contracts | Frozen baseline, targeted and adjacent regression, contamination review |
| `C3` | Security, permissions, CI, dependencies, ingestion, approval logic | Threat review, adversarial tests, least-privilege review, named approval |
| `C4` | Release, deployment, external write, production data, legal/scientific clearance, high-risk biology | Explicit action approval, rollback rehearsal, post-action verification |

Do not classify a policy, authority, security, rights, or evaluation-semantic change as `C0`.

---

## 8. Branch Naming

Create a focused branch from the current `main`.

Recommended formats:

```text
fix/<short-description>
feat/<short-description>
test/<short-description>
docs/<short-description>
ci/<short-description>
security/<short-description>
governance/<short-description>
refactor/<short-description>
chore/<short-description>
```

Examples:

```text
fix/registry-duplicate-source-id
test/sitecustomize-symlink-escape
docs/contributing-community-pack
ci/python-312-compatibility-probe
governance/source-rights-status-contract
```

Branch names should:

- describe one cohesive outcome;
- avoid personal names;
- avoid vague names such as `update`, `changes`, or `new`;
- avoid combining unrelated work;
- remain reusable in logs and rollback records.

---

## 9. Keep Changes Cohesive

A pull request should contain one primary decision.

Good scope:

```text
Add deterministic validation for one registry field
+ tests
+ documentation directly affected
```

Bad scope:

```text
Replace retrieval architecture
+ rewrite documentation
+ change dependencies
+ rename directories
+ update evaluation thresholds
+ add unrelated UI work
```

Do not:

- perform unrelated refactoring;
- reformat the entire repository;
- rename stable paths without migration evidence;
- add speculative scaffolding;
- add duplicate sources of truth;
- silently introduce dependencies;
- modify tests merely to accommodate incorrect behavior;
- mix generated artifacts with unrelated source changes.

---

## 10. Coding Standards

### 10.1 Prefer deterministic components

Use deterministic logic for:

- schema validation;
- metadata normalization;
- lifecycle transitions;
- hashing;
- permission checks;
- citation integrity;
- exact parsing;
- source filtering;
- status validation;
- reproducible scoring.

Use model or agent behavior only when deterministic logic cannot satisfy the requirement.

### 10.2 Preserve the standard-library core

The deterministic package core intentionally has no unconditional runtime dependencies.

A new runtime dependency requires:

- a demonstrated need;
- a simpler-alternative analysis;
- maintenance and supply-chain review;
- supported-version bounds;
- license review;
- failure behavior;
- rollback plan;
- tests showing the dependency is isolated appropriately.

### 10.3 Error handling

Material functions should define:

```text
input contract
output contract
failure modes
error messages
side effects
idempotency
rollback or recovery
```

Fail closed for:

- unauthorized actions;
- unknown permissions;
- invalid registry state;
- unresolved source rights;
- contaminated evaluation;
- missing mandatory provenance;
- ambiguous external-write authority.

Do not silently continue after a security, rights, evaluation-integrity, or approval failure.

### 10.4 Type and schema discipline

- Use explicit types where they improve correctness.
- Validate external and untrusted input.
- Keep schemas versioned and reviewable.
- Do not introduce multiple vocabularies for the same lifecycle state.
- Preserve backward compatibility or provide an explicit migration.
- Do not silently reinterpret existing metadata.

### 10.5 Formatting and linting

Run:

```bash
python -m ruff check src tests scripts
python -m ruff format --check src tests scripts
```

Do not apply broad automatic formatting to unrelated files.

For canonical package typing:

```bash
python -m mypy src/asperitas_agent
```

Typing checks are evidence for the inspected surface. They do not replace runtime tests.

---

## 11. Tests

Every behavior-changing contribution should include or update tests.

Tests should cover:

- expected behavior;
- invalid input;
- boundary conditions;
- failure behavior;
- permission denial;
- provenance preservation;
- rollback or idempotency where applicable;
- regression for the exact defect being fixed.

Avoid tests that:

- depend on network access without explicit approval;
- depend on current time without control;
- use unstable ordering;
- require private data;
- expose evaluation answers;
- assert implementation details instead of behavior;
- pass only because a fixture was weakened.

### 11.1 Targeted tests

Run the smallest relevant suite first.

Examples:

```bash
python -m pytest -q tests/test_source_registry_contract.py
python -m pytest -q tests/test_skill_registry.py
python -m pytest -q tests/test_sitecustomize.py
```

### 11.2 Full test suite

Before a material pull request is ready for merge:

```bash
python -m pytest
```

### 11.3 Artifact verification

```bash
python scripts/verify_artifacts.py
```

### 11.4 Registry verification

```bash
python -m asperitas_agent.cli validate-registry-contract
python scripts/validate_external_benchmark_registry.py
```

### 11.5 Retrieval evaluation

When retrieval, metadata routing, ranking, or chunking can be affected:

```bash
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5
```

Record:

- evaluated commit SHA;
- environment;
- command;
- dataset or fixture identity;
- metrics before and after;
- threshold;
- prohibited regressions;
- contamination status.

### 11.6 Packaging verification

For packaging, CLI, import-path, or bootstrap changes:

```bash
python -m build
check-wheel-contents dist/*.whl
python scripts/verify_packaging_contract.py --json
python scripts/verify_distribution_install.py --dist-dir dist --json
```

### 11.7 Diff hygiene

```bash
git diff --check
```

---

## 12. Source and Data Contributions

Source-related contributions must be metadata-first.

A source candidate is not automatically:

- approved;
- verified;
- licensed;
- ingested;
- indexed;
- retrievable;
- suitable for model training;
- suitable for commercialization;
- suitable for public claims.

Record the applicable fields defined by the current canonical schemas, including where relevant:

```text
source_id
title
source_type
origin
author_or_owner
version_or_date
date_accessed
source_url
provenance
disclosure_level
verification_status
license_status
ingestion_status
allowed_use_cases
prohibited_use_cases
risk_flags
evidence_label
```

Do not add raw external source files merely because a metadata record exists.

Do not ingest, process, chunk, embed, index, train on, redistribute, or commercialize source content until the required rights and approval state is established.

### 12.1 Biological-rights separation

Treat these as separate rights:

```text
specimen possession
source-country access
collection authority
PIC/MAT
CITES movement
research
sequencing
derived data
dataset inclusion
model training
model weights
model output
commercialization
sublicensing
patenting
customer transfer
```

One right does not automatically grant another.

---

## 13. Biological and Scientific Contributions

Use the evidence ladder:

```text
computational prediction
-> literature-supported hypothesis
-> single assay
-> replicated assay
-> independent validation
-> scale-up
-> production evidence
-> commercial evidence
```

Preserve:

- controls;
- replicates;
- uncertainty;
- negative results;
- assay conditions;
- versioned inputs;
- provenance;
- failure taxonomy;
- next decision.

Do not submit high-risk wet-lab instructions, pathogenic enhancement, regulatory-evasion guidance, unauthorized genetic-resource use, or autonomous laboratory execution.

Safe contributions may include:

- public, non-sensitive computational analysis;
- metadata normalization;
- compliance-aware routing;
- validation schemas;
- evidence-state classification;
- public literature synthesis with clear uncertainty;
- non-operational biosafety documentation.

---

## 14. Evaluation Contributions

Before changing an evaluator, fixture, threshold, or grader, define:

```text
evaluation identity
input set
environment
expected behavior
prohibited behavior
rubric
criticality
threshold
number of trials
contamination controls
```

Separate:

```text
runner input
ground truth
grader metadata
runtime retrieval corpus
```

Do not expose protected ground truth to the system being evaluated.

A valid evaluation report must identify:

- exact commit SHA;
- evaluator version;
- fixture version;
- environment;
- commands;
- metrics;
- threshold;
- failure cases;
- invalid or untestable cases;
- limitations.

Changes made after observing results require a fresh clean evaluation.

---

## 15. Security Contributions

Security changes should include:

- affected asset;
- threat or failure mode;
- trust boundary;
- attacker capability;
- expected security property;
- least-privilege analysis;
- failure behavior;
- targeted test;
- adjacent regression;
- rollback;
- residual risk.

Do not claim that a scanner result or passing test proves the repository is secure.

For sensitive findings, do not open a public issue or pull request. Follow [`SECURITY.md`](SECURITY.md).

---

## 16. Dependency Contributions

A dependency addition or upgrade should document:

```text
package:
current_version:
proposed_version:
purpose:
simplest_alternative:
runtime_or_optional:
license_review:
security_review:
transitive_dependency_impact:
supported_python_versions:
size_impact:
failure_behavior:
tests:
rollback:
```

Prefer:

- pinned compatible ranges;
- optional extras for non-core capabilities;
- official packages;
- maintained dependencies;
- minimal transitive dependency trees.

Avoid:

- unmaintained libraries;
- packages with unclear provenance;
- silent major-version upgrades;
- dependencies used only for trivial helper logic;
- dependencies that introduce network access without explicit design;
- dependencies that weaken supported Python versions.

---

## 17. Documentation Contributions

Documentation must distinguish:

| Status | Meaning |
|---|---|
| `DOCUMENTED` | Described in a repository artifact |
| `IMPLEMENTED` | Code or configuration exists |
| `TESTED` | Named tests ran in a stated environment |
| `CI_VERIFIED` | Required checks passed on the exact evaluated SHA |
| `APPROVED` | A named human granted the specific authority |
| `DEPLOYED` | Deployment evidence exists for a named environment |
| `OPERATIONALLY_VERIFIED` | Runtime behavior was observed |
| `PRODUCTION_READY` | Release, security, operations, compliance, ownership, and rollback gates passed |
| `PLANNED` | Intended future work |
| `UNVERIFIED` | Evidence is missing, stale, inaccessible, or insufficient |
| `BLOCKED` | A mandatory gate failed |
| `INVALID` | Evidence integrity or comparability failed |

Do not describe a planned or documented capability as implemented.

Do not describe a CI-passing component as deployed or production-ready.

Do not attribute private prompts, private workflows, or undisclosed engineering methods to external companies or individuals.

Use public official sources only as benchmark input, not as evidence that Asperitas uses equivalent internal systems.

---

## 18. AI-Assisted Contributions

AI-assisted work is permitted, but the contributor remains responsible for the result.

Review all generated content for:

- correctness;
- security;
- licensing;
- provenance;
- hallucinated APIs;
- hallucinated files or tests;
- stale package behavior;
- fabricated citations;
- unauthorized data disclosure;
- evaluation contamination;
- overclaiming;
- unnecessary complexity.

Do not paste confidential material into an external model or tool without explicit authorization.

In the pull request, disclose material AI assistance when it affected:

- architecture;
- implementation;
- tests;
- security analysis;
- source selection;
- biological interpretation;
- legal or compliance extraction.

Suggested disclosure:

```text
AI assistance:
- Tool or model:
- Scope:
- Human verification performed:
- External data transmitted:
- Known limitations:
```

Do not treat model output as reviewer approval.

---

## 19. Commit Guidelines

Commits should be:

- cohesive;
- reviewable;
- reversible;
- free of unrelated formatting;
- free of generated secrets or local artifacts;
- descriptive enough for audit and rollback.

Recommended commit format:

```text
type(scope): imperative summary
```

Examples:

```text
fix(registry): reject duplicate source identifiers
test(bootstrap): cover repository path deduplication
docs(governance): add contribution requirements
ci(packaging): verify clean wheel installation
security(permissions): fail closed on unknown write authority
```

Recommended types:

```text
feat
fix
test
docs
ci
security
governance
refactor
perf
chore
```

Do not use a commit message to claim verification that did not occur.

Bad:

```text
fix everything
production ready
fully secure
validated biology
```

Better:

```text
fix(registry): reject malformed verification status
```

---

## 20. Pull Request Requirements

All changes to `main` must go through a pull request under the active repository ruleset.

A pull request should include:

```markdown
## Decision

What exact outcome does this pull request implement?

## Baseline

What is the current behavior, evidence, bottleneck, and simplest alternative?

## Scope

### In scope

- ...

### Out of scope

- ...

## Change class

C0 / C1 / C2 / C3 / C4

## Changes

- exact file and behavior changes

## Truth status

- DOCUMENTED:
- IMPLEMENTED:
- TESTED:
- CI_VERIFIED:
- UNVERIFIED:
- BLOCKED:

## Verification

- exact commands
- test results
- evaluation identity
- exact head SHA

## Security, rights, and biology review

- trust boundaries
- sensitive data
- source rights
- biosafety or compliance impact

## Failure modes

- expected failures
- prohibited behavior
- residual risks

## Rollback

- exact revert or restoration path
```

### 20.1 Pull request quality bar

A pull request is not ready when:

- scope is ambiguous;
- unrelated files are included;
- required tests are absent;
- tests are weakened;
- source provenance is missing;
- rights status is overstated;
- sensitive information is exposed;
- generated artifacts cannot be tied to the exact head;
- rollback is undefined;
- capability claims exceed evidence.

### 20.2 Draft pull requests

Use a draft PR for:

- early design review;
- C2–C4 work in progress;
- architecture changes;
- security-sensitive design without sensitive disclosure;
- changes awaiting baseline measurement;
- changes awaiting full regression.

Do not mark a PR ready until its scope, tests, risks, and rollback are reviewable.

---

## 21. Required Merge Gates

The live GitHub ruleset and workflow definitions are authoritative.

The expected required check contexts currently include:

```text
Python smoke checks
tests-artifacts-retrieval-eval
ubuntu-latest / Python 3.10
ubuntu-latest / Python 3.11
windows-latest / Python 3.11
```

Before merge:

- the PR branch must be up to date with `main`;
- all required checks must pass;
- review conversations must be resolved;
- force push must not be used to bypass review;
- merge must use the allowed repository merge method;
- the evaluated head SHA must match the merge decision.

If check names or workflow structure change, update this guide in the same governance change or immediately afterward.

Historical successful checks do not certify a new head.

---

## 22. Review Standards

Reviewers evaluate:

### Correctness

- Does the implementation satisfy the stated contract?
- Are edge cases and failure modes covered?

### Scope

- Is this the smallest sufficient change?
- Are unrelated modifications excluded?

### Evidence

- Are claims tied to exact repository evidence?
- Are verification commands and results reproducible?

### Security

- Does the change preserve least privilege?
- Can untrusted input gain authority?
- Are secrets or restricted data exposed?

### Source governance

- Is provenance preserved?
- Are verification, license, and permitted-use states accurate?

### Evaluation integrity

- Were thresholds frozen?
- Is ground truth isolated?
- Was regression tested without contamination?

### Biology and compliance

- Are scientific claims at the correct evidence stage?
- Are legal, rights, biosafety, and regulatory decisions human-gated?

### Operations

- Is failure observable?
- Is rollback explicit?
- Is the change maintainable?

Review outcomes may be:

```text
APPROVE
REQUEST_CHANGES
DEFER
BLOCK
SUPERSEDED
```

A request for changes is not a personal judgment. It identifies unmet repository requirements.

---

## 23. Merge and Post-Merge Expectations

Use the repository-approved merge method, normally squash merge.

The squash commit should describe:

- the decision;
- the primary implementation;
- important verification;
- material limitations;
- rollback identity.

After merge:

1. verify the resulting `main` commit;
2. confirm required workflows;
3. verify that no unexpected files were introduced;
4. update implementation status only when evidence supports it;
5. record significant failures as durable tests, schemas, controls, or decision records.

A merged pull request proves only that the code was merged.

It does not by itself prove:

- deployment;
- runtime correctness;
- vulnerability absence;
- legal or regulatory clearance;
- scientific validation;
- wet-lab validation;
- production readiness;
- customer demand.

---

## 24. Unacceptable Contributions

Maintainers may close or reject contributions that:

- expose confidential or restricted information;
- include unauthorized source material;
- weaken tests or thresholds without approved evidence;
- introduce prompt injection or permission bypass;
- make unverified legal, scientific, security, or production claims;
- include high-risk biological instructions;
- duplicate an existing authority or schema;
- introduce excessive architecture without baseline evidence;
- mix unrelated changes;
- lack provenance or permitted-use information;
- conceal AI-generated content that was not human-verified;
- use abusive, harassing, discriminatory, or disruptive conduct;
- cannot be reviewed or safely rolled back.

---

## 25. Final Contributor Checklist

Before requesting review, confirm:

```text
[ ] I read README.md, AGENTS.md, gitcore.md, and SECURITY.md.
[ ] I recorded the exact base and head SHAs.
[ ] The branch contains one cohesive outcome.
[ ] Unrelated user or agent work is preserved.
[ ] No secrets, confidential data, or restricted biological information are included.
[ ] Third-party code and data have a documented permitted basis.
[ ] Scientific, legal, security, and production claims match the evidence.
[ ] Tests cover the intended behavior and relevant failures.
[ ] I did not weaken fixtures, thresholds, schemas, or expected behavior to obtain a pass.
[ ] Runtime inputs are isolated from evaluation ground truth.
[ ] Targeted tests pass.
[ ] Full pytest passes when required.
[ ] Artifact and registry verification pass when applicable.
[ ] Retrieval evaluations were rerun when retrieval behavior could change.
[ ] Packaging checks were rerun when package, CLI, or import behavior could change.
[ ] Ruff and diff hygiene checks pass for the affected surface.
[ ] The PR documents verification on its exact head SHA.
[ ] Security, rights, compliance, and biology impacts are disclosed.
[ ] AI assistance is disclosed when material.
[ ] Rollback is explicit and feasible.
[ ] All required GitHub checks pass.
[ ] All review conversations are resolved.
```

Thank you for helping build verifiable, safe, and commercially credible biological-intelligence infrastructure.
