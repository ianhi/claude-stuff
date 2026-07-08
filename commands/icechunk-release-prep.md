---
name: icechunk-release-prep
description: Prepare an icechunk release (version bumps, changelog, commit)
argument-hint: "[version, e.g. 1.1.21]"
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(git *), Bash(cargo *), Bash(gh *), Bash(just *)
---

# Release Preparation for Icechunk

Prepare the icechunk release for version $ARGUMENTS.

## Context

Current date: !`date "+%b %d, %Y"`
Current branch: !`git rev-parse --abbrev-ref HEAD`
Last release tag: !`git describe --tags --abbrev=0`
Current Rust icechunk version: !`grep '^version' icechunk/Cargo.toml | head -1`
Current Python icechunk version: !`grep '^version' icechunk-python/Cargo.toml | head -1`

## Step 0: Determine version

If `$ARGUMENTS` is empty or missing, ask the user what version to release before proceeding. Suggest the next patch version based on the current Python icechunk version above (e.g. if current is 1.1.20, suggest 1.1.21). Do NOT proceed until you have a confirmed version number. Use VERSION to refer to the confirmed version in subsequent steps.

If `$ARGUMENTS` is provided, set VERSION = `$ARGUMENTS`.

## Tasks

1. **Create a release branch**:
   - Create a new branch off the current branch: `git checkout -b release/vVERSION`
   - This prevents accidental direct commits to the release/support branch

2. **Identify changes since the last release**:
   - Run `gh pr list --state merged --base main --limit 100 --json number,title,author,labels --search "merged:>YYYY-MM-DD"` (use the date of the last release tag)
   - Also check `git log --oneline <last-tag>..HEAD` on the current branch for backports or cherry-picks
   - Categorize PRs into: Features, Fixes, Breaking Changes, Performance
   - Skip automation-only PRs (dependabot, CI-only changes) unless they affect users

3. **Update version numbers**:
   - Update `icechunk-python/Cargo.toml` version to VERSION
   - If there are Rust library changes, update `icechunk/Cargo.toml` version too
   - If the Rust version was bumped, update the `icechunk` dependency version in `icechunk-python/Cargo.toml`
   - Run `cargo check` to update `Cargo.lock`

4. **Update the changelog** in `Changelog.python.md`:
   - Add a new section at the top, below the `# Changelog` header
   - Follow the existing format exactly (see Format Reference below)
   - Include entries for all non-trivial merged PRs with links
   - Each entry should be a single line with a PR link in the format `([#NNN](https://github.com/earth-mover/icechunk/pull/NNN))`
   - Remove empty sections (don't include Features if there are none, etc.)

5. **Run tests** to verify everything works:
   - Run `just pre-commit-ci` or at minimum `cargo check` to ensure the workspace compiles

6. **Commit the changes** with message:

   ```
   Release vVERSION

   Co-authored-by: Claude <noreply@anthropic.com>
   ```

   Stage only the relevant files:
   - `icechunk/Cargo.toml` (if changed)
   - `icechunk-python/Cargo.toml`
   - `Cargo.lock`
   - `Changelog.python.md`

7. **Push and create a draft PR**:
   - Push the release branch: `git push -u origin release/vVERSION`
   - Target the base release branch (e.g. `support/v1.x` if on a support branch, or `main`)
   - Title: `Release vVERSION`
   - Request the logged-in GitHub user as reviewer (`gh api user --jq '.login'`)
   - Include the changelog entries in the PR body

## Changelog Format Reference

The changelog entry should look like:

```markdown
## Python Icechunk Library VERSION

### Features

- Description of feature ([#NNN](https://github.com/earth-mover/icechunk/pull/NNN)).

### Fixes

- Description of fix ([#NNN](https://github.com/earth-mover/icechunk/pull/NNN)).

### Breaking Changes

- Description of breaking change ([#NNN](https://github.com/earth-mover/icechunk/pull/NNN)).

### Performance

- Description of perf improvement ([#NNN](https://github.com/earth-mover/icechunk/pull/NNN)).
```

## Post-merge: Publishing checklist

After the release PR merges, remind the user of these manual steps:

1. **Publish Rust library** (if `icechunk/Cargo.toml` version was bumped):
   - Go to GitHub Actions → `publish rust library` workflow → Run workflow (manual dispatch)
2. **Publish Python wheels to PyPI**:
   - Go to GitHub Actions → `Python CI and library release` workflow → Run workflow with `pypi_release=true`
3. **Create GitHub Release**:
   - Go to Releases → Draft a new release
   - Let GitHub create the tag (`vVERSION`)
   - Use "Generate release notes" for the body
   - This triggers the community Slack notification

## Important Notes

- The Python version (`icechunk-python/Cargo.toml`) and Rust version (`icechunk/Cargo.toml`) are independent — the Python version can be ahead of the Rust version
- `Changelog.md` is a symlink to `Changelog.python.md` — edit `Changelog.python.md` directly
- Allowed release branches: `main`, `release-*`, `support/v*`
