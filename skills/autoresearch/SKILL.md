---
name: autoresearch
description: Use Karpathy's autoresearch workflow when the user wants to run, adapt, audit, or operationalize the autoresearch repo or idea for autonomous ML experimentation. Use for: cloning/setting up autoresearch, explaining how it works, adapting it to local hardware, turning it into a repeatable workflow, editing program.md guidance, or evaluating whether it fits the user's machine and goals. Do not use for generic web research or ordinary GitHub repo browsing.
---

# autoresearch

Use this skill when the task is specifically about **karpathy/autoresearch** or the pattern of autonomous overnight ML experiments.

## What this repo is

`autoresearch` is a tiny autonomous research loop around a real training setup:
- `prepare.py` handles one-time data prep and runtime utilities
- `train.py` is the file the agent iterates on
- `program.md` is the human-written research-org instruction file for the agent

The important mental model: **the human edits `program.md`; the agent edits `train.py`.**

## Default workflow

1. Inspect the target machine first.
   - Check whether the machine has an NVIDIA GPU.
   - If not, say the upstream repo is not a direct fit and recommend a fork or adaptation path.
2. Inspect the repo state.
   - Read `README.md` and `program.md`.
   - Identify whether the user wants explanation, setup, adaptation, or operationalization.
3. Pick the correct path:
   - **Explain/evaluate**: summarize fit, risks, and operating model.
   - **Setup**: install deps, run `uv sync`, then `uv run prepare.py`, then a single `uv run train.py` smoke test.
   - **Adaptation**: prefer changing `program.md` and environment guidance before broad code churn.
   - **Operationalization**: create scripts/docs/automation around safe experiment running and result review.
4. Keep scope tight.
   - Avoid casually turning this into a broad ML platform project.
   - Preserve the repo's core constraint: small surface area, fast comparable iterations.

## Platform guidance

Upstream `autoresearch` expects:
- single NVIDIA GPU
- Python 3.10+
- `uv`

If the user is on macOS / Apple Silicon / CPU-only, say so bluntly:
- upstream is not the right default
- consider one of the forks from the README instead
- if adapting locally, lower ambition and tune for tiny experiments, not parity with H100 assumptions

Read `references/platform-notes.md` when you need the practical adaptation summary.

## Repo operation rules

When working in an autoresearch checkout:
- treat `prepare.py` as effectively fixed unless the user explicitly wants deeper adaptation
- expect the agent/research loop to modify `train.py`
- use `program.md` as the primary place to encode research policy and workflow
- prefer one small validated change at a time

## Safety / practicality

This project can burn compute fast. Before operationalizing it:
- check hardware fit
- check cost/thermals expectations
- avoid unattended long-running changes unless the user clearly wants that
- if adding automation, make reviewability and stop conditions explicit

## Output style

Be concrete, not mystical.

Good outputs for this skill:
- "This repo is a bad fit for your Mac; use an MLX/macOS fork instead."
- "I'll adapt `program.md` so the agent explores only optimizer and depth changes."
- "I'll set up a smoke-test run first before any unattended loop."

Avoid vague hype about autonomous research. The useful part is the operating loop, not the sci-fi framing.
