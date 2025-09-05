import importlib.util
from pathlib import Path
import json

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "generate_enum_docs.py"
_spec = importlib.util.spec_from_file_location("ged", MODULE_PATH)
ged = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ged)


def test_enum_doc_generation(tmp_path):
    data = {
        "colors": [
            {"name": "RED", "description": "Red color"},
            {"name": "BLUE", "description": "Blue color"},
        ]
    }
    schema = tmp_path / "enums.json"
    schema.write_text(json.dumps(data))
    out = tmp_path / "out.md"
    ged.generate(schema, out)
    text = out.read_text()
    assert "# Colors" in text
    assert "RED" in text and "BLUE" in text

