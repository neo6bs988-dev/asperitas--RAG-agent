from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


HYBRID_SOURCE_GROUNDING_FIELDS = (
    "source_id",
    "source_file",
    "source_priority",
    "evidence_label",
    "section",
    "section_heading",
    "section_path",
    "heading_context",
    "embedding_model",
    "embedding_dim",
    "embedding_version",
    "content_hash",
)


@dataclass(frozen=True)
class HybridScoreWeights:
    mvp003: float = 0.70
    vector: float = 0.20
    section: float = 0.05
    metadata: float = 0.05

    def __post_init__(self) -> None:
        values = (self.mvp003, self.vector, self.section, self.metadata)
        if any(value < 0.0 for value in values):
            raise ValueError("hybrid score weights must be non-negative")
        total = sum(values)
        if total <= 0.0:
            raise ValueError("hybrid score weights must have positive total")

    def normalized(self) -> "HybridScoreWeights":
        total = self.mvp003 + self.vector + self.section + self.metadata
        return HybridScoreWeights(
            mvp003=self.mvp003 / total,
            vector=self.vector / total,
            section=self.section / total,
            metadata=self.metadata / total,
        )


@dataclass(frozen=True)
class HybridScoreInputs:
    mvp003_score: float
    vector_score: float
    section_score: float
    metadata_score: float


@dataclass(frozen=True)
class HybridScoreBreakdown:
    hybrid_score: float
    components: dict[str, float] = field(default_factory=dict)


DEFAULT_HYBRID_SCORE_WEIGHTS = HybridScoreWeights()


def clamp_unit(value: float) -> float:
    return max(0.0, min(float(value), 1.0))


def normalize_cosine_similarity(value: float) -> float:
    return clamp_unit((float(value) + 1.0) / 2.0)


def score_metadata_preservation(
    payload: Mapping[str, Any],
    required_fields: tuple[str, ...] = HYBRID_SOURCE_GROUNDING_FIELDS,
) -> float:
    if not required_fields:
        return 1.0
    present = sum(1 for field_name in required_fields if _has_value(payload.get(field_name)))
    return present / len(required_fields)


def combine_hybrid_score(
    inputs: HybridScoreInputs,
    weights: HybridScoreWeights = DEFAULT_HYBRID_SCORE_WEIGHTS,
) -> HybridScoreBreakdown:
    normalized_weights = weights.normalized()
    components = {
        "mvp003": clamp_unit(inputs.mvp003_score) * normalized_weights.mvp003,
        "vector": clamp_unit(inputs.vector_score) * normalized_weights.vector,
        "section": clamp_unit(inputs.section_score) * normalized_weights.section,
        "metadata": clamp_unit(inputs.metadata_score) * normalized_weights.metadata,
    }
    return HybridScoreBreakdown(
        hybrid_score=sum(components.values()),
        components=components,
    )


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True

