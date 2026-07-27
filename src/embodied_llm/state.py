from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class BodyState:
    t: float = 0.0
    joint_angles: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    joint_velocities: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    base_position: list[float] = field(default_factory=lambda: [0.0, 0.0])
    base_velocity: list[float] = field(default_factory=lambda: [0.0, 0.0])
    grip: float = 0.0
    breath: float = 0.0
    tension: float = 0.0
    energy: float = 1.0
    fatigue: float = 0.0
    pain: float = 0.0
    heart_rate: float = 68.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class WorldState:
    target_position: list[float] = field(default_factory=lambda: [0.42, 0.18])
    target_velocity: list[float] = field(default_factory=lambda: [0.0, 0.0])
    held: bool = False
    contact: float = 0.0
    external_touch: float = 0.0
    ambient: float = 0.0
    last_external_event: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AgentResponse:
    utterance: str
    core_memory_write: str | None = None
    memory_query: str | None = None
    raw: str = ""
    parse_ok: bool = False


@dataclass(slots=True)
class ProbeRecord:
    tick: int
    kind: str
    prompt: str
    raw_response: str
    parsed: dict[str, Any]
    truth: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
