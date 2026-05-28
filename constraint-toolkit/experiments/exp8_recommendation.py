"""
Experiment 8: Music recommendation demo.

Analyzes workspace audio files, recommends closest traditions, generates
a taste map, and finds novel positions for composition.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from constraint_toolkit.recommender import MusicRecommender
from constraint_toolkit.dials import DIAL_RANGES, DialPosition


def main() -> None:
    """Run the recommendation demo."""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║      EXPERIMENT 8 - MUSIC RECOMMENDATION ENGINE        ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()

    recommender = MusicRecommender(seed=42)

    # Check for workspace WAV files
    workspace = Path(__file__).resolve().parent.parent / "workspace"
    wav_files = sorted(workspace.glob("*.wav")) if workspace.exists() else []

    results_data = {}

    # Part 1: Recommend based on tradition profiles
    print("── Part 1: Recommendations from tradition profiles ──")
    print()

    # Use tradition centers as queries
    sample_traditions = ["Jazz", "Classical", "Gamelan", "EDM", "Gagaku"]
    for trad_name in sample_traditions:
        center = DIAL_RANGES[trad_name]["center"]
        query_pos = DialPosition.from_array(center, tradition_name=trad_name)
        recs = recommender._recommend_from_position(query_pos, n=3)

        print(f"  If you like {trad_name}:")
        for rec in recs:
            print(f"    → {rec.explanation}")
            print(f"      Distance: {rec.distance:.2f} | Adventure: {rec.adventure_factor:.0%} | Fusion: {rec.fusion_viability:.0%}")
        print()

        results_data[trad_name] = [
            {
                "tradition": rec.tradition_name,
                "distance": rec.distance,
                "adventure": rec.adventure_factor,
                "fusion_viability": rec.fusion_viability,
                "explanation": rec.explanation,
            }
            for rec in recs
        ]

    # Part 2: Between-tradition recommendations
    print("── Part 2: Between-tradition interpolation ──")
    print()

    pairs = [("Jazz", "Gamelan"), ("EDM", "Classical"), ("Hip-hop", "Gagaku")]
    for a, b in pairs:
        positions = recommender.recommend_between(a, b, n=3)
        print(f"  {a} ↔ {b}:")
        for pos in positions:
            print(
                f"    → H={pos.harmonic_tension:.2f} R={pos.rhythmic_complexity:.2f} "
                f"S={pos.spectral_density:.2f} ({pos.tradition_name})"
            )
        print()

    # Part 3: Novel positions
    print("── Part 3: Novel unexplored positions ──")
    print()

    novel = recommender.recommend_novel(n=5)
    for pos in novel:
        min_dist = pos.metadata.get("min_distance_to_tradition", 0)
        print(
            f"  → H={pos.harmonic_tension:.2f} R={pos.rhythmic_complexity:.2f} "
            f"S={pos.spectral_density:.2f} (distance to nearest tradition: {min_dist:.2f})"
        )
    print()

    results_data["novel_positions"] = [
        {
            "position": pos.to_array().tolist(),
            "min_distance": pos.metadata.get("min_distance_to_tradition", 0),
        }
        for pos in novel
    ]

    # Part 4: Taste map
    print("── Part 4: Taste Map ──")
    print()

    # Generate taste map from tradition centers
    taste_lines = recommender.taste_map([])
    print(taste_lines)
    print()

    # Save results
    output = Path(__file__).resolve().parent.parent / "results" / "exp8_recommendation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        json.dump(results_data, f, indent=2, default=str)
    print(f"Results saved to {output}")


if __name__ == "__main__":
    main()
