"""Shared fixtures for testing Claude Code hooks."""

import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOKS_SCRIPTS = REPO_ROOT / "hooks" / "scripts"


@pytest.fixture
def run_hook():
    """Run a hook script with a JSON payload piped to stdin.

    Returns (stdout, stderr, exit_code).
    """

    def _run(script_name: str, payload: dict) -> tuple[str, str, int]:
        script = HOOKS_SCRIPTS / script_name
        result = subprocess.run(
            [str(script)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout, result.stderr, result.returncode

    return _run


@pytest.fixture
def make_write_payload():
    """Create a Write tool payload."""

    def _make(content: str) -> dict:
        return {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/tmp/test.py",
                "content": content,
            },
        }

    return _make


@pytest.fixture
def make_edit_payload():
    """Create an Edit tool payload."""

    def _make(new_string: str) -> dict:
        return {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "/tmp/test.py",
                "old_string": "placeholder",
                "new_string": new_string,
            },
        }

    return _make


@pytest.fixture
def make_notebook_payload():
    """Create a NotebookEdit tool payload."""

    def _make(new_source: str) -> dict:
        return {
            "tool_name": "NotebookEdit",
            "tool_input": {
                "notebook_path": "/tmp/test.ipynb",
                "new_source": new_source,
            },
        }

    return _make
