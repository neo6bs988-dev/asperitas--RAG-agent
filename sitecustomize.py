"""Safely expose the repository's ``src`` layout to local Python processes.

Python imports ``sitecustomize`` automatically when this repository root is on
``sys.path``. This module enables commands such as:

    python -m asperitas_agent.cli

from a plain repository checkout before editable installation.

Security and behavior boundaries:

- only the repository-local ``src`` directory may be added;
- symlink escape outside the repository is rejected;
- the expected project and package markers must exist;
- equivalent ``sys.path`` entries are normalized to one canonical first entry;
- no project module is imported;
- no files, environment variables, network resources, or external systems are
  modified;
- bootstrap failure must not break Python startup.

Set ``ASPERITAS_DISABLE_REPO_BOOTSTRAP=1`` to disable this compatibility layer.
Editable installation remains the preferred development configuration.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Final


_DISABLE_ENV: Final[str] = "ASPERITAS_DISABLE_REPO_BOOTSTRAP"
_TRUE_VALUES: Final[frozenset[str]] = frozenset(
    {
        "1",
        "on",
        "true",
        "yes",
    }
)

_REPOSITORY_MARKER: Final[str] = "pyproject.toml"
_PACKAGE_NAME: Final[str] = "asperitas_agent"
_PACKAGE_MARKER: Final[str] = "__init__.py"


def _bootstrap_disabled() -> bool:
    """Return whether repository-local path bootstrapping is disabled."""

    value = os.environ.get(_DISABLE_ENV, "")
    return value.strip().casefold() in _TRUE_VALUES


def _path_key(path: str | os.PathLike[str]) -> str:
    """Return a normalized path key suitable for duplicate detection."""

    raw_path = os.fspath(path) or os.curdir
    return os.path.normcase(os.path.realpath(raw_path))


def _validated_src_directory() -> Path | None:
    """Return the trusted repository ``src`` path, or ``None`` if invalid."""

    repository_root = Path(__file__).resolve(strict=True).parent
    project_marker = repository_root / _REPOSITORY_MARKER

    if not project_marker.is_file():
        return None

    src_directory = (repository_root / "src").resolve(strict=True)

    try:
        src_directory.relative_to(repository_root)
    except ValueError:
        # Reject a symlinked ``src`` directory that escapes the repository.
        return None

    package_marker = src_directory / _PACKAGE_NAME / _PACKAGE_MARKER
    if not package_marker.is_file():
        return None

    return src_directory


def _path_is_registered(target: Path) -> bool:
    """Return whether an equivalent path is already present in ``sys.path``."""

    target_key = _path_key(target)

    for entry in sys.path:
        try:
            if _path_key(entry) == target_key:
                return True
        except (OSError, TypeError, ValueError):
            # Ignore malformed or non-filesystem entries owned by other tools.
            continue

    return False


def _prepend_unique_path(target: Path) -> None:
    """Place ``target`` first in ``sys.path`` and remove equivalent duplicates."""

    target_key = _path_key(target)
    retained_entries: list[object] = []

    for entry in sys.path:
        try:
            if _path_key(entry) == target_key:
                continue
        except (OSError, TypeError, ValueError):
            # Preserve malformed or non-filesystem entries owned by other tools.
            pass
        retained_entries.append(entry)

    sys.path[:] = [str(target), *retained_entries]


def _bootstrap_src_layout() -> None:
    """Normalize the validated repository ``src`` path to first precedence."""

    if _bootstrap_disabled():
        return

    src_directory = _validated_src_directory()
    if src_directory is None:
        return

    # ``src`` must precede repository-root compatibility shims so imports use
    # the canonical package implementation even when editable-install metadata
    # already registered ``src`` later in ``sys.path``.
    _prepend_unique_path(src_directory)


try:
    _bootstrap_src_layout()
except (OSError, RuntimeError, TypeError, ValueError):
    # ``sitecustomize`` executes during interpreter startup. A compatibility
    # bootstrap failure must not prevent Python itself from starting.
    pass
