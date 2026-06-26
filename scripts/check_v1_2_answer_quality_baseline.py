from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUBRIC_PATH = REPO_ROOT / "docs" / "evals" / "V1_2_ANSWER_QUALITY_RUBRIC.md"
TAXONOMY_PATH = REPO_ROOT / "docs" / "evals" / "V1_2_FAILURE_TAXONOMY.md"
FIXTURE_PATH = REPO_ROOT / "docs" / "evals" / "V1_2_GOLDEN_EVAL_SET.json"

RUBRIC_TERMS = (
    "source grounding",
    "citation accuracy",
    "retrieval fit",
    "usefulness",
    "truth-boundary",
    "compliance",
    "biosafety",
    "legal",
    "scalability",
    "moat",
)

FAILURE_CATEGORIES = (
    "no_weak_source",
    "wrong_source",
    "overclaim",
    "missing_compliance_gate",
    "vague_answer",
    "wrong_source_priority",
    "retrieval_miss",
    "citation_mismatch",
    "unsafe_externalization",
    "not_actionable",
)

EXPECTED_DIMENSIONS = (
    "source_grounding",
    "citation_accuracy",
    "retrieval_fit",
    "usefulness_actionability",
    "truth_boundary_discipline",
    "compliance_biosafety_legal_gate_handling",
    "strategic_fit_scalability",
    "strategic_fit_moat",
    "strategic_fit_biosafety_compliance",
)

FORBIDDEN_OVERCLAIM_PATTERNS = (
    re.compile(r"\bproduction[- ]ready\b", re.IGNORECASE),
    re.compile(r"\bvalidated biological model\b", re.IGNORECASE),
    re.compile(r"\bregulatory approval\b", re.IGNORECASE),
    re.compile(r"\blegal approval\b", re.IGNORECASE),
    re.compile(r"\bautonomous wet[- ]lab\b", re.IGNORECASE),
    re.compile(r"\bcustomer traction\b", re.IGNORECASE),
)

BOUNDARY_TERMS = (
    "not",
    "no ",
    "without",
    "does not",
    "do not",
    "must not",
    "unless",
    "should not",
    "cannot",
    "do-not",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _repo_relative(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def validate_fixture(payload: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["fixture must be a JSON object"]
    if payload.get("schema_version") != "v1.2-answer-quality-baseline":
        errors.append("fixture schema_version must be v1.2-answer-quality-baseline")
    if payload.get("measurement_only") is not True:
        errors.append("fixture measurement_only must be true")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        return errors + ["fixture cases must be a non-empty list"]
    seen_ids: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"case {index} must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"case {index} id must be a non-empty string")
        elif case_id in seen_ids:
            errors.append(f"duplicate case id: {case_id}")
        else:
            seen_ids.add(case_id)
        if not isinstance(case.get("question"), str) or not case["question"].strip():
            errors.append(f"case {case_id or index} question must be a non-empty string")
        source_scope = case.get("source_scope")
        if not isinstance(source_scope, list) or not source_scope:
            errors.append(f"case {case_id or index} source_scope must be a non-empty list")
        elif any(not isinstance(item, str) or not item.strip() for item in source_scope):
            errors.append(f"case {case_id or index} source_scope entries must be non-empty strings")
        dimensions = case.get("expected_rubric_dimensions")
        if dimensions != list(EXPECTED_DIMENSIONS):
            errors.append(f"case {case_id or index} expected_rubric_dimensions must match V1.2 rubric dimensions")
        if not isinstance(case.get("expected_truth_boundary"), str) or not case["expected_truth_boundary"].strip():
            errors.append(f"case {case_id or index} expected_truth_boundary must be a non-empty string")
        gates = case.get("required_compliance_gates")
        if not isinstance(gates, list) or not gates:
            errors.append(f"case {case_id or index} required_compliance_gates must be a non-empty list")
        watched = case.get("failure_categories_to_watch")
        if not isinstance(watched, list) or not watched:
            errors.append(f"case {case_id or index} failure_categories_to_watch must be a non-empty list")
        elif any(category not in FAILURE_CATEGORIES for category in watched):
            errors.append(f"case {case_id or index} has unknown failure_categories_to_watch entry")
    return errors


def validate_baseline(repo_root: Path = REPO_ROOT) -> dict[str, object]:
    paths = {
        "rubric": repo_root / "docs" / "evals" / "V1_2_ANSWER_QUALITY_RUBRIC.md",
        "taxonomy": repo_root / "docs" / "evals" / "V1_2_FAILURE_TAXONOMY.md",
        "fixture": repo_root / "docs" / "evals" / "V1_2_GOLDEN_EVAL_SET.json",
    }
    errors: list[str] = []
    for label, path in paths.items():
        if not path.exists():
            errors.append(f"{label} missing: {_repo_relative(path, repo_root)}")
    if errors:
        return {"ok": False, "errors": errors}

    rubric_text = _read_text(paths["rubric"])
    taxonomy_text = _read_text(paths["taxonomy"])
    combined_eval_docs = f"{rubric_text}\n{taxonomy_text}"
    lower_combined = combined_eval_docs.lower()

    for term in RUBRIC_TERMS:
        if term not in lower_combined:
            errors.append(f"rubric/taxonomy missing required term: {term}")
    for category in FAILURE_CATEGORIES:
        if category not in taxonomy_text:
            errors.append(f"failure taxonomy missing category: {category}")
    if "truth-boundary" not in lower_combined:
        errors.append("eval docs must reference truth-boundary")
    if "compliance gate" not in lower_combined and "compliance gates" not in lower_combined:
        errors.append("eval docs must reference compliance gates")

    for path in paths.values():
        for line_number, line in enumerate(_read_text(path).splitlines(), start=1):
            line_lower = line.lower()
            for pattern in FORBIDDEN_OVERCLAIM_PATTERNS:
                if pattern.search(line) and not any(term in line_lower for term in BOUNDARY_TERMS):
                    errors.append(
                        "forbidden production overclaim pattern in "
                        f"{_repo_relative(path, repo_root)}:{line_number}: {pattern.pattern}"
                    )

    try:
        fixture_payload = json.loads(_read_text(paths["fixture"]))
    except json.JSONDecodeError as exc:
        errors.append(f"fixture JSON invalid: {exc}")
    else:
        errors.extend(validate_fixture(fixture_payload))

    return {
        "ok": not errors,
        "errors": errors,
        "checked_files": {label: _repo_relative(path, repo_root) for label, path in paths.items()},
        "failure_categories": list(FAILURE_CATEGORIES),
        "rubric_dimensions": list(EXPECTED_DIMENSIONS),
    }


def main() -> int:
    result = validate_baseline()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
