---
name: plot-check
description: Dispatch a subagent to review a plot image for visual issues and suggest fixes.
---

# Plot Check

Review a rendered plot for visual quality issues by dispatching a subagent. The
subagent analyzes both the rendered image and the code that produced it, then
returns a structured report of problems with specific code fixes. This keeps the
image analysis out of the main context window.

## When to Use

- After rendering a plot that the user will review
- Before presenting a visualization as "done"
- When the user asks you to check/review a plot
- Proactively after creating complex multi-panel figures, dense annotations, or
  plots with many overlapping elements

## How It Works

1. Spawn a **haiku** subagent with instructions to get the image, the plotting
   code (or instructions to retrieve it), and the review prompt
2. The subagent gets the image, analyzes it alongside the code, and returns a
   structured report of issues with code-level fixes
3. Apply fixes, re-render, and run another check
4. Repeat until the subagent reports no issues or only minor ones

Expect **2-3 rounds** for a typical complex figure. The first round catches the
obvious problems (overlap, contrast), later rounds catch subtler issues revealed
by the fixes.

## Getting the Image

The subagent should retrieve the image itself. Tell it how based on the
current environment:

- **Jupyter MCP available**: Tell the subagent to use `get_cell_outputs` on the
  plot cell to retrieve the rendered image directly, and `get_notebook_content`
  with the cell index to get the code. This is the simplest path — the subagent
  handles everything.
- **Saved to disk**: Tell the subagent to `Read` the image file at its path.
  Include the plotting code in the prompt directly.
- **Puppeteer/browser**: Tell the subagent to take a screenshot. Include the
  plotting code in the prompt directly.

## Subagent Prompt

Spawn a **haiku** subagent (cheap, fast, multimodal). Adapt the prompt based on
how the image and code are accessed.

### When Jupyter MCP is available

```
Review a plot for visual quality issues.

First, retrieve the plot:
1. Use `get_cell_outputs` on cell CELL_INDEX of notebook NOTEBOOK_PATH to see
   the rendered image
2. Use `get_notebook_content` with start_index=CELL_INDEX, end_index=CELL_INDEX+1
   to get the code that produced it

PLOT_CONTEXT (optional — what this plot is supposed to show, what data it
represents, what message it should convey)
```

### When image is on disk

```
Review this plot for visual quality issues. You have both the rendered image
and the code that produced it.

Read the image at: IMAGE_PATH

## Code That Produced This Plot
```python
PLOTTING_CODE
```

PLOT_CONTEXT (optional — what this plot is supposed to show, what data it
represents, what message it should convey)
```

### Review checklist (include in all variants)

Check for these issues and report ONLY problems you actually find:

## Overlapping Text
- Labels, annotations, or titles that overlap each other or data
- Tick labels that collide or are cut off
- Legend text overlapping chart elements

## Color & Contrast
- Colors that are too similar to distinguish
- Low-alpha elements that are hard to see against the background
- Poor contrast between data and background
- Colorbar or legend colors that don't match the described data

## Clutter & Density
- Too many elements competing for attention
- Redundant visual information (e.g., same data shown twice)
- Axes or panels that feel cramped or too empty
- Tick marks too dense or too sparse

## Missing or Misleading
- Axes without labels or units
- Data that looks wrong for what the plot claims to show
- Legends that don't match the visible elements
- Inconsistent formatting across panels
- Hardcoded values in labels that should reference variables

For each issue found, provide:
1. **What**: one-line description of the problem
2. **Where**: which part of the plot (e.g., "top-left panel legend", "x-axis ticks")
3. **Fix**: a specific code change — reference the exact line/variable in the
   plotting code and show what to change (e.g., "change `alpha=0.3` to `alpha=0.7`
   on the scatter call at line 12", "add `plt.subplots(..., constrained_layout=True)`")

If the plot looks good, say "No issues found" — don't invent problems.

Return issues sorted by severity (most visually distracting first).
```

## Applying Fixes

Read the subagent's report. Apply all fixes, re-render the plot, and save a new
image. Common fix patterns:

- **Overlapping text**: Reposition with `loc=`, `bbox_to_anchor=`, or increase
  `figsize`. Consider `constrained_layout=True` if not already set.
- **Color/contrast**: Increase alpha, choose more distinct colors, check against
  colorblind-safe palettes. Print actual data ranges if the color mapping might
  be wrong.
- **Clutter**: Remove redundant elements, increase spacing, consider splitting
  into multiple panels.
- **Missing labels**: Add them. Use f-strings on variables for any values that
  could change.

Then **run another check** with the updated image. Fixes often reveal new issues
(e.g., repositioning a legend may cause it to overlap something else). Stop when
the subagent reports no issues or the remaining issues are minor/subjective.

## Tips

- **The subagent must see both image and code** — it gives much better fixes when
  it can reference specific lines and variables. When using Jupyter MCP, the
  subagent retrieves both itself. Otherwise, include the code in the prompt.
- **Prefer Jupyter MCP when available** — letting the subagent call
  `get_cell_outputs` and `get_notebook_content` directly is simpler and avoids
  the main agent needing to save files or copy code into the prompt
- For multi-panel figures, the subagent catches issues you'd miss scanning code
- For data analysis plots, add to the context: "does this data look plausible?"
  — the subagent can spot obvious anomalies (flat lines, wrong scale, etc.)
- If the plot has many elements, describe what each represents so the subagent
  can check consistency between legend and data
- Don't run this on every tiny tweak — use it after first render, after major
  changes, and as a final check before showing the user
