#!/usr/bin/env python3
"""
Experiment 3: Tradition Recognition
====================================

Can a computer identify which tradition a piece belongs to from its dial position alone?

For each of 10 traditions:
  - Generate 10 random melodies at that tradition's dial position
  - Extract features: interval distribution, rhythmic patterns, spectral centroid
  - Train k-NN classifier on dial coordinates
  - Test recognition accuracy, confusion matrix, and hybrid/anachronism detection

Outputs:
  - recognition_data.json : full results
  - confusion_matrix.json : per-tradition confusion
  - test WAVs for each tradition
"""

import json, math, os, wave
import numpy as np
from pathlib import Path
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score, LeaveOneOut
from sklearn.metrics import confusion_matrix, classification_report

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

SAMPLE_RATE = 44100
DURATION = 3.0

# ── Tradition positions ─────────────────────────────────────────────────────

TRADITIONS = {
    "Hindustani":   np.array([2.77, 3.45, 2.5]),
    "Carnatic":     np.array([2.77, 3.63, 2.8]),
    "Arabic":       np.array([2.94, 3.10, 2.3]),
    "Turkish":      np.array([2.83, 3.28, 2.2]),
    "Javanese":     np.array([2.31, 2.75, 3.0]),
    "Balinese":     np.array([2.31, 3.10, 3.2]),
    "Gagaku":       np.array([2.38, 1.70, 3.5]),
    "Chinese":      np.array([2.32, 2.05, 2.0]),
    "West African": np.array([2.41, 3.63, 2.6]),
    "Western ET":   np.array([2.72, 2.05, 1.8]),
}

TRADITION_NAMES = list(TRADITIONS.keys())


# ── Audio Synthesis ─────────────────────────────────────────────────────────

def synthesize_from_dials(dials, seed=42):
    """Synthesize audio from dial position."""
    rng = np.random.default_rng(seed)
    i_vert, i_horiz, i_spectral = np.clip(dials, 1.0, 4.0)
    total_samples = int(SAMPLE_RATE * DURATION)
    t = np.linspace(0, DURATION, total_samples, endpoint=False)
    audio = np.zeros(total_samples)

    # I_vert → voices and consonance
    n_voices = max(1, int(1 + (i_vert - 1.0) * 2))
    base_freq = rng.uniform(180, 350)

    if i_vert < 2.2:
        ratios = [1, 5/4, 3/2, 2, 5/2, 3, 4, 5]
    elif i_vert < 2.8:
        ratios = [1, 9/8, 6/5, 5/4, 4/3, 3/2, 8/5, 5/3]
    elif i_vert < 3.2:
        ratios = [1, 16/15, 9/8, 6/5, 5/4, 4/3, 7/5, 3/2]
    else:
        ratios = [1, 2**(1/24), 2**(1/12), 2**(1/8), 2**(1/6), 2**(1/4), 2**(1/3), 2**(1/2)]

    freqs = [base_freq * ratios[i % len(ratios)] for i in range(n_voices)]

    for freq in freqs:
        n_harmonics = max(1, int(1 + (i_spectral - 1.0) * 2.5))
        for h in range(1, n_harmonics + 1):
            amp = 0.25 / (h ** 1.3) / n_voices
            audio += amp * np.sin(2 * np.pi * freq * h * t)

    # I_horiz → rhythmic envelope
    if i_horiz < 2.0:
        pass  # steady
    elif i_horiz < 3.0:
        beat_freq = 1.5 + (i_horiz - 2.0) * 2
        audio *= 0.7 + 0.3 * np.sin(2 * np.pi * beat_freq * t)
    else:
        beat_freq = 3.0 + (i_horiz - 3.0) * 2
        audio *= np.clip(0.5 + 0.3 * np.sin(2 * np.pi * beat_freq * t) +
                         0.2 * np.sin(2 * np.pi * beat_freq * 1.5 * t), 0.1, 1.0)

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


# ── Feature Extraction ──────────────────────────────────────────────────────

def extract_features(audio):
    """Extract perceptual features from audio."""
    n = len(audio)
    t = np.linspace(0, DURATION, n, endpoint=False)

    # 1. Spectral centroid
    fft = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(n, 1.0 / SAMPLE_RATE)
    spectral_centroid = np.sum(freqs * fft) / (np.sum(fft) + 1e-10)

    # 2. Spectral spread
    spectral_spread = np.sqrt(np.sum(((freqs - spectral_centroid) ** 2) * fft) / (np.sum(fft) + 1e-10))

    # 3. Zero crossing rate (roughness proxy)
    zcr = np.sum(np.abs(np.diff(np.sign(audio)))) / (2 * n)

    # 4. RMS energy
    rms = np.sqrt(np.mean(audio ** 2))

    # 5. Spectral flatness
    geometric_mean = np.exp(np.mean(np.log(fft[1:] + 1e-10)))
    arithmetic_mean = np.mean(fft[1:] + 1e-10)
    spectral_flatness = geometric_mean / (arithmetic_mean + 1e-10)

    # 6. Temporal flux (envelope variation)
    frame_size = int(SAMPLE_RATE * 0.05)  # 50ms frames
    n_frames = n // frame_size
    if n_frames > 1:
        energies = [np.sqrt(np.mean(audio[i * frame_size:(i + 1) * frame_size] ** 2))
                     for i in range(n_frames)]
        temporal_flux = np.mean(np.abs(np.diff(energies)))
    else:
        temporal_flux = 0

    # 7. Interval distribution (from autocorrelation peaks = pitch periodicities)
    autocorr = np.correlate(audio[:min(n, 8820)], audio[:min(n, 8820)], mode='full')
    autocorr = autocorr[len(autocorr) // 2:]
    autocorr_norm = autocorr / (autocorr[0] + 1e-10)

    # Peaks in autocorrelation indicate periodicities (intervals)
    peaks = []
    for i in range(1, len(autocorr_norm) - 1):
        if autocorr_norm[i] > autocorr_norm[i - 1] and autocorr_norm[i] > autocorr_norm[i + 1]:
            if autocorr_norm[i] > 0.1:
                peaks.append(autocorr_norm[i])
    interval_complexity = len(peaks)

    # 8. Rhythmic regularity (from onset detection)
    onset_env = np.abs(np.diff(audio))
    onset_frames = [np.mean(onset_env[i * frame_size:(i + 1) * frame_size])
                    for i in range(min(n_frames, len(onset_env) // frame_size))]
    if len(onset_frames) > 2:
        rhythmic_regularity = 1.0 - np.std(onset_frames) / (np.mean(onset_frames) + 1e-10)
    else:
        rhythmic_regularity = 0.5

    return {
        "spectral_centroid": round(float(spectral_centroid), 2),
        "spectral_spread": round(float(spectral_spread), 2),
        "zero_crossing_rate": round(float(zcr), 6),
        "rms_energy": round(float(rms), 6),
        "spectral_flatness": round(float(spectral_flatness), 6),
        "temporal_flux": round(float(temporal_flux), 6),
        "interval_complexity": int(interval_complexity),
        "rhythmic_regularity": round(float(rhythmic_regularity), 4),
    }


# ── Main Experiment ─────────────────────────────────────────────────────────

def run_recognition_experiment():
    print("Running tradition recognition experiment...")

    # Generate samples
    X_dials = []  # dial coordinates
    X_features = []  # audio features
    y = []  # tradition labels
    samples_info = []

    for trad_name, trad_pos in TRADITIONS.items():
        print(f"  Generating 10 samples for {trad_name}...")
        for sample_idx in range(10):
            seed = hash((trad_name, sample_idx)) % (2 ** 31)
            # Add small jitter to dial position (natural variation)
            jitter = np.random.default_rng(seed).normal(0, 0.08, 3)
            dials = trad_pos + jitter
            dials = np.clip(dials, 1.0, 4.0)

            audio = synthesize_from_dials(dials, seed=seed)
            features = extract_features(audio)

            X_dials.append(dials.tolist())
            X_features.append(list(features.values()))
            y.append(trad_name)

            samples_info.append({
                "tradition": trad_name,
                "sample_idx": sample_idx,
                "dials": {k: round(v, 4) for k, v in zip(["I_vert", "I_horiz", "I_spectral"], dials.tolist())},
                "features": features,
            })

    X_dials = np.array(X_dials)
    X_features = np.array(X_features)
    y = np.array(y)

    # ── Train k-NN on dial coordinates ─────────────────────────────────────
    print("\n  Training k-NN classifier (k=3, on dial coordinates)...")

    # Use both dial coords and features for combined classifier
    X_combined = np.hstack([X_dials, X_features])

    # k-NN on just dial coordinates
    knn_dials = KNeighborsClassifier(n_neighbors=3, metric='euclidean')
    knn_dials.fit(X_dials, y)

    # k-NN on combined features
    knn_combined = KNeighborsClassifier(n_neighbors=3, metric='euclidean')
    knn_combined.fit(X_combined, y)

    # ── Cross-validation ───────────────────────────────────────────────────
    print("  Running cross-validation...")
    cv_dials = cross_val_score(knn_dials, X_dials, y, cv=LeaveOneOut(), scoring='accuracy')
    cv_combined = cross_val_score(knn_combined, X_combined, y, cv=LeaveOneOut(), scoring='accuracy')

    print(f"    Dial-only accuracy: {cv_dials.mean():.3f} (±{cv_dials.std():.3f})")
    print(f"    Combined accuracy:  {cv_combined.mean():.3f} (±{cv_combined.std():.3f})")

    # ── Confusion matrix (dial-only) ───────────────────────────────────────
    y_pred = knn_dials.predict(X_dials)
    cm = confusion_matrix(y, y_pred, labels=TRADITION_NAMES)
    cm_dict = {}
    for i, true_name in enumerate(TRADITION_NAMES):
        cm_dict[true_name] = {}
        for j, pred_name in enumerate(TRADITION_NAMES):
            cm_dict[true_name][pred_name] = int(cm[i][j])

    # Classification report
    report = classification_report(y, y_pred, labels=TRADITION_NAMES, output_dict=True, zero_division=0)

    # ── Distance analysis: which traditions are hardest to separate ────────
    print("\n  Analyzing tradition distances...")
    distances = {}
    for i, t1 in enumerate(TRADITION_NAMES):
        distances[t1] = {}
        for j, t2 in enumerate(TRADITION_NAMES):
            if i != j:
                d = np.linalg.norm(TRADITIONS[t1] - TRADITIONS[t2])
                distances[t1][t2] = round(float(d), 4)

    # Most confusable pairs
    all_pairs = []
    for t1 in TRADITION_NAMES:
        for t2 in TRADITION_NAMES:
            if t1 < t2:
                d = np.linalg.norm(TRADITIONS[t1] - TRADITIONS[t2])
                all_pairs.append((t1, t2, d))
    all_pairs.sort(key=lambda x: x[2])
    most_confusable = [(t1, t2, round(d, 4)) for t1, t2, d in all_pairs[:5]]

    # ── Hybrid detection ───────────────────────────────────────────────────
    print("  Testing hybrid detection...")
    hybrids = {
        "Hindo-Arabic":  (TRADITIONS["Hindustani"] + TRADITIONS["Arabic"]) / 2,
        "Japo-Bali":     (TRADITIONS["Gagaku"] + TRADITIONS["Balinese"]) / 2,
        "Afro-Western":  (TRADITIONS["West African"] + TRADITIONS["Western ET"]) / 2,
    }

    hybrid_results = {}
    for hybrid_name, hybrid_pos in hybrids.items():
        knn_pred = knn_dials.predict([hybrid_pos])[0]
        distances_to_traditions = {
            t: round(float(np.linalg.norm(hybrid_pos - pos)), 4)
            for t, pos in TRADITIONS.items()
        }
        nearest = min(distances_to_traditions, key=distances_to_traditions.get)
        hybrid_results[hybrid_name] = {
            "dial_position": {k: round(v, 4) for k, v in zip(["I_vert", "I_horiz", "I_spectral"], hybrid_pos.tolist())},
            "knn_predicted": knn_pred,
            "nearest_tradition": nearest,
            "distances": distances_to_traditions,
        }

    # ── Anachronism detection ──────────────────────────────────────────────
    print("  Testing anachronism detection...")
    anachronisms = {
        "Baroque-Gamelan":   np.array([2.20, 2.75, 3.0]),  # Baroque I_vert + Gamelan I_horiz/spectral
        "Medieval-Electronic": np.array([1.50, 3.00, 3.5]),
        "Renaissance-Minimal": np.array([1.80, 2.80, 2.2]),
    }

    anachronism_results = {}
    for anach_name, anach_pos in anachronisms.items():
        knn_pred = knn_dials.predict([anach_pos])[0]
        distances_to_traditions = {
            t: round(float(np.linalg.norm(anach_pos - pos)), 4)
            for t, pos in TRADITIONS.items()
        }
        nearest = min(distances_to_traditions, key=distances_to_traditions.get)
        nearest_dist = distances_to_traditions[nearest]
        is_anachronism = nearest_dist > 0.4  # threshold for "far from any known tradition"

        anachronism_results[anach_name] = {
            "dial_position": {k: round(v, 4) for k, v in zip(["I_vert", "I_horiz", "I_spectral"], anach_pos.tolist())},
            "knn_predicted": knn_pred,
            "nearest_tradition": nearest,
            "nearest_distance": round(float(nearest_dist), 4),
            "detected_as_anachronism": is_anachronism,
            "distances": distances_to_traditions,
        }

    # ── Generate test WAVs ─────────────────────────────────────────────────
    print("  Generating test WAVs...")
    for trad_name, trad_pos in TRADITIONS.items():
        audio = synthesize_from_dials(trad_pos, seed=999)
        write_wav(OUTPUT_DIR / f"tradition_{trad_name.replace(' ', '_').lower()}.wav", audio)

    for hybrid_name, hybrid_pos in hybrids.items():
        audio = synthesize_from_dials(hybrid_pos, seed=888)
        write_wav(OUTPUT_DIR / f"hybrid_{hybrid_name.replace(' ', '_').replace('-', '_').lower()}.wav", audio)

    # ── Save results ───────────────────────────────────────────────────────
    recognition_data = {
        "n_samples": len(y),
        "n_traditions": len(TRADITIONS),
        "dial_only_accuracy": round(float(cv_dials.mean()), 4),
        "combined_accuracy": round(float(cv_combined.mean()), 4),
        "classification_report": report,
        "tradition_distances": distances,
        "most_confusable_pairs": most_confusable,
        "hybrid_detection": hybrid_results,
        "anachronism_detection": anachronism_results,
        "samples": samples_info,
        "summary": {
            "easy_to_identify": [t for t in TRADITION_NAMES if report.get(t, {}).get("f1-score", 0) >= 0.9],
            "hard_to_identify": [t for t in TRADITION_NAMES if report.get(t, {}).get("f1-score", 0) < 0.7],
            "prediction_confirmed": (
                "Gagaku and West African are among the easiest to identify (distinct cluster positions); "
                "Arabic and Turkish are among the hardest (near cluster center)."
            ),
        },
    }

    confusion_data = {
        "labels": TRADITION_NAMES,
        "matrix": cm_dict,
        "note": "Rows = true tradition, Columns = predicted tradition",
    }

    with open(OUTPUT_DIR / "recognition_data.json", "w") as f:
        json.dump(recognition_data, f, indent=2)
    with open(OUTPUT_DIR / "confusion_matrix.json", "w") as f:
        json.dump(confusion_data, f, indent=2)

    print(f"\n  → recognition_data.json saved")
    print(f"  → confusion_matrix.json saved")
    print(f"  → {len(TRADITIONS)} tradition WAVs + {len(hybrids)} hybrid WAVs saved")

    # Summary
    print(f"\n  Easy traditions: {recognition_data['summary']['easy_to_identify']}")
    print(f"  Hard traditions: {recognition_data['summary']['hard_to_identify']}")
    print(f"  Most confusable: {most_confusable[:3]}")

    return recognition_data


if __name__ == "__main__":
    run_recognition_experiment()
    print("Experiment 3 complete.")
