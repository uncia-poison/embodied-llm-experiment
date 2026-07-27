import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from embodied_llm.suite import SuiteRunner


def _write_suite(tmp_path: Path, *, name: str = "resilient-suite") -> Path:
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
                "name": name,
                "seeds": [1],
                "output_dir": str(tmp_path / "suite-runs"),
                "conditions": [{"name": "single", "config_path": "single.yaml"}],
            }
        ),
        encoding="utf-8",
    )
    return suite


def test_suite_plan_reports_exact_mock_budget(tmp_path: Path):
    runner = SuiteRunner(_write_suite(tmp_path))
    plan = runner.plan()
    assert plan["total_runs"] == 1
    assert plan["estimated_model_calls"] == 3
    assert plan["runs"][0]["estimate"]["probe_calls"] == 0


def test_suite_resume_skips_successful_cells(tmp_path: Path):
    suite = _write_suite(tmp_path)
    output = SuiteRunner(suite).run()
    first_run_dirs = sorted((output / "runs").iterdir())
    assert len(first_run_dirs) == 1

    SuiteRunner(suite).run()
    second_run_dirs = sorted((output / "runs").iterdir())
    assert second_run_dirs == first_run_dirs

    records = json.loads((output / "records.json").read_text(encoding="utf-8"))
    assert records["records"][0]["status"] == "success"
    assert len((output / "attempts.jsonl").read_text(encoding="utf-8").splitlines()) == 1


def test_suite_persists_failure_and_continues(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    suite = _write_suite(tmp_path, name="failure-suite")

    class FailingRunner:
        def __init__(self, config):
            run_dir = Path(config.output_dir) / "failed-cell"
            run_dir.mkdir(parents=True, exist_ok=True)
            self.logger = SimpleNamespace(run_dir=run_dir)

        def run(self):
            raise RuntimeError("synthetic endpoint failure")

    monkeypatch.setattr("embodied_llm.suite.ExperimentRunner", FailingRunner)
    output = SuiteRunner(suite, continue_on_error=True).run()
    progress = json.loads((output / "progress.json").read_text(encoding="utf-8"))
    records = json.loads((output / "records.json").read_text(encoding="utf-8"))

    assert progress["status"] == "completed_with_failures"
    assert progress["failed_runs"] == 1
    assert records["records"][0]["error_type"] == "RuntimeError"
    assert "synthetic endpoint failure" in records["records"][0]["error"]


def test_suite_rejects_protocol_change_inside_existing_output(tmp_path: Path):
    suite = _write_suite(tmp_path, name="fingerprint-suite")
    SuiteRunner(suite).run()
    config = tmp_path / "single.yaml"
    raw = yaml.safe_load(config.read_text(encoding="utf-8"))
    raw["ticks"] = 4
    config.write_text(yaml.safe_dump(raw), encoding="utf-8")

    with pytest.raises(RuntimeError, match="changed"):
        SuiteRunner(suite).run()
