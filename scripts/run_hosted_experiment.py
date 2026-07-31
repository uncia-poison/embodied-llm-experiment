from __future__ import annotations

import argparse
import json

from embodied_llm.hosted import run_hosted_episode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a hosted embodied-LLM episode with transport pacing")
    parser.add_argument("--config", required=True)
    parser.add_argument("--minimum-request-interval-seconds", type=float, default=0.0)
    parser.add_argument("--policy-output")
    args = parser.parse_args()

    run_dir = run_hosted_episode(
        args.config,
        minimum_request_interval_seconds=args.minimum_request_interval_seconds,
        policy_output=args.policy_output,
    )
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
