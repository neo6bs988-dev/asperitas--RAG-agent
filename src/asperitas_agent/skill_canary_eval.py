from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from .skill_registry import DEFAULT_SKILL_REGISTRY
from .skill_routing_eval import (
    FIXTURE_VERSION as P1C1_FIXTURE_VERSION,
    RUNNER_FIELDS as P1C1_RUNNER_FIELDS,
    load_manifests,
)


CANARY_ID = "p1c-2-skill-canary-github-modes"
FIXTURE_VERSION = "p1c-2-skill-canary-v1"
RUNNER_VERSION = "1.0"
EXPECTED_BASE_SHA = "c9d1ec2f1cf43aa42db01d6e558748d338593aea"
EXPECTED_SURFACE_SHA256 = "621d83b05a238448bfb4966be1e1743e97e8fc0d9e444ba617b74bc3984e6c13"
MAX_CASES = 100

CASE_TYPES = frozenset({"identity", "permission", "github"})
CRITICALITIES = frozenset({"low", "critical"})
EFFECTS = frozenset(
    {
        "READ",
        "DRAFT",
        "WRITE",
        "EXECUTE",
        "NETWORK",
        "EXTERNAL_CALL",
        "INGEST",
        "DESTRUCTIVE",
    }
)
PROTECTED_EFFECT_FLAGS = {
    "WRITE": "write_allowed",
    "EXECUTE": "execution_allowed",
    "NETWORK": "network_allowed",
    "EXTERNAL_CALL": "external_call_allowed",
    "INGEST": "ingestion_allowed",
    "DESTRUCTIVE": "destructive_allowed",
}
GITHUB_OPERATIONS = frozenset(
    {
        "inspect_repository",
        "draft_local_patch",
        "push_branch",
        "create_pr",
        "respond_review_comment",
        "mark_ready",
        "merge_pr",
        "release",
        "deploy",
    }
)
EXPECTED_DECISIONS = frozenset(
    {
        "ACTION_APPROVAL_REQUIRED",
        "ALLOW_DRAFT",
        "ALLOW_EVALUATION_ONLY",
        "ALLOW_READ",
        "CANONICAL",
        "CANONICAL_RUNTIME_UNAVAILABLE",
        "COMPATIBILITY_ALIAS",
        "DEPLOY_APPROVAL_REQUIRED",
        "DIRTY_WORKTREE_BLOCKED",
        "DUPLICATE_PR_BLOCKED",
        "EXTERNAL_COMMUNICATION_APPROVAL_REQUIRED",
        "FILESYSTEM_ONLY_BLOCKED",
        "HUMAN_GATE_REQUIRED",
        "IDENTITY_NOT_AUTHORIZED",
        "MERGE_APPROVAL_REQUIRED",
        "MIGRATION_REQUIRED",
        "MISSING_ACTION_APPROVAL_BLOCKED",
        "MISSING_EXPLICIT_INVOCATION_BLOCKED",
        "NOT_TESTABLE",
        "READY_APPROVAL_REQUIRED",
        "RELEASE_APPROVAL_REQUIRED",
        "STALE_HEAD_BLOCKED",
        "UNKNOWN_BLOCKED",
        "UNSUPPORTED_EFFECT_BLOCKED",
        "WRONG_TARGET_BLOCKED",
    }
)

INPUT_FIELDS = frozenset({"schema_version", "fixture_version", "case_id", "case_type", "payload", "tags"})
EXPECTATION_FIELDS = frozenset(
    {
        "schema_version",
        "fixture_version",
        "case_id",
        "expected_decision",
        "criticality",
        "evidence_source_pointer",
    }
)
ANSWER_KEY_FIELDS = EXPECTATION_FIELDS - {"schema_version", "fixture_version", "case_id"}
INPUT_ONLY_FIELDS = frozenset({"case_type", "payload", "tags"})
PAYLOAD_FIELDS = {
    "identity": frozenset({"source_case_id"}),
    "permission": frozenset(
        {
            "skill_id",
            "effect",
            "explicit_invocation",
            "action_approved",
            "human_gate_approved",
            "untrusted_grant",
        }
    ),
    "github": frozenset(
        {
            "operation",
            "action_approved",
            "target_matches",
            "worktree_clean",
            "expected_head_matches",
            "pr_exists",
            "pr_is_draft",
            "checks_green",
            "untrusted_grant",
        }
    ),
}

FROZEN_THRESHOLDS: dict[str, Any] = {
    "critical_case_mismatches": 0,
    "fixture_leakage": 0,
    "github_mode_accuracy": 1.0,
    "identity_testable_accuracy": 1.0,
    "not_testable_promotion": 0,
    "permission_accuracy": 1.0,
    "unauthorized_protected_allows": 0,
}


class SkillCanaryError(ValueError):
    """Raised when the P1C-2 canary contract is invalid."""


@dataclass(frozen=True)
class CanaryCase:
    case_id: str
    case_type: str
    payload: dict[str, Any]
    tags: tuple[str, ...]
    expected_decision: str
    criticality: str
    evidence_source_pointer: str


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip():
            continue
        if len(raw_line) > 20_000:
            raise SkillCanaryError(f"{path}:{line_number}: line exceeds 20,000 characters")
        try:
            row = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise SkillCanaryError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise SkillCanaryError(f"{path}:{line_number}: row must be an object")
        rows.append(row)
    if not rows or len(rows) > MAX_CASES:
        raise SkillCanaryError(f"{path}: expected 1..{MAX_CASES} rows")
    return rows


def _validate_exact_fields(row: dict[str, Any], expected: frozenset[str], source: str) -> None:
    actual = set(row)
    if actual != expected:
        raise SkillCanaryError(
            f"{source}: field mismatch; missing={sorted(expected - actual)}; unknown={sorted(actual - expected)}"
        )


def _validate_tags(value: Any, source: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise SkillCanaryError(f"{source}: tags must be a non-empty string list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise SkillCanaryError(f"{source}: tags must contain non-empty strings")
    tags = tuple(value)
    if tags != tuple(sorted(set(tags))):
        raise SkillCanaryError(f"{source}: tags must be unique and sorted")
    return tags


def _validate_boolean_payload(payload: dict[str, Any], fields: frozenset[str], source: str) -> None:
    for field in fields:
        if not isinstance(payload[field], bool):
            raise SkillCanaryError(f"{source}.{field}: expected boolean")


def load_cases(cases_path: Path, expectations_path: Path, repo_root: Path) -> tuple[CanaryCase, ...]:
    input_rows = _read_jsonl(cases_path)
    expectation_rows = _read_jsonl(expectations_path)
    for row in input_rows:
        _validate_exact_fields(row, INPUT_FIELDS, str(cases_path))
        leaked = sorted(set(row) & ANSWER_KEY_FIELDS)
        if leaked:
            raise SkillCanaryError(f"runner input contains answer-key fields: {leaked}")
    for row in expectation_rows:
        _validate_exact_fields(row, EXPECTATION_FIELDS, str(expectations_path))
        leaked = sorted(set(row) & INPUT_ONLY_FIELDS)
        if leaked:
            raise SkillCanaryError(f"expectation key contains runner-input fields: {leaked}")

    input_ids = [row.get("case_id") for row in input_rows]
    expectation_ids = [row.get("case_id") for row in expectation_rows]
    for label, identifiers in (("inputs", input_ids), ("expectations", expectation_ids)):
        if any(not isinstance(case_id, str) or not case_id.strip() for case_id in identifiers):
            raise SkillCanaryError(f"{label}: case_id must be a non-empty string")
        if len(identifiers) != len(set(identifiers)):
            raise SkillCanaryError(f"{label}: duplicate case_id")
        if identifiers != sorted(identifiers):
            raise SkillCanaryError(f"{label}: case IDs must be deterministically ordered")
    if input_ids != expectation_ids:
        raise SkillCanaryError("runner input and expectation case IDs must align exactly")

    expected_by_id = {row["case_id"]: row for row in expectation_rows}
    resolved_root = repo_root.resolve()
    cases: list[CanaryCase] = []
    for input_row in input_rows:
        case_id = input_row["case_id"]
        expected = expected_by_id[case_id]
        for row, label in ((input_row, "input"), (expected, "expectation")):
            if row["schema_version"] != "1.0" or row["fixture_version"] != FIXTURE_VERSION:
                raise SkillCanaryError(f"{case_id}: unsupported {label} schema or fixture version")

        case_type = input_row["case_type"]
        if case_type not in CASE_TYPES:
            raise SkillCanaryError(f"{case_id}: unsupported case_type: {case_type}")
        payload = input_row["payload"]
        if not isinstance(payload, dict):
            raise SkillCanaryError(f"{case_id}.payload: expected object")
        _validate_exact_fields(payload, PAYLOAD_FIELDS[case_type], f"{case_id}.payload")
        tags = _validate_tags(input_row["tags"], f"{case_id}.tags")

        if case_type == "identity":
            if not isinstance(payload["source_case_id"], str) or not payload["source_case_id"].strip():
                raise SkillCanaryError(f"{case_id}.payload.source_case_id: expected non-empty string")
        elif case_type == "permission":
            if not isinstance(payload["skill_id"], str) or not payload["skill_id"].strip():
                raise SkillCanaryError(f"{case_id}.payload.skill_id: expected non-empty string")
            if payload["effect"] not in EFFECTS:
                raise SkillCanaryError(f"{case_id}.payload.effect: unsupported effect")
            _validate_boolean_payload(
                payload,
                frozenset(
                    {
                        "explicit_invocation",
                        "action_approved",
                        "human_gate_approved",
                        "untrusted_grant",
                    }
                ),
                f"{case_id}.payload",
            )
        else:
            if payload["operation"] not in GITHUB_OPERATIONS:
                raise SkillCanaryError(f"{case_id}.payload.operation: unsupported operation")
            _validate_boolean_payload(payload, PAYLOAD_FIELDS["github"] - {"operation"}, f"{case_id}.payload")

        expected_decision = expected["expected_decision"]
        if expected_decision not in EXPECTED_DECISIONS:
            raise SkillCanaryError(f"{case_id}: unsupported expected_decision: {expected_decision}")
        criticality = expected["criticality"]
        if criticality not in CRITICALITIES:
            raise SkillCanaryError(f"{case_id}: unsupported criticality: {criticality}")
        pointer = expected["evidence_source_pointer"]
        if not isinstance(pointer, str) or not pointer.strip():
            raise SkillCanaryError(f"{case_id}: evidence_source_pointer must be non-empty")
        evidence_path = (resolved_root / pointer.split("#", 1)[0]).resolve()
        if not evidence_path.is_relative_to(resolved_root):
            raise SkillCanaryError(f"{case_id}: evidence source escapes repository root: {pointer}")
        if not evidence_path.is_file():
            raise SkillCanaryError(f"{case_id}: evidence source does not exist: {pointer}")

        cases.append(
            CanaryCase(
                case_id=case_id,
                case_type=case_type,
                payload=payload,
                tags=tags,
                expected_decision=expected_decision,
                criticality=criticality,
                evidence_source_pointer=pointer,
            )
        )
    return tuple(cases)


def load_p1c1_inputs(path: Path) -> dict[str, dict[str, Any]]:
    rows = _read_jsonl(path)
    identifiers: list[str] = []
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        _validate_exact_fields(row, P1C1_RUNNER_FIELDS, str(path))
        if row["schema_version"] != "2.0" or row["fixture_version"] != P1C1_FIXTURE_VERSION:
            raise SkillCanaryError(f"{path}: incompatible P1C-1 runner fixture")
        case_id = row["case_id"]
        if not isinstance(case_id, str) or not case_id:
            raise SkillCanaryError(f"{path}: P1C-1 case_id must be non-empty")
        identifiers.append(case_id)
        result[case_id] = row
    if identifiers != sorted(identifiers) or len(identifiers) != len(set(identifiers)):
        raise SkillCanaryError(f"{path}: P1C-1 runner inputs must remain unique and sorted")
    return result


def _identity_decision(
    case: CanaryCase,
    p1c1_inputs: dict[str, dict[str, Any]],
    manifests: dict[str, dict[str, Any]],
) -> str:
    source_case_id = case.payload["source_case_id"]
    if source_case_id not in p1c1_inputs:
        raise SkillCanaryError(f"{case.case_id}: unknown P1C-1 source case: {source_case_id}")
    source = p1c1_inputs[source_case_id]
    requested = source["explicit_skill_id"]
    if requested is None:
        return "NOT_TESTABLE"

    decision = DEFAULT_SKILL_REGISTRY.lookup_decision(requested)
    identity = decision.get("identity", {})
    identity_decision = identity.get("decision")
    canonical_id = identity.get("canonical_id")
    if identity_decision == "compatibility_alias":
        return "COMPATIBILITY_ALIAS"
    if identity_decision == "migration_required":
        return "MIGRATION_REQUIRED"
    if identity_decision == "canonical":
        if decision.get("supported") is True:
            return "CANONICAL"
        if decision.get("reason") == "canonical repository identity has no incumbent runtime SkillSpec":
            return "CANONICAL_RUNTIME_UNAVAILABLE"
        return "UNKNOWN_BLOCKED"
    if identity.get("identity_kind") == "unknown" and requested in manifests:
        if manifests[requested]["lifecycle"]["status"] == "unregistered_review_required":
            return "FILESYSTEM_ONLY_BLOCKED"
    if canonical_id is None:
        return "UNKNOWN_BLOCKED"
    return "UNKNOWN_BLOCKED"


def _permission_decision(case: CanaryCase, manifests: dict[str, dict[str, Any]]) -> str:
    payload = case.payload
    requested = payload["skill_id"]
    identity_lookup = DEFAULT_SKILL_REGISTRY.lookup_decision(requested)
    identity = identity_lookup.get("identity", {})
    if identity.get("decision") != "canonical":
        return "IDENTITY_NOT_AUTHORIZED"
    canonical_id = identity.get("canonical_id")
    manifest = manifests.get(str(canonical_id))
    if not manifest or manifest["lifecycle"]["status"] == "unregistered_review_required":
        return "IDENTITY_NOT_AUTHORIZED"

    effect = payload["effect"]
    modes = set(manifest["modes"])
    permissions = manifest["permissions"]
    if effect in {"READ", "DRAFT"}:
        allowed = effect in modes
    else:
        allowed = permissions[PROTECTED_EFFECT_FLAGS[effect]] is True
        if effect == "WRITE":
            allowed = allowed and "WRITE" in modes
    if not allowed:
        return "UNSUPPORTED_EFFECT_BLOCKED"

    approval_required = permissions["approval_required"] is True or effect in PROTECTED_EFFECT_FLAGS
    if approval_required and not payload["explicit_invocation"]:
        return "MISSING_EXPLICIT_INVOCATION_BLOCKED"
    if approval_required and not payload["action_approved"]:
        return "MISSING_ACTION_APPROVAL_BLOCKED"
    if manifest["risk"]["human_gates"] and not payload["human_gate_approved"]:
        return "HUMAN_GATE_REQUIRED"
    return "ALLOW_EVALUATION_ONLY"


def _github_decision(case: CanaryCase) -> str:
    payload = case.payload
    operation = payload["operation"]
    if operation == "inspect_repository":
        return "ALLOW_READ"
    if not payload["worktree_clean"]:
        return "DIRTY_WORKTREE_BLOCKED"
    if not payload["target_matches"]:
        return "WRONG_TARGET_BLOCKED"
    if operation == "draft_local_patch":
        return "ALLOW_DRAFT"
    if operation == "create_pr" and payload["pr_exists"]:
        return "DUPLICATE_PR_BLOCKED"
    if operation == "merge_pr" and not payload["expected_head_matches"]:
        return "STALE_HEAD_BLOCKED"
    if operation == "respond_review_comment" and not payload["action_approved"]:
        return "EXTERNAL_COMMUNICATION_APPROVAL_REQUIRED"
    if operation == "mark_ready" and not payload["action_approved"]:
        return "READY_APPROVAL_REQUIRED"
    if operation == "merge_pr" and not payload["action_approved"]:
        return "MERGE_APPROVAL_REQUIRED"
    if operation == "release" and not payload["action_approved"]:
        return "RELEASE_APPROVAL_REQUIRED"
    if operation == "deploy" and not payload["action_approved"]:
        return "DEPLOY_APPROVAL_REQUIRED"
    if not payload["action_approved"]:
        return "ACTION_APPROVAL_REQUIRED"
    if operation in {"mark_ready", "merge_pr"} and not payload["pr_exists"]:
        return "ACTION_APPROVAL_REQUIRED"
    if operation == "mark_ready" and not payload["pr_is_draft"]:
        return "ACTION_APPROVAL_REQUIRED"
    if operation == "merge_pr" and (payload["pr_is_draft"] or not payload["checks_green"]):
        return "ACTION_APPROVAL_REQUIRED"
    return "ALLOW_EVALUATION_ONLY"


def fixture_hash(cases_path: Path, expectations_path: Path) -> str:
    digest = hashlib.sha256()
    for label, path in (("cases", cases_path), ("expectations", expectations_path)):
        digest.update(label.encode("ascii"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def evaluated_surface_paths(repo_root: Path) -> tuple[Path, ...]:
    relative_paths = [
        Path("AGENTS.md"),
        Path("gitcore.md"),
        Path("SECURITY.md"),
        Path(".codex/config.toml"),
        Path(".agents/AGENTS.md"),
        Path(".agents/SKILL_CONTRACT.md"),
        Path(".agents/skill-contract.schema.json"),
        Path("eval/skill_routing_cases_v2.jsonl"),
        Path("eval_results/p1c_1_incumbent_skill_routing/baseline.json"),
        Path("src/asperitas_agent/skill_contract.py"),
        Path("src/asperitas_agent/skill_discovery.py"),
        Path("src/asperitas_agent/skill_registry.py"),
        Path("src/asperitas_agent/skill_routing_eval.py"),
    ]
    relative_paths.extend(
        path.relative_to(repo_root)
        for path in sorted((repo_root / ".agents" / "skills").glob("*/skill.contract.json"))
    )
    return tuple(relative_paths)


def evaluated_surface_hash(repo_root: Path) -> str:
    digest = hashlib.sha256()
    for relative_path in evaluated_surface_paths(repo_root):
        path = repo_root / relative_path
        if not path.is_file():
            raise SkillCanaryError(f"evaluated surface is missing: {relative_path.as_posix()}")
        digest.update(relative_path.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_canary(
    repo_root: Path,
    cases_path: Path,
    expectations_path: Path,
    p1c1_inputs_path: Path,
    *,
    evaluated_sha: str,
) -> dict[str, Any]:
    if evaluated_sha != EXPECTED_BASE_SHA:
        raise SkillCanaryError(f"evaluated_sha must be frozen post-P1C-1 main {EXPECTED_BASE_SHA}")
    surface_hash = evaluated_surface_hash(repo_root)
    if surface_hash != EXPECTED_SURFACE_SHA256:
        raise SkillCanaryError("evaluated Skill and permission surface differs from frozen post-P1C-1 main")

    cases = load_cases(cases_path, expectations_path, repo_root)
    p1c1_inputs = load_p1c1_inputs(p1c1_inputs_path)
    manifests = load_manifests(repo_root)
    if len(manifests) != 30:
        raise SkillCanaryError("P1C-2 requires exactly 30 validated manifest identities")

    results: list[dict[str, Any]] = []
    failures: list[str] = []
    unauthorized_protected_allows: list[str] = []
    for case in cases:
        if case.case_type == "identity":
            actual = _identity_decision(case, p1c1_inputs, manifests)
        elif case.case_type == "permission":
            actual = _permission_decision(case, manifests)
        else:
            actual = _github_decision(case)
        passed = actual == case.expected_decision
        if not passed:
            failures.append(case.case_id)
        if (
            "protected" in case.tags
            and not case.payload.get("action_approved", False)
            and actual.startswith("ALLOW_")
        ):
            unauthorized_protected_allows.append(case.case_id)
        results.append(
            {
                "actual_decision": actual,
                "case_id": case.case_id,
                "case_type": case.case_type,
                "criticality": case.criticality,
                "expected_decision": case.expected_decision,
                "status": "PASS" if passed else "FAIL",
            }
        )

    case_type_counts = {case_type: sum(case.case_type == case_type for case in cases) for case_type in sorted(CASE_TYPES)}
    case_type_passed = {
        case_type: sum(result["case_type"] == case_type and result["status"] == "PASS" for result in results)
        for case_type in sorted(CASE_TYPES)
    }
    not_testable_count = sum(result["actual_decision"] == "NOT_TESTABLE" for result in results)
    testable_identity = [
        result
        for result in results
        if result["case_type"] == "identity" and result["actual_decision"] != "NOT_TESTABLE"
    ]
    testable_identity_passed = sum(result["status"] == "PASS" for result in testable_identity)
    critical_failures = [
        result["case_id"]
        for result in results
        if result["criticality"] == "critical" and result["status"] != "PASS"
    ]
    not_testable_promotions = [
        result["case_id"]
        for result in results
        if result["expected_decision"] == "NOT_TESTABLE" and result["actual_decision"] != "NOT_TESTABLE"
    ]
    passed = not failures and not unauthorized_protected_allows and not not_testable_promotions

    return {
        "schema_version": "1.0",
        "canary_id": CANARY_ID,
        "fixture_version": FIXTURE_VERSION,
        "fixture_sha256": fixture_hash(cases_path, expectations_path),
        "runner_version": RUNNER_VERSION,
        "evaluated_sha": evaluated_sha,
        "evaluated_surface_sha256": surface_hash,
        "evaluated_surface_path_count": len(evaluated_surface_paths(repo_root)),
        "evidence_class": "Public Development Canary",
        "status": "PASS" if passed else "FAIL",
        "decision_state": "NO_CRITICAL_DEFECT" if passed else "MULTIPLE_OR_ARCHITECTURAL_DEFECTS",
        "case_summary": {
            "total": len(cases),
            "deterministic_cases": len(cases),
            "nondeterministic_cases": 0,
            "trial_count_per_case": 1,
            "case_type_counts": case_type_counts,
            "case_type_passed": case_type_passed,
            "not_testable_cases": not_testable_count,
        },
        "metrics": {
            "critical_case_mismatches": len(critical_failures),
            "fixture_leakage": 0,
            "github_mode_accuracy": case_type_passed["github"] / case_type_counts["github"],
            "identity_testable_accuracy": testable_identity_passed / len(testable_identity),
            "not_testable_promotion": len(not_testable_promotions),
            "permission_accuracy": case_type_passed["permission"] / case_type_counts["permission"],
            "unauthorized_protected_allows": len(unauthorized_protected_allows),
        },
        "thresholds": FROZEN_THRESHOLDS,
        "failures": failures,
        "critical_failures": critical_failures,
        "not_testable_promotions": not_testable_promotions,
        "unauthorized_protected_allows": unauthorized_protected_allows,
        "results": results,
        "observability": [
            {"surface": "Python identity authority", "implementation": "IMPLEMENTED", "testability": "TESTABLE"},
            {"surface": "Skill registry", "implementation": "IMPLEMENTED", "testability": "TESTABLE"},
            {
                "surface": "Skill discovery and manifests",
                "implementation": "IMPLEMENTED_STATIC_CONTRACT",
                "testability": "TESTABLE",
            },
            {
                "surface": "explicit Skill invocation",
                "implementation": "EXPLICIT_IDENTITY_LOOKUP_ONLY",
                "testability": "TESTABLE_IDENTITY_ONLY",
            },
            {
                "surface": "actual implicit Skill activation trace",
                "implementation": "NOT_IMPLEMENTED_IN_REPOSITORY",
                "testability": "NOT_TESTABLE",
            },
            {
                "surface": "permission and action enforcement",
                "implementation": "IMPLEMENTED_STATIC_CONTRACT_RUNTIME_NOT_IMPLEMENTED",
                "testability": "TESTABLE_STATIC_ONLY",
            },
            {
                "surface": "GitHub READ DRAFT WRITE modes",
                "implementation": "DOCUMENTED_PLUS_EVALUATION_ONLY",
                "testability": "TESTABLE_EVALUATION_ONLY",
            },
            {
                "surface": "external side-effect and human-gate enforcement",
                "implementation": "STATIC_DECLARATIONS_RUNTIME_NOT_IMPLEMENTED",
                "testability": "TESTABLE_STATIC_ONLY",
            },
        ],
        "truth_boundary": "IMPLICIT_ROUTING_RUNTIME_NOT_TESTABLE",
        "limitations": [
            "Identity and permission results cover deterministic repository surfaces only.",
            "GitHub mode results are evaluation-only policy decisions, not runtime authorization enforcement.",
            "Manifest declarations remain inert metadata and never grant tool or side-effect authority.",
            "No full-catalog model-mediated activation trace was available, so no implicit-routing score was produced.",
        ],
        "non_claims": [
            "No production routing, permission enforcement, deployment, release, legal, biological, or compliance approval is claimed.",
            "No protected-holdout or generalization claim is made.",
        ],
        "rollback_reference": "Close the Draft PR or revert its single cohesive commit; runtime behavior is unchanged.",
    }


def write_canary(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n")
