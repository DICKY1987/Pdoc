import importlib.util
from pathlib import Path
import json

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_change_requests.py"
_spec = importlib.util.spec_from_file_location("vcr", MODULE_PATH)
vcr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vcr)


def test_validate_change_requests(tmp_path):
    valid = [
        {
            "id": 1,
            "title": "a",
            "description": "b",
            "branch": "feat",
            "impact": "impact",
            "status": "open",
            "reviewers": [],
        }
    ]
    db = tmp_path / "cr.json"
    db.write_text(json.dumps(valid))
    assert vcr.validate(db) == []

    invalid = [
        {"id": 2, "title": "b", "description": "c", "status": "open", "reviewers": []}
    ]
    db2 = tmp_path / "bad.json"
    db2.write_text(json.dumps(invalid))
    errors = vcr.validate(db2)
    assert errors and "missing impact" in errors[0]

