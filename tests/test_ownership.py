from pathlib import Path

from embodied_llm.config import ExperimentConfig
from embodied_llm.ownership import OwnershipPairRunner


def test_ownership_pair_runs(tmp_path: Path):
    config = ExperimentConfig.from_yaml("configs/suites/ownership-pair.yaml")
    config.ticks = 12
    config.output_dir = str(tmp_path)
    config.ownership.blocks = []
    config.ownership.probe_warmup_ticks = 2
    config.ownership.probe_every = 3
    run_dir = OwnershipPairRunner(config).run()
    assert (run_dir / "events.jsonl").exists()
    assert len((run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()) == 12
