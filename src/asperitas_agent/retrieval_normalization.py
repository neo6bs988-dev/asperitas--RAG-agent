from __future__ import annotations

import re
import unicodedata
from pathlib import PurePosixPath

from .schemas import SourceRecord


TOKEN_RE = re.compile(r"[가-힣]+|[A-Za-z]+(?:&[A-Za-z]+)?|\d+(?:\.\d+)?")

QUERY_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("source priority policy", ("source hierarchy", "source of truth", "evidence hierarchy")),
    ("source of truth hierarchy", ("source hierarchy", "source priority policy", "evidence labels")),
    ("development priorities", ("engineering priorities", "build order", "validation rules")),
    ("legal approval", ("regulatory approval", "wet lab validation", "approval limits")),
    ("regulatory approval", ("legal approval", "wet lab validation", "approval limits")),
    ("wet lab validation", ("wet-lab validation", "legal approval", "regulatory approval")),
    ("ir deck", ("investor deck", "investor narrative", "fundraising deck")),
    ("investor narrative", ("ir deck", "investor deck")),
    ("company introduction", ("asperitas introduction", "asperitas 소개")),
    ("ai study roadmap", ("ai roadmap", "ai 공부 로드맵")),
    ("ai roadmap", ("ai study roadmap", "ai 공부 로드맵")),
    ("china and ai", ("china ai", "china&ai")),
    ("global synthetic biology market outlook", ("2026 2036 market outlook", "synthetic biology market 전망")),
    ("market outlook", ("market 전망", "시장 전망")),
    ("4p analysis", ("4p 분석", "4p framework")),
    ("growth strategy", ("성장 전략", "policy considerations")),
    ("policy considerations", ("정책 고려사항", "growth strategy")),
    ("policy tasks", ("정책 과제", "innovation opportunities")),
    ("innovation opportunities", ("혁신 기회", "policy tasks")),
    ("promotion law", ("육성법", "law implications")),
    ("government r&d investment", ("정부 r&d 투자", "government research investment")),
    ("technology competitiveness", ("기술경쟁력", "technical competitiveness")),
    ("national bio competitiveness", ("국가 바이오 경쟁력", "bio competitiveness")),
    ("lmo regulation trends", ("lmo 규제 동향", "gmo regulation trends")),
    ("biofoundry", ("바이오파운드리", "bio foundry")),
    ("cell free synthetic biology", ("cell-free synthetic biology", "무세포 합성생물학")),
    ("genetic circuit", ("유전자회로", "gene circuit")),
    ("white bio", ("화이트바이오", "white biotechnology")),
    ("drug development", ("신약개발", "new drug development")),
    ("core technologies", ("핵심기술", "application status", "활용 현황")),
    ("antibiotic development", ("항생제 개발", "antibiotics research trends")),
    ("electron flow", ("전자 흐름", "microorganism electrode", "미생물 전극")),
    ("microorganism electrode", ("미생물 전극", "electron flow")),
    ("crispr", ("gene editing", "crispr synthetic biology")),
    ("convergence design strategy", ("융합 설계 전략", "design strategy")),
    ("protein design", ("protein engineering",)),
    ("seed conference", ("seed 후기", "industry intelligence")),
    ("industry intelligence", ("market intelligence", "seed conference")),
    ("ptmc", ("2026 ptmc project",)),
    ("r&d projects", ("rnd projects", "research projects", "p1 rnd projects")),
    ("db integration", ("database integration", "constitution db integration")),
)


def normalize_text_for_retrieval(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text or "")
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"[_/\\|:;,.()\[\]{}]+", " ", normalized)
    normalized = re.sub(r"[-‐‑‒–—]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.casefold().strip()


def tokenize_retrieval(text: str) -> list[str]:
    normalized = normalize_text_for_retrieval(text)
    tokens = [token.casefold() for token in TOKEN_RE.findall(normalized)]
    expanded: list[str] = []
    for token in tokens:
        expanded.append(token)
        if token.endswith("ies") and len(token) > 4:
            expanded.append(token[:-3] + "y")
        elif token.endswith("s") and len(token) > 3 and not token.endswith("ss"):
            expanded.append(token[:-1])
    return list(dict.fromkeys(expanded))


def token_ngrams(tokens: list[str], max_n: int = 3) -> list[str]:
    phrases: list[str] = []
    for size in range(2, max_n + 1):
        for index in range(0, max(len(tokens) - size + 1, 0)):
            phrases.append(" ".join(tokens[index : index + size]))
    return phrases


def expand_query_aliases(text: str) -> list[str]:
    normalized = normalize_text_for_retrieval(text)
    aliases: list[str] = []
    for trigger, expansions in QUERY_ALIASES:
        if normalize_text_for_retrieval(trigger) in normalized:
            aliases.extend(expansions)
    return list(dict.fromkeys(aliases))


def source_aliases(record: SourceRecord) -> list[str]:
    text = normalize_text_for_retrieval(" ".join([record.title, record.original_filename, record.path]))
    aliases: list[str] = []
    path = PurePosixPath(record.path)
    aliases.extend(path.parts)
    aliases.append(path.name)
    aliases.append(path.stem)

    patterns: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("agents", ("source priority policy", "agent architecture", "source governance")),
        ("readme", ("development priorities", "validation rules", "source priority policy")),
        ("universal ai tool master prompt", ("source of truth hierarchy", "evidence hierarchy")),
        ("master constitution", ("source of truth", "legal approval", "regulatory approval", "wet lab validation")),
        ("build guidebook", ("codex ai agent build guide", "source registry", "retrieval evaluation", "advanced rag")),
        ("db integration guide", ("database integration", "db integration", "master constitution db integration")),
        ("ir deck", ("ir deck", "investor deck", "investor narrative", "company positioning")),
        ("소개", ("company introduction", "asperitas introduction")),
        ("ptmc", ("ptmc", "2026 ptmc project")),
        ("p1_rnd_projects", ("r&d projects", "rnd projects", "research projects")),
        ("ai x business strategy", ("ai x business strategy", "ai business strategy")),
        ("ai 공부", ("ai study roadmap", "ai roadmap")),
        ("china&ai", ("china and ai", "china ai")),
        ("시장 전망", ("global synthetic biology market outlook", "2026 2036 market outlook", "market outlook")),
        ("4p", ("4p analysis", "4p framework")),
        ("성장 전략", ("growth strategy", "policy considerations")),
        ("정책 과제", ("policy tasks", "innovation opportunities")),
        ("육성법", ("promotion law", "law implications")),
        ("기술경쟁력", ("technology competitiveness", "government r&d investment")),
        ("정부 r", ("government r&d investment", "government research investment")),
        ("국가 바이오", ("national bio competitiveness", "bio competitiveness")),
        ("lmo", ("lmo regulation trends", "gmo regulation trends", "biosafety regulation")),
        ("바이오파운드리", ("biofoundry", "bio foundry")),
        ("무세포", ("cell free synthetic biology", "cell-free synthetic biology")),
        ("유전자회로", ("genetic circuit", "gene circuit")),
        ("화이트바이오", ("white bio", "white biotechnology")),
        ("신약개발", ("drug development", "new drug development")),
        ("핵심기술", ("core technologies", "application status")),
        ("활용 현황", ("application status", "core technologies")),
        ("항생제", ("antibiotic development", "antibiotics research trends")),
        ("미생물", ("microorganism electrode", "electron flow")),
        ("전자 흐름", ("electron flow", "microorganism electrode")),
        ("crispr", ("crispr", "gene editing", "convergence design strategy")),
        ("융합 설계", ("convergence design strategy", "design strategy")),
        ("protein design", ("protein design", "protein engineering")),
        ("seed", ("seed conference", "seed 후기")),
        ("p5_industry_intelligence", ("industry intelligence", "market intelligence", "conference intelligence")),
    )
    for marker, additions in patterns:
        if normalize_text_for_retrieval(marker) in text:
            aliases.extend(additions)
    return [alias for alias in dict.fromkeys(aliases) if alias]


def normalized_token_set(*texts: str) -> set[str]:
    tokens: set[str] = set()
    for text in texts:
        text_tokens = tokenize_retrieval(text)
        tokens.update(text_tokens)
        tokens.update(token_ngrams(text_tokens, max_n=3))
    return tokens
