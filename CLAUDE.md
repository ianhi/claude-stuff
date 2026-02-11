# claude-stuff — Development Guide

## What This Is

A Claude Code plugin repo containing hooks and skills. Structured as a distributable plugin (`.claude-plugin/plugin.json`) and also used directly during local development.

## Project Structure

- `hooks/scripts/` — Hook shell scripts
- `hooks/hooks.json` — Hook event → script mappings (plugin format, uses `${CLAUDE_PLUGIN_ROOT}`)
- `skills/` — Skill definitions (future)
- `tests/` — pytest tests for hooks and skills
- `.claude-plugin/plugin.json` — Plugin manifest for distribution

## Running Tests

```bash
uv run pytest
uv run pytest tests/hooks/test_block_bare_except.py -v  # single file
```

## Adding a New Hook

1. Create the script in `hooks/scripts/your-hook.sh` (make it executable: `chmod +x`)
2. Register it in `hooks/hooks.json` under the appropriate event
3. Add tests in `tests/hooks/test_your_hook.py`
4. Use the fixtures from `tests/conftest.py` — `run_hook`, `make_write_payload`, etc.

## Hook Protocol

Hooks receive JSON on stdin with `tool_name` and `tool_input` fields.

**Exit codes:** Always exit 0. Use stdout JSON to signal decisions.

**To deny a tool call**, print:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Explanation of why"
  }
}
```

**To allow**, produce no output and exit 0.

## Environment

- Use `uv` for all Python commands (`uv run pytest`, not `pytest`)
- Hook scripts should be POSIX-compatible and work on macOS + Linux
- Hooks depend on `jq` and `perl` being available on PATH
