from __future__ import annotations

from dataclasses import dataclass
from typing import Any

RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
DATA_CLASSES = {"PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"}
EFFECT_CEILINGS = {"NONE", "READ"}


@dataclass(frozen=True)
class ShadowCase:
    case_id: str
    query: str
    top_k: int
    repetitions: int
    risk: str
    data_class: str
    expected_statuses: tuple[str, ...]
    require_evidence: bool
    require_citation_integrity: bool
    slices: dict[str, str]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ShadowCase":
        risk = str(value["risk"]).upper()
        data_class = str(value["data_class"]).upper()
        if risk not in RISK_LEVELS:
            raise ValueError(f"invalid risk: {risk}")
        if data_class not in DATA_CLASSES:
            raise ValueError(f"invalid data class: {data_class}")
        top_k = int(value["top_k"])
        repetitions = int(value["repetitions"])
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        if repetitions <= 0:
            raise ValueError("repetitions must be positive")
        return cls(
            case_id=str(value["case_id"]),
            query=str(value["query"]),
            top_k=top_k,
            repetitions=repetitions,
            risk=risk,
            data_class=data_class,
            expected_statuses=tuple(
                str(item) for item in value["expected_statuses"]
            ),
            require_evidence=bool(value["require_evidence"]),
            require_citation_integrity=bool(
                value["require_citation_integrity"]
            ),
            slices={
                str(key): str(raw)
                for key, raw in dict(value.get("slices", {})).items()
            },
        )


@dataclass(frozen=True)
class ShadowPolicy:
    effect_ceiling: str
    provider_export_enabled: bool
    network_egress_enabled: bool
    content_capture_enabled: bool
    mutation_prohibited: bool
    minimum_repetitions: int
    determinism_rate_min: float
    citation_integrity_rate_min: float
    trace_validity_rate_min: float
    privacy_rate_min: float
    maximum_latency_ratio: float
    minimum_latency_ms_for_ratio: float
    maximum_latency_absolute_delta_ms: float
    maximum_status_rate_delta: float

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ShadowPolicy":
        effect_ceiling = str(value["effect_ceiling"]).upper()
        if effect_ceiling not in EFFECT_CEILINGS:
            raise ValueError(f"invalid effect ceiling: {effect_ceiling}")
        instance = cls(
            effect_ceiling=effect_ceiling,
            provider_export_enabled=bool(
                value["provider_export_enabled"]
            ),
            network_egress_enabled=bool(value["network_egress_enabled"]),
            content_capture_enabled=bool(
                value["content_capture_enabled"]
            ),
            mutation_prohibited=bool(value["mutation_prohibited"]),
            minimum_repetitions=int(value["minimum_repetitions"]),
            determinism_rate_min=float(value["determinism_rate_min"]),
            citation_integrity_rate_min=float(
                value["citation_integrity_rate_min"]
            ),
            trace_validity_rate_min=float(
                value["trace_validity_rate_min"]
            ),
            privacy_rate_min=float(value["privacy_rate_min"]),
            maximum_latency_ratio=float(value["maximum_latency_ratio"]),
            minimum_latency_ms_for_ratio=float(
                value["minimum_latency_ms_for_ratio"]
            ),
            maximum_latency_absolute_delta_ms=float(
                value["maximum_latency_absolute_delta_ms"]
            ),
            maximum_status_rate_delta=float(
                value["maximum_status_rate_delta"]
            ),
        )
        for field_name in (
            "determinism_rate_min",
            "citation_integrity_rate_min",
            "trace_validity_rate_min",
            "privacy_rate_min",
            "maximum_status_rate_delta",
        ):
            raw = float(getattr(instance, field_name))
            if not 0.0 <= raw <= 1.0:
                raise ValueError(f"{field_name} must be in [0, 1]")
        if instance.minimum_repetitions <= 0:
            raise ValueError("minimum_repetitions must be positive")
        if instance.maximum_latency_ratio < 1.0:
            raise ValueError("maximum_latency_ratio must be >= 1")
        if instance.minimum_latency_ms_for_ratio < 0.0:
            raise ValueError(
                "minimum_latency_ms_for_ratio must be non-negative"
            )
        if instance.maximum_latency_absolute_delta_ms < 0.0:
            raise ValueError(
                "maximum_latency_absolute_delta_ms must be non-negative"
            )
        return instance
