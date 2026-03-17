from __future__ import annotations

from pathlib import Path


def collect_session_history(root: Path, max_chars: int = 3000) -> str:
    candidates = [root / ".claude" / "session.md", root / ".claude" / "history.md", root / ".claude" / "sessions.log"]
    chunks = []
    for p in candidates:
        try:
            if p.exists() and p.is_file():
                txt = p.read_text(encoding="utf-8", errors="ignore")
                if txt.strip():
                    chunks.append(f"# {p}\n{txt[-max_chars:]}")
        except Exception:
            continue
    return "\n\n".join(chunks)
