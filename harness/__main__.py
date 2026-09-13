"""python -m harness"""

from __future__ import annotations

import argparse
import json

from harness.runner import default_suite, write_digest
from harness.wrap_misw import agent_root, probe_class_agent


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay the Track 1 containment harness")
    parser.add_argument(
        "--probe-class-agent",
        action="store_true",
        help="Classify MISW4412 tool destinations without calling the LLM",
    )
    args = parser.parse_args()

    results = default_suite()
    digest = write_digest(results)
    print(f"digest: {digest}")
    for result in results:
        print(
            f"{result.name}: stop@{result.stopped_at} "
            f"control={result.stop_control} pages={result.pages}"
        )
        for row in result.log:
            print(
                f"  {row['step']:>2} {row['verdict']:5} {row['control'] or '-':3} "
                f"{row['phase']} ({row['reason']})"
            )

    if args.probe_class_agent:
        root = agent_root()
        if root is None:
            print("class agent: not found (set MISW4412_ROOT)")
            return 0
        print(f"class agent: {root}")
        try:
            probes = probe_class_agent(root)
        except Exception as exc:
            print(f"class agent probe failed: {exc}")
            return 1
        print(json.dumps([p.__dict__ for p in probes], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
