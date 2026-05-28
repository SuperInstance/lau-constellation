"""
Experiment 4: Groove Optimization

Take a quantized MIDI pattern, optimize toward Jazz, Funk, EDM targets,
and report before/after comparison of dial positions and convergence.
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from constraint_toolkit.composer import ConstraintComposer
from constraint_toolkit.dials import DIAL_RANGES, DialPosition, compute_dial_distance
from constraint_toolkit.optimizer import GrooveOptimizer


def main():
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    print("=== Groove Optimization ===\n")

    # Generate a quantized MIDI pattern
    composer = ConstraintComposer(seed=42)
    base_midi = composer.compose(
        DialPosition(harmonic_tension=2.5, rhythmic_complexity=2.5, spectral_density=2.5),
        bars=4,
        tempo=120,
    )

    optimizer = GrooveOptimizer(seed=42, max_offset_ms=50.0)
    targets = ["Jazz", "EDM", "Blues", "Latin"]

    all_results = {}

    for target_genre in targets:
        print(f"\n--- Optimizing toward {target_genre} ---")

        result = optimizer.optimize(
            base_midi,
            target_genre=target_genre,
            iterations=100,
            bpm=120,
        )

        print(result.summary())

        # Convergence analysis
        fitness = result.fitness_history
        if len(fitness) > 1:
            improvement = fitness[-1] - fitness[0]
            print(f"  Fitness improvement: {improvement:.4f}")
            print(f"  Initial distance: {-fitness[0]:.3f}")
            print(f"  Final distance: {-fitness[-1]:.3f}")

            # Convergence rate: iterations to reach 90% of improvement
            if abs(improvement) > 1e-6:
                target_fitness = fitness[0] + 0.9 * improvement
                for idx, f in enumerate(fitness):
                    if f >= target_fitness:
                        print(f"  90% convergence at iteration {idx}")
                        break

        all_results[target_genre] = {
            "original": {
                "harmonic_tension": result.original_position.harmonic_tension,
                "rhythmic_complexity": result.original_position.rhythmic_complexity,
                "spectral_density": result.original_position.spectral_density,
            },
            "target": {
                "harmonic_tension": result.target_position.harmonic_tension,
                "rhythmic_complexity": result.target_position.rhythmic_complexity,
                "spectral_density": result.target_position.spectral_density,
            },
            "optimized": {
                "harmonic_tension": result.optimized_position.harmonic_tension,
                "rhythmic_complexity": result.optimized_position.rhythmic_complexity,
                "spectral_density": result.optimized_position.spectral_density,
            },
            "distance_to_target": compute_dial_distance(result.optimized_position, result.target_position),
            "converged": result.converged,
            "iterations": result.iterations,
            "n_offsets": len(result.offset_ms),
            "fitness_history": result.fitness_history,
        }

    # Hybridization demo
    print(f"\n=== Genre Hybridization ===\n")
    hybrids = [
        ("Jazz", "EDM", 0.5),
        ("Blues", "Gamelan", 0.3),
        ("Classical", "Hip-hop", 0.7),
    ]

    for genre_a, genre_b, blend in hybrids:
        hybrid = optimizer.hybridize(genre_a, genre_b, blend)
        print(f"  {genre_a} × {genre_b} ({blend:.0%}): "
              f"H={hybrid.harmonic_tension:.2f} R={hybrid.rhythmic_complexity:.2f} S={hybrid.spectral_density:.2f}")
        all_results[f"hybrid_{genre_a}_{genre_b}"] = {
            "genre_a": genre_a,
            "genre_b": genre_b,
            "blend": blend,
            "position": {
                "harmonic_tension": hybrid.harmonic_tension,
                "rhythmic_complexity": hybrid.rhythmic_complexity,
                "spectral_density": hybrid.spectral_density,
            },
        }

    # Pocket optimization demo
    print(f"\n=== Pocket Optimization ===\n")
    pocket_result = optimizer.optimize_for_pocket(base_midi, epsilon_ms=20.0, bpm=120)
    print(f"  Pocket width before: {pocket_result.fitness_history[0]:.1f} ms")
    print(f"  Pocket width after:  {pocket_result.fitness_history[1]:.1f} ms")
    print(f"  Converged: {pocket_result.converged}")
    print(f"  Notes adjusted: {len(pocket_result.offset_ms)}")

    output = {
        "experiment": "groove_optimization",
        "results": all_results,
        "pocket_optimization": {
            "width_before_ms": pocket_result.fitness_history[0],
            "width_after_ms": pocket_result.fitness_history[1],
            "converged": pocket_result.converged,
            "n_offsets": len(pocket_result.offset_ms),
        },
    }

    with open(results_dir / "exp4_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {results_dir / 'exp4_results.json'}")


if __name__ == "__main__":
    main()
