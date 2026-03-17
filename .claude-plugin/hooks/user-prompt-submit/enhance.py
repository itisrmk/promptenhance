#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gate import should_enhance
from enhancer import build_additional_context
from context.claude_md import collect_claude_md
from context.git_state import collect_git_state
from context.file_tree import collect_file_tree
from context.session import collect_session_history
from context.errors import collect_errors_and_todos


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists() and path.is_file():
            return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        pass
    return {}


def load_config(root: Path) -> Dict[str, Any]:
    cfg: Dict[str, Any] = {
        "enabled": True,
        "max_context_chars": 12000,
        "anthropic_enabled": False,
        "anthropic_model": "claude-3-5-haiku-latest",
        "anthropic_max_tokens": 350,
        "log_path": str(Path.home() / ".claude" / "promptenhance.log"),
    }
    cfg.update(_read_json(Path.home() / ".claude" / "promptenhance.json"))
    cfg.update(_read_json(root / ".claude" / "promptenhance.json"))

    if os.getenv("PROMPTENHANCE_ENABLED") is not None:
        cfg["enabled"] = os.getenv("PROMPTENHANCE_ENABLED", "1").lower() not in {"0", "false", "no"}
    if os.getenv("PROMPTENHANCE_ANTHROPIC_ENABLED") is not None:
        cfg["anthropic_enabled"] = os.getenv("PROMPTENHANCE_ANTHROPIC_ENABLED", "0").lower() in {"1", "true", "yes"}
    if os.getenv("PROMPTENHANCE_MAX_CONTEXT_CHARS"):
        try:
            cfg["max_context_chars"] = int(os.getenv("PROMPTENHANCE_MAX_CONTEXT_CHARS", "12000"))
        except ValueError:
            pass
    return cfg


def log_line(cfg: Dict[str, Any], msg: str) -> None:
    try:
        p = Path(cfg.get("log_path", str(Path.home() / ".claude" / "promptenhance.log")))
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def parse_prompt(stdin_data: str) -> str:
    if not stdin_data.strip():
        return ""
    try:
        d = json.loads(stdin_data)
        for k in ("prompt", "userPrompt", "input", "text"):
            if isinstance(d.get(k), str):
                return d[k]
        return ""
    except Exception:
        return stdin_data.strip()


def collect_context(root: Path) -> Dict[str, str]:
    errors, todo_bugs = collect_errors_and_todos(root)
    return {
        "claude_md": collect_claude_md(root),
        "git_state": collect_git_state(root),
        "file_tree": collect_file_tree(root),
        "session": collect_session_history(root),
        "errors": errors,
        "todo_bugs": todo_bugs,
    }


def payload(additional: str | None = None) -> Dict[str, Any]:
    out: Dict[str, Any] = {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit"}}
    if additional:
        out["hookSpecificOutput"]["additionalContext"] = additional
    return out


def main() -> int:
    root = Path.cwd()
    cfg = load_config(root)

    try:
        prompt = parse_prompt(sys.stdin.read())
        if not cfg.get("enabled", True):
            print(json.dumps(payload()))
            return 0

        if prompt.startswith("*"):
            print(json.dumps(payload()))
            return 0

        force = prompt.startswith("!")
        if force:
            prompt = prompt[1:].lstrip()

        decision, reason = should_enhance(prompt, max_ms=50)
        if not (force or decision):
            log_line(cfg, f"pass-through: {reason}")
            print(json.dumps(payload()))
            return 0

        context = collect_context(root)
        additional = build_additional_context(prompt, context, cfg)
        additional = additional[: int(cfg.get("max_context_chars", 12000))]
        log_line(cfg, f"enhanced: {reason}, chars={len(additional)}")
        print(json.dumps(payload(additional), ensure_ascii=False))
        return 0
    except Exception as exc:
        log_line(cfg, f"error: {type(exc).__name__}: {exc}")
        print(json.dumps(payload()))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
