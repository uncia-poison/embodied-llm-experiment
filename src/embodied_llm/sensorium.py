from __future__ import annotations

import random
from dataclasses import dataclass

from .config import SensoriumConfig


@dataclass(slots=True)
class SensoriumFrame:
    tick: int
    text: str
    opaque_values: dict[str, float | None]
    researcher_values: dict[str, float]
    mapping: dict[str, str]


class SensoriumEncoder:
    """Render named simulator channels as stable, unnamed first-person signals.

    Unlike the removed base85 codec, this layer preserves learnable continuity.
    It hides semantics, not information. A model can notice that q07 rises after
    some expression without being told that q07 is heart rate or elbow velocity.
    """

    def __init__(self, config: SensoriumConfig):
        self.config = config
        self._ordered_names: list[str] | None = None
        self._permutation: list[int] | None = None
        self._last_opaque: dict[str, float | None] = {}

    def _initialize(self, names: list[str]) -> None:
        self._ordered_names = list(names)
        indices = list(range(len(names)))
        if self.config.mode in {"permuted", "masked"}:
            random.Random(self.config.channel_seed).shuffle(indices)
        self._permutation = indices

    def _revealed_count(self, tick: int, total: int) -> int:
        if self.config.mode != "masked":
            return total
        if self.config.reveal_every <= 0:
            return total
        stages = tick // self.config.reveal_every
        return min(total, self.config.reveal_start + stages * self.config.reveal_add)

    def encode(self, tick: int, channels: dict[str, float]) -> SensoriumFrame:
        names = list(channels)
        if self._ordered_names is None:
            self._initialize(names)
        elif names != self._ordered_names:
            raise ValueError("sensorium channel set or order changed during an episode")
        assert self._permutation is not None

        total = len(names)
        revealed = self._revealed_count(tick, total)
        opaque_values: dict[str, float | None] = {}
        mapping: dict[str, str] = {}
        lines = [f"CURRENT_SENSATION t={tick}"]
        for opaque_index, source_index in enumerate(self._permutation):
            opaque = f"q{opaque_index:02d}"
            source = names[source_index]
            mapping[opaque] = source
            value = round(float(channels[source]), self.config.decimals)
            shown: float | None = value if opaque_index < revealed else None
            opaque_values[opaque] = shown
            if shown is None:
                lines.append(f"{opaque} = ?")
                continue
            if self.config.include_delta and opaque in self._last_opaque:
                previous = self._last_opaque[opaque]
                delta = None if previous is None else round(shown - previous, self.config.decimals)
                if delta is not None:
                    lines.append(f"{opaque} = {shown:+.{self.config.decimals}f}  Δ {delta:+.{self.config.decimals}f}")
                    continue
            lines.append(f"{opaque} = {shown:+.{self.config.decimals}f}")
        self._last_opaque = dict(opaque_values)
        return SensoriumFrame(tick, "\n".join(lines), opaque_values, dict(channels), mapping)
