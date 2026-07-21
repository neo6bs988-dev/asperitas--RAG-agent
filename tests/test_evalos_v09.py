from pathlib import Path

from asperitas_agent.evalos.candidate_eval import compare_candidates
from asperitas_agent.evalos.context_quality import evaluate_context
from asperitas_agent.evalos.diagnostics import diagnose_failure_layer
from asperitas_agent.evalos.release_gate import decide_release, validate_release
from asperitas_agent.evalos.runner import expand_paired_trials, load_json, run

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "eval/evalos/public/v0.9_contract.json"
CASES = ROOT / "eval/evalos/public/v0.9_cases.json"


def test_end_to_end_prompt_harness_candidate() -> None:
    report = run(CONTRACT, CASES)
    assert report["decision"]["status"] == "PROMPT_HARNESS_RELEASE_CANDIDATE"
    assert report["decision"]["promotion_allowed"] is False


def test_release_hash_is_frozen() -> None:
    contract = load_json(CONTRACT)
    assert validate_release(contract["release"])["passed"]
    contract["release"]["effect_ceiling"] = "WRITE"
    assert not validate_release(contract["release"])["passed"]


def test_prompt_change_requires_prompt_layer_evidence() -> None:
    cases = load_json(CASES)
    context_failure = cases["failure_diagnostics"][0]
    prompt_failure = cases["failure_diagnostics"][2]
    assert not diagnose_failure_layer(context_failure)["prompt_change_allowed"]
    assert diagnose_failure_layer(prompt_failure)["prompt_change_allowed"]


def test_context_rejects_duplicate_content() -> None:
    cases = load_json(CASES)
    items = list(cases["context_items"])
    duplicate = dict(items[0])
    duplicate["item_id"] = "duplicate"
    items.append(duplicate)
    report = evaluate_context(items, token_budget=2000)
    assert not report["passed"]
    assert any(error.startswith("DUPLICATE_CONTENT") for error in report["errors"])


def test_candidate_has_no_slice_regression() -> None:
    contract = load_json(CONTRACT)
    cases = load_json(CASES)
    report = compare_candidates(
        expand_paired_trials(cases["paired_trial_specs"]),
        minimum_trials_per_slice=contract["minimum_trials_per_slice"],
        critical_pass_required=contract["critical_pass_required"],
        candidate_delta_min=contract["candidate_delta_min"],
    )
    assert report["passed"]
    assert not report["critical_failures"]
    assert all(
        value["pass_rate_delta"] >= 0
        for value in report["slice_reports"].values()
    )


def test_private_oracle_access_invalidates_release() -> None:
    report = run(CONTRACT, CASES)
    invalid = decide_release(
        release_validation=report["release_validation"],
        diagnostics=report["failure_diagnostics"],
        context=report["context_quality"],
        candidate_eval=report["candidate_evaluation"],
        private_oracle_accessed=True,
        threshold_changed_after_results=False,
    )
    assert invalid["status"] == "INVALID"
