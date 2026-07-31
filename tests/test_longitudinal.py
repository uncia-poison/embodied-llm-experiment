from __future__ import annotations

import json
from pathlib import Path

import pytest

from embodied_llm.checkpoint import (
    apply_memory_variant,
    read_checkpoint,
    write_checkpoint,
)
from embodied_llm.config import ExperimentConfig, ModelConfig, ProbeConfig
from embodied_llm.experiment import ExperimentRunner
from embodied_llm.longitudinal import run_evaluation


class ConstantModel:
    def generate(self, messages, *, temperature=None, max_tokens=None) -> str:
        return json.dumps(
            {
                "utterance": "I move forward slightly and compare the stream.",
                "core_memory_write": "Forward language repeatedly changes a stable channel subset.",
                "memory_query": None,
            }
        )

    def reset_context(self) -> None:
        return None


def _config(tmp_path: Path, *, ticks: int, probes: bool, name: str) -> ExperimentConfig:
    return ExperimentConfig(
        name=name,
        seed=41,
        ticks=ticks,
        output_dir=str(tmp_path / "runs"),
        model=ModelConfig(provider="mock", model="mock-explorer"),
        probes=ProbeConfig(
            enabled=probes,
            warmup_ticks=0,
            agency_every=1,
            prediction_every=1,
            max_probe_tokens=250,
        ),
    )


def test_checkpoint_checksum_rejects_tampering(tmp_path: Path):
    config = _config(tmp_path, ticks=2, probes=False, name="sealed")
    checkpoint_path = tmp_path / "sealed.checkpoint.json"
    ExperimentRunner(
        config,
        model=ConstantModel(),
        checkpoint_out=checkpoint_path,
    ).run()

    payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    payload["state"]["age_ticks"] = 999
    checkpoint_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="checksum mismatch"):
        read_checkpoint(checkpoint_path)


def test_split_chapters_preserve_physical_memory_and_rng_continuity(tmp_path: Path):
    continuous_path = tmp_path / "continuous.checkpoint.json"
    continuous = _config(tmp_path / "continuous", ticks=8, probes=False, name="continuous")
    ExperimentRunner(
        continuous,
        model=ConstantModel(),
        checkpoint_out=continuous_path,
    ).run()

    chapter_path = tmp_path / "chapter.checkpoint.json"
    first = _config(tmp_path / "split-a", ticks=4, probes=False, name="chapter-a")
    ExperimentRunner(
        first,
        model=ConstantModel(),
        checkpoint_out=chapter_path,
    ).run()
    source = read_checkpoint(chapter_path)
    assert source["state"]["age_ticks"] == 4

    second = _config(tmp_path / "split-b", ticks=4, probes=False, name="chapter-b")
    ExperimentRunner(
        second,
        model=ConstantModel(),
        checkpoint=source,
        checkpoint_out=chapter_path,
    ).run()

    whole = read_checkpoint(continuous_path)["state"]
    split = read_checkpoint(chapter_path)["state"]
    assert split["age_ticks"] == whole["age_ticks"] == 8
    for key in (
        "body_state",
        "world_state",
        "rng_state",
        "sensorium_state",
        "drive_state",
        "memory",
        "history",
        "current_frame",
        "last_remap_seed",
    ):
        assert split[key] == whole[key]
    assert [item["tick"] for item in split["memory"]["archive"]] == list(range(8))
    assert split["coupling_state"]["rng_state"] == whole["coupling_state"]["rng_state"]
    assert split["coupling_state"]["delay_buffer"] == whole["coupling_state"]["delay_buffer"]


def test_memory_variants_are_frozen_independent_branches(tmp_path: Path):
    config = _config(tmp_path, ticks=6, probes=False, name="source")
    checkpoint_path = tmp_path / "source.checkpoint.json"
    ExperimentRunner(
        config,
        model=ConstantModel(),
        checkpoint_out=checkpoint_path,
    ).run()
    source = read_checkpoint(checkpoint_path)
    source_sha = source["checkpoint_sha256"]
    archive = source["state"]["memory"]["archive"]
    assert len(archive) == 6
    assert source["state"]["memory"]["core"]

    empty = apply_memory_variant(source, "empty")
    assert empty["state"]["memory"]["core"] == ""
    assert empty["state"]["memory"]["archive"] == []

    core_only = apply_memory_variant(source, "core_only")
    assert core_only["state"]["memory"]["core"]
    assert core_only["state"]["memory"]["archive"] == []

    archive_only = apply_memory_variant(source, "archive_only")
    assert archive_only["state"]["memory"]["core"] == ""
    assert len(archive_only["state"]["memory"]["archive"]) == 6

    shuffled = apply_memory_variant(source, "shuffled", shuffle_seed=9)
    assert [
        item["utterance"] for item in shuffled["state"]["memory"]["archive"]
    ] == [item["utterance"] for item in archive]
    assert shuffled["state"]["history"] == []
    assert source["checkpoint_sha256"] == source_sha
    assert read_checkpoint(checkpoint_path)["checkpoint_sha256"] == source_sha


def test_evaluation_runs_matched_variants_from_one_frozen_state(tmp_path: Path):
    discovery = _config(tmp_path / "discovery", ticks=6, probes=False, name="discovery")
    checkpoint_path = tmp_path / "frozen.checkpoint.json"
    ExperimentRunner(
        discovery,
        model=ConstantModel(),
        checkpoint_out=checkpoint_path,
        phase="discovery",
    ).run()
    frozen_sha = read_checkpoint(checkpoint_path)["checkpoint_sha256"]

    evaluation = _config(tmp_path / "evaluation", ticks=2, probes=True, name="evaluation")
    config_path = tmp_path / "evaluation.yaml"
    config_path.write_text(
        "\n".join(
            [
                "name: evaluation",
                "seed: 41",
                "ticks: 2",
                f"output_dir: {tmp_path / 'unused'}",
                "model:",
                "  provider: mock",
                "  model: mock-explorer",
                "probes:",
                "  enabled: true",
                "  warmup_ticks: 0",
                "  agency_every: 1",
                "  prediction_every: 1",
                "  max_probe_tokens: 250",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    assert evaluation.probes.enabled

    result = run_evaluation(
        config_path,
        checkpoint_path=checkpoint_path,
        output_dir=tmp_path / "evaluation-output",
        variants=["full", "empty", "shuffled", "core_only", "archive_only"],
    )
    assert result["successful_variants"] == 5
    assert result["failed_variants"] == 0
    assert {item["variant"] for item in result["records"]} == {
        "full",
        "empty",
        "shuffled",
        "core_only",
        "archive_only",
    }
    assert read_checkpoint(checkpoint_path)["checkpoint_sha256"] == frozen_sha
    for record in result["records"]:
        manifest = json.loads(
            (Path(record["run_dir"]) / "manifest.json").read_text(encoding="utf-8")
        )
        assert manifest["starting_age_ticks"] == 6
        assert manifest["source_checkpoint_sha256"] == record["branch_checkpoint_sha256"]
