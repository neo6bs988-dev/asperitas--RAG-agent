from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .candidate_eval import compare_candidates
from .context_quality import evaluate_context
from .diagnostics import diagnose_suite
from .release_gate import decide_release, validate_release


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def expand_paired_trials(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    trials: list[dict[str, Any]] = []
    for spec in specs:
        slice_name = str(spec["slice"])
        trial_count = int(spec["trials"])
        incumbent_successes = int(spec["incumbent_successes"])
        candidate_successes = int(spec["candidate_successes"])
        critical = bool(spec["critical"])
        if not 0 <= incumbent_successes <= trial_count:
            raise ValueError(f"{slice_name}: invalid incumbent_successes")
        if not 0 <= candidate_successes <= trial_count:
            raise ValueError(f"{slice_name}: invalid candidate_successes")

        for index in range(trial_count):
            trials.append(
                {
                    "trial_id": f"{slice_name}-inc-{index}",
                    "slice": slice_name,
                    "variant": "incumbent",
                    "passed": index < incumbent_successes,
                    "critical": critical,
                    "cost": float(spec["incumbent_cost"]),
                    "latency_ms": float(spec["incumbent_latency_ms"]) + index,
                }
            )
            trials.append(
                {
                    "trial_id": f"{slice_name}-cand-{index}",
                    "slice": slice_name,
                    "variant": "candidate",
                    "passed": index < candidate_successes,
                    "critical": critical,
                    "cost": float(spec["candidate_cost"]),
                    "latency_ms": float(spec["candidate_latency_ms"]) + index,
                }
            )
    return trials


def run(contract_path: str | Path, cases_path: str | Path) -> dict[str, Any]:
    contract = load_json(contract_path)
    cases = load_json(cases_path)

    release_validation = validate_release(contract["release"])
    diagnostics = diagnose_suite(cases["failure_diagnostics"])
    context = evaluate_context(
        cases["context_items"],
        token_budget=int(contract["context_token_budget"]),
    )
    paired_trials = expand_paired_trials(cases["paired_trial_specs"])
    candidate_eval = compare_candidates(
        paired_trials,
        minimum_trials_per_slice=int(
            contract["minimum_trials_per_slice"]
        ),
        critical_pass_required=float(
            contract["critical_pass_required"]
        ),
        candidate_delta_min=float(contract["candidate_delta_min"]),
    )
    decision = decide_release(
        release_validation=release_validation,
        diagnostics=diagnostics,
        context=context,
        candidate_eval=candidate_eval,
        private_oracle_accessed=bool(
            cases["integrity"]["private_oracle_accessed"]
        ),
        threshold_changed_after_results=bool(
            cases["integrity"]["threshold_changed_after_results"]
        ),
    )
    return {
        "schema_version": "asperitas-evalos-v0.9",
        "decision": decision,
        "release_validation": release_validation,
        "failure_diagnostics": diagnostics,
        "context_quality": context,
        "candidate_evaluation": candidate_eval,
        "truth_boundary": (
            "Synthetic local controls do not establish repository-wide "
            "compatibility, protected-holdout performance, deployment, "
            "scientific or legal clearance, rights clearance, or "
            "production readiness."
        ),
    }
