#!/usr/bin/env python3
"""
Experiment 1: Emptiness Dominance (Theorem 1)
E > 0.5 for D > 2

Generate random viability functions over D-dimensional spaces.
Measure fraction of space that is viable as D increases.
"""

import numpy as np
import json
import os

np.random.seed(42)

# Results storage
results = {"experiment": "emptiness_dominance", "dimensions": [], "data": {}}

# Dimensions to test
dimensions = [2, 3, 5, 10, 20, 50]
n_samples = 50000  # Monte Carlo samples per dimension
n_landscapes = 10  # Average over multiple random landscapes

for D in dimensions:
    print(f"\n=== Dimension D = {D} ===")
    emptiness_values = []
    
    for landscape_idx in range(n_landscapes):
        # Generate a random viability landscape:
        # Create K random Gaussian peaks (local minima = viable regions)
        K = max(3, int(2 + D * 0.5))  # Number of peaks scales mildly with D
        
        # Random peak centers in [0, 1]^D
        centers = np.random.uniform(0.2, 0.8, size=(K, D))
        # Random peak widths (standard deviations)
        widths = np.random.uniform(0.05, 0.15, size=K)
        # Random peak heights
        heights = np.random.uniform(0.5, 1.0, size=K)
        
        # Sample random points in [0, 1]^D
        points = np.random.uniform(0, 1, size=(n_samples, D))
        
        # Compute viability: O(c) = max over peaks of height * exp(-||x - center||^2 / (2 * width^2))
        O = np.zeros(n_samples)
        for k in range(K):
            dist_sq = np.sum((points - centers[k]) ** 2, axis=1)
            contribution = heights[k] * np.exp(-dist_sq / (2 * widths[k] ** 2))
            O = np.maximum(O, contribution)
        
        # Threshold: point is viable if O > 0.3
        threshold = 0.3
        viable_fraction = np.mean(O > threshold)
        emptiness = 1.0 - viable_fraction
        emptiness_values.append(emptiness)
    
    mean_emptiness = np.mean(emptiness_values)
    std_emptiness = np.std(emptiness_values)
    
    print(f"  K peaks: {K}")
    print(f"  Mean emptiness E: {mean_emptiness:.4f} ± {std_emptiness:.4f}")
    print(f"  Viable fraction: {1 - mean_emptiness:.4f}")
    print(f"  E > 0.5? {'YES' if mean_emptiness > 0.5 else 'NO'}")
    
    results["data"][str(D)] = {
        "K_peaks": K,
        "n_samples": n_samples,
        "n_landscapes": n_landscapes,
        "mean_emptiness": round(mean_emptiness, 6),
        "std_emptiness": round(std_emptiness, 6),
        "viable_fraction": round(1 - mean_emptiness, 6),
        "all_values": [round(v, 6) for v in emptiness_values],
        "theorem_holds": bool(mean_emptiness > 0.5)
    }
    results["dimensions"].append(D)

# Also test with different threshold values for D=3
print("\n=== Sensitivity analysis: threshold variation for D=3 ===")
D = 3
thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
sensitivity = {}
for thresh in thresholds:
    emptiness_vals = []
    for _ in range(20):
        K = 4
        centers = np.random.uniform(0.2, 0.8, size=(K, D))
        widths = np.random.uniform(0.05, 0.15, size=K)
        heights = np.random.uniform(0.5, 1.0, size=K)
        points = np.random.uniform(0, 1, size=(n_samples, D))
        O = np.zeros(n_samples)
        for k in range(K):
            dist_sq = np.sum((points - centers[k]) ** 2, axis=1)
            O = np.maximum(O, heights[k] * np.exp(-dist_sq / (2 * widths[k] ** 2)))
        emptiness_vals.append(1.0 - np.mean(O > thresh))
    sensitivity[str(thresh)] = round(np.mean(emptiness_vals), 4)
    print(f"  threshold={thresh:.1f}: E = {np.mean(emptiness_vals):.4f}")

results["sensitivity_threshold_D3"] = sensitivity

# Compare with music result
results["music_comparison"] = {
    "music_D": 3,
    "music_emptiness": 0.82,
    "simulated_D3_emptiness": results["data"]["3"]["mean_emptiness"],
    "note": "Music E=0.82 from 10 traditions in 3D space"
}

# Summary
print("\n" + "="*60)
print("EMPTINESS DOMINANCE SUMMARY")
print("="*60)
for D in dimensions:
    d = results["data"][str(D)]
    status = "✓ HOLDS" if d["theorem_holds"] else "✗ FAILS"
    print(f"  D={D:3d}: E = {d['mean_emptiness']:.4f} ± {d['std_emptiness']:.4f}  {status}")

print(f"\nMusic comparison (D=3): simulated E = {results['data']['3']['mean_emptiness']:.4f}, empirical = 0.82")

# Save
with open(os.path.join(os.path.dirname(__file__), "emptiness_dominance.json"), "w") as f:
    json.dump(results, f, indent=2)

print("\nResults saved to emptiness_dominance.json")
