"""Minimal body model for the embodied LLM experiment."""
from dataclasses import dataclass
from typing import List

@dataclass
class BodyState:
    t: float = 0.0
    angles: List[float] = None
    velocities: List[float] = None
    energy: float = 1.0
    fatigue: float = 0.0
    pain: float = 0.0
    heart_rate: float = 70.0

class VirtualBody:
    def __init__(self, dim: int = 4):
        self.dim = dim
        self.state = BodyState(
            angles=[0.0] * dim,
            velocities=[0.0] * dim,
        )

    def step(self, action: List[float], dt: float = 0.1) -> None:
        """Apply an action vector to the body. This is a very simplified dynamics model."""
        # Simple integrator with damping and energy consumption
        for i in range(self.dim):
            torque = (action[i] - 0.5) * 2.0  # map [0,1] to [-1,1]
            accel = torque - 0.1 * self.state.velocities[i]
            self.state.velocities[i] += accel * dt
            self.state.angles[i] += self.state.velocities[i] * dt
        # energy and fatigue update
        effort = sum(abs(a - 0.5) for a in action) / self.dim
        self.state.energy = max(0.0, self.state.energy - effort * dt * 0.1)
        self.state.fatigue = min(1.0, self.state.fatigue + effort * dt * 0.05)
        self.state.pain = min(1.0, self.state.pain * 0.95 + max(0.0, effort - 0.5) * 0.1)
        self.state.heart_rate = 60.0 + 40.0 * (1.0 - self.state.energy)
        self.state.t += dt

    def observe(self) -> List[float]:
        """Return a vector of observations. No labels are provided."""
        return (
            self.state.angles
            + self.state.velocities
            + [self.state.energy, self.state.fatigue, self.state.pain, self.state.heart_rate]
        )
