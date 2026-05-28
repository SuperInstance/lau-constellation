"""
Experiment 11: Musical Evolution Simulator.

Runs the genetic algorithm for 120 generations and reports:
- phase transitions over time
- diversity trajectory
- rebellion prediction
- ASCII plot of diversity history
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from constraint_toolkit.evolution import MusicalEvolution
from constraint_toolkit.visualize import ascii_scatter


def main():
    workspace = Path(__file__).parent.parent
    results_dir = workspace / "results"
    results_dir.mkdir(exist_ok=True)

    print("\n=== Experiment 11: Musical Evolution Simulator ===\n")

    sim = MusicalEvolution(population_size=60, seed=42)
    history = sim.evolve(n_generations=120)

    # Summary statistics
    phases = [h["phase"] for h in history]
    diversities = [h["diversity"] for h in history]
    mean_fitnesses = [h["mean_fitness"] for h in history]

    print(f"Generations simulated: {len(history)}")
    print(f"Final phase: {phases[-1]}")
    print(f"Phase sequence: {' → '.join(phases[:10])} ... {' → '.join(phases[-5:])}")
    print(f"Peak diversity: {max(diversities):.2f} at gen {int(np.argmax(diversities))}")
    print(f"Lowest diversity: {min(diversities):.2f} at gen {int(np.argmin(diversities))}")

    # Rebellion prediction
    prediction = sim.predict_rebellion(horizon=50)
    print(f"\nRebellion forecast:")
    print(f"  Current phase:      {prediction['current_phase']}")
    print(f"  Predicted gen:      {prediction['predicted_generation']}")
    print(f"  Confidence:         {prediction['confidence']:.1%}")

    # ASCII diversity plot
    gens = list(range(len(diversities)))
    chart = ascii_scatter(
        gens, diversities,
        width=70, height=15,
        title="Diversity Over Generations",
    )
    print(f"\n{chart}\n")

    # Save results
    output = {
        "experiment": "musical_evolution",
        "n_generations": len(history),
        "final_phase": phases[-1],
        "diversity_trajectory": [round(d, 4) for d in diversities],
        "mean_fitness_trajectory": [round(f, 4) for f in mean_fitnesses],
        "phase_sequence": phases,
        "rebellion_prediction": prediction,
    }
    out_path = results_dir / "exp11_results.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()
