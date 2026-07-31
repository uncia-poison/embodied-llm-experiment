from pathlib import Path

from embodied_llm.config import ExperimentConfig
from embodied_llm.experiment import ExperimentRunner


def test_end_to_end_mock_run(tmp_path: Path):
    config = ExperimentConfig(ticks=12, output_dir=str(tmp_path))
    config.probes.warmup_ticks = 2
    config.probes.agency_every = 3
    config.probes.prediction_every = 3
    run_dir = ExperimentRunner(config).run()
    assert (run_dir / "manifest.json").exists()
    assert (run_dir / "events.jsonl").exists()
    assert (run_dir / "summary.json").exists()
    assert len((run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()) == 12
