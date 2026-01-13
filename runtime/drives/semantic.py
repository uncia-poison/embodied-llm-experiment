"""Semantic drive: uses a text embedding to produce an action vector.

This is a placeholder implementation that hashes the text to generate a pseudo-random but deterministic vector. In a real experiment, you would replace this with a proper embedding model (e.g. e5, Qwen embeddings) and a random projection matrix.
"""
import hashlib
from typing import List

class SemanticDrive:
    def __init__(self, dim: int = 8):
        self.dim = dim
        seed = b"fixed_seed_for_projection"
        md = hashlib.sha256(seed).digest()
        self.projection = [(md[i % len(md)] / 255.0) * 2.0 - 1.0 for i in range(dim)]

    def _embed(self, text: str, embed_dim: int = 16) -> List[float]:
        h = hashlib.sha256(text.encode("utf-8")).digest()
        return [(h[i] / 255.0) for i in range(embed_dim)]

    def __call__(self, text: str) -> List[float]:
        embed = self._embed(text, embed_dim=len(self.projection))
        action = []
        for i in range(self.dim):
            v = embed[i] * self.projection[i]
            action.append((v + 1.0) / 2.0)
        return action
