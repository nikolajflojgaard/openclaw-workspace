#!/usr/bin/env python3
"""Validate QA findings and render a concise red-team report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SEVERITY_ORDER = {
    "blocker": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "question": 4,
    "risk": 5,
}

REQUIRED_TOP_LEVEL = [
    "status",
    "scope",
    "findings",
    "questions",
    "validation_gaps",
    "risks",
    "summary",
    "handoff",
]

REQUIRED_FINDING = [
    "severity",
    "title",
    "evidence",
    "impact",
    "recommendation",
    "confidence",
]


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: root must be a JSON object")
    return value


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    findings = payload.get("findings", [])
    if not isinstance(findings, list):
        errors.append("findings must be a list")
        return errors

    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            errors.append(f"findings[{index}] must be an object")
            continue
        for key in REQUIRED_FINDING:
            if not finding.get(key):
                errors.append(f"findings[{index}] missing field: {key}")
        severity = finding.get("severity")
        if severity and severity not in SEVERITY_ORDER:
            errors.append(
                f"findings[{index}] severity must be one of: "
                + ", ".join(SEVERITY_ORDER)
            )

    for key in ["questions", "validation_gaps", "risks"]:
        if key in payload and not isinstance(payload[key], list):
            errors.append(f"{key} must be a list")

    return errors


def sorted_findings(payload: dict[str, Any]) -> list[dict[str, Any]]:
    findings = payload.get("findings", [])
    return sorted(
        findings,
        key=lambda item: (
            SEVERITY_ORDER.get(item.get("severity", "risk"), 99),
            item.get("title", ""),
        ),
    )


def format_location(finding: dict[str, Any]) -> str:
    file_name = finding.get("file")
    line = finding.get("line")
    if file_name and line:
        return f"{file_name}:{line}"
    if file_name:
        return str(file_name)
    return "n/a"


def bullet_list(values: list[Any], empty: str) -> str:
    if not values:
        return f"- {empty}\n"
    return "".join(f"- {value}\n" for value in values)


def render_report(payload: dict[str, Any]) -> str:
    findings = sorted_findings(payload)
    blockers = [item for item in findings if item.get("severity") == "blocker"]
    normal = [item for item in findings if item.get("severity") != "blocker"]

    lines = [
        "# QA / Red-Team Report",
        "",
        "## Scope",
        "",
        str(payload.get("scope", "")),
        "",
        "## Blockers",
        "",
    ]

    if blockers:
        for finding in blockers:
            lines.extend(format_finding(finding))
    else:
        lines.append("- None")

    lines.extend(["", "## Findings", ""])
    if normal:
        for finding in normal:
            lines.extend(format_finding(finding))
    else:
        lines.append("- No findings")

    lines.extend(["", "## Questions", "", bullet_list(payload.get("questions", []), "None").rstrip()])
    lines.extend(
        [
            "",
            "## Validation Gaps",
            "",
            bullet_list(payload.get("validation_gaps", []), "None").rstrip(),
        ]
    )
    lines.extend(
        [
            "",
            "## Low-Confidence Risks",
            "",
            bullet_list(payload.get("risks", []), "None").rstrip(),
        ]
    )
    lines.extend(["", "## Summary", "", str(payload.get("summary", ""))])
    lines.extend(["", "## Handoff", "", str(payload.get("handoff", "")), ""])
    return "\n".join(lines)


def format_finding(finding: dict[str, Any]) -> list[str]:
    title = finding.get("title", "Untitled")
    severity = finding.get("severity", "risk")
    confidence = finding.get("confidence", "unknown")
    return [
        f"### {severity.upper()}: {title}",
        "",
        f"- Evidence: {finding.get('evidence')}",
        f"- Location: {format_location(finding)}",
        f"- Impact: {finding.get('impact')}",
        f"- Recommendation: {finding.get('recommendation')}",
        f"- Confidence: {confidence}",
        "",
    ]


def command_validate(args: argparse.Namespace) -> int:
    payload = load_json(args.findings)
    errors = validate_payload(payload)
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print(f"{args.findings}: valid")
    return 0


def command_report(args: argparse.Namespace) -> int:
    payload = load_json(args.findings)
    errors = validate_payload(payload)
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    report = render_report(payload)
    if args.out:
        args.out.write_text(report, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(report)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate findings JSON")
    validate.add_argument("findings", type=Path)
    validate.set_defaults(func=command_validate)

    report = subparsers.add_parser("report", help="render findings as Markdown")
    report.add_argument("findings", type=Path)
    report.add_argument("--out", type=Path, help="Markdown output path")
    report.set_defaults(func=command_report)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
