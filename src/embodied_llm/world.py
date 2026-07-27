from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Final

from .config import WorldConfig
from .state import WorldState


@dataclass(frozen=True, slots=True)
class ExternalEventPacket:
    """A fully sampled exogenous event that can be replayed across worlds."""

    kind: str | None = None
    impulse_x: float = 0.0
    impulse_y: float = 0.0
    ambient_delta: float = 0.0
    touch_level: float = 0.0


@dataclass(slots=True)
class WorldStepDiagnostics:
    external_event: str | None
    external_event_packet: ExternalEventPacket
    distance_to_target: float
    contact: float


_AUTO_EVENT: Final = object()


class WorldModel:
    def __init__(self, config: WorldConfig, rng: random.Random):
        self.config = config
        self.rng = rng
        self.state = WorldState()
        self.reset()

    def reset(self) -> WorldState:
        # Never place the target at the arm's default endpoint (0.7, 0.0).
        while True:
            x = self.rng.uniform(self.config.target_min, self.config.target_max)
            y = self.rng.uniform(self.config.target_min, self.config.target_max)
            if math.dist((x, y), (0.7, 0.0)) > self.config.contact_radius * 2.5:
                break
        self.state = WorldState(target_position=[x, y], ambient=self.rng.uniform(-0.2, 0.2))
        return self.state

    def sample_external_event(self) -> ExternalEventPacket:
        if not self.config.autonomous or self.rng.random() >= self.config.event_probability:
            return ExternalEventPacket()
        kind = self.rng.choice(["target_nudge", "ambient_shift", "external_touch"])
        if kind == "target_nudge":
            return ExternalEventPacket(
                kind=kind,
                impulse_x=self.rng.uniform(-0.8, 0.8),
                impulse_y=self.rng.uniform(-0.8, 0.8),
            )
        if kind == "ambient_shift":
            return ExternalEventPacket(kind=kind, ambient_delta=self.rng.uniform(-0.45, 0.45))
        return ExternalEventPacket(kind=kind, touch_level=self.rng.uniform(0.45, 1.0))

    def step(
        self,
        hand_position: tuple[float, float],
        grip: float,
        dt: float = 0.2,
        external_event: ExternalEventPacket | object = _AUTO_EVENT,
    ) -> WorldStepDiagnostics:
        packet = self.sample_external_event() if external_event is _AUTO_EVENT else external_event
        if not isinstance(packet, ExternalEventPacket):
            raise TypeError("external_event must be an ExternalEventPacket")

        self.state.external_touch *= 0.55
        self.state.last_external_event = packet.kind

        if packet.kind == "target_nudge" and not self.state.held:
            self.state.target_velocity[0] += packet.impulse_x
            self.state.target_velocity[1] += packet.impulse_y
        elif packet.kind == "ambient_shift":
            self.state.ambient = max(-1.0, min(1.0, self.state.ambient + packet.ambient_delta))
        elif packet.kind == "external_touch":
            self.state.external_touch = packet.touch_level

        dx = hand_position[0] - self.state.target_position[0]
        dy = hand_position[1] - self.state.target_position[1]
        distance = math.hypot(dx, dy)
        contact = max(0.0, 1.0 - distance / self.config.contact_radius)
        self.state.contact = contact

        if contact > 0.5 and grip > 0.35:
            self.state.held = True
        elif grip < -0.25:
            self.state.held = False

        if self.state.held:
            self.state.target_position[0] += (hand_position[0] - self.state.target_position[0]) * 0.75
            self.state.target_position[1] += (hand_position[1] - self.state.target_position[1]) * 0.75
            self.state.target_velocity = [0.0, 0.0]
        else:
            for index in range(2):
                self.state.target_position[index] += self.state.target_velocity[index] * dt
                self.state.target_velocity[index] *= 0.72
                bound = self.config.target_max
                if abs(self.state.target_position[index]) > bound:
                    self.state.target_position[index] = math.copysign(bound, self.state.target_position[index])
                    self.state.target_velocity[index] *= -0.5

        dx = self.state.target_position[0] - hand_position[0]
        dy = self.state.target_position[1] - hand_position[1]
        distance = math.hypot(dx, dy)
        self.state.contact = max(0.0, 1.0 - distance / self.config.contact_radius)
        return WorldStepDiagnostics(packet.kind, packet, distance, self.state.contact)

    def observation(self, hand_position: tuple[float, float]) -> dict[str, float]:
        dx = self.state.target_position[0] - hand_position[0]
        dy = self.state.target_position[1] - hand_position[1]
        return {
            "target_rel_x": dx,
            "target_rel_y": dy,
            "target_distance": math.hypot(dx, dy),
            "contact": self.state.contact,
            "external_touch": self.state.external_touch,
            "ambient": self.state.ambient,
            "held": 1.0 if self.state.held else 0.0,
        }
