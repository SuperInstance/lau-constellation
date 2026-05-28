"""
Experiment 17: Synthetic Round-Trip Benchmark

For each tradition: compose → render to audio → analyze back → measure error.
This tests the full pipeline's round-trip fidelity.
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from constraint_toolkit.dials import DIAL_RANGES, DialPosition, compute_dial_distance
from constraint_toolkit.composer import ConstraintComposer
from constraint_toolkit.synthesizer import ConstraintSynth
from constraint_toolkit.features import extract_features
from constraint_toolkit.analyzer import compute_dial_from_features
from constraint_toolkit.visualize import ascii_bar_chart, format_results_table

WORKSPACE = Path("/home/phoenix/.openclaw/workspace")


def main():
    print("=" * 70)
    print("EXPERIMENT 17: Synthetic Round-Trip Benchmark")
    print("=" * 70)
    print()

    traditions = list(DIAL_RANGES.keys())
    n_samples = 20

    composer = ConstraintComposer(seed=42)
    synth = ConstraintSynth(sr=44100)

    results_per_tradition: dict[str, dict] = {}
    all_errors: list[float] = []

    print(f"Testing {len(traditions)} traditions × {n_samples} samples each")
    print()

    for tradition in traditions:
        center = DIAL_RANGES[tradition]["center"]
        target = DialPosition.from_array(center, tradition_name=tradition)
        errors = []

        print(f"  {tradition}:", end=" ", flush=True)

        for sample_idx in range(n_samples):
            seed = 42 + sample_idx * 100 + hash(tradition) % 1000
            comp = ConstraintComposer(seed=seed)

            try:
                # Compose
                midi = comp.compose_in_tradition(tradition, bars=4, tempo=120)

                # Render to audio
                audio = synth.render_midi(midi, dial_target=target, bpm=120)

                # Analyze back
                fv = extract_features(audio, 44100)
                recovered = compute_dial_from_features(fv)

                # Compute error
                error = compute_dial_distance(target, recovered)
                errors.append(error)
                all_errors.append(error)

            except Exception as e:
                print(f"E", end="", flush=True)
                errors.append(float("nan"))

        mean_err = float(np.nanmean(errors))
        std_err = float(np.nanstd(errors))
        max_err = float(np.nanmax(errors))
        min_err = float(np.nanmin(errors))

        results_per_tradition[tradition] = {
            "mean_error": mean_err,
            "std_error": std_err,
            "min_error": min_err,
            "max_error": max_err,
            "n_samples": n_samples,
            "all_errors": errors,
        }

        # Per-axis errors
        print(f"mean={mean_err:.2f} ± {std_err:.2f}")

    # Overall summary
    print("\n" + "=" * 70)
    print("ROUND-TRIP RESULTS")
    print("=" * 70)

    overall_mean = float(np.nanmean(all_errors))
    overall_std = float(np.nanstd(all_errors))
    print(f"\n   Overall mean error: {overall_mean:.2f} ± {overall_std:.2f}")
    print(f"   Total samples: {len(all_errors)}")

    # Per-tradition table
    print("\n")
    table_data = []
    for trad in traditions:
        r = results_per_tradition[trad]
        table_data.append({
            "Tradition": trad,
            "Mean Error": r["mean_error"],
            "Std": r["std_error"],
            "Min": r["min_error"],
            "Max": r["max_error"],
        })
    print(format_results_table(table_data, ["Tradition", "Mean Error", "Std", "Min", "Max"]))

    # Bar chart
    print()
    mean_errors = {t: results_per_tradition[t]["mean_error"] for t in traditions}
    print(ascii_bar_chart(mean_errors, title="Mean Round-Trip Error by Tradition"))

    # Hardest/easiest traditions
    sorted_trads = sorted(results_per_tradition.items(), key=lambda x: x[1]["mean_error"])
    print(f"\n   Easiest (lowest error): {sorted_trads[0][0]} ({sorted_trads[0][1]['mean_error']:.2f})")
    print(f"   Hardest (highest error): {sorted_trads[-1][0]} ({sorted_trads[-1][1]['mean_error']:.2f})")

    # Per-axis breakdown (compute for a subset)
    print("\n" + "─" * 50)
    print("PER-AXIS ERROR BREAKDOWN")
    print("─" * 50)
    axis_errors = {"harmonic_tension": [], "rhythmic_complexity": [], "spectral_density": []}

    for tradition in traditions:
        center = DIAL_RANGES[tradition]["center"]
        target = DialPosition.from_array(center, tradition_name=tradition)
        for sample_idx in range(min(10, n_samples)):
            seed = 42 + sample_idx * 100 + hash(tradition) % 1000
            comp = ConstraintComposer(seed=seed)
            try:
                midi = comp.compose_in_tradition(tradition, bars=4, tempo=120)
                audio = synth.render_midi(midi, dial_target=target, bpm=120)
                fv = extract_features(audio, 44100)
                recovered = compute_dial_from_features(fv)

                axis_errors["harmonic_tension"].append(
                    abs(target.harmonic_tension - recovered.harmonic_tension))
                axis_errors["rhythmic_complexity"].append(
                    abs(target.rhythmic_complexity - recovered.rhythmic_complexity))
                axis_errors["spectral_density"].append(
                    abs(target.spectral_density - recovered.spectral_density))
            except Exception:
                pass

    for axis, errs in axis_errors.items():
        if errs:
            print(f"   {axis:25s}: mean={np.mean(errs):.2f} ± {np.std(errs):.2f}")

    # Save
    results = {
        "experiment": "exp17_synthetic_benchmark",
        "n_samples_per_tradition": n_samples,
        "overall": {"mean_error": overall_mean, "std_error": overall_std},
        "per_tradition": results_per_tradition,
        "per_axis": {k: {"mean": float(np.mean(v)), "std": float(np.std(v))}
                     for k, v in axis_errors.items() if v},
    }

    results_path = PROJECT_ROOT / "results" / "results_exp17.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Results saved to {results_path}")


if __name__ == "__main__":
    main()
