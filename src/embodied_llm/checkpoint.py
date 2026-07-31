from __future__ import annotations

import copy
import hashlib
import json
import random
import re
from pathlib import Path
from typing import Any, Literal

from .config import ExperimentConfig

MemoryVariant = Literal[
    "full",
    "empty",
    "shuffled",
    "core_only",
    "archive_only",
    "unrelated",
]

_TOKEN_RE = re.compile(r"[\w'-]+", re.UNICODE)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def continuity_payload(config: ExperimentConfig) -> dict[str, Any]:
    """Return only fields that must remain stable across chapters and evaluation branches.

    Chapter length, output location, probes and coupling interventions are intentionally excluded:
    they are allowed to change between discovery and evaluation while the embodied lineage remains
    the same. The model identity, body, world, sensorium, drive and memory architecture are not.
    """

    raw = config.to_dict()
    model = raw["model"]
    return {
        "paradigm": raw["paradigm"],
        "seed": raw["seed"],
        "body": raw["body"],
        "world": raw["world"],
        "sensorium": raw["sensorium"],
        "drive": raw["drive"],
        "memory": raw["memory"],
        "prompt": raw["prompt"],
        "model": {
            "provider": model["provider"],
            "model": model["model"],
            "json_mode": model["json_mode"],
            "seed": model["seed"],
        },
    }


def continuity_hash(config: ExperimentConfig) -> str:
    return _sha256(continuity_payload(config))


def encode_random_state(state: object) -> Any:
    if isinstance(state, tuple):
        return [encode_random_state(item) for item in state]
    if isinstance(state, list):
        return [encode_random_state(item) for item in state]
    return state


def decode_random_state(state: Any) -> object:
    if isinstance(state, list):
        return tuple(decode_random_state(item) for item in state)
    return state


def seal_checkpoint(payload: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(payload)
    result.pop("checkpoint_sha256", None)
    result["checkpoint_sha256"] = _sha256(result)
    return result


def write_checkpoint(path: str | Path, payload: dict[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    sealed = seal_checkpoint(payload)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(
        json.dumps(sealed, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(target)
    return target


def read_checkpoint(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    if int(payload.get("schema_version", 0)) != 1:
        raise ValueError("unsupported checkpoint schema_version")
    expected = str(payload.get("checkpoint_sha256", ""))
    if not expected:
        raise ValueError("checkpoint is missing checkpoint_sha256")
    unsigned = copy.deepcopy(payload)
    unsigned.pop("checkpoint_sha256", None)
    actual = _sha256(unsigned)
    if actual != expected:
        raise ValueError(f"checkpoint checksum mismatch: expected {expected}, computed {actual}")
    return payload


def validate_checkpoint(config: ExperimentConfig, checkpoint: dict[str, Any]) -> None:
    expected = continuity_hash(config)
    actual = str(checkpoint.get("continuity_hash", ""))
    if actual != expected:
        raise ValueError(
            "checkpoint continuity hash does not match this configuration; body, model, "
            "sensorium, drive, memory architecture or seed changed"
        )


def _tags(utterance: str, sensation: str) -> list[str]:
    tokens = {
        token.lower()
        for token in _TOKEN_RE.findall(f"{utterance}\n{sensation}")
        if len(token) > 2
    }
    return sorted(tokens)[:20]


def apply_memory_variant(
    checkpoint: dict[str, Any],
    variant: MemoryVariant,
    *,
    shuffle_seed: int = 1701,
    unrelated_checkpoint: dict[str, Any] | None = None,
    fresh_context: bool = True,
) -> dict[str, Any]:
    """Create an evaluation branch without mutating the frozen source checkpoint."""

    if variant not in {
        "full",
        "empty",
        "shuffled",
        "core_only",
        "archive_only",
        "unrelated",
    }:
        raise ValueError(f"unsupported memory variant: {variant}")

    branch = copy.deepcopy(checkpoint)
    state = branch.setdefault("state", {})
    memory = state.setdefault(
        "memory", {"core": "", "archive": [], "recent_utterances": []}
    )

    if variant == "empty":
        memory["core"] = ""
        memory["archive"] = []
        memory["recent_utterances"] = []
    elif variant == "core_only":
        memory["archive"] = []
        memory["recent_utterances"] = []
    elif variant == "archive_only":
        memory["core"] = ""
        memory["recent_utterances"] = []
    elif variant == "shuffled":
        archive = list(memory.get("archive", []))
        sensations = [str(item.get("sensation_excerpt", "")) for item in archive]
        random.Random(shuffle_seed).shuffle(sensations)
        for item, sensation in zip(archive, sensations):
            item["sensation_excerpt"] = sensation
            item["tags"] = _tags(str(item.get("utterance", "")), sensation)
        memory["archive"] = archive
        memory["recent_utterances"] = []
    elif variant == "unrelated":
        if unrelated_checkpoint is None:
            raise ValueError("unrelated memory variant requires an unrelated checkpoint")
        source_state = unrelated_checkpoint.get("state", {})
        source_memory = source_state.get("memory")
        if not isinstance(source_memory, dict):
            raise ValueError("unrelated checkpoint does not contain memory state")
        memory.clear()
        memory.update(copy.deepcopy(source_memory))
        memory["recent_utterances"] = []

    if fresh_context:
        state["history"] = []
        memory["recent_utterances"] = []
        state["model_context_reset"] = True

    branch["evaluation_memory_variant"] = variant
    branch["source_checkpoint_sha256"] = checkpoint.get("checkpoint_sha256")
    branch.pop("checkpoint_sha256", None)
    return seal_checkpoint(branch)
