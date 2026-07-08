---
name: xarray-release-prep
description: Prepare whats-new.rst for an xarray release
argument-hint: "[version, e.g. 2026.01.0]"
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(git *), Bash(pixi *), Bash(gh *)
---

# Release Preparation for xarray

Prepare whats-new.rst for version $ARGUMENTS.

## Context

Current date: !`date "+%b %d, %Y"`
Current branch: !`git rev-parse --abbrev-ref HEAD`
Last release tag: !`git describe --tags --abbrev=0`

## Contributors

Run the contributor script to get the list:

```bash
pixi run release-contributors
```

## Tasks

1. **Read current whats-new.rst** to understand the structure. Look at the previous release entry (e.g., v2025.12.0) for the format.

2. **Check for missing PRs** since the last release:
   - Run `gh pr list --state merged --base main --limit 100 --json number,title,author,labels --search "merged:>YYYY-MM-DD"` (use last release date)
   - Compare with entries in whats-new.rst
   - Add entries for any non-trivial PRs that are missing (skip automation, CI, dependabot bumps)
   - Categorize into: New Features, Breaking Changes, Bug Fixes, Documentation, Performance, Internal Changes

3. **Fix rST formatting** in all entries:
   - Use proper rST roles: `:py:func:`, `:py:meth:`, `:py:class:` for xarray API references
   - Always use comma between `:issue:` and `:pull:` references: `(:issue:\`1234\`, :pull:\`5678\`)`
   - Remove empty sections (like Deprecations with no entries)

4. **Update the unreleased section** in `doc/whats-new.rst`:
   - Change the version reference from `` whats-new.vX.X.X`` to ``whats-new.$ARGUMENTS`` (note: no `v` prefix in the label)
   - Update the version header from `vX.X.X (unreleased)` to `v$ARGUMENTS (DATE)` using today's date
   - Write a ~50 word release summary highlighting key features and any breaking changes (look at both the New Features and Breaking Changes sections; ignore sections like Deprecations that have no entries)
   - Add the contributor thanks line from `pixi run release-contributors`

5. **Commit the changes** with message:

   ```
   Update whats-new for v$ARGUMENTS release

   Co-authored-by: Claude <noreply@anthropic.com>
   ```

6. **Push and create a draft PR** with the `Release` label:
   - Request the logged-in GitHub user as reviewer (`gh api user --jq '.login'`)
   - Add `[This is Claude Code on behalf of <username>]` to the PR body

## rST Formatting Examples

Good entry format:
```rst
- :py:meth:`Dataset.eval` now works with more than 2 dimensions (:pull:`11064`).
  By `Maximilian Roos <https://github.com/max-sixty>`_.
- Fix :py:func:`where` for ``cupy.array`` inputs (:issue:`10843`, :pull:`11026`).
  By `Simon Høxbro Hansen <https://github.com/hoxbro>`_.
```

Common rST roles:
- `:py:func:\`open_dataset\`` — top-level functions
- `:py:meth:\`Dataset.sel\`` — methods
- `:py:class:\`DataTree\`` — classes
- `:py:class:\`~xarray.indexes.PandasIndex\`` — use `~` prefix to show only class name
- `:pull:\`1234\`` — PR reference
- `:issue:\`1234\`` — issue reference

## Format Reference

The release entry should look like:

```rst
.. _whats-new.YYYY.MM.X:

vYYYY.MM.X (Mon DD, YYYY)
--------------------------

<Release summary ~50 words highlighting key features and breaking changes>

Thanks to the N contributors to this release:
<contributor list from pixi run release-contributors>

New Features
~~~~~~~~~~~~
...

Breaking Changes
~~~~~~~~~~~~~~~~
...

Bug Fixes
~~~~~~~~~
...

Documentation
~~~~~~~~~~~~~
...

Performance
~~~~~~~~~~~
...

Internal Changes
~~~~~~~~~~~~~~~~
...
```
