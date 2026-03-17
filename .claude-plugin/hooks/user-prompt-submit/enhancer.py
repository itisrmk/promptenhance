from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

PROMPTENHANCE_MARKER_TEXT = "🧠 [promptenhance — ENHANCED]"


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() not in {"0", "false", "no", "off"}
    return default


def _truncate(text: str, limit: int = 120) -> str:
    txt = (text or "").strip().replace("\n", " ")
    if len(txt) <= limit:
        return txt
    return txt[: limit - 3] + "..."


def _format_visual_marker(cfg: Dict[str, Any], reason: Optional[str], prompt: str) -> str:
    show_marker = _to_bool(cfg.get("promptenhance_show_marker"), True)
    if not show_marker:
        return ""

    return "\n".join(
        [
            PROMPTENHANCE_MARKER_TEXT,
            f"result: enhanced",
            f"reason: {reason or 'auto'}",
            f"prompt: {_truncate(prompt)}",
            "",
        ]
    )


def _format_diff_block(cfg: Dict[str, Any], reason: Optional[str], prompt: str, context_text: str) -> str:
    if not _to_bool(cfg.get("promptenhance_show_diff"), False):
        return ""

    return "\n".join(
        [
            "[promptenhance diff]",
            f"- prompt: {_truncate(prompt)}",
            f"+ added additionalContext ({len(context_text)} chars)",
            f"+ reason: {reason or 'auto'}",
        ]
    )


def _decorate_additional_context(text: str, prompt: str, cfg: Dict[str, Any], reason: Optional[str] = None) -> str:
    show_marker = _to_bool(cfg.get("promptenhance_show_marker"), True)
    show_diff = _to_bool(cfg.get("promptenhance_show_diff"), False)

    if not show_marker and not show_diff:
        return text

    blocks = []
    marker = _format_visual_marker(cfg, reason, prompt)
    if marker:
        blocks.append(marker)

    blocks.append(text)

    diff = _format_diff_block(cfg, reason, prompt, text)
    if diff:
        blocks.append(diff)

    return "\n\n".join(blocks).strip()


def _build_local_enhancement(prompt: str, context: Dict[str, Any], cfg: Dict[str, Any], reason: Optional[str] = None) -> str:
    parts = [
        "PromptEnhance context (auto-added):",
        "",
        "User intent:",
        prompt.strip(),
        "",
    ]
    for key, title in [
        ("claude_md", "Relevant CLAUDE.md snippets"),
        ("git_state", "Git state"),
        ("file_tree", "Project file tree snapshot"),
        ("session", "Recent session history"),
        ("errors", "Recent errors"),
        ("todo_bugs", "TODO/BUG notes"),
    ]:
        value = (context.get(key) or "").strip()
        if value:
            parts += [f"{title}:", value, ""]
    parts += [
        "Guidance:",
        "- Keep responses concise and implementation-focused.",
        "- Respect existing project conventions.",
        "- If requirements are unclear, ask one focused clarification.",
    ]
    base = "\n".join(parts).strip()
    return _decorate_additional_context(base, prompt, cfg, reason)


def _try_anthropic(prompt: str, context: Dict[str, Any], cfg: Dict[str, Any], reason: Optional[str] = None) -> str | None:
    if not _to_bool(cfg.get("anthropic_enabled"), False):
        return None
    api_key = os.getenv("ANTHROPIC_API_KEY") or cfg.get("anthropic_api_key")
    if not api_key:
        return None
    try:
        from anthropic import Anthropic  # type: ignore
    except Exception:
        return None

    try:
        client = Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=cfg.get("anthropic_model", "claude-3-5-haiku-latest"),
            max_tokens=int(cfg.get("anthropic_max_tokens", 350)),
            messages=[
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "instruction": "Generate concise additionalContext only.",
                            "prompt": prompt,
                            "context": context,
                        }
                    ),
                }
            ],
        )
        chunks = [getattr(b, "text", "") for b in getattr(msg, "content", []) if getattr(b, "text", "")]
        out = "\n".join(chunks).strip()
        if not out:
            return None

        return _decorate_additional_context(out, prompt, cfg, reason)
    except Exception:
        return None


def build_additional_context(prompt: str, context: Dict[str, Any], cfg: Dict[str, Any], reason: Optional[str] = None) -> str:
    return _try_anthropic(prompt, context, cfg, reason) or _build_local_enhancement(prompt, context, cfg, reason)
