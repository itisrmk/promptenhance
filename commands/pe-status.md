# /pe-status

Shows PromptEnhance runtime status in this project.

## What to check

1. `plugin.json` exists and includes UserPromptSubmit command.
2. Hook entry exists at `.claude-plugin/hooks/user-prompt-submit/enhance.py`.
3. Config resolution order:
   - `~/.claude/promptenhance.json`
   - `.claude/promptenhance.json`
   - environment overrides (`PROMPTENHANCE_*`)
4. Log file: `~/.claude/promptenhance.log` (best effort)
5. Prefix modes:
   - `*` bypass enhancement
   - `!` force enhancement

## Quick local check

```bash
echo '{"prompt":"!help me make this better"}' | python3 hooks/user-prompt-submit/enhance.py
```
