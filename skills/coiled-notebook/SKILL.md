---
name: coiled-notebook
description: Launch a Coiled cloud Jupyter notebook and connect via the jupyter MCP. Use when the user wants to start, spin up, or use a Coiled notebook for remote execution.
---

# Coiled Notebook Launch + Connect

Start a Coiled cloud JupyterLab, grab its URL, connect via `mcp__jupyter__connect_jupyter`.

## When to use

- User asks to start / spin up / launch / use a Coiled notebook
- User wants the agent to drive `coiled notebook start`

## Prerequisites

Coiled requires both `coiled` and `jupyterlab` on the local machine. If `jupyterlab` is missing, Coiled refuses to launch. If either is only in a project venv, prefix commands with `uv run` from that directory.

## Launch (background)

```bash
coiled notebook start \
  --name <session-name> \
  --vm-type c7a.medium \
  --idle-timeout 15m \
  --no-block \
  2>&1 | tee /tmp/coiled-start.log
```

Run with `run_in_background: true` — provisioning takes 2-5 min.

Don't use `--cpu 1 --memory 2GiB` alone: Coiled rejects tiny specs without an explicit `--vm-type`. `c7a.medium` (1 CPU, 2 GiB) is the smallest it accepts.

## Extract URL

```bash
grep -oE 'https://[^ ]+/jupyter/lab\?token=[^ ]+' /tmp/coiled-start.log | head -1
```

Pattern: `https://cluster-<hash>.dask.host/jupyter/lab?token=<token>` — note the `/jupyter/` base path.

If grep returns nothing, `cat /tmp/coiled-start.log` and surface the error to the user.

## Connect

Pass the URL to `mcp__jupyter__connect_jupyter`. Proceed with whatever the user asked for.

## Teardown

```bash
coiled notebook stop --name <session-name>
```

The `--idle-timeout 15m` is a fallback if the user walks away.
