import json
from pathlib import Path

import yaml

from embodied_llm.blinding import create_blind_package
from embodied_llm.suite import SuiteRunner


def test_blind_package_separates_condition_codebook(tmp_path: Path):
    config = tmp_path / "single.yaml"
    config.write_text(
        yaml.safe_dump(
            {
                "name": "single",
                "ticks": 3,
                "output_dir": str(tmp_path / "runs"),
                "model": {"provider": "mock"},
                "probes": {"enabled": False},
            }
        ),
        encoding="utf-8",
    )
    suite = tmp_path / "suite.yaml"
    suite.write_text(
        yaml.safe_dump(
            {
                "name": "blind-suite",
                "seeds": [7],
                "output_dir": str(tmp_path / "suite-runs"),
                "conditions": [{"name": "secret-condition", "config_path": "single.yaml"}],
            }
        ),
        encoding="utf-8",
    )
    output = SuiteRunner(suite).run()
    blind = create_blind_package(output)

    visible = "\n".join(
        path.read_text(encoding="utf-8")
        for path in blind.rglob("*")
        if path.is_file()
    )
    assert "secret-condition" not in visible
    assert "researcher_only" not in visible
    assert "applied_action" not in visible

    codebook = json.loads((output / "blind-codebook.json").read_text(encoding="utf-8"))
    assert codebook["runs"][0]["condition"] == "secret-condition"
    assert (blind / "B0001" / "events.jsonl").exists()
