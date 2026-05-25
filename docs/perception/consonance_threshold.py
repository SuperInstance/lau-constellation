#!/usr/bin/env python3
"""
Experiment 1: Consonance Threshold Detector
============================================

Find the exact point where intervals transition from "consonant" to "dissonant"
by sweeping from unison (1/1) through to the tritone (~√2) in 1-cent increments.

At each step compute:
- Tenney height (log₂(p·q) for ratio p/q in lowest terms)
- Plomp-Levelt roughness
- Framework consonance score (from our neuro-harmonic model)

Find the "cliff" — where consonance drops fastest.

Outputs:
- threshold_data.json : full sweep data + cliff analysis
- sweep.wav           : 60-second continuous sweep from consonance to dissonance
"""

import json, math, os, struct, wave
import numpy as np
from pathlib import Path
from fractions import Fraction

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

SAMPLE_RATE = 44100
SWEEP_DURATION = 60.0  # seconds

# ── Tradition dial positions (from neuro_harmonic.py) ───────────────────────
TRADITIONS = {
    "Hindustani":   {"I_vert": 2.77, "I_horiz": 3.45, "I_spectral": 2.5},
    "Carnatic":     {"I_vert": 2.77, "I_horiz": 3.63, "I_spectral": 2.8},
    "Arabic":       {"I_vert": 2.94, "I_horiz": 3.10, "I_spectral": 2.3},
    "Turkish":      {"I_vert": 2.83, "I_horiz": 3.28, "I_spectral": 2.2},
    "Javanese":     {"I_vert": 2.31, "I_horiz": 2.75, "I_spectral": 3.0},
    "Balinese":     {"I_vert": 2.31, "I_horiz": 3.10, "I_spectral": 3.2},
    "Gagaku":       {"I_vert": 2.38, "I_horiz": 1.70, "I_spectral": 3.5},
    "Chinese":      {"I_vert": 2.32, "I_horiz": 2.05, "I_spectral": 2.0},
    "West African": {"I_vert": 2.41, "I_horiz": 3.63, "I_spectral": 2.6},
    "Western ET":   {"I_vert": 2.72, "I_horiz": 2.05, "I_spectral": 1.8},
}


# ── Consonance Metrics ──────────────────────────────────────────────────────

def tenney_height(cents):
    """
    Tenney height for an interval of given cents.
    We find the best simple-ratio approximation within ±5 cents and compute
    H(p/q) = log₂(p) + log₂(q) for the ratio p/q in lowest terms.
    Lower = more consonant.
    """
    ratio = 2 ** (cents / 1200.0)

    # Search for best simple ratio with numerator, denominator ≤ 1000
    best_th = float('inf')
    for denom in range(1, 501):
        numer = round(ratio * denom)
        if numer < 1 or numer > 1000:
            continue
        actual_ratio = numer / denom
        actual_cents = 1200 * math.log2(actual_ratio)
        if abs(actual_cents - cents) < 5:  # within 5 cents
            f = Fraction(numer, denom)
            th = math.log2(f.numerator) + math.log2(f.denominator)
            if th < best_th:
                best_th = th
    return best_th if best_th < float('inf') else 10.0  # cap for very complex ratios


def plomp_levelt_roughness(cents, base_freq=261.63):
    """
    Plomp-Levelt roughness model.
    For two sinusoids at frequencies f1 and f2, roughness peaks when
    |f2-f1| ≈ 0.25 × critical bandwidth.
    We model with a Gaussian-like curve centered on ~1.2 Bark difference.
    Returns 0 (no roughness) to 1 (maximum roughness).
    """
    ratio = 2 ** (cents / 1200.0)
    f1 = base_freq
    f2 = base_freq * ratio

    # Critical bandwidth approximation (Bark scale)
    bark1 = 13 * math.atan(0.00076 * f1) + 3.5 * math.atan((f1 / 7500) ** 2)
    bark2 = 13 * math.atan(0.00076 * f2) + 3.5 * math.atan((f2 / 7500) ** 2)
    delta_bark = abs(bark2 - bark1)

    # Roughness peaks at ~1.2 Bark, falls off on either side
    # R = exp(-((δ_bark - 1.2)² / (2 × 0.6²)))
    roughness = math.exp(-((delta_bark - 1.2) ** 2) / (2 * 0.6 ** 2))

    # Reduce for very small intervals (unison zone) and very large intervals
    if cents < 15:
        roughness *= cents / 15.0
    if cents > 1100:
        roughness *= max(0, (1200 - cents) / 100.0)

    return roughness


def framework_consonance_score(cents, i_vert=2.72, i_horiz=2.05, i_spectral=1.8):
    """
    Our framework's consonance score combining Tenney height and Plomp-Levelt
    with tradition-weighted expectations.
    
    Higher = more consonant. Normalized to 0-1.
    """
    th = tenney_height(cents)
    pl = plomp_levelt_roughness(cents)

    # Normalize Tenney height: simple ratios have TH ~1-3, complex ~7+
    th_normalized = max(0, 1.0 - (th - 1.0) / 6.0)

    # PL roughness is already 0-1, invert for consonance
    pl_consonance = 1.0 - pl

    # Weight by tradition dials
    # Higher I_vert means more tolerance for complex intervals
    vert_tolerance = (i_vert - 1.5) / 3.0  # 0 to ~1
    # Higher I_spectral means timbre masks dissonance
    spectral_mask = (i_spectral - 1.5) / 2.5

    # Combined score
    raw = 0.4 * th_normalized + 0.4 * pl_consonance + 0.2 * (vert_tolerance + spectral_mask) / 2
    return max(0.0, min(1.0, raw))


# ── Published human perception data (approximate) ───────────────────────────
# From Vassilakis (2001), Huron (1994), and McDermott et al. (2010)
# Mapped as approximate consonance ratings for standard Western intervals
HUMAN_PERCEPTION = {
    0:    1.00,   # Unison
    100:  0.35,   # Minor second
    200:  0.50,   # Major second
    300:  0.65,   # Minor third
    400:  0.72,   # Major third
    500:  0.40,   # Perfect fourth
    600:  0.25,   # Tritone
    700:  0.85,   # Perfect fifth
    800:  0.60,   # Minor sixth
    900:  0.70,   # Major sixth
    1000: 0.50,   # Minor seventh
    1100: 0.40,   # Major seventh
    1200: 0.95,   # Octave
}

# Interpolate for arbitrary cents
def human_perception_at(cents):
    keys = sorted(HUMAN_PERCEPTION.keys())
    if cents <= keys[0]:
        return HUMAN_PERCEPTION[keys[0]]
    if cents >= keys[-1]:
        return HUMAN_PERCEPTION[keys[-1]]
    for i in range(len(keys) - 1):
        if keys[i] <= cents <= keys[i + 1]:
            t = (cents - keys[i]) / (keys[i + 1] - keys[i])
            return HUMAN_PERCEPTION[keys[i]] * (1 - t) + HUMAN_PERCEPTION[keys[i + 1]] * t
    return 0.5


# ── Main Sweep ──────────────────────────────────────────────────────────────

def run_sweep():
    print("Running consonance threshold sweep (0-1200 cents, 1-cent steps)...")

    sweep_data = []
    for cents in range(0, 1201):
        th = tenney_height(cents)
        pl = plomp_levelt_roughness(cents)
        fw = framework_consonance_score(cents)
        hp = human_perception_at(cents)

        sweep_data.append({
            "cents": cents,
            "tenney_height": round(th, 4),
            "plomp_levelt_roughness": round(pl, 4),
            "framework_consonance": round(fw, 4),
            "human_perception": round(hp, 4),
        })

    # ── Find cliffs (steepest drops) ────────────────────────────────────────
    cliffs = {"tenney_height": [], "plomp_levelt": [], "framework": [], "human": []}

    for key in ["framework_consonance", "human_perception"]:
        max_drop = 0
        cliff_cents = 0
        for i in range(1, len(sweep_data)):
            drop = sweep_data[i - 1][key] - sweep_data[i][key]
            if drop > max_drop:
                max_drop = drop
                cliff_cents = sweep_data[i]["cents"]
        cliffs[key] = {"cents": cliff_cents, "max_drop_per_cent": round(max_drop, 6)}

    # Also find cliff for roughness (steepest *increase*)
    max_rise = 0
    cliff_rise_cents = 0
    for i in range(1, len(sweep_data)):
        rise = sweep_data[i]["plomp_levelt_roughness"] - sweep_data[i - 1]["plomp_levelt_roughness"]
        if rise > max_rise:
            max_rise = rise
            cliff_rise_cents = sweep_data[i]["cents"]
    cliffs["plomp_levelt_roughness"] = {"cents": cliff_rise_cents, "max_rise_per_cent": round(max_rise, 6)}

    # Tenney height cliff
    max_th_rise = 0
    cliff_th_cents = 0
    for i in range(1, len(sweep_data)):
        rise = sweep_data[i]["tenney_height"] - sweep_data[i - 1]["tenney_height"]
        if rise > max_th_rise:
            max_th_rise = rise
            cliff_th_cents = sweep_data[i]["cents"]
    cliffs["tenney_height"] = {"cents": cliff_th_cents, "max_rise_per_cent": round(max_th_rise, 6)}

    # ── Tradition-specific threshold predictions ────────────────────────────
    tradition_thresholds = {}
    for name, dials in TRADITIONS.items():
        # Find where consonance crosses 0.5 for this tradition
        threshold = None
        for cents in range(0, 1201):
            score = framework_consonance_score(cents, dials["I_vert"], dials["I_horiz"], dials["I_spectral"])
            if score < 0.5 and threshold is None:
                threshold = cents
                break
        tradition_thresholds[name] = {
            "consonance_threshold_cents": threshold or 1200,
            "dials": dials,
        }

    # ── Correlation between framework and human data ────────────────────────
    fw_scores = [d["framework_consonance"] for d in sweep_data]
    hp_scores = [d["human_perception"] for d in sweep_data]
    fw_mean = sum(fw_scores) / len(fw_scores)
    hp_mean = sum(hp_scores) / len(hp_scores)
    covariance = sum((f - fw_mean) * (h - hp_mean) for f, h in zip(fw_scores, hp_scores)) / len(fw_scores)
    fw_std = (sum((f - fw_mean) ** 2 for f in fw_scores) / len(fw_scores)) ** 0.5
    hp_std = (sum((h - hp_mean) ** 2 for h in hp_scores) / len(hp_scores)) ** 0.5
    correlation = covariance / (fw_std * hp_std) if fw_std * hp_std > 0 else 0

    # ── Save threshold_data.json ────────────────────────────────────────────
    result = {
        "sweep": sweep_data,
        "cliffs": cliffs,
        "tradition_thresholds": tradition_thresholds,
        "framework_vs_human_correlation": round(correlation, 4),
        "summary": {
            "framework_consonance_cliff_at_cents": cliffs["framework_consonance"]["cents"],
            "human_perception_cliff_at_cents": cliffs["human_perception"]["cents"],
            "framework_human_correlation_r": round(correlation, 4),
            "western_threshold_cents": tradition_thresholds.get("Western ET", {}).get("consonance_threshold_cents"),
            "prediction": (
                "The consonance cliff is near the minor second (~100 cents) for roughness-based metrics, "
                "but the major perceptual transition zone spans 200-400 cents. "
                "Traditions with higher I_vert (Arabic, Hindustani) tolerate more dissonance before threshold."
            ),
        },
    }

    with open(OUTPUT_DIR / "threshold_data.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"  → threshold_data.json saved ({len(sweep_data)} data points)")
    print(f"  Framework-human correlation: r = {correlation:.4f}")
    print(f"  Framework consonance cliff: {cliffs['framework_consonance']['cents']} cents")
    print(f"  Human perception cliff: {cliffs['human_perception']['cents']} cents")

    return sweep_data


# ── Generate Sweep WAV ──────────────────────────────────────────────────────

def generate_sweep_wav(sweep_data):
    """
    Generate a 60-second WAV that sweeps from unison (0 cents) to octave (1200 cents).
    Uses two sine tones: a fixed reference and a sweeping tone.
    Amplitude modulated by consonance score so dissonant intervals sound 'rougher'.
    """
    print("Generating 60-second consonance sweep WAV...")

    total_samples = int(SAMPLE_RATE * SWEEP_DURATION)
    t = np.linspace(0, SWEEP_DURATION, total_samples, endpoint=False)
    base_freq = 261.63  # C4

    # Sweep from unison to octave
    sweep_cents = np.linspace(0, 1200, total_samples)
    sweep_ratios = 2 ** (sweep_cents / 1200.0)

    # Fixed reference tone
    ref_tone = 0.4 * np.sin(2 * np.pi * base_freq * t)

    # Sweeping tone
    sweep_freqs = base_freq * sweep_ratios
    phase = 2 * np.pi * np.cumsum(sweep_freqs) / SAMPLE_RATE
    sweep_tone = 0.4 * np.sin(phase)

    # Add slight amplitude modulation based on consonance
    # (dissonant = slightly quieter to simulate perceptual masking, but still audible)
    consonance_env = np.array([
        framework_consonance_score(c) for c in sweep_cents[::1000]
    ])
    # Interpolate to full length
    from scipy.interpolate import interp1d
    interp_consonance = interp1d(
        np.linspace(0, total_samples, len(consonance_env)),
        consonance_env,
        kind='linear',
        fill_value='extrapolate'
    )
    env = interp_consonance(np.arange(total_samples))
    # Mix: consonant sections louder, but keep everything audible
    amp = 0.5 + 0.5 * env  # range 0.5-1.0

    audio = (ref_tone + sweep_tone * amp) / 2.0

    # Normalize
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.85

    # Write WAV
    filepath = OUTPUT_DIR / "sweep.wav"
    pcm = (audio * 32767).astype(np.int16)
    with wave.open(str(filepath), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm.tobytes())

    print(f"  → sweep.wav saved ({SWEEP_DURATION:.0f}s, {SAMPLE_RATE}Hz)")


# ── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sweep_data = run_sweep()
    generate_sweep_wav(sweep_data)
    print("Experiment 1 complete.")
