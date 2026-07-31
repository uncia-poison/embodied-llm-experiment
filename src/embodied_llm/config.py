from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

DriveMode = Literal["none", "numeric", "token", "pattern", "semantic", "random"]
ModelProvider = Literal[
    "mock",
    "openai_compatible",
    "gemini",
    "ollama",
    "manual_relay",
    "replay",
]
SensoriumMode = Literal["plain", "permuted", "masked"]
CouplingMode = Literal["coupled", "disconnected", "random", "delayed"]
Paradigm = Literal["single_body", "ownership_pair"]
RelayVendor = Literal["generic", "deepseek", "gemini"]


@dataclass(slots=True)
class BodyConfig:
    action_dim: int = 8
    dt: float = 0.2
    damping: float = 0.18
    max_joint_angle: float = 2.6
    max_base_position: float = 1.5


@dataclass(slots=True)
class WorldConfig:
    autonomous: bool = True
    event_probability: float = 0.04
    contact_radius: float = 0.09
    target_min: float = -0.65
    target_max: float = 0.65


@dataclass(slots=True)
class SensoriumConfig:
    mode: SensoriumMode = "permuted"
    channel_seed: int = 1701
    decimals: int = 3
    reveal_start: int = 8
    reveal_every: int = 20
    reveal_add: int = 3
    include_delta: bool = True


@dataclass(slots=True)
class DriveConfig:
    mode: DriveMode = "pattern"
    action_dim: int = 8
    inertia: float = 0.15
    projection_seed: int = 9137
    embedding_provider: Literal[
        "hash_ngram", "sentence_transformers", "openai_compatible"
    ] = "hash_ngram"
    embedding_model: str = "intfloat/multilingual-e5-small"
    embedding_endpoint: str = "http://localhost:11434/v1/embeddings"
    embedding_api_key_env: str = "OPENAI_API_KEY"
    embedding_dim: int = 384


@dataclass(slots=True)
class MemoryConfig:
    mode: Literal["none", "core", "full"] = "full"
    core_max_chars: int = 1800
    archive_max_items: int = 5000
    peek_items: int = 6
    retrieval_items: int = 5
    digest_turns: int = 4
    history_turns: int = 3


@dataclass(slots=True)
class ModelConfig:
    provider: ModelProvider = "mock"
    model: str = "mock-explorer"
    endpoint: str = "http://localhost:11434/v1/chat/completions"
    api_key_env: str = "OPENAI_API_KEY"
    api_key_required: bool = False
    json_mode: bool = False
    temperature: float = 0.7
    max_tokens: int = 450
    timeout_seconds: float = 120.0
    max_retries: int = 2
    retry_backoff_seconds: float = 1.0
    seed: int | None = None
    replay_path: str | None = None
    relay_dir: str = "manual-sessions/default"
    relay_vendor: RelayVendor = "generic"
    relay_sentinel: str = ".submit"
    relay_require_fresh_chat: bool = True


@dataclass(slots=True)
class PromptConfig:
    profile: Literal["genesis", "neutral", "minimal"] = "neutral"


@dataclass(slots=True)
class ProbeConfig:
    enabled: bool = True
    warmup_ticks: int = 30
    agency_every: int = 10
    prediction_every: int = 10
    max_probe_tokens: int = 250


@dataclass(slots=True)
class CouplingBlock:
    start: int
    end: int
    mode: CouplingMode = "coupled"
    remap_seed: int | None = None
    reset_context_at_start: bool = False

    def contains(self, tick: int) -> bool:
        return self.start <= tick < self.end


@dataclass(slots=True)
class OwnershipBlock:
    start: int
    end: int
    owner: Literal["A", "B"] = "A"

    def contains(self, tick: int) -> bool:
        return self.start <= tick < self.end


@dataclass(slots=True)
class OwnershipConfig:
    shadow_mode: Literal["delayed", "random", "disconnected"] = "delayed"
    probe_warmup_ticks: int = 30
    probe_every: int = 10
    randomize_field_labels: bool = True
    blocks: list[OwnershipBlock] = field(default_factory=list)


@dataclass(slots=True)
class ExperimentConfig:
    paradigm: Paradigm = "single_body"
    name: str = "genesis-mvp"
    seed: int = 42
    ticks: int = 120
    output_dir: str = "runs"
    body: BodyConfig = field(default_factory=BodyConfig)
    world: WorldConfig = field(default_factory=WorldConfig)
    sensorium: SensoriumConfig = field(default_factory=SensoriumConfig)
    drive: DriveConfig = field(default_factory=DriveConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    probes: ProbeConfig = field(default_factory=ProbeConfig)
    prompt: PromptConfig = field(default_factory=PromptConfig)
    coupling: list[CouplingBlock] = field(default_factory=list)
    ownership: OwnershipConfig = field(default_factory=OwnershipConfig)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ExperimentConfig":
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        ownership_raw = raw.get("ownership", {})
        cfg = cls(
            paradigm=str(raw.get("paradigm", "single_body")),
            name=str(raw.get("name", "genesis-mvp")),
            seed=int(raw.get("seed", 42)),
            ticks=int(raw.get("ticks", 120)),
            output_dir=str(raw.get("output_dir", "runs")),
            body=BodyConfig(**raw.get("body", {})),
            world=WorldConfig(**raw.get("world", {})),
            sensorium=SensoriumConfig(**raw.get("sensorium", {})),
            drive=DriveConfig(**raw.get("drive", {})),
            memory=MemoryConfig(**raw.get("memory", {})),
            model=ModelConfig(**raw.get("model", {})),
            probes=ProbeConfig(**raw.get("probes", {})),
            prompt=PromptConfig(**raw.get("prompt", {})),
            coupling=[CouplingBlock(**item) for item in raw.get("coupling", [])],
            ownership=OwnershipConfig(
                shadow_mode=ownership_raw.get("shadow_mode", "delayed"),
                probe_warmup_ticks=int(ownership_raw.get("probe_warmup_ticks", 30)),
                probe_every=int(ownership_raw.get("probe_every", 10)),
                randomize_field_labels=bool(ownership_raw.get("randomize_field_labels", True)),
                blocks=[OwnershipBlock(**item) for item in ownership_raw.get("blocks", [])],
            ),
        )
        cfg.validate()
        return cfg

    @staticmethod
    def _validate_nonoverlap(blocks: list[Any], label: str) -> None:
        ordered = sorted(blocks, key=lambda block: (block.start, block.end))
        for left, right in zip(ordered, ordered[1:]):
            if right.start < left.end:
                raise ValueError(f"overlapping {label} blocks: {left} and {right}")

    def validate(self) -> None:
        if self.ticks <= 0:
            raise ValueError("ticks must be positive")
        if self.body.action_dim != self.drive.action_dim:
            raise ValueError("body.action_dim and drive.action_dim must match")
        if self.body.action_dim != 8:
            raise ValueError("the current body implementation requires action_dim=8")
        if self.body.dt <= 0:
            raise ValueError("body.dt must be positive")
        if not 0.0 <= self.body.damping <= 1.0:
            raise ValueError("body.damping must be between 0 and 1")
        if not 0.0 <= self.world.event_probability <= 1.0:
            raise ValueError("world.event_probability must be between 0 and 1")
        if self.world.contact_radius <= 0:
            raise ValueError("world.contact_radius must be positive")
        if self.world.target_min >= self.world.target_max:
            raise ValueError("world.target_min must be lower than world.target_max")
        if self.sensorium.decimals < 0 or self.sensorium.decimals > 8:
            raise ValueError("sensorium.decimals must be between 0 and 8")
        if not 0.0 <= self.drive.inertia < 1.0:
            raise ValueError("drive.inertia must be in [0, 1)")
        if self.model.max_retries < 0:
            raise ValueError("model.max_retries cannot be negative")
        if self.model.timeout_seconds <= 0:
            raise ValueError("model.timeout_seconds must be positive")
        if self.model.provider not in {
            "mock",
            "openai_compatible",
            "gemini",
            "ollama",
            "manual_relay",
            "replay",
        }:
            raise ValueError(f"unsupported model provider: {self.model.provider}")
        if self.model.relay_vendor not in {"generic", "deepseek", "gemini"}:
            raise ValueError(f"unsupported relay vendor: {self.model.relay_vendor}")
        if self.model.provider == "manual_relay":
            if not self.model.relay_dir.strip():
                raise ValueError("model.relay_dir is required for manual_relay")
            if not self.model.relay_sentinel.strip():
                raise ValueError("model.relay_sentinel cannot be empty")
        if self.paradigm not in {"single_body", "ownership_pair"}:
            raise ValueError(f"unsupported paradigm: {self.paradigm}")
        for block in self.coupling:
            if block.start < 0 or block.end <= block.start:
                raise ValueError(f"invalid coupling block: {block}")
            if block.end > self.ticks:
                raise ValueError(f"coupling block extends beyond run: {block}")
        self._validate_nonoverlap(self.coupling, "coupling")
        for block in self.ownership.blocks:
            if block.start < 0 or block.end <= block.start or block.end > self.ticks:
                raise ValueError(f"invalid ownership block: {block}")
        self._validate_nonoverlap(self.ownership.blocks, "ownership")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def ownership_for_tick(self, tick: int) -> OwnershipBlock:
        for block in self.ownership.blocks:
            if block.contains(tick):
                return block
        return OwnershipBlock(start=0, end=self.ticks, owner="A")

    def coupling_for_tick(self, tick: int) -> CouplingBlock:
        for block in self.coupling:
            if block.contains(tick):
                return block
        return CouplingBlock(start=0, end=self.ticks, mode="coupled")