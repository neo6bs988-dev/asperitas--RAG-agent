from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Sequence
import venv

ROOT = Path(__file__).resolve().parents[1]
DISTRIBUTION_NAME = "asperitas-agent"
CONSOLE_SCRIPT_NAME = "asperitas-agent"


def _run(command: Sequence[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def _venv_python(environment: Path) -> Path:
    if os.name == "nt":
        return environment / "Scripts" / "python.exe"
    return environment / "bin" / "python"


def _venv_console_script(environment: Path) -> Path:
    if os.name == "nt":
        return environment / "Scripts" / f"{CONSOLE_SCRIPT_NAME}.exe"
    return environment / "bin" / CONSOLE_SCRIPT_NAME


def _outside_repository(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return True
    return False


def verify_distribution_install(dist_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    dist_dir = dist_dir.resolve()
    wheels = sorted(dist_dir.glob("*.whl"))
    source_distributions = sorted(dist_dir.glob("*.tar.gz"))

    if len(wheels) != 1:
        errors.append(f"expected exactly one wheel in {dist_dir}, found {len(wheels)}")
    if len(source_distributions) != 1:
        errors.append(f"expected exactly one source distribution in {dist_dir}, found {len(source_distributions)}")
    if errors:
        return {
            "ok": False,
            "dist_dir": dist_dir.as_posix(),
            "wheels": [path.name for path in wheels],
            "source_distributions": [path.name for path in source_distributions],
            "errors": errors,
            "warnings": warnings,
        }

    wheel = wheels[0]
    source_distribution = source_distributions[0]

    checker = shutil.which("check-wheel-contents")
    if checker is None:
        errors.append("check-wheel-contents executable is not available")
        checker_returncode = None
    else:
        checker_result = _run((checker, str(wheel)), cwd=ROOT)
        checker_returncode = checker_result.returncode
        if checker_result.returncode != 0:
            errors.append(
                "wheel contents validation failed: "
                + (checker_result.stderr.strip() or checker_result.stdout.strip() or "unknown error")
            )

    installed_payload: dict[str, Any] | None = None
    console_help_returncode: int | None = None

    with tempfile.TemporaryDirectory(prefix="asperitas-dist-cert-") as temporary_directory:
        temporary_root = Path(temporary_directory)
        environment = temporary_root / "venv"
        workdir = temporary_root / "outside-repository"
        workdir.mkdir()

        venv.EnvBuilder(with_pip=True, clear=True).create(environment)
        python = _venv_python(environment)
        console_script = _venv_console_script(environment)

        install_result = _run(
            (
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--no-deps",
                str(wheel),
            ),
            cwd=workdir,
        )
        if install_result.returncode != 0:
            errors.append(
                "clean wheel installation failed: "
                + (install_result.stderr.strip() or install_result.stdout.strip() or "unknown error")
            )
        else:
            probe = """
import importlib.metadata as metadata
import json
from pathlib import Path
import asperitas_agent
payload = {
    "module_file": str(Path(asperitas_agent.__file__).resolve()),
    "package_version": asperitas_agent.__version__,
    "distribution_version": metadata.version("asperitas-agent"),
    "working_directory": str(Path.cwd().resolve()),
}
print(json.dumps(payload, sort_keys=True))
""".strip()
            probe_result = _run((str(python), "-I", "-c", probe), cwd=workdir)
            if probe_result.returncode != 0:
                errors.append(
                    "isolated installed-package probe failed: "
                    + (probe_result.stderr.strip() or probe_result.stdout.strip() or "unknown error")
                )
            else:
                try:
                    installed_payload = json.loads(probe_result.stdout.strip().splitlines()[-1])
                except (IndexError, json.JSONDecodeError) as exc:
                    errors.append(f"installed-package probe returned invalid JSON: {exc}")
                else:
                    module_file = Path(installed_payload["module_file"])
                    if not _outside_repository(module_file):
                        errors.append(f"clean install imported repository source instead of wheel contents: {module_file}")
                    if installed_payload["package_version"] != installed_payload["distribution_version"]:
                        errors.append(
                            "clean install package and distribution versions differ: "
                            f"{installed_payload['package_version']!r} != "
                            f"{installed_payload['distribution_version']!r}"
                        )

            if not console_script.is_file():
                errors.append(f"clean install did not create console script: {console_script}")
            else:
                console_result = _run((str(console_script), "--help"), cwd=workdir)
                console_help_returncode = console_result.returncode
                if console_result.returncode != 0:
                    errors.append(
                        "clean-install console script failed: "
                        + (console_result.stderr.strip() or console_result.stdout.strip() or "unknown error")
                    )

    return {
        "ok": not errors,
        "dist_dir": dist_dir.as_posix(),
        "wheel": wheel.name,
        "source_distribution": source_distribution.name,
        "wheel_contents_returncode": checker_returncode,
        "console_help_returncode": console_help_returncode,
        "installed_payload": installed_payload,
        "python_version": sys.version,
        "platform": sys.platform,
        "errors": errors,
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify an Asperitas wheel from a clean isolated environment")
    parser.add_argument("--dist-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--output", type=Path, help="Optionally write the JSON report to this path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = verify_distribution_install(args.dist_dir)
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")

    if args.json or args.output is None:
        print(rendered)
    else:
        print("distribution install passed" if report["ok"] else "distribution install failed")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
