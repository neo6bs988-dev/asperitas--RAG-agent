from __future__ import annotations

import re
from dataclasses import dataclass

from .claim_verifier_schema import AtomicClaim


EXTRACTOR_NAME = "v1.5c-deterministic-claim-extractor"
EXTRACTOR_VERSION = "V1.5C-step2"
DEFAULT_REQUIRED_EVIDENCE_TYPE = "retrieved_context_or_source_metadata"
UNVERIFIED_SUPPORT_STATUS = "not_verifiable_from_context"
UNVERIFIED_FAILURE_MODE = "verifier_not_applicable"

_BULLET_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[\.)]\s+|[A-Za-z]\)\s+)")
_CITATION_RE = re.compile(r"\[(?:[A-Za-z]+)?\d+(?:[-,]\s*(?:[A-Za-z]+)?\d+)*\]")
_SPACE_RE = re.compile(r"\s+")
_LIST_SPLIT_RE = re.compile(r"\s+(?:and|also|plus)\s+", re.IGNORECASE)
_LEADING_FILLER_RE = re.compile(r"^(?:bottom line|caution|internal facts?|key evidence|inference|speculation|verification needed)\s*:\s*", re.IGNORECASE)

_ABBREVIATIONS = {
    "al",
    "cf",
    "dr",
    "e.g",
    "etc",
    "fig",
    "i.e",
    "inc",
    "mr",
    "mrs",
    "ms",
    "no",
    "prof",
    "sp",
    "spp",
    "vs",
}

_NON_CLAIM_PREFIXES = (
    "based on",
    "below",
    "first",
    "for example",
    "here are",
    "here is",
    "i can",
    "i will",
    "in summary",
    "let's",
    "next",
    "now",
    "overall",
    "please",
    "the following",
    "this answer",
    "to answer",
)

_NON_CLAIM_EXACT = {
    "hello",
    "hi",
    "thanks",
    "thank you",
    "you are welcome",
}

_CLAIM_SIGNAL_RE = re.compile(
    r"\b("
    r"are|is|was|were|has|have|had|can|could|may|might|must|should|will|would|"
    r"requires?|supports?|contains?|includes?|uses?|shows?|indicates?|suggests?|"
    r"increases?|decreases?|grows?|inhibits?|activates?|binds?|expresses?|produces?|"
    r"associated|correlates?|causes?|measured|detected|validated|blocks?|preserves?"
    r")\b",
    re.IGNORECASE,
)

_BIOLOGY_SIGNAL_RE = re.compile(
    r"\b("
    r"gene|protein|enzyme|species|strain|compound|pathway|assay|phenotype|"
    r"cell|tissue|organism|metabolite|receptor|arabidopsis|escherichia|saccharomyces|"
    r"crispr|dna|rna"
    r")\b",
    re.IGNORECASE,
)

_COMPLIANCE_SIGNAL_RE = re.compile(
    r"\b(cites|nagoya|abs|lmo|gmo|biosafety|biosecurity|license|regulatory|legal|approval|export)\b",
    re.IGNORECASE,
)

_STATUS_SIGNAL_RE = re.compile(r"\b(production|deployed|validated|approved|complete|completed|ready)\b", re.IGNORECASE)
_MEASUREMENT_SIGNAL_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|mg|g|kg|ml|l|um|mm|cm|nm|h|hr|s|min|days?|fold|x)\b", re.IGNORECASE)
_RELATION_SIGNAL_RE = re.compile(r"\b(inhibits?|activates?|binds?|expresses?|produces?|associated with|correlates? with|causes?)\b", re.IGNORECASE)


@dataclass(frozen=True)
class ClaimExtractionConfig:
    min_claim_chars: int = 12
    split_semicolons: bool = True
    split_simple_list_clauses: bool = True


@dataclass(frozen=True)
class _TextUnit:
    text: str
    source_text: str
    line_index: int
    unit_index: int
    locator: str


def extract_atomic_claims(
    answer_text: str,
    *,
    answer_id: str | None = None,
    config: ClaimExtractionConfig | None = None,
) -> list[AtomicClaim]:
    active_config = config or ClaimExtractionConfig()
    claims: list[AtomicClaim] = []
    for unit in _candidate_units(answer_text):
        for fragment in _claim_fragments(unit.text, active_config):
            claim_text = _normalize_claim_text(fragment)
            if not _is_claim_candidate(claim_text, active_config):
                continue
            claim_index = len(claims) + 1
            claim = AtomicClaim(
                claim_id=_claim_id(answer_id, claim_index),
                answer_id=answer_id or "",
                claim_text=claim_text,
                claim_type=_claim_type(claim_text),
                source_sentence=unit.source_text,
                sentence_index=unit.unit_index,
                cited_source_ids=(),
                cited_span_ids=(),
                citation_keys=_citation_keys(claim_text),
                required_evidence_type=DEFAULT_REQUIRED_EVIDENCE_TYPE,
                detected_entities=(),
                compliance_tags=(),
                support_status=UNVERIFIED_SUPPORT_STATUS,
                confidence=None,
                verifier_notes="Extracted deterministically from answer text; support has not been verified.",
                failure_mode=UNVERIFIED_FAILURE_MODE,
                blocking=False,
                metadata={
                    "extractor_name": EXTRACTOR_NAME,
                    "extractor_version": EXTRACTOR_VERSION,
                    "claim_index": claim_index,
                    "source_line_index": unit.line_index,
                    "source_unit_index": unit.unit_index,
                    "source_locator": unit.locator,
                },
            )
            claim.require_valid()
            claims.append(claim)
    return claims


def _candidate_units(answer_text: str) -> list[_TextUnit]:
    units: list[_TextUnit] = []
    unit_index = 0
    for line_index, raw_line in enumerate((answer_text or "").splitlines()):
        line = raw_line.strip()
        if not line:
            continue
        stripped = _strip_markup(line)
        if not stripped or _is_header(stripped) or _is_filler(stripped):
            continue
        source_text = stripped
        if _BULLET_RE.match(stripped):
            stripped = _BULLET_RE.sub("", stripped).strip()
            if stripped and not _is_header(stripped) and not _is_filler(stripped):
                units.append(_TextUnit(text=stripped, source_text=source_text, line_index=line_index, unit_index=unit_index, locator=f"line:{line_index + 1}"))
                unit_index += 1
            continue
        for sentence in _split_sentences(stripped):
            if sentence and not _is_header(sentence) and not _is_filler(sentence):
                units.append(_TextUnit(text=sentence, source_text=source_text, line_index=line_index, unit_index=unit_index, locator=f"line:{line_index + 1}"))
                unit_index += 1
    return units


def _claim_fragments(text: str, config: ClaimExtractionConfig) -> list[str]:
    fragments = [text]
    if config.split_semicolons:
        fragments = [part for fragment in fragments for part in _split_semicolons(fragment)]
    if config.split_simple_list_clauses:
        fragments = [part for fragment in fragments for part in _split_simple_list_clauses(fragment)]
    return fragments


def _strip_markup(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^#{1,6}\s+", "", text)
    text = _LEADING_FILLER_RE.sub("", text)
    return _compact(text)


def _split_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    start = 0
    index = 0
    while index < len(text):
        char = text[index]
        if char in ".!?" and _is_sentence_boundary(text, index):
            end = index + 1
            while end < len(text) and text[end] in "\"')]}":
                end += 1
            while end < len(text) and text[end].isspace() and _starts_with_citation(text, end):
                citation_end = text.find("]", end)
                if citation_end == -1:
                    break
                end = citation_end + 1
            sentences.append(text[start:end].strip())
            start = end
            while start < len(text) and text[start].isspace():
                start += 1
            index = start
            continue
        index += 1
    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def _is_sentence_boundary(text: str, index: int) -> bool:
    if index > 0 and index + 1 < len(text) and text[index - 1].isdigit() and text[index + 1].isdigit():
        return False
    if index > 0 and text[index - 1].isupper() and (index == 1 or text[index - 2].isspace()) and _next_word_starts_lowercase(text, index + 1):
        return False
    token = _previous_token(text[:index])
    if token.casefold() in _ABBREVIATIONS:
        return False
    next_index = index + 1
    while next_index < len(text) and text[next_index] in "\"')]}":
        next_index += 1
    if next_index >= len(text):
        return True
    if len(token) == 1 and token.isupper() and _next_word_starts_lowercase(text, next_index):
        return False
    return text[next_index].isspace()


def _previous_token(prefix: str) -> str:
    match = re.search(r"([A-Za-z][A-Za-z.]*)$", prefix.strip())
    return match.group(1).rstrip(".") if match else ""


def _next_word_starts_lowercase(text: str, index: int) -> bool:
    while index < len(text) and text[index].isspace():
        index += 1
    return index < len(text) and text[index].islower()


def _starts_with_citation(text: str, index: int) -> bool:
    return bool(_CITATION_RE.match(text[index:].lstrip()))


def _split_semicolons(text: str) -> list[str]:
    if ";" not in text:
        return [text]
    parts = [_normalize_claim_text(part) for part in text.split(";")]
    return [part for part in parts if part]


def _split_simple_list_clauses(text: str) -> list[str]:
    matches = list(_LIST_SPLIT_RE.finditer(text))
    if not matches or len(matches) > 1:
        return [text]
    first, second = _LIST_SPLIT_RE.split(text, maxsplit=1)
    if _has_claim_signal(first) and _has_claim_signal(second):
        return [_normalize_claim_text(first), _normalize_claim_text(second)]
    return [text]


def _normalize_claim_text(text: str) -> str:
    text = _compact(text.strip(" -;\t\r\n"))
    if text and text[-1] not in ".!?]":
        text += "."
    return text


def _is_claim_candidate(text: str, config: ClaimExtractionConfig) -> bool:
    compact = _compact(text).strip()
    if len(compact) < config.min_claim_chars:
        return False
    if _is_filler(compact) or _is_header(compact) or _is_citation_only(compact):
        return False
    return _has_claim_signal(compact)


def _has_claim_signal(text: str) -> bool:
    return bool(_CLAIM_SIGNAL_RE.search(text) or _MEASUREMENT_SIGNAL_RE.search(text))


def _is_filler(text: str) -> bool:
    lowered = _compact(text).casefold().strip(" .:")
    if lowered in _NON_CLAIM_EXACT:
        return True
    return any(lowered.startswith(prefix) for prefix in _NON_CLAIM_PREFIXES)


def _is_header(text: str) -> bool:
    compact = _compact(text).strip()
    if not compact or _is_citation_only(compact):
        return True
    if compact.endswith(":"):
        return True
    if len(compact.split()) <= 5 and not _has_claim_signal(compact) and not compact.endswith((".", "!", "?")):
        return True
    return False


def _is_citation_only(text: str) -> bool:
    compact = _compact(text).strip()
    return bool(compact) and not _CITATION_RE.sub("", compact).strip(" .;,")


def _citation_keys(text: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(match.group(0) for match in _CITATION_RE.finditer(text)))


def _claim_type(text: str) -> str:
    if _COMPLIANCE_SIGNAL_RE.search(text):
        return "compliance_sensitive"
    if _STATUS_SIGNAL_RE.search(text):
        return "status"
    if _MEASUREMENT_SIGNAL_RE.search(text):
        return "measurement"
    if _RELATION_SIGNAL_RE.search(text) or _BIOLOGY_SIGNAL_RE.search(text):
        return "biology_relation"
    return "sourced_fact"


def _claim_id(answer_id: str | None, claim_index: int) -> str:
    if answer_id:
        safe_answer_id = re.sub(r"[^A-Za-z0-9_-]+", "-", answer_id).strip("-")
        return f"{safe_answer_id}-C{claim_index}"
    return f"C{claim_index}"


def _compact(text: str) -> str:
    return _SPACE_RE.sub(" ", text or "").strip()
