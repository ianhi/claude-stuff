# claude-stuff

A personal collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills, slash commands, and hooks. Installable as a plugin or usable as a reference.

## Included Skills

| Skill | Description |
|-------|-------------|
| `agent-handoff` | Prepare a handoff so a fresh session can continue the current work |
| `coiled-notebook` | Launch a [Coiled](https://coiled.io) cloud Jupyter notebook and connect via the Jupyter MCP |
| `hypothesis-failure-investigation` | Triage and diagnose [Hypothesis](https://hypothesis.readthedocs.io) stateful test failures |
| `plot-check` | Dispatch a subagent to review a plot image for visual issues and suggest fixes |

## Included Commands

| Command | Description |
|---------|-------------|
| `/review-changes` | Dispatch a fresh-context subagent to review the current branch's changes against its base |
| `/icechunk-release-prep` | Prepare an [icechunk](https://github.com/earth-mover/icechunk) release (version bumps, changelog, commit) |
| `/xarray-release-prep` | Prepare `whats-new.rst` for an [xarray](https://github.com/pydata/xarray) release |

## Included Hooks

| Hook | Event | Description |
|------|-------|-------------|
| `block-bare-except` | PreToolUse | Blocks `except Exception: pass` — forces proper error handling |

## Installation

```bash
claude plugin marketplace add ianhi/claude-stuff
claude plugin install claude-stuff
```

## Development

### Setup

```bash
git clone https://github.com/ianhi/claude-stuff
cd claude-stuff

# Load as a plugin from local checkout (session only)
claude --plugin-dir .

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
