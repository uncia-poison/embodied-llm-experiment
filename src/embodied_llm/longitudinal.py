from __future__ import annotations

import copy
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

from .checkpoint import (
    MemoryVariant,
    apply_memory_variant,
    read_checkpoint,
    validate_checkpoint,
)
from .config import ExperimentConfig
from .experiment import ExperimentRunner
from .models import LanguageModel

ModelFactory = Callable[[ExperimentConfig], LanguageModel]

DEFAULT_VARIANTS: tuple[MemoryVariant, ...] = (
    "full",
    "empty",
    "shuffled",
    "core_only",
    "archive_only",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _summary(run_dir: Path) -> dict[str, Any]:
    return json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))


def inspect_checkpoint(path: str | Path) -> dict[str, Any]:
    checkpoint = read_checkpoint(path)
    state = checkpoint.get("state", {})
    memory = state.get("memory", {})
    return {
        "path": str(path),
        "checkpoint_sha256": checkpoint["checkpoint_sha256"],
        "lineage_id": checkpoint.get("lineage_id"),
        "phase": checkpoint.get("phase"),
        "age_ticks": state.get("age_ticks"),
        "core_chars": len(str(memory.get("core", ""))),
        "archive_items": len(memory.get("archive", [])),
        "working_items": len(memory.get("recent_utterances", [])),
        "parent_checkpoint_sha256": checkpoint.get("parent_checkpoint_sha256"),
        "source_checkpoint_sha256": checkpoint.get("source_checkpoint_sha256"),
        "evaluation_memory_variant": checkpoint.get("evaluation_memory_variant"),
    }


def run_discovery(
    config_path: str | Path,
    *,
    checkpoint_out: str | Path,
    checkpoint_in: str | Path | None = None,
    checkpoint_every: int = 1,
    fresh_context: bool = False,
    model_factory: ModelFactory | None = None,
) -> dict[str, Any]:
    config = ExperimentConfig.from_yaml(config_path)
    if config.paradigm != "single_body":
        raise ValueError("longitudinal discovery currently supports single_body only")
    if config.probes.enabled:
        raise ValueError(
            "discovery configuration must set probes.enabled: false to avoid tutoring the model"
        )

    checkpoint = read_checkpoint(checkpoint_in) if checkpoint_in is not None else None
    model = model_factory(config) if model_factory is not None else None
    runner = ExperimentRunner(
        config,
        model=model,
        checkpoint=checkpoint,
        checkpoint_out=checkpoint_out,
        checkpoint_every=checkpoint_every,
        phase="discovery",
        fresh_context=fresh_context,
    )
    run_dir = runner.run()
    result = {
        "schema_version": 1,
        "phase": "discovery",
        "run_dir": str(run_dir),
        "checkpoint": inspect_checkpoint(checkpoint_out),
        "summary": _summary(run_dir),
    }
    _atomic_json(run_dir / "longitudinal-result.json", result)
    return result


def _normalise_variants(values: Iterable[str]) -> list[MemoryVariant]:
    variants: list[MemoryVariant] = []
    allowed = {"full", "empty", "shuffled", "core_only", "archive_only", "unrelated"}
    for value in values:
        item = value.strip().lower()
        if not item:
            continue
        if item not in allowed:
            raise ValueError(f"unsupported evaluation memory variant: {item}")
        if item not in variants:
            variants.append(item)  # type: ignore[arg-type]
    if not variants:
        raise ValueError("evaluation requires at least one memory variant")
    return variants


def run_evaluation(
    config_path: str | Path,
    *,
    checkpoint_path: str | Path,
    output_dir: str | Path,
    variants: Iterable[str] = DEFAULT_VARIANTS,
    unrelated_checkpoint_path: str | Path | None = None,
    shuffle_seed: int = 1701,
    continue_on_error: bool = True,
    model_factory: ModelFactory | None = None,
) -> dict[str, Any]:
    config = ExperimentConfig.from_yaml(config_path)
    if config.paradigm != "single_body":
        raise ValueError("longitudinal evaluation currently supports single_body only")
    if not config.probes.enabled:
        raise ValueError("evaluation configuration must enable probes")

    source = read_checkpoint(checkpoint_path)
    validate_checkpoint(config, source)
    selected = _normalise_variants(variants)
    unrelated = (
        read_checkpoint(unrelated_checkpoint_path)
        if unrelated_checkpoint_path is not None
        else None
    )
    if "unrelated" in selected:
        if unrelated is None:
            raise ValueError("unrelated variant requires --unrelated-checkpoint")
        validate_checkpoint(config, unrelated)
        if unrelated.get("lineage_id") == source.get("lineage_id"):
            raise ValueError("unrelated checkpoint must come from a different lineage")

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "phase": "evaluation",
        "created_at": _utc_now(),
        "source_checkpoint": inspect_checkpoint(checkpoint_path),
        "unrelated_checkpoint": (
            inspect_checkpoint(unrelated_checkpoint_path)
            if unrelated_checkpoint_path is not None
            else None
        ),
        "config": str(config_path),
        "variants": selected,
        "shuffle_seed": int(shuffle_seed),
        "fresh_model_context_per_variant": True,
        "working_memory_cleared_per_variant": True,
        "same_frozen_body_world_rng_state": True,
    }
    _atomic_json(root / "evaluation-manifest.json", manifest)

    records: list[dict[str, Any]] = []
    for variant in selected:
        branch = apply_memory_variant(
            source,
            variant,
            shuffle_seed=shuffle_seed,
            unrelated_checkpoint=unrelated,
            fresh_context=True,
        )
        branch_path = root / "frozen-branches" / f"{variant}.checkpoint.json"
        _atomic_json(branch_path, branch)

        variant_config = copy.deepcopy(config)
        variant_config.name = f"{config.name}-memory-{variant}"
        variant_config.output_dir = str(root / "runs")
        started = _utc_now()
        try:
            model = model_factory(variant_config) if model_factory is not None else None
            runner = ExperimentRunner(
                variant_config,
                model=model,
                checkpoint=branch,
                phase=f"evaluation:{variant}",
                fresh_context=True,
            )
            run_dir = runner.run()
            record = {
                "variant": variant,
                "status": "success",
                "started_at": started,
                "completed_at": _utc_now(),
                "run_dir": str(run_dir),
                "branch_checkpoint": str(branch_path),
                "branch_checkpoint_sha256": branch["checkpoint_sha256"],
                "summary": _summary(run_dir),
            }
        except Exception as exc:
            record = {
                "variant": variant,
                "status": "failed",
                "started_at": started,
                "completed_at": _utc_now(),
                "branch_checkpoint": str(branch_path),
                "branch_checkpoint_sha256": branch["checkpoint_sha256"],
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
            records.append(record)
            _atomic_json(root / "evaluation-records.json", {"records": records})
            if not continue_on_error:
                raise
            continue
        records.append(record)
        _atomic_json(root / "evaluation-records.json", {"records": records})

    result = {
        "schema_version": 1,
        "phase": "evaluation",
        "source_checkpoint_sha256": source["checkpoint_sha256"],
        "source_lineage_id": source.get("lineage_id"),
        "successful_variants": sum(item["status"] == "success" for item in records),
        "failed_variants": sum(item["status"] == "failed" for item in records),
        "records": records,
    }
    _atomic_json(root / "evaluation-result.json", result)
    return result
