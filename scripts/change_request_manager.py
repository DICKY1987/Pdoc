"""Comprehensive change request management utility.

This script tracks change requests in ``change_requests.json`` using JSON.
It supports adding requests, attaching impact analysis, starting review
cycles, and resolving requests. Requests progress through the states:
``open`` → ``in_review`` → ``resolved``.

Usage::

    python change_request_manager.py add TITLE [--description DESC] [--branch BR]
    python change_request_manager.py impact ID "impact description"
    python change_request_manager.py start-review ID reviewer1 reviewer2
    python change_request_manager.py list [--status STATE]
    python change_request_manager.py resolve ID

Stored change request format::

    - id: 1
      title: "..."
      description: "..."
      branch: "feature-branch"
      impact: "..."
      status: "in_review"
      reviewers: ["alice", "bob"]

The storage file uses JSON for portability.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, Iterable, List

import json

DEFAULT_DB = Path(__file__).resolve().parents[1] / "change_requests.json"


def load_requests(db_path: Path = DEFAULT_DB) -> List[Dict[str, Any]]:
    """Load change requests from disk."""
    if db_path.exists():
        data = json.loads(db_path.read_text())
        if isinstance(data, list):
            return data
    return []


def save_requests(requests: List[Dict[str, Any]], db_path: Path = DEFAULT_DB) -> None:
    """Persist change requests to disk."""
    db_path.write_text(json.dumps(requests, indent=2, sort_keys=True))


def add_request(
    title: str,
    description: str = "",
    branch: str | None = None,
    db_path: Path = DEFAULT_DB,
) -> Dict[str, Any]:
    """Add a new change request."""
    requests = load_requests(db_path)
    next_id = 1 + max((r["id"] for r in requests), default=0)
    request = {
        "id": next_id,
        "title": title,
        "description": description,
        "branch": branch,
        "impact": "",
        "status": "open",
        "reviewers": [],
    }
    requests.append(request)
    save_requests(requests, db_path)
    return request


def list_requests(status: str | None = None, db_path: Path = DEFAULT_DB) -> List[Dict[str, Any]]:
    """Return requests filtered by optional status."""
    requests = load_requests(db_path)
    if status:
        requests = [r for r in requests if r["status"] == status]
    return requests


def set_impact(req_id: int, impact: str, db_path: Path = DEFAULT_DB) -> bool:
    """Attach impact analysis to a request."""
    requests = load_requests(db_path)
    for r in requests:
        if r["id"] == req_id:
            r["impact"] = impact
            save_requests(requests, db_path)
            return True
    return False


def start_review(req_id: int, reviewers: Iterable[str], db_path: Path = DEFAULT_DB) -> bool:
    """Move request to ``in_review`` with specified reviewers."""
    requests = load_requests(db_path)
    for r in requests:
        if r["id"] == req_id:
            r["status"] = "in_review"
            r["reviewers"] = list(reviewers)
            save_requests(requests, db_path)
            return True
    return False


def resolve_request(req_id: int, db_path: Path = DEFAULT_DB) -> bool:
    """Mark a request as resolved."""
    requests = load_requests(db_path)
    for r in requests:
        if r["id"] == req_id:
            r["status"] = "resolved"
            save_requests(requests, db_path)
            return True
    return False


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Change request manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    add_p = sub.add_parser("add", help="Add a new change request")
    add_p.add_argument("title")
    add_p.add_argument("--description", default="")
    add_p.add_argument("--branch", default=None)

    list_p = sub.add_parser("list", help="List change requests")
    list_p.add_argument(
        "--status", choices=["open", "in_review", "resolved"], default=None
    )

    impact_p = sub.add_parser("impact", help="Attach impact analysis to a request")
    impact_p.add_argument("id", type=int)
    impact_p.add_argument("impact")

    review_p = sub.add_parser(
        "start-review", help="Begin review cycle for a request"
    )
    review_p.add_argument("id", type=int)
    review_p.add_argument("reviewers", nargs="+")

    res_p = sub.add_parser("resolve", help="Mark a change request as resolved")
    res_p.add_argument("id", type=int)

    args = parser.parse_args()

    if args.cmd == "add":
        req = add_request(args.title, args.description, args.branch)
        print(f"Added change request #{req['id']}")
    elif args.cmd == "list":
        for r in list_requests(args.status):
            branch = f" ({r['branch']})" if r.get("branch") else ""
            print(f"[{r['status']}] {r['id']}{branch}: {r['title']}")
    elif args.cmd == "impact":
        if set_impact(args.id, args.impact):
            print(f"Recorded impact for change request #{args.id}")
        else:
            print(f"Change request #{args.id} not found")
    elif args.cmd == "start-review":
        if start_review(args.id, args.reviewers):
            print(f"Started review for change request #{args.id}")
        else:
            print(f"Change request #{args.id} not found")
    elif args.cmd == "resolve":
        if resolve_request(args.id):
            print(f"Resolved change request #{args.id}")
        else:
            print(f"Change request #{args.id} not found")


if __name__ == "__main__":
    _cli()

