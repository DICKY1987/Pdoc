"""Validate change requests for required metadata.

This script ensures that all change requests in ``change_requests.json``
contain the fields needed for automation. Requests that are not yet resolved
must include an ``impact`` description and a tracking ``branch``. Requests in
``in_review`` state must also list ``reviewers``.

Running the module as a script prints any validation errors and exits with a
non-zero status if problems are found.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import json

DEFAULT_DB = Path(__file__).resolve().parents[1] / "change_requests.json"


def load_requests(db_path: Path = DEFAULT_DB) -> List[Dict[str, Any]]:
    if db_path.exists():
        data = json.loads(db_path.read_text())
        if isinstance(data, list):
            return data
    return []


def validate(db_path: Path = DEFAULT_DB) -> List[str]:
    """Return a list of validation error messages."""
    errors: List[str] = []
    for req in load_requests(db_path):
        if req.get("status") != "resolved":
            if not req.get("impact"):
                errors.append(f"Request {req['id']} missing impact analysis")
            if not req.get("branch"):
                errors.append(f"Request {req['id']} missing tracking branch")
        if req.get("status") == "in_review" and not req.get("reviewers"):
            errors.append(f"Request {req['id']} missing reviewers")
    return errors


def _cli() -> None:
    errors = validate()
    if errors:
        for e in errors:
            print(e)
        raise SystemExit(1)
    print("All change requests valid.")


if __name__ == "__main__":
    _cli()

