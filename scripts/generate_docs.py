"""Generate documents from template and JSON data.

This utility performs simple variable substitution using ``string.Template``.
Templates use ``$VARIABLE`` placeholders.

Usage:
    python generate_docs.py template_path data_json output_path
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from string import Template


def render_template(template_path: Path, data_path: Path, output_path: Path) -> None:
    template_text = template_path.read_text()
    data = json.loads(data_path.read_text())
    result = Template(template_text).safe_substitute(data)
    output_path.write_text(result)


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Render a documentation template")
    parser.add_argument("template", type=Path)
    parser.add_argument("data", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render_template(args.template, args.data, args.output)
    print(f"Generated {args.output}")


if __name__ == "__main__":
    _cli()
