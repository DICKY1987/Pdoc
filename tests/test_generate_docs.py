import importlib.util
from pathlib import Path
import json

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "generate_docs.py"
_spec = importlib.util.spec_from_file_location("gen", MODULE_PATH)
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)


def test_render_template(tmp_path):
    template = tmp_path / "t.tpl"
    template.write_text("Hello, $NAME!")
    data = tmp_path / "data.json"
    data.write_text(json.dumps({"NAME": "World"}))
    output = tmp_path / "out.md"
    gen.render_template(template, data, output)
    assert output.read_text() == "Hello, World!"
