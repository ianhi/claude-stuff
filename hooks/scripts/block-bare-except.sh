#!/bin/bash
# Hook: Block bare "except Exception: pass" patterns
# Fires on PreToolUse for Write, Edit, and MCP tools that write code.
# Checks the content being written for the anti-pattern:
#   except Exception:
#       pass
#   except Exception as e:
#       pass

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')

# Only check Python files — skip everything else for speed
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty')
case "$FILE_PATH" in
  *.py|*.ipynb) ;;  # continue
  *)
    # MCP tools may not have a recognizable path — check those too
    if [ -n "$FILE_PATH" ]; then
      exit 0
    fi
    ;;
esac

# Extract the relevant content based on tool type
CONTENT=""
case "$TOOL_NAME" in
  Write)
    CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty')
    ;;
  Edit)
    CONTENT=$(echo "$INPUT" | jq -r '.tool_input.new_string // empty')
    ;;
  NotebookEdit)
    CONTENT=$(echo "$INPUT" | jq -r '.tool_input.new_source // empty')
    ;;
  *)
    # For MCP tools or others, try common field names
    CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // .tool_input.source // .tool_input.new_source // .tool_input.code // empty')
    ;;
esac

# Nothing to check
if [ -z "$CONTENT" ]; then
  exit 0
fi

# Check for bare except Exception: pass pattern using perl (portable across macOS/Linux)
# Matches variations like:
#   except Exception:
#       pass
#   except Exception as e:
#       pass
#   except Exception as err:\n        pass
if echo "$CONTENT" | perl -0777 -ne 'exit 1 unless /except\s+Exception(\s+as\s+\w+)?\s*:\s*\n\s*pass/'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "BLOCKED: Bare `except Exception: pass` detected. This silently swallows all errors and makes debugging impossible. Please handle the exception properly — log it, re-raise it, or catch a more specific exception type. Reconsider your approach."
    }
  }'
  exit 0
fi

# Allow if no issues found
exit 0
