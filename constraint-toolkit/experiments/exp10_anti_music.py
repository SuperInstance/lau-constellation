"""
Experiment 10: Anti-music detection demo.

Scores workspace audio files, generates anti-music at 3 intensity levels,
compares against random baseline, and calibrates the detector.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from constraint_toolkit.anti_music import AntiMusicDetector


def main() -> None:
    """Run the anti-music detection demo."""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║      EXPERIMENT 10 - ANTI-MUSIC DETECTOR                ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()

    detector = AntiMusicDetector(n_baseline=5000, seed=42)
    results = {}

    # Part 1: Generate and score anti-music at 3 intensity levels
    print("── Part 1: Anti-music at 3 intensity levels ──")
    print()

    intensity_results = {}
    for intensity in [0.2, 0.6, 1.0]:
        print(f"  Generating anti-music at intensity {intensity:.0%}...")
        midi = detector.generate_anti_music(intensity=intensity, duration=15.0)

        # Extract features and score directly
        onsets = []
        pitches = []
        for track in midi.tracks:
            abs_time = 0.0
            for msg in track:
                abs_time += msg.time
                if msg.type == "note_on" and msg.velocity > 0:
                    time_sec = abs_time / (midi.ticks_per_beat * 120 / 60.0)
                    onsets.append(time_sec)
                    pitches.append(msg.note % 12)

        onset_arr = np.array(sorted(onsets), dtype=np.float64)
        pitch_arr = np.array(pitches, dtype=np.intp)
        pseudo_spectrum = np.abs(np.random.RandomState(42).exponential(1.0, 2048))

        score = detector.score_raw(onset_arr, pitch_arr, pseudo_spectrum, duration=15.0)

        print(f"    Score: {score.total_score:.3f} | Percentile: {score.percentile:.1f}% | Beyond random: {score.beyond_random}")
        print(f"    Negative consonance: {score.negative_consonance:.3f}")
        print(f"    Maximum syncopation: {score.maximum_syncopation:.3f}")
        print(f"    Spectral chaos:      {score.spectral_chaos:.3f}")
        print()

        intensity_results[f"intensity_{intensity:.1f}"] = {
            "intensity": intensity,
            "total_score": score.total_score,
            "percentile": score.percentile,
            "beyond_random": score.beyond_random,
            "negative_consonance": score.negative_consonance,
            "maximum_syncopation": score.maximum_syncopation,
            "spectral_chaos": score.spectral_chaos,
        }

        # Save generated MIDI
        midi_dir = Path(__file__).resolve().parent.parent / "results" / "anti_music"
        midi_dir.mkdir(parents=True, exist_ok=True)
        midi_path = midi_dir / f"anti_music_i{intensity:.1f}.mid"
        midi.save(str(midi_path))
        print(f"    Saved to {midi_path}")
        print()

    results["intensity_tests"] = intensity_results

    # Part 2: Random baseline statistics
    print("── Part 2: Random baseline statistics ──")
    print()

    baseline = detector._ensure_baseline()
    print(f"  Baseline samples: {len(baseline)}")
    print(f"  Mean score:    {np.mean(baseline):.4f}")
    print(f"  Std score:     {np.std(baseline):.4f}")
    print(f"  Median score:  {np.median(baseline):.4f}")
    print(f"  P95:           {np.percentile(baseline, 95):.4f}")
    print(f"  P99:           {np.percentile(baseline, 99):.4f}")
    print(f"  P99.93:        {np.percentile(baseline, 99.93):.4f}")
    print()

    results["baseline"] = {
        "n_samples": len(baseline),
        "mean": float(np.mean(baseline)),
        "std": float(np.std(baseline)),
        "median": float(np.median(baseline)),
        "p95": float(np.percentile(baseline, 95)),
        "p99": float(np.percentile(baseline, 99)),
        "p99_93": float(np.percentile(baseline, 99.93)),
    }

    # Part 3: Calibration test
    print("── Part 3: Calibration test ──")
    print()

    calibration = detector.calibrate()
    print(f"  Monotonicity (higher intensity → higher score): {calibration['calibration_monotonic']}")
    print()

    for key, val in calibration.items():
        if key.startswith("intensity_"):
            print(
                f"  {key}: score={val['total_score']:.3f} "
                f"percentile={val['percentile']:.1f}% "
                f"beyond_random={val['beyond_random']}"
            )
    print()

    results["calibration"] = calibration

    # Part 4: Score workspace WAV files if any
    workspace = Path(__file__).resolve().parent.parent / "workspace"
    wav_files = sorted(workspace.glob("*.wav")) if workspace.exists() else []

    if wav_files:
        print("── Part 4: Scoring workspace files ──")
        print()

        file_scores = {}
        for wav_path in wav_files:
            try:
                score = detector.score(wav_path)
                print(f"  {wav_path.name}:")
                print(f"    {score.summary()}")
                print()
                file_scores[wav_path.name] = {
                    "total_score": score.total_score,
                    "percentile": score.percentile,
                    "beyond_random": score.beyond_random,
                }
            except Exception as e:
                print(f"  {wav_path.name}: Error - {e}")
                print()

        results["file_scores"] = file_scores
    else:
        print("  No WAV files found in workspace/ — skipping file scoring.")
        print()

    # Save results
    output = Path(__file__).resolve().parent.parent / "results" / "exp10_anti_music.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output}")


if __name__ == "__main__":
    main()
