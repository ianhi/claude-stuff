# claude-stuff

A personal collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) hooks and skills. Installable as a plugin or usable as a reference.

## Included Hooks

| Hook | Event | Description |
|------|-------|-------------|
| `block-bare-except` | PreToolUse | Blocks `except Exception: pass` — forces proper error handling |

## Installation

```bash
claude /plugin install https://github.com/ianhi/claude-stuff
```

## Development

### Setup

```bash
git clone https://github.com/ianhi/claude-stuff
cd claude-stuff

# Install as a plugin from local checkout
claude /plugin install .

# Install test dependencies
uv sync
```

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
