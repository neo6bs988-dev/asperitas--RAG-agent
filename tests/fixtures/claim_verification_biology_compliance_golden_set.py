from __future__ import annotations

from dataclasses import dataclass

from asperitas_agent.claim_verifier_schema import AtomicClaim, BiologyEntity, EvidenceSpan


GOLDEN_SET_ID = "v1_5f_biology_compliance_claim_verification_golden_set"
ANSWER_ID = "V1_5F_A1"
QUESTION = "Which fixture biology and compliance claims are supported by cited evidence?"

EXPECTED_STATUS_BY_CLAIM_ID = {
    "C1": "supported",
    "C2": "unsupported",
    "C3": "contradicted",
    "C4": "partially_supported",
    "C5": "not_verifiable_from_context",
    "C6": "citation_mismatch",
    "C7": "supported",
    "C8": "supported",
    "C9": "supported",
}

EXPECTED_FAILURE_MODE_BY_CLAIM_ID = {
    "C1": None,
    "C2": "cited_span_does_not_support_claim",
    "C3": "claim_contradicts_cited_span",
    "C4": "overgeneralization",
    "C5": "evidence_span_missing",
    "C6": "citation_points_to_wrong_source",
    "C7": None,
    "C8": None,
    "C9": None,
}

EXPECTED_COMPLIANCE_TAGS = (
    "biosafety",
    "cites",
    "export_or_security_sensitive_biology",
    "ip_license",
    "nagoya_abs",
)

EXPECTED_SUMMARY_COUNTS = {
    "total_claims": 9,
    "supported_claims": 4,
    "partially_supported_claims": 1,
    "unsupported_claims": 1,
    "contradicted_claims": 1,
    "citation_missing_claims": 0,
    "citation_mismatch_claims": 1,
    "ambiguous_claims": 0,
    "not_verifiable_from_context_claims": 1,
    "compliance_blocked_claims": 0,
}


@dataclass(frozen=True)
class GoldenSetCase:
    case_id: str
    claim: AtomicClaim
    evidence_spans: tuple[EvidenceSpan, ...]
    expected_support_status: str
    expected_failure_mode: str | None
    truth_boundary_notes: tuple[str, ...]


def biology_compliance_golden_set_cases() -> tuple[GoldenSetCase, ...]:
    return (
        _case(
            case_id="biology_supported_correct_citation",
            claim_id="C1",
            claim_text="Arabidopsis thaliana expresses FLC in leaf tissue [E1].",
            claim_type="biology_relation",
            citation_key="[E1]",
            span_id="E1",
            evidence_text="Arabidopsis thaliana expresses FLC in leaf tissue.",
            entities=(
                _entity("Arabidopsis thaliana", "species", "E1"),
                _entity("FLC", "gene", "E1"),
                _entity("leaf tissue", "tissue_or_cell_type", "E1"),
            ),
            expected_status="supported",
            expected_failure_mode=None,
        ),
        _case(
            case_id="biology_unsupported_plausible_citation",
            claim_id="C2",
            claim_text="Arabidopsis thaliana FLC activates a salinity tolerance pathway [E2].",
            claim_type="biology_relation",
            citation_key="[E2]",
            span_id="E2",
            evidence_text="Arabidopsis thaliana was included as a plant model in the fixture.",
            entities=(
                _entity("Arabidopsis thaliana", "species", "E2"),
                _entity("FLC", "gene", "E2"),
                _entity("salinity tolerance pathway", "pathway", "E2"),
            ),
            expected_status="unsupported",
            expected_failure_mode="cited_span_does_not_support_claim",
        ),
        _case(
            case_id="biology_contradicted_directional_claim",
            claim_id="C3",
            claim_text="Treatment increases pathway activity [E3].",
            claim_type="biology_relation",
            citation_key="[E3]",
            span_id="E3",
            evidence_text="Treatment decreases pathway activity in the assay.",
            entities=(_entity("pathway activity", "pathway", "E3"),),
            expected_status="contradicted",
            expected_failure_mode="claim_contradicts_cited_span",
        ),
        _case(
            case_id="biology_partially_supported_scoped_claim",
            claim_id="C4",
            claim_text="The extract reduces fungal growth and induces apoptosis in plant callus cells [E4].",
            claim_type="biology_relation",
            citation_key="[E4]",
            span_id="E4",
            evidence_text="The extract reduces fungal growth in an agar assay.",
            entities=(
                _entity("fungal growth", "phenotype", "E4"),
                _entity("agar assay", "assay", "E4"),
                _entity("plant callus cells", "tissue_or_cell_type", "E4"),
            ),
            expected_status="partially_supported",
            expected_failure_mode="overgeneralization",
        ),
        _case(
            case_id="biology_not_verifiable_missing_experimental_evidence",
            claim_id="C5",
            claim_text="Compound X was confirmed by LC-MS in the assay [E5].",
            claim_type="method",
            citation_key="[E5]",
            span_id="E5",
            evidence_text="N/A",
            entities=(
                _entity("Compound X", "compound", "E5"),
                _entity("LC-MS", "experimental_method", "E5"),
            ),
            expected_status="not_verifiable_from_context",
            expected_failure_mode="evidence_span_missing",
        ),
        GoldenSetCase(
            case_id="biology_citation_mismatch_wrong_span",
            claim=_claim(
                claim_id="C6",
                claim_text="The enzyme assay detects laccase activity in fungal extracts [E6].",
                claim_type="biology_relation",
                citation_key="[E6]",
                span_id="E6",
                entities=(
                    _entity("enzyme assay", "assay", "E6"),
                    _entity("laccase activity", "protein", "E6_SUPPORT"),
                    _entity("fungal extracts", "organism_or_source_material", "E6_SUPPORT"),
                ),
                truth_boundary_notes=("support exists in fixture evidence but not in the cited span",),
            ),
            evidence_spans=(
                _span(
                    source_id="BIO-SRC-06-WRONG",
                    span_id="E6",
                    citation_key="[E6]",
                    evidence_text="The fixture source describes sample storage metadata.",
                    chunk_id="bio-compliance-chunk-06-wrong",
                    section_path=("Golden set", "Biology", "Storage metadata"),
                ),
                _span(
                    source_id="BIO-SRC-06-SUPPORT",
                    span_id="E6_SUPPORT",
                    citation_key="[E6_SUPPORT]",
                    evidence_text="The enzyme assay detects laccase activity in fungal extracts.",
                    chunk_id="bio-compliance-chunk-06-support",
                    section_path=("Golden set", "Biology", "Assay support"),
                ),
            ),
            expected_support_status="citation_mismatch",
            expected_failure_mode="citation_points_to_wrong_source",
            truth_boundary_notes=("support exists in fixture evidence but not in the cited span",),
        ),
        _case(
            case_id="compliance_biosafety_tag_metadata_only",
            claim_id="C7",
            claim_text="The biosafety review note says the organism-handling plan requires institutional review before wet-lab use [E7].",
            claim_type="compliance_sensitive",
            citation_key="[E7]",
            span_id="E7",
            evidence_text="The biosafety review note says the organism-handling plan requires institutional review before wet-lab use.",
            entities=(_entity("organism-handling plan", "experimental_method", "E7"),),
            compliance_tags=("biosafety",),
            license_tags=("fixture_source_permission",),
            expected_status="supported",
            expected_failure_mode=None,
            truth_boundary_notes=("biosafety is a fixture metadata flag, not an approval conclusion",),
        ),
        _case(
            case_id="compliance_nagoya_cites_tags_metadata_only",
            claim_id="C8",
            claim_text="The source-permission note flags CITES and Nagoya ABS review for specimen sourcing [E8].",
            claim_type="compliance_sensitive",
            citation_key="[E8]",
            span_id="E8",
            evidence_text="The source-permission note flags CITES and Nagoya ABS review for specimen sourcing.",
            entities=(_entity("specimen sourcing", "organism_or_source_material", "E8"),),
            compliance_tags=("cites", "nagoya_abs"),
            license_tags=("source_permission_required",),
            expected_status="supported",
            expected_failure_mode=None,
            truth_boundary_notes=("CITES and Nagoya ABS are fixture flags only",),
        ),
        _case(
            case_id="compliance_dual_use_license_tags_metadata_only",
            claim_id="C9",
            claim_text="The fixture labels the enzyme-engineering note as dual-use sensitive and source-permission restricted [E9].",
            claim_type="compliance_sensitive",
            citation_key="[E9]",
            span_id="E9",
            evidence_text="The fixture labels the enzyme-engineering note as dual-use sensitive and source-permission restricted.",
            entities=(_entity("enzyme-engineering note", "experimental_method", "E9"),),
            compliance_tags=("export_or_security_sensitive_biology", "ip_license"),
            license_tags=("source_permission_required", "fixture_only"),
            expected_status="supported",
            expected_failure_mode=None,
            truth_boundary_notes=("dual-use and license tags are passive metadata, not permission or legal conclusions",),
        ),
    )


def golden_set_claims() -> tuple[AtomicClaim, ...]:
    return tuple(case.claim for case in biology_compliance_golden_set_cases())


def golden_set_evidence_by_claim_id() -> dict[str, tuple[EvidenceSpan, ...]]:
    return {case.claim.claim_id: case.evidence_spans for case in biology_compliance_golden_set_cases()}


def _case(
    *,
    case_id: str,
    claim_id: str,
    claim_text: str,
    claim_type: str,
    citation_key: str,
    span_id: str,
    evidence_text: str,
    entities: tuple[BiologyEntity, ...],
    compliance_tags: tuple[str, ...] = (),
    license_tags: tuple[str, ...] = ("fixture_public",),
    expected_status: str,
    expected_failure_mode: str | None,
    truth_boundary_notes: tuple[str, ...] = ("fixture behavior label only",),
) -> GoldenSetCase:
    return GoldenSetCase(
        case_id=case_id,
        claim=_claim(
            claim_id=claim_id,
            claim_text=claim_text,
            claim_type=claim_type,
            citation_key=citation_key,
            span_id=span_id,
            entities=entities,
            compliance_tags=compliance_tags,
            truth_boundary_notes=truth_boundary_notes,
        ),
        evidence_spans=(
            _span(
                source_id=f"BIO-SRC-{claim_id[1:]:0>2}",
                span_id=span_id,
                citation_key=citation_key,
                evidence_text=evidence_text,
                chunk_id=f"bio-compliance-chunk-{claim_id[1:]:0>2}",
                section_path=("Golden set", "Biology compliance", case_id),
                license_tags=license_tags,
                compliance_tags=compliance_tags,
            ),
        ),
        expected_support_status=expected_status,
        expected_failure_mode=expected_failure_mode,
        truth_boundary_notes=truth_boundary_notes,
    )


def _claim(
    *,
    claim_id: str,
    claim_text: str,
    claim_type: str,
    citation_key: str,
    span_id: str,
    entities: tuple[BiologyEntity, ...],
    compliance_tags: tuple[str, ...] = (),
    truth_boundary_notes: tuple[str, ...] = ("fixture behavior label only",),
) -> AtomicClaim:
    return AtomicClaim(
        claim_id=claim_id,
        answer_id=ANSWER_ID,
        claim_text=claim_text,
        claim_type=claim_type,
        source_sentence=claim_text,
        sentence_index=int(claim_id[1:]) - 1,
        cited_source_ids=(),
        cited_span_ids=(),
        citation_keys=(citation_key,),
        required_evidence_type="fixture_claim_evidence_only",
        detected_entities=entities,
        compliance_tags=compliance_tags,
        support_status="not_verifiable_from_context",
        confidence=None,
        verifier_notes="Fixture claim awaiting deterministic support classification.",
        failure_mode="verifier_not_applicable",
        blocking=False,
        metadata={
            "golden_set_id": GOLDEN_SET_ID,
            "golden_set_case_id": claim_id,
            "biology_entity_types": tuple(sorted({entity.entity_type for entity in entities})),
            "truth_boundary_notes": truth_boundary_notes,
        },
    )


def _span(
    *,
    source_id: str,
    span_id: str,
    citation_key: str,
    evidence_text: str,
    chunk_id: str,
    section_path: tuple[str, ...],
    license_tags: tuple[str, ...] = ("fixture_public",),
    compliance_tags: tuple[str, ...] = (),
) -> EvidenceSpan:
    return EvidenceSpan(
        source_id=source_id,
        span_id=span_id,
        document_title="V1.5F biology compliance verifier fixture",
        section="Biology compliance golden set",
        locator=f"fixture:{span_id}",
        evidence_text_hash_or_excerpt=evidence_text,
        metadata={
            "golden_set_id": GOLDEN_SET_ID,
            "source_priority": "P3",
            "fixture_source_rights": "synthetic_fixture_text",
        },
        license_tags=license_tags,
        compliance_tags=compliance_tags,
        retrieval_rank=1,
        retrieval_score=1.0,
        citation_key=citation_key,
        chunk_id=chunk_id,
        source_path=f"tests/fixtures/{GOLDEN_SET_ID}.py::{span_id}",
        section_heading=section_path[-1],
        section_path=section_path,
    )


def _entity(entity_text: str, entity_type: str, span_id: str) -> BiologyEntity:
    return BiologyEntity(
        entity_text=entity_text,
        entity_type=entity_type,
        normalized_label=entity_text,
        source_span_ids=(span_id,),
        confidence=1.0,
        metadata={"golden_set_id": GOLDEN_SET_ID},
    )
