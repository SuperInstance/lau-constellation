#!/usr/bin/env python3
"""Experiment 5: Cross-cultural dial analysis.

Analyzes .wav files from the workspace with cross-cultural dial comparison,
tests whether traditions with similar dial positions sound similar, and
reports which traditions are closest/furthest apart in dial space.
"""

import json
import os
import sys
from pathlib import Path

# Allow running from anywhere
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from constraint_toolkit.dials import (
    DIAL_RANGES,
    DialPosition,
    compute_dial_distance,
    compute_dial_signature,
)
from constraint_toolkit.analyzer import analyze_wav
from constraint_toolkit.classifier import DialClassifier


WORKSPACE = Path(__file__).resolve().parent.parent.parent

# Map filename patterns to cultural traditions
FILENAME_TRADITIONS = {
    "blues": "Blues",
    "delta_blues": "Blues",
    "jazz": "Jazz",
    "bebop": "Jazz",
    "techno": "EDM",
    "electronic": "EDM",
    "ella": "Jazz",
    "gospel": "Gospel",
    "hindustani": "Hindustani",
    "gamelan": "Gamelan",
    "gagaku": "Gagaku",
    "african": "African Polyrhythm",
    "hip_hop": "Hip-hop",
    "latin": "Latin",
    "classical": "Classical",
}


def infer_tradition(filename: str) -> str | None:
    """Infer the cultural tradition from a filename."""
    lower = filename.lower()
    for pattern, tradition in FILENAME_TRADITIONS.items():
        if pattern in lower:
            return tradition
    return None


def find_wav_files() -> list[Path]:
    """Find all .wav files in workspace root."""
    files = []
    for f in sorted(WORKSPACE.glob("*.wav")):
        files.append(f)
    return files


def analyze_cross_cultural() -> dict:
    """Run cross-cultural analysis on all available .wav files."""
    wav_files = find_wav_files()
    results = {
        "files_analyzed": [],
        "traditions_found": {},
        "distances": {},
        "closest_pair": None,
        "furthest_pair": None,
        "similarity_prediction": {},
    }

    positions: dict[str, DialPosition] = {}

    for wf in wav_files:
        try:
            dial = analyze_wav(wf).dial_position
            tradition = infer_tradition(wf.name) or "Unknown"
            positions[wf.name] = dial
            results["files_analyzed"].append({
                "file": wf.name,
                "tradition": tradition,
                "harmonic": dial.harmonic_tension,
                "rhythmic": dial.rhythmic_complexity,
                "spectral": dial.spectral_density,
            })
            if tradition not in results["traditions_found"]:
                results["traditions_found"][tradition] = []
            results["traditions_found"][tradition].append(wf.name)
        except Exception as e:
            results["files_analyzed"].append({
                "file": wf.name,
                "error": str(e),
            })

    # Compute pairwise distances between files
    names = list(positions.keys())
    min_dist = float("inf")
    max_dist = 0.0
    min_pair = ("", "")
    max_pair = ("", "")

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            d = compute_dial_distance(positions[names[i]], positions[names[j]])
            key = f"{names[i]} vs {names[j]}"
            results["distances"][key] = round(d, 4)
            if d < min_dist:
                min_dist = d
                min_pair = (names[i], names[j])
            if d > max_dist:
                max_dist = d
                max_pair = (names[i], names[j])

    if min_pair[0]:
        results["closest_pair"] = {
            "files": list(min_pair),
            "distance": round(min_dist, 4),
            "tradition_a": infer_tradition(min_pair[0]),
            "tradition_b": infer_tradition(min_pair[1]),
            "similar_sound": infer_tradition(min_pair[0])
            == infer_tradition(min_pair[1]),
        }
    if max_pair[0]:
        results["furthest_pair"] = {
            "files": list(max_pair),
            "distance": round(max_dist, 4),
            "tradition_a": infer_tradition(max_pair[0]),
            "tradition_b": infer_tradition(max_pair[1]),
        }

    # Test prediction: traditions with similar dial positions should sound similar
    classifier = DialClassifier()
    for name, pos in positions.items():
        predicted, conf = classifier.predict_genre(pos)
        actual = infer_tradition(name)
        results["similarity_prediction"][name] = {
            "actual_tradition": actual,
            "predicted_genre": predicted,
            "confidence": round(conf, 4),
            "correct": actual is not None and predicted == actual,
        }

    # Tradition-level distance analysis using known profiles
    tradition_centres = {}
    for tradition, pos_list in results["traditions_found"].items():
        if tradition in DIAL_RANGES:
            prof = DIAL_RANGES[tradition]
            c = prof["center"]
            centre = DialPosition(
                harmonic_tension=float(c[0]),
                rhythmic_complexity=float(c[1]),
                spectral_density=float(c[2]),
                tradition_name=tradition,
            )
            tradition_centres[tradition] = centre

    results["tradition_distances"] = {}
    trad_names = list(tradition_centres.keys())
    for i in range(len(trad_names)):
        for j in range(i + 1, len(trad_names)):
            d = compute_dial_distance(
                tradition_centres[trad_names[i]],
                tradition_centres[trad_names[j]],
            )
            results["tradition_distances"][
                f"{trad_names[i]} vs {trad_names[j]}"
            ] = round(d, 4)

    return results


def main():
    print("=" * 60)
    print("EXPERIMENT 5: Cross-Cultural Dial Analysis")
    print("=" * 60)

    results = analyze_cross_cultural()

    print(f"\nFiles analyzed: {len(results['files_analyzed'])}")
    print(f"Traditions found: {list(results['traditions_found'].keys())}")

    print("\n--- Pairwise File Distances ---")
    for pair, dist in sorted(
        results["distances"].items(), key=lambda x: x[1]
    ):
        print(f"  {pair}: {dist:.4f}")

    if results["closest_pair"]:
        cp = results["closest_pair"]
        print(f"\nClosest pair: {cp['files']} (d={cp['distance']:.4f})")
        print(f"  Same tradition? {cp['similar_sound']}")

    if results["furthest_pair"]:
        fp = results["furthest_pair"]
        print(f"Furthest pair: {fp['files']} (d={fp['distance']:.4f})")

    print("\n--- Classifier Predictions ---")
    correct = 0
    total = 0
    for name, pred in results["similarity_prediction"].items():
        status = "✓" if pred["correct"] else "✗"
        print(
            f"  {status} {name}: predicted={pred['predicted_genre']}, "
            f"actual={pred['actual_tradition']} (conf={pred['confidence']:.2f})"
        )
        if pred["actual_tradition"] != "Unknown":
            total += 1
            if pred["correct"]:
                correct += 1

    if total > 0:
        accuracy = correct / total
        print(f"\nClassification accuracy: {correct}/{total} = {accuracy:.1%}")

    print("\n--- Tradition-Level Distances ---")
    for pair, dist in sorted(
        results["tradition_distances"].items(), key=lambda x: x[1]
    ):
        print(f"  {pair}: {dist:.4f}")

    # Save results
    output = Path(__file__).resolve().parent / "results_exp5.json"
    with open(output, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {output}")


if __name__ == "__main__":
    main()
