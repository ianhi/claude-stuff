---
name: agent-handoff
description: Prepare a handoff so a fresh session can continue the current work.
---

# Agent Handoff

Prepare the current session's context for a fresh Claude Code session to pick up
where you left off. Use when context is large, the user wants to start fresh, or
work needs to continue in a different session.

## Choose the Right Variant

Ask the user which applies, or infer from context:

| Situation | Variant | Deliverable |
|-----------|---------|-------------|
| Next session implements a well-defined task | **A: Implementation plan** | A structured plan pasted into the new session |
| Ongoing exploratory / research work | **B: Handoff doc** | A file in the project the next session reads |
| Major pivot or complex environment setup | **C: Context files kit** | 2-3 files at different detail levels |

If unsure, default to **Variant A** — it's the most common and most actionable.

## Phase 1: Inventory (all variants)

Before writing anything, understand the current state. Run these yourself (small
output, fine for main context):

1. Check git status — **branch name** (needed for the handoff filename),
   uncommitted changes, recent commits
2. Glob key directories to know what files exist
3. Read any existing memory files (`memory/MEMORY.md` in the project's `.claude/`
   directory) and skill files relevant to this project
4. Note what has been tried and failed in this session — pivots, dead ends,
   abandoned approaches

## Phase 2: Capture What the Next Agent Can't Get from the Code

The next agent can read the diff, git log, and codebase. Don't repeat what's
already there. Focus on what took time to figure out and would be lost:

- **The problem itself** — a clear statement with minimal repro if applicable
- **Where to look** — specific files, functions, line numbers
- **What was tried and didn't work** — dead ends to avoid repeating
- **Domain knowledge** — non-obvious constraints, gotchas, why things are the way they are
- **Open questions** — unresolved uncertainties the next agent should be aware of
- **Architectural decisions** — only if the rationale isn't obvious from the code

## Handoff File Location

**Always write the handoff to a file** — don't just print it to the conversation.
The user may not start the next session immediately, and a file persists.

**Default location:** `notes/handoff-<branch>.md` in the project root, where
`<branch>` is the current git branch name (sanitized for filenames). This lets
the user work on multiple things in parallel within one project, each with its
own handoff state.

Examples:
- `notes/handoff-main.md`
- `notes/handoff-ian-fix-shift-array.md`
- `notes/handoff-feature-mcp-server.md`

If there's no git repo or no meaningful branch, fall back to `notes/handoff.md`.

Create the `notes/` directory if it doesn't exist. If a handoff file already
exists for this branch, overwrite it — the old one is stale.

For **Variant A** (implementation plans), still write the plan to the handoff
file. The user can then `cat` and paste it, or tell the next session to read it.

## Phase 3: Write the Handoff

### Variant A: Implementation Plan

Write the plan to the handoff file. Also present it to the user so they can
copy-paste it as the first prompt of the new session if they prefer. Structure:

```markdown
# Plan: [Short title]

## Context
[2-4 sentences: What problem, why now, desired end state]

## Prerequisites
Read these files first:
- `[path]` — [what it contains]
[If from a prior session:]
Prior session transcript: `~/.claude/projects/<slug>/<session-id>.jsonl`

## Design
[Component-level overview. One section per major component.]

## Detailed Changes
### 1. `path/to/file` — [what changes]
[Exact code for non-obvious parts. Method signatures for interfaces.]

## What Gets Removed
[Explicit list of methods, classes, or files to delete. Agents don't delete
unless told to.]

## Implementation Order
[Numbered steps if sequence matters. Include parallelization guidance for
large tasks: which files/steps can be done by subagents concurrently.]

## Verification
```bash
[runnable command]
```
[Additional checks]
```

**Key principles for good plans:**
- Every design choice is already resolved — no "you could do X or Y"
- Include exact code for the tricky parts, not the obvious parts
- Name every file that needs to change with its full relative path
- "What Gets Removed" is required for modification tasks — skip only for greenfield
- Reference skill files and memory files by path so the agent reads them first
- The verification command must be runnable, not a description of success

Present the plan to the user. They will copy-paste it into the new session.

### Variant B: Handoff Doc

Write to the standard handoff file location (`notes/handoff-<branch>.md`).

**The handoff doc is for the next agent, not a session log.** Focus on what the
next agent needs to pick up the work — the problem, where to look, how to verify.
Do NOT include a recap of what was done this session; the next agent can see the
diff and git log. Only include session history if something was tried and failed
(so the next agent doesn't repeat it).

**Contents (in priority order):**
- The problem / bug / task — with a minimal repro if applicable
- Where the relevant code lives (file paths, function names, line numbers)
- How to run the test that exercises the issue
- Open questions and uncertainties
- What was tried and didn't work (dead ends to avoid)
- Key decisions made and rationale (only if non-obvious from the code)
- A suggested opening prompt for the next session

**After writing:**
- Commit the handoff doc separately from code changes
- Tell the user the opening prompt for the next session, e.g.:
  "please read notes/handoff.md to understand where we are at. then [next task]"

### Variant C: Context Files Kit

For major pivots or complex setups. Create 2-3 files at different detail levels:

1. **Deep reference** (e.g., `PROJECT-PROMPT.md`) — full context, design rationale,
   code examples, everything the next agent might need
2. **Quick reference** (update `CLAUDE.md`) — just the key facts: API endpoints,
   connection flow, critical file paths
3. **Getting started** (e.g., `README.md` or test harness) — literal commands to
   run, the smallest runnable unit

**Before writing context files:**
- Clean up dead code and abandoned artifacts first
- Re-read existing docs to extend rather than conflict

**After writing:**
- Create a concrete runnable artifact as the target (test script, minimal example)
- Compose a structured opening prompt for the next session:

```
[Imperative task description]

Context:
- [Key decision 1]
- [Key decision 2]

To test:
1. [command]
2. [command]

Goal: [success criterion]. Once that works, [next milestone].

Read [file1] and [file2] for full details.
```

## Phase 4: Update Memory

If the project has a `.claude/projects/<slug>/memory/` directory, update
`MEMORY.md` with any durable findings from this session — architectural decisions,
file path conventions, things that apply beyond just the next session.

Don't duplicate the handoff artifact into memory. Memory is for stable facts;
the handoff is for session-specific state.

## Phase 5: Confirm with User

Print the full contents of the handoff file to the conversation — the user
can't see tool results, so they need the text in the chat to review it.

Then tell the user:
- The file path: `notes/handoff-<branch>.md`
- The git branch: `<branch>`
- A suggested opening prompt for the next session, e.g.:
  "please read notes/handoff-<branch>.md and continue from where we left off"

For Variant A, also mention they can copy-paste the plan directly if they prefer.

Ask if anything needs to be added or changed before they start the new session.
