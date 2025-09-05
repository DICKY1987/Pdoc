import importlib.util
from pathlib import Path

import json

VALIDATOR_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_cross_refs.py"
_spec = importlib.util.spec_from_file_location("validate_cross_refs", VALIDATOR_PATH)
validator_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator_module)


def test_cross_refs_valid():
    validator = validator_module.CrossReferenceValidator("cross_refs.yml", Path(__file__).resolve().parents[1])
    assert validator.validate_references() == []


def test_cross_refs_missing_shared(tmp_path):
    data = json.loads(Path("cross_refs.yml").read_text())
    data["identifier_systems"]["cal8_format"]["shared_definition"] = "schemas/missing.md"
    temp = tmp_path / "cross_refs.yml"
    temp.write_text(json.dumps(data))
    validator = validator_module.CrossReferenceValidator(temp, Path(__file__).resolve().parents[1])
    errors = validator.validate_references()
    assert any("Missing shared definition" in e for e in errors)
