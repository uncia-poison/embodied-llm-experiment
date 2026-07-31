from pathlib import Path

import yaml

from embodied_llm.suite import SuiteRunner


def test_suite_runs(tmp_path: Path):
    single = tmp_path / "single.yaml"
    single.write_text(
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
                "name": "test-suite",
                "seeds": [1],
                "output_dir": str(tmp_path / "suite-runs"),
                "conditions": [{"name": "single", "config_path": "single.yaml"}],
            }
        ),
        encoding="utf-8",
    )
    output = SuiteRunner(suite).run()
    assert (output / "aggregate.json").exists()
