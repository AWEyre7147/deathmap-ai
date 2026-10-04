"""Explicit command entry point for one OmicsDI invocation; never auto-resumes."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from deathmap_ai.omicsdi import run_pilot


def main():
    """Parse run/resume options and print the saved manifest and output location."""
    parser = argparse.ArgumentParser(description="Run the bounded OmicsDI metadata pilot")
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--candidate-cap", type=int)
    parser.add_argument("--detail-cap", type=int)
    parser.add_argument("--budget-seconds", type=float, default=None, help="Optional total budget; no fixed default")
    parser.add_argument("--request-timeout", type=float, default=10)
    parser.add_argument("--retries", type=int, default=1)
    args = parser.parse_args()
    if args.resume and args.run_dir is None:
        parser.error("--resume requires --run-dir")
    directory = args.run_dir or Path("outputs/omicsdi/cache/probes") / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    manifest = run_pilot(directory, resume=args.resume, candidate_cap=args.candidate_cap,
                         detail_cap=args.detail_cap, budget_seconds=args.budget_seconds,
                         request_timeout=args.request_timeout, retries=args.retries)
    print(json.dumps({"output_directory": str(directory.resolve()), "counts": manifest["counts"],
                      "stop_reasons": manifest["stop_reasons"],
                      "elapsed_seconds": manifest["invocations"][-1]["elapsed_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
