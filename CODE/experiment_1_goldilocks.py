"""
Universal Theory Computational Experiments
Tests predictions from the universal freedom-constraint framework.
"""
import numpy as np
from collections import Counter
import json
import gzip
from itertools import combinations

# ============================================================
# Core simulation function
# ============================================================
def run_agent(epsilon, n_steps=100, dim=12, seed=None):
    """Simulate a constraint-satisfaction agent with freedom ε."""
    if seed is not None:
        np.random.seed(seed)
    state = np.random.randn(dim)
    lattice = np.round(state)
    
    outputs = []
    for _ in range(n_steps):
        output = (1 - epsilon) * lattice + epsilon * state
        outputs.append(output)
        state = output + 0.1 * np.random.randn(dim)
        lattice = np.round(state)
    
    return np.array(outputs)

def measure_quality(outputs, epsilon):
    """Measure quality metrics for a given output sequence."""
    diffs = np.diff(outputs, axis=0)
    novelty = np.mean(np.linalg.norm(diffs, axis=1))
    
    snapped = np.round(outputs)
    structure = np.mean(np.linalg.norm(outputs - snapped, axis=1))
    
    data = outputs.tobytes()
    compressed = gzip.compress(data)
    complexity = len(compressed) / len(data)
    
    balance = novelty / (1 + structure)
    
    return {
        'epsilon': epsilon,
        'novelty': float(novelty),
        'structure': float(structure),
        'complexity': float(complexity),
        'balance': float(balance)
    }

# ============================================================
# Experiment 1: ε Sweet Spot (Goldilocks Curve)
# ============================================================
print("=" * 60)
print("EXPERIMENT 1: Goldilocks Curve (ε Sweet Spot)")
print("=" * 60)

exp1_results = []
epsilons = np.arange(0, 1.01, 0.05)
for eps in epsilons:
    trial_results = []
    for trial in range(10):
        outputs = run_agent(eps, seed=trial)
        metrics = measure_quality(outputs, eps)
        trial_results.append(metrics)
    
    avg = {
        'epsilon': round(float(eps), 4),
        'novelty': float(np.mean([t['novelty'] for t in trial_results])),
        'structure': float(np.mean([t['structure'] for t in trial_results])),
        'complexity': float(np.mean([t['complexity'] for t in trial_results])),
        'balance': float(np.mean([t['balance'] for t in trial_results])),
        'novelty_std': float(np.std([t['novelty'] for t in trial_results])),
        'balance_std': float(np.std([t['balance'] for t in trial_results])),
    }
    exp1_results.append(avg)
    print(f"  ε={eps:.2f}: novelty={avg['novelty']:.4f}, structure={avg['structure']:.4f}, "
          f"balance={avg['balance']:.4f} ± {avg['balance_std']:.4f}")

best_exp1 = max(exp1_results, key=lambda r: r['balance'])
print(f"\n  🏆 Sweet spot: ε={best_exp1['epsilon']:.2f} (balance={best_exp1['balance']:.4f})")

# ============================================================
# Experiment 2: Non-Pre-Calculability (Diversity)
# ============================================================
print("\n" + "=" * 60)
print("EXPERIMENT 2: Non-Pre-Calculability (Diversity)")
print("=" * 60)

sweet_eps = best_exp1['epsilon']
outputs_list = []
for seed in range(10):
    result = run_agent(sweet_eps, seed=seed)
    outputs_list.append(result.flatten())

distances = []
for i, j in combinations(range(10), 2):
    d = np.linalg.norm(outputs_list[i] - outputs_list[j])
    distances.append(d)

mean_dist = float(np.mean(distances))
std_dist = float(np.std(distances))
cv = std_dist / mean_dist if mean_dist > 0 else 0

print(f"  Mean pairwise distance: {mean_dist:.4f} ± {std_dist:.4f}")
print(f"  Diversity coefficient (CV): {cv:.4f}")
print(f"  Max distance: {max(distances):.4f}")
print(f"  Min distance: {min(distances):.4f}")
print(f"  → Output is {'genuinely different' if cv > 0 else 'deterministic'} each time")

exp2_result = {
    'epsilon_used': sweet_eps,
    'n_seeds': 10,
    'mean_pairwise_distance': mean_dist,
    'std_pairwise_distance': std_dist,
    'diversity_coefficient_cv': cv,
    'max_distance': float(max(distances)),
    'min_distance': float(min(distances))
}

# ============================================================
# Experiment 3: Compression Ratio Invariance
# ============================================================
print("\n" + "=" * 60)
print("EXPERIMENT 3: Compression Ratio Across Domains")
print("=" * 60)

# Domain 1: Pure random (ε=1.0)
random_data = np.random.randn(1000, 12).tobytes()
random_compressed = len(gzip.compress(random_data))
random_ratio = random_compressed / len(random_data)

# Domain 2: Pure snap (ε=0.0)
snap_data = np.round(np.random.randn(1000, 12)).tobytes()
snap_compressed = len(gzip.compress(snap_data))
snap_ratio = snap_compressed / len(snap_data)

# Domain 3: Sweet spot
sweet_outputs = run_agent(sweet_eps, n_steps=1000, seed=42)
sweet_data = sweet_outputs.tobytes()
sweet_compressed = len(gzip.compress(sweet_data))
sweet_ratio = sweet_compressed / len(sweet_data)

# Domain 4: Over-constrained (ε=0.1)
tight_outputs = run_agent(0.1, n_steps=1000, seed=42)
tight_data = tight_outputs.tobytes()
tight_compressed = len(gzip.compress(tight_data))
tight_ratio = tight_compressed / len(tight_data)

print(f"  Random (ε=1.0):  {random_ratio:.4f}")
print(f"  Snap (ε=0.0):    {snap_ratio:.4f}")
print(f"  Sweet (ε={sweet_eps:.2f}): {sweet_ratio:.4f}")
print(f"  Tight (ε=0.10):  {tight_ratio:.4f}")

exp3_result = {
    'random_epsilon1': {'ratio': random_ratio, 'description': 'Pure noise'},
    'snap_epsilon0': {'ratio': snap_ratio, 'description': 'Pure structure'},
    'sweet_epsilon_opt': {'ratio': sweet_ratio, 'epsilon': sweet_eps, 'description': 'Optimal freedom'},
    'tight_epsilon01': {'ratio': tight_ratio, 'epsilon': 0.1, 'description': 'Over-constrained'},
}

# ============================================================
# Experiment 4: Scale Invariance of ε*
# ============================================================
print("\n" + "=" * 60)
print("EXPERIMENT 4: Scale Invariance of ε*")
print("=" * 60)

exp4_results = []
for dim in [3, 6, 12, 24, 48, 96]:
    best_balance = -1
    best_eps = 0
    all_eps = []
    for eps in np.arange(0.05, 0.95, 0.05):
        np.random.seed(42)
        outputs = run_agent(eps, n_steps=100, dim=dim)
        diffs = np.diff(outputs, axis=0)
        novelty = np.mean(np.linalg.norm(diffs, axis=1))
        structure = np.mean(np.linalg.norm(outputs - np.round(outputs), axis=1))
        balance = novelty / (1 + structure)
        all_eps.append({'epsilon': float(eps), 'balance': float(balance)})
        if balance > best_balance:
            best_balance = balance
            best_eps = float(eps)
    
    exp4_results.append({
        'dimension': dim,
        'optimal_epsilon': best_eps,
        'best_balance': float(best_balance),
        'curve': all_eps
    })
    print(f"  dim={dim:3d}: best ε*={best_eps:.2f} (balance={best_balance:.4f})")

# Check variance of ε* across dimensions
eps_stars = [r['optimal_epsilon'] for r in exp4_results]
eps_star_mean = np.mean(eps_stars)
eps_star_std = np.std(eps_stars)
print(f"\n  ε* across dimensions: {eps_star_mean:.3f} ± {eps_star_std:.3f}")
print(f"  → ε* is {'scale invariant' if eps_star_std < 0.05 else 'scale dependent'}")

# ============================================================
# Save all results
# ============================================================
all_results = {
    'experiment_1_goldilocks': {
        'description': 'ε Sweet Spot - balance of novelty and structure',
        'results': exp1_results,
        'sweet_spot': best_exp1
    },
    'experiment_2_diversity': {
        'description': 'Non-pre-calculability - output diversity across seeds',
        'results': exp2_result
    },
    'experiment_3_compression': {
        'description': 'Compression ratio across constraint regimes',
        'results': exp3_result
    },
    'experiment_4_scale_invariance': {
        'description': 'Scale invariance of optimal ε*',
        'results': exp4_results,
        'eps_star_mean': float(eps_star_mean),
        'eps_star_std': float(eps_star_std),
        'scale_invariant': bool(eps_star_std < 0.05)
    }
}

output_path = '/home/phoenix/.openclaw/workspace/RESEARCH/EXPERIMENT-RESULTS-1.json'
with open(output_path, 'w') as f:
    json.dump(all_results, f, indent=2)
print(f"\n✅ Results saved to {output_path}")
