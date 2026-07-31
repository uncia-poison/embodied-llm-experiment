from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

from .config import ExperimentConfig
from .experiment import ExperimentRunner
from .models import LanguageModel, build_model
from .ownership import OwnershipPairRunner


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
        return self.delegate.generate(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def reset_context(self) -> None:
        self.delegate.reset_context()


def run_hosted_episode(
    config_path: str | Path,
    *,
    minimum_request_interval_seconds: float = 0.0,
    policy_output: str | Path | None = None,
) -> Path:
    config = ExperimentConfig.from_yaml(config_path)
    model: LanguageModel = build_model(config.model)
    if minimum_request_interval_seconds > 0:
        model = PacedLanguageModel(model, minimum_request_interval_seconds)

    if policy_output is not None:
        path = Path(policy_output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "provider": config.model.provider,
                    "model": config.model.model,
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

    runner = (
        OwnershipPairRunner(config, model=model)
        if config.paradigm == "ownership_pair"
        else ExperimentRunner(config, model=model)
    )
    return runner.run()
