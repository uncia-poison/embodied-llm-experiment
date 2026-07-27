from __future__ import annotations

import random
from collections import deque

from .config import CouplingBlock


class CouplingController:
    def __init__(self, action_dim: int, seed: int):
        self.action_dim = action_dim
        self.rng = random.Random(seed)
        self.delay_buffer: deque[list[float]] = deque(maxlen=2)
        self.last_block_key: tuple[int, int, str, int | None] | None = None

    def apply(self, proposed: list[float], block: CouplingBlock) -> tuple[list[float], dict]:
        key = (block.start, block.end, block.mode, block.remap_seed)
        changed = key != self.last_block_key
        self.last_block_key = key
        if block.mode == "coupled":
            applied = list(proposed)
        elif block.mode == "disconnected":
            applied = [0.0] * self.action_dim
        elif block.mode == "random":
            applied = [self.rng.uniform(-1.0, 1.0) for _ in range(self.action_dim)]
        elif block.mode == "delayed":
            self.delay_buffer.append(list(proposed))
            applied = (
                list(self.delay_buffer[0])
                if len(self.delay_buffer) == self.delay_buffer.maxlen
                else [0.0] * self.action_dim
            )
        else:
            raise ValueError(f"unsupported coupling mode: {block.mode}")
        return applied, {
            "mode": block.mode,
            "block_changed": changed,
            "remap_seed": block.remap_seed,
        }
