from __future__ import annotations

import hashlib
import random
import re

from .base import clip_action


class NoneDrive:
    def __init__(self, action_dim: int):
        self.action_dim = action_dim

    def __call__(self, text: str) -> list[float]:
        return [0.0] * self.action_dim

    def remap(self, seed: int) -> None:
        return None


class NumericDrive:
    def __init__(self, action_dim: int):
        self.action_dim = action_dim

    def __call__(self, text: str) -> list[float]:
        numbers = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", text or "")
        values = [float(item) for item in numbers[: self.action_dim]]
        return clip_action(values, self.action_dim)

    def remap(self, seed: int) -> None:
        return None


class TokenDrive:
    def __init__(self, action_dim: int):
        self.action_dim = action_dim

    def __call__(self, text: str) -> list[float]:
        text = text or ""
        features = [
            min(1.0, len(text) / 500.0),
            min(1.0, sum(c in "!?" for c in text) / 8.0),
            min(1.0, sum(c.isupper() for c in text) / 30.0),
            min(1.0, len(text.split()) / 80.0),
        ]
        signed = [value * 2.0 - 1.0 for value in features]
        return clip_action(signed, self.action_dim)

    def remap(self, seed: int) -> None:
        return None


class RandomDrive:
    def __init__(self, action_dim: int, seed: int):
        self.action_dim = action_dim
        self.rng = random.Random(seed)

    def __call__(self, text: str) -> list[float]:
        return [self.rng.uniform(-1.0, 1.0) for _ in range(self.action_dim)]

    def remap(self, seed: int) -> None:
        self.rng.seed(seed)


class PatternDrive:
    def __init__(self, action_dim: int, inertia: float = 0.0):
        self.action_dim = action_dim
        self.inertia = max(0.0, min(0.95, inertia))
        self.previous = [0.0] * action_dim

    @staticmethod
    def _has(text: str, *terms: str) -> bool:
        return any(term in text for term in terms)

    def __call__(self, text: str) -> list[float]:
        t = (text or "").lower()
        action = [0.0] * self.action_dim
        if self._has(t, "forward", "ahead", "вперёд", "вперед", "прямо"):
            action[3] += 0.8
        if self._has(t, "backward", "назад"):
            action[3] -= 0.8
        if self._has(t, "left", "налево", "влево"):
            action[4] += 0.7
        if self._has(t, "right", "направо", "вправо"):
            action[4] -= 0.7
        if self._has(t, "raise", "lift", "подними", "поднять", "вверх"):
            action[0] += 0.8
        if self._has(t, "lower", "опусти", "вниз"):
            action[0] -= 0.8
        if self._has(t, "bend", "согни", "согнуть"):
            action[1] += 0.8
        if self._has(t, "straighten", "extend", "разогни"):
            action[1] -= 0.8
        if self._has(t, "turn", "rotate", "поверни", "разверни"):
            digest = hashlib.sha256(t.encode("utf-8")).digest()
            action[2] += 0.65 if digest[0] % 2 else -0.65
        if self._has(t, "grip", "clench", "сожми", "схвати"):
            action[5] += 0.9
        if self._has(t, "release", "отпусти", "разожми"):
            action[5] -= 0.9
        if self._has(t, "breathe", "breath", "дыши", "вдох"):
            action[6] += 0.75
        if self._has(t, "slowly", "медленно", "медленнее"):
            action[6] -= 0.3
        if self._has(t, "relax", "расслаб"):
            action[7] -= 0.9
        if self._has(t, "tense", "напряг"):
            action[7] += 0.9
        if self._has(t, "still", "stop", "стой", "замри", "не двига"):
            action = [0.0] * self.action_dim
        blended = [
            self.inertia * old + (1.0 - self.inertia) * new
            for old, new in zip(self.previous, action)
        ]
        self.previous = clip_action(blended, self.action_dim)
        return list(self.previous)

    def remap(self, seed: int) -> None:
        # Pattern mode is an interpretable positive control and does not remap.
        return None
