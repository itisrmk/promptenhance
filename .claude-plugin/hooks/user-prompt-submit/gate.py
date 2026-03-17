from __future__ import annotations

import re
import time
from typing import Tuple

QUESTION_WORDS = {
    "how",
    "why",
    "what",
    "when",
    "where",
    "which",
    "who",
    "can",
    "could",
    "should",
    "would",
}

SPECIFICITY_HINTS = (
    r"\.[A-Za-z0-9_-]+\.(py|ts|tsx|js|jsx|go|rs|java|kt|swift|rb|php|html|css|scss|json|yaml|yml|toml|md)",
    r"\b(src|lib|app|package[s]?|packages|services|components?|tests?|hooks|commands|pages)/[\w./-]+",
    r"\b[a-zA-Z_][a-zA-Z0-9_]*\([^)]*\)",
)


def _has_reference(text: str) -> bool:
    return any(re.search(pat, text, re.IGNORECASE) for pat in SPECIFICITY_HINTS)


def _is_short_ambiguous(text: str) -> bool:
    words = re.findall(r"\S+", text)
    vague_verbs = (
        "fix it",
        "clean this up",
        "make it work",
        "add tests",
        "refactor that",
        "improve it",
        "figure this out",
        "debug",
        "optimize",
    )
    lowered = text.lower().strip()
    if len(words) < 6 and not _has_reference(text) and any(v in lowered for v in vague_verbs):
        return True
    return False


def _is_question(text: str) -> bool:
    t = text.strip().lower()
    return any(t.startswith(f"{w} ") for w in QUESTION_WORDS) or t.endswith("?")


def should_enhance(prompt: str, max_ms: int = 50) -> Tuple[bool, str]:
    start = time.perf_counter()
    text = (prompt or "").strip()
    if not text:
        return False, "empty"
    if text.startswith(("/", "#", "*")):
        return False, "slash_or_control_prefix"

    # clear explicit intent in long prompt with concrete target
    if len(re.findall(r"\S+", text)) >= 8 and _has_reference(text):
        return False, "clear_reference"

    # question prompts are explicit in intent and generally should pass through
    if _is_question(text):
        return False, "question"

    if _is_short_ambiguous(text):
        return True, "short_ambiguous"

    # generic short prompts without concrete targets should be enhanced
    if len(re.findall(r"\S+", text)) <= 5 and not _has_reference(text):
        return True, "generic_short"

    if (time.perf_counter() - start) * 1000 > max_ms:
        return False, "timeout"
    return False, "pass_through"


__all__ = ["should_enhance"]
