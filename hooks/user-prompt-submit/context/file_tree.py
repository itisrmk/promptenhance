from __future__ import annotations

from pathlib import Path


def collect_file_tree(root: Path, max_depth: int = 3, max_entries: int = 200) -> str:
    lines, count = [], 0

    def walk(path: Path, depth: int = 0) -> None:
        nonlocal count
        if depth > max_depth or count >= max_entries:
            return
        try:
            items = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except Exception:
            return
        for item in items:
            if count >= max_entries:
                return
            if item.name.startswith(".") and item.name not in {".claude", ".claude-plugin"}:
                continue
            lines.append(f"{'  ' * depth}{item.name}{'/' if item.is_dir() else ''}")
            count += 1
            if item.is_dir():
                walk(item, depth + 1)

    walk(root)
    return "\n".join(lines)
