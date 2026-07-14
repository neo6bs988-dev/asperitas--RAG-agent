from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PACKAGE = (ROOT / "src" / "asperitas_agent").resolve()
DISTRIBUTION_NAME = "asperitas-agent"
CONSOLE_SCRIPT_NAME = "asperitas-agent"
CONSOLE_SCRIPT_TARGET = "asperitas_agent.cli:main"


def _run(command: Sequence[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def _entry_points_for_console_script() -> list[metadata.EntryPoint]:
    entry_points = metadata.entry_points()
    if hasattr(entry_points, "select"):
        return list(entry_points.select(group="console_scripts", name=CONSOLE_SCRIPT_NAME))
    return [
        entry_point
        for entry_point in entry_points.get("console_scripts", ())
        if entry_point.name == CONSOLE_SCRIPT_NAME
    ]


def _git_head() -> tuple[str | None, str | None]:
    result = _run(("git", "rev-parse", "HEAD"))
    if result.returncode != 0:
        return None, result.stderr.strip() or result.stdout.strip() or "git rev-parse failed"
    return result.stdout.strip(), None


def verify_packaging_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        import asperitas_agent
    except Exception as exc:  # pragma: no cover - reported as structured failure
        return {
            "ok": False,
            "errors": [f"package import failed: {type(exc).__name__}: {exc}"],
            "warnings": warnings,
        }

    package_file = Path(asperitas_agent.__file__ or "").resolve()
    expected_init = CANONICAL_PACKAGE / "__init__.py"
    if package_file != expected_init:
        errors.append(
            "package import did not resolve to the canonical src layout: "
            f"expected={expected_init.as_posix()} actual={package_file.as_posix()}"
        )

    package_version = str(getattr(asperitas_agent, "__version__", "")).strip()
    if not package_version:
        errors.append("asperitas_agent.__version__ is empty")

    try:
        distribution_version = metadata.version(DISTRIBUTION_NAME)
    except metadata.PackageNotFoundError:
        distribution_version = None
        errors.append("installed distribution metadata is missing; install the project before certification")

    if distribution_version is not None and distribution_version != package_version:
        errors.append(
            "package and distribution versions differ: "
            f"package={package_version!r} distribution={distribution_version!r}"
        )

    console_entry_points = _entry_points_for_console_script()
    if len(console_entry_points) != 1:
        errors.append(
            f"expected exactly one {CONSOLE_SCRIPT_NAME!r} console entry point, found {len(console_entry_points)}"
        )
    elif console_entry_points[0].value != CONSOLE_SCRIPT_TARGET:
        errors.append(
            "console entry point target differs from the repository contract: "
            f"expected={CONSOLE_SCRIPT_TARGET!r} actual={console_entry_points[0].value!r}"
        )

    try:
        requirements = metadata.requires(DISTRIBUTION_NAME) or []
    except metadata.PackageNotFoundError:
        requirements = []

    unconditional_requirements = sorted(requirement for requirement in requirements if "extra ==" not in requirement)
    if unconditional_requirements:
        errors.append(
            "deterministic core gained unconditional runtime dependencies: "
            + ", ".join(unconditional_requirements)
        )

    module_help = _run((sys.executable, "-m", "asperitas_agent.cli", "--help"))
    if module_help.returncode != 0:
        errors.append(
            "module CLI smoke test failed: "
            + (module_help.stderr.strip() or module_help.stdout.strip() or "unknown error")
        )

    console_script = shutil.which(CONSOLE_SCRIPT_NAME)
    if console_script is None:
        errors.append(f"installed console script is not discoverable on PATH: {CONSOLE_SCRIPT_NAME}")
        console_help_returncode = None
    else:
        console_help = _run((console_script, "--help"))
        console_help_returncode = console_help.returncode
        if console_help.returncode != 0:
            errors.append(
                "installed console-script smoke test failed: "
                + (console_help.stderr.strip() or console_help.stdout.strip() or "unknown error")
            )

    git_head, git_error = _git_head()
    if git_error:
        errors.append(git_error)

    expected_head = (
        os.environ.get("ASPERITAS_EXPECTED_HEAD_SHA", "").strip()
        or os.environ.get("GITHUB_SHA", "").strip()
        or None
    )
    if expected_head is not None and git_head != expected_head:
        errors.append(f"checked-out HEAD differs from expected exact head: expected={expected_head} actual={git_head}")
    if expected_head is None:
        warnings.append("no expected head environment variable is set; HEAD was recorded but not externally asserted")

    return {
        "ok": not errors,
        "distribution": DISTRIBUTION_NAME,
        "package_version": package_version,
        "distribution_version": distribution_version,
        "package_file": package_file.as_posix(),
        "expected_package_file": expected_init.as_posix(),
        "console_script": console_script,
        "console_script_target": CONSOLE_SCRIPT_TARGET,
        "module_help_returncode": module_help.returncode,
        "console_help_returncode": console_help_returncode,
        "unconditional_requirements": unconditional_requirements,
        "git_head": git_head,
        "expected_git_head": expected_head,
        "python_version": sys.version,
        "platform": sys.platform,
        "errors": errors,
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify Asperitas packaging, import, CLI, and exact-head contracts")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--output", type=Path, help="Optionally write the JSON report to this path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = verify_packaging_contract()
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")

    if args.json or args.output is None:
        print(rendered)
    else:
        print("packaging contract passed" if report["ok"] else "packaging contract failed")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
