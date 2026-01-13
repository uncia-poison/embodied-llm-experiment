"""Token drive: maps token-level features to an action vector."""
from typing import List

class TokenDrive:
    def __init__(self, dim: int = 8):
        self.dim = dim

    def __call__(self, text: str) -> List[float]:
        length = len(text)
        punct = sum(1 for c in text if c in "!?.;:")
        uppercase = sum(1 for c in text if c.isupper())
        action = [0.5] * self.dim
        # Simple mapping
        if self.dim >= 3:
            action[0] = min(1.0, length / 1000.0)
            action[1] = min(1.0, punct / 10.0)
            action[2] = min(1.0, uppercase / 50.0)
        return action
