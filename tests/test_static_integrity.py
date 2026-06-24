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


def test_forbidden_dependency_scan_is_clean_for_runtime_code():
    module = load_eval_module()

    assert module.scan_forbidden_references() == []


def test_anti_cheating_scan_is_clean_for_runtime_code():
    module = load_eval_module()

    assert module.scan_anti_cheating() == []


def test_skill_registry_verification_metadata_is_not_runtime_anti_cheating():
    module = load_eval_module()

    assert "src/asperitas_agent/skill_registry.py" in module.ANTI_CHEATING_EXCLUDED_PATHS


def test_protected_file_hash_set_includes_core_artifacts():
    module = load_eval_module()
    hashes = module.protected_file_hashes()

    assert "data/chunks.jsonl" in hashes
    assert "data/source_registry.csv" in hashes
    assert "eval/retrieval_questions.jsonl" in hashes
    assert "eval/expected_sources.jsonl" in hashes
    assert all(len(value) == 64 for value in hashes.values())
