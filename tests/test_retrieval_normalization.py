from asperitas_agent.retrieval_normalization import (
    expand_query_aliases,
    normalize_text_for_retrieval,
    tokenize_retrieval,
)


def test_normalize_text_cleans_punctuation_and_case():
    assert normalize_text_for_retrieval("AI_X-Business/Strategy") == "ai x business strategy"


def test_tokenize_keeps_hangul_latin_numbers_and_acronyms():
    tokens = tokenize_retrieval("CRISPR_합성생물학 2026 R&D")

    assert "crispr" in tokens
    assert "합성생물학" in tokens
    assert "2026" in tokens
    assert "r" in tokens
    assert "d" in tokens


def test_expand_query_aliases_is_deterministic():
    aliases = expand_query_aliases("Which source covers LMO regulation trends?")

    assert "lmo 규제 동향" in aliases
    assert aliases == expand_query_aliases("Which source covers LMO regulation trends?")
