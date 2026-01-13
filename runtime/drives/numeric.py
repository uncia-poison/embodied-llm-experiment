"""Numeric drive: extracts the first N numbers from the text."""
import re
from typing import List

class NumericDrive:
    def __init__(self, dim: int = 8):
        self.dim = dim

    def __call__(self, text: str) -> List[float]:
        nums = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", text)
        action = [0.5] * self.dim
        for i, n in enumerate(nums[: self.dim]):
            try:
                v = float(n)
                action[i] = max(0.0, min(1.0, v))
            except ValueError:
                pass
        return action
