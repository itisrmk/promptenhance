from __future__ import annotations

import subprocess
from pathlib import Path


def _run(cmd: list[str], cwd: Path) -> str:
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=1.2)
        return (p.stdout or p.stderr or "").strip()
    except Exception:
        return ""


def collect_git_state(root: Path) -> str:
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], root)
    status = _run(["git", "status", "--short"], root)
    recent = _run(["git", "log", "--oneline", "-n", "5"], root)
    if not (branch or status or recent):
        return ""
    return "\n".join([f"branch: {branch}" if branch else "", "status:", status[:1500], "recent commits:", recent[:1500]]).strip()
