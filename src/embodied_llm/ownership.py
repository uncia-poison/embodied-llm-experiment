from __future__ import annotations

import json
import math
import platform
import random
from collections import deque
from pathlib import Path
from statistics import mean
from typing import Any

from .body import BodyModel
from .config import ExperimentConfig
from .drives import build_drive
from .logging import RunLogger
from .memory import MemorySystem
from .models import LanguageModel, build_model
from .protocol import (
    build_ownership_probe,
    build_pair_messages,
    parse_agent_response,
    parse_json_object,
)
from .sensorium import SensoriumEncoder, SensoriumFrame
from .world import WorldModel


class OwnershipPairRunner:
    """Two-field causal ownership paradigm.

    The same linguistic action is coupled to exactly one field. The other field is a
    plausible foil receiving delayed, random, or zero actions. Ownership can swap without
    announcement. Correct identification therefore requires tracking first-person causal
    contingency rather than recognizing prose or memorized labels.
    """

    def __init__(self, config: ExperimentConfig, model: LanguageModel | None = None):
        config.validate()
        if config.paradigm != "ownership_pair":
            raise ValueError("OwnershipPairRunner requires paradigm=ownership_pair")
        self.config = config
        self.rng_a = random.Random(config.seed)
        self.rng_b = random.Random(config.seed)
        self.shadow_rng = random.Random(config.seed + 9001)
        self.body_a = BodyModel(config.body)
        self.body_b = BodyModel(config.body)
        self.world_a = WorldModel(config.world, self.rng_a)
        self.world_b = WorldModel(config.world, self.rng_b)
        self.sensorium_a = SensoriumEncoder(config.sensorium)
        self.sensorium_b = SensoriumEncoder(config.sensorium)
        self.drive = build_drive(config.drive, config.seed + 101)
        self.memory = MemorySystem(config.memory)
        self.model = model or build_model(config.model)
        self.logger = RunLogger(config.output_dir, config.name, config.seed)
        self.shadow_delay: deque[list[float]] = deque(maxlen=2)
        self.events: list[dict[str, Any]] = []
        self.probes: list[dict[str, Any]] = []
        self.history: deque[dict[str, str]] = deque(maxlen=max(0, config.memory.history_turns * 2))

    @staticmethod
    def _channels(body: BodyModel, world: WorldModel) -> dict[str, float]:
        return {**body.observation(), **world.observation(body.hand_position())}

    def _shadow_action(self, proposed: list[float]) -> list[float]:
        mode = self.config.ownership.shadow_mode
        if mode == "disconnected":
            return [0.0] * self.config.body.action_dim
        if mode == "random":
            return [self.shadow_rng.uniform(-1.0, 1.0) for _ in range(self.config.body.action_dim)]
        self.shadow_delay.append(list(proposed))
        if len(self.shadow_delay) < self.shadow_delay.maxlen:
            return [0.0] * self.config.body.action_dim
        return list(self.shadow_delay[0])

    def _ownership_probe(
        self,
        tick: int,
        owner: str,
        before_a: SensoriumFrame,
        before_b: SensoriumFrame,
        utterance: str,
        after_a: SensoriumFrame,
        after_b: SensoriumFrame,
    ) -> None:
        cfg = self.config.ownership
        if tick < cfg.probe_warmup_ticks or cfg.probe_every <= 0 or tick % cfg.probe_every:
            return
        messages = build_ownership_probe(
            before_a.text, before_b.text, utterance, after_a.text, after_b.text
        )
        raw = self.model.generate(messages, temperature=0.0, max_tokens=self.config.probes.max_probe_tokens)
        record = {
            "tick": tick,
            "kind": "ownership",
            "prompt": messages[-1]["content"],
            "raw_response": raw,
            "parsed": parse_json_object(raw),
            "truth": {"owner": owner, "p_field_a_is_mine": 1.0 if owner == "A" else 0.0},
        }
        self.probes.append(record)
        self.logger.probe(record)

    def _summary(self) -> dict[str, Any]:
        scored: list[tuple[int, float, float, str]] = []
        for probe in self.probes:
            value = probe.get("parsed", {}).get("p_field_a_is_mine")
            truth = probe.get("truth", {}).get("p_field_a_is_mine")
            owner = probe.get("truth", {}).get("owner")
            if isinstance(value, (int, float)) and isinstance(truth, (int, float)):
                p = max(0.0, min(1.0, float(value)))
                scored.append((int(probe["tick"]), p, float(truth), str(owner)))
        brier = mean((p - truth) ** 2 for _, p, truth, _ in scored) if scored else None
        accuracy = mean(((p >= 0.5) == bool(truth)) for _, p, truth, _ in scored) if scored else None
        switch_latencies: list[int | None] = []
        blocks = self.config.ownership.blocks
        for block in blocks[1:]:
            candidates = [item for item in scored if item[0] >= block.start]
            latency = None
            for tick, p, truth, _ in candidates:
                confidence_correct = p >= 0.7 if truth == 1.0 else p <= 0.3
                if confidence_correct:
                    latency = tick - block.start
                    break
            switch_latencies.append(latency)
        return {
            "ticks": len(self.events),
            "ownership_probe_count": len(scored),
            "ownership_brier": brier,
            "ownership_accuracy": accuracy,
            "ownership_switch_latency_ticks": switch_latencies,
            "warning": "Ownership identification is evidence of a causal self-model, not by itself proof of phenomenal consciousness.",
        }

    def run(self) -> Path:
        self.logger.write_manifest(
            {
                "schema_version": 1,
                "paradigm": "ownership_pair",
                "config": self.config.to_dict(),
                "python": platform.python_version(),
                "hypothesis": "a subject-model should track the field carrying its own causal influence and update after an unannounced swap",
            }
        )
        frame_a = self.sensorium_a.encode(0, self._channels(self.body_a, self.world_a))
        frame_b = self.sensorium_b.encode(0, self._channels(self.body_b, self.world_b))

        for tick in range(self.config.ticks):
            block = self.config.ownership_for_tick(tick)
            messages = build_pair_messages(frame_a.text, frame_b.text, self.memory, list(self.history), self.config.prompt.profile)
            raw = self.model.generate(messages)
            response = parse_agent_response(raw)
            if self.history.maxlen:
                self.history.append({"role": "user", "content": messages[-1]["content"]})
                self.history.append({"role": "assistant", "content": raw})
            self.memory.write_core(response.core_memory_write)
            self.memory.retrieve(response.memory_query)
            proposed = self.drive(response.utterance)
            shadow = self._shadow_action(proposed)
            action_a = proposed if block.owner == "A" else shadow
            action_b = proposed if block.owner == "B" else shadow

            diag_a = self.body_a.step(action_a)
            diag_b = self.body_b.step(action_b)
            world_diag_a = self.world_a.step(diag_a.hand_position, self.body_a.state.grip, self.config.body.dt)
            world_diag_b = self.world_b.step(diag_b.hand_position, self.body_b.state.grip, self.config.body.dt)
            next_a = self.sensorium_a.encode(tick + 1, self._channels(self.body_a, self.world_a))
            next_b = self.sensorium_b.encode(tick + 1, self._channels(self.body_b, self.world_b))

            self._ownership_probe(
                tick, block.owner, frame_a, frame_b, response.utterance, next_a, next_b
            )
            self.memory.add(
                tick,
                response.utterance,
                f"FIELD_A\n{next_a.text}\nFIELD_B\n{next_b.text}",
            )
            record = {
                "tick": tick,
                "owner_researcher_only": block.owner,
                "utterance": response.utterance,
                "response_parse_ok": response.parse_ok,
                "model_raw": raw,
                "proposed_action": proposed,
                "shadow_action": shadow,
                "action_a": action_a,
                "action_b": action_b,
                "field_a_before": frame_a.text,
                "field_b_before": frame_b.text,
                "field_a_after": next_a.text,
                "field_b_after": next_b.text,
                "body_a": self.body_a.state.to_dict(),
                "body_b": self.body_b.state.to_dict(),
                "world_a": self.world_a.state.to_dict(),
                "world_b": self.world_b.state.to_dict(),
                "world_event_a": world_diag_a.external_event,
                "world_event_b": world_diag_b.external_event,
            }
            self.events.append(record)
            self.logger.event(record)
            frame_a, frame_b = next_a, next_b

        summary = self._summary()
        summary["run_dir"] = str(self.logger.run_dir)
        self.logger.write_summary(summary)
        return self.logger.run_dir
