"""
Experiment 2: Conservation Stress Test

Generate 10,000 random melodic sequences, compute I_v + I_h for each,
report statistics, compare meantone vs ET (ratio 1.003 expected).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np

from constraint_toolkit.conservation import measure_tension, stress_test


def main():
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    print("=== Conservation Stress Test ===\n")
    print("Generating 10,000 random melodic sequences...")

    results = stress_test(n_sequences=10000, seq_length=12, seed=42)

    print(f"\nResults:")
    print(f"  Mean I_v + I_h:  {results['mean_sum']:.6f}")
    print(f"  Std I_v + I_h:   {results['std_sum']:.6f}")
    print(f"  CV:              {results['cv']:.4f} ({results['cv']*100:.2f}%)")
    print(f"  Correlation r:   {results['correlation']:.4f}")
    print(f"  (Known result: r ≈ +0.436, weakly supported)")
    print(f"\nMeantone vs ET:")
    print(f"  ET mean sum:      {results['et_mean']:.6f}")
    print(f"  Meantone mean:    {results['meantone_mean']:.6f}")
    print(f"  Ratio (MT/ET):    {results['meantone_ratio']:.4f}")
    print(f"  (Expected ratio:  1.003)")

    # Additional analysis: distribution shape
    rng = np.random.RandomState(42)
    sums = []
    for _ in range(10000):
        seq = rng.randint(0, 12, size=12).tolist()
        I_v, I_h = measure_tension(seq, "ET")
        sums.append(I_v + I_h)
    sums = np.array(sums)

    percentiles = np.percentile(sums, [5, 25, 50, 75, 95])
    print(f"\nDistribution percentiles:")
    print(f"  5th:  {percentiles[0]:.4f}")
    print(f"  25th: {percentiles[1]:.4f}")
    print(f"  50th: {percentiles[2]:.4f}")
    print(f"  75th: {percentiles[3]:.4f}")
    print(f"  95th: {percentiles[4]:.4f}")

    # Histogram data for plotting
    hist, bin_edges = np.histogram(sums, bins=50)
    hist_data = {
        "counts": hist.tolist(),
        "bin_edges": bin_edges.tolist(),
    }

    output = {
        "experiment": "conservation_stress_test",
        **results,
        "distribution": hist_data,
        "percentiles": {
            "p5": float(percentiles[0]),
            "p25": float(percentiles[1]),
            "p50": float(percentiles[2]),
            "p75": float(percentiles[3]),
            "p95": float(percentiles[4]),
        },
    }

    with open(results_dir / "exp2_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {results_dir / 'exp2_results.json'}")


if __name__ == "__main__":
    main()
