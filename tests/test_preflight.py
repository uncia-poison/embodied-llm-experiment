from pathlib import Path

import pytest

from embodied_llm.config import ExperimentConfig
from embodied_llm.experiment import ExperimentRunner
from embodied_llm.preflight import run_preflight


def test_mock_preflight_passes(tmp_path: Path):
    config = ExperimentConfig(output_dir=str(tmp_path))
    report = run_preflight(config)
    assert report["ok"] is True
    assert all(item["ok"] for item in report["checks"] if item["required"])


def test_runner_writes_failure_record(tmp_path: Path):
    class BrokenModel:
        def generate(self, messages, *, temperature=None, max_tokens=None):
            raise RuntimeError("provider broke")

        def reset_context(self):
            return None

    config = ExperimentConfig(ticks=2, output_dir=str(tmp_path))
    runner = ExperimentRunner(config, model=BrokenModel())
    with pytest.raises(RuntimeError, match="provider broke"):
        runner.run()
    failure = runner.logger.run_dir / "failure.json"
    assert failure.exists()
    assert "provider broke" in failure.read_text(encoding="utf-8")
