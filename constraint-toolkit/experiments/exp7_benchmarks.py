"""
Experiment 7: Run full benchmark suite.

Executes all benchmarks against known research results, prints a
formatted report, and saves results as JSON.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from constraint_toolkit.benchmarks import BenchmarkSuite, save_report


def main() -> None:
    """Run the full benchmark suite."""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║      CONSTRAINT TOOLKIT - BENCHMARK SUITE LAUNCHING     ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()

    suite = BenchmarkSuite()
    report = suite.run_all()

    # Print formatted report
    print(report.format_report())
    print()

    # Print detailed results
    for r in report.results:
        print(f"  {r.name}:")
        print(f"    Expected: {r.expected}")
        print(f"    Actual:   {r.actual}")
        print(f"    Metric:   {r.metric:.4f}")
        print(f"    Tolerance: ±{r.tolerance:.4f}")
        if r.details:
            for k, v in r.details.items():
                if isinstance(v, float):
                    print(f"    {k}: {v:.4f}")
                else:
                    print(f"    {k}: {v}")
        print()

    # Save JSON
    output = Path(__file__).resolve().parent.parent / "results" / "exp7_benchmarks.json"
    save_report(report, output)
    print(f"Results saved to {output}")


if __name__ == "__main__":
    main()
