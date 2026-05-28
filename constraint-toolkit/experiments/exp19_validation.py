"""Experiment 19: Run all validations and produce a formatted report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure parent dir is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from constraint_toolkit.validation import run_all_validations


# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def main() -> None:
    report = run_all_validations()

    # Print colored report
    print(f"\n{BOLD}{'=' * 70}{RESET}")
    print(f"{BOLD}  CONSTRAINT TOOLKIT — VALIDATION REPORT{RESET}")
    print(f"{BOLD}{'=' * 70}{RESET}")

    for r in report.results:
        if r.passed and not r.marginal:
            status = f"{GREEN}✓ PASS{RESET}"
        elif r.marginal:
            status = f"{YELLOW}~ MARGINAL{RESET}"
        else:
            status = f"{RED}✗ FAIL{RESET}"

        print(f"\n  {status}  {BOLD}{r.name}{RESET}")
        print(f"         expected: {r.expected}")
        print(f"         actual:   {r.actual}")

    print(f"\n{BOLD}{'=' * 70}{RESET}")
    total = len(report.results)
    color = GREEN if report.n_fail == 0 else (YELLOW if report.n_fail <= 2 else RED)
    print(f"  {color}{BOLD}Results: {report.n_pass} PASS, {report.n_marginal} MARGINAL, "
          f"{report.n_fail} FAIL out of {total}{RESET}")
    print(f"{BOLD}{'=' * 70}\n")

    # Save JSON results
    out_path = Path(__file__).resolve().parent / "results" / "exp19_validation.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "experiment": "exp19_validation",
        "results": [
            {
                "name": r.name,
                "expected": r.expected,
                "actual": r.actual,
                "passed": r.passed,
                "marginal": r.marginal,
                "details": r.details,
            }
            for r in report.results
        ],
        "summary": {
            "n_pass": report.n_pass,
            "n_marginal": report.n_marginal,
            "n_fail": report.n_fail,
            "total": total,
        },
    }

    with open(out_path, "w") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"  Results saved to {out_path}")


if __name__ == "__main__":
    main()
