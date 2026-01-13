"""Minimal world model for the embodied LLM experiment."""
from dataclasses import dataclass
from typing import Tuple
import random

@dataclass
class WorldState:
    target_pos: Tuple[float, float] = (0.5, 0.0)
    contact: bool = False

class SimpleWorld:
    def __init__(self):
        self.state = WorldState()

    def reset(self):
        self.state.target_pos = (random.uniform(0.3, 0.7), random.uniform(-0.2, 0.2))
        self.state.contact = False

    def update(self, hand_pos: Tuple[float, float]):
        dx = hand_pos[0] - self.state.target_pos[0]
        dy = hand_pos[1] - self.state.target_pos[1]
        self.state.contact = (dx * dx + dy * dy) < 0.05

    def observe(self) -> Tuple[float, float, float]:
        dx = self.state.target_pos[0]
        dy = self.state.target_pos[1]
        return dx, dy, 1.0 if self.state.contact else 0.0
