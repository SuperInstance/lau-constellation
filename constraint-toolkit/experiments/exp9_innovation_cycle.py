"""
Experiment 9: Map traditions to innovation phases.

Scores all 10 traditions on each innovation cycle phase, predicts
transitions, identifies rebellion candidates, and displays an ASCII
cycle chart.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from constraint_toolkit.innovation import InnovationTracker


def main() -> None:
    """Run the innovation cycle analysis."""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║      EXPERIMENT 9 - INNOVATION CYCLE TRACKER            ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()

    tracker = InnovationTracker()

    # Part 1: Map all traditions
    print("── Part 1: All traditions mapped to cycle phases ──")
    print()

    mapping = tracker.map_all_traditions()
    results = {}

    for name, score in sorted(mapping.items(), key=lambda x: x[1].dominant_score, reverse=True):
        bar_width = 30
        bars = ""
        for phase_name, val in score.scores.items():
            n_chars = int(val * bar_width)
            bars += f"    {phase_name:<14s} {'█' * n_chars}{'░' * (bar_width - n_chars)} {val:.0%}\n"

        print(f"  {score.dominant_phase.emoji} {name:<20s} → {score.dominant_phase.value} ({score.dominant_score:.0%})")
        print(bars)

        results[name] = {
            "dominant_phase": score.dominant_phase.value,
            "scores": score.scores,
        }

    print()

    # Part 2: Phase predictions
    print("── Part 2: Phase transition predictions ──")
    print()

    predictions = {}
    for name in mapping:
        pred = tracker.predict_next_phase(name)
        print(f"  {name}:")
        print(f"    Current: {pred['current_phase']} ({pred['current_score']:.0%})")
        print(f"    Next:    {pred['next_phase']} ({pred['next_score']:.0%})")
        print(f"    Readiness: {pred['transition_readiness']:.0%}")
        print(f"    Direction: {pred['predicted_direction']}")
        print()
        predictions[name] = pred

    # Part 3: Rebellion candidates
    print("── Part 3: Traditions ripe for rebellion ──")
    print()

    candidates = tracker.find_rebellion_candidates()
    if candidates:
        for c in candidates:
            print(
                f"  🔥 {c['tradition']:<20s} "
                f"Phase: {c['phase']:<14s} "
                f"Boredom: {c['boredom_score']:.0%} "
                f"Rebellion: {c['rebellion_score']:.0%} "
                f"Readiness: {c['readiness']:.0%}"
            )
    else:
        print("  No traditions currently in rebellion phase.")
    print()

    # Part 4: Cycle chart
    print("── Part 4: Innovation Cycle Chart ──")
    print()
    print(tracker.format_cycle_chart())

    # Save results
    output = Path(__file__).resolve().parent.parent / "results" / "exp9_innovation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        json.dump(
            {"tradition_scores": results, "predictions": predictions, "rebellion_candidates": candidates},
            f,
            indent=2,
            default=str,
        )
    print(f"\nResults saved to {output}")


if __name__ == "__main__":
    main()
