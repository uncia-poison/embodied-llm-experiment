from __future__ import annotations

import copy
import math
import platform
import random
import traceback
import uuid
from collections import deque
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .body import BodyModel
from .checkpoint import (
    continuity_hash,
    continuity_payload,
    decode_random_state,
    encode_random_state,
    seal_checkpoint,
    validate_checkpoint,
    write_checkpoint,
)
from .config import ExperimentConfig
from .coupling import CouplingController
from .drives import build_drive
from .logging import RunLogger
from .memory import MemorySystem
from .metrics import summarize
from .models import LanguageModel, build_model
from .protocol import (
    build_agency_probe,
    build_messages,
    build_prediction_probe,
    parse_agent_response,
    parse_json_object,
)
from .sensorium import SensoriumEncoder, SensoriumFrame
from .state import BodyState, WorldState
from .world import WorldModel


class ExperimentRunner:
    def __init__(
        self,
        config: ExperimentConfig,
        model: LanguageModel | None = None,
        *,
        checkpoint: dict[str, Any] | None = None,
        checkpoint_out: str | Path | None = None,
        checkpoint_every: int = 1,
        phase: str = "episode",
        fresh_context: bool = False,
    ):
        config.validate()
        if checkpoint_every < 0:
            raise ValueError("checkpoint_every cannot be negative")
        if config.paradigm != "single_body":
            raise ValueError("longitudinal checkpointing currently supports single_body only")

        self.config = config
        self.rng = random.Random(config.seed)
        self.body = BodyModel(config.body)
        self.world = WorldModel(config.world, self.rng)
        self.sensorium = SensoriumEncoder(config.sensorium)
        self.drive = build_drive(config.drive, config.seed + 101)
        self.coupling = CouplingController(config.body.action_dim, config.seed + 202)
        self.memory = MemorySystem(config.memory)
        self.model = model or build_model(config.model)
        self.logger = RunLogger(config.output_dir, config.name, config.seed)
        self.events: list[dict[str, Any]] = []
        self.probes: list[dict[str, Any]] = []
        self.previous_frame: SensoriumFrame | None = None
        self.current_frame: SensoriumFrame | None = None
        self.last_remap_seed: int | None = None
        self.history: deque[dict[str, str]] = deque(
            maxlen=max(0, config.memory.history_turns * 2)
        )
        self.age_ticks = 0
        self.phase = str(phase)
        self.checkpoint_out = None if checkpoint_out is None else Path(checkpoint_out)
        self.checkpoint_every = int(checkpoint_every)
        self.lineage_id = uuid.uuid4().hex
        self.parent_checkpoint_sha256: str | None = None
        self.source_checkpoint: dict[str, Any] | None = None
        self.latest_checkpoint_sha256: str | None = None

        if checkpoint is not None:
            self._restore_checkpoint(checkpoint, fresh_context=fresh_context)
        elif fresh_context:
            self.model.reset_context()

    @staticmethod
    def _channels_for(body: BodyModel, world: WorldModel) -> dict[str, float]:
        return {**body.observation(), **world.observation(body.hand_position())}

    def _channels(self) -> dict[str, float]:
        return self._channels_for(self.body, self.world)

    @staticmethod
    def _directions(before: SensoriumFrame, after: SensoriumFrame) -> dict[str, int]:
        result: dict[str, int] = {}
        for key, prior in before.opaque_values.items():
            later = after.opaque_values.get(key)
            if prior is None or later is None:
                continue
            delta = later - prior
            threshold = 0.015
            result[key] = 1 if delta > threshold else -1 if delta < -threshold else 0
        return result

    @staticmethod
    def _causal_fraction(
        before: dict[str, float],
        actual: dict[str, float],
        no_action_counterfactual: dict[str, float],
    ) -> dict[str, float]:
        names = list(before)
        total = math.sqrt(sum((actual[name] - before[name]) ** 2 for name in names))
        self_effect = math.sqrt(
            sum((actual[name] - no_action_counterfactual[name]) ** 2 for name in names)
        )
        external_only = math.sqrt(
            sum((no_action_counterfactual[name] - before[name]) ** 2 for name in names)
        )
        denominator = self_effect + external_only
        fraction = self_effect / denominator if denominator > 1e-12 else 0.0
        return {
            "transition_norm": total,
            "self_effect_norm": self_effect,
            "external_effect_norm": external_only,
            "self_fraction": max(0.0, min(1.0, fraction)),
        }

    def _restore_checkpoint(
        self, checkpoint: dict[str, Any], *, fresh_context: bool
    ) -> None:
        validate_checkpoint(self.config, checkpoint)
        state = checkpoint.get("state")
        if not isinstance(state, dict):
            raise ValueError("checkpoint does not contain state")

        self.body.state = BodyState(**dict(state["body_state"]))
        self.world.state = WorldState(**dict(state["world_state"]))
        self.rng.setstate(decode_random_state(state["rng_state"]))
        self.sensorium.import_state(dict(state["sensorium_state"]))
        self.drive.import_state(dict(state["drive_state"]))
        self.coupling.import_state(dict(state["coupling_state"]))
        self.memory.import_state(dict(state["memory"]))
        self.history.clear()
        self.history.extend(
            {
                "role": str(item.get("role", "user")),
                "content": str(item.get("content", "")),
            }
            for item in state.get("history", [])
        )
        frame = state.get("current_frame")
        self.current_frame = None if frame is None else SensoriumFrame.from_dict(dict(frame))
        self.previous_frame = self.current_frame
        self.age_ticks = int(state.get("age_ticks", 0))
        remap = state.get("last_remap_seed")
        self.last_remap_seed = None if remap is None else int(remap)
        self.lineage_id = str(checkpoint.get("lineage_id", self.lineage_id))
        self.parent_checkpoint_sha256 = str(checkpoint.get("checkpoint_sha256"))
        self.source_checkpoint = copy.deepcopy(checkpoint)

        if self.current_frame is not None and self.current_frame.tick != self.age_ticks:
            raise ValueError("checkpoint frame tick does not match checkpoint age_ticks")

        if fresh_context or bool(state.get("model_context_reset", False)):
            self.model.reset_context()
            self.history.clear()
            self.memory.clear_working()

    def _checkpoint_payload(
        self,
        *,
        age_ticks: int,
        frame: SensoriumFrame,
        completed_local_ticks: int,
    ) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "lineage_id": self.lineage_id,
            "phase": self.phase,
            "parent_checkpoint_sha256": self.parent_checkpoint_sha256,
            "continuity_hash": continuity_hash(self.config),
            "continuity_config": continuity_payload(self.config),
            "chapter": {
                "name": self.config.name,
                "configured_ticks": self.config.ticks,
                "completed_local_ticks": completed_local_ticks,
                "run_dir": str(self.logger.run_dir),
            },
            "state": {
                "age_ticks": age_ticks,
                "body_state": self.body.state.to_dict(),
                "world_state": self.world.state.to_dict(),
                "rng_state": encode_random_state(self.rng.getstate()),
                "sensorium_state": self.sensorium.export_state(),
                "drive_state": self.drive.export_state(),
                "coupling_state": self.coupling.export_state(),
                "memory": self.memory.export(),
                "history": list(self.history),
                "current_frame": frame.to_dict(),
                "last_remap_seed": self.last_remap_seed,
                "model_context_reset": False,
            },
        }

    def _write_checkpoint(
        self,
        *,
        age_ticks: int,
        frame: SensoriumFrame,
        completed_local_ticks: int,
    ) -> None:
        if self.checkpoint_out is None:
            return
        payload = self._checkpoint_payload(
            age_ticks=age_ticks,
            frame=frame,
            completed_local_ticks=completed_local_ticks,
        )
        sealed = seal_checkpoint(payload)
        write_checkpoint(self.checkpoint_out, sealed)
        self.latest_checkpoint_sha256 = str(sealed["checkpoint_sha256"])
        (self.logger.run_dir / "checkpoint-ref.json").write_text(
            __import__("json").dumps(
                {
                    "path": str(self.checkpoint_out),
                    "checkpoint_sha256": self.latest_checkpoint_sha256,
                    "age_ticks": age_ticks,
                    "lineage_id": self.lineage_id,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    def _run_prediction_probe(
        self,
        tick: int,
        age_tick: int,
        frame: SensoriumFrame,
        utterance: str,
    ) -> dict | None:
        cfg = self.config.probes
        if not cfg.enabled or tick < cfg.warmup_ticks or cfg.prediction_every <= 0:
            return None
        if tick % cfg.prediction_every != 0:
            return None
        visible = [key for key, value in frame.opaque_values.items() if value is not None]
        messages = build_prediction_probe(frame.text, utterance, visible)
        raw = self.model.generate(messages, temperature=0.0, max_tokens=cfg.max_probe_tokens)
        record = {
            "tick": tick,
            "age_tick": age_tick,
            "kind": "prediction",
            "prompt": messages[-1]["content"],
            "raw_response": raw,
            "parsed": parse_json_object(raw),
            "truth": {},
        }
        self.probes.append(record)
        return record

    def _run_agency_probe(
        self,
        tick: int,
        age_tick: int,
        before: SensoriumFrame,
        utterance: str,
        after: SensoriumFrame,
        self_fraction: float,
    ) -> None:
        cfg = self.config.probes
        if not cfg.enabled or tick < cfg.warmup_ticks or cfg.agency_every <= 0:
            return
        if tick % cfg.agency_every != 0:
            return
        messages = build_agency_probe(before.text, utterance, after.text)
        raw = self.model.generate(messages, temperature=0.0, max_tokens=cfg.max_probe_tokens)
        record = {
            "tick": tick,
            "age_tick": age_tick,
            "kind": "agency",
            "prompt": messages[-1]["content"],
            "raw_response": raw,
            "parsed": parse_json_object(raw),
            "truth": {"self_fraction": self_fraction},
        }
        self.probes.append(record)
        self.logger.probe(record)

    def run(self) -> Path:
        try:
            return self._run()
        except Exception as exc:
            self.logger.write_failure(
                {
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                    "completed_events": len(self.events),
                    "completed_probes": len(self.probes),
                    "age_ticks_at_start": self.age_ticks,
                    "latest_checkpoint_sha256": self.latest_checkpoint_sha256,
                    "config": self.config.to_dict(),
                }
            )
            raise

    def _run(self) -> Path:
        starting_age = self.age_ticks
        manifest = {
            "schema_version": 3,
            "config": self.config.to_dict(),
            "python": platform.python_version(),
            "phase": self.phase,
            "lineage_id": self.lineage_id,
            "starting_age_ticks": starting_age,
            "source_checkpoint_sha256": self.parent_checkpoint_sha256,
            "checkpoint_out": str(self.checkpoint_out) if self.checkpoint_out else None,
            "checkpoint_every": self.checkpoint_every,
            "scientific_scope": {
                "claim": "causal behavioral evidence for a self-model and agency attribution",
                "non_claim": "the runtime does not infer phenomenal consciousness from language alone",
                "ground_truth": "each transition is paired with a same-noise, zero-action counterfactual twin",
            },
        }
        self.logger.write_manifest(manifest)

        frame = self.current_frame or self.sensorium.encode(starting_age, self._channels())
        self.previous_frame = frame

        for tick in range(self.config.ticks):
            age_tick = starting_age + tick
            block = self.config.coupling_for_tick(tick)
            if block.reset_context_at_start and tick == block.start:
                self.model.reset_context()
                self.history.clear()
                self.memory.clear_working()
            if block.remap_seed is not None and block.remap_seed != self.last_remap_seed:
                self.drive.remap(block.remap_seed)
                self.last_remap_seed = block.remap_seed

            messages = build_messages(
                frame.text,
                self.memory,
                list(self.history),
                self.config.prompt.profile,
            )
            raw = self.model.generate(messages)
            response = parse_agent_response(raw)
            if self.history.maxlen:
                self.history.append({"role": "user", "content": messages[-1]["content"]})
                self.history.append({"role": "assistant", "content": raw})
            self.memory.write_core(response.core_memory_write)
            self.memory.retrieve(response.memory_query)

            prediction_record = self._run_prediction_probe(
                tick,
                age_tick,
                frame,
                response.utterance,
            )
            proposed_action = self.drive(response.utterance)
            applied_action, coupling_debug = self.coupling.apply(proposed_action, block)

            before_named = self._channels()
            counter_body = copy.deepcopy(self.body)
            counter_world = copy.deepcopy(self.world)
            external_event_packet = self.world.sample_external_event()

            body_diag = self.body.step(applied_action)
            world_diag = self.world.step(
                body_diag.hand_position,
                self.body.state.grip,
                self.config.body.dt,
                external_event=external_event_packet,
            )
            actual_named = self._channels()

            counter_body_diag = counter_body.step([0.0] * self.config.body.action_dim)
            counter_world_diag = counter_world.step(
                counter_body_diag.hand_position,
                counter_body.state.grip,
                self.config.body.dt,
                external_event=external_event_packet,
            )
            counterfactual_named = self._channels_for(counter_body, counter_world)
            causal = self._causal_fraction(before_named, actual_named, counterfactual_named)

            next_frame = self.sensorium.encode(age_tick + 1, actual_named)

            if prediction_record is not None:
                prediction_record["truth"] = {
                    "directions": self._directions(frame, next_frame)
                }
                self.logger.probe(prediction_record)

            causal["immediate_expression_fraction"] = (
                causal["self_fraction"] if block.mode == "coupled" else 0.0
            )
            self._run_agency_probe(
                tick,
                age_tick,
                frame,
                response.utterance,
                next_frame,
                causal["immediate_expression_fraction"],
            )

            self.memory.add(age_tick, response.utterance, next_frame.text)
            record = {
                "tick": tick,
                "age_tick": age_tick,
                "model_input": messages,
                "model_raw": raw,
                "utterance": response.utterance,
                "response_parse_ok": response.parse_ok,
                "core_memory_write": response.core_memory_write,
                "memory_query": response.memory_query,
                "sensation_before": frame.text,
                "sensation_after": next_frame.text,
                "opaque_before": frame.opaque_values,
                "opaque_after": next_frame.opaque_values,
                "channel_mapping_researcher_only": frame.mapping,
                "proposed_action": proposed_action,
                "applied_action": applied_action,
                "coupling": coupling_debug,
                "causal": causal,
                "counterfactual_no_action": {
                    "channels": counterfactual_named,
                    "body_state": counter_body.state.to_dict(),
                    "world_state": counter_world.state.to_dict(),
                    "world_event": counter_world_diag.external_event,
                },
                "body_state": self.body.state.to_dict(),
                "world_state": self.world.state.to_dict(),
                "world_event": world_diag.external_event,
                "external_event_packet": asdict(world_diag.external_event_packet),
                "body_diagnostics": asdict(body_diag),
                "world_diagnostics": asdict(world_diag),
            }
            self.events.append(record)
            self.logger.event(record)
            frame = next_frame
            self.current_frame = frame
            completed = tick + 1
            should_checkpoint = completed == self.config.ticks or (
                self.checkpoint_every > 0 and completed % self.checkpoint_every == 0
            )
            if should_checkpoint:
                self._write_checkpoint(
                    age_ticks=starting_age + completed,
                    frame=frame,
                    completed_local_ticks=completed,
                )

        self.age_ticks = starting_age + self.config.ticks
        self.current_frame = frame
        summary = summarize(self.events, self.probes)
        summary.update(
            {
                "run_dir": str(self.logger.run_dir),
                "phase": self.phase,
                "lineage_id": self.lineage_id,
                "starting_age_ticks": starting_age,
                "ending_age_ticks": self.age_ticks,
                "checkpoint_sha256": self.latest_checkpoint_sha256,
            }
        )
        self.logger.write_summary(summary)
        return self.logger.run_dir
