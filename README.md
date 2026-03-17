# promptenhance

Fail-safe, lightweight prompt enhancement scaffold for Claude Code `UserPromptSubmit` hooks.

## Install

1. Keep this repo as your project plugin scaffold.
2. Ensure Claude plugin points to:

```json
{
  "hooks": {
    "UserPromptSubmit": {
      "command": "python3 .claude-plugin/hooks/user-prompt-submit/enhance.py"
    }
  }
}
```

3. Optional config files:
   - `~/.claude/promptenhance.json`
   - `<project>/.claude/promptenhance.json`

### Example config

```json
{
  "enabled": true,
  "max_context_chars": 12000,
  "anthropic_enabled": false,
  "anthropic_model": "claude-3-5-haiku-latest",
  "anthropic_max_tokens": 350
}
```

Environment overrides:
- `PROMPTENHANCE_ENABLED`
- `PROMPTENHANCE_ANTHROPIC_ENABLED`
- `PROMPTENHANCE_MAX_CONTEXT_CHARS`

## Behavior

- Clarity gate (`hooks/user-prompt-submit/gate.py`) runs fast (<50ms target).
- If prompt is already clear or uncertain: pass-through.
- If enhancement is chosen (or forced with `!`): gather context and emit `additionalContext`.
- Prefix `*` bypasses enhancement.
- Hook is always fail-safe: exits `0`, never blocks user prompt.
- Best-effort logging to `~/.claude/promptenhance.log`.

## Hook output contract

When enhancing:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "..."
  }
}
```

When passing through:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit"
  }
}
```

## Context collection

- `CLAUDE.md`: project + parent + `~/.claude`
- Git state: branch/status/recent commits
- File tree snapshot
- Session history from `.claude/*` history files
- Recent errors log
- TODO/BUG files

## Non-goals / constraints

- No heavy orchestration or embedding pipeline.
- No mandatory external API.
- Uses Python stdlib only for baseline.
- Optional Anthropic SDK call is best-effort and gracefully skipped if unavailable.

## Developer packaging + local release

Use the Makefile targets for local packaging checks before publishing/releasing:

```bash
cd promptenhance

# 1) verify hook package health (compile + smoke tests)
make verify
# optional alias
make lint

# 2) remove generated caches/bytecode artifacts
make clean

# 3) placeholder install helper for local plugin docs
make install

# discover all targets
make help
```

`make verify` runs `scripts/verify_promptenhance.sh`, which validates:
- `py_compile` across hook + context modules
- JSON contract correctness for clear/vague/bypass/empty-input runs of `enhance.py` (non-zero exit on invalid output)



## Install

Install from npm (recommended):

```bash
npm install -g promptenhance
```

Or install from a local clone:

```bash
git clone https://github.com/rahul/promptenhance
cd promptenhance
claude plugin install .
```

Keep this repo as your project plugin scaffold.
Ensure Claude plugin points to:
