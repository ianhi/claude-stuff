"""Tests for the block-bare-except hook."""

import json

HOOK = "block-bare-except.sh"


class TestDeniesBareCatch:
    """The hook should deny bare except Exception: pass patterns."""

    def test_denies_except_exception_pass(self, run_hook, make_write_payload):
        code = "try:\n    do_stuff()\nexcept Exception:\n    pass\n"
        stdout, _, exit_code = run_hook(HOOK, make_write_payload(code))
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert exit_code == 0

    def test_denies_except_exception_as_e_pass(self, run_hook, make_write_payload):
        code = "try:\n    do_stuff()\nexcept Exception as e:\n    pass\n"
        stdout, _, exit_code = run_hook(HOOK, make_write_payload(code))
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert exit_code == 0

    def test_denies_except_exception_as_err_pass(self, run_hook, make_write_payload):
        code = "try:\n    do_stuff()\nexcept Exception as err:\n    pass\n"
        stdout, _, exit_code = run_hook(HOOK, make_write_payload(code))
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert exit_code == 0

    def test_denies_with_indentation(self, run_hook, make_write_payload):
        code = "def f():\n    try:\n        do_stuff()\n    except Exception:\n        pass\n"
        stdout, _, exit_code = run_hook(HOOK, make_write_payload(code))
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert exit_code == 0


class TestAllowsProperHandling:
    """The hook should allow specific exceptions and proper handling."""

    def test_allows_specific_exception(self, run_hook, make_write_payload):
        code = "try:\n    do_stuff()\nexcept ValueError:\n    pass\n"
        stdout, _, exit_code = run_hook(HOOK, make_write_payload(code))
        assert stdout.strip() == ""
        assert exit_code == 0

    def test_allows_proper_handling(self, run_hook, make_write_payload):
        code = "try:\n    do_stuff()\nexcept Exception as e:\n    logger.error(e)\n"
        stdout, _, exit_code = run_hook(HOOK, make_write_payload(code))
        assert stdout.strip() == ""
        assert exit_code == 0

    def test_allows_reraise(self, run_hook, make_write_payload):
        code = "try:\n    do_stuff()\nexcept Exception:\n    raise\n"
        stdout, _, exit_code = run_hook(HOOK, make_write_payload(code))
        assert stdout.strip() == ""
        assert exit_code == 0

    def test_allows_no_exception_handling(self, run_hook, make_write_payload):
        code = "def hello():\n    print('world')\n"
        stdout, _, exit_code = run_hook(HOOK, make_write_payload(code))
        assert stdout.strip() == ""
        assert exit_code == 0


class TestToolTypes:
    """The hook should work across Write, Edit, and NotebookEdit tools."""

    BARE_CATCH = "try:\n    x()\nexcept Exception:\n    pass\n"

    def test_edit_tool(self, run_hook, make_edit_payload):
        stdout, _, exit_code = run_hook(HOOK, make_edit_payload(self.BARE_CATCH))
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert exit_code == 0

    def test_notebook_tool(self, run_hook, make_notebook_payload):
        stdout, _, exit_code = run_hook(HOOK, make_notebook_payload(self.BARE_CATCH))
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert exit_code == 0

    def test_unknown_tool_with_content_field(self, run_hook):
        payload = {
            "tool_name": "mcp__editor__write",
            "tool_input": {"content": self.BARE_CATCH},
        }
        stdout, _, exit_code = run_hook(HOOK, payload)
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert exit_code == 0

    def test_unknown_tool_no_content(self, run_hook):
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "echo hello"},
        }
        stdout, _, exit_code = run_hook(HOOK, payload)
        assert stdout.strip() == ""
        assert exit_code == 0


class TestFileTypeFiltering:
    """The hook should only check Python files and skip everything else."""

    BARE_CATCH = "try:\n    x()\nexcept Exception:\n    pass\n"

    def test_skips_javascript_file(self, run_hook):
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": "/tmp/app.js", "content": self.BARE_CATCH},
        }
        stdout, _, exit_code = run_hook(HOOK, payload)
        assert stdout.strip() == ""
        assert exit_code == 0

    def test_skips_typescript_file(self, run_hook):
        payload = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "/tmp/app.ts",
                "old_string": "x",
                "new_string": self.BARE_CATCH,
            },
        }
        stdout, _, exit_code = run_hook(HOOK, payload)
        assert stdout.strip() == ""
        assert exit_code == 0

    def test_skips_markdown_file(self, run_hook):
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": "/tmp/README.md", "content": self.BARE_CATCH},
        }
        stdout, _, exit_code = run_hook(HOOK, payload)
        assert stdout.strip() == ""
        assert exit_code == 0

    def test_checks_python_file(self, run_hook):
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": "/tmp/app.py", "content": self.BARE_CATCH},
        }
        stdout, _, exit_code = run_hook(HOOK, payload)
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_checks_notebook_file(self, run_hook):
        payload = {
            "tool_name": "NotebookEdit",
            "tool_input": {
                "notebook_path": "/tmp/analysis.ipynb",
                "new_source": self.BARE_CATCH,
            },
        }
        stdout, _, exit_code = run_hook(HOOK, payload)
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_mcp_tool_no_path_still_checked(self, run_hook):
        """MCP tools without a file path should still be checked."""
        payload = {
            "tool_name": "mcp__editor__write",
            "tool_input": {"content": self.BARE_CATCH},
        }
        stdout, _, exit_code = run_hook(HOOK, payload)
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
