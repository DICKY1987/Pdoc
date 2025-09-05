import importlib.util
from pathlib import Path
import sys
import textwrap

import pytest

LINT_PATH = Path(__file__).resolve().parents[1] / "pdoc" / "huey_doc_lint.py"
_spec = importlib.util.spec_from_file_location("huey_doc_lint", LINT_PATH)
lint_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lint_module)


@pytest.fixture
def valid_spec(tmp_path):
    content = textwrap.dedent(
        """
        file_seq: 1
        created_at_utc: 2025-09-05T21:17:35Z
        checksum_sha256: dummy

        <!-- BEGIN:HUEY.001.002.003.DEF.sample -->
        reference to @HUEY.001.002
        <!-- END:HUEY.001.002.003.DEF.sample -->
        """
    ).strip()
    path = tmp_path / "valid.md"
    path.write_text(content)
    return path


@pytest.fixture
def invalid_spec(tmp_path):
    content = textwrap.dedent(
        """
        file_seq: 1
        created_at_utc: 2025-09-05T21:17:35Z

        <!-- BEGIN:HUEY.001.002.003.DEF.sample -->
        reference to @HUEY.001.002
        <!-- END:HUEY.001.002.999.DEF.sample -->
        """
    ).strip()
    path = tmp_path / "invalid.md"
    path.write_text(content)
    return path


def test_valid_spec_passes(valid_spec, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["prog", str(valid_spec)])
    lint_module.main()
    captured = capsys.readouterr()
    assert "OK: Lint passed" in captured.out


def test_invalid_spec_fails(invalid_spec, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["prog", str(invalid_spec)])
    with pytest.raises(SystemExit) as excinfo:
        lint_module.main()
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "END id mismatch" in captured.out
    assert "Missing required CSV meta field in doc: checksum_sha256" in captured.out
