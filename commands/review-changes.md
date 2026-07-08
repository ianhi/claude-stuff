---
description: Dispatch a subagent to review changes against a base branch
argument-hint: [focus-areas]
---

## Your task

Dispatch a **subagent** with a fresh context to review the changes on the current branch. The subagent should have no prior context from this conversation — it gets a clean slate to evaluate the work.

The subagent should determine the appropriate base branch itself (e.g. by checking the PR target, the default branch, or the merge-base). Don't hardcode `main` — let it figure out what makes sense for this repo.

### Focus areas

The user may specify focus areas as arguments: `$ARGUMENTS`

If arguments are provided, map them to review focus areas. Common shorthands:

- **correctness** — Look for bugs, logic errors, off-by-one mistakes, missing edge cases, incorrect assumptions
- **style** — Code style, naming conventions, consistency with the rest of the codebase
- **simplify** / **simplifications** — Unnecessary complexity, over-engineering, code that could be shorter or clearer
- **tests** — Test coverage gaps, missing edge case tests, test quality
- **security** — Input validation, injection risks, secrets handling
- **perf** / **performance** — Unnecessary allocations, O(n^2) where O(n) would do, repeated work
- **reviewability** — How would a human reviewer receive this PR? Look for: unclear commit scope, changes that should be split into separate PRs, missing context that a reviewer would need, confusing diffs (e.g. large renames mixed with logic changes), and anything that would make a reviewer ask "why?"
- **all** — Cover all of the above

If no arguments are provided, default to: **correctness, style, simplifications, reviewability**.

### Subagent instructions

When dispatching the subagent, include these instructions:

1. **Determine the base branch** — check if there's an open PR (use `gh pr view` if available), otherwise fall back to the repo's default branch (`git symbolic-ref refs/remotes/origin/HEAD` or common names like `main`/`master`/`develop`)
2. **Read the full diff** between the base branch and `HEAD` using `git diff {base}...HEAD`
3. **Read each changed file in full** to understand the surrounding context
4. **Check for project instructions** — read `CLAUDE.md` at the repo root if it exists
5. **Environment note** — If you need to run Python or tests, check the project's CLAUDE.md or pyproject.toml for the right tool. Common: `uv run python` / `uv run pytest`. Never use bare `python` or `pytest` without checking first.
5. **Review the changes** with the specified focus areas in mind
6. **Report findings** organized by focus area, with file paths and line numbers for each issue
7. **Be concise** — flag real issues, skip nitpicks and obvious false positives. Don't praise code that's fine.
8. If there are no issues worth flagging for a focus area, say so in one line and move on.

### How to dispatch

Use the **Agent tool** to spawn the subagent. You have leeway to craft the prompt — adapt it to the repo, the size of the diff, and what you already know from the conversation. The key requirements are:

1. The subagent must get **enough context** to do a real review (the diff, the changed files in full, project conventions from CLAUDE.md)
2. Tell it the **focus areas** and what quality bar to hit
3. Tell it to check CLAUDE.md or pyproject.toml before running any commands

Beyond that, use your judgment. If the diff is small, keep the prompt short. If there's important context from the conversation (e.g. "this is a refactor, behavior shouldn't change"), pass that along. If there are uncommitted changes that should be included, mention that.

### Review quality

Tell the subagent to review like a thoughtful, experienced human reviewer would — not a linter. It should:

- **Understand intent** before critiquing. Read the full context, not just the diff lines.
- **Think about what could go wrong** in production, not just what looks wrong in the code.
- **Flag things a human reviewer would catch** — subtle bugs, missed interactions between changed files, assumptions that don't hold, changes that will confuse the next person reading this code.
- **Skip noise** — don't flag style nitpicks that a formatter handles, don't praise code that's fine, don't pad the review with non-issues.
- Report findings organized by focus area with file:line references.

After the subagent completes, **summarize its findings** back to the user. Include file:line references for any issues found.
