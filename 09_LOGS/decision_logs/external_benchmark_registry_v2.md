# External Benchmark Registry v2 Decision Log

## Decision status

- Status: `PLANNED / IMPLEMENTED ON BRANCH / NOT MERGED`
- Change class: `C2 — metadata-governance and validation change`
- Owner and approver: `Asperitas COO / AI Lead`
- Branch: `chore/external-benchmark-registry-v2`
- Base authority: current `main` at branch creation

## Goal

Create one metadata-only external benchmark candidate registry that aligns with the repository's current canonical metadata vocabulary and benchmark topology without acquiring, processing, embedding, indexing, evaluating, or promoting external source content.

## Baseline

The prior PRs `#99` and `#101` proposed useful registry scaffolds but were based on an old `main`, used a competing singular `P6_EXTERNAL_BENCHMARK/` path, and introduced metadata enums that diverged from `00_ADMIN/metadata_schema.yaml`.

The simplest safe alternative was to preserve the current `01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/` topology and add only:

- a CSV candidate registry;
- a machine-readable registry contract;
- a deterministic standard-library validator;
- focused tests.

## Scope

Added on the branch:

- `00_ADMIN/source_registries/external_benchmark_source_registry.csv`
- `00_ADMIN/source_registries/external_benchmark_source_registry.schema.json`
- `scripts/validate_external_benchmark_registry.py`
- `tests/test_external_benchmark_registry.py`
- this decision log

No existing source file, registry row, ingestion artifact, retrieval implementation, evaluation threshold, workflow, permission, or production configuration was changed.

## Truth boundary

The registry contains candidate metadata inherited from the current repository benchmark manifest. This change does not establish that:

- an external page or repository was freshly retrieved;
- a URL or current version was independently verified;
- license or terms review passed;
- raw content was acquired;
- content was processed or chunked;
- embeddings or vector records were generated;
- retrieval or answer-generation behavior changed;
- an evaluation passed;
- a named company practice is equivalent to Asperitas implementation;
- legal, scientific, biosafety, security, or production clearance exists.

Every candidate remains:

```text
verification_status = needs_external_verification
license_status = needs_review
ingestion_status = registered
version_or_date = unverified_current_version
```

## Key controls

1. Registry enums must remain subsets of `00_ADMIN/metadata_schema.yaml`.
2. Provenance must use `01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/`.
3. The legacy singular `P6_EXTERNAL_BENCHMARK/` path is rejected.
4. Source IDs and HTTPS URLs must be unique.
5. P5 is reserved for AI-bio platform benchmark candidates.
6. Unverified papers cannot claim peer review or scientific validation.
7. External content acquisition and downstream ingestion remain blocked pending separate review and approval.

## Verification plan

Run against the exact branch head:

```bash
python scripts/validate_external_benchmark_registry.py
python -m pytest -q tests/test_external_benchmark_registry.py
python -m pytest -q
python -m asperitas_agent.cli verify-artifacts
git diff --check
```

GitHub Actions `CI` and `Quality Gates` must pass on the exact PR head before merge readiness is claimed.

## Success criteria

- validator exits successfully with `record_count = 19`;
- focused tests pass;
- full regression suite passes;
- artifact verification passes;
- no non-canonical benchmark directory is added;
- no source is promoted beyond metadata-only candidate state;
- exact-head CI and Quality Gates pass.

## Failure modes and stop conditions

Stop or block merge when:

- canonical metadata enums cannot be resolved;
- any candidate uses a non-HTTPS or duplicate URL;
- license or verification state is promoted without evidence;
- a path creates a second benchmark authority;
- full tests or artifact verification regress;
- CI evidence is absent, stale, cancelled, or tied to a different SHA.

## Rollback

Close the replacement PR without merge or revert the branch commits. The change has no external side effect and does not alter `main` until explicitly merged.

## Follow-up gate

Fresh retrieval, source-by-source license review, raw acquisition, processing, indexing, or evaluation must be a separate scoped change with named approval, evidence, verification, and rollback.
