#!/usr/bin/env python3
"""Create a small agent workbench run packet."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from string import Template


DEFAULT_LANES = [
    {
        "name": "Intake",
        "goal": "Clarify objective, acceptance criteria, constraints, and non-goals.",
        "writes": "none",
    },
    {
        "name": "Map",
        "goal": "Inspect relevant files, repos, docs, systems, or source material.",
        "writes": "none",
    },
    {
        "name": "Build",
        "goal": "Implement the scoped change or produce the requested artifact.",
        "writes": "scoped task files only",
    },
    {
        "name": "Review",
        "goal": "Find bugs, security risks, missing validation, and unclear claims.",
        "writes": "none",
    },
    {
        "name": "Release",
        "goal": "Commit, publish, deploy, or hand off only after gates pass.",
        "writes": "release metadata only",
    },
]


BRIEF_TEMPLATE = """# ${name} Brief

## Objective

${objective}

## Context

This lane is part of an agent workbench run generated from the original request.

## Scope

${goal}

## Non-Goals

- Do not expand beyond the lane scope without reporting back to the hub.
- Do not perform public or external actions unless explicitly approved.

## Write Permissions

${writes}

## Privacy Boundaries

- Use only context needed for this lane.
- Do not expose secrets, private data, tokens, credentials, or unrelated user history.

## Expected Output

- status: done, blocked, partial, or no-change
- summary
- evidence
- changes
- validation
- risks
- handoff

## Validation

Run the strongest practical validation for this lane, or state the exact gap.

## Stop Conditions

- Unsafe external action is required.
- Write scope overlaps another lane.
- User changes would be overwritten.
- Validation failure changes the implementation plan.
"""


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:64] or "workbench-run"


def parse_lane(value: str) -> dict[str, str]:
    parts = [part.strip() for part in value.split(":", 2)]
    if len(parts) != 3 or not all(parts):
        raise argparse.ArgumentTypeError(
            "lanes must use the format 'Name:Goal:Writes'"
        )
    return {"name": parts[0], "goal": parts[1], "writes": parts[2]}


def lane_id(name: str) -> str:
    return slugify(name).replace("-", "_")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def create_run(args: argparse.Namespace) -> None:
    lanes = args.lane or DEFAULT_LANES
    output = args.output or Path(slugify(args.request))
    output.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    state = {
        "objective": args.request,
        "status": "pending",
        "created_at": created_at,
        "lanes": [
            {
                "id": lane_id(lane["name"]),
                "name": lane["name"],
                "goal": lane["goal"],
                "writes": lane["writes"],
                "status": "pending",
            }
            for lane in lanes
        ],
        "artifacts": [],
        "gates": [
            "request matched",
            "scope explicit",
            "user changes preserved",
            "write ownership respected",
            "validation complete or gap stated",
            "privacy protected",
            "external actions approved",
        ],
        "blocked": [],
        "notes": [],
    }

    plan_lines = [
        "# Workbench Plan",
        "",
        "## Objective",
        "",
        args.request,
        "",
        "## Lanes",
        "",
    ]
    for lane in state["lanes"]:
        plan_lines.append(
            f"- **{lane['name']}**: {lane['goal']} (writes: {lane['writes']})"
        )

    write_text(output / "plan.md", "\n".join(plan_lines) + "\n")
    write_text(output / "state.json", json.dumps(state, indent=2) + "\n")

    for lane in state["lanes"]:
        brief = Template(BRIEF_TEMPLATE).substitute(
            name=lane["name"],
            objective=args.request,
            goal=lane["goal"],
            writes=lane["writes"],
        )
        write_text(output / "briefs" / f"{lane['id']}.md", brief)

    write_text(
        output / "gate-checklist.md",
        "# Gate Checklist\n\n"
        "- [ ] The result still matches the user's request.\n"
        "- [ ] Scope changes are explicit.\n"
        "- [ ] User or unrelated worktree changes are preserved.\n"
        "- [ ] One-writer-per-surface was respected.\n"
        "- [ ] Validation ran, or the exact gap is stated.\n"
        "- [ ] Secrets and private data were not exposed.\n"
        "- [ ] Public/external actions were approved.\n"
        "- [ ] CI/deploy status was checked when relevant.\n"
        "- [ ] Final report names commits, links, artifacts, or proposals.\n",
    )
    write_text(
        output / "final-report.md",
        "# Final Report\n\n"
        "## Shipped\n\n- \n\n"
        "## Lanes\n\n- \n\n"
        "## Validation\n\n- \n\n"
        "## Artifacts\n\n- \n\n"
        "## Residual Risks\n\n- \n\n"
        "## Next Action\n\n- \n",
    )

    print(f"Created workbench run at {output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="create a workbench run packet")
    create.add_argument("request", help="original user request")
    create.add_argument(
        "--lane",
        action="append",
        type=parse_lane,
        help="lane as 'Name:Goal:Writes'; repeat for multiple lanes",
    )
    create.add_argument(
        "--output",
        type=Path,
        help="output directory for the run packet",
    )
    create.set_defaults(func=create_run)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
