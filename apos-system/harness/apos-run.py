#!/usr/bin/env python
"""Minimal APOS-X safe harness seed.

This first version is intentionally conservative: it can preflight commands,
inspect explicit CSV matrices, and block ambiguous production patterns. It does
not replace project-specific dry-run logic; it wraps it with traceable checks.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path.cwd()
EVIDENCE_DIR = ROOT / ".apos" / "evidence" / "harness-runs"


CRITICAL_PATTERNS = [
    "rm -rf",
    "del /s",
    "Remove-Item -Recurse",
    "rmdir /s",
    "format ",
    "DROP DATABASE",
    "git clean -fdx",
]


def run_id() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def write_evidence(kind: str, payload: str) -> Path:
    rid = run_id()
    outdir = EVIDENCE_DIR / rid
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{kind}.md"
    path.write_text(payload, encoding="utf-8")
    return path


def split_cmd(cmd: str) -> list[str]:
    try:
        return shlex.split(cmd, posix=False)
    except ValueError:
        return cmd.split()


def assess_command(cmd: str) -> tuple[bool, list[str]]:
    text = cmd.strip()
    tokens = split_cmd(text)
    reasons: list[str] = []

    for pattern in CRITICAL_PATTERNS:
        if pattern.lower() in text.lower():
            reasons.append(f"critical pattern: {pattern}")

    if "run_production.py" in text and "--pilot" in tokens and "--prod" in tokens:
        reasons.append("run_production.py with --pilot and --prod is ambiguous")

    if "run_production.py" in text or "--prod" in tokens:
        if "--dry-run" not in tokens and "--confirm-token" not in tokens:
            reasons.append("production command requires prior dry-run evidence or confirm token")
        if "--max-cases" not in tokens:
            reasons.append("production command requires --max-cases")
        if "--matrix" not in tokens:
            reasons.append("production command requires explicit --matrix")

    allowed = not reasons
    return allowed, reasons


def cmd_preflight(args: argparse.Namespace) -> int:
    allowed, reasons = assess_command(args.cmd)
    lines = [
        "# APOS-X preflight",
        "",
        f"Command: `{args.cmd}`",
        f"Allowed: {allowed}",
        "",
        "## Reasons",
    ]
    if reasons:
        lines.extend(f"- {r}" for r in reasons)
    else:
        lines.append("- no blocking rule matched")
    path = write_evidence("preflight", "\n".join(lines) + "\n")

    if allowed:
        print("APOS preflight OK")
    else:
        print("BLOQUEADO POR APOS SAFE-HARNESS")
        for reason in reasons:
            print(f"- {reason}")
    print(f"Evidence: {path}")
    return 0 if allowed else 2


def read_matrix(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def cmd_dry_run(args: argparse.Namespace) -> int:
    matrix = Path(args.matrix).resolve()
    rows = read_matrix(matrix)
    if len(rows) > args.max_cases and not args.allow_large:
        print("BLOQUEADO POR APOS SAFE-HARNESS")
        print(f"- matrix rows ({len(rows)}) exceed --max-cases ({args.max_cases})")
        return 2

    report = {
        "matrix": str(matrix),
        "rows": len(rows),
        "max_cases": args.max_cases,
        "allow_large": args.allow_large,
        "columns": list(rows[0].keys()) if rows else [],
        "case_ids": [r.get("case_id", "<missing>") for r in rows],
    }
    path = write_evidence("dry-run", "# APOS-X dry-run\n\n```json\n" + json.dumps(report, indent=2) + "\n```\n")
    print(json.dumps(report, indent=2))
    print(f"Evidence: {path}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    if not args.confirm_token:
        print("BLOQUEADO POR APOS SAFE-HARNESS")
        print("- run requires --confirm-token")
        return 2
    allowed, reasons = assess_command(args.cmd + " --confirm-token " + args.confirm_token)
    if reasons:
        print("BLOQUEADO POR APOS SAFE-HARNESS")
        for reason in reasons:
            print(f"- {reason}")
        return 2
    path = write_evidence("command", f"# APOS-X command\n\n```text\n{args.cmd}\n```\n")
    print(f"Evidence: {path}")
    return subprocess.call(args.cmd, shell=True)


def main() -> int:
    parser = argparse.ArgumentParser(prog="apos-run")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("preflight")
    p.add_argument("--cmd", required=True)
    p.set_defaults(func=cmd_preflight)

    p = sub.add_parser("dry-run")
    p.add_argument("--matrix", required=True)
    p.add_argument("--max-cases", type=int, required=True)
    p.add_argument("--allow-large", action="store_true")
    p.set_defaults(func=cmd_dry_run)

    p = sub.add_parser("run")
    p.add_argument("--cmd", required=True)
    p.add_argument("--confirm-token", required=False)
    p.set_defaults(func=cmd_run)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
