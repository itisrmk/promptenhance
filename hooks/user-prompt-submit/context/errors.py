from __future__ import annotations

from pathlib import Path


def collect_errors_and_todos(root: Path, max_bytes: int = 4000) -> tuple[str, str]:
    error_files = [root / ".claude" / "errors.log", root / "logs" / "error.log"]
    todo_files = [root / "TODO.md", root / "BUGS.md", root / "bugs.md"]

    def read_tail(p: Path) -> str:
        try:
            if p.exists() and p.is_file():
                data = p.read_text(encoding="utf-8", errors="ignore")
                return data[-max_bytes:]
        except Exception:
            pass
        return ""

    errors = "\n\n".join(f"# {p}\n{tail}" for p in error_files if (tail := read_tail(p)))
    todos = "\n\n".join(f"# {p}\n{tail}" for p in todo_files if (tail := read_tail(p)))
    return errors, todos
