from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from asperitas_agent.eval_artifacts import EvalArtifactError, EvalReportArtifact, load_eval_report_artifact


SCHEMA_VERSION = "MVP-017D"


class EvalManifestError(ValueError):
    """Raised when an eval manifest cannot be built, written, or loaded safely."""


@dataclass(frozen=True)
class EvalManifestEntry:
    artifact_path: str
    artifact_id: str
    report_id: str
    ok: bool
    strict_count: int
    report_only_count: int
    failed_count: int
    warnings: tuple[str, ...]
    errors: tuple[str, ...]

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        for field_name in ("artifact_path", "artifact_id", "report_id"):
            if not str(getattr(self, field_name)).strip():
                errors.append(f"{field_name} is required")
        for field_name in ("strict_count", "report_only_count", "failed_count"):
            if not isinstance(getattr(self, field_name), int) or getattr(self, field_name) < 0:
                errors.append(f"{field_name} must be a non-negative integer")
        for field_name in ("warnings", "errors"):
            if not isinstance(getattr(self, field_name), tuple):
                errors.append(f"{field_name} must be a tuple")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {key: list(value) if isinstance(value, tuple) else value for key, value in data.items()}


@dataclass(frozen=True)
class EvalManifest:
    manifest_id: str
    schema_version: str
    created_at_utc: str
    entries: tuple[EvalManifestEntry, ...]
    metadata: dict[str, Any]

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        for field_name in ("manifest_id", "schema_version", "created_at_utc"):
            if not str(getattr(self, field_name)).strip():
                errors.append(f"{field_name} is required")
        if self.schema_version != SCHEMA_VERSION:
            errors.append(f"unsupported schema_version: {self.schema_version}")
        if not isinstance(self.entries, tuple) or not self.entries:
            errors.append("entries must be a non-empty tuple")
        else:
            for entry in self.entries:
                errors.extend(f"{entry.artifact_id}: {error}" for error in entry.validate())
        if not isinstance(self.metadata, dict):
            errors.append("metadata must be an object")
        try:
            json.dumps(self.to_dict(), sort_keys=True)
        except (TypeError, ValueError) as exc:
            errors.append(f"manifest must be JSON-safe: {exc}")
        return tuple(errors)

    def require_valid(self) -> None:
        errors = self.validate()
        if errors:
            raise EvalManifestError("; ".join(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "schema_version": self.schema_version,
            "created_at_utc": self.created_at_utc,
            "entries": [entry.to_dict() for entry in self.entries],
            "metadata": self.metadata,
        }


def build_eval_manifest(artifact_paths: list[str | Path] | tuple[str | Path, ...], metadata: dict[str, Any] | None = None) -> EvalManifest:
    if not artifact_paths:
        raise EvalManifestError("artifact_paths must not be empty")
    entries: list[EvalManifestEntry] = []
    for artifact_path in artifact_paths:
        path = Path(artifact_path)
        try:
            artifact = load_eval_report_artifact(path)
        except EvalArtifactError as exc:
            raise EvalManifestError(f"could not load artifact {path}: {exc}") from exc
        entries.append(_entry_from_artifact(path, artifact))
    manifest = EvalManifest(
        manifest_id=f"eval_manifest:{SCHEMA_VERSION}",
        schema_version=SCHEMA_VERSION,
        created_at_utc=datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        entries=tuple(entries),
        metadata=dict(metadata or {}),
    )
    manifest.require_valid()
    return manifest


def write_eval_manifest(
    manifest: EvalManifest,
    path: str | Path,
    overwrite: bool = False,
    create_dirs: bool = False,
) -> Path:
    if path is None or not str(path).strip():
        raise EvalManifestError("explicit output path is required")
    manifest.require_valid()
    output_path = Path(path)
    if output_path.exists() and not overwrite:
        raise EvalManifestError(f"output path already exists: {output_path}")
    if not output_path.parent.exists():
        if not create_dirs:
            raise EvalManifestError(f"parent directory does not exist: {output_path.parent}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path


def load_eval_manifest(path: str | Path) -> EvalManifest:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise EvalManifestError(f"could not read manifest: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise EvalManifestError(f"malformed manifest JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise EvalManifestError("manifest JSON must be an object")
    required_fields = ("manifest_id", "schema_version", "created_at_utc", "entries", "metadata")
    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise EvalManifestError(f"manifest missing fields: {', '.join(missing)}")
    entries_payload = payload["entries"]
    if not isinstance(entries_payload, list):
        raise EvalManifestError("entries must be a list")
    entries = tuple(_entry_from_payload(item, index) for index, item in enumerate(entries_payload))
    manifest = EvalManifest(
        manifest_id=str(payload["manifest_id"]),
        schema_version=str(payload["schema_version"]),
        created_at_utc=str(payload["created_at_utc"]),
        entries=entries,
        metadata=payload["metadata"],
    )
    manifest.require_valid()
    return manifest


def _entry_from_artifact(path: Path, artifact: EvalReportArtifact) -> EvalManifestEntry:
    return EvalManifestEntry(
        artifact_path=str(path),
        artifact_id=artifact.artifact_id,
        report_id=artifact.report_id,
        ok=artifact.ok,
        strict_count=int(artifact.summary.get("strict_count", 0)),
        report_only_count=int(artifact.summary.get("report_only_count", 0)),
        failed_count=int(artifact.summary.get("failed_count", 0)),
        warnings=tuple(str(warning) for warning in artifact.warnings),
        errors=tuple(str(error) for error in artifact.errors),
    )


def _entry_from_payload(item: Any, index: int) -> EvalManifestEntry:
    if not isinstance(item, dict):
        raise EvalManifestError(f"entries[{index}] must be an object")
    required_fields = (
        "artifact_path",
        "artifact_id",
        "report_id",
        "ok",
        "strict_count",
        "report_only_count",
        "failed_count",
        "warnings",
        "errors",
    )
    missing = [field for field in required_fields if field not in item]
    if missing:
        raise EvalManifestError(f"entries[{index}] missing fields: {', '.join(missing)}")
    return EvalManifestEntry(
        artifact_path=str(item["artifact_path"]),
        artifact_id=str(item["artifact_id"]),
        report_id=str(item["report_id"]),
        ok=bool(item["ok"]),
        strict_count=int(item["strict_count"]),
        report_only_count=int(item["report_only_count"]),
        failed_count=int(item["failed_count"]),
        warnings=tuple(str(warning) for warning in item["warnings"]),
        errors=tuple(str(error) for error in item["errors"]),
    )
