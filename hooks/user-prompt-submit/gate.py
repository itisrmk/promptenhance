from __future__ import annotations

import re
import time
from typing import Tuple

QUESTION_WORDS = {"how", "why", "what", "when", "where", "which", "who", "can", "could", "should", "would"}


def should_enhance(prompt: str, max_ms: int = 50) -> Tuple[bool, str]:
    start = time.perf_counter()
    decision: Tuple[bool, str] = (False, "pass_through")
    try:
        text = (prompt or "").strip()
        if not text:
            decision = (False, "empty")
        elif text.startswith(("/", "#", "*")):
            decision = (False, "command_or_bypass")
        elif len(text) < 12:
            decision = (False, "short")
        else:
            lowered = text.lower()
            wc = len(re.findall(r"\S+", text))
            has_qmark = "?" in text
            has_question_word = any(lowered.startswith(w + " ") for w in QUESTION_WORDS)
            has_task_verb = bool(re.search(r"\b(build|create|write|fix|debug|refactor|design|implement|summarize|explain)\b", lowered))
            has_constraints = bool(re.search(r"\b(with|using|without|must|should|don't|do not|only|exactly)\b", lowered))
            has_file_ref = bool(re.search(r"\b(src|lib|app|tests?|packages)/|\.[a-z]{2,4}\b", lowered))

            if has_task_verb and (has_constraints or has_file_ref or wc >= 16):
                decision = (False, "already_clear")
            elif wc >= 6 and not has_constraints and not has_qmark and not has_question_word:
                decision = (True, "likely_ambiguous")
            else:
                decision = (False, "pass_through")
    except Exception:
        decision = (False, "gate_error")

    if (time.perf_counter() - start) * 1000 > max_ms:
        return False, "timeout"
    return decision
