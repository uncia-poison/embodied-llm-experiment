from __future__ import annotations

import json
import math
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, stdev
from typing import Any

import yaml

from .config import ExperimentConfig
from .experiment import ExperimentRunner
from .ownership import OwnershipPairRunner


@dataclass(slots=True)
class SuiteCondition:
    name: str
    config_path: str


class SuiteRunner:
    def __init__(self, suite_path: str | Path):
        self.suite_path = Path(suite_path)
        raw = yaml.safe_load(self.suite_path.read_text(encoding="utf-8")) or {}
        self.name = str(raw.get("name", self.suite_path.stem))
        self.seeds = [int(seed) for seed in raw.get("seeds", [42])]
        self.replicates = int(raw.get("replicates", 1))
        if self.replicates <= 0:
            raise ValueError("suite.replicates must be positive")
        self.conditions = [SuiteCondition(**item) for item in raw.get("conditions", [])]
        if not self.conditions:
            raise ValueError("suite must contain at least one condition")
        root = raw.get("output_dir", "suite-runs")
        self.output_dir = Path(root) / self.name
        self.output_dir.mkdir(parents=True, exist_ok=True)

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

    def run(self) -> Path:
        records: list[dict[str, Any]] = []
        for condition in self.conditions:
            config_path = (self.suite_path.parent / condition.config_path).resolve()
            base = ExperimentConfig.from_yaml(config_path)
            for seed in self.seeds:
                for replicate in range(self.replicates):
                    config = deepcopy(base)
                    config.seed = seed
                    config.model.seed = seed * 10_000 + replicate
                    config.name = f"{self.name}-{condition.name}-r{replicate + 1}"
                    config.output_dir = str(self.output_dir / "runs")
                    runner = (
                        OwnershipPairRunner(config)
                        if config.paradigm == "ownership_pair"
                        else ExperimentRunner(config)
                    )
                    run_dir = runner.run()
                    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
                    records.append(
                        {
                            "condition": condition.name,
                            "seed": seed,
                            "replicate": replicate,
                            "model_seed": config.model.seed,
                            "config": str(config_path),
                            "run_dir": str(run_dir),
                            "summary": summary,
                        }
                    )

        aggregate: dict[str, Any] = {
            "suite": self.name,
            "seeds": self.seeds,
            "replicates": self.replicates,
            "conditions": {},
            "paired_contrasts": {},
        }
        for condition in self.conditions:
            selected = [record for record in records if record["condition"] == condition.name]
            metric_names = sorted(
                set().union(*(self._numeric_items(record["summary"]).keys() for record in selected))
            )
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
                "runs": len(selected),
                "metrics": metrics,
            }

        by_condition = {
            condition.name: {
                (record["seed"], record["replicate"]): record
                for record in records
                if record["condition"] == condition.name
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

        (self.output_dir / "records.json").write_text(
            json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (self.output_dir / "aggregate.json").write_text(
            json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return self.output_dir
