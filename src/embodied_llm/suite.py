from __future__ import annotations

import hashlib
import json
import math
import traceback
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev
from typing import Any

import yaml

from .config import ExperimentConfig
from .experiment import ExperimentRunner
from .ownership import OwnershipPairRunner
from .preflight import run_preflight


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    temporary.replace(path)


@dataclass(slots=True)
class SuiteCondition:
    name: str
    config_path: str


@dataclass(slots=True)
class RunSpec:
    condition: str
    seed: int
    replicate: int
    model_seed: int
    config_path: Path
    config: ExperimentConfig

    @property
    def key(self) -> str:
        return f"{self.condition}|{self.seed}|{self.replicate}"


class SuiteRunner:
    def __init__(
        self,
        suite_path: str | Path,
        *,
        resume: bool | None = None,
        continue_on_error: bool | None = None,
    ):
        self.suite_path = Path(suite_path)
        self.raw = yaml.safe_load(self.suite_path.read_text(encoding="utf-8")) or {}
        self.name = str(self.raw.get("name", self.suite_path.stem))
        self.seeds = [int(seed) for seed in self.raw.get("seeds", [42])]
        self.replicates = int(self.raw.get("replicates", 1))
        if self.replicates <= 0:
            raise ValueError("suite.replicates must be positive")
        self.conditions = [SuiteCondition(**item) for item in self.raw.get("conditions", [])]
        if not self.conditions:
            raise ValueError("suite must contain at least one condition")
        if len({item.name for item in self.conditions}) != len(self.conditions):
            raise ValueError("suite condition names must be unique")
        root = self.raw.get("output_dir", "suite-runs")
        self.output_dir = Path(root) / self.name
        self.resume = bool(self.raw.get("resume", True)) if resume is None else bool(resume)
        self.continue_on_error = (
            bool(self.raw.get("continue_on_error", True))
            if continue_on_error is None
            else bool(continue_on_error)
        )
        self.records_path = self.output_dir / "records.json"
        self.attempts_path = self.output_dir / "attempts.jsonl"
        self.aggregate_path = self.output_dir / "aggregate.json"
        self.progress_path = self.output_dir / "progress.json"
        self.manifest_path = self.output_dir / "suite_manifest.json"
        self.fingerprint, self.config_hashes = self._fingerprint()

    def _config_path(self, condition: SuiteCondition) -> Path:
        return (self.suite_path.parent / condition.config_path).resolve()

    def _fingerprint(self) -> tuple[str, dict[str, str]]:
        config_hashes: dict[str, str] = {}
        for condition in self.conditions:
            path = self._config_path(condition)
            config_hashes[condition.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        payload = {
            "suite": self.raw,
            "config_hashes": config_hashes,
        }
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest(), config_hashes

    def _manifest(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "suite": self.name,
            "fingerprint": self.fingerprint,
            "suite_path": str(self.suite_path.resolve()),
            "seeds": self.seeds,
            "replicates": self.replicates,
            "resume": self.resume,
            "continue_on_error": self.continue_on_error,
            "conditions": [
                {
                    "name": condition.name,
                    "config_path": condition.config_path,
                    "resolved_path": str(self._config_path(condition)),
                    "sha256": self.config_hashes[condition.name],
                }
                for condition in self.conditions
            ],
        }

    def _ensure_manifest(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.manifest_path.exists():
            existing = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            prior = existing.get("fingerprint")
            if prior != self.fingerprint:
                raise RuntimeError(
                    "suite definition or referenced config changed after output was created; "
                    "use a new suite name/output directory instead of mixing protocols"
                )
            return
        if self.records_path.exists() or self.attempts_path.exists():
            raise RuntimeError(
                "legacy suite output exists without suite_manifest.json; archive it or choose a new "
                "suite name before resuming"
            )
        _atomic_write_json(self.manifest_path, self._manifest())

    @staticmethod
    def _scheduled_count(ticks: int, warmup: int, every: int) -> int:
        if every <= 0:
            return 0
        return sum(1 for tick in range(ticks) if tick >= warmup and tick % every == 0)

    @classmethod
    def _estimate_calls(cls, config: ExperimentConfig) -> dict[str, int]:
        primary = config.ticks
        if config.paradigm == "ownership_pair":
            probe = cls._scheduled_count(
                config.ticks,
                config.ownership.probe_warmup_ticks,
                config.ownership.probe_every,
            )
            prediction = 0
            agency = 0
        elif config.probes.enabled:
            prediction = cls._scheduled_count(
                config.ticks, config.probes.warmup_ticks, config.probes.prediction_every
            )
            agency = cls._scheduled_count(
                config.ticks, config.probes.warmup_ticks, config.probes.agency_every
            )
            probe = prediction + agency
        else:
            prediction = 0
            agency = 0
            probe = 0
        total = primary + probe
        max_output_tokens = primary * config.model.max_tokens + probe * config.probes.max_probe_tokens
        return {
            "primary_calls": primary,
            "prediction_calls": prediction,
            "agency_calls": agency,
            "probe_calls": probe,
            "total_calls": total,
            "max_output_tokens": max_output_tokens,
        }

    def _specs(self) -> list[RunSpec]:
        specs: list[RunSpec] = []
        for condition in self.conditions:
            config_path = self._config_path(condition)
            base = ExperimentConfig.from_yaml(config_path)
            for seed in self.seeds:
                for replicate in range(self.replicates):
                    config = deepcopy(base)
                    config.seed = seed
                    config.model.seed = seed * 10_000 + replicate
                    config.name = f"{self.name}-{condition.name}-r{replicate + 1}"
                    config.output_dir = str(self.output_dir / "runs")
                    specs.append(
                        RunSpec(
                            condition=condition.name,
                            seed=seed,
                            replicate=replicate,
                            model_seed=int(config.model.seed),
                            config_path=config_path,
                            config=config,
                        )
                    )
        return specs

    def plan(self) -> dict[str, Any]:
        runs: list[dict[str, Any]] = []
        total_calls = 0
        total_max_output_tokens = 0
        for spec in self._specs():
            estimate = self._estimate_calls(spec.config)
            total_calls += estimate["total_calls"]
            total_max_output_tokens += estimate["max_output_tokens"]
            runs.append(
                {
                    "key": spec.key,
                    "condition": spec.condition,
                    "seed": spec.seed,
                    "replicate": spec.replicate,
                    "model_seed": spec.model_seed,
                    "config": str(spec.config_path),
                    "paradigm": spec.config.paradigm,
                    "ticks": spec.config.ticks,
                    "provider": spec.config.model.provider,
                    "model": spec.config.model.model,
                    "estimate": estimate,
                }
            )
        return {
            "schema_version": 1,
            "suite": self.name,
            "fingerprint": self.fingerprint,
            "output_dir": str(self.output_dir),
            "total_runs": len(runs),
            "estimated_model_calls": total_calls,
            "max_output_tokens_upper_bound": total_max_output_tokens,
            "runs": runs,
        }

    def preflight(self) -> dict[str, Any]:
        reports: list[dict[str, Any]] = []
        for condition in self.conditions:
            path = self._config_path(condition)
            config = ExperimentConfig.from_yaml(path)
            report = run_preflight(config)
            reports.append(
                {
                    "condition": condition.name,
                    "config": str(path),
                    "ok": bool(report["ok"]),
                    "checks": report["checks"],
                }
            )
        return {
            "suite": self.name,
            "fingerprint": self.fingerprint,
            "ok": all(item["ok"] for item in reports),
            "conditions": reports,
        }

    def _load_records(self) -> list[dict[str, Any]]:
        if not self.records_path.exists():
            return []
        raw = json.loads(self.records_path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            return raw
        if raw.get("fingerprint") != self.fingerprint:
            raise RuntimeError("records fingerprint does not match current suite definition")
        return list(raw.get("records", []))

    @staticmethod
    def _numeric_items(summary: dict[str, Any]) -> dict[str, float]:
        result: dict[str, float] = {}
        for key, value in summary.items():
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)) and math.isfinite(float(value)):
                result[key] = float(value)
        return result

    @staticmethod
    def _aggregate_metric(values: list[float]) -> dict[str, float | None]:
        return {
            "n": float(len(values)),
            "mean": mean(values) if values else None,
            "stdev": stdev(values) if len(values) > 1 else 0.0 if values else None,
        }

    def _aggregate(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        successful = [record for record in records if record.get("status") == "success"]
        failed = [record for record in records if record.get("status") == "failed"]
        aggregate: dict[str, Any] = {
            "schema_version": 2,
            "suite": self.name,
            "fingerprint": self.fingerprint,
            "seeds": self.seeds,
            "replicates": self.replicates,
            "successful_runs": len(successful),
            "failed_runs": len(failed),
            "conditions": {},
            "paired_contrasts": {},
        }
        for condition in self.conditions:
            selected = [
                record
                for record in successful
                if record["condition"] == condition.name and isinstance(record.get("summary"), dict)
            ]
            metric_names = sorted(
                set().union(
                    *(self._numeric_items(record["summary"]).keys() for record in selected)
                )
            ) if selected else []
            metrics: dict[str, dict[str, float | None]] = {}
            for metric in metric_names:
                values = [
                    self._numeric_items(record["summary"])[metric]
                    for record in selected
                    if metric in self._numeric_items(record["summary"])
                ]
                metrics[metric] = self._aggregate_metric(values)
            aggregate["conditions"][condition.name] = {
                "config": condition.config_path,
                "successful_runs": len(selected),
                "failed_runs": sum(
                    1 for record in failed if record["condition"] == condition.name
                ),
                "metrics": metrics,
            }

        by_condition = {
            condition.name: {
                (record["seed"], record["replicate"]): record
                for record in successful
                if record["condition"] == condition.name
                and isinstance(record.get("summary"), dict)
            }
            for condition in self.conditions
        }
        for left_index, left in enumerate(self.conditions):
            for right in self.conditions[left_index + 1 :]:
                common = sorted(set(by_condition[left.name]) & set(by_condition[right.name]))
                metric_differences: dict[str, list[float]] = {}
                for key in common:
                    left_metrics = self._numeric_items(by_condition[left.name][key]["summary"])
                    right_metrics = self._numeric_items(by_condition[right.name][key]["summary"])
                    for metric in set(left_metrics) & set(right_metrics):
                        metric_differences.setdefault(metric, []).append(
                            left_metrics[metric] - right_metrics[metric]
                        )
                aggregate["paired_contrasts"][f"{left.name}-minus-{right.name}"] = {
                    "matched_runs": len(common),
                    "metrics": {
                        metric: self._aggregate_metric(values)
                        for metric, values in sorted(metric_differences.items())
                    },
                }
        return aggregate

    @staticmethod
    def _record_key(record: dict[str, Any]) -> str:
        return f"{record['condition']}|{record['seed']}|{record['replicate']}"

    def _append_attempt(self, record: dict[str, Any]) -> None:
        self.attempts_path.parent.mkdir(parents=True, exist_ok=True)
        with self.attempts_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def _write_state(
        self,
        records_by_key: dict[str, dict[str, Any]],
        *,
        current: str | None,
        status: str,
    ) -> None:
        ordered = [records_by_key[key] for key in sorted(records_by_key)]
        successful = sum(record.get("status") == "success" for record in ordered)
        failed = sum(record.get("status") == "failed" for record in ordered)
        total = len(self._specs())
        _atomic_write_json(
            self.records_path,
            {
                "schema_version": 2,
                "suite": self.name,
                "fingerprint": self.fingerprint,
                "records": ordered,
            },
        )
        _atomic_write_json(self.aggregate_path, self._aggregate(ordered))
        _atomic_write_json(
            self.progress_path,
            {
                "schema_version": 1,
                "suite": self.name,
                "fingerprint": self.fingerprint,
                "status": status,
                "current": current,
                "total_runs": total,
                "successful_runs": successful,
                "failed_runs": failed,
                "remaining_runs": max(0, total - successful),
                "updated_at": _utc_now(),
            },
        )

    def run(self) -> Path:
        self._ensure_manifest()
        records = self._load_records()
        records_by_key = {self._record_key(record): record for record in records}
        self._write_state(records_by_key, current=None, status="running")

        for spec in self._specs():
            previous = records_by_key.get(spec.key)
            if self.resume and previous and previous.get("status") == "success":
                continue

            attempt = int(previous.get("attempt", 0)) + 1 if previous else 1
            started_at = _utc_now()
            self._write_state(records_by_key, current=spec.key, status="running")
            runner = None
            try:
                runner = (
                    OwnershipPairRunner(spec.config)
                    if spec.config.paradigm == "ownership_pair"
                    else ExperimentRunner(spec.config)
                )
                run_dir = runner.run()
                summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
                record = {
                    "status": "success",
                    "condition": spec.condition,
                    "seed": spec.seed,
                    "replicate": spec.replicate,
                    "model_seed": spec.model_seed,
                    "attempt": attempt,
                    "config": str(spec.config_path),
                    "run_dir": str(run_dir.resolve()),
                    "started_at": started_at,
                    "finished_at": _utc_now(),
                    "summary": summary,
                }
            except Exception as exc:
                record = {
                    "status": "failed",
                    "condition": spec.condition,
                    "seed": spec.seed,
                    "replicate": spec.replicate,
                    "model_seed": spec.model_seed,
                    "attempt": attempt,
                    "config": str(spec.config_path),
                    "run_dir": (
                        str(runner.logger.run_dir.resolve())
                        if runner is not None
                        else None
                    ),
                    "started_at": started_at,
                    "finished_at": _utc_now(),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                    "summary": None,
                }
                records_by_key[spec.key] = record
                self._append_attempt(record)
                self._write_state(records_by_key, current=spec.key, status="running")
                if not self.continue_on_error:
                    self._write_state(records_by_key, current=spec.key, status="failed")
                    raise
                continue

            records_by_key[spec.key] = record
            self._append_attempt(record)
            self._write_state(records_by_key, current=spec.key, status="running")

        failures = sum(record.get("status") == "failed" for record in records_by_key.values())
        final_status = "completed" if failures == 0 else "completed_with_failures"
        self._write_state(records_by_key, current=None, status=final_status)
        return self.output_dir
