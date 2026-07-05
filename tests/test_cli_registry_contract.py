import json
from pathlib import Path

from asperitas_agent.cli import main


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PATH = ROOT / "02_SOURCE_REGISTRY" / "source_registry.example.json"


def test_validate_registry_contract_cli_passes_for_example(capsys) -> None:
    exit_code = main(["validate-registry-contract", "--path", str(EXAMPLE_PATH)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["errors"] == []
    assert payload["registry_contract"] == EXAMPLE_PATH.as_posix()


def test_validate_registry_contract_cli_fails_for_missing_file(tmp_path, capsys) -> None:
    missing_path = tmp_path / "missing.json"

    exit_code = main(["validate-registry-contract", "--path", str(missing_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 1
    assert payload["ok"] is False
    assert payload["registry_contract"] == missing_path.as_posix()
    assert payload["errors"]
