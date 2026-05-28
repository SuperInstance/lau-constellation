"""
Experiment 15: Production Classification Benchmark

Loads ALL workspace WAV files, extracts full features, runs stratified
5-fold cross-validation, and compares multiple classifiers with statistical
significance testing.
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from constraint_toolkit.datasets import Dataset, label_from_filename
from constraint_toolkit.classifier import FeatureClassifier
from constraint_toolkit.dials import DIAL_RANGES, DialPosition, classify_dial_cluster
from constraint_toolkit.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_with_ci,
    permutation_test,
)
from constraint_toolkit.visualize import (
    ascii_confusion_matrix,
    ascii_bar_chart,
    format_results_table,
)

WORKSPACE = Path("/home/phoenix/.openclaw/workspace")


def run_baseline_random(labels: list[str], seed: int = 42) -> list[str]:
    """Random baseline: guess proportionally to class frequency."""
    rng = np.random.RandomState(seed)
    unique, counts = np.unique(labels, return_counts=True)
    probs = counts / counts.sum()
    return list(rng.choice(unique, size=len(labels), p=probs))


def run_nearest_centre(X: np.ndarray, y: list[str]) -> list[str]:
    """Nearest centroid classifier."""
    labels_unique = sorted(set(y))
    centres = {}
    for lab in labels_unique:
        mask = [yi == lab for yi in y]
        centres[lab] = X[mask].mean(axis=0)

    preds = []
    for row in X:
        best_lab = min(centres, key=lambda l: np.linalg.norm(row - centres[l]))
        preds.append(best_lab)
    return preds


def main():
    print("=" * 70)
    print("EXPERIMENT 15: Production Classification Benchmark")
    print("=" * 70)
    print()

    # Load dataset
    print("📂 Loading workspace WAV files...")
    t0 = time.time()
    ds = Dataset()
    loaded = ds.load_workspace_wavs(WORKSPACE, pattern="*.wav")
    elapsed = time.time() - t0
    print(f"   Loaded {len(loaded)} files in {elapsed:.1f}s")

    if ds.size == 0:
        print("ERROR: No WAV files found!")
        return

    # Print dataset summary
    print(f"\n📊 Dataset Summary:")
    print(f"   Total samples: {ds.size}")
    print(f"   Unique labels: {ds.unique_labels}")
    for lab, cnt in sorted(ds.label_counts.items()):
        print(f"     {lab}: {cnt}")

    # Get feature matrix
    X, y = ds.get_feature_matrix()
    print(f"\n   Feature matrix: {X.shape}")

    # ---- 1. Random Baseline ----
    print("\n" + "─" * 50)
    print("1. RANDOM BASELINE")
    print("─" * 50)
    random_preds = run_baseline_random(y, seed=42)
    acc_rand, ci_lo, ci_hi = accuracy_with_ci(y, random_preds)
    print(f"   Accuracy: {acc_rand:.3f} (95% CI: [{ci_lo:.3f}, {ci_hi:.3f}])")

    # ---- 2. Nearest Centroid ----
    print("\n" + "─" * 50)
    print("2. NEAREST CENTROID")
    print("─" * 50)
    nc_preds = run_nearest_centre(X, y)
    acc_nc, ci_lo_nc, ci_hi_nc = accuracy_with_ci(y, nc_preds)
    print(f"   Accuracy: {acc_nc:.3f} (95% CI: [{ci_lo_nc:.3f}, {ci_hi_nc:.3f}])")

    # ---- 3. FeatureClassifier (5-fold CV) ----
    print("\n" + "─" * 50)
    print("3. FEATURE CLASSIFIER (5-fold Cross-Validation)")
    print("─" * 50)
    cv_results = ds.cross_validate(FeatureClassifier, k=5, seed=42)
    acc_cv = cv_results["accuracy"]
    print(f"   CV Accuracy: {acc_cv:.3f}")
    print(f"   Per-fold accuracies: {[f'{a:.3f}' for a in cv_results['per_fold_accuracies']]}")
    print(f"   Mean confidence: {cv_results['mean_confidence']:.3f}")

    if cv_results["per_class_accuracy"]:
        print("\n   Per-class accuracy:")
        print(ascii_bar_chart(cv_results["per_class_accuracy"], title=""))

    # ---- 4. Bootstrapped accuracy ----
    print("\n" + "─" * 50)
    print("4. BOOTSTRAPPED ACCURACY (n=100)")
    print("─" * 50)
    boot = ds.bootstrapped_accuracy(FeatureClassifier, n=100, seed=42)
    print(f"   Mean: {boot['mean']:.3f} ± {boot['std']:.3f}")
    print(f"   95% CI: [{boot['ci_lower']:.3f}, {boot['ci_upper']:.3f}]")

    # ---- 5. Full classification report ----
    print("\n" + "─" * 50)
    print("5. CLASSIFICATION REPORT (FeatureClassifier on full dataset)")
    print("─" * 50)
    # Train on all data, predict on all (overfit but shows separability)
    clf = FeatureClassifier(seed=42)
    clf.train_from_vectors([s.feature_array for s in ds.audio_samples],
                           [s.label for s in ds.audio_samples])
    all_preds = []
    for s in ds.audio_samples:
        pred, conf, _ = clf.predict_from_vector(s.feature_array)
        all_preds.append(pred)

    print(classification_report(y, all_preds))

    # Confusion matrix
    cm, labels = confusion_matrix(y, all_preds)
    print()
    print(ascii_confusion_matrix(cm, labels))

    # ---- 6. Statistical significance ----
    print("\n" + "─" * 50)
    print("6. STATISTICAL SIGNIFICANCE")
    print("─" * 50)

    # FeatureClassifier vs Random
    cv_scores_a = cv_results["per_fold_accuracies"]
    random_scores = []
    rng = np.random.RandomState(42)
    for _ in range(len(cv_scores_a)):
        idx = rng.randint(0, len(y), size=len(y))
        correct = sum(1 for i in idx if random_preds[i] == y[i])
        random_scores.append(correct / len(y))

    perm = permutation_test(cv_scores_a if cv_scores_a else [acc_cv],
                            random_scores, n_permutations=10000, seed=42)
    print(f"   FeatureClassifier vs Random:")
    print(f"     Observed diff: {perm['observed_diff']:.3f}")
    print(f"     p-value: {perm['p_value']:.4f}")
    print(f"     Significant at 0.05: {'Yes' if perm['significant_0.05'] else 'No'}")

    # ---- Save results ----
    results = {
        "experiment": "exp15_production_classification",
        "dataset": {
            "total_samples": ds.size,
            "label_counts": ds.label_counts,
            "unique_labels": ds.unique_labels,
        },
        "random_baseline": {"accuracy": acc_rand, "ci": [ci_lo, ci_hi]},
        "nearest_centroid": {"accuracy": acc_nc, "ci": [ci_lo_nc, ci_hi_nc]},
        "feature_classifier_cv": {
            "accuracy": acc_cv,
            "per_fold": cv_results["per_fold_accuracies"],
            "per_class": cv_results["per_class_accuracy"],
        },
        "bootstrapped": boot,
        "permutation_test": perm,
    }

    results_path = PROJECT_ROOT / "results" / "results_exp15.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Results saved to {results_path}")

    # Summary table
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    table_data = [
        {"Classifier": "Random", "Accuracy": acc_rand, "95% CI Lower": ci_lo, "95% CI Upper": ci_hi},
        {"Classifier": "Nearest Centroid", "Accuracy": acc_nc, "95% CI Lower": ci_lo_nc, "95% CI Upper": ci_hi_nc},
        {"Classifier": "FeatureClassifier", "Accuracy": acc_cv, "95% CI Lower": boot["ci_lower"], "95% CI Upper": boot["ci_upper"]},
    ]
    print(format_results_table(table_data, ["Classifier", "Accuracy", "95% CI Lower", "95% CI Upper"]))


if __name__ == "__main__":
    main()
