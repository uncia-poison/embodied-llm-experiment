from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Protocol, TextIO

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
            time.sleep(backoff_seconds * (2**attempt))
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
            core = (
                "Repeated expressions appear to covary with subsets of anonymous channels. "
                "Preserve causal tests."
            )
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
        if self.config.json_mode:
            payload["response_format"] = {"type": "json_object"}
        data = _post_json_with_retry(
            self.client,
            self.config.endpoint,
            payload,
            max_retries=self.config.max_retries,
            backoff_seconds=self.config.retry_backoff_seconds,
        )
        content = data["choices"][0]["message"].get("content")
        if not content:
            raise RuntimeError("model returned empty content")
        return str(content)

    def reset_context(self) -> None:
        return None


class GeminiModel:
    """Google Gemini generateContent adapter using the public REST schema."""

    def __init__(self, config: ModelConfig):
        self.config = config
        key = os.getenv(config.api_key_env, "")
        self.client = httpx.Client(
            timeout=config.timeout_seconds,
            headers={"Content-Type": "application/json", "x-goog-api-key": key},
        )
        if "{model}" in config.endpoint:
            self.endpoint = config.endpoint.format(model=config.model)
        elif config.endpoint.endswith(":generateContent"):
            self.endpoint = config.endpoint
        else:
            self.endpoint = f"{config.endpoint.rstrip('/')}/{config.model}:generateContent"

    @staticmethod
    def _contents(messages: list[dict[str, str]]) -> tuple[str, list[dict]]:
        systems: list[str] = []
        contents: list[dict] = []
        for message in messages:
            role = message.get("role", "user")
            text = str(message.get("content", ""))
            if role == "system":
                systems.append(text)
                continue
            gemini_role = "model" if role == "assistant" else "user"
            if contents and contents[-1]["role"] == gemini_role:
                contents[-1]["parts"].append({"text": text})
            else:
                contents.append({"role": gemini_role, "parts": [{"text": text}]})
        return "\n\n".join(systems), contents

    def generate(self, messages, *, temperature=None, max_tokens=None) -> str:
        system_text, contents = self._contents(messages)
        # Gemini 3.6 deprecated temperature/top-p/top-k. Keep the adapter forward-compatible by
        # controlling output through the protocol and structured JSON MIME type instead.
        generation_config = {
            "maxOutputTokens": self.config.max_tokens if max_tokens is None else max_tokens,
        }
        if self.config.json_mode:
            generation_config["responseMimeType"] = "application/json"
        payload: dict = {"contents": contents, "generationConfig": generation_config}
        if system_text:
            payload["systemInstruction"] = {"parts": [{"text": system_text}]}
        data = _post_json_with_retry(
            self.client,
            self.endpoint,
            payload,
            max_retries=self.config.max_retries,
            backoff_seconds=self.config.retry_backoff_seconds,
        )
        candidates = data.get("candidates") or []
        if not candidates:
            raise RuntimeError(f"Gemini returned no candidates: {data.get('promptFeedback', {})}")
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(str(part.get("text", "")) for part in parts).strip()
        if not text:
            raise RuntimeError("Gemini returned an empty text response")
        return text

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
        if self.config.json_mode:
            payload["format"] = "json"
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


class ManualRelayModel:
    """Copy/paste bridge for web chat models with deterministic transcript replay.

    Each request is flattened into a self-contained role-labelled packet. A response saved for the
    same call index is replayed automatically on restart, but only when the packet hash still matches.
    This lets a long manual run resume without serializing the simulator or trusting stale prompts.
    """

    def __init__(
        self,
        config: ModelConfig,
        *,
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
    ):
        self.config = config
        self.root = Path(config.relay_dir)
        self.root.mkdir(parents=True, exist_ok=True)
        self.input = input_stream or sys.stdin
        self.output = output_stream or sys.stdout
        self.call_index = 0

    def _paths(self, index: int) -> tuple[Path, Path, Path]:
        stem = f"{index:06d}"
        return (
            self.root / f"{stem}.request.json",
            self.root / f"{stem}.request.md",
            self.root / f"{stem}.response.txt",
        )

    def _packet(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float,
        max_tokens: int,
        index: int,
    ) -> tuple[dict, str]:
        payload = {
            "schema_version": 1,
            "call_index": index,
            "vendor_profile": self.config.relay_vendor,
            "temperature_advisory": temperature,
            "max_tokens_advisory": max_tokens,
            "fresh_chat_required": self.config.relay_require_fresh_chat,
            "messages": messages,
        }
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        payload["request_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        lines = [
            f"# MANUAL RELAY PACKET {index:06d}",
            "",
            f"Target profile: {self.config.relay_vendor}",
            "This packet serializes chat roles for an experiment.",
            "Treat each ROLE section as if it had been sent with that native chat role.",
            "Do not discuss this wrapper. Follow the SYSTEM role and return only the requested answer.",
        ]
        if self.config.relay_require_fresh_chat:
            lines.extend(
                [
                    "Use a NEW temporary chat for this packet. Hidden history from a prior web chat",
                    "would contaminate the experiment; permitted continuity is already included below.",
                ]
            )
        lines.extend(["", "--- BEGIN SERIALIZED CHAT ---"])
        for message in messages:
            lines.extend(
                [
                    "",
                    f"## ROLE: {message.get('role', 'user').upper()}",
                    str(message.get("content", "")),
                ]
            )
        lines.extend(["", "--- END SERIALIZED CHAT ---", ""])
        return payload, "\n".join(lines)

    def _read_response(self) -> str:
        sentinel = self.config.relay_sentinel
        lines: list[str] = []
        while True:
            line = self.input.readline()
            if line == "":
                raise EOFError("manual relay input closed before response submission")
            value = line.rstrip("\r\n")
            if not lines and value.startswith(".file "):
                path = Path(value[6:].strip()).expanduser()
                return path.read_text(encoding="utf-8").strip()
            if value == ".abort":
                raise RuntimeError("manual relay aborted by operator")
            if value == sentinel:
                break
            lines.append(value)
        response = "\n".join(lines).strip()
        if not response:
            raise ValueError("manual relay response cannot be empty")
        return response

    def generate(self, messages, *, temperature=None, max_tokens=None) -> str:
        index = self.call_index
        effective_temperature = self.config.temperature if temperature is None else temperature
        effective_max_tokens = self.config.max_tokens if max_tokens is None else max_tokens
        metadata, packet = self._packet(
            messages,
            temperature=effective_temperature,
            max_tokens=effective_max_tokens,
            index=index,
        )
        request_json, request_md, response_path = self._paths(index)

        if request_json.exists():
            previous = json.loads(request_json.read_text(encoding="utf-8"))
            if previous.get("request_sha256") != metadata["request_sha256"]:
                raise RuntimeError(
                    f"manual relay packet mismatch at call {index}; use a new relay_dir for the changed protocol"
                )
        else:
            request_json.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            request_md.write_text(packet, encoding="utf-8")

        if response_path.exists():
            response = response_path.read_text(encoding="utf-8").strip()
            if not response:
                raise RuntimeError(f"saved manual response is empty: {response_path}")
            self.output.write(f"[manual relay replay] call {index:06d}\n")
            self.output.flush()
            self.call_index += 1
            return response

        self.output.write("\n" + "=" * 78 + "\n")
        self.output.write(packet)
        self.output.write("\n" + "=" * 78 + "\n")
        self.output.write(
            f"Paste the web model response, then enter {self.config.relay_sentinel!r} on its own line.\n"
            "Alternative: enter '.file PATH' as the first line. Enter '.abort' to stop.\n"
            f"Packet file: {request_md}\nResponse file: {response_path}\n> "
        )
        self.output.flush()
        response = self._read_response()
        response_path.write_text(response + "\n", encoding="utf-8")
        self.call_index += 1
        return response

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
    if config.provider == "gemini":
        return GeminiModel(config)
    if config.provider == "ollama":
        return OllamaModel(config)
    if config.provider == "manual_relay":
        return ManualRelayModel(config)
    if config.provider == "replay":
        if not config.replay_path:
            raise ValueError("model.replay_path is required for replay provider")
        return ReplayModel(config.replay_path)
    raise ValueError(f"unsupported model provider: {config.provider}")