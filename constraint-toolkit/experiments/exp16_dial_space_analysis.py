"""
Experiment 16: Dial Space Analysis

Computes dial positions for all WAV files, projects onto 2D,
clusters using K-means, identifies outliers, and tests genre separation.
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from constraint_toolkit.datasets import Dataset, label_from_filename
from constraint_toolkit.dials import DIAL_RANGES, DialPosition, classify_dial_cluster, compute_dial_distance
from constraint_toolkit.metrics import permutation_test
from constraint_toolkit.visualize import ascii_dial_space, ascii_scatter, ascii_bar_chart, format_results_table, ascii_heatmap

WORKSPACE = Path("/home/phoenix/.openclaw/workspace")


def silhouette_score(data: np.ndarray, labels: np.ndarray) -> float:
    """Compute mean silhouette score."""
    n = len(data)
    if n < 2:
        return 0.0

    unique_labels = np.unique(labels)
    if len(unique_labels) < 2:
        return 0.0

    scores = np.zeros(n, dtype=np.float64)
    for i in range(n):
        same = data[labels == labels[i]]
        others = data[labels != labels[i]]

        if len(same) > 1:
            a = np.mean(np.linalg.norm(same - data[i], axis=1)) - 0  # exclude self
            a = np.sum(np.linalg.norm(same - data[i], axis=1)) / max(len(same) - 1, 1)
        else:
            a = 0.0

        if len(others) > 0:
            b = np.min([np.mean(np.linalg.norm(data[labels == l] - data[i], axis=1))
                        for l in unique_labels if l != labels[i] and np.sum(labels == l) > 0])
        else:
            b = 0.0

        denom = max(a, b, 1e-10)
        scores[i] = (b - a) / denom

    return float(np.mean(scores))


def main():
    print("=" * 70)
    print("EXPERIMENT 16: Dial Space Analysis")
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

    # Get dial positions
    positions = [s.dial_position for s in ds.audio_samples]
    names = [s.name for s in ds.audio_samples]
    labels = [s.label for s in ds.audio_samples]
    D, _ = ds.get_dial_matrix()

    print(f"\n📊 Dial positions computed for {len(positions)} samples")

    # ---- 1. 2D Dial projection ----
    print("\n" + "─" * 50)
    print("1. 2D DIAL PROJECTION (Harmonic Tension × Rhythmic Complexity)")
    print("─" * 50)
    print(ascii_dial_space(positions, names, width=80, height=25))

    # Also show H × S
    print("\n2D DIAL PROJECTION (Harmonic Tension × Spectral Density)")
    print("─" * 50)
    h = [p.harmonic_tension for p in positions]
    s = [p.spectral_density for p in positions]
    print(ascii_scatter(h, s, labels=names, width=80, height=20,
                        title="Harmonic Tension × Spectral Density"))

    # ---- 2. K-means clustering ----
    print("\n" + "─" * 50)
    print("2. K-MEANS CLUSTERING (optimal k via silhouette)")
    print("─" * 50)

    best_k = 3
    best_sil = -2.0
    sil_scores = {}

    for k in range(3, min(8, len(positions))):
        cluster_labels, centers = classify_dial_cluster(positions, n_clusters=k, seed=42)
        if len(positions) >= k:
            sil = silhouette_score(D, np.array(cluster_labels))
            sil_scores[k] = sil
            print(f"   k={k}: silhouette={sil:.3f}")
            if sil > best_sil:
                best_sil = sil
                best_k = k

    print(f"\n   Optimal k={best_k} (silhouette={best_sil:.3f})")
    print()
    print(ascii_bar_chart(sil_scores, title="Silhouette Score by k"))

    # Cluster with optimal k
    cluster_labels, centers = classify_dial_cluster(positions, n_clusters=best_k, seed=42)
    print(f"\n   Cluster assignments:")
    for name, label, cl in zip(names, labels, cluster_labels):
        print(f"     {name:40s} [{label:12s}] → cluster {cl}")

    print(f"\n   Cluster centres:")
    for i, c in enumerate(centers):
        print(f"     Cluster {i}: H={c.harmonic_tension:.2f} R={c.rhythmic_complexity:.2f} S={c.spectral_density:.2f}")

    # ---- 3. Outlier detection ----
    print("\n" + "─" * 50)
    print("3. OUTLIER DETECTION")
    print("─" * 50)

    # Distance to nearest tradition centre
    tradition_centres = {name: prof["center"] for name, prof in DIAL_RANGES.items()}

    outlier_data = []
    for pos, name, lab in zip(positions, names, labels):
        dists = {t: float(np.linalg.norm(pos.to_array() - c))
                 for t, c in tradition_centres.items()}
        nearest = min(dists, key=dists.get)
        min_dist = dists[nearest]
        outlier_data.append({
            "file": name,
            "label": lab,
            "nearest_tradition": nearest,
            "distance": min_dist,
        })

    outlier_data.sort(key=lambda x: -x["distance"])
    print(f"\n   Files ranked by distance to nearest known tradition:")
    for od in outlier_data:
        marker = " ← OUTLIER" if od["distance"] > 2.5 else ""
        print(f"     {od['file']:40s} dist={od['distance']:.2f} → {od['nearest_tradition']}{marker}")

    # ---- 4. Intra/inter-genre distances ----
    print("\n" + "─" * 50)
    print("4. INTRA-GENRE vs INTER-GENRE DISTANCE")
    print("─" * 50)

    unique_labels_list = sorted(set(labels))
    intra_dists: dict[str, list[float]] = {}
    inter_dists: list[float] = []

    for lab in unique_labels_list:
        lab_pos = [positions[i] for i in range(len(positions)) if labels[i] == lab]
        if len(lab_pos) < 2:
            intra_dists[lab] = [0.0]
            continue
        dists = []
        for i in range(len(lab_pos)):
            for j in range(i + 1, len(lab_pos)):
                dists.append(compute_dial_distance(lab_pos[i], lab_pos[j]))
        intra_dists[lab] = dists

    # Inter-genre: distances between class centres
    class_centres = {}
    for lab in unique_labels_list:
        lab_pos = [positions[i] for i in range(len(positions)) if labels[i] == lab]
        arr = np.array([p.to_array() for p in lab_pos])
        class_centres[lab] = arr.mean(axis=0)

    inter_class_dists = {}
    for i, lab_a in enumerate(unique_labels_list):
        for lab_b in unique_labels_list[i + 1:]:
            d = float(np.linalg.norm(class_centres[lab_a] - class_centres[lab_b]))
            inter_class_dists[f"{lab_a} ↔ {lab_b}"] = d
            inter_dists.append(d)

    intra_means = {lab: float(np.mean(d)) for lab, d in intra_dists.items()}
    mean_intra = float(np.mean([d for dists in intra_dists.values() for d in dists]))
    mean_inter = float(np.mean(inter_dists)) if inter_dists else 0.0

    print(f"\n   Mean intra-genre distance: {mean_intra:.2f}")
    print(f"   Mean inter-genre distance: {mean_inter:.2f}")
    print(f"   Ratio (inter/intra): {mean_inter / max(mean_intra, 0.01):.2f}")
    print()
    print(ascii_bar_chart(intra_means, title="Mean intra-genre spread"))

    if inter_class_dists:
        print()
        print("   Inter-class distances:")
        sorted_inter = dict(sorted(inter_class_dists.items(), key=lambda x: x[1]))
        for pair, d in list(sorted_inter.items())[:10]:
            print(f"     {pair:40s} {d:.2f}")

    # ---- 5. Permutation test for genre separation ----
    print("\n" + "─" * 50)
    print("5. GENRE SEPARATION TEST (permutation-based MANOVA)")
    print("─" * 50)

    # Compute F-statistic-like measure: between/within variance
    grand_mean = D.mean(axis=0)
    n_total = len(D)

    ss_between = 0.0
    ss_within = 0.0
    for lab in unique_labels_list:
        mask = np.array([l == lab for l in labels])
        group = D[mask]
        group_mean = group.mean(axis=0)
        n_group = len(group)
        ss_between += n_group * np.sum((group_mean - grand_mean) ** 2)
        ss_within += np.sum((group - group_mean) ** 2)

    observed_f = ss_between / max(ss_within, 1e-10)

    # Permutation test
    rng = np.random.RandomState(42)
    n_perm = 5000
    count_extreme = 0
    for _ in range(n_perm):
        perm_labels = rng.permutation(labels)
        ss_b = 0.0
        ss_w = 0.0
        for lab in unique_labels_list:
            mask = np.array([l == lab for l in perm_labels])
            if mask.sum() == 0:
                continue
            group = D[mask]
            gm = group.mean(axis=0)
            ng = len(group)
            ss_b += ng * np.sum((gm - grand_mean) ** 2)
            ss_w += np.sum((group - gm) ** 2)
        perm_f = ss_b / max(ss_w, 1e-10)
        if perm_f >= observed_f:
            count_extreme += 1

    p_value = count_extreme / n_perm
    print(f"   F-statistic (between/within): {observed_f:.4f}")
    print(f"   Permutation p-value ({n_perm} permutations): {p_value:.4f}")
    print(f"   Genres significantly separated: {'Yes' if p_value < 0.05 else 'No'} (α=0.05)")

    # ---- Save results ----
    results = {
        "experiment": "exp16_dial_space_analysis",
        "dial_positions": {
            name: {
                "H": float(p.harmonic_tension),
                "R": float(p.rhythmic_complexity),
                "S": float(p.spectral_density),
                "label": lab,
            }
            for name, p, lab in zip(names, positions, labels)
        },
        "optimal_k": best_k,
        "silhouette_scores": {str(k): v for k, v in sil_scores.items()},
        "cluster_assignments": {name: int(cl) for name, cl in zip(names, cluster_labels)},
        "cluster_centres": {f"cluster_{i}": {
            "H": float(c.harmonic_tension),
            "R": float(c.rhythmic_complexity),
            "S": float(c.spectral_density),
        } for i, c in enumerate(centers)},
        "outliers": outlier_data,
        "intra_genre_distance": {"mean": mean_intra, "per_genre": intra_means},
        "inter_genre_distance": {"mean": mean_inter},
        "separation_test": {"f_statistic": float(observed_f), "p_value": float(p_value)},
    }

    results_path = PROJECT_ROOT / "results" / "results_exp16.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Results saved to {results_path}")

    # ---- Dial heatmap ----
    print("\n" + "─" * 50)
    print("DIAL POSITION HEATMAP (File × Dial Axis)")
    print("─" * 50)
    dial_matrix = np.array([[p.harmonic_tension, p.rhythmic_complexity, p.spectral_density]
                            for p in positions], dtype=np.float64)
    print(ascii_heatmap(dial_matrix, ["H_tens", "R_comp", "S_dens"],
                        [n[:30] for n in names], title=""))


if __name__ == "__main__":
    main()
