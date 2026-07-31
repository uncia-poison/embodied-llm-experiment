from __future__ import annotations

from typing import Protocol


class Drive(Protocol):
    def __call__(self, text: str) -> list[float]: ...

    def remap(self, seed: int) -> None: ...


def clip_action(values: list[float], action_dim: int) -> list[float]:
    if len(values) < action_dim:
        values = values + [0.0] * (action_dim - len(values))
    values = values[:action_dim]
    return [max(-1.0, min(1.0, float(value))) for value in values]
