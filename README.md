# claude-stuff

A personal collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) hooks and skills. Installable as a plugin or usable as a reference.

## Included Hooks

| Hook | Event | Description |
|------|-------|-------------|
| `block-bare-except` | PreToolUse | Blocks `except Exception: pass` — forces proper error handling |

## Installation

### As a Claude Code plugin

```bash
claude /plugin install /path/to/claude-stuff
# or from a git URL:
claude /plugin install https://github.com/youruser/claude-stuff
```

### Manual

Copy individual hook scripts and wire them up in your `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|NotebookEdit|mcp__.*",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/hooks/scripts/block-bare-except.sh"
          }
        ]
      }
    ]
  }
}
```

## Development

### Prerequisites

- [uv](https://docs.astral.sh/uv/) for Python environment management
- `jq` and `perl` (available by default on macOS)

### Run tests

```bash
uv run pytest
```

### Add a new hook

1. Create `hooks/scripts/your-hook.sh` (executable)
2. Register in `hooks/hooks.json`
3. Add tests in `tests/hooks/`

See [CLAUDE.md](CLAUDE.md) for the full hook protocol reference.

## License

MIT
