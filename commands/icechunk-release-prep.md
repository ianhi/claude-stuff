---
name: icechunk-release-prep
description: Prepare an icechunk release (version bumps, changelog, commit)
argument-hint: "[version, e.g. 2.3.1]"
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(git *), Bash(cargo *), Bash(gh *), Bash(just *)
---

# Release Preparation for Icechunk

Prepare the icechunk release for version $ARGUMENTS.

`RELEASE.md` at the repo root is the source of truth for which files to bump and how to publish. Read it first and follow it. This command adds the branch, changelog and PR conventions that `RELEASE.md` leaves out.

## Context

Current date: !`date "+%b %d, %Y"`
Current branch: !`git rev-parse --abbrev-ref HEAD`
Last release tag: !`git describe --tags --abbrev=0`
Current Python icechunk version: !`grep '^version' icechunk-python/Cargo.toml | head -1`

## Step 0: Determine version

If `$ARGUMENTS` is empty or missing, ask the user what version to release before proceeding. Suggest the next patch version based on the current Python icechunk version above (e.g. if current is 2.3.0, suggest 2.3.1). Do NOT proceed until you have a confirmed version number. Use VERSION to refer to the confirmed version in subsequent steps.

If `$ARGUMENTS` is provided, set VERSION = `$ARGUMENTS`.

## Tasks

1. **Create a release branch** off the current branch: `git checkout -b release/vVERSION --no-track`. This keeps release commits off `main` and support branches.

2. **Identify changes since the last release**:
   - Run `gh pr list --state merged --base main --limit 100 --json number,title,author,labels --search "merged:>YYYY-MM-DD"` (use the date of the last release tag)
   - Also check `git log --oneline <last-tag>..HEAD` on the current branch for backports or cherry-picks
   - Categorize PRs into: Features, Fixes, Breaking Changes, Performance
   - Skip automation-only PRs (dependabot, CI-only changes) unless they affect users

3. **Bump versions** as described under "Update version metadata files" in `RELEASE.md`. Every workspace crate and `icechunk-js/package.json` move to VERSION in lockstep, along with the internal pins under `[workspace.dependencies]`. Run `cargo check` to update `Cargo.lock`.

4. **Update the changelog** in `Changelog.python.md` (`Changelog.md` is a symlink to it):
   - If there is a `## Python Icechunk Library [unreleased]` section, rename it to `## Python Icechunk Library VERSION` and fill in anything missing. Otherwise add a new section below the `# Changelog` header.
   - Follow the existing format exactly (see Format Reference below)
   - Include entries for all non-trivial merged PRs, each a single line ending with a link like `([#NNN](https://github.com/earth-mover/icechunk/pull/NNN))`
   - Remove empty sections

5. **Verify** with `just pre-commit-ci`, or at minimum `cargo check`.

6. **Commit** with the message `Release vVERSION`. Stage only the files the version bump and changelog touched (check `git status`); the bump also regenerates `icechunk-js/index.js`.

7. **Push and create a draft PR**:
   - Push the release branch: `git push -u origin release/vVERSION`
   - Target the base release branch (`main`, or e.g. `support/v1.x` for a support release)
   - Title: `Release vVERSION`
   - Request the logged-in GitHub user as reviewer (`gh api user --jq '.login'`)
   - Include the changelog entries in the PR body

## Changelog Format Reference

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

After the release PR merges, walk the user through the publishing sections of `RELEASE.md`, in this order:

1. Rust crates: the `publish rust library` workflow.
2. Python wheels: the `Python CI and library release` workflow with `Make a PyPI release` checked.
3. JS package: the `JS CI` workflow. Every manual run publishes to npm.
4. GitHub release: let GitHub create the `vVERSION` tag and generate the notes. This notifies the community Slack.
5. conda-forge: merge the automated feedstock PR when it appears.

Each step publishes, so the user starts them; don't dispatch workflows yourself.
