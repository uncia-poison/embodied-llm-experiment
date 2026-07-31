from __future__ import annotations

import hashlib
import os
import re
from typing import Any, Protocol

import httpx
import numpy as np

from ..config import DriveConfig


class Embedder(Protocol):
    @property
    def dimension(self) -> int: ...

    def embed(self, text: str) -> np.ndarray: ...


class HashNgramEmbedder:
    """Dependency-free control embedder.

    This is not claimed to be a full semantic model. It preserves lexical and
    phrase similarity, making the end-to-end runtime reproducible without a model
    download. Scientific U3 runs should use sentence-transformers or an embedding API.
    """

    def __init__(self, dimension: int = 384):
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, text: str) -> np.ndarray:
        vector = np.zeros(self._dimension, dtype=np.float64)
        normalized = " ".join((text or "").lower().split())
        tokens = re.findall(r"[\w'-]+", normalized, flags=re.UNICODE)
        features = tokens + [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]
        for feature in features:
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=16).digest()
            index = int.from_bytes(digest[:8], "little") % self._dimension
            sign = 1.0 if digest[8] & 1 else -1.0
            vector[index] += sign
        norm = float(np.linalg.norm(vector))
        return vector / norm if norm > 0 else vector


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "install the 'semantic' extra to use sentence_transformers"
            ) from exc
        self.model = SentenceTransformer(model_name)
        self._dimension = int(self.model.get_sentence_embedding_dimension())

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, text: str) -> np.ndarray:
        value = self.model.encode([text], normalize_embeddings=True)[0]
        return np.asarray(value, dtype=np.float64)


class OpenAICompatibleEmbedder:
    def __init__(self, config: DriveConfig):
        self.config = config
        key = os.getenv(config.embedding_api_key_env, "")
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        self.client = httpx.Client(timeout=120.0, headers=headers)
        self._dimension = config.embedding_dim

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, text: str) -> np.ndarray:
        response = self.client.post(
            self.config.embedding_endpoint,
            json={"model": self.config.embedding_model, "input": text},
        )
        response.raise_for_status()
        vector = np.asarray(response.json()["data"][0]["embedding"], dtype=np.float64)
        self._dimension = int(vector.size)
        norm = float(np.linalg.norm(vector))
        return vector / norm if norm > 0 else vector


class SemanticProjectionDrive:
    def __init__(self, config: DriveConfig):
        self.config = config
        self.embedder = self._build_embedder(config)
        self.previous = np.zeros(config.action_dim, dtype=np.float64)
        self.current_projection_seed = int(config.projection_seed)
        self._set_projection(self.current_projection_seed)

    @staticmethod
    def _build_embedder(config: DriveConfig) -> Embedder:
        if config.embedding_provider == "hash_ngram":
            return HashNgramEmbedder(config.embedding_dim)
        if config.embedding_provider == "sentence_transformers":
            return SentenceTransformerEmbedder(config.embedding_model)
        if config.embedding_provider == "openai_compatible":
            return OpenAICompatibleEmbedder(config)
        raise ValueError(f"unsupported embedding provider: {config.embedding_provider}")

    def _set_projection(self, seed: int) -> None:
        self.current_projection_seed = int(seed)
        rng = np.random.default_rng(seed)
        matrix = rng.normal(size=(self.config.action_dim, self.embedder.dimension))
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        self.matrix = matrix / np.where(norms == 0, 1.0, norms)
        self.bias = rng.normal(0.0, 0.08, size=self.config.action_dim)

    def remap(self, seed: int) -> None:
        self._set_projection(seed)
        self.previous[:] = 0.0

    def __call__(self, text: str) -> list[float]:
        embedding = self.embedder.embed(text or "")
        if embedding.size != self.matrix.shape[1]:
            self._set_projection(self.config.projection_seed)
            if embedding.size != self.matrix.shape[1]:
                rng = np.random.default_rng(self.config.projection_seed)
                matrix = rng.normal(size=(self.config.action_dim, embedding.size))
                self.matrix = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
        raw = np.tanh(self.matrix @ embedding + self.bias)
        inertia = max(0.0, min(0.95, self.config.inertia))
        action = inertia * self.previous + (1.0 - inertia) * raw
        self.previous = np.clip(action, -1.0, 1.0)
        return self.previous.astype(float).tolist()

    def export_state(self) -> dict[str, Any]:
        return {
            "current_projection_seed": self.current_projection_seed,
            "matrix": self.matrix.astype(float).tolist(),
            "bias": self.bias.astype(float).tolist(),
            "previous": self.previous.astype(float).tolist(),
        }

    def import_state(self, state: dict[str, Any]) -> None:
        matrix = np.asarray(state.get("matrix", []), dtype=np.float64)
        bias = np.asarray(state.get("bias", []), dtype=np.float64)
        previous = np.asarray(state.get("previous", []), dtype=np.float64)
        expected_rows = self.config.action_dim
        if matrix.ndim != 2 or matrix.shape[0] != expected_rows:
            raise ValueError("checkpoint semantic drive matrix has incompatible shape")
        if bias.shape != (expected_rows,) or previous.shape != (expected_rows,):
            raise ValueError("checkpoint semantic drive vectors have incompatible shape")
        self.matrix = matrix
        self.bias = bias
        self.previous = np.clip(previous, -1.0, 1.0)
        self.current_projection_seed = int(
            state.get("current_projection_seed", self.config.projection_seed)
        )
