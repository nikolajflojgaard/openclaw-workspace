#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

PHRASE_REPLACEMENTS = {
    r"\bat the end of the day\b": "ultimately",
    r"\bit'?s worth noting\b": "notably",
    r"\bin today'?s fast-paced world\b": "today",
    r"\blet'?s be real\b": "",
    r"\bto be honest\b": "",
    r"\bhonestly\b": "",
    r"\bspeaking candidly\b": "",
    r"\bas an ai( language model)?\b": "",
    r"\bdelving into\b": "exploring",
    r"\brobust\b": "strong",
    r"\bseamlessly\b": "smoothly",
    r"\bgame-?changer\b": "major shift",
}

HEDGE_WORDS = {
    "maybe", "perhaps", "arguably", "potentially", "possibly", "might", "could"
}

TRANSITIONS = {"moreover", "furthermore", "additionally"}


def clean_spacing(text: str) -> str:
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def reduce_hedging(text: str) -> str:
    words = text.split()
    out = []
    recent_hedges = 0
    for w in words:
        key = re.sub(r"[^a-z]", "", w.lower())
        if key in HEDGE_WORDS:
            recent_hedges += 1
            if recent_hedges > 1:
                continue
        else:
            recent_hedges = 0
        out.append(w)
    return " ".join(out)


def simplify_structure(text: str) -> str:
    # Em dash to comma (common AI cadence tell)
    text = text.replace("—", ", ")

    # Soften repetitive transitions at sentence start
    for t in TRANSITIONS:
        text = re.sub(rf"(?im)^\s*{t}\b[, ]*", "", text)

    # Break repetitive "X, Y, and Z" style by dropping filler adjective in long triads
    text = re.sub(r"\b(\w+),\s+(\w+),\s+and\s+(\w+)\b", r"\1 and \3", text)
    return text


def humanize(text: str):
    flags = []
    out = text

    for pat, repl in PHRASE_REPLACEMENTS.items():
        if re.search(pat, out, flags=re.IGNORECASE):
            flags.append(f"phrase:{pat}")
            out = re.sub(pat, repl, out, flags=re.IGNORECASE)

    if "—" in out:
        flags.append("structure:emdash")

    out2 = simplify_structure(out)
    if out2 != out:
        flags.append("structure:simplified")
    out = out2

    out2 = reduce_hedging(out)
    if out2 != out:
        flags.append("tone:hedging-reduced")
    out = out2

    out = clean_spacing(out)
    return out, sorted(set(flags))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="infile")
    p.add_argument("--out", dest="outfile")
    p.add_argument("--text", dest="text")
    args = p.parse_args()

    if not args.text and not args.infile:
        raise SystemExit("Provide --text or --in")

    raw = args.text if args.text is not None else Path(args.infile).read_text(encoding="utf-8")
    rewritten, flags = humanize(raw)

    if args.outfile:
        Path(args.outfile).write_text(rewritten, encoding="utf-8")
    else:
        print(rewritten)

    print("\n---")
    print(json.dumps({"flags": flags, "length_before": len(raw), "length_after": len(rewritten)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
