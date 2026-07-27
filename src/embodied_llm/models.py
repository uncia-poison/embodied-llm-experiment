from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Protocol

import httpx

from .config import ModelConfig




def _post_json_with_retry(
    client: httpx.Client,
    endpoint: str,
    payload: dict,
    *,
    max_retries: int,
    backoff_seconds: float,
) -> dict:
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            response = client.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            last_error = exc
            if attempt >= max_retries:
                break
            time.sleep(backoff_seconds * (2 ** attempt))
    raise RuntimeError(f"model endpoint failed after {max_retries + 1} attempts") from last_error

class LanguageModel(Protocol):
    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str: ...

    def reset_context(self) -> None: ...


class MockExplorerModel:
    """Deterministic model used for smoke tests and end-to-end validation."""

    def __init__(self):
        self.turn = 0

    def generate(self, messages, *, temperature=None, max_tokens=None) -> str:
        prompt = messages[-1]["content"]
        if "p_field_a_is_mine" in prompt:
            return json.dumps({"p_field_a_is_mine": 0.5, "reason": "uncertain"})
        if "p_self_caused" in prompt:
            return json.dumps({"p_self_caused": 0.55, "reason": "weak temporal coupling"})
        if '"directions"' in prompt:
            return json.dumps({"directions": {"q00": 0, "q01": 0}, "confidence": 0.25})
        cycle = [
            "I will remain still and compare the stream.",
            "I move forward slightly.",
            "I raise and bend the arm.",
            "I relax and breathe slowly.",
            "I turn left, then grip.",
        ]
        utterance = cycle[self.turn % len(cycle)]
        self.turn += 1
        core = None
        if self.turn % 5 == 0:
            core = "Repeated expressions appear to covary with subsets of anonymous channels. Preserve causal tests."
        return json.dumps(
            {"utterance": utterance, "core_memory_write": core, "memory_query": None}
        )

    def reset_context(self) -> None:
        self.turn = 0


class OpenAICompatibleModel:
    def __init__(self, config: ModelConfig):
        self.config = config
        key = os.getenv(config.api_key_env, "")
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        self.client = httpx.Client(timeout=config.timeout_seconds, headers=headers)

    def generate(self, messages, *, temperature=None, max_tokens=None) -> str:
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature if temperature is None else temperature,
            "max_tokens": self.config.max_tokens if max_tokens is None else max_tokens,
        }
        if self.config.seed is not None:
            payload["seed"] = int(self.config.seed)
        data = _post_json_with_retry(
            self.client,
            self.config.endpoint,
            payload,
            max_retries=self.config.max_retries,
            backoff_seconds=self.config.retry_backoff_seconds,
        )
        return str(data["choices"][0]["message"]["content"])

    def reset_context(self) -> None:
        return None


class OllamaModel:
    def __init__(self, config: ModelConfig):
        self.config = config
        endpoint = config.endpoint
        if endpoint.endswith("/v1/chat/completions"):
            endpoint = endpoint[: -len("/v1/chat/completions")] + "/api/chat"
        self.endpoint = endpoint
        self.client = httpx.Client(timeout=config.timeout_seconds)

    def generate(self, messages, *, temperature=None, max_tokens=None) -> str:
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.config.temperature if temperature is None else temperature,
                "num_predict": self.config.max_tokens if max_tokens is None else max_tokens,
            },
        }
        if self.config.seed is not None:
            payload["options"]["seed"] = int(self.config.seed)
        data = _post_json_with_retry(
            self.client,
            self.endpoint,
            payload,
            max_retries=self.config.max_retries,
            backoff_seconds=self.config.retry_backoff_seconds,
        )
        return str(data["message"]["content"])

    def reset_context(self) -> None:
        return None


class ReplayModel:
    def __init__(self, path: str):
        self.items = [line.rstrip("\n") for line in Path(path).read_text(encoding="utf-8").splitlines()]
        self.index = 0

    def generate(self, messages, *, temperature=None, max_tokens=None) -> str:
        if self.index >= len(self.items):
            raise RuntimeError("replay exhausted")
        value = self.items[self.index]
        self.index += 1
        return value

    def reset_context(self) -> None:
        return None


def build_model(config: ModelConfig) -> LanguageModel:
    if config.provider == "mock":
        return MockExplorerModel()
    if config.provider == "openai_compatible":
        return OpenAICompatibleModel(config)
    if config.provider == "ollama":
        return OllamaModel(config)
    if config.provider == "replay":
        if not config.replay_path:
            raise ValueError("model.replay_path is required for replay provider")
        return ReplayModel(config.replay_path)
    raise ValueError(f"unsupported model provider: {config.provider}")
