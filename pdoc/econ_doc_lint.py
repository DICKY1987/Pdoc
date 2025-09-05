#!/usr/bin/env python3
"""Lint economic specification Markdown documents.

Validate ``BEGIN``/``END`` markers, cross references, and required metadata
fields inside one or more Markdown files.

Args:
    FILE [FILE ...]: Markdown files to lint.
    -s, --strict: Enable additional checks such as detecting duplicate block
        IDs.

Exit codes:
    0: All files pass linting.
    1: Lint errors were found or a file could not be read.
    2: Invalid command line usage.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

ID_RE = re.compile(
    r"^<!-- BEGIN:(ECON\.\d{3}\.\d{3}\.\d{3}\.(DEF|REQ|TABLE|FLOW|ALERT|ARCH|CTRL|EXAMPLE|ACCEPTANCE)\.[a-z0-9_]+) -->$"
)
END_RE = re.compile(
    r"^<!-- END:(ECON\.\d{3}\.\d{3}\.\d{3}\.(DEF|REQ|TABLE|FLOW|ALERT|ARCH|CTRL|EXAMPLE|ACCEPTANCE)\.[a-z0-9_]+) -->$"
)
REF_RE = re.compile(r"@ECON\.\d+\.\d+")


def lint_text(text: str, *, strict: bool = False) -> list[str]:
    """Return a list of lint errors for *text*.

    Parameters
    ----------
    text:
        Markdown content to check.
    strict:
        Whether to enable additional strict validations.
    """

    lines = text.splitlines()
    errors: list[str] = []
    stack: list[tuple[str, int]] = []
    ids: set[str] = set()

    for i, line in enumerate(lines, 1):
        m = ID_RE.match(line.strip())
        if m:
            bid = m.group(1)
            if strict and bid in ids:
                errors.append(f"{i}: Duplicate BEGIN id: {bid}")
            stack.append((bid, i))
            ids.add(bid)
            continue
        m = END_RE.match(line.strip())
        if m:
            eid = m.group(1)
            if not stack:
                errors.append(f"{i}: END without BEGIN: {eid}")
            else:
                bid, bi = stack.pop()
                if bid != eid:
                    errors.append(
                        f"{i}: END id mismatch. BEGIN at {bi} was {bid}, END is {eid}"
                    )
            continue

    if stack:
        for bid, bi in stack:
            errors.append(f"{bi}: Unclosed BEGIN: {bid}")

    # Cross-ref sanity: section prefix resolution
    for ref in REF_RE.findall(text):
        try:
            _, major, minor = ref.split(".")
            prefix = f"ECON.{int(major):03d}.{int(minor):03d}."
            if not any(x.startswith(prefix) for x in ids):
                errors.append(
                    f"Cross-ref {ref} has no matching section prefix among block IDs"
                )
        except Exception:
            errors.append(f"Malformed cross-ref: {ref}")

    # CSV required meta fields appear at least once in the doc
    for required in ["file_seq", "created_at_utc", "checksum_sha256"]:
        if required not in text:
            errors.append(f"Missing required CSV meta field in doc: {required}")

    return errors


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""

    parser = argparse.ArgumentParser(
        description="Lint economic specification Markdown files."
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Markdown files to lint",
    )
    parser.add_argument(
        "-s",
        "--strict",
        action="store_true",
        help="Enable additional strict checks",
    )
    args = parser.parse_args(argv)

    failed = False
    for path in args.files:
        p = Path(path)
        try:
            text = p.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"{p}: {exc}", file=sys.stderr)
            failed = True
            continue

        errors = lint_text(text, strict=args.strict)
        if errors:
            failed = True
            print(f"{p}:")
            print("\n".join(errors))
        else:
            print(f"{p}: OK")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

