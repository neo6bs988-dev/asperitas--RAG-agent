from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import sitecustomize as bootstrap

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "src").resolve()
CANONICAL_INIT = SRC / "asperitas_agent" / "__init__.py"


def _python_environment(*, pythonpath: Path, updates: dict[str, str] | None = None) -> dict[str, str]:
    environment = os.environ.copy()
    existing = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = str(pythonpath) + (os.pathsep + existing if existing else "")
    environment["PYTHONUTF8"] = "1"
    if updates:
        environment.update(updates)
    return environment


def _run_python(code: str, *, cwd: Path, environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=cwd,
        env=environment,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "On", "  true  "])
def test_bootstrap_disabled_accepts_documented_truthy_values(monkeypatch, value):
    monkeypatch.setenv("ASPERITAS_DISABLE_REPO_BOOTSTRAP", value)
    assert bootstrap._bootstrap_disabled() is True


@pytest.mark.parametrize("value", ["", "0", "false", "off", "no", "unexpected"])
def test_bootstrap_disabled_rejects_other_values(monkeypatch, value):
    monkeypatch.setenv("ASPERITAS_DISABLE_REPO_BOOTSTRAP", value)
    assert bootstrap._bootstrap_disabled() is False


def test_validated_src_directory_resolves_canonical_repository_path():
    assert bootstrap._validated_src_directory() == SRC


def test_missing_project_marker_fails_closed(tmp_path, monkeypatch):
    fake_sitecustomize = tmp_path / "sitecustomize.py"
    fake_sitecustomize.write_text("# marker\n", encoding="utf-8")
    (tmp_path / "src" / "asperitas_agent").mkdir(parents=True)
    (tmp_path / "src" / "asperitas_agent" / "__init__.py").write_text("", encoding="utf-8")
    monkeypatch.setattr(bootstrap, "__file__", str(fake_sitecustomize))

    assert bootstrap._validated_src_directory() is None


def test_missing_package_marker_fails_closed(tmp_path, monkeypatch):
    fake_sitecustomize = tmp_path / "sitecustomize.py"
    fake_sitecustomize.write_text("# marker\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[build-system]\n", encoding="utf-8")
    (tmp_path / "src" / "asperitas_agent").mkdir(parents=True)
    monkeypatch.setattr(bootstrap, "__file__", str(fake_sitecustomize))

    assert bootstrap._validated_src_directory() is None


def test_symlink_escape_is_rejected(tmp_path, monkeypatch):
    repository = tmp_path / "repository"
    outside = tmp_path / "outside" / "src"
    repository.mkdir()
    (repository / "sitecustomize.py").write_text("# marker\n", encoding="utf-8")
    (repository / "pyproject.toml").write_text("[build-system]\n", encoding="utf-8")
    (outside / "asperitas_agent").mkdir(parents=True)
    (outside / "asperitas_agent" / "__init__.py").write_text("", encoding="utf-8")

    try:
        (repository / "src").symlink_to(outside, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"directory symlink unavailable on this platform: {exc}")

    monkeypatch.setattr(bootstrap, "__file__", str(repository / "sitecustomize.py"))
    assert bootstrap._validated_src_directory() is None


def test_path_registration_tolerates_malformed_entries(monkeypatch):
    monkeypatch.setattr(sys, "path", [object(), str(SRC)])
    assert bootstrap._path_is_registered(SRC) is True


def test_bootstrap_inserts_canonical_src_once(monkeypatch):
    filtered = [entry for entry in sys.path if bootstrap._path_key(entry) != bootstrap._path_key(SRC)]
    monkeypatch.setattr(sys, "path", filtered)
    monkeypatch.delenv("ASPERITAS_DISABLE_REPO_BOOTSTRAP", raising=False)

    bootstrap._bootstrap_src_layout()
    bootstrap._bootstrap_src_layout()

    assert bootstrap._path_key(sys.path[0]) == bootstrap._path_key(SRC)
    assert sum(bootstrap._path_key(entry) == bootstrap._path_key(SRC) for entry in sys.path) == 1


def test_disable_environment_prevents_insertion(monkeypatch):
    filtered = [entry for entry in sys.path if bootstrap._path_key(entry) != bootstrap._path_key(SRC)]
    monkeypatch.setattr(sys, "path", filtered)
    monkeypatch.setenv("ASPERITAS_DISABLE_REPO_BOOTSTRAP", "1")

    bootstrap._bootstrap_src_layout()

    assert all(bootstrap._path_key(entry) != bootstrap._path_key(SRC) for entry in sys.path)


def test_fresh_repository_process_imports_canonical_src_package():
    code = """
from pathlib import Path
import asperitas_agent
print(Path(asperitas_agent.__file__).resolve())
""".strip()
    result = _run_python(
        code,
        cwd=ROOT,
        environment=_python_environment(pythonpath=ROOT, updates={"ASPERITAS_DISABLE_REPO_BOOTSTRAP": "0"}),
    )

    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip().splitlines()[-1]) == CANONICAL_INIT


def test_disable_environment_is_honored_in_fresh_process(tmp_path):
    copied = tmp_path / "sitecustomize.py"
    copied.write_text((ROOT / "sitecustomize.py").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[build-system]\n", encoding="utf-8")
    fake_src = tmp_path / "src"
    (fake_src / "asperitas_agent").mkdir(parents=True)
    (fake_src / "asperitas_agent" / "__init__.py").write_text("", encoding="utf-8")

    code = f"""
import json
import os
import sys
canonical = os.path.normcase(os.path.realpath({str(fake_src)!r}))
paths = [os.path.normcase(os.path.realpath(path or os.curdir)) for path in sys.path]
print(json.dumps({{"canonical_present": canonical in paths}}))
""".strip()
    result = _run_python(
        code,
        cwd=tmp_path,
        environment=_python_environment(pythonpath=tmp_path, updates={"ASPERITAS_DISABLE_REPO_BOOTSTRAP": "1"}),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload == {"canonical_present": False}


def test_startup_survives_missing_src_directory(tmp_path):
    copied = tmp_path / "sitecustomize.py"
    copied.write_text((ROOT / "sitecustomize.py").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[build-system]\n", encoding="utf-8")

    result = _run_python(
        "print('startup-ok')",
        cwd=tmp_path,
        environment=_python_environment(pythonpath=tmp_path),
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().splitlines()[-1] == "startup-ok"
