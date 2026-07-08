---
name: hypothesis-failure-investigation
description: Triage and diagnose Hypothesis stateful test failures.
---

# Hypothesis Failure Investigation

Investigate a Hypothesis stateful test failure: triage, reproduce, identify root cause
(test bug vs real bug), fix, and propagate.

## Phase 1: Triage

1. **Read the traceback carefully.** Identify:
   - The exact failing line (file, method, line number)
   - The Hypothesis falsifying example (the state machine operation sequence)
   - Whether the error is in test code or production code
2. **Ensure correct branch and up-to-date state.** Run `git status`, confirm you're
   on the right branch, and `git pull` if needed. If the failure came from CI,
   confirm the local branch head matches the CI run's commit.
3. **Read the failing test file and the method that raised.** Understand the state
   machine class hierarchy — check for parent/child `@rule` relationships.
4. **If the failing code is in a dependency**, find its installed source by
   printing `<pkg>.<module>.__file__` from within the project's Python environment.

## Phase 2: Reproduce

Ensure the project builds and tests can run before attempting reproduction.
Check the project's CLAUDE.md or contributing docs for build instructions.

The approach depends on whether the failure is **deterministic** or **stochastic**:

### Deterministic failures (MRO conflicts, TypeErrors, missing args)
The falsifying example from the traceback is enough — analyze it directly.
No reproduction script needed; the error will occur on every run with that
state sequence.

### Stochastic failures (precondition gaps, race conditions)
1. **Use the `@reproduce_failure` decorator** if Hypothesis printed one in the
   output. Add it to the test function temporarily and run:
   ```
   uv run pytest <test_file>::<test_function> -xvs
   ```
2. **Never brute-force seeds.** The seed space is enormous and guessing is
   impractical. If `@reproduce_failure` is not available, shift to static
   analysis — read the precondition and method body, look for mismatches.
3. **Write a minimal standalone reproduction script** if static analysis finds
   the bug. Keep it simple:
   - Just the essential API calls that demonstrate the bug
   - No unnecessary prints, wrappers, or Hypothesis machinery

## Phase 3: Root Cause Analysis

**CRITICAL: Discuss the root cause with the user before proceeding to a fix.**

Present your analysis:
- What the bug is (concisely)
- Whether it's a **test bug** or a **real bug** (see below)
- The specific code path that leads to the failure
- Any related code that might have the same issue

### Test Bug vs Real Bug

This is the key decision point. Common test bugs in Hypothesis stateful tests:

- **Precondition/body mismatch** — precondition allows a state where the body
  crashes. Often happens when the body filters a collection further than the
  precondition checks (e.g. precondition ensures `len(groups) >= 2` but body
  filters to nested groups only, which can be empty).
- **MRO `@rule` signature conflicts** — subclass overrides a parent `@rule`
  method with a different signature (e.g. adds a required `data` parameter).
  Parent methods that call `self.method()` with the original args dispatch via
  MRO to the incompatible subclass override. Fix by using distinct method names
  or making the extra parameter optional.
- **Model state divergence** — the test model tracks state that silently diverges
  from the system under test after certain operations (e.g. an upgrade resets an
  ops log to length 1 but the model keeps incrementing its counter). Check: does
  every state-changing operation update the model consistently?
- **Stale hypothesis cache** — `.hypothesis/examples/` contains cached falsifying
  examples from before a `@rule` signature change, causing confusing secondary
  failures unrelated to the actual bug.

Real bugs surface when the system under test violates its own invariants under
a valid sequence of operations. These need fixes in production code, not test code.
Real bugs in upstream dependencies are also possible — the precondition/body
mismatch pattern applies equally to upstream state machine classes you inherit from.

## Decision Points (always ask the user)

- Is this a test bug or a real bug? (Phase 3)
- Is the bug in our code or in a dependency?
- Confirm the root cause analysis before the user proceeds to fix

## Common Pitfalls

- **Never brute-force Hypothesis seeds.** The seed space is enormous. Use
  `@reproduce_failure` or shift to static analysis.
- **Check sibling test files.** If one stateful test file has the bug, related
  test files likely have the same pattern.
- **Stale hypothesis cache.** If `@rule` signatures changed, `.hypothesis/examples/`
  may contain invalid cached examples that cause confusing secondary failures.
