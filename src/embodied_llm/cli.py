from __future__ import annotations

import argparse
import json
from pathlib import Path

from .blinding import create_blind_package
from .config import ExperimentConfig
from .experiment import ExperimentRunner
from .metrics import summarize
from .ownership import OwnershipPairRunner
from .preflight import run_preflight
from .suite import SuiteRunner


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


def suite_command(args: argparse.Namespace) -> int:
    runner = SuiteRunner(
        args.suite,
        resume=not args.no_resume,
        continue_on_error=not args.fail_fast,
    )
    if args.plan:
        print(json.dumps(runner.plan(), ensure_ascii=False, indent=2))
        return 0
    if args.preflight:
        report = runner.preflight()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 1

    output = runner.run()
    blind_dir = None
    if args.blind:
        blind_dir = create_blind_package(
            output,
            blind_seed=args.blind_seed,
            overwrite=args.overwrite_blind,
        )
    progress = json.loads((output / "progress.json").read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "output_dir": str(output),
                "blind_dir": str(blind_dir) if blind_dir is not None else None,
                "progress": progress,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if progress["failed_runs"] == 0 else 2


def blind_command(args: argparse.Namespace) -> int:
    output = create_blind_package(
        args.suite_dir,
        blind_seed=args.blind_seed,
        overwrite=args.overwrite,
    )
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

    suite_parser = sub.add_parser("suite", help="plan, validate or run a condition suite")
    suite_parser.add_argument("--suite", required=True)
    suite_parser.add_argument("--plan", action="store_true", help="print the exact run matrix and call budget")
    suite_parser.add_argument("--preflight", action="store_true", help="validate every referenced condition")
    suite_parser.add_argument("--no-resume", action="store_true", help="rerun completed cells")
    suite_parser.add_argument("--fail-fast", action="store_true", help="stop after the first failed cell")
    suite_parser.add_argument("--blind", action="store_true", help="build a blinded rating package after the suite")
    suite_parser.add_argument("--blind-seed", type=int, default=1701)
    suite_parser.add_argument("--overwrite-blind", action="store_true")

    analyze_parser = sub.add_parser("analyze", help="recompute summary metrics")
    analyze_parser.add_argument("run_dir")

    doctor_parser = sub.add_parser("doctor", help="validate dependencies and endpoints")
    doctor_parser.add_argument("--config", required=True)

    blind_parser = sub.add_parser("blind", help="create a blinded qualitative-rating package")
    blind_parser.add_argument("suite_dir")
    blind_parser.add_argument("--blind-seed", type=int, default=1701)
    blind_parser.add_argument("--overwrite", action="store_true")

    args = parser.parse_args()
    if args.command == "run":
        return run_command(args.config)
    if args.command == "suite":
        if args.plan and args.preflight:
            parser.error("--plan and --preflight are mutually exclusive")
        return suite_command(args)
    if args.command == "doctor":
        return doctor_command(args.config)
    if args.command == "blind":
        return blind_command(args)
    return analyze_command(args.run_dir)


if __name__ == "__main__":
    raise SystemExit(main())
