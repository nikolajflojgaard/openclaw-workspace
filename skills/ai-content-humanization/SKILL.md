---
name: ai-content-humanization
description: Rewrite AI-flavored text so it sounds like a real person wrote it. Use when drafting or editing social posts, blog paragraphs, emails, scripts, landing-page copy, or other prose that feels generic, over-polished, repetitive, inflated, or obviously model-generated. Also use when the user asks to make writing more human, less robotic, less LinkedIn-cringe, more conversational, or better tuned to a destination channel.
---

# AI Content Humanization

Rewrite for credibility, clarity, and human cadence.

Do not merely swap synonyms. Remove the underlying patterns that make text feel generated.

## Core workflow

1. Identify the real message.
2. Detect obvious AI tells.
3. Rewrite for specificity, rhythm, and voice.
4. Tune for the destination channel if known.
5. Return clean final copy first.
6. Explain major changes only if the user asks or if the rewrite involved a strong directional choice.

## Detect AI tells

Look for these patterns:

- bloated framing (`it's important to note`, `in today's fast-paced world`, `in conclusion`)
- inflated adjectives (`game-changing`, `revolutionary`, `transformative`) without proof
- vague business sludge (`leverage`, `unlock`, `navigate the landscape`)
- generic claims that could fit any topic
- repetitive sentence openings or uniform sentence length
- listicles that are too parallel and too clean
- hedging and throat-clearing
- bland transitions that add no meaning
- conclusions that restate instead of land

Also check for a deeper problem: text that is technically fine but has no point of view.

## Rewrite rules

Always prefer:

- concrete nouns and verbs over abstract phrasing
- shorter openings
- varied sentence length
- contractions when natural
- small asymmetries in rhythm
- selective bluntness over fake polish
- one sharp point over three diluted ones

Avoid adding fake personality. Human does not mean sloppy cosplay.

Do not:

- invent personal stories or experiences
- add unsupported claims
- force slang where it does not belong
- keep filler just because it sounds “professional”

## Channel tuning

If the target channel is clear, tune to it.

### X / short social
- get to the point fast
- trim setup
- keep punch and tension
- remove anything that reads like content marketing

### LinkedIn
- keep authority, remove puffery
- sound like a competent adult, not a brand team
- allow opinion and edge, but keep it readable

### Blog / essay
- preserve structure and depth
- vary paragraph rhythm
- keep argument flow intact
- let the voice have a point of view

### Email
- optimize for clarity and action
- keep warmth, remove ceremony
- default to brief unless the situation clearly needs detail

## Output modes

Default: return only the rewritten text.

Optional modes when asked:
- **light pass**: preserve most wording, remove obvious AI residue
- **heavy pass**: rewrite aggressively for stronger voice and clarity
- **with notes**: include a short list of what changed and why
- **multi-variant**: provide 2-3 distinct versions for different tones

## Heuristics for good final copy

The rewrite should usually be:

- shorter than the input
- more specific than the input
- less symmetrical than the input
- more opinionated than the input when appropriate
- easier to say out loud

A useful test: if every sentence feels equally polished, it still probably sounds generated.

## Example transformations

### Corporate sludge
Input:
> It is important to note that leveraging AI in today's evolving landscape can be transformative for organizations seeking to unlock efficiency.

Better:
> AI can save teams time, but only when it is wired into real workflows instead of sitting in demo-land.

### Generic LinkedIn tone
Input:
> I’m excited to share some thoughts on how innovation is reshaping the future of work.

Better:
> Most “future of work” talk is recycled fluff. The real shift is simpler: more decisions get automated, and badly designed systems break faster.

### Over-generated list
Input:
> There are three key considerations: scalability, adaptability, and stakeholder alignment.

Better:
> Three things matter here: can it scale, can it change without breaking, and will anyone actually use it?

## If the user provides style guidance

Match it. If they say:

- “make it more blunt” → cut softness and get to the point
- “make it warmer” → soften transitions, keep clarity
- “less AI” → reduce symmetry, filler, inflated language
- “more human” → increase specificity and cadence, not gimmicks
- “sound like me” → mimic only from supplied samples or explicit guidance

## Reference

For the original source brief this skill was derived from, read `references/source-brief.md`.
