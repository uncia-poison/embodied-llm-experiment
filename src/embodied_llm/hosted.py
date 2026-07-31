from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable, Iterable

import httpx

from .config import ExperimentConfig
from .experiment import ExperimentRunner
from .longitudinal import run_discovery, run_evaluation
from .models import LanguageModel, build_model
from .ownership import OwnershipPairRunner


def _http_error_detail(error: BaseException) -> str | None:
    """Recover a bounded provider response from a wrapped HTTP exception."""

    current: BaseException | None = error
    visited: set[int] = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        if isinstance(current, httpx.HTTPStatusError):
            response = current.response
            retry_after = response.headers.get("retry-after")
            body = response.text.strip().replace("\x00", "")
            if len(body) > 2000:
                body = body[:2000] + "…"
            parts = [f"status={response.status_code}"]
            if retry_after:
                parts.append(f"retry_after={retry_after}")
            if body:
                parts.append(f"response={body}")
            return "; ".join(parts)
        current = current.__cause__ or current.__context__
    return None


class PacedLanguageModel:
    """Enforce a minimum wall-clock interval between hosted model requests.

    Pacing changes only network timing. It does not alter simulator ticks, seeds, prompts,
    memory, actions or counterfactuals.
    """

    def __init__(
        self,
        delegate: LanguageModel,
        minimum_interval_seconds: float,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ):
        if minimum_interval_seconds < 0:
            raise ValueError("minimum_interval_seconds cannot be negative")
        self.delegate = delegate
        self.minimum_interval_seconds = float(minimum_interval_seconds)
        self.clock = clock
        self.sleeper = sleeper
        self.last_request_started_at: float | None = None

    def generate(self, messages, *, temperature=None, max_tokens=None) -> str:
        now = self.clock()
        if self.last_request_started_at is not None:
            remaining = self.minimum_interval_seconds - (now - self.last_request_started_at)
            if remaining > 0:
                self.sleeper(remaining)
        self.last_request_started_at = self.clock()
        try:
            return self.delegate.generate(
                messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:
            detail = _http_error_detail(exc)
            if detail is not None:
                raise RuntimeError(f"hosted model request failed: {detail}") from exc
            raise

    def reset_context(self) -> None:
        self.delegate.reset_context()


def _paced_model(config: ExperimentConfig, interval: float) -> LanguageModel:
    model: LanguageModel = build_model(config.model)
    return PacedLanguageModel(model, interval) if interval > 0 else model


def _write_policy(
    config: ExperimentConfig,
    *,
    minimum_request_interval_seconds: float,
    policy_output: str | Path | None,
    phase: str,
) -> None:
    if policy_output is None:
        return
    path = Path(policy_output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "provider": config.model.provider,
                "model": config.model.model,
                "phase": phase,
                "minimum_request_interval_seconds": float(
                    minimum_request_interval_seconds
                ),
                "scientific_effect": (
                    "network timing only; simulator ticks, seeds, prompts, memory, actions "
                    "and counterfactuals are unchanged"
                ),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def run_hosted_episode(
    config_path: str | Path,
    *,
    minimum_request_interval_seconds: float = 0.0,
    policy_output: str | Path | None = None,
) -> Path:
    config = ExperimentConfig.from_yaml(config_path)
    model = _paced_model(config, minimum_request_interval_seconds)
    _write_policy(
        config,
        minimum_request_interval_seconds=minimum_request_interval_seconds,
        policy_output=policy_output,
        phase="episode",
    )
    runner = (
        OwnershipPairRunner(config, model=model)
        if config.paradigm == "ownership_pair"
        else ExperimentRunner(config, model=model)
    )
    return runner.run()


def run_hosted_discovery(
    config_path: str | Path,
    *,
    checkpoint_out: str | Path,
    checkpoint_in: str | Path | None = None,
    checkpoint_every: int = 1,
    fresh_context: bool = False,
    minimum_request_interval_seconds: float = 0.0,
    policy_output: str | Path | None = None,
) -> dict:
    config = ExperimentConfig.from_yaml(config_path)
    model = _paced_model(config, minimum_request_interval_seconds)
    _write_policy(
        config,
        minimum_request_interval_seconds=minimum_request_interval_seconds,
        policy_output=policy_output,
        phase="discovery",
    )
    return run_discovery(
        config_path,
        checkpoint_in=checkpoint_in,
        checkpoint_out=checkpoint_out,
        checkpoint_every=checkpoint_every,
        fresh_context=fresh_context,
        model_factory=lambda _: model,
    )


def run_hosted_evaluation(
    config_path: str | Path,
    *,
    checkpoint_path: str | Path,
    output_dir: str | Path,
    variants: Iterable[str],
    unrelated_checkpoint_path: str | Path | None = None,
    shuffle_seed: int = 1701,
    minimum_request_interval_seconds: float = 0.0,
    policy_output: str | Path | None = None,
) -> dict:
    config = ExperimentConfig.from_yaml(config_path)
    shared_model = _paced_model(config, minimum_request_interval_seconds)
    _write_policy(
        config,
        minimum_request_interval_seconds=minimum_request_interval_seconds,
        policy_output=policy_output,
        phase="evaluation",
    )
    return run_evaluation(
        config_path,
        checkpoint_path=checkpoint_path,
        output_dir=output_dir,
        variants=variants,
        unrelated_checkpoint_path=unrelated_checkpoint_path,
        shuffle_seed=shuffle_seed,
        model_factory=lambda _: shared_model,
    )
