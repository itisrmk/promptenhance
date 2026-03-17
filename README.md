# 🚀 promptenhance

[![npm version](https://img.shields.io/npm/v/promptenhance.svg)](https://www.npmjs.com/package/promptenhance)
[![npm downloads](https://img.shields.io/npm/dm/promptenhance.svg)](https://www.npmjs.com/package/promptenhance)
[![license](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE)
[![node](https://img.shields.io/node/v/promptenhance)](https://nodejs.org)
[![GitHub stars](https://img.shields.io/github/stars/itisrmk/promptenhance?style=social)](https://github.com/itisrmk/promptenhance)

**promptenhance** is a **Claude Code plugin** that makes everyday prompts smarter.

Most prompts are clear enough as-is, but short/ambiguous prompts often need quick context to get precise results. `promptenhance` sits on `UserPromptSubmit`, auto-injects concise project context, and keeps your flow safe and non-disruptive.

---

## ✨ About

`promptenhance` is designed to help Claude Code understand what you mean before it starts working.

It reads lightweight, local project context and injects a compact `additionalContext` block only when needed:

- ✅ **Visible and predictable**: JSON output is always valid and explicit
- ✅ **Fast**: clarity gate is designed to be quick, with a short timeout target
- ✅ **Safe by design**: if anything fails, it passes your prompt through
- ✅ **Configurable**: project-level and global config supported
- ✅ **No lock-in**: optional Anthropic enhancement is best-effort; stdlib path always works

This keeps the plugin usable from day one and low-friction for teams.

> _“If it’s already clear, pass through. If it’s vague, enrich with signal.”_

---

## 🎯 Why use it?

You’ll get better results when prompts are shorthand or task-like:

- `fix it`
- `clean this up`
- `add tests`
- `refactor that`

Instead of guessing context, `promptenhance` supplies:

- project rules from `CLAUDE.md`
- recent git state
- a relevant file-tree snapshot
- recent session activity
- recent errors + TODO/BUG signals

---

## 📦 Install

### Recommended: npm (quickest for users)

```bash
npm install -g promptenhance
```

### Local plugin install from source

```bash
git clone https://github.com/itisrmk/promptenhance.git
cd promptenhance
claude plugin install .
```

### Install as part of this workspace

```bash
# from within this repo folder
cd promptenhance
npm install -g .
```

---

## ⚡ Quick start

1. Install `promptenhance` (npm or local install)
2. Configure in Claude Code plugin path (`promptenhance` plugin entry uses:
   `python3 .claude-plugin/hooks/user-prompt-submit/enhance.py`)
3. Optionally add config files:
   - `~/.claude/promptenhance.json`
   - `<project>/.claude/promptenhance.json`
4. Start prompting as usual.

### Example short prompt (auto-enhanced)

```text
fix it
```

If this is ambiguous, the plugin enriches it with project context before sending to Claude.

---

## 🧠 How it works

1. Hook receives user prompt on `UserPromptSubmit`
2. Clarity gate decides if enhancement is needed (target: very fast)
3. If clear/passed through, no context is injected
4. If enhanced, collect local context and build `additionalContext`
5. Always returns valid hook JSON; never blocks on errors

---

## 🔧 Configuration

```json
{
  "enabled": true,
  "max_context_chars": 12000,
  "anthropic_enabled": false,
  "anthropic_model": "claude-3-5-haiku-latest",
  "anthropic_max_tokens": 350
}
```

Supported env overrides:

- `PROMPTENHANCE_ENABLED`
- `PROMPTENHANCE_ANTHROPIC_ENABLED`
- `PROMPTENHANCE_MAX_CONTEXT_CHARS`

---

## 🎛️ Prefix controls

- `*` — **bypass** enhancement for this prompt
- `!` — **force** enhancement even on clear prompts

---

## 🧾 Hook output contract

### Enhancement path

```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "<promptenhance auto-injected context>"
  }
}
```

### Pass-through path

```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit"
  }
}
```

---

## 🛡️ Safety + behavior guarantees

- Never blocks prompt submission
- Never returns non-zero on normal hook failure
- Logs best-effort to `~/.claude/promptenhance.log` if enabled
- No external requirements for the baseline mode

---

## 🧪 Developer packaging + local release

This repo ships a verification script and Makefile for quick local checks.

```bash
# 1) verify py_compile + smoke cases (clear/vague/bypass/empty)
make verify

# 2) lint alias
make lint

# 3) cleanup generated artifacts
make clean

# 4) discover targets
make help
```

`make verify` validates strict JSON contract and exit code behavior.

---

## 📸 Screenshot / Demo

### About this view

<!-- Replace the placeholder below with your preferred screenshot/gif -->
![promptenhance demo](./assets/promptenhance-demo.png)

If you already captured this screenshot:

```bash
cp '/var/folders/v1/nt11424d20gc2jdmpzglj9tm0000gn/T/TemporaryItems/NSIRD_screencaptureui_4G76hU/Screenshot 2026-03-16 at 9.49.07 PM.png' ./assets/promptenhance-demo.png
```

### Example smoke demo

```bash
printf '{"prompt":"fix it"}' | python3 .claude-plugin/hooks/user-prompt-submit/enhance.py
```

---

## 📬 Links

- **npm**: https://www.npmjs.com/package/promptenhance
- **GitHub**: https://github.com/itisrmk/promptenhance

---

Built by Rahul / OpenClaw
