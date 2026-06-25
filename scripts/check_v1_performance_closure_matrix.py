from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = Path("docs/V1_PERFORMANCE_CLOSURE_MATRIX.md")
ROADMAP_PATH = Path("docs/ROADMAP.md")

REQUIRED_ROWS = (
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
    "Stage-gate scope",
    "MVP performance pack",
    "Closure matrix",
)

REQUIRED_COMMANDS = (
    "python -m pytest",
    "python scripts/verify_artifacts.py",
    "python scripts/check_v1_stage_gate_scope.py",
    "python scripts/check_v1_mvp_performance_pack.py",
    "python scripts/check_v1_release_readiness.py --json",
    "python scripts/run_retrieval_eval.py --retriever baseline --limit 5",
    "python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5",
    "python scripts/check_v1_performance_closure_matrix.py",
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
    re.compile(r"\bP0/P1 Gap Fix Only completed\b", re.IGNORECASE),
    re.compile(r"\bFinal Pre-RC Regression completed\b", re.IGNORECASE),
    re.compile(r"\bv1\.0\.0-rc1 completed\b", re.IGNORECASE),
    re.compile(r"\bInternal Dry-run completed\b", re.IGNORECASE),
    re.compile(r"\bv1\.0\.0-internal completed\b", re.IGNORECASE),
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
            errors.append(f"Forbidden closure-matrix mutation: {path}")
    return errors


def _matrix_rows(text: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("| "):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and cells[0] in REQUIRED_ROWS:
            rows.setdefault(cells[0], stripped)
    return rows


def check_matrix_text(root: Path) -> list[str]:
    path = root / MATRIX_PATH
    if not path.exists():
        return [f"Missing closure matrix: {MATRIX_PATH.as_posix()}"]

    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    rows = _matrix_rows(text)

    for row_name in REQUIRED_ROWS:
        row = rows.get(row_name)
        if row is None:
            errors.append(f"Missing closure matrix row: {row_name}")
            continue
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) != 7:
            errors.append(f"Closure matrix row must have 7 columns: {row_name}")
            continue
        status, command, result, gap, owner_action, go_no_go = cells[1:]
        if status not in {"verified", "blocked"}:
            errors.append(f"Invalid status for {row_name}: {status}")
        if "`python " not in command and "`git " not in command:
            errors.append(f"Missing evidence command: {row_name}")
        if "exit code 0" not in result and "covered by full `python -m pytest` exit code 0" not in result:
            errors.append(f"Missing concrete result: {row_name}")
        if not any(label in gap for label in ("P0", "P1", "P2")):
            errors.append(f"Missing gap severity: {row_name}")
        if not owner_action:
            errors.append(f"Missing owner action: {row_name}")
        if "GO" not in go_no_go or "NO-GO" not in go_no_go:
            errors.append(f"Missing GO/NO-GO: {row_name}")

    for command in REQUIRED_COMMANDS:
        if command not in text:
            errors.append(f"Missing required verification command: {command}")

    required_phrases = (
        "No decision log update is required",
        "Only P0/P1 items are allowed as the next remediation step.",
        "P2 items stay in V1.1 or later performance-hardening work.",
        "No source/raw/chunk/vector/embedding/retrieval/ranking/reranker/generation/runtime RAG mutation",
    )
    for phrase in required_phrases:
        if phrase not in text:
            errors.append(f"Missing required closure-matrix phrase: {phrase}")

    for pattern in FORBIDDEN_CLAIM_PATTERNS:
        if pattern.search(text):
            errors.append(f"Forbidden closure-matrix claim: {pattern.pattern}")

    return errors


def check_roadmap_text(root: Path) -> list[str]:
    path = root / ROADMAP_PATH
    if not path.exists():
        return [f"Missing roadmap: {ROADMAP_PATH.as_posix()}"]

    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    required_rows = (
        "| 3. MVP Performance Pack Backfill | Completed by `docs/V1_MVP_PERFORMANCE_PACK.md` |",
        "| 4. V1 Performance Closure Matrix | Completed by `docs/V1_PERFORMANCE_CLOSURE_MATRIX.md` after closure checks pass |",
        "| 5. P0/P1 Gap Fix Only | Completed by `scripts/check_v1_p0_p1_gap_fix.py` after PR #86 main verification |",
        "| 6. Final Pre-RC Regression | Completed by `docs/V1_FINAL_PRE_RC_REGRESSION.md` for RC preparation only |",
        "| 7. v1.0.0-rc1 | V1.0.0-rc1 baseline complete as prerelease at `7f28f0a60fae2d7e0b674d1111287386d2d64fc6` |",
        "| 8. Internal Dry-run | Pending reproducible dry-run evidence from `scripts/run_v1_internal_dry_run.py` |",
        "| 9. v1.0.0-internal | Pending; v1.0.0-internal pending until internal dry-run evidence passes |",
    )
    for row in required_rows:
        if row not in text:
            errors.append(f"Missing roadmap row: {row}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify V1 performance closure matrix completeness and scope.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()

    errors = []
    errors.extend(check_changed_files(git_changed_files(root)))
    errors.extend(check_matrix_text(root))
    errors.extend(check_roadmap_text(root))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("V1 performance closure matrix check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
