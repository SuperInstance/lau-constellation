"""
Experiment 3: Dial Space Map

Define known tradition profiles, identify unexplored regions (82% should be empty),
mark the "most pleasing" point. Outputs a text-based 3D dial space visualization
and saves tradition positions as JSON.
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from constraint_toolkit.dials import (
    DIAL_RANGES,
    MOST_PLEASING_POINT,
    UNEXPLORED_FRACTION,
    DialPosition,
    compute_dial_distance,
)


def main():
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    print("=== Dial Space Map ===\n")

    # Print tradition positions
    print(f"{'Tradition':<22} {'H':>5} {'R':>5} {'S':>5} {'Spread_H':>8} {'Spread_R':>8} {'Spread_S':>8}")
    print("-" * 70)

    tradition_data = {}
    for name, profile in DIAL_RANGES.items():
        c = profile["center"]
        s = profile["spread"]
        print(f"{name:<22} {c[0]:>5.2f} {c[1]:>5.2f} {c[2]:>5.2f} {s[0]:>8.2f} {s[1]:>8.2f} {s[2]:>8.2f}")
        tradition_data[name] = {
            "center": c.tolist(),
            "spread": s.tolist(),
            "description": profile["description"],
        }

    # Most pleasing point
    mp = MOST_PLEASING_POINT
    print(f"\nMost Pleasing Point: ({mp.harmonic_tension}, {mp.rhythmic_complexity}, {mp.spectral_density})")
    print(f"  Tradition: {mp.tradition_name}")

    # Distance matrix between traditions
    names = list(DIAL_RANGES.keys())
    centers = [DIAL_RANGES[n]["center"] for n in names]
    print(f"\n=== Distance Matrix Between Traditions ===\n")
    header = f"{'':>22}" + "".join(f"{n[:8]:>9}" for n in names)
    print(header)
    for i, name_a in enumerate(names):
        row = f"{name_a:>22}"
        for j, name_b in enumerate(names):
            if i == j:
                row += f"{'---':>9}"
            else:
                d = np.linalg.norm(centers[i] - centers[j])
                row += f"{d:>9.2f}"
        print(row)

    # Unexplored region analysis
    print(f"\n=== Unexplored Region Analysis ===\n")
    rng = np.random.RandomState(42)
    n_samples = 10000
    n_near_tradition = 0
    threshold = 1.5  # within 1.5 units counts as "near"

    for _ in range(n_samples):
        point = rng.uniform(0, 5, size=3)
        min_dist = min(np.linalg.norm(point - c) for c in centers)
        if min_dist < threshold:
            n_near_tradition += 1

    explored_fraction = n_near_tradition / n_samples
    unexplored = 1.0 - explored_fraction
    print(f"Samples tested:        {n_samples}")
    print(f"Near a tradition:      {n_near_tradition} ({explored_fraction:.1%})")
    print(f"Unexplored:            {n_samples - n_near_tradition} ({unexplored:.1%})")
    print(f"Expected unexplored:   {UNEXPLORED_FRACTION:.0%}")

    # Text-based 2D projection (H vs R)
    print(f"\n=== 2D Projection (Harmonic × Rhythmic) ===\n")
    print(f"  R=5 |")
    for r_level in [5, 4, 3, 2, 1, 0]:
        row = f"  R={r_level} |"
        for h_level in range(6):
            cell = "  . "
            for name, profile in DIAL_RANGES.items():
                c = profile["center"]
                if abs(c[0] - h_level) < 1.0 and abs(c[1] - r_level) < 1.0:
                    cell = f" {name[:2]:>2} "
                    break
            row += cell
        print(row)
    print(f"       " + "".join(f"  H={h}" for h in range(6)))

    # Mark the most pleasing point
    print(f"\n★ Most pleasing: Gagaku at ({mp.harmonic_tension}, {mp.rhythmic_complexity}, {mp.spectral_density})")

    output = {
        "experiment": "dial_space_map",
        "traditions": tradition_data,
        "most_pleasing_point": {
            "harmonic_tension": mp.harmonic_tension,
            "rhythmic_complexity": mp.rhythmic_complexity,
            "spectral_density": mp.spectral_density,
            "tradition": mp.tradition_name,
        },
        "unexplored_analysis": {
            "samples": n_samples,
            "explored_fraction": explored_fraction,
            "unexplored_fraction": unexplored,
            "expected_unexplored": UNEXPLORED_FRACTION,
            "threshold": threshold,
        },
    }

    with open(results_dir / "exp3_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {results_dir / 'exp3_results.json'}")


if __name__ == "__main__":
    main()
