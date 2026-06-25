from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACK_PATH = Path("docs/V1_MVP_PERFORMANCE_PACK.md")

REQUIRED_MVPS = (
    "MVP-001",
    "MVP-002",
    "MVP-002.5",
    "MVP-003",
    "MVP-004",
    "MVP-005",
    "MVP-006",
    "MVP-007",
    "MVP-008",
    "MVP-009",
    "MVP-010",
    "MVP-014",
    "MVP-015",
    "MVP-016",
    "MVP-017",
    "MVP-018",
    "MVP-019A",
    "MVP-019B",
    "MVP-019C",
    "MVP-019D",
    "MVP-019E",
)

REQUIRED_COMMANDS = (
    "python -m pytest",
    "python scripts/verify_artifacts.py",
    "python scripts/check_v1_stage_gate_scope.py",
    "python scripts/run_retrieval_eval.py --retriever baseline --limit 5",
    "python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5",
    "python scripts/check_v1_mvp_performance_pack.py",
    "git diff --check",
)

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

FORBIDDEN_CLAIM_PATTERNS = (
    re.compile(r"\bproduction[- ]grade\b", re.IGNORECASE),
    re.compile(r"(?<!NO-)GO for production deployment\b", re.IGNORECASE),
    re.compile(r"(?<!NO-)GO for final RC readiness\b", re.IGNORECASE),
    re.compile(r"(?<!NO-)GO for internal dry-run readiness\b", re.IGNORECASE),
    re.compile(r"(?<!NO-)GO for internal release readiness\b", re.IGNORECASE),
    re.compile(r"\bready for (?:production deployment|final RC readiness|internal dry-run readiness|internal release readiness)\b", re.IGNORECASE),
    re.compile(r"\bsource expansion (?:is )?complete\b", re.IGNORECASE),
    re.compile(r"\bClosure Matrix completed\b", re.IGNORECASE),
    re.compile(r"\bP0/P1 Gap Fix Only completed\b", re.IGNORECASE),
    re.compile(r"\bFinal Pre-RC Regression completed\b", re.IGNORECASE),
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
            errors.append(f"Forbidden performance-pack mutation: {path}")
    return errors


def _scorecard_rows(text: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("| MVP-"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells:
            rows[cells[0]] = stripped
    return rows


def check_pack_text(root: Path) -> list[str]:
    path = root / PACK_PATH
    if not path.exists():
        return [f"Missing performance pack: {PACK_PATH.as_posix()}"]

    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    rows = _scorecard_rows(text)

    for mvp in REQUIRED_MVPS:
        row = rows.get(mvp)
        if row is None:
            errors.append(f"Missing scorecard row: {mvp}")
            continue
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) != 6:
            errors.append(f"Scorecard row must have 6 columns: {mvp}")
            continue
        metric, threshold, command, go_no_go = cells[2], cells[3], cells[4], cells[5]
        if not metric:
            errors.append(f"Missing metric: {mvp}")
        if not threshold:
            errors.append(f"Missing threshold: {mvp}")
        if "`python " not in command and "`git " not in command:
            errors.append(f"Missing command: {mvp}")
        if "GO" not in go_no_go or "NO-GO" not in go_no_go:
            errors.append(f"Missing GO/NO-GO rule: {mvp}")

    for command in REQUIRED_COMMANDS:
        if command not in text:
            errors.append(f"Missing required verification command: {command}")

    required_phrases = (
        "P0 | None introduced by this docs/tests/checks backfill.",
        "No decision log update is required for this pack",
        "later V1 roadmap steps remain pending",
        "Playbook v3 and Stage-Gate status",
    )
    for phrase in required_phrases:
        if phrase not in text:
            errors.append(f"Missing required performance-pack phrase: {phrase}")

    for pattern in FORBIDDEN_CLAIM_PATTERNS:
        if pattern.search(text):
            errors.append(f"Forbidden performance-pack claim: {pattern.pattern}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify V1 MVP performance pack scope and scorecard completeness.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()

    errors = []
    errors.extend(check_changed_files(git_changed_files(root)))
    errors.extend(check_pack_text(root))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("V1 MVP performance pack check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
