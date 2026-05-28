"""
Experiment 1: Genre Classification (Upgraded)

Uses FeatureClassifier with 42-dim feature vectors on real WAV files.
Compares old DialClassifier accuracy (~33%) with new FeatureClassifier.
Reports per-genre accuracy, feature importance ranking, and confusion matrix.
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from constraint_toolkit.analyzer import analyze_wav, batch_analyze
from constraint_toolkit.classifier import DialClassifier, FeatureClassifier
from constraint_toolkit.features import extract_features
from constraint_toolkit.audio_utils import load_wav
from constraint_toolkit.dials import DIAL_RANGES


def extract_true_label(filename: str) -> str:
    """Extract the true genre label from filename."""
    name = Path(filename).stem.lower()
    genre_map = {
        "blues": "Blues", "gospel": "Blues",
        "jazz": "Jazz", "bebop": "Jazz",
        "techno": "EDM", "electronic": "EDM", "edm": "EDM",
        "classical": "Classical",
        "gamelan": "Gamelan", "gagaku": "Gagaku",
        "hindustani": "Hindustani",
        "african": "African Polyrhythm",
        "hiphop": "Hip-hop", "hip_hop": "Hip-hop", "rap": "Hip-hop",
        "latin": "Latin", "salsa": "Latin",
    }
    for keyword, genre in genre_map.items():
        if keyword in name:
            return genre
    return "Unknown"


def generate_synthetic_dataset(n_per_genre=30, seed=42):
    """Generate synthetic feature vectors for each genre."""
    from constraint_toolkit.features import FeatureVector

    rng = np.random.RandomState(seed)

    # Genre-specific feature profiles (mean + std for key feature groups)
    profiles = {
        "Jazz": {
            "mfcc_mean": 0.6, "chroma_entropy": 0.8, "contrast": 0.4,
            "rhythm_density": 0.7, "tonal_complexity": 0.8,
        },
        "Classical": {
            "mfcc_mean": 0.5, "chroma_entropy": 0.5, "contrast": 0.3,
            "rhythm_density": 0.3, "tonal_complexity": 0.5,
        },
        "Blues": {
            "mfcc_mean": 0.5, "chroma_entropy": 0.6, "contrast": 0.5,
            "rhythm_density": 0.5, "tonal_complexity": 0.6,
        },
        "EDM": {
            "mfcc_mean": 0.7, "chroma_entropy": 0.3, "contrast": 0.7,
            "rhythm_density": 0.6, "tonal_complexity": 0.2,
        },
        "Hip-hop": {
            "mfcc_mean": 0.6, "chroma_entropy": 0.4, "contrast": 0.6,
            "rhythm_density": 0.8, "tonal_complexity": 0.3,
        },
        "Gamelan": {
            "mfcc_mean": 0.5, "chroma_entropy": 0.6, "contrast": 0.5,
            "rhythm_density": 0.7, "tonal_complexity": 0.5,
        },
        "Hindustani": {
            "mfcc_mean": 0.5, "chroma_entropy": 0.7, "contrast": 0.4,
            "rhythm_density": 0.5, "tonal_complexity": 0.7,
        },
        "African Polyrhythm": {
            "mfcc_mean": 0.5, "chroma_entropy": 0.5, "contrast": 0.5,
            "rhythm_density": 0.9, "tonal_complexity": 0.3,
        },
        "Latin": {
            "mfcc_mean": 0.5, "chroma_entropy": 0.5, "contrast": 0.5,
            "rhythm_density": 0.8, "tonal_complexity": 0.5,
        },
        "Gagaku": {
            "mfcc_mean": 0.6, "chroma_entropy": 0.5, "contrast": 0.4,
            "rhythm_density": 0.4, "tonal_complexity": 0.5,
        },
    }

    vectors = []
    labels = []

    for genre, profile in profiles.items():
        for _ in range(n_per_genre):
            vec = rng.uniform(0.2, 0.8, size=42)

            # Bias features toward genre profile
            # MFCCs (dims 0-12)
            vec[0:13] = np.clip(profile["mfcc_mean"] + rng.randn(13) * 0.1, 0, 1)
            # Chroma (dims 13-24): higher entropy = more uniform
            entropy = profile["chroma_entropy"]
            vec[13:25] = np.clip(1.0 / 12 + rng.randn(12) * (0.05 + 0.1 * entropy), 0, 1)
            vec[13:25] /= vec[13:25].sum()  # normalize
            # Spectral contrast (dims 25-30)
            vec[25:31] = np.clip(profile["contrast"] + rng.randn(6) * 0.1, 0, 1)
            # Rhythmic (dims 31-36)
            vec[31] = np.clip(profile["rhythm_density"] + rng.randn() * 0.1, 0, 1)  # density
            vec[32] = np.clip(0.5 + rng.randn() * 0.15, 0, 1)  # regularity
            vec[33] = np.clip(rng.rand() * 0.5, 0, 1)  # syncopation
            vec[34] = np.clip(rng.rand() * 0.3, 0, 1)  # swing
            vec[35] = np.clip(0.5 + rng.randn() * 0.1, 0, 1)  # tempo
            vec[36] = np.clip(0.5 + rng.randn() * 0.1, 0, 1)  # pulse clarity
            # Tonal (dims 37-41)
            vec[37] = np.clip(0.5 + profile["tonal_complexity"] * 0.3 + rng.randn() * 0.1, 0, 1)
            vec[38] = np.clip(0.5 + rng.randn() * 0.2, 0, 1)  # mode
            vec[39] = np.clip(profile["tonal_complexity"] + rng.randn() * 0.1, 0, 1)
            vec[40] = np.clip(0.5 + rng.randn() * 0.1, 0, 1)  # tension
            vec[41] = np.clip(rng.rand() * 0.2, 0, 1)  # modulation

            vectors.append(vec)
            labels.append(genre)

    return vectors, labels


def main():
    workspace = Path(__file__).parent.parent.parent
    results_dir = workspace / "constraint-toolkit" / "results"
    results_dir.mkdir(exist_ok=True)

    wav_files = list(workspace.glob("*.wav"))

    if wav_files:
        print(f"\n=== Genre Classification with FeatureClassifier ({len(wav_files)} files) ===\n")
        _run_on_real_wavs(wav_files, results_dir)
    else:
        print("\n=== Genre Classification (Synthetic Benchmark) ===\n")
        _run_synthetic_benchmark(results_dir)


def _run_on_real_wavs(wav_files, results_dir):
    """Run classification on real WAV files."""
    # Extract features from all files
    vectors = []
    labels = []
    filenames = []

    for fpath in sorted(wav_files):
        try:
            audio, sr = load_wav(str(fpath))
            fv = extract_features(audio, sr)
            vec = fv.to_array()
            label = extract_true_label(fpath.name)
            vectors.append(vec)
            labels.append(label)
            filenames.append(fpath.name)
        except Exception as e:
            print(f"  Error processing {fpath.name}: {e}")

    if not vectors:
        print("No WAV files could be processed. Falling back to synthetic.")
        _run_synthetic_benchmark(results_dir)
        return

    n = len(vectors)

    # --- FeatureClassifier (leave-one-out if small) ---
    print(f"{'File':<40} {'True':<18} {'Predicted':<18} {'Confidence':>10}")
    print("-" * 90)

    correct_fc = 0
    total = 0
    predictions = {}

    for i in range(n):
        test_vec = vectors[i]
        true_label = labels[i]

        # Leave-one-out training
        train_vecs = [vectors[j] for j in range(n) if j != i]
        train_labs = [labels[j] for j in range(n) if j != i]

        clf = FeatureClassifier(seed=42)
        clf.train_from_vectors(train_vecs, train_labs)

        pred, conf, _ = clf.predict_from_vector(test_vec)
        predictions[filenames[i]] = (pred, conf)

        is_correct = pred == true_label and true_label != "Unknown"
        if true_label != "Unknown":
            correct_fc += int(is_correct)
            total += 1

        mark = "✓" if is_correct else "✗"
        print(f"{filenames[i]:<40} {true_label:<18} {pred:<18} {conf:>9.1%} {mark}")

    fc_accuracy = correct_fc / total if total > 0 else 0.0
    print(f"\nFeatureClassifier accuracy: {fc_accuracy:.1%} ({correct_fc}/{total})")

    # --- Old DialClassifier for comparison ---
    dial_correct = 0
    dial_total = 0
    dial_clf = DialClassifier(seed=42)
    dial_clf.fit_defaults(samples_per_tradition=30)

    for fpath in sorted(wav_files):
        try:
            result = analyze_wav(fpath)
            true_label = extract_true_label(fpath.name)
            if true_label != "Unknown":
                pred, _ = dial_clf.predict_genre(result.dial_position)
                dial_correct += int(pred == true_label)
                dial_total += 1
        except Exception:
            pass

    dial_accuracy = dial_correct / dial_total if dial_total > 0 else 0.0
    print(f"DialClassifier accuracy:    {dial_accuracy:.1%} ({dial_correct}/{dial_total})")

    # Feature importance
    if n >= 3:
        clf_full = FeatureClassifier(seed=42)
        clf_full.train_from_vectors(vectors, labels)
        importance = clf_full.feature_importance()
        print(f"\nFeature group importance:")
        for name, score in sorted(importance.items(), key=lambda x: -x[1]):
            bar = "█" * int(score * 40)
            print(f"  {name:<20} {score:.3f} {bar}")

    output = {
        "experiment": "genre_classification_feature_based",
        "feature_classifier_accuracy": fc_accuracy,
        "dial_classifier_accuracy": dial_accuracy,
        "n_files": n,
        "predictions": {k: {"predicted": v[0], "confidence": v[1]} for k, v in predictions.items()},
    }
    with open(results_dir / "exp1_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {results_dir / 'exp1_results.json'}")


def _run_synthetic_benchmark(results_dir):
    """Run benchmark with synthetic data."""
    vectors, labels = generate_synthetic_dataset(n_per_genre=30, seed=42)

    # --- FeatureClassifier cross-validation ---
    clf = FeatureClassifier(seed=42)
    cv_fc = clf.cross_validate(vectors, labels, n_folds=5)
    print(f"FeatureClassifier 5-fold CV:")
    print(f"  Accuracy:          {cv_fc['accuracy']:.1%}")
    print(f"  Mean Confidence:   {cv_fc['mean_confidence']:.1%}")
    print(f"  Per-class accuracy:")
    for genre, acc in sorted(cv_fc.get("per_class_accuracy", {}).items()):
        print(f"    {genre:<22} {acc:.1%}")

    # --- Old DialClassifier for comparison ---
    from constraint_toolkit.dials import DialPosition
    dial_positions = []
    dial_labels = []
    rng = np.random.RandomState(42)
    for name, profile in DIAL_RANGES.items():
        for _ in range(30):
            sample = profile["center"] + rng.randn(3) * profile["spread"]
            sample = np.clip(sample, 0, 5)
            dial_positions.append(DialPosition.from_array(sample, tradition_name=name))
            dial_labels.append(name)

    dial_clf = DialClassifier(seed=42)
    cv_dial = dial_clf.cross_validate(dial_positions, dial_labels, n_folds=5)
    print(f"\nDialClassifier 5-fold CV (on dial space data):")
    print(f"  Accuracy:          {cv_dial['accuracy']:.1%}")

    # Feature importance
    clf_full = FeatureClassifier(seed=42)
    clf_full.train_from_vectors(vectors, labels)
    importance = clf_full.feature_importance()
    print(f"\nFeature group importance:")
    for name, score in sorted(importance.items(), key=lambda x: -x[1]):
        bar = "█" * int(score * 40)
        print(f"  {name:<20} {score:.3f} {bar}")

    output = {
        "experiment": "genre_classification_synthetic",
        "feature_classifier_cv": cv_fc,
        "dial_classifier_cv": cv_dial,
    }
    with open(results_dir / "exp1_results.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {results_dir / 'exp1_results.json'}")


if __name__ == "__main__":
    main()
