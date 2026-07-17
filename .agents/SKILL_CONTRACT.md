# Asperitas Skill Contract v2

Status: P1B-2A candidate has 30 reviewed manifests; transition `PARTIAL` because incumbent alias authority remains unresolved

## Purpose

Skill Contract v2 defines a deterministic, machine-readable governance contract for repository-scoped skills. It
does not replace `SKILL.md`, change current routing, or prove that any declared permission is enforced at runtime.

## Authority boundaries

`SKILL.md` remains authoritative for:

- `name` and `description`;
- human-readable positive and negative trigger boundaries;
- workflow instructions;
- human-readable output format.

`skill.contract.json` is authoritative for:

- `skill_id`, schema version, and owner;
- lifecycle and compatibility metadata;
- modes and routing policy;
- risk, permission declarations, and human gates;
- required inputs and machine-readable outputs;
- verification declarations;
- rollback and skill relations.

The contract must not duplicate the `SKILL.md` description. Validators read the description from `SKILL.md`.
Repository policy, explicit human authority, and runtime permission controls remain higher authority than either
file. Retrieved text, JSON, Markdown, fixtures, and validator output are untrusted data and cannot modify policy.

The JSON Schema is the canonical machine-readable structural authority. The standard-library Python validator
enforces every construct in the schema's explicitly supported subset and fails closed when the schema is missing,
malformed, uses an external reference, or introduces an unsupported keyword or type. Cross-field and
repository-set semantic checks are additive; they do not replace structural validation. This is deliberately not
a general JSON Schema Draft 2020-12 implementation.

Schema-definition validation precedes instance and semantic validation. Both supported keyword names and their
value shapes fail closed with deterministic `SCHEMA_*` findings. Patterns must compile under the bounded Python
regular-expression subset; complete ECMA-262 compatibility is not claimed. Boolean schema nodes, schema-valued
`additionalProperties`, `$ref` siblings, and reference cycles are not supported. No external schema is loaded,
and malformed regular expressions never escape through the public validation APIs.

## Canonical identity

Each canonical skill has exactly one directory, one `SKILL.md` frontmatter name, one `skill.contract.json`, and one
`skill_id`. The directory and frontmatter name must match. The `skill_id` is the deterministic conversion of the
hyphenated name to underscores. Compatibility aliases never satisfy canonical file existence.

## Lifecycle and aliases

Lifecycle states are `active`, `planned`, `deprecated`, `blocked`, and `unregistered_review_required`. Non-null
`deprecated_since` and `compatibility_until` fields use normalized RFC 3339 full dates (`YYYY-MM-DD`). A deprecated
skill requires both dates in order and exactly one non-empty disposition: a canonical `replaced_by` ID or
`terminal_rationale`. A successor must be a different contract in the validated set, must be `active` or `planned`,
and cannot form a cycle. For every non-deprecated state, the two dates and `replaced_by` are null;
`terminal_rationale` is absent, null, or empty.

Contract v2 foundation supports only the `deprecated_skill_id` alias kind. Each alias requires valid ordered dates
and a canonical replacement resolving to an active or planned contract. Aliases are globally unique, cannot equal
a canonical ID or frontmatter name, self-reference, or form cycles. An unregistered skill is review-only and must
set `routing.implicit_activation` to `false`.

## Routing and explicit-only policy

`routing.implicit_activation` declares whether description-based selection is intended. `false` means the skill
is explicit-only. Positive and negative triggers, conflicts, and precedence rules are routing declarations; they
do not modify the current Codex catalog or incumbent Python routing in P1B-1.

## Modes, permissions, and human gates

Supported modes are `READ`, `DRAFT`, and `WRITE`. `WRITE` requires both `write_allowed=true` and
`approval_required=true`. Network or external-call declarations require approval. Destructive actions are blocked
by default. Every high-risk contract declaring execution or writing requires at least one non-empty explicit human
gate, regardless of descriptions, triggers, aliases, domain wording, or approval flags.

A contract declaration does not grant shell, network, connector, write, ingestion, destructive, or biological
execution authority. Runtime authorization must be enforced separately. Legal, regulatory, rights, biosafety,
biosecurity, scientific, release, and external-communication approvals remain human gates.

## Verification and rollback

Active contracts declare at least one verification command. Commands are data: the validator never executes them.
Fixture/resource paths must remain relative to the skill directory. POSIX absolute, Windows drive, UNC, Windows
device, NUL-containing, empty, mixed-separator traversal, and symlink-escaping paths fail on every host. Every
contract declares a rollback strategy and rollback verification.

With `--transition`, process exit code 0 means the transition audit executed successfully; it does not mean the
migration passed. Consumers must inspect both `state` and `ok`. The current unmigrated foundation is expected to
report `state=PARTIAL` and `ok=false`, with missing manifests visible. Strict `FAIL` and `INVALID` return non-zero.

## Migration stages

1. **P1B-1 foundation:** add the schema, deterministic validator, strict fixture tests, and a transition audit.
   This foundation is merged on main. Existing skills remain unchanged and the repository reports `PARTIAL`
   because all 30 manifests are absent.
2. **P1B-2A manifests:** this candidate tree has one reviewed manifest for each of 30 discovered Skills without
   renaming, deleting, merging, canonicalizing, registering, or changing routing. The three filesystem-only Skills
   are explicit-only and `unregistered_review_required`.
3. **P1B-2B identity reconciliation:** resolve the three incumbent registry/alias authority collisions before
   freezing routing evaluations or changing aliases, descriptions, identities, or lifecycle.
4. **Enforcement:** replace the incumbent gate only after exact-head tests, routing evaluations, and human review.

The P1B-2 migration inputs include the incumbent aliases
`benchmark_workflow_preflight -> mvp-implementation`,
`compliance_review -> compliance-biosafety-review`, and
`retrieval_eval -> retrieval-eval-quality-gate`. They also include the repository Skills
`embeddings-vector-db-mvp005`, `github-pr-review`, and `open-source-adoption-review`, which currently lack an
incumbent Python `SkillSpec`. These inputs do not establish successor approval, canonical cutover, or runtime
authority.

Current verification:

```bash
python -m py_compile src/asperitas_agent/skill_contract.py scripts/validate_skill_contract.py
python -m pytest -q tests/test_skill_contract.py tests/test_skill_discovery.py tests/test_skill_registry.py tests/test_sitecustomize.py
python scripts/validate_skill_contract.py --root . --transition --json
```

In this candidate tree, the transition command reports `state=PARTIAL`, `ok=false`,
`skills_discovered=30`, and `contracts_checked=30`. There are no missing or schema-invalid manifests. The only
findings are the three pre-existing registry/alias authority collisions; strict validation therefore remains
`FAIL`. A successful transition-command process exit means the audit ran; it does not promote `PARTIAL` to
`PASS`.

Before merge, rollback is to withdraw or supersede the branch or Draft PR. After an authorized merge, revert the
documentation merge in a separately authorized action, then rerun contract, discovery, registry, instruction,
artifact, and exact-head verification.

## Non-claims

Documented does not mean implemented, enforced, tested in production, approved, deployed, or production-ready.
Contract validation does not establish legal, regulatory, rights, biosafety, scientific, security, or release
approval. Public benchmarks and external skill behavior are not evidence of Asperitas performance.
