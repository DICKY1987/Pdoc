import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "change_request_manager.py"
_spec = importlib.util.spec_from_file_location("crm", MODULE_PATH)
crm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(crm)


def test_full_workflow(tmp_path):
    db = tmp_path / "cr.json"
    req = crm.add_request("CR1", description="desc", branch="feature", db_path=db)
    crm.set_impact(req["id"], "affects docs", db_path=db)
    crm.start_review(req["id"], ["alice", "bob"], db_path=db)
    in_review = crm.list_requests(status="in_review", db_path=db)[0]
    assert in_review["reviewers"] == ["alice", "bob"]
    assert crm.resolve_request(req["id"], db_path=db)
    assert crm.list_requests(status="resolved", db_path=db)[0]["id"] == req["id"]
