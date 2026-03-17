#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

HOOK_ROOT=".claude-plugin/hooks/user-prompt-submit"
HOOK_FILES=(
  "$HOOK_ROOT/__init__.py"
  "$HOOK_ROOT/enhance.py"
  "$HOOK_ROOT/enhancer.py"
  "$HOOK_ROOT/gate.py"
  "$HOOK_ROOT/context/__init__.py"
  "$HOOK_ROOT/context/claude_md.py"
  "$HOOK_ROOT/context/git_state.py"
  "$HOOK_ROOT/context/file_tree.py"
  "$HOOK_ROOT/context/session.py"
  "$HOOK_ROOT/context/errors.py"
)

compile_all() {
  for f in "${HOOK_FILES[@]}"; do
    [[ -f "$f" ]] || { echo "missing: $f" >&2; exit 1; }
    python3 -m py_compile "$f"
  done
}

run_case() {
  local label="$1"
  local expected_mode="$2"
  local payload="$3"

  local out
  out="$(printf '%s' "$payload" | python3 "$HOOK_ROOT/enhance.py")"
  [[ -n "$out" ]] || { echo "FAIL [$label]: empty output" >&2; exit 1; }

  python3 - "$label" "$expected_mode" "$out" <<'PY'
import json
import sys

label, expected_mode, raw = sys.argv[1], sys.argv[2], sys.argv[3]

try:
    data = json.loads(raw)
except json.JSONDecodeError as exc:
    raise SystemExit(f"FAIL [{label}]: invalid JSON output: {exc}")

if not isinstance(data, dict):
    raise SystemExit(f"FAIL [{label}]: output must be a JSON object")

hso = data.get("hookSpecificOutput")
if not isinstance(hso, dict):
    raise SystemExit(f"FAIL [{label}]: missing/invalid hookSpecificOutput object")

if hso.get("hookEventName") != "UserPromptSubmit":
    raise SystemExit(f"FAIL [{label}]: unexpected hookEventName={hso.get('hookEventName')!r}")

ac = hso.get("additionalContext", "")
if not isinstance(ac, str):
    raise SystemExit(f"FAIL [{label}]: additionalContext must be a string")

if expected_mode == "enhanced":
    if not ac.strip():
        raise SystemExit(f"FAIL [{label}]: expected non-empty additionalContext")
elif expected_mode == "pass":
    if ac.strip():
        raise SystemExit(f"FAIL [{label}]: expected pass-through (empty additionalContext)")
else:
    raise SystemExit(f"FAIL [{label}]: unknown expected mode {expected_mode!r}")

print(f"ok [{label}]")
PY
}

echo "[verify] py_compile checks"
compile_all

echo "[verify] smoke tests"
run_case "clear" "pass" '{"prompt":"src/auth/index.ts add rate limit guard"}'
run_case "vague" "enhanced" '{"prompt":"fix it"}'
run_case "bypass" "pass" '{"prompt":"* add tests"}'
run_case "empty-input" "pass" ''

echo "verify ok"
