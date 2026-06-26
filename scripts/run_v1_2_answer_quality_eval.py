from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_v1_2_answer_quality_baseline import (  # noqa: E402
    EXPECTED_DIMENSIONS,
    FAILURE_CATEGORIES,
    validate_fixture,
)


SCHEMA_VERSION = "v1.2b-answer-quality-fixture-coverage"
DEFAULT_FIXTURE_PATH = REPO_ROOT / "docs" / "evals" / "V1_2_GOLDEN_EVAL_SET.json"
DEFAULT_OUTPUT_PATH = (
    REPO_ROOT / "eval_results" / "v1_2_answer_quality_baseline" / "baseline_fixture_coverage.json"
)
FIXTURE_COVERAGE_BASELINE = "fixture_coverage_baseline"
NOT_BEHAVIOR_SCORED = "not_yet_behavior_scored"
CREATED_AT_UTC = "1970-01-01T00:00:00Z"


def _repo_relative(path: Path, repo_root: Path = REPO_ROOT) -> str:
    return path.relative_to(repo_root).as_posix() if path.is_relative_to(repo_root) else path.as_posix()


def load_fixture(path: Path = DEFAULT_FIXTURE_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"fixture not found: {_repo_relative(path)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_fixture(payload)
    if errors:
        raise ValueError("; ".join(errors))
    return payload


def build_case_record(case: dict[str, Any]) -> dict[str, Any]:
    dimensions = list(case["expected_rubric_dimensions"])
    gates = list(case["required_compliance_gates"])
    watched = list(case["failure_categories_to_watch"])
    return {
        "id": case["id"],
        "question": case["question"],
        "source_scope": list(case["source_scope"]),
        "required_rubric_dimensions": dimensions,
        "required_compliance_gates": gates,
        "failure_categories_to_watch": watched,
        "expected_truth_boundary": case["expected_truth_boundary"],
        "coverage_status": "covered_by_fixture",
        "behavior_score_status": NOT_BEHAVIOR_SCORED,
        "answer_output_present": False,
        "scores": None,
        "failure_category_observed": None,
        "coverage_checks": {
            "has_case_id": bool(case["id"]),
            "has_question": bool(case["question"].strip()),
            "has_source_scope": bool(case["source_scope"]),
            "has_all_required_dimensions": dimensions == list(EXPECTED_DIMENSIONS),
            "has_required_compliance_gates": bool(gates),
            "has_failure_categories_to_watch": bool(watched),
            "has_truth_boundary": bool(case["expected_truth_boundary"].strip()),
        },
    }


def validate_result_artifact(payload: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["result artifact must be a JSON object"]
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if payload.get("baseline_type") != FIXTURE_COVERAGE_BASELINE:
        errors.append(f"baseline_type must be {FIXTURE_COVERAGE_BASELINE}")
    if payload.get("measurement_only") is not True:
        errors.append("measurement_only must be true")
    if payload.get("answer_generation_executed") is not False:
        errors.append("answer_generation_executed must be false")
    if payload.get("retrieval_executed") is not False:
        errors.append("retrieval_executed must be false")
    if payload.get("model_outputs_present") is not False:
        errors.append("model_outputs_present must be false")
    if payload.get("behavior_score_status") != NOT_BEHAVIOR_SCORED:
        errors.append(f"behavior_score_status must be {NOT_BEHAVIOR_SCORED}")
    summary = payload.get("summary")
    cases = payload.get("cases")
    if not isinstance(summary, dict):
        errors.append("summary must be an object")
    if not isinstance(cases, list) or not cases:
        errors.append("cases must be a non-empty list")
        return errors
    case_ids: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"case {index} must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"case {index} id must be a non-empty string")
        elif case_id in case_ids:
            errors.append(f"duplicate case id: {case_id}")
        else:
            case_ids.add(case_id)
        if case.get("required_rubric_dimensions") != list(EXPECTED_DIMENSIONS):
            errors.append(f"case {case_id or index} required_rubric_dimensions must match V1.2 dimensions")
        watched = case.get("failure_categories_to_watch")
        if not isinstance(watched, list) or any(category not in FAILURE_CATEGORIES for category in watched):
            errors.append(f"case {case_id or index} failure_categories_to_watch contains an unknown category")
        if case.get("behavior_score_status") != NOT_BEHAVIOR_SCORED:
            errors.append(f"case {case_id or index} behavior_score_status must be {NOT_BEHAVIOR_SCORED}")
        if case.get("answer_output_present") is not False:
            errors.append(f"case {case_id or index} answer_output_present must be false")
        if case.get("scores") is not None:
            errors.append(f"case {case_id or index} scores must be null for fixture coverage baseline")
    if isinstance(summary, dict):
        if summary.get("case_count") != len(cases):
            errors.append("summary case_count must equal cases length")
        if summary.get("behavior_scored_case_count") != 0:
            errors.append("summary behavior_scored_case_count must be 0")
        if summary.get("fixture_covered_case_count") != len(cases):
            errors.append("summary fixture_covered_case_count must equal cases length")
    return errors


def build_fixture_coverage_result(fixture_path: Path = DEFAULT_FIXTURE_PATH) -> dict[str, Any]:
    fixture = load_fixture(fixture_path)
    cases = [build_case_record(case) for case in fixture["cases"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at_utc": CREATED_AT_UTC,
        "baseline_type": FIXTURE_COVERAGE_BASELINE,
        "behavior_score_status": NOT_BEHAVIOR_SCORED,
        "measurement_only": True,
        "answer_generation_executed": False,
        "retrieval_executed": False,
        "model_outputs_present": False,
        "scoreboard_path": "docs/evals/V1_2_BASELINE_SCOREBOARD.md",
        "fixture_path": _repo_relative(fixture_path),
        "rubric_path": "docs/evals/V1_2_ANSWER_QUALITY_RUBRIC.md",
        "taxonomy_path": "docs/evals/V1_2_FAILURE_TAXONOMY.md",
        "summary": {
            "case_count": len(cases),
            "fixture_covered_case_count": len(cases),
            "behavior_scored_case_count": 0,
            "required_rubric_dimensions": list(EXPECTED_DIMENSIONS),
            "failure_categories": list(FAILURE_CATEGORIES),
            "status": "fixture coverage baseline; actual answer-performance scoring not run",
            "v1_3_entry_criteria": [
                "stable answer outputs are captured without changing runtime behavior",
                "rubric scoring records are attached to answer outputs",
                "compliance gates and truth-boundary outcomes are reviewable per case",
                "failures are categorized using the V1.2 taxonomy",
            ],
        },
        "cases": cases,
        "non_mutation_statement": (
            "This artifact is generated from the V1.2 fixture only. It does not execute retrieval, "
            "ranking, embeddings, vector DB behavior, reranking, answer generation, source ingestion, "
            "registry mutation, chunk mutation, or model judging."
        ),
        "truth_boundary_statement": (
            "This is a fixture coverage baseline, not a model performance baseline. Scores remain null "
            "until actual answer outputs are available and reviewed."
        ),
    }


def write_result_artifact(payload: dict[str, Any], output_path: Path, overwrite: bool = False) -> Path:
    errors = validate_result_artifact(payload)
    if errors:
        raise ValueError("; ".join(errors))
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"output already exists: {_repo_relative(output_path)}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the V1.2B answer-quality fixture coverage baseline artifact.")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print the artifact JSON to stdout.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = build_fixture_coverage_result(args.fixture)
        write_result_artifact(result, args.output, overwrite=args.overwrite)
    except (FileNotFoundError, ValueError, FileExistsError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"ok: true")
        print(f"baseline_type: {result['baseline_type']}")
        print(f"behavior_score_status: {result['behavior_score_status']}")
        print(f"output: {_repo_relative(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
