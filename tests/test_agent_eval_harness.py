from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_eval_module():
    spec = importlib.util.spec_from_file_location("evaluate_agent", REPO_ROOT / "scripts" / "evaluate_agent.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_eval_harness_report_shape_with_stubbed_retrieval_regression(monkeypatch):
    module = load_eval_module()
    monkeypatch.setattr(
        module,
        "run_retrieval_regression",
        lambda: {
            "ok": True,
            "pass_fail_reason": "stubbed pass",
            "threshold_source": module.MVP003_TARGET_SOURCE,
            "thresholds": {
                "source_file_match_at_3": 0.5,
                "source_file_match_at_5": 0.6,
                "section_match": 0.45,
                "overall_pass_rate": 0.45,
            },
            "baseline": {"command": "python scripts/run_retrieval_eval.py --retriever baseline --json"},
            "mvp003": {"command": "python scripts/run_retrieval_eval.py --retriever mvp003 --json"},
        },
    )

    report = module.evaluate_agent()

    assert report["ok"]
    assert report["total_cases"] == 3
    assert report["passed_cases"] == 3
    assert report["failed_cases"] == 0
    assert set(report["checks"]) == {
        "json_output",
        "schema",
        "status",
        "citations",
        "guardrails",
        "determinism",
        "protected_files_unchanged",
        "forbidden_imports",
        "anti_cheating",
        "retrieval_regression_unchanged",
    }


def test_eval_harness_cases_cover_answer_caution_and_abstention():
    module = load_eval_module()

    cases, checks = module.run_cases()
    statuses = {case["status"] for case in cases}

    assert statuses == {"answered", "caution", "abstained"}
    assert all(case["ok"] for case in cases)
    assert all(checks.values())


def test_agent_response_schema_validator_rejects_missing_required_fields():
    module = load_eval_module()

    errors = module.validate_agent_response_schema({"query": "incomplete"})

    assert any("missing field: top_k" in error for error in errors)
    assert any("missing field: guardrail" in error for error in errors)


def test_retrieval_regression_report_names_official_commands(monkeypatch):
    module = load_eval_module()

    def fake_run(retriever: str):
        value = 0.344 if retriever == "baseline" else 0.906
        return {
            "command": f"python scripts/run_retrieval_eval.py --retriever {retriever} --json",
            "returncode": 0,
            "metrics": {
                "source_file_match_at_3": value,
                "source_file_match_at_5": value,
                "source_priority_match": value,
                "evidence_label_match": value,
                "section_match": value,
                "overall_pass_rate": value,
            },
            "stdout_parse_error": "",
            "stderr": "",
        }

    monkeypatch.setattr(module, "_run_retrieval_eval", fake_run)
    monkeypatch.setattr(
        module,
        "load_mvp003_thresholds",
        lambda: (
            {
                "source_file_match_at_3": 0.5,
                "source_file_match_at_5": 0.6,
                "section_match": 0.45,
                "overall_pass_rate": 0.45,
            },
            module.MVP003_TARGET_SOURCE,
        ),
    )

    report = module.run_retrieval_regression()

    assert report["ok"]
    assert report["baseline"]["command"].endswith("--retriever baseline --json")
    assert report["mvp003"]["command"].endswith("--retriever mvp003 --json")
    assert report["mvp003"]["metrics"]["overall_pass_rate"] == 0.906
