#!/usr/bin/env python3
"""Validate document cross-references defined in config/cross_refs.yml."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
import json


class CrossReferenceValidator:
    """Check that referenced sections and shared definitions exist."""

    def __init__(self, cross_ref_file: Path | str, doc_directory: Path | str) -> None:
        self.cross_refs = json.loads(Path(cross_ref_file).read_text())
        self.doc_dir = Path(doc_directory)

    def validate_references(self) -> list[str]:
        errors: list[str] = []
        for category, items in self.cross_refs.items():
            for item_name, refs in items.items():
                for doc_type in ["huey_p_section", "backend_section"]:
                    if doc_type in refs:
                        section = refs[doc_type]
                        if not self.section_exists(doc_type, section):
                            errors.append(
                                f"Missing section {section} in {doc_type} for {item_name}"
                            )
                if "shared_definition" in refs:
                    shared_file = self.doc_dir / refs["shared_definition"]
                    if not shared_file.exists():
                        errors.append(
                            f"Missing shared definition: {shared_file} for {item_name}"
                        )
        return errors

    def section_exists(self, doc_type: str, section: str) -> bool:
        doc_map = {
            "huey_p_section": "docs/huey_p_unified_gui_signals_spec.md",
            "backend_section": "docs/integrated_economic_calendar_matrix_re_entry_system_spec.md",
        }
        doc_file = self.doc_dir / doc_map[doc_type]
        if not doc_file.exists():
            return False
        content = doc_file.read_text()
        pattern = rf"^#+\s*{re.escape(section)}\b"
        return re.search(pattern, content, re.MULTILINE) is not None


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate document cross-references")
    parser.add_argument(
        "--cross-ref",
        default="config/cross_refs.yml",
        help="Path to cross reference YAML file",
    )
    parser.add_argument(
        "--doc-dir", default=".", help="Directory containing documentation files"
    )
    args = parser.parse_args()

    validator = CrossReferenceValidator(args.cross_ref, args.doc_dir)
    errors = validator.validate_references()
    if errors:
        for err in errors:
            print(err)
        raise SystemExit(1)
    print("All cross-references valid")


if __name__ == "__main__":
    main()
