# /pe-bypass

Bypass PromptEnhance for a single prompt by prefixing with `*`.

## Example

`*just send this exactly`

Behavior:
- Hook always exits 0.
- Returns pass-through payload without `additionalContext`.
- No blocking even if enhancement internals fail.
