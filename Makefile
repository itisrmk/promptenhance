SHELL := /usr/bin/env bash

.PHONY: verify lint clean install help

HOOK_FILES := \
	.claude-plugin/hooks/user-prompt-submit/enhance.py \
	.claude-plugin/hooks/user-prompt-submit/enhancer.py \
	.claude-plugin/hooks/user-prompt-submit/gate.py \
	.claude-plugin/hooks/user-prompt-submit/context/claude_md.py \
	.claude-plugin/hooks/user-prompt-submit/context/git_state.py \
	.claude-plugin/hooks/user-prompt-submit/context/file_tree.py \
	.claude-plugin/hooks/user-prompt-submit/context/session.py \
	.claude-plugin/hooks/user-prompt-submit/context/errors.py

verify:
	@bash scripts/verify_promptenhance.sh

lint:
	@$(MAKE) verify

clean:
	@rm -rf .claude-plugin/hooks/.pe_cache
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	@find . -name '*.pyc' -type f -delete
	@echo "cleaned"

install:
	@echo "To install locally, run:"
	@echo "claude plugin install ."

help:
	@echo "promptenhance Makefile targets:"
	@echo "  make verify   - run compilation + smoke tests"
	@echo "  make lint     - alias for make verify"
	@echo "  make clean    - remove plugin cache artifacts"
	@echo "  make install  - print install command"
