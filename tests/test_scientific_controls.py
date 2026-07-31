import json
import math
from pathlib import Path

import httpx
import pytest
import yaml

from embodied_llm.config import (
    CouplingBlock,
    ExperimentConfig,
    MemoryConfig,
    ModelConfig,
    OwnershipBlock,
)
from embodied_llm.coupling import CouplingController
from embodied_llm.memory import MemorySystem
from embodied_llm.models import OpenAICompatibleModel
from embodied_llm.ownership import OwnershipPairRunner
from embodied_llm.suite import SuiteRunner


def test_yoked_random_control_preserves_action_distribution():
    controller = CouplingController(action_dim=8, seed=5)
    proposed = [0.9, -0.7, 0.4, -0.2, 0.1, 0.0, 0.6, -0.3]
    applied, debug = controller.apply(proposed, CouplingBlock(0, 10, mode="random"))
    assert sorted(abs(value) for value in applied) == sorted(abs(value) for value in proposed)
    assert math.isclose(
        math.sqrt(sum(value * value for value in applied)),
        math.sqrt(sum(value * value for value in proposed)),
    )
    assert debug["detail"] == "signed_permutation_yoked_to_current_action"


def test_delay_buffer_is_cleared_at_block_boundary():
    controller = CouplingController(action_dim=8, seed=5)
    first = CouplingBlock(0, 2, mode="delayed")
    second = CouplingBlock(2, 4, mode="delayed")
    assert controller.apply([0.5] * 8, first)[0] == [0.0] * 8
    assert controller.apply([0.2] * 8, first)[0] == [0.5] * 8
    assert controller.apply([-0.8] * 8, second)[0] == [0.0] * 8


def test_archive_retrieval_returns_prior_sensation_not_only_expression():
    memory = MemorySystem(MemoryConfig(mode="full", peek_items=2, retrieval_items=2))
    memory.add(4, "I tried a small variation.", "CURRENT_SENSATION t=5\nq07 = +0.812")
    results = memory.retrieve("q07")
    assert results and results[0].tick == 4
    text = memory.peek_text()
    assert "ensuing sensation" in text
    assert "q07 = +0.812" in text


def test_overlapping_blocks_are_rejected():
    config = ExperimentConfig(ticks=10)
    config.coupling = [
        CouplingBlock(0, 7, mode="coupled"),
        CouplingBlock(6, 10, mode="disconnected"),
    ]
    with pytest.raises(ValueError, match="overlapping coupling"):
        config.validate()


def test_ownership_ties_receive_half_credit(tmp_path: Path):
    config = ExperimentConfig(paradigm="ownership_pair", ticks=2, output_dir=str(tmp_path))
    config.ownership.randomize_field_labels = False
    config.ownership.blocks = [OwnershipBlock(0, 1, "A"), OwnershipBlock(1, 2, "B")]
    runner = OwnershipPairRunner(config)
    runner.events = [{"tick": 0}, {"tick": 1}]
    runner.probes = [
        {"tick": 0, "parsed": {"p_field_a_is_mine": 0.5}, "truth": {"p_field_a_is_mine": 1.0, "owner": "A"}},
        {"tick": 1, "parsed": {"p_field_a_is_mine": 0.5}, "truth": {"p_field_a_is_mine": 0.0, "owner": "B"}},
    ]
    summary = runner._summary()
    assert summary["ownership_accuracy_ties_half_credit"] == 0.5
    assert summary["ownership_field_a_bias"] == 0.0


def test_model_seed_is_sent_to_openai_compatible_endpoint():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    config = ModelConfig(
        provider="openai_compatible",
        model="test",
        endpoint="http://model.test/v1/chat/completions",
        seed=1234,
    )
    model = OpenAICompatibleModel(config)
    model.client.close()
    model.client = httpx.Client(transport=httpx.MockTransport(handler))
    assert model.generate([{"role": "user", "content": "x"}]) == "ok"
    assert captured["seed"] == 1234


def test_suite_replicates_and_builds_paired_contrasts(tmp_path: Path):
    conditions = []
    for name, mode in (("coupled", "coupled"), ("disconnected", "disconnected")):
        path = tmp_path / f"{name}.yaml"
        path.write_text(
            yaml.safe_dump(
                {
                    "name": name,
                    "ticks": 2,
                    "output_dir": str(tmp_path / "runs"),
                    "model": {"provider": "mock"},
                    "probes": {"enabled": False},
                    "coupling": [{"start": 0, "end": 2, "mode": mode}],
                }
            ),
            encoding="utf-8",
        )
        conditions.append({"name": name, "config_path": path.name})
    suite_path = tmp_path / "suite.yaml"
    suite_path.write_text(
        yaml.safe_dump(
            {
                "name": "paired",
                "seeds": [3],
                "replicates": 2,
                "output_dir": str(tmp_path / "suite-runs"),
                "conditions": conditions,
            }
        ),
        encoding="utf-8",
    )
    output = SuiteRunner(suite_path).run()
    records = json.loads((output / "records.json").read_text(encoding="utf-8"))
    aggregate = json.loads((output / "aggregate.json").read_text(encoding="utf-8"))
    assert len(records) == 4
    assert aggregate["paired_contrasts"]["coupled-minus-disconnected"]["matched_runs"] == 2


def test_external_event_packet_replays_identically_across_worlds():
    import random

    from embodied_llm.config import WorldConfig
    from embodied_llm.world import ExternalEventPacket, WorldModel

    config = WorldConfig(autonomous=True, event_probability=1.0)
    world_a = WorldModel(config, random.Random(91))
    world_b = WorldModel(config, random.Random(91))
    packet = ExternalEventPacket(kind="ambient_shift", ambient_delta=0.31)
    diag_a = world_a.step((0.2, -0.1), 0.0, external_event=packet)
    diag_b = world_b.step((0.2, -0.1), 0.0, external_event=packet)
    assert diag_a.external_event_packet == diag_b.external_event_packet
    assert world_a.state.to_dict() == world_b.state.to_dict()
