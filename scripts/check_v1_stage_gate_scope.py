from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCTRINE_PATH = Path("docs/V1_PLAYBOOK_V3_STAGE_GATE_ABSORPTION.md")

FORBIDDEN_CHANGED_PREFIXES = (
    "00_ADMIN/source_registry",
    "00_ADMIN/source_registries/",
    "01_RAW_SOURCES/",
    "03_PROCESSED_KB/chunks/",
    "04_VECTOR_DB/",
    "05_RAG_PIPELINE/scripts/asperitas_kb.py",
    "data/chunks.jsonl",
    "data/source_registry.csv",
    "src/asperitas_agent/retrieval",
    "src/asperitas_agent/embeddings.py",
    "src/asperitas_agent/reranking.py",
    "src/asperitas_agent/answer_generation.py",
)

FORBIDDEN_COMPLETED_ROADMAP_STEPS = (
    "MVP Performance Pack Backfill",
    "V1 Performance Closure Matrix",
    "P0/P1 Gap Fix Only",
    "Final Pre-RC Regression",
    "v1.0.0-rc1",
    "Internal Dry-run",
    "v1.0.0-internal",
)

FORBIDDEN_CLAIM_PATTERNS = (
    re.compile(r"\bproduction[- ]grade\b", re.IGNORECASE),
    re.compile(r"\bproduction deployment\b", re.IGNORECASE),
    re.compile(r"\bautonomous ingestion\b", re.IGNORECASE),
    re.compile(r"\bsource expansion (?:is )?complete\b", re.IGNORECASE),
    re.compile(r"\bfull V1 closure\b", re.IGNORECASE),
    re.compile(r"\bready for (?:final pre-RC regression|v1\.0\.0-rc1|internal dry-run|internal release)\b", re.IGNORECASE),
)

REQUIRED_PHRASES = (
    "Scope: Playbook v3 Absorption plus Benchmark Absorption & Stage-Gate Calibration only",
    "process doctrine absorbed from performance feature implemented",
    "Allowed status after those gates pass: ready for next V1 step.",
    "| 1. Playbook v3 Absorption | Completed by this process subtask |",
    "| 2. Benchmark Absorption & Stage-Gate Calibration | Completed by this process subtask |",
)


def git_changed_files(root: Path) -> tuple[str, ...]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip().replace("\\", "/")
        if " -> " in path:
            path = path.rsplit(" -> ", maxsplit=1)[1]
        paths.append(path)
    return tuple(paths)


def check_changed_files(changed_files: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    for path in changed_files:
        if path.startswith(FORBIDDEN_CHANGED_PREFIXES):
            errors.append(f"Forbidden V1 stage-gate scope mutation: {path}")
    return errors


def check_doctrine_text(root: Path) -> list[str]:
    path = root / DOCTRINE_PATH
    errors: list[str] = []
    if not path.exists():
        return [f"Missing doctrine file: {DOCTRINE_PATH.as_posix()}"]

    text = path.read_text(encoding="utf-8")
    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            errors.append(f"Missing required doctrine phrase: {phrase}")

    for step in FORBIDDEN_COMPLETED_ROADMAP_STEPS:
        completed_pattern = re.compile(rf"\|\s*\d+\.\s*{re.escape(step)}\s*\|\s*Completed\b", re.IGNORECASE)
        if completed_pattern.search(text):
            errors.append(f"Later V1 roadmap step must remain pending: {step}")

    for pattern in FORBIDDEN_CLAIM_PATTERNS:
        if pattern.search(text):
            errors.append(f"Forbidden stage-gate claim in doctrine: {pattern.pattern}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify V1 Playbook v3 stage-gate scope integrity.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()

    errors = []
    errors.extend(check_changed_files(git_changed_files(root)))
    errors.extend(check_doctrine_text(root))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("V1 stage-gate scope check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
