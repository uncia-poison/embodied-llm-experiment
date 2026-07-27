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

    def _yoked_random_action(self, proposed: list[float]) -> list[float]:
        """Break axis semantics while preserving the exact action magnitude distribution.

        A signed permutation preserves L1/L2 norms and the component multiset, avoiding the
        gross-effort confound introduced by independent uniform random actions.
        """
        indices = list(range(self.action_dim))
        self.rng.shuffle(indices)
        return [
            proposed[source] * (-1.0 if self.rng.random() < 0.5 else 1.0)
            for source in indices
        ]

    def apply(self, proposed: list[float], block: CouplingBlock) -> tuple[list[float], dict]:
        key = (block.start, block.end, block.mode, block.remap_seed)
        changed = key != self.last_block_key
        if changed:
            self.delay_buffer.clear()
        self.last_block_key = key

        detail: str | None = None
        if block.mode == "coupled":
            applied = list(proposed)
        elif block.mode == "disconnected":
            applied = [0.0] * self.action_dim
        elif block.mode == "random":
            applied = self._yoked_random_action(proposed)
            detail = "signed_permutation_yoked_to_current_action"
        elif block.mode == "delayed":
            self.delay_buffer.append(list(proposed))
            applied = (
                list(self.delay_buffer[0])
                if len(self.delay_buffer) == self.delay_buffer.maxlen
                else [0.0] * self.action_dim
            )
            detail = "one_tick_delay"
        else:
            raise ValueError(f"unsupported coupling mode: {block.mode}")
        return applied, {
            "mode": block.mode,
            "detail": detail,
            "block_changed": changed,
            "start": block.start,
            "end": block.end,
            "remap_seed": block.remap_seed,
            "reset_context_at_start": block.reset_context_at_start,
        }
