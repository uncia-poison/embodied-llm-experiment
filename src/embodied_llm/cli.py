from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import ExperimentConfig
from .experiment import ExperimentRunner
from .ownership import OwnershipPairRunner
from .suite import SuiteRunner
from .metrics import summarize
from .preflight import run_preflight


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def run_command(config_path: str) -> int:
    config = ExperimentConfig.from_yaml(config_path)
    runner = OwnershipPairRunner(config) if config.paradigm == "ownership_pair" else ExperimentRunner(config)
    run_dir = runner.run()
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def analyze_command(run_dir: str) -> int:
    root = Path(run_dir)
    summary = summarize(_load_jsonl(root / "events.jsonl"), _load_jsonl(root / "probes.jsonl"))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def suite_command(suite_path: str) -> int:
    output = SuiteRunner(suite_path).run()
    print(str(output))
    return 0


def doctor_command(config_path: str) -> int:
    report = run_preflight(ExperimentConfig.from_yaml(config_path))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(prog="embodied-llm")
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run", help="run one configured episode")
    run_parser.add_argument("--config", required=True)
    suite_parser = sub.add_parser("suite", help="run a preregistered condition suite")
    suite_parser.add_argument("--suite", required=True)
    analyze_parser = sub.add_parser("analyze", help="recompute summary metrics")
    analyze_parser.add_argument("run_dir")
    doctor_parser = sub.add_parser("doctor", help="validate dependencies and endpoints")
    doctor_parser.add_argument("--config", required=True)
    args = parser.parse_args()
    if args.command == "run":
        return run_command(args.config)
    if args.command == "suite":
        return suite_command(args.suite)
    if args.command == "doctor":
        return doctor_command(args.config)
    return analyze_command(args.run_dir)


if __name__ == "__main__":
    raise SystemExit(main())
