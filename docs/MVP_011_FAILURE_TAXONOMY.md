# MVP-011 Failure Analysis / Error Taxonomy

## Purpose

MVP-011 adds deterministic failure-category metadata to the local Asperitas agent evaluation stack. MVP-009 and MVP-010 already decide whether evaluations pass or fail; MVP-011 classifies why a failure happened so regressions can be triaged quickly.

## Scope

MVP-011 covers evaluation result objects from:

- `scripts/evaluate_agent.py`
- `scripts/run_golden_agent_eval.py`

It introduces:

- `src/asperitas_agent/failure_taxonomy.py`
- `tests/test_failure_taxonomy.py`
- additive `failure_category` metadata for failed case reports

## Non-Goals

- No retrieval ranking changes.
- No guardrail weakening.
- No answer-generation changes.
- No benchmark manipulation.
- No ingestion rerun.
- No external APIs, LLM APIs, embeddings, vector DB, UI, or web server.

## Categories

The stable categories are:

1. `protected_file_mutation`
2. `forbidden_dependency_failure`
3. `anti_cheating_failure`
4. `determinism_failure`
5. `schema_failure`
6. `status_mismatch`
7. `guardrail_mismatch`
8. `citation_integrity_failure`
9. `evidence_count_failure`
10. `retrieval_regression_failure`
11. `required_substring_missing`
12. `forbidden_substring_present`
13. `source_priority_failure`
14. `evidence_label_failure`
15. `unknown_failure`

## Priority Order

The classifier uses the category order above as deterministic first-match priority. This means a protected-file mutation takes precedence over a status mismatch, and anti-cheating or forbidden-dependency failures take precedence over ordinary answer-quality failures.

## Trigger Definitions

- `schema_failure`: schema check failed, required fields are missing, or validation reports wrong field types.
- `status_mismatch`: actual status differs from expected status.
- `guardrail_mismatch`: expected guardrail decision, caution, or abstention behavior is not preserved.
- `citation_integrity_failure`: malformed, dangling, or unsupported citations appear.
- `evidence_count_failure`: evidence count is below the expected minimum.
- `retrieval_regression_failure`: retrieval regression check fails or metrics fall below thresholds.
- `protected_file_mutation`: protected source, registry, benchmark, or artifact hashes changed.
- `determinism_failure`: repeated deterministic runs differ.
- `forbidden_dependency_failure`: static scan finds forbidden API, dependency, vector DB, UI, or web-server references.
- `anti_cheating_failure`: static scan finds benchmark leakage, pytest/CI switching, or query special-casing risk.
- `required_substring_missing`: a required answer concept is absent.
- `forbidden_substring_present`: a forbidden answer claim appears.
- `source_priority_failure`: required source priority constraints fail.
- `evidence_label_failure`: required evidence labels are missing.
- `unknown_failure`: the result failed but no known category matched.

## Integration Points

`scripts/evaluate_agent.py` attaches `failure_category` only to failed MVP-009 case reports.

`scripts/run_golden_agent_eval.py` attaches `failure_category` only to failed MVP-010 golden case reports.

Top-level pass/fail behavior remains unchanged:

- `ok`
- `total_cases`
- `passed_cases`
- `failed_cases`
- exit codes
- thresholds
- protected file hash behavior

## Anti-Cheating Safeguards

- Runtime agent code must not detect golden query ids, exact query text, pytest, CI, benchmark filenames, or test filenames to change behavior.
- The taxonomy module classifies evaluation result dictionaries only.
- It does not read `eval/golden_agent_queries.jsonl` or benchmark answer files.
- It does not alter retrieval, answer generation, guardrails, chunks, registry, or source data.

## Determinism Safeguards

- Classification is pure and deterministic.
- It does not use randomness, timestamps, environment variables, network calls, or machine-specific paths.
- It prefers structured check fields over string parsing.
- It falls back to failure text only when structured fields are unavailable.

## Validation Commands

```powershell
python -m pytest
python scripts/verify_artifacts.py
python scripts/evaluate_agent.py
python scripts/run_golden_agent_eval.py
```

## Expected Behavior

Existing PASS/FAIL behavior is unchanged. Failure category is additive report metadata only, emitted for failed cases so future failures can be grouped without changing evaluation semantics.
