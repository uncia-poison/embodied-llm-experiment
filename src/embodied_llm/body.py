from __future__ import annotations

import math
from dataclasses import dataclass

from .config import BodyConfig
from .state import BodyState


@dataclass(slots=True)
class BodyStepDiagnostics:
    effort: float
    hand_position: tuple[float, float]


class BodyModel:
    """A compact body with arm, translation, grip and interoceptive dynamics.

    The action contract is deliberately strict: every drive returns exactly eight
    signed controls in [-1, 1]. Zero always means no command. The runtime never
    guesses whether a vector is normalized in some other convention.
    """

    ACTION_DIM = 8

    def __init__(self, config: BodyConfig):
        self.config = config
        self.state = BodyState()

    @staticmethod
    def validate_action(action: list[float]) -> list[float]:
        if len(action) != BodyModel.ACTION_DIM:
            raise ValueError(f"expected {BodyModel.ACTION_DIM} actions, got {len(action)}")
        cleaned: list[float] = []
        for value in action:
            value = float(value)
            if not math.isfinite(value):
                raise ValueError("action contains a non-finite value")
            cleaned.append(max(-1.0, min(1.0, value)))
        return cleaned

    def reset(self, state: BodyState | None = None) -> BodyState:
        self.state = state or BodyState()
        return self.state

    def hand_position(self) -> tuple[float, float]:
        shoulder, elbow, wrist = self.state.joint_angles
        lengths = (0.35, 0.25, 0.10)
        a1 = shoulder
        a2 = shoulder + elbow
        a3 = shoulder + elbow + wrist
        x = self.state.base_position[0]
        y = self.state.base_position[1]
        x += lengths[0] * math.cos(a1) + lengths[1] * math.cos(a2) + lengths[2] * math.cos(a3)
        y += lengths[0] * math.sin(a1) + lengths[1] * math.sin(a2) + lengths[2] * math.sin(a3)
        return x, y

    def step(self, action: list[float]) -> BodyStepDiagnostics:
        a = self.validate_action(action)
        dt = self.config.dt

        for index in range(3):
            acceleration = a[index] - self.config.damping * self.state.joint_velocities[index]
            self.state.joint_velocities[index] += acceleration * dt
            self.state.joint_angles[index] += self.state.joint_velocities[index] * dt
            limit = self.config.max_joint_angle
            if abs(self.state.joint_angles[index]) > limit:
                overflow = abs(self.state.joint_angles[index]) - limit
                self.state.joint_angles[index] = math.copysign(limit, self.state.joint_angles[index])
                self.state.joint_velocities[index] *= -0.2
                self.state.pain = min(1.0, self.state.pain + overflow * 0.3)

        for index, axis in enumerate((3, 4)):
            acceleration = a[axis] - self.config.damping * self.state.base_velocity[index]
            self.state.base_velocity[index] += acceleration * dt
            self.state.base_position[index] += self.state.base_velocity[index] * dt
            limit = self.config.max_base_position
            if abs(self.state.base_position[index]) > limit:
                self.state.base_position[index] = math.copysign(limit, self.state.base_position[index])
                self.state.base_velocity[index] *= -0.25
                self.state.pain = min(1.0, self.state.pain + 0.03)

        response_rate = min(1.0, dt * 2.5)
        self.state.grip += (a[5] - self.state.grip) * response_rate
        self.state.breath += (a[6] - self.state.breath) * response_rate
        self.state.tension += (a[7] - self.state.tension) * response_rate

        effort = sum(abs(value) for value in a) / len(a)
        motion = (
            sum(abs(v) for v in self.state.joint_velocities)
            + sum(abs(v) for v in self.state.base_velocity)
        ) / 5.0
        metabolic_load = 0.65 * effort + 0.25 * motion + 0.10 * max(0.0, self.state.tension)
        recovery = max(0.0, 1.0 - effort) * max(0.0, -self.state.tension) * 0.004
        self.state.energy = min(1.0, max(0.0, self.state.energy - metabolic_load * dt * 0.045 + recovery))
        self.state.fatigue = min(
            1.0,
            max(0.0, self.state.fatigue + metabolic_load * dt * 0.035 - (1.0 - effort) * dt * 0.012),
        )
        overload = max(0.0, metabolic_load - 0.78)
        self.state.pain = min(1.0, max(0.0, self.state.pain * (1.0 - dt * 0.015) + overload * dt * 0.12))
        breath_relief = max(0.0, self.state.breath) * 5.0
        self.state.heart_rate = max(
            48.0,
            min(
                190.0,
                62.0
                + 54.0 * metabolic_load
                + 24.0 * (1.0 - self.state.energy)
                + 16.0 * self.state.fatigue
                - breath_relief,
            ),
        )
        self.state.t += dt
        return BodyStepDiagnostics(effort=effort, hand_position=self.hand_position())

    def observation(self) -> dict[str, float]:
        hand_x, hand_y = self.hand_position()
        values: dict[str, float] = {}
        for idx, value in enumerate(self.state.joint_angles):
            values[f"joint_angle_{idx}"] = value
        for idx, value in enumerate(self.state.joint_velocities):
            values[f"joint_velocity_{idx}"] = value
        values.update(
            {
                "base_x": self.state.base_position[0],
                "base_y": self.state.base_position[1],
                "base_vx": self.state.base_velocity[0],
                "base_vy": self.state.base_velocity[1],
                "hand_x": hand_x,
                "hand_y": hand_y,
                "grip": self.state.grip,
                "breath": self.state.breath,
                "tension": self.state.tension,
                "energy": self.state.energy,
                "fatigue": self.state.fatigue,
                "pain": self.state.pain,
                "heart_rate": self.state.heart_rate / 200.0,
            }
        )
        return values
