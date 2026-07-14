# Security Policy

This public repository contains development infrastructure for source-grounded RAG, retrieval evaluation, AI-assisted workflows, and compliance-aware biological information handling.

**Do not open a public GitHub issue for a sensitive security finding.** Public issues, pull requests, discussions, screenshots, logs, and pasted prompts are not approved channels for credentials, private data, confidential source text, unpublished research, protected biological data, or exploit details.

> **VERIFY_BEFORE_PUBLISHING:** Confirm that GitHub Private Vulnerability Reporting is enabled for this repository, or add an owner-approved private security contact before merging this policy. Until a private reporting route is verified, do not transmit sensitive details through public repository channels.

If a credential or token may already be exposed, revoke or rotate it immediately through the relevant provider or repository owner. Deleting it from the latest commit is not sufficient incident remediation.

## Supported Versions and Scope

This repository does not currently publish a production support or long-term-support commitment.

| Version or branch | Support status | Notes |
|---|---|---|
| `main` | Supported for security review | Actively maintained development branch. Reports should identify the affected commit SHA. |
| Open pull-request branches | Reviewable when relevant | Report issues that could merge into `main`, expose data, weaken controls, or affect contributors. |
| Historical branches and commits | Not routinely supported | Reproduce against current `main` when it is safe and practical. |
| External deployments or forks | Not covered by default | Report repository defects here; deployment-specific incidents belong to the operator. |
| Production service | Not established | This repository does not claim a supported production deployment. |

Package metadata, roadmap phases, evaluation fixtures, prompts, or architecture documents do not create a production support commitment.

## How to Report a Vulnerability

Use the following order:

1. **GitHub Private Vulnerability Reporting**, after the repository owner verifies that it is enabled.
2. An owner-approved private maintainer or security channel documented outside public issue content.
3. A draft repository security advisory created by an authorized maintainer after a private report is received.

Do not include sensitive details in:

- public issues or discussions;
- pull-request descriptions or review comments;
- public commit messages;
- CI logs or uploaded artifacts;
- screenshots containing tokens, private paths, partner information, or source text;
- prompts sent to tools that are not approved for the affected data classification.

If no verified private route is available, send only a non-sensitive request for private contact through an established maintainer relationship. Do not reveal the vulnerability, affected secret, confidential document, or reproduction details publicly.

### Sensitive attachment handling

- Redact credentials, tokens, cookies, private keys, personal data, and confidential biological content.
- Prefer the minimum proof required to establish impact.
- Do not attach a full private corpus, source registry, model trace, index, or partner dataset when a reduced synthetic reproduction is sufficient.
- Identify any content that must be deleted after triage.
- State whether external systems or third-party services received any data.

## What to Include in a Report

Provide as much of the following as safely possible:

- a concise title;
- affected file, module, script, workflow, tool, connector, or policy;
- affected branch, version, and commit SHA;
- vulnerability class and relevant trust boundary;
- prerequisites, permissions, and attacker capabilities;
- minimal non-destructive reproduction steps;
- expected behavior and observed behavior;
- confidentiality, integrity, availability, safety, or governance impact;
- whether credentials, private data, source provenance, external tools, or approval gates are affected;
- whether network access, filesystem writes, Git operations, or external side effects occurred;
- whether the issue reproduces in a clean environment;
- redacted logs, traces, or screenshots;
- a minimal proof of concept using synthetic or test data;
- suggested mitigation, regression test, or containment step if known;
- disclosure constraints and preferred contact method.

### AI-agent and RAG details

When relevant, also include:

- the trusted instruction source and the untrusted input source;
- model, provider, tool, MCP server, plugin, or connector involved;
- granted permission level and approval state;
- sandbox, working-directory, and network configuration;
- prompt-injection, retrieved-document, tool-output, memory, or rules-file vector;
- source ID, evidence span, provenance, confidentiality, license, verification, or `allowed_use` impact;
- whether untrusted content influenced a privileged action;
- any data-exfiltration path or unintended external transmission;
- whether an autonomous or repeated side effect occurred;
- affected guardrail, schema, test, evaluation, or trace;
- whether answer-key, expected-answer, oracle, or protected-holdout information crossed into a runtime or promotion path;
- whether a required human approval was bypassed.

### Biological and compliance details

When relevant, identify without exposing unnecessary sensitive content:

- data classification: public, private-development, confidential, or protected;
- species, sample, specimen, sequence, assay, or partner-data sensitivity;
- CITES, Nagoya/ABS, LMO/GMO, biosafety, biosecurity, IP, licensing, privacy, or export-control relevance;
- whether operational biological instructions were exposed;
- whether a compliance, release, or wet-lab human gate was bypassed;
- whether unpublished research, proprietary data, or partner information left its authorized boundary.

## In-Scope Security Issues

A report is in scope when it plausibly affects confidentiality, integrity, availability, safety, approval boundaries, source governance, or software supply-chain trust.

### Application and repository security

Examples include:

- command injection or arbitrary code execution;
- unsafe subprocess or shell invocation;
- path traversal, symlink escape, or filesystem-boundary bypass;
- unauthorized file creation, modification, deletion, or overwrite;
- unsafe deserialization or parser behavior;
- access-control or approval bypass;
- sensitive information written to logs, traces, caches, or artifacts;
- secret, credential, token, or private-key exposure;
- CI permission escalation or unsafe workflow behavior;
- artifact tampering or untrusted generated-file promotion.

### AI agent and tool security

Examples include:

- direct or indirect prompt injection with material impact;
- untrusted text overriding repository or developer policy;
- tool-output, rules-file, skill, plugin, issue, PR, or webpage injection;
- excessive agency or unauthorized tool use;
- bypass of user approval, sandbox, branch, filesystem, or network boundaries;
- unauthorized push, merge, release, external communication, or state change;
- MCP or connector trust confusion, impersonation, or permission escalation;
- malicious or compromised skills, plugins, hooks, or tool definitions;
- cross-context, cross-project, or agent-memory leakage;
- memory poisoning or untrusted content promoted into durable policy;
- unsafe multi-agent handoff or authority confusion;
- duplicate or repeated side effects after retry or resume;
- sandbox escape or network egress that violates the configured boundary.

### RAG, retrieval, and data security

Examples include:

- source, corpus, index, embedding, or retrieval poisoning;
- unauthorized ingestion, indexing, or reactivation of blocked sources;
- provenance, citation, evidence-span, confidentiality, license, verification, or `allowed_use` metadata loss;
- citation spoofing or source identity substitution;
- retrieval of confidential or protected documents outside authorization;
- public, private-development, confidential, or protected corpus mixing;
- retrieved content controlling privileged behavior;
- embedding, index, cache, trace, or artifact disclosure;
- stale, revoked, or blocked source use after revocation;
- answer-key, expected-answer, oracle, rationale, or protected-holdout leakage into runtime retrieval or promotion decisions;
- evaluation contamination or misleading promotion evidence;
- hidden retrieval manipulation that defeats auditability.

Evaluation-oracle leakage that affects only benchmark validity may be classified as an evaluation-integrity defect rather than a production security incident. It becomes a security issue when it also creates unauthorized data access, privilege, disclosure, unsafe action, or approval bypass.

### Model and output security

Examples include:

- unvalidated model output directly driving privileged actions;
- schema or structured-output bypass;
- insecure generated code entering an execution or deployment path without required review;
- private or confidential data disclosure;
- unsupported evidence represented as verified with material downstream impact;
- model or provider fallback that silently weakens required security controls;
- safety or refusal bypass that enables a prohibited action;
- system, developer, credential, or secret leakage.

### Software supply chain and CI/CD

Examples include:

- malicious, compromised, or dependency-confused packages;
- unreviewed automatic dependency, plugin, skill, model, or MCP installation;
- compromised or overly privileged GitHub Actions;
- secret leakage through workflows, caches, artifacts, or logs;
- build, artifact, package, or release provenance failure;
- unreviewed third-party code, model assets, binaries, or generated files;
- lockfile or resolved-dependency integrity failure;
- dependency or action updates that materially weaken security or compliance controls.

### Biological, compliance, and governance security

Examples include:

- exposure of confidential biological, sequence, species, sample, specimen, assay, or partner data;
- unauthorized use or disclosure of genetic-resource information;
- bypass of provenance, licensing, confidentiality, verification, or permitted-use controls;
- unauthorized protected-data ingestion or retrieval;
- bypass of CITES, Nagoya/ABS, LMO/GMO, biosafety, biosecurity, IP, privacy, legal, export-control, or release human gates;
- unsafe biological output escaping required review;
- autonomous high-risk wet-lab action or external instruction;
- unauthorized modification of compliance, approval, validation, or wet-lab status;
- unpublished research, investor, partner, or public-claim leakage.

These categories describe security and governance boundaries. They do not state that the repository has received legal, regulatory, CITES, Nagoya, LMO, biosafety, biosecurity, IP, or wet-lab approval.

## Out-of-Scope or Non-Security Reports

The following are normally handled as bugs, documentation issues, research questions, or governance discussions rather than security vulnerabilities:

- feature requests;
- model-quality or answer-quality complaints without a security boundary impact;
- unsupported hypothetical concerns with no plausible impact path;
- documentation typos or stale wording;
- known development-only limitations;
- the absence of a production deployment or capability;
- benchmark-score differences without confidentiality, integrity, access, or approval impact;
- legal or compliance interpretation disagreements;
- independent vulnerabilities in third-party services that do not originate in this repository;
- social-engineering, phishing, or credential-harvesting requests;
- unrestricted denial-of-service or load testing;
- testing that requires access to another person’s or organization’s data;
- expected behavior in public synthetic fixtures without a boundary violation.

A report becomes security-relevant when it also demonstrates unauthorized access, secret leakage, data exposure, unsafe action, integrity loss, supply-chain compromise, or approval bypass.

## Researcher Safety Rules

Use the minimum activity necessary to validate a finding.

Permitted research should:

- occur in systems and accounts you own or are explicitly authorized to test;
- use synthetic, public, or dedicated test data;
- remain rate-limited, non-destructive, and reversible;
- avoid persistent access;
- redact sensitive evidence;
- stop once impact is established;
- preserve logs needed for coordinated remediation.

Do not:

- access, copy, alter, or delete another user’s or organization’s data;
- install persistence or maintain unauthorized access;
- harvest credentials or conduct social engineering;
- disrupt services or run uncontrolled scanning;
- bypass payment, legal, compliance, or approval processes for personal benefit;
- modify external production-like systems;
- publicly disclose the issue before coordination;
- copy confidential biological, specimen, sequence, partner, or unpublished data;
- execute high-risk biological procedures;
- perform autonomous wet-lab actions;
- use a vulnerability for financial, competitive, operational, or research advantage.

Good-faith, non-destructive reporting is appreciated. This policy does not grant authorization, legal immunity, a promise not to pursue remedies, or permission to violate applicable law or third-party terms.

## Maintainer Response Process

Maintainers should use the following public-safe process:

```text
report received
-> confidentiality and exposure check
-> acknowledgment
-> reproduction and triage
-> severity and affected-scope assessment
-> containment and credential rotation when needed
-> smallest safe remediation
-> regression and adversarial tests
-> exact-head CI and security validation
-> advisory / CVE / disclosure decision
-> coordinated publication
-> incident and decision learn-back
```

Reports are reviewed as promptly as practical. Confirmed critical exposure receives priority. No fixed acknowledgment, remediation, or disclosure deadline is guaranteed by this policy.

### Severity assessment

Severity considers:

- exploitability and reproducibility;
- required permissions and user interaction;
- confidentiality, integrity, and availability impact;
- secret or credential exposure;
- network or external side effects;
- public, private, confidential, or protected data impact;
- approval, sandbox, or agency bypass;
- supply-chain blast radius;
- biological and compliance human-gate impact;
- production relevance and actual deployment status;
- availability of containment and rollback.

Suggested categories are Critical, High, Medium, Low, and Informational. CVSS may be used as supporting input, but repository-specific impact and actual deployment evidence remain authoritative.

## AI and Agent Security Principles

- Retrieved or external content is data, not authority.
- Untrusted text must not be inserted into privileged system or developer instructions.
- Structured schemas and validated fields should constrain data flow between components.
- Model output must not directly authorize privileged, destructive, external, legal, compliance, biological, or release actions.
- Sensitive tool calls require explicit human approval.
- Unknown tools, connectors, plugins, skills, and MCP servers fail closed.
- Filesystem, network, Git, provider, and external-system permissions follow least privilege.
- Public, private-development, confidential, and protected contexts remain separated.
- Agent memory must not silently promote untrusted content into policy or trusted facts.
- Multi-agent workflows require explicit trust, authority, handoff, and state-consistency boundaries.
- Retries and resumes must avoid duplicated side effects.
- Security controls require deterministic tests, adversarial evaluations, traceability, and review; prompt wording alone is not a sufficient control.
- Human approval remains mandatory for destructive, external, production, legal, compliance, biological, and wet-lab actions.

## RAG and Data-Security Principles

- Register and classify sources before ingestion.
- Validate provenance, confidentiality, licensing, verification status, ownership, and `allowed_use`.
- Preserve stable source IDs, evidence labels, evidence spans, and compliance tags throughout retrieval and reranking.
- Treat document content, metadata, citations, and embedded instructions as untrusted input.
- Blocked or revoked sources fail closed and must not silently re-enter indexes or caches.
- Unsupported claims remain unsupported.
- Citations must resolve to actual evidence spans.
- Public development fixtures are not protected evidence or generalization proof.
- Protected holdout data must not be committed publicly.
- Answer-key, expected-answer, rationale, and oracle fields must not influence runtime ranking or answer behavior.
- Indexes, caches, logs, traces, and derived artifacts inherit the confidentiality of their source material.
- Deletion and revocation should propagate to derived artifacts where the architecture supports it.
- Retrieval, reranking, generation, and verification changes require regression evidence and rollback.

## Software Supply-Chain Policy

Changes that add or modify dependencies, GitHub Actions, plugins, MCP servers, external models, parsers, binaries, or generated artifacts require explicit review of:

- source and maintainer trust;
- license compatibility and permitted use;
- known vulnerabilities and advisories;
- dependency confusion and package-name risk;
- direct and transitive dependencies;
- version pinning or justified version bounds;
- lockfile or resolved-artifact integrity;
- install-time scripts and network behavior;
- workflow permissions and third-party Action trust;
- artifact provenance and reproducibility;
- secret and environment-variable exposure;
- rollback and removal path;
- targeted security and regression checks.

Do not install missing MCP, plugin, skill, model, or package dependencies implicitly in a security-sensitive workflow.

This policy does not claim that SBOM generation, artifact signing, SLSA provenance, Dependabot, CodeQL, secret scanning, or push protection are enabled unless repository or GitHub settings evidence confirms them.

## Secret and Credential Handling

- Never commit secrets, tokens, credentials, cookies, private keys, or recovery codes.
- Do not place secrets in prompts, fixtures, screenshots, logs, traces, issues, PRs, or generated artifacts.
- Use environment variables or an owner-approved secret store.
- Grant AI tools and connectors only the credentials required for the immediate task.
- Redact diagnostics before sharing them.
- If exposure is suspected, revoke or rotate the credential; deleting it from a file is not sufficient.
- Treat Git history, workflow logs, caches, artifacts, indexes, and backups as potential exposure surfaces.
- Review MCP and connector credential scope and data transmission before use.

## Biological and Compliance Human Gates

The following are not autonomous approval domains:

- CITES;
- Nagoya Protocol and access-and-benefit sharing;
- LMO/GMO;
- biosafety and biosecurity;
- genetic resources;
- species, sample, specimen, assay, and sequence rights;
- IP and licensing;
- export control;
- personal or protected data;
- partner confidentiality;
- unpublished results;
- investor or public communication;
- production release;
- wet-lab execution.

An AI model, evaluator, retrieval result, score, report, or agent does not grant approval in these domains.

High-risk wet-lab automation, pathogenic enhancement, regulatory evasion, unauthorized genetic-resource use, or unreviewed external biological action must be blocked or reduced to a safe, high-level alternative and escalated to qualified human review.

## Current Security Controls and Evidence Boundary

The repository currently contains public policy, coding-agent rules, source-registry validation, targeted and regression tests, artifact verification, retrieval evaluation, CI, Quality Gates, and human-review requirements.

| Control | Current statement |
|---|---|
| `SECURITY.md` policy | Implemented as repository policy after merge |
| Agent security rules | Present in `AGENTS.md`; effectiveness depends on implementation and review |
| CI and Quality Gates | Repository workflows exist and validate defined changed surfaces |
| Source-registry contract validation | Implemented in repository code and CI |
| Artifact verification and retrieval evaluation | Implemented for development evidence |
| Public-safe biology/compliance fixtures | Synthetic development evidence only |
| Prompt-injection and adversarial coverage | Partial repository controls; not a complete security guarantee |
| Private Vulnerability Reporting | **VERIFY_BEFORE_PUBLISHING** |
| Dependabot configuration | Not confirmed |
| CodeQL configuration | Not confirmed |
| Secret scanning and push protection | Repository setting not confirmed |
| SBOM, signing, and SLSA provenance | Not confirmed |
| Production monitoring and incident operations | Not confirmed |
| Legal, regulatory, biosafety, IP, or wet-lab approval | Not granted by this repository |

Passing tests or CI does not prove the absence of vulnerabilities.

## Security Validation and Release Gates

Security-sensitive changes should use the smallest sufficient implementation and risk-based validation.

Depending on the changed surface, evidence may include:

- targeted unit and regression tests;
- prompt-injection, source-poisoning, secret-leakage, provenance, and excessive-agency tests;
- schema and structured-output validation;
- source-registry and metadata-preservation checks;
- artifact verification;
- dependency, license, workflow-permission, and configuration review;
- retrieval and reranking evaluations;
- clean-environment GitHub Actions;
- exact-head CI and Quality Gates;
- human security, compliance, and release review;
- documented rollback and incident containment.

Controls must be labeled accurately as implemented, CI-enforced, manually reviewed, planned, unavailable, or not independently verified.

Security-relevant fixes should add a regression test, adversarial case, guardrail, schema rule, decision record, runbook update, or durable workflow improvement when appropriate.

## Disclosure and Advisory Policy

- Coordinated disclosure is preferred.
- Public disclosure timing should be agreed with maintainers after affected users, dependencies, and remediation status are understood.
- A GitHub repository security advisory may be used for confirmed repository vulnerabilities.
- A CVE request depends on confirmed impact, affected distribution, and project eligibility.
- Fixes should include regression evidence and exact-head validation when practical.
- Reporter credit is optional and requires reporter consent.
- Anonymity preferences are respected where practical.
- This project does not currently advertise a bug-bounty program.
- No payment, reward, or reimbursement is implied.

## Security Contact and Escalation

**VERIFY_BEFORE_PUBLISHING:** Enable GitHub Private Vulnerability Reporting or publish an owner-approved private security contact before this policy is treated as a complete reporting route.

Do not add a personal phone number, private messenger account, or unapproved email address to this file.

For non-sensitive bugs, documentation issues, and feature requests, use normal GitHub issue workflows. Sensitive findings must remain private.

## Policy Limitations

- This policy is operational guidance, not legal advice.
- No control guarantees that the repository is free of vulnerabilities.
- Prompt-injection defenses reduce risk but do not eliminate it.
- Evaluator, model, or agent output does not grant legal, regulatory, compliance, biosafety, biosecurity, IP, public-communication, release, or wet-lab approval.
- Third-party providers, tools, models, packages, and services have separate security policies.
- Repository support scope may change with releases and architecture.
- Roadmaps, prompts, fixtures, schemas, or documentation are not proof of production security or deployment.
- This repository does not claim production RAG, production vector DB or KG, protected-holdout generalization, production tracing, autonomous laboratory execution, production readiness, or proprietary biological foundation-model capability.

## Related Repository Policies

- [README](README.md)
- [Agent Constitution](AGENTS.md)
- [Human + Codex Workflow](docs/WORKFLOW.md)
- [Quality Gates](docs/QUALITY_GATES.md)
- [Current State and Performance Roadmap](docs/CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md)
