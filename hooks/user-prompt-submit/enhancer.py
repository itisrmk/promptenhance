from __future__ import annotations

import json
import os
from typing import Dict, Any, Optional


def _format_visual_marker(cfg: Dict[str, Any], reason: Optional[str], prompt: str) -> str:
    if not cfg.get("show_visual", True):
        return "[promptenhance — auto-injected context]"

    label = cfg.get("visual_label", "🧠 [promptenhance-enhanced]")
    reason_text = reason or "auto"
    prompt_preview = (prompt or "").strip().replace("\n", " ")
    if len(prompt_preview) > 120:
        prompt_preview = prompt_preview[:117] + "..."

    return "\n".join(
        [
            str(label),
            f"Result: Enhanced",
            f"Trigger: {reason_text}",
            f"Prompt: {prompt_preview}",
            "",
        ]
    )


def _build_local_enhancement(prompt: str, context: Dict[str, Any], cfg: Dict[str, Any], reason: Optional[str] = None) -> str:
    parts = [
        _format_visual_marker(cfg, reason, prompt),
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
        "[end promptenhance]",
    ]
    return "\n".join(parts).strip()


def _try_anthropic(prompt: str, context: Dict[str, Any], cfg: Dict[str, Any], reason: Optional[str] = None) -> str | None:
    if not cfg.get("anthropic_enabled", False):
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
            messages=[{
                "role": "user",
                "content": json.dumps(
                    {
                        "instruction": "Generate concise additionalContext only.",
                        "prompt": prompt,
                        "context": context,
                    }
                ),
            }],
        )
        chunks = [getattr(b, "text", "") for b in getattr(msg, "content", []) if getattr(b, "text", "")]
        out = "\n".join(chunks).strip()
        if not out:
            return None

        if cfg.get("show_visual", True):
            out = _format_visual_marker(cfg, reason, prompt) + "\n" + out
        return out
    except Exception:
        return None


def build_additional_context(prompt: str, context: Dict[str, Any], cfg: Dict[str, Any], reason: Optional[str] = None) -> str:
    return _try_anthropic(prompt, context, cfg, reason) or _build_local_enhancement(prompt, context, cfg, reason)
