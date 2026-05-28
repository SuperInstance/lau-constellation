"""
Experiment 18: Corpus Statistics

Computes full statistical profile of the workspace WAV corpus:
mean/std of features per genre, correlation matrix, PCA,
most distinctive features per genre, and ANOVA F-statistics.
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from constraint_toolkit.datasets import Dataset, label_from_filename
from constraint_toolkit.features import FeatureVector
from constraint_toolkit.visualize import ascii_heatmap, ascii_bar_chart, format_results_table

WORKSPACE = Path("/home/phoenix/.openclaw/workspace")

# Feature group names for reporting
FEATURE_NAMES = (
    [f"MFCC_{i}" for i in range(13)]
    + [f"Chroma_{i}" for i in range(12)]
    + [f"SpecCon_{i}" for i in range(6)]
    + [f"Rhythm_{i}" for i in range(6)]
    + [f"Tonal_{i}" for i in range(5)]
)

FEATURE_GROUPS = {
    "MFCCs": (0, 13),
    "Chroma": (13, 25),
    "Spectral Contrast": (25, 31),
    "Rhythmic": (31, 37),
    "Tonal": (37, 42),
}


def pca(X: np.ndarray, n_components: int = 3) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Simple PCA via SVD. Returns (components, explained_variance_ratio, projected)."""
    X_centered = X - X.mean(axis=0)
    # Use SVD
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    components = Vt[:n_components]
    total_var = np.sum(S ** 2)
    explained = (S[:n_components] ** 2) / max(total_var, 1e-10)
    projected = X_centered @ components.T
    return components, explained, projected


def anova_f_statistic(X: np.ndarray, labels: list[str]) -> np.ndarray:
    """Compute ANOVA F-statistic for each feature dimension."""
    unique_labels = sorted(set(labels))
    n_features = X.shape[1]
    f_stats = np.zeros(n_features, dtype=np.float64)

    grand_mean = X.mean(axis=0)
    n_total = len(X)

    for dim in range(n_features):
        ss_between = 0.0
        ss_within = 0.0
        for lab in unique_labels:
            mask = np.array([l == lab for l in labels])
            group = X[mask, dim]
            n_group = len(group)
            if n_group < 2:
                continue
            group_mean = group.mean()
            ss_between += n_group * (group_mean - grand_mean[dim]) ** 2
            ss_within += np.sum((group - group_mean) ** 2)

        df_between = max(len(unique_labels) - 1, 1)
        df_within = max(n_total - len(unique_labels), 1)
        ms_between = ss_between / df_between
        ms_within = ss_within / max(df_within, 1)
        f_stats[dim] = ms_between / max(ms_within, 1e-10)

    return f_stats


def main():
    print("=" * 70)
    print("EXPERIMENT 18: Corpus Statistics")
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

    X, y = ds.get_feature_matrix()
    labels_unique = sorted(set(y))
    print(f"   Features: {X.shape[1]}, Samples: {X.shape[0]}, Classes: {len(labels_unique)}")

    # ---- 1. Mean/Std per genre ----
    print("\n" + "─" * 50)
    print("1. FEATURE STATISTICS PER GENRE")
    print("─" * 50)

    stats_per_genre = {}
    for lab in labels_unique:
        mask = np.array([l == lab for l in y])
        group = X[mask]
        stats_per_genre[lab] = {
            "n": int(mask.sum()),
            "feature_means": group.mean(axis=0).tolist(),
            "feature_stds": group.std(axis=0).tolist(),
        }
        print(f"\n   {lab} (n={mask.sum()}):")
        for gname, (start, end) in FEATURE_GROUPS.items():
            means = group.mean(axis=0)[start:end]
            stds = group.std(axis=0)[start:end]
            print(f"     {gname:20s}: mean={means.mean():.3f} ± {stds.mean():.3f}")

    # ---- 2. Correlation matrix (feature groups) ----
    print("\n" + "─" * 50)
    print("2. FEATURE GROUP CORRELATIONS")
    print("─" * 50)

    group_names = list(FEATURE_GROUPS.keys())
    n_groups = len(group_names)
    corr_matrix = np.zeros((n_groups, n_groups), dtype=np.float64)

    for i, (gname_a, (sa, ea)) in enumerate(FEATURE_GROUPS.items()):
        for j, (gname_b, (sb, eb)) in enumerate(FEATURE_GROUPS.items()):
            # Mean correlation between features of two groups
            corr_sum = 0.0
            count = 0
            for fi in range(sa, ea):
                for fj in range(sb, eb):
                    if fi == fj:
                        corr_sum += 1.0
                    else:
                        va = X[:, fi]
                        vb = X[:, fj]
                        va_c = va - va.mean()
                        vb_c = vb - vb.mean()
                        denom = np.sqrt(np.sum(va_c ** 2) * np.sum(vb_c ** 2))
                        if denom > 1e-10:
                            corr_sum += float(np.sum(va_c * vb_c) / denom)
                    count += 1
            corr_matrix[i, j] = corr_sum / max(count, 1)

    print(ascii_heatmap(corr_matrix, group_names, group_names, title="Feature Group Correlations"))

    # ---- 3. PCA ----
    print("\n" + "─" * 50)
    print("3. PCA OF FEATURE SPACE")
    print("─" * 50)

    components, explained, projected = pca(X, n_components=3)

    print(f"   Explained variance ratio:")
    for i in range(3):
        print(f"     PC{i + 1}: {explained[i]:.3f} ({explained[i] * 100:.1f}%)")
    print(f"   Total (3 components): {explained.sum():.3f} ({explained.sum() * 100:.1f}%)")

    print(f"\n   Top contributing features per component:")
    for i in range(3):
        top_indices = np.argsort(np.abs(components[i]))[-5:][::-1]
        print(f"     PC{i + 1}: ", end="")
        print(", ".join(f"{FEATURE_NAMES[j]} ({components[i, j]:.3f})" for j in top_indices))

    # Projected positions per genre
    print(f"\n   Genre positions in PCA space (PC1, PC2, PC3):")
    for lab in labels_unique:
        mask = np.array([l == lab for l in y])
        centre = projected[mask].mean(axis=0)
        print(f"     {lab:20s}: ({centre[0]:+.2f}, {centre[1]:+.2f}, {centre[2]:+.2f})")

    # ---- 4. Most distinctive features per genre ----
    print("\n" + "─" * 50)
    print("4. MOST DISTINCTIVE FEATURES PER GENRE")
    print("─" * 50)

    overall_mean = X.mean(axis=0)

    for lab in labels_unique:
        mask = np.array([l == lab for l in y])
        group = X[mask]
        group_mean = group.mean(axis=0)

        # Z-score deviation from overall mean
        overall_std = X.std(axis=0)
        overall_std[overall_std < 1e-10] = 1.0
        z_scores = (group_mean - overall_mean) / overall_std

        top_positive = np.argsort(z_scores)[-3:][::-1]
        top_negative = np.argsort(z_scores)[:3]

        print(f"\n   {lab}:")
        print(f"     Most above average: " + ", ".join(
            f"{FEATURE_NAMES[i]} (z={z_scores[i]:+.2f})" for i in top_positive if z_scores[i] > 0.1))
        print(f"     Most below average: " + ", ".join(
            f"{FEATURE_NAMES[i]} (z={z_scores[i]:+.2f})" for i in top_negative if z_scores[i] < -0.1))

    # ---- 5. ANOVA F-statistics ----
    print("\n" + "─" * 50)
    print("5. FEATURE DISCRIMINATIVE POWER (ANOVA F-statistic)")
    print("─" * 50)

    f_stats = anova_f_statistic(X, y)

    # Top discriminative features
    top_features = np.argsort(f_stats)[-10:][::-1]
    print(f"\n   Top 10 most discriminative features:")
    for rank, idx in enumerate(top_features):
        print(f"     {rank + 1:2d}. {FEATURE_NAMES[idx]:20s} F={f_stats[idx]:.2f}")

    # By group
    print(f"\n   Mean F-statistic by feature group:")
    group_f = {}
    for gname, (start, end) in FEATURE_GROUPS.items():
        mean_f = float(f_stats[start:end].mean())
        group_f[gname] = mean_f
        print(f"     {gname:20s}: {mean_f:.2f}")

    print()
    print(ascii_bar_chart(group_f, title="Discriminative Power by Feature Group"))

    # ---- Save results ----
    results = {
        "experiment": "exp18_corpus_statistics",
        "dataset": {
            "total_samples": int(X.shape[0]),
            "n_features": int(X.shape[1]),
            "classes": labels_unique,
            "label_counts": {lab: int(sum(1 for l in y if l == lab)) for lab in labels_unique},
        },
        "pca": {
            "explained_variance": explained.tolist(),
            "total_3pc": float(explained.sum()),
        },
        "anova_f_statistics": {
            FEATURE_NAMES[i]: float(f_stats[i]) for i in range(len(FEATURE_NAMES))
        },
        "top_discriminative_features": [
            {"feature": FEATURE_NAMES[i], "f_stat": float(f_stats[i])}
            for i in top_features
        ],
        "genre_statistics": {
            lab: {
                "n": stats_per_genre[lab]["n"],
                "feature_means": stats_per_genre[lab]["feature_means"],
                "feature_stds": stats_per_genre[lab]["feature_stds"],
                "pca_centre": projected[np.array([l == lab for l in y])].mean(axis=0).tolist(),
            }
            for lab in labels_unique
        },
        "correlation_matrix": corr_matrix.tolist(),
        "group_f_statistics": group_f,
    }

    results_path = PROJECT_ROOT / "results" / "results_exp18.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Results saved to {results_path}")


if __name__ == "__main__":
    main()
