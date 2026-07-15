# Skill Contract v2 fixtures

P1B-1 fixture contracts are created in pytest temporary directories so each test can isolate one invariant without
adding manifests to the 30 current skills. A strict fixture directory contains `SKILL.md` and
`skill.contract.json`. The tests cover identity, aliases, permissions, lifecycle, path safety, verification, and
transition behavior. Production-like contracts are intentionally deferred to P1B-2.
