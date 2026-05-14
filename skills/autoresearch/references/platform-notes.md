# Platform notes for autoresearch

## Upstream fit

Best fit:
- single NVIDIA GPU
- enough VRAM for the default tiny training loop
- ability to run repeated 5-minute training experiments

Weak fit:
- Apple Silicon without using a fork
- CPU-only machines
- laptops where thermals/noise/power are a concern

## Practical advice on smaller machines

If adapting for smaller hardware, the README points to these levers:
- use a lower-entropy dataset like TinyStories
- reduce vocab size
- reduce max sequence length
- reduce eval token count
- reduce depth
- simplify attention/window patterns
- reduce total batch size

This means the right posture is:
- shrink the problem first
- keep experiments cheap and comparable
- do not pretend a MacBook is an H100 box

## Recommended approach on non-upstream hardware

1. Prefer a maintained fork from the README when possible.
2. If the user still wants local adaptation, state clearly that this is now a forking task, not a stock setup.
3. Make a single smoke test succeed before proposing unattended loops.
