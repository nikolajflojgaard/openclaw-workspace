#!/usr/bin/env python3
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
mod_path = ROOT / "scripts" / "humanize.py"
spec = importlib.util.spec_from_file_location("humanize", mod_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def run_case(inp, must_not_contain=(), must_contain=()):
    out, flags = mod.humanize(inp)
    low = out.lower()
    for s in must_not_contain:
        assert s.lower() not in low, f"found forbidden phrase: {s}\nOUT={out}\nFLAGS={flags}"
    for s in must_contain:
        assert s.lower() in low, f"missing required phrase: {s}\nOUT={out}\nFLAGS={flags}"


def test_stock_phrases_removed():
    run_case(
        "At the end of the day, it's worth noting this is a game-changer.",
        must_not_contain=("at the end of the day", "it's worth noting", "game-changer"),
        must_contain=("ultimately", "notably"),
    )


def test_performed_authenticity_removed():
    run_case(
        "Honestly, let's be real — as an AI language model, I think this is robust.",
        must_not_contain=("honestly", "let's be real", "as an ai language model"),
        must_contain=("strong",),
    )


def test_hedging_cluster_reduced():
    run_case(
        "This could maybe perhaps work, and it might possibly scale.",
        must_not_contain=("maybe perhaps", "might possibly"),
    )


def test_rule_of_three_pattern_softened():
    run_case(
        "We need speed, quality, and consistency in every release.",
        must_not_contain=("speed, quality, and consistency",),
    )


if __name__ == "__main__":
    test_stock_phrases_removed()
    test_performed_authenticity_removed()
    test_hedging_cluster_reduced()
    test_rule_of_three_pattern_softened()
    print("ok")
