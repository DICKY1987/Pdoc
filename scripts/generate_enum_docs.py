"""Generate markdown documentation from enum registry YAML."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Any

import json


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def _section_markdown(name: str, items: List[Dict[str, Any]]) -> str:
    headers: List[str] = []
    for item in items:
        for key in item.keys():
            if key not in headers:
                headers.append(key)
    lines = [f"# {name.replace('_', ' ').title()}"]
    lines.append("| " + " | ".join(h.capitalize() for h in headers) + " |")
    lines.append("|" + " | ".join(["---"] * len(headers)) + " |")
    for item in items:
        row = [str(item.get(h, "")) for h in headers]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    return "\n".join(lines)


def generate(schema_path: Path, output_path: Path) -> None:
    data = _load(schema_path)
    sections = [
        _section_markdown(section, items)
        for section, items in data.items()
    ]
    output_path.write_text("\n".join(sections))


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Generate enum documentation")
    parser.add_argument("schema", type=Path, help="Path to enums.json")
    parser.add_argument("output", type=Path, help="Destination markdown file")
    args = parser.parse_args()
    generate(args.schema, args.output)
    print(f"Generated {args.output}")


if __name__ == "__main__":
    _cli()

