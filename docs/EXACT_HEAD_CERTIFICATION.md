# Exact-Head Certification Contract

> **Status:** ACTIVE VERIFICATION CONTRACT  
> **Scope:** Repository packaging, import bootstrap, CLI exposure, source-registry contracts, agent-governance contracts, and run-scoped evidence  
> **Owner:** Asperitas COO / AI Lead  
> **Classification:** PUBLIC-SAFE GOVERNANCE  
> **Truth boundary:** This document defines required evidence. It does not certify any commit by itself.

## 1. Decision

A repository revision may be described as `CI_VERIFIED` only when the required checks complete successfully against the exact commit being evaluated.

```text
named commit SHA
-> exact source checkout
-> deterministic checks
-> run-scoped artifacts
-> successful required workflows
-> human promotion decision where applicable
```

A branch name, pull-request number, mergeability result, documentation statement, prior successful run, or status badge is not an exact-head certificate.

## 2. Required workflow set

For material changes, the evidence set is:

1. `CI`
2. `Quality Gates`
3. `Exact Head Certification`

The first two workflows validate the repository-wide test, artifact, metadata, and retrieval-evaluation baseline. `Exact Head Certification` specializes the packaging, import, compatibility-bootstrap, and cross-platform surfaces that are not fully represented by the default Python 3.11 Ubuntu jobs.

## 3. Exact Head Certification matrix

The workflow checks:

| Environment | Purpose |
|---|---|
| Ubuntu / Python 3.10 | Minimum supported Python contract |
| Ubuntu / Python 3.11 | Primary CI Python contract |
| Windows / Python 3.11 | Cross-platform path, console-script, and bootstrap contract |

Each matrix entry must:

- check out the explicit pull-request source SHA or pushed `main` SHA;
- assert that the checked-out Git SHA matches the expected SHA;
- install the declared development, parser, and packaging extras;
- resolve `asperitas_agent` from the canonical `src/` layout;
- verify package and distribution version consistency;
- verify the `asperitas-agent` console entry point;
- confirm that the deterministic core has no unconditional runtime dependency;
- validate the canonical source-registry contracts;
- run dedicated `sitecustomize.py` regression tests;
- run skill-registry and skill-discovery governance tests;
- build a wheel and source distribution;
- validate wheel contents;
- install the wheel in a clean isolated environment outside the repository;
- verify module and console-script execution from that clean environment;
- run `git diff --check`;
- upload run-scoped JSON and JUnit evidence.

## 4. Status vocabulary

| Status | Meaning |
|---|---|
| `IMPLEMENTED` | Workflow, scripts, or tests exist in the inspected revision |
| `TESTED` | Named checks ran in a stated environment |
| `CI_VERIFIED` | Required workflows passed on the exact evaluated SHA |
| `APPROVED` | A named human approved the specific promotion or merge |
| `DEPLOYED` | Deployment evidence exists for a named environment |
| `PRODUCTION_READY` | Release, security, operations, compliance, ownership, and rollback gates passed |
| `UNVERIFIED` | Exact-head evidence is absent, stale, incomplete, inaccessible, or ambiguous |
| `INVALID` | Evidence is contaminated, mismatched to the SHA, or produced under altered criteria |

Passing repository workflows does not establish deployment, legal clearance, scientific validation, wet-lab validation, protected-holdout generalization, vulnerability absence, or production readiness.

## 5. Certificate identity

A valid certification record must identify:

- repository;
- exact commit SHA;
- workflow name and run ID;
- job environment;
- Python version;
- commands or named checks;
- completion result;
- generated evidence artifacts;
- known skipped steps;
- timestamp supplied by the execution platform.

Evidence from one SHA must not be attached to another SHA.

## 6. Invalidation rules

Certification is invalidated when:

- the branch or `main` head changes;
- a required workflow is missing, cancelled, skipped, or unsuccessful;
- the checkout SHA differs from the declared source SHA;
- tests, fixtures, answer keys, schemas, thresholds, or expected behavior are weakened after results are known;
- protected evaluation information contaminates runtime inputs;
- a required artifact cannot be tied to the workflow run;
- a dependency, Python version, runner image, or workflow change makes the result non-comparable for the decision being made;
- a material change occurs after the certified commit.

A new material head requires a fresh run. Historical success may be used as context, not as current certification.

## 7. Failure handling

On failure:

1. preserve the failing SHA and workflow evidence;
2. identify the failing contract and smallest responsible change;
3. do not weaken tests, thresholds, schemas, or truth labels;
4. patch on a branch;
5. rerun the affected targeted check;
6. rerun all required exact-head workflows;
7. merge only after the new head passes and the owner approves the action.

## 8. Rollback

The workflow and its supporting scripts are repository controls, not irreversible infrastructure.

Rollback options are:

- close the unmerged pull request;
- revert the exact merge commit;
- restore the previous workflow and scripts from Git history;
- invalidate certificates produced by the reverted or defective control version.

Rollback must not be represented as proof that an earlier revision is secure, correct, or production-ready. It only restores the previous repository state.
