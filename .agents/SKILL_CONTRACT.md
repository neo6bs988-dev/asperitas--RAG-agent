# Asperitas Skill Contract v2

Status: P1B-1 foundation; transition audit only

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

## Canonical identity

Each canonical skill has exactly one directory, one `SKILL.md` frontmatter name, one `skill.contract.json`, and one
`skill_id`. The directory and frontmatter name must match. The `skill_id` is the deterministic conversion of the
hyphenated name to underscores. Compatibility aliases never satisfy canonical file existence.

## Lifecycle and aliases

Lifecycle states are `active`, `planned`, `deprecated`, `blocked`, and `unregistered_review_required`.
Deprecated skills require either `replaced_by` or a terminal rationale. Deprecated aliases require an expiry in
`compatibility_until`. Aliases are globally unique, cannot equal a canonical ID or frontmatter name, and cannot
form cycles. An unregistered skill is review-only and must set `routing.implicit_activation` to `false`.

## Routing and explicit-only policy

`routing.implicit_activation` declares whether description-based selection is intended. `false` means the skill
is explicit-only. Positive and negative triggers, conflicts, and precedence rules are routing declarations; they
do not modify the current Codex catalog or incumbent Python routing in P1B-1.

## Modes, permissions, and human gates

Supported modes are `READ`, `DRAFT`, and `WRITE`. `WRITE` requires both `write_allowed=true` and
`approval_required=true`. Network or external-call declarations require approval. Destructive actions are blocked
by default. High-risk execution or writing, especially biological or wet-lab activity, requires explicit human
gates and remains subject to repository policy.

A contract declaration does not grant shell, network, connector, write, ingestion, destructive, or biological
execution authority. Runtime authorization must be enforced separately. Legal, regulatory, rights, biosafety,
biosecurity, scientific, release, and external-communication approvals remain human gates.

## Verification and rollback

Active contracts declare at least one verification command. Commands are data: the validator never executes them.
Fixture/resource paths must remain relative to the skill directory. Every contract declares a rollback strategy
and rollback verification.

## Migration stages

1. **P1B-1 foundation:** add the schema, deterministic validator, strict fixture tests, and a transition audit.
   Existing skills remain unchanged and the repository reports `PARTIAL` because manifests are absent.
2. **P1B-2 manifests:** add reviewed contracts to existing skills without renaming or changing routing.
3. **Later migration:** freeze routing evaluations before changing aliases, descriptions, identities, or lifecycle.
4. **Enforcement:** replace the incumbent gate only after exact-head tests, routing evaluations, and human review.

## Non-claims

Documented does not mean implemented, enforced, tested in production, approved, deployed, or production-ready.
Contract validation does not establish legal, regulatory, rights, biosafety, scientific, security, or release
approval. Public benchmarks and external skill behavior are not evidence of Asperitas performance.
