---
name: doc-writing
description: Write technical documentation with strong narrative structure and crosslinking.
---

# Doc Writing

Guide for writing technical documentation — tutorials, reference docs, blog
posts, research notebooks, contributor guides — with strong narrative structure,
clear introductions, effective crosslinking, and appropriate tone.

## Before Writing: Establish Context

Before drafting anything, clarify these with the user (or infer from context):

### 1. Audience

Who is reading this? The answer changes everything:

- **End users** — focus on "how to use", hide internals
- **Contributors** — focus on "how it works", show internals
- **Researchers/learners** — focus on "why", build up from first principles
- **Decision-makers** — focus on "what it does and why it matters"

Hold audience constant throughout every section. If a page is for contributors,
every section must be for contributors. Audience drift within a page is confusing.

### 2. Writing Style

Don't assume a style — detect it from existing content or ask. Different
contexts call for different voices:

- A blog post might want personality and energy
- API reference docs want precision and consistency
- A tutorial wants warmth and encouragement
- Contributor docs want directness and specificity

If the project already has docs, read them first and match their voice. If
starting fresh, ask: "What tone are you going for?"

When the user has written prose, treat their phrasing as intentional. Don't
rewrite their words — build around them. If you think something should change,
suggest rather than replace.

### 3. Type of Document

| Type | Key concern |
|------|-------------|
| Tutorial/notebook | Progressive build-up, pose problem before solution |
| Reference docs | Completeness, consistent format, dependency ordering |
| Blog post | Narrative arc, concrete examples, appropriate energy |
| Contributor guide | Internals focus, verified claims, "why" behind decisions |
| Research notebook | Separate spec/reference from experiments |

## Narrative Structure Principles

These apply across all doc types. The user owns the structure — never reorganize
sections without asking first.

### Start with the destination

The most important concept belongs at the top as a motivating hook. Don't define
building blocks first and leave the reader wondering what they're for. Show the
destination, then explain the journey to get there from the ground up.

### Order by dependency

If Concept A references Concept B, define B first. A reader hitting a forward
reference ("...see Manifest below") loses context and trust. Within a section
that introduces multiple concepts, order them so each builds on already-defined
vocabulary.

### Pose the problem before the solution

Motivation must come first, and it must be concrete — a specific example of
what fails without the mechanism you're introducing. Abstract motivation
("useful for high-dimensional data") is weaker than concrete motivation
("how would we color a map based on scattered observations?").

### Each section answers the previous section's question

Structure transitions so each section raises a question the next section answers.
At the macro level this gives the document a narrative arc. At the micro level
(within a section) each paragraph can do the same: state the situation, introduce
the tension, resolve it.

### Name the progression

When building from simple to complex, state it explicitly: "Let's start with 1D,
then extend to 2D." The reader needs to know they are at step 1 of N, not that
you happen to be discussing a simpler case.

### Separate reference from exploration

Within a single page, don't mix definition/spec content with
experimental/exploratory content. If a page has both, split into clearly labeled
sections: reference material at the top, experiments/exploration below.

### Defer bookend pages

Introduction and summary pages are easier to write last. The intro can accurately
scope what the doc covers; the summary can synthesize what was actually found.
Writing them first produces vague framing.

### Use scope notes

When a page covers only part of a larger system, state what it covers and what
it does not at the top: "This page covers types that are persisted to storage.
For in-memory types, see session.md."

## Crosslinking

### Link everything linkable

- Language concepts → language docs (Rust Book, Python docs, MDN)
- Domain terms → Wikipedia or authoritative reference
- Internal types/concepts → anchor links within the doc or to sibling pages
- Config types → generated API docs (docs.rs, ReadTheDocs)

### Make cross-links symmetric and prominent

When two documents are complementary, both must link to the other. Place links
early (top of page) using an admonition or callout that makes the relationship
clear. Don't bury cross-references in prose mid-page.

### Keep local copies of external specs

If you're documenting against an external specification, keep a local copy in
the doc tree so internal cross-references work without network dependency and
don't break when the external resource moves.

### Use line-level code references

When referencing code, link to specific lines (GitHub permalinks), not just
files. Show both the problem location and the fix location when documenting
changes.

## Code + Prose Integration

### Verify claims before writing them

A prose assertion about code behavior ("the KD-tree picks the wrong point") is
not acceptable until a code cell or test confirms it. The code is ground truth;
the prose describes what the code shows.

### No speculation about design rationale

If you cannot find a design rationale in the source code or comments, don't
invent one. Remove or flag it as an open question.

### Hide boilerplate, show the interesting code

For notebooks: use `hide-input` on cells that only produce a figure — the output
matters for learning; the matplotlib configuration does not. Keep visible any
cell that demonstrates the API or concept being documented.

### Pre-compute outputs for static builds

For Jupyter Book / Sphinx builds that render notebooks statically, all code
outputs must be saved in the `.ipynb` file (`jupyter execute --inplace`). Empty
outputs will not render.

### Real artifacts over constructed examples

Actual diffs, real command output, real file paths are more compelling than
polished summaries or synthetic examples. Show the real thing when possible.

## Diagrams

### Diagrams must be exactly correct

An approximate diagram that is "mostly right but mistaken in some places" teaches
the wrong mental model. Verify every node and edge against actual code/data.
If you're not certain a diagram is correct, verify by reading the source.

### Simplify for comprehension

If a diagram is too busy to understand at a glance, it fails. Prefer fewer
nodes with clearer labels over architectural completeness. A diagram's job is
to build a mental model, not to be an exhaustive map.

### Use sequential panels for processes

A single complex diagram showing an end state is harder to follow than N panels
showing N steps. Each step of a search, transformation, or pipeline gets its own
panel.

## Review: Dispatch a Subagent

For longer documents, dispatch a subagent to review narrative flow and structure.
This keeps the review analysis out of the main context. Prompt:

```
Read the document at: DOC_PATH

Assess it for:

1. **Narrative flow** — Does each section build on the previous? Are there
   forward references to concepts not yet introduced? Does the reader always
   know why they're reading the current section?

2. **Audience consistency** — Is the document consistently written for
   [AUDIENCE]? Flag any sections that drift to a different audience.

3. **Missing motivation** — Are there concepts introduced without explaining
   why they matter? Flag sections that jump to "what" without "why".

4. **Crosslink opportunities** — Are there terms or concepts that should link
   to other docs, external references, or code?

5. **Scope clarity** — Is it clear at the top what this document covers and
   what it doesn't?

For each issue, quote the specific passage and suggest a fix.
```

The user should see the review before changes are made — present the findings
and ask which to address.
