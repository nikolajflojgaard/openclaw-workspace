#!/usr/bin/env python3
"""Create a read-only memory distillation packet."""

from __future__ import annotations

import argparse
import re
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path


DAILY_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")


def parse_date_from_name(path: Path) -> date:
    return datetime.strptime(path.stem, "%Y-%m-%d").date()


def recent_daily_notes(workspace: Path, days: int) -> list[Path]:
    memory_dir = workspace / "memory"
    if not memory_dir.exists():
        return []
    cutoff = date.today() - timedelta(days=days - 1)
    notes = []
    for path in memory_dir.glob("*.md"):
        if not DAILY_NAME.match(path.name):
            continue
        if parse_date_from_name(path) >= cutoff:
            notes.append(path)
    return sorted(notes)


def extract_candidate_lines(path: Path, limit: int) -> list[str]:
    candidates: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("- "):
            continue
        if any(token in line.lower() for token in ["token", "secret", "password"]):
            candidates.append("- [privacy-sensitive candidate omitted]")
            continue
        candidates.append(line)
        if len(candidates) >= limit:
            break
    return candidates


def git_commits(repo: Path, days: int) -> list[str]:
    if not (repo / ".git").exists():
        return [f"- {repo}: not a Git repository"]
    since = f"{days} days ago"
    command = [
        "git",
        "-C",
        str(repo),
        "log",
        f"--since={since}",
        "--pretty=format:- %h %s",
        "--max-count=20",
    ]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return [f"- {repo}: git log failed"]
    output = result.stdout.strip()
    if not output:
        return [f"- {repo}: no recent commits"]
    return output.splitlines()


def render_packet(args: argparse.Namespace) -> str:
    workspace = args.workspace.expanduser().resolve()
    notes = recent_daily_notes(workspace, args.days)
    lines = [
        "# Memory Distillation Packet",
        "",
        "## Workspace",
        "",
        f"`{workspace}`",
        "",
        "## Daily Notes Reviewed",
        "",
    ]

    if notes:
        lines.extend(f"- `{note.relative_to(workspace)}`" for note in notes)
    else:
        lines.append("- None")

    lines.extend(["", "## Candidate Daily Bullets", ""])
    if notes:
        for note in notes:
            lines.append(f"### {note.name}")
            candidates = extract_candidate_lines(note, args.max_bullets_per_note)
            lines.extend(candidates or ["- No bullet candidates found"])
            lines.append("")
    else:
        lines.append("- No daily notes found in scope")

    lines.extend(["", "## Commit Context", ""])
    if args.repo:
        for repo in args.repo:
            repo_path = repo.expanduser().resolve()
            lines.append(f"### `{repo_path}`")
            lines.extend(git_commits(repo_path, args.days))
            lines.append("")
    else:
        lines.append("- No repositories included")

    lines.extend(
        [
            "",
            "## Distillation Plan",
            "",
            "### Promote To MEMORY.md",
            "",
            "- ",
            "",
            "### Revise In MEMORY.md",
            "",
            "- ",
            "",
            "### Remove From MEMORY.md",
            "",
            "- ",
            "",
            "### Keep Daily Only",
            "",
            "- ",
            "",
            "### Privacy Flags",
            "",
            "- ",
            "",
            "### No-Change Rationale",
            "",
            "- Use this when nothing deserves promotion.",
            "",
            "## Checklist",
            "",
            "- [ ] Promotions are stable and reusable.",
            "- [ ] One-off logs stay in daily notes.",
            "- [ ] Secrets and sensitive personal data are excluded.",
            "- [ ] Control-file rules are not buried in MEMORY.md.",
            "- [ ] Index rebuild decision is explicit.",
            "",
        ]
    )
    return "\n".join(lines)


def command_packet(args: argparse.Namespace) -> int:
    packet = render_packet(args)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(packet, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(packet)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    packet = subparsers.add_parser("packet", help="create a distillation packet")
    packet.add_argument("workspace", type=Path, help="workspace containing memory/")
    packet.add_argument("--days", type=int, default=7, help="recent days to review")
    packet.add_argument(
        "--repo",
        action="append",
        type=Path,
        help="optional Git repo to include recent commits from",
    )
    packet.add_argument(
        "--max-bullets-per-note",
        type=int,
        default=20,
        help="maximum daily note bullets to include per note",
    )
    packet.add_argument("--out", type=Path, help="output Markdown path")
    packet.set_defaults(func=command_packet)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if getattr(args, "days", 1) < 1:
        parser.error("--days must be at least 1")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
