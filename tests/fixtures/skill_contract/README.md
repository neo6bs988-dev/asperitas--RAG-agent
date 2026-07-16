# Skill Contract v2 fixtures

P1B-1 fixture contracts are created in pytest temporary directories so each test can isolate one invariant without
adding manifests to the 30 current skills. A strict fixture directory contains `SKILL.md` and
`skill.contract.json`. The tests cover canonical-schema structure, identity, aliases, permissions, lifecycle,
host-independent path safety, verification, and transition behavior. The schema subset fails closed on missing,
malformed, externally referenced, or unsupported schema constructs; semantic checks are additive.

Schema definitions are validated before contracts. Supported keyword names and value shapes must be valid;
malformed values produce deterministic `SCHEMA_*` findings. Patterns use a bounded Python-regex subset rather
than complete ECMA-262 semantics. Boolean schema nodes, schema-valued `additionalProperties`, `$ref` siblings,
reference cycles, and external schema loading are unsupported and fail closed.

Lifecycle and alias dates use normalized RFC 3339 full dates (`YYYY-MM-DD`). Deprecated successors and alias
replacements resolve to a different active or planned canonical contract in the validated set. Only
`deprecated_skill_id` aliases are supported. Every high-risk execution/write declaration requires a non-empty
human gate without keyword inference. A declaration never grants runtime authority.

`--transition` exit code 0 means the audit completed, not that migration passed: consumers must inspect `state`
and `ok`. The current no-manifest inventory remains `PARTIAL` with `ok=false`. Production-like contracts and
P1B-2 are intentionally blocked pending exact-head recertification and independent reaudit.
