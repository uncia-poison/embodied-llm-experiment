from pathlib import Path

from embodied_llm.config import CouplingBlock, ExperimentConfig
from embodied_llm.experiment import ExperimentRunner


def test_delayed_current_expression_truth_is_zero(tmp_path: Path):
    config = ExperimentConfig(ticks=4, output_dir=str(tmp_path))
    config.coupling = [CouplingBlock(0, 4, mode="delayed")]
    config.probes.warmup_ticks = 0
    config.probes.agency_every = 1
    config.probes.prediction_every = 0
    runner = ExperimentRunner(config)
    runner.run()
    agency = [probe for probe in runner.probes if probe["kind"] == "agency"]
    assert agency
    assert all(probe["truth"]["self_fraction"] == 0.0 for probe in agency)
    assert any(event["causal"]["self_fraction"] > 0.0 for event in runner.events[1:])


def test_context_reset_removes_short_history_but_keeps_run_alive(tmp_path: Path):
    config = ExperimentConfig(ticks=6, output_dir=str(tmp_path))
    config.probes.enabled = False
    config.coupling = [
        CouplingBlock(0, 3, mode="coupled"),
        CouplingBlock(3, 6, mode="coupled", reset_context_at_start=True),
    ]
    runner = ExperimentRunner(config)
    runner.run()
    assert len(runner.events[2]["model_input"]) > 2
    assert len(runner.events[3]["model_input"]) == 2
