"""
Experiment 6: Feature Importance Analysis

Computes feature importance using permutation testing and shows which
features matter most for each genre distinction. Ranks top-10 features
by discriminative power.
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from constraint_toolkit.classifier import FeatureClassifier


# Feature dimension names for display
FEATURE_NAMES = [
    # MFCCs (0-12)
    "MFCC_1", "MFCC_2", "MFCC_3", "MFCC_4", "MFCC_5",
    "MFCC_6", "MFCC_7", "MFCC_8", "MFCC_9", "MFCC_10",
    "MFCC_11", "MFCC_12", "MFCC_13",
    # Chroma (13-24)
    "Chroma_C", "Chroma_C#", "Chroma_D", "Chroma_D#", "Chroma_E",
    "Chroma_F", "Chroma_F#", "Chroma_G", "Chroma_G#", "Chroma_A",
    "Chroma_A#", "Chroma_B",
    # Spectral contrast (25-30)
    "Contrast_0-200Hz", "Contrast_200-400Hz", "Contrast_400-800Hz",
    "Contrast_800-1600Hz", "Contrast_1600-3200Hz", "Contrast_3200+Hz",
    # Rhythmic (31-36)
    "Onset_Density", "Onset_Regularity", "Syncopation",
    "Swing_Ratio", "Tempo_Estimate", "Pulse_Clarity",
    # Tonal (37-41)
    "Key_Clarity", "Mode", "Harmonic_Complexity",
    "Tonal_Tension", "Modulation_Frequency",
]

FEATURE_GROUPS = {
    "MFCCs": range(0, 13),
    "Chroma": range(13, 25),
    "Spectral Contrast": range(25, 31),
    "Rhythmic": range(31, 37),
    "Tonal": range(37, 42),
}


def generate_synthetic_dataset(n_per_genre=30, seed=42):
    """Generate synthetic feature vectors for each genre."""
    rng = np.random.RandomState(seed)

    profiles = {
        "Jazz": {"mfcc": 0.6, "chroma_ent": 0.8, "contrast": 0.4, "rhythm": 0.7, "tonal": 0.8},
        "Classical": {"mfcc": 0.5, "chroma_ent": 0.5, "contrast": 0.3, "rhythm": 0.3, "tonal": 0.5},
        "Blues": {"mfcc": 0.5, "chroma_ent": 0.6, "contrast": 0.5, "rhythm": 0.5, "tonal": 0.6},
        "EDM": {"mfcc": 0.7, "chroma_ent": 0.3, "contrast": 0.7, "rhythm": 0.6, "tonal": 0.2},
        "Hip-hop": {"mfcc": 0.6, "chroma_ent": 0.4, "contrast": 0.6, "rhythm": 0.8, "tonal": 0.3},
        "Gamelan": {"mfcc": 0.5, "chroma_ent": 0.6, "contrast": 0.5, "rhythm": 0.7, "tonal": 0.5},
        "African Polyrhythm": {"mfcc": 0.5, "chroma_ent": 0.5, "contrast": 0.5, "rhythm": 0.9, "tonal": 0.3},
        "Latin": {"mfcc": 0.5, "chroma_ent": 0.5, "contrast": 0.5, "rhythm": 0.8, "tonal": 0.5},
    }

    vectors = []
    labels = []

    for genre, p in profiles.items():
        for _ in range(n_per_genre):
            vec = rng.uniform(0.2, 0.8, size=42)
            vec[0:13] = np.clip(p["mfcc"] + rng.randn(13) * 0.1, 0, 1)
            vec[13:25] = np.clip(1.0 / 12 + rng.randn(12) * (0.05 + 0.1 * p["chroma_ent"]), 0, 1)
            vec[13:25] /= max(vec[13:25].sum(), 1e-10)
            vec[25:31] = np.clip(p["contrast"] + rng.randn(6) * 0.1, 0, 1)
            vec[31] = np.clip(p["rhythm"] + rng.randn() * 0.1, 0, 1)
            vec[32] = np.clip(0.5 + rng.randn() * 0.15, 0, 1)
            vec[33] = np.clip(rng.rand() * 0.5, 0, 1)
            vec[34] = np.clip(rng.rand() * 0.3, 0, 1)
            vec[35] = np.clip(0.5 + rng.randn() * 0.1, 0, 1)
            vec[36] = np.clip(0.5 + rng.randn() * 0.1, 0, 1)
            vec[37] = np.clip(0.5 + p["tonal"] * 0.3 + rng.randn() * 0.1, 0, 1)
            vec[38] = np.clip(0.5 + rng.randn() * 0.2, 0, 1)
            vec[39] = np.clip(p["tonal"] + rng.randn() * 0.1, 0, 1)
            vec[40] = np.clip(0.5 + rng.randn() * 0.1, 0, 1)
            vec[41] = np.clip(rng.rand() * 0.2, 0, 1)
            vectors.append(vec)
            labels.append(genre)

    return vectors, labels


def pairwise_importance(vectors, labels, genre_a, genre_b, n_repeats=10, seed=42):
    """Compute permutation importance for distinguishing two genres."""
    # Filter to just the two genres
    idx = [i for i, l in enumerate(labels) if l in (genre_a, genre_b)]
    pair_vecs = [vectors[i] for i in idx]
    pair_labs = [labels[i] for i in idx]

    if len(pair_vecs) < 4:
        return np.zeros(42, dtype=np.float64)

    clf = FeatureClassifier(seed=seed)
    clf.train_from_vectors(pair_vecs, pair_labs)
    return clf.permutation_importance(pair_vecs, pair_labs, n_repeats=n_repeats)


def main():
    workspace = Path(__file__).parent.parent.parent
    results_dir = workspace / "constraint-toolkit" / "results"
    results_dir.mkdir(exist_ok=True)

    print("=== Feature Importance Analysis ===\n")

    vectors, labels = generate_synthetic_dataset(n_per_genre=30, seed=42)

    # 1. Overall permutation importance
    print("Training full classifier for permutation importance...")
    clf = FeatureClassifier(seed=42)
    clf.train_from_vectors(vectors, labels)

    overall_importance = clf.permutation_importance(vectors, labels, n_repeats=10)

    print("\nTop 10 features by permutation importance:")
    top_indices = np.argsort(overall_importance)[::-1][:10]
    for rank, idx in enumerate(top_indices, 1):
        score = overall_importance[idx]
        bar = "█" * int(score * 200)
        print(f"  {rank:2d}. {FEATURE_NAMES[idx]:<25} {score:.4f} {bar}")

    # 2. Feature group importance
    print("\nFeature group importance (mean permutation drop):")
    group_importance = {}
    for group_name, dim_range in FEATURE_GROUPS.items():
        mean_imp = float(np.mean(overall_importance[list(dim_range)]))
        group_importance[group_name] = mean_imp
        bar = "█" * int(mean_imp * 200)
        print(f"  {group_name:<20} {mean_imp:.4f} {bar}")

    # 3. Pairwise genre importance (top discriminating features)
    genres = sorted(set(labels))
    print(f"\nTop discriminating feature per genre pair:")
    print(f"  {'Genre A':<18} {'Genre B':<18} {'Top Feature':<25} {'Importance':>10}")
    print("  " + "-" * 75)

    pairwise_results = {}
    for i, ga in enumerate(genres):
        for gb in genres[i + 1:]:
            imp = pairwise_importance(vectors, labels, ga, gb, n_repeats=5)
            top_idx = int(np.argmax(imp))
            top_score = imp[top_idx]
            pairwise_results[f"{ga}_vs_{gb}"] = {
                "top_feature": FEATURE_NAMES[top_idx],
                "top_importance": float(top_score),
                "all_importance": imp.tolist(),
            }
            print(f"  {ga:<18} {gb:<18} {FEATURE_NAMES[top_idx]:<25} {top_score:>10.4f}")

    # 4. Per-genre analysis: which features distinguish each genre from all others
    print("\nPer-genre most distinctive features:")
    for genre in genres:
        genre_idx = [i for i, l in enumerate(labels) if l == genre]
        other_idx = [i for i, l in enumerate(labels) if l != genre]

        genre_vecs = [vectors[i] for i in genre_idx]
        other_vecs = [vectors[i] for i in other_idx]

        genre_mean = np.mean(genre_vecs, axis=0)
        other_mean = np.mean(other_vecs, axis=0)

        # Largest absolute differences
        diff = np.abs(genre_mean - other_mean)
        top3 = np.argsort(diff)[::-1][:3]
        features_str = ", ".join(
            f"{FEATURE_NAMES[j]} ({diff[j]:.3f})" for j in top3
        )
        print(f"  {genre:<22} → {features_str}")

    # Save results
    output = {
        "experiment": "feature_importance",
        "top_10_features": [
            {"name": FEATURE_NAMES[i], "importance": float(overall_importance[i]), "rank": r}
            for r, i in enumerate(top_indices, 1)
        ],
        "group_importance": group_importance,
        "pairwise_top_features": {
            k: {"top_feature": v["top_feature"], "importance": v["top_importance"]}
            for k, v in pairwise_results.items()
        },
    }
    with open(results_dir / "exp6_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {results_dir / 'exp6_results.json'}")


if __name__ == "__main__":
    main()
