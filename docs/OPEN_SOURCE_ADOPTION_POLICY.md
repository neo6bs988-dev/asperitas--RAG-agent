# Open Source Adoption Policy

Status: repository governance
Scope: public GitHub repositories, official documentation, dependencies, code snippets, skills, workflows, and reference implementations

## Executive Bottom Line

Asperitas may learn from high-quality public open-source projects and official documentation, but must not copy, depend on, ingest, or operationalize external assets without provenance, license, security, and evaluation review.

The default adoption mode is:

```text
Scout -> Metadata -> License Review -> Security Review -> Local Minimal Adaptation -> Tests/Eval -> Decision Log -> PR
```

## Source Priority

Prefer:

1. official documentation;
2. official GitHub repositories;
3. peer-reviewed or review-needed research papers;
4. mature open-source projects with clear license, active maintenance, tests, and security posture.

Avoid production ingestion or direct adoption of:

- unofficial blogs;
- social posts;
- newsletters;
- copied tutorials;
- unclear-license snippets;
- abandoned repositories;
- repositories that require broad secrets, tokens, or external access;
- unreviewed agent skills or prompt packages.

## Intake Record

Every candidate should be recorded with:

```json
{
  "source_title": "",
  "source_url": "",
  "source_type": "official_docs | official_github_repo | research_paper_review_needed | open_source_project",
  "publisher_or_org": "",
  "version_or_date": "",
  "retrieved_date": "",
  "license": "unknown | review_needed | permissive | restrictive | incompatible",
  "maintenance_status": "unknown | active | stale | archived",
  "security_status": "unknown | review_needed | acceptable | blocked",
  "intended_use": "architecture_reference | implementation_reference | evaluation_reference | security_reference",
  "production_ingestion_allowed": false,
  "copy_code_allowed": false,
  "dependency_allowed": false,
  "notes": ""
}
```

## Adoption Levels

| Level | Meaning | Default for V1 |
| --- | --- | --- |
| L0 Metadata only | record title, URL, type, date, summary, patterns | allowed |
| L1 Architecture reference | use concepts without copying code | allowed after review |
| L2 Local minimal adaptation | implement equivalent local pattern with tests | allowed when scoped |
| L3 Dependency adoption | add package/dependency | requires security/license review |
| L4 Source ingestion | ingest content into KB | requires license/provenance approval |
| L5 External connector | tool/API/MCP integration | V1.1+ only unless explicitly approved |

## Required Reviews

### License Review

Check:

- license exists;
- license permits intended use;
- NOTICE/attribution requirements;
- copyleft or commercial restrictions;
- whether copied code, dependency use, documentation summarization, or data ingestion is allowed.

### Security Review

Check:

- dependency risk;
- maintainer status;
- known vulnerabilities;
- GitHub Actions permissions;
- secret handling;
- network behavior;
- tool execution behavior;
- prompt-injection or skill-instruction risk.

### Evaluation Review

For any change affecting retrieval, answer generation, eval fixtures, embeddings, vector DB, reranking, or default behavior, run before/after evals and record regressions.

## Agent Skill Review

Treat every third-party `SKILL.md` as operational text, not passive documentation.

Before importing or adapting a skill:

- inspect frontmatter and description;
- check whether it grants or assumes tool access;
- remove broad or hidden execution permissions;
- keep skill body concise;
- make unsafe operations fail closed;
- do not adopt external scripts without code review.

## Prohibited Shortcuts

Do not:

- copy-paste external code without license/security review;
- add dependencies because a benchmark project uses them;
- turn on external connectors without human approval;
- ingest full docs or papers because they are useful;
- allow untrusted source text to override AGENTS.md or system policy;
- claim an external benchmark result as Asperitas performance.

## Decision Log Requirement

A decision log is required when:

- a new dependency is added;
- an external project pattern is adopted;
- a public source moves from metadata-only to ingestion candidate;
- security posture changes;
- CI/CD behavior changes;
- retrieval/eval/default behavior changes.
