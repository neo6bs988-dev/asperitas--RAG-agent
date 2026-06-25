from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

RELEASE_POSTURE_DOCS = (
    Path("docs/V1_RELEASE_CLOSEOUT.md"),
    Path("docs/releases/V1_0_0_RC1_RELEASE_NOTES.md"),
    Path("docs/releases/V1_0_0_RC1_CLOSEOUT_PACKET.md"),
    Path("docs/releases/V1_0_0_RC1_MANUAL_RELEASE_STEPS.md"),
)

REQUIRED_FRESH_OUTPUT_PHRASES = (
    "fresh command output",
    "final RC",
    "internal dry-run",
    "internal release",
)

FORBIDDEN_RELEASE_CLAIMS = (
    re.compile(r"^Status:\s*(?:internal release candidate|internal release-candidate packet|V1 internal release candidate closeout)\s*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"\bfinal RC readiness\b(?![^.\n]*\b(?:not|NO-GO|remain pending|requires fresh command output)\b)", re.IGNORECASE),
    re.compile(r"\binternal dry-run (?:is )?(?:ready|complete|completed)\b", re.IGNORECASE),
    re.compile(r"\binternal release (?:is )?(?:ready|complete|completed)\b", re.IGNORECASE),
    re.compile(r"(?<!NO-)GO for (?:final RC|internal dry-run|internal release|production)", re.IGNORECASE),
    re.compile(r"\bproduction readiness\b(?![^.\n]*\b(?:not|does not|without|claim)\b)", re.IGNORECASE),
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def check_release_posture_docs(root: Path) -> list[str]:
    errors: list[str] = []
    combined_parts: list[str] = []
    for relative in RELEASE_POSTURE_DOCS:
        path = root / relative
        if not path.exists():
            errors.append(f"Missing release posture doc: {relative.as_posix()}")
            continue
        text = _read_text(path)
        combined_parts.append(text)
        if "production readiness" in text.lower() and "does not claim production readiness" not in text.lower():
            errors.append(f"Production-readiness mention must stay explicitly negative: {relative.as_posix()}")

    combined = "\n".join(combined_parts)
    for pattern in FORBIDDEN_RELEASE_CLAIMS:
        match = pattern.search(combined)
        if match:
            errors.append(f"Forbidden release/final-readiness claim: {match.group(0)}")

    normalized = " ".join(combined.lower().split())
    for phrase in REQUIRED_FRESH_OUTPUT_PHRASES:
        if phrase.lower() not in normalized:
            errors.append(f"Missing fresh-output guard phrase: {phrase}")

    if "publish release notes" not in normalized and "publish these notes" not in normalized:
        errors.append("Missing explicit fresh-output guard for release notes.")
    if "claim go" not in normalized and "go claim" not in normalized:
        errors.append("Missing explicit fresh-output guard for GO claims.")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify V1 P0/P1 gap-fix release-posture and fresh-output guards.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    errors = check_release_posture_docs(args.repo_root.resolve())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("V1 P0/P1 gap-fix guard check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
