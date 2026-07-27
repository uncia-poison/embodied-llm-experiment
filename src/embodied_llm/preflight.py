from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import httpx

from .config import ExperimentConfig


def _check(name: str, ok: bool, detail: str, required: bool = True) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "required": required, "detail": detail}


def _base_url(endpoint: str) -> str:
    parsed = urlsplit(endpoint)
    return urlunsplit((parsed.scheme, parsed.netloc, "", "", "")).rstrip("/")


def run_preflight(config: ExperimentConfig) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    try:
        config.validate()
        checks.append(_check("configuration", True, "configuration is internally consistent"))
    except Exception as exc:
        checks.append(_check("configuration", False, str(exc)))
        return {"ok": False, "checks": checks}

    output = Path(config.output_dir)
    try:
        output.mkdir(parents=True, exist_ok=True)
        probe = output / ".write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        checks.append(_check("output_directory", True, str(output.resolve())))
    except OSError as exc:
        checks.append(_check("output_directory", False, str(exc)))

    if config.drive.embedding_provider == "sentence_transformers":
        available = importlib.util.find_spec("sentence_transformers") is not None
        checks.append(
            _check(
                "sentence_transformers",
                available,
                "installed" if available else "install with: pip install -e .[semantic]",
            )
        )
    elif config.drive.embedding_provider == "openai_compatible":
        key_present = bool(os.getenv(config.drive.embedding_api_key_env, ""))
        checks.append(
            _check(
                "embedding_api_key",
                key_present,
                f"environment variable {config.drive.embedding_api_key_env} is "
                + ("set" if key_present else "not set"),
                required=False,
            )
        )

    provider = config.model.provider
    if provider == "replay":
        replay = Path(config.model.replay_path or "")
        checks.append(_check("replay_file", replay.is_file(), str(replay)))
    elif provider == "ollama":
        endpoint = f"{_base_url(config.model.endpoint)}/api/tags"
        try:
            response = httpx.get(endpoint, timeout=min(10.0, config.model.timeout_seconds))
            response.raise_for_status()
            data = response.json()
            names = {
                str(item.get("name", ""))
                for item in data.get("models", [])
                if isinstance(item, dict)
            }
            present = config.model.model in names or any(
                name.split(":", 1)[0] == config.model.model for name in names
            )
            checks.append(_check("ollama_endpoint", True, endpoint))
            checks.append(
                _check(
                    "ollama_model",
                    present,
                    f"{config.model.model}; available={sorted(names)}",
                )
            )
        except Exception as exc:
            checks.append(_check("ollama_endpoint", False, f"{endpoint}: {exc}"))
    elif provider == "openai_compatible":
        key_present = bool(os.getenv(config.model.api_key_env, ""))
        checks.append(
            _check(
                "model_api_key",
                key_present,
                f"environment variable {config.model.api_key_env} is "
                + ("set" if key_present else "not set"),
                required=False,
            )
        )
        checks.append(_check("model_endpoint", True, config.model.endpoint, required=False))
    else:
        checks.append(_check("model_provider", True, provider))

    required_failures = [item for item in checks if item["required"] and not item["ok"]]
    return {"ok": not required_failures, "checks": checks}
