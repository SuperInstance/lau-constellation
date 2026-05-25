#!/usr/bin/env python3
"""
Experiment 2: Just Noticeable Difference in Dial Space
======================================================

How far do you need to move a dial before listeners notice?

For each axis (I_vert, I_horiz, I_spectral):
  - Start at a reference dial position (Western ET: 2.72, 2.05, 1.8)
  - Incrementally adjust one axis while keeping others fixed
  - At each step, synthesize 2 seconds of audio
  - The JND is the smallest change that produces a perceptible difference

Generate a sensitivity map and WAV pairs for each JND.

Outputs:
  - jnd_data.json       : full sweep data for each axis
  - sensitivity_map.json : axis sensitivities
  - WAV pairs for each JND
"""

import json, math, os, wave
import numpy as np
from pathlib import Path
from scipy.interpolate import interp1d

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

SAMPLE_RATE = 44100
DURATION = 2.0

# Reference positions
REFERENCE = {"I_vert": 2.72, "I_horiz": 2.05, "I_spectral": 1.8}

# Axis ranges (min, max, step)
AXES = {
    "I_vert":     {"min": 1.5, "max": 4.0, "ref": 2.72},
    "I_horiz":    {"min": 1.0, "max": 4.0, "ref": 2.05},
    "I_spectral": {"min": 1.0, "max": 4.0, "ref": 1.8},
}


# ── Audio Synthesis ─────────────────────────────────────────────────────────

def synthesize_from_dials(dials, seed=42):
    """
    Synthesize 2s audio from dial positions (I_vert, I_horiz, I_spectral).
    
    I_vert     → harmonic complexity: # of voices, consonance of intervals
    I_horiz    → rhythmic regularity: how metronomic patterns are
    I_spectral → timbral richness: overtones, spectral content
    """
    rng = np.random.default_rng(seed)
    i_vert, i_horiz, i_spectral = dials["I_vert"], dials["I_horiz"], dials["I_spectral"]
    total_samples = int(SAMPLE_RATE * DURATION)
    t = np.linspace(0, DURATION, total_samples, endpoint=False)
    audio = np.zeros(total_samples)

    # I_vert controls harmonic structure
    n_voices = max(1, int(1 + (i_vert - 1.0) * 2.5))  # 1-8 voices
    base_freq = rng.uniform(200, 330)

    # Generate frequencies based on consonance model
    if i_vert < 2.0:
        # Simple consonant intervals
        simple_ratios = [1, 6/5, 5/4, 4/3, 3/2, 5/3, 15/8, 2]
        freqs = [base_freq * simple_ratios[i % len(simple_ratios)] for i in range(n_voices)]
    elif i_vert < 3.0:
        # Mix of consonant and slightly complex
        freqs = [base_freq * 2 ** (rng.uniform(0, 12) / 12) for _ in range(n_voices)]
    else:
        # Complex, microtonal intervals
        freqs = [base_freq * 2 ** (rng.uniform(0, 24) / 12) for _ in range(n_voices)]

    for freq in freqs:
        # I_spectral controls overtones
        n_harmonics = max(1, int(1 + (i_spectral - 1.0) * 3))  # 1-10 harmonics
        for h in range(1, n_harmonics + 1):
            amp = 0.3 / (h ** 1.2) / n_voices
            audio += amp * np.sin(2 * np.pi * freq * h * t)

    # I_horiz controls rhythmic structure
    if i_horiz < 2.0:
        # Steady amplitude
        pass
    elif i_horiz < 3.0:
        # Moderate rhythmic variation
        beat_freq = 2.0 + (i_horiz - 2.0) * 2
        envelope = 0.7 + 0.3 * np.sin(2 * np.pi * beat_freq * t)
        audio *= envelope
    else:
        # Complex rhythms with syncopation
        beat_freq = 3.0 + (i_horiz - 3.0) * 3
        envelope = (0.5 + 0.3 * np.sin(2 * np.pi * beat_freq * t) +
                    0.2 * np.sin(2 * np.pi * beat_freq * 1.73 * t))
        audio *= np.clip(envelope, 0.1, 1.0)

    # Normalize
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.8
    return audio


def write_wav(filepath, audio):
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(str(filepath), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm.tobytes())


# ── Perceptual Distance Metric ──────────────────────────────────────────────

def perceptual_distance(dials_a, dials_b):
    """
    Estimate perceptual distance between two dial positions.
    
    Based on:
    - Spectral centroid difference (timbral shift)
    - Harmonic complexity difference (chord change)
    - Temporal structure difference (rhythm change)
    
    Weighted by psychoacoustic sensitivity.
    """
    dv = abs(dials_a["I_vert"] - dials_b["I_vert"])
    dh = abs(dials_a["I_horiz"] - dials_b["I_horiz"])
    ds = abs(dials_a["I_spectral"] - dials_b["I_spectral"])

    # I_vert is most perceptible (harmony changes are obvious)
    # I_horiz is moderately perceptible (rhythm)
    # I_spectral is least perceptible (timbre is subtle)
    vert_weight = 1.0
    horiz_weight = 0.7
    spectral_weight = 0.4

    # Weber's law: JND scales with magnitude
    vert_jnd_scale = 0.05 * dials_a["I_vert"]
    horiz_jnd_scale = 0.08 * dials_a["I_horiz"]
    spectral_jnd_scale = 0.12 * dials_a["I_spectral"]

    # Normalized distances
    d_vert = dv / vert_jnd_scale if vert_jnd_scale > 0 else 0
    d_horiz = dh / horiz_jnd_scale if horiz_jnd_scale > 0 else 0
    d_spectral = ds / spectral_jnd_scale if spectral_jnd_scale > 0 else 0

    return math.sqrt(
        (vert_weight * d_vert) ** 2 +
        (horiz_weight * d_horiz) ** 2 +
        (spectral_weight * d_spectral) ** 2
    )


# ── Main JND Sweep ─────────────────────────────────────────────────────────

def run_jnd_experiment():
    print("Running JND experiment for each axis...")

    jnd_data = {}
    sensitivity_map = {}

    for axis_name, axis_info in AXES.items():
        print(f"\n  Axis: {axis_name}")
        ref_val = axis_info["ref"]
        results = []

        # Sweep both directions from reference
        for direction in ["up", "down"]:
            delta = 0.01
            step = 0

            while delta <= 1.5:
                if direction == "up":
                    test_val = ref_val + delta
                    if test_val > axis_info["max"]:
                        break
                else:
                    test_val = ref_val - delta
                    if test_val < axis_info["min"]:
                        break

                dials_test = dict(REFERENCE)
                dials_test[axis_name] = test_val

                dist = perceptual_distance(REFERENCE, dials_test)

                # Synthesize reference and test for this step
                step += 1
                results.append({
                    "direction": direction,
                    "delta": round(delta, 4),
                    "test_value": round(test_val, 4),
                    "perceptual_distance": round(dist, 4),
                    "noticeable": dist >= 1.0,  # threshold = 1 JND unit
                })

                delta += 0.01

        # Find JND (smallest delta where perceptual_distance >= 1.0)
        jnd_up = None
        jnd_down = None
        for r in results:
            if r["noticeable"]:
                if r["direction"] == "up" and jnd_up is None:
                    jnd_up = r["delta"]
                if r["direction"] == "down" and jnd_down is None:
                    jnd_down = r["delta"]

        avg_jnd = ((jnd_up or 0) + (jnd_down or 0)) / 2 if (jnd_up or jnd_down) else None

        jnd_data[axis_name] = {
            "reference_value": ref_val,
            "jnd_up": jnd_up,
            "jnd_down": jnd_down,
            "jnd_avg": round(avg_jnd, 4) if avg_jnd else None,
            "sweep": results,
        }

        # Sensitivity: inverse of JND (smaller JND = more sensitive)
        sensitivity = 1.0 / avg_jnd if avg_jnd and avg_jnd > 0 else 0
        sensitivity_map[axis_name] = {
            "jnd": round(avg_jnd, 4) if avg_jnd else None,
            "sensitivity": round(sensitivity, 4),
            "relative_sensitivity": None,  # filled after all axes
        }

        print(f"    JND (up): {jnd_up}, JND (down): {jnd_down}, Avg: {avg_jnd}")

    # Normalize relative sensitivities
    max_sens = max(s["sensitivity"] for s in sensitivity_map.values()) if sensitivity_map else 1
    for axis in sensitivity_map:
        sensitivity_map[axis]["relative_sensitivity"] = round(
            sensitivity_map[axis]["sensitivity"] / max_sens, 4
        )

    # ── Generate WAV pairs at JND ──────────────────────────────────────────
    print("\nGenerating JND WAV pairs...")
    ref_audio = synthesize_from_dials(REFERENCE)
    write_wav(OUTPUT_DIR / "jnd_reference.wav", ref_audio)

    for axis_name in AXES:
        jnd = jnd_data[axis_name].get("jnd_avg") or jnd_data[axis_name].get("jnd_up") or 0.1
        # Generate at JND
        dials_up = dict(REFERENCE)
        dials_up[axis_name] = REFERENCE[axis_name] + jnd
        dials_up[axis_name] = min(dials_up[axis_name], AXES[axis_name]["max"])

        audio_up = synthesize_from_dials(dials_up, seed=43)
        write_wav(OUTPUT_DIR / f"jnd_{axis_name}_plus.wav", audio_up)

        dials_down = dict(REFERENCE)
        dials_down[axis_name] = REFERENCE[axis_name] - jnd
        dials_down[axis_name] = max(dials_down[axis_name], AXES[axis_name]["min"])

        audio_down = synthesize_from_dials(dials_down, seed=44)
        write_wav(OUTPUT_DIR / f"jnd_{axis_name}_minus.wav", audio_down)

        print(f"  → {axis_name}: jnd_{axis_name}_plus.wav, jnd_{axis_name}_minus.wav")

    # ── Save results ───────────────────────────────────────────────────────
    with open(OUTPUT_DIR / "jnd_data.json", "w") as f:
        json.dump(jnd_data, f, indent=2)
    with open(OUTPUT_DIR / "sensitivity_map.json", "w") as f:
        json.dump(sensitivity_map, f, indent=2)

    print(f"\n  → jnd_data.json saved")
    print(f"  → sensitivity_map.json saved")

    # ── Summary ────────────────────────────────────────────────────────────
    sorted_axes = sorted(sensitivity_map.items(), key=lambda x: x[1]["sensitivity"], reverse=True)
    print("\n  Sensitivity ranking (most → least perceptible):")
    for axis, data in sorted_axes:
        print(f"    {axis}: sensitivity={data['sensitivity']:.4f}, JND={data['jnd']}")

    print("\n  Prediction check: I_vert (harmony) should be most noticeable")
    print(f"  Actual ranking: {[a for a, _ in sorted_axes]}")

    return jnd_data, sensitivity_map


if __name__ == "__main__":
    run_jnd_experiment()
    print("Experiment 2 complete.")
