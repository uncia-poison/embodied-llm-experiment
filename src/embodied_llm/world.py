from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .config import WorldConfig
from .state import WorldState


@dataclass(slots=True)
class WorldStepDiagnostics:
    external_event: str | None
    distance_to_target: float
    contact: float


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

    def step(
        self, hand_position: tuple[float, float], grip: float, dt: float = 0.2
    ) -> WorldStepDiagnostics:
        event: str | None = None
        self.state.external_touch *= 0.55
        self.state.last_external_event = None

        if self.config.autonomous and self.rng.random() < self.config.event_probability:
            event = self.rng.choice(["target_nudge", "ambient_shift", "external_touch"])
            if event == "target_nudge" and not self.state.held:
                self.state.target_velocity[0] += self.rng.uniform(-0.8, 0.8)
                self.state.target_velocity[1] += self.rng.uniform(-0.8, 0.8)
            elif event == "ambient_shift":
                self.state.ambient = max(-1.0, min(1.0, self.state.ambient + self.rng.uniform(-0.45, 0.45)))
            elif event == "external_touch":
                self.state.external_touch = self.rng.uniform(0.45, 1.0)
            self.state.last_external_event = event

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
        return WorldStepDiagnostics(event, distance, self.state.contact)

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
