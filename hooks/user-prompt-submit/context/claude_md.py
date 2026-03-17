from __future__ import annotations

from pathlib import Path
from typing import List


def collect_claude_md(root: Path, max_chars: int = 5000) -> str:
    candidates: List[Path] = [root / "CLAUDE.md", root.parent / "CLAUDE.md", Path.home() / ".claude" / "CLAUDE.md"]
    out = []
    for p in candidates:
        try:
            if p.exists() and p.is_file():
                txt = p.read_text(encoding="utf-8", errors="ignore").strip()
                if txt:
                    out.append(f"# {p}\n{txt[:max_chars]}")
        except Exception:
            continue
    return "\n\n".join(out)
