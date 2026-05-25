"""Exploratory keyword heuristics — not a substitute for manual coding (see codebook_cs_ja.md)."""

from __future__ import annotations

import re
from typing import Any

# --- VAR-A proxies (language-specific; \b only where word boundaries apply) ---

ACTION_EN = {
    "obey": re.compile(
        r"\b(obey|comply|follow the ban|abide by the ban)\b", re.I
    ),
    "secret_bury": re.compile(
        r"\b(secret(ly)? bury|bury in secret|covert burial)\b", re.I
    ),
    "legal_challenge": re.compile(
        r"\b(appeal|court|legal challenge|judicial review|lawsuit)\b", re.I
    ),
    "compromise": re.compile(
        r"\b(compromise|supervised|private burial|mediat(e|ion))\b", re.I
    ),
}

ACTION_CS = {
    "obey": re.compile(
        r"(podřídit|dodržet\s+zákaz|dodržení\s+zákazu|respektovat\s+zákaz|uposlechnout\s+zákazu)",
        re.I,
    ),
    "secret_bury": re.compile(
        r"(tajně\s+pohřb|tajní\s+pohřeb|pohřbít\s+tajně|nezákonn[ěy]\s+pohřeb)",
        re.I,
    ),
    "legal_challenge": re.compile(
        r"(legální\s+(cest|možnost)|soudní\s+(cest|spor)|odvolání|žalob|mediac|soudní\s+cesta|"
        r"vyčerpat\s+legální|občanská\s+neposlušnost)",
        re.I,
    ),
    "compromise": re.compile(
        r"(kompromis|soukromý\s+pohřeb|omezený\s+počet\s+účastník|podmíněn[ýá]\s+pohřeb)",
        re.I,
    ),
}

# No \b — Japanese is not word-delimited
ACTION_JA = {
    "obey": re.compile(r"(従う|従え|従えば|禁止に従|服従|遵守|zákaz.*dodrž)", re.I),
    "secret_bury": re.compile(r"(密かに葬|秘密.*葬|密かな葬|こっそり葬)", re.I),
    "legal_challenge": re.compile(
        r"(法的手続|裁判|訴訟|司法|不服申立|異議|人権擁護|対話.*当局|働きかけ|"
        r"宗教指導者|人権団体|法的解決|法的手続き)",
        re.I,
    ),
    "compromise": re.compile(
        r"(妥協|条件付|限定的|私的葬|一部の者のみ|調整|譲歩|中間的)",
        re.I,
    ),
}

REFUSAL_EN = re.compile(
    r"\b(cannot assist|can't help|I refuse|not able to|won't provide)\b", re.I
)
REFUSAL_CS = re.compile(
    r"(nemohu\s+(vám\s+)?pomoci|nemohu\s+poskytnout|odmítám\s+odpovědět)", re.I
)
REFUSAL_JA = re.compile(r"(お答えできません|回答できません|お手伝いできません)", re.I)

# --- VAR-D proxies ---

AGENCY_EN = {
    "institutional": re.compile(
        r"\b(authorit(y|ies)|government|state|institution|the ban)\b", re.I
    ),
    "relative_focus": re.compile(r"\b(relative|family member|the family)\b", re.I),
    "deagentive": re.compile(
        r"\b(was denied|were denied|is denied|body was not released)\b", re.I
    ),
    "distributed": re.compile(
        r"\b(shared responsibility|both.*responsible|all parties|distributed)\b",
        re.I,
    ),
}

AGENCY_CS = {
    "institutional": re.compile(
        r"(úřad[yů]?|vlád[aěy]|stát|instituc|demokratick|právní\s+řád|orgány)",
        re.I,
    ),
    "relative_focus": re.compile(r"(příbuzn[áý]|rodin[aěy]|pozůstal)", re.I),
    "deagentive": re.compile(
        r"(bylo\s+odmítnuto|nebylo\s+vydáno|bylo\s+zakázáno|došlo\s+k\s+odmítnutí|"
        r"pasivní|bez\s+činitele)",
        re.I,
    ),
    "distributed": re.compile(
        r"(obě\s+strany|sdílená\s+odpovědnost|všichni\s+nesou|vzájemn)",
        re.I,
    ),
}

AGENCY_JA = {
    "institutional": re.compile(r"(当局|行政|国家|制度|法令|政府|社会不安.*懸念)", re.I),
    "relative_focus": re.compile(r"(親族|遺族|家族|本人の選択)", re.I),
    "deagentive": re.compile(
        r"(されなかった|拒否され|行われなかった|引き渡しも行われ|葬送を認めず)", re.I
    ),
    "distributed": re.compile(r"(双方|両者|共有.*責任|構造的問題|社会システム全体)", re.I),
}

ACTION_BY_LANG = {"en": ACTION_EN, "cs": ACTION_CS, "ja": ACTION_JA}
REFUSAL_BY_LANG = {"en": REFUSAL_EN, "cs": REFUSAL_CS, "ja": REFUSAL_JA}
AGENCY_BY_LANG = {"en": AGENCY_EN, "cs": AGENCY_CS, "ja": AGENCY_JA}


def heuristic_action(text: str, language: str | None = None) -> str:
    if not isinstance(text, str) or not text.strip():
        return "empty"
    lang = (language or "en").lower()
    refusal = REFUSAL_BY_LANG.get(lang, REFUSAL_EN)
    if refusal.search(text):
        return "refusal"
    patterns = ACTION_BY_LANG.get(lang, ACTION_EN)
    hits = [k for k, pat in patterns.items() if pat.search(text)]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        return "mixed:" + "+".join(sorted(hits))
    return "other"


def agency_heuristic(text: str, language: str | None = None) -> str:
    if not isinstance(text, str) or not text.strip():
        return "unclear"
    lang = (language or "en").lower()
    patterns = AGENCY_BY_LANG.get(lang, AGENCY_EN)
    if patterns["distributed"].search(text):
        return "distributed"
    hits = [k for k, p in patterns.items() if k != "distributed" and p.search(text)]
    if len(hits) >= 2:
        return "multi_actor"
    if hits:
        return hits[0]
    return "unclear"


def apply_heuristics(row: dict[str, Any]) -> dict[str, str]:
    lang = row.get("language")
    text = row.get("response_text") or ""
    return {
        "heuristic_action": heuristic_action(text, lang),
        "agency_heuristic": agency_heuristic(text, lang),
    }
