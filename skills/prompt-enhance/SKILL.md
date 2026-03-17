---
name: prompt-enhance
description: Lightweight prompt enhancement hook for Claude Code UserPromptSubmit.
---

# Prompt Enhance Skill

## Purpose
Add context-aware `additionalContext` to qualifying prompts while staying fail-safe and fast.

## Rules
- Never block normal prompt flow.
- If uncertain, pass through.
- Exit code must always be `0`.
- Keep gate decision under ~50ms.

## Trigger Controls
- Prefix `*` => bypass enhancement.
- Prefix `!` => force enhancement.

## Context Sources
- `CLAUDE.md` (project, parent, `~/.claude`)
- git branch/status/recent commits
- file tree snapshot
- session history
- errors logs
- TODO/BUG files

## Non-goals
- No heavy retrieval pipelines or embeddings.
- No required third-party dependencies.
- No network dependency for baseline behavior.
- No mutation of user prompt text (context-only augmentation).
