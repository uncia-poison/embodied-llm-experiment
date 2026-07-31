from __future__ import annotations

import argparse
import json

from embodied_llm.hosted import (
    run_hosted_discovery,
    run_hosted_episode,
    run_hosted_evaluation,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a paced hosted embodied-LLM episode or longitudinal phase"
    )
    parser.add_argument("--config", required=True)
    parser.add_argument(
        "--mode",
        choices=["episode", "discovery", "evaluation"],
        default="episode",
    )
    parser.add_argument("--minimum-request-interval-seconds", type=float, default=0.0)
    parser.add_argument("--policy-output")
    parser.add_argument("--checkpoint-in")
    parser.add_argument("--checkpoint-out")
    parser.add_argument("--checkpoint-every", type=int, default=1)
    parser.add_argument("--fresh-context", action="store_true")
    parser.add_argument("--output-dir")
    parser.add_argument(
        "--variants",
        default="full,empty,shuffled,core_only,archive_only",
    )
    parser.add_argument("--unrelated-checkpoint")
    parser.add_argument("--shuffle-seed", type=int, default=1701)
    args = parser.parse_args()

    common = {
        "minimum_request_interval_seconds": args.minimum_request_interval_seconds,
        "policy_output": args.policy_output,
    }
    if args.mode == "episode":
        run_dir = run_hosted_episode(args.config, **common)
        result = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    elif args.mode == "discovery":
        if not args.checkpoint_out:
            parser.error("discovery requires --checkpoint-out")
        result = run_hosted_discovery(
            args.config,
            checkpoint_in=args.checkpoint_in,
            checkpoint_out=args.checkpoint_out,
            checkpoint_every=args.checkpoint_every,
            fresh_context=args.fresh_context,
            **common,
        )
    else:
        if not args.checkpoint_in:
            parser.error("evaluation requires --checkpoint-in")
        if not args.output_dir:
            parser.error("evaluation requires --output-dir")
        result = run_hosted_evaluation(
            args.config,
            checkpoint_path=args.checkpoint_in,
            output_dir=args.output_dir,
            variants=[item.strip() for item in args.variants.split(",") if item.strip()],
            unrelated_checkpoint_path=args.unrelated_checkpoint,
            shuffle_seed=args.shuffle_seed,
            **common,
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
