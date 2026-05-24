"""
Experiment 41: Creative Style Transfer
Morph between musical styles in real-time by interpolating Lorenz parameters.
"""

import numpy as np
import json
import sys

print("=== Experiment 41: Creative Style Transfer ===\n")


class LorenzSystem:
    """Lorenz attractor as a generative source for musical sequences."""

    def __init__(self, rho=28.0, sigma=10.0, beta=8.0/3.0, dt=0.01):
        self.rho = rho
        self.sigma = sigma
        self.beta = beta
        self.dt = dt
        self.state = np.array([1.0, 1.0, 1.0])
        self.outputs = []

    def step(self):
        x, y, z = self.state
        dx = self.sigma * (y - x)
        dy = x * (self.rho - z) - y
        dz = x * y - self.beta * z
        self.state = self.state + self.dt * np.array([dx, dy, dz])
        self.outputs.append(float(self.state[0]))
        return self.state[0]

    def run(self, n_steps, discard=500):
        self.outputs = []
        for _ in range(discard):
            self.step()
        self.outputs = []
        for _ in range(n_steps):
            self.step()

    def diversity(self):
        """Measure output diversity (normalized entropy of binned values)."""
        if len(self.outputs) < 10:
            return 0.0
        arr = np.array(self.outputs)
        hist, _ = np.histogram(arr, bins=20, density=True)
        hist = hist / hist.sum()
        hist = hist[hist > 0]
        entropy = -np.sum(hist * np.log2(hist))
        return entropy / np.log2(20)  # normalize to [0, 1]


class QualityMetrics:
    """Compute quality, novelty, and coherence of a sequence."""
    def __init__(self, quality, novelty, coherence):
        self.quality = quality
        self.novelty = novelty
        self.coherence = coherence

    @classmethod
    def from_outputs(cls, outputs):
        arr = np.array(outputs)
        if len(arr) < 10:
            return cls(0, 0, 0)

        # Novelty: rate of change
        diffs = np.diff(arr)
        novelty = np.std(diffs) / (np.std(arr) + 1e-10)

        # Coherence: autocorrelation at lag 1
        if np.std(arr) < 1e-10:
            coherence = 1.0
        else:
            coherence = abs(np.corrcoef(arr[:-1], arr[1:])[0, 1])

        # Quality: balance of novelty and coherence
        quality = 2 * (novelty * coherence) / (novelty + coherence + 1e-10)

        return cls(float(quality), float(novelty), float(coherence))


# Define styles as (ρ, σ) pairs — Lorenz parameters
styles = {
    'drone':       {'rho': 1,   'sigma': 3,  'scale': [0, 7]},
    'gregorian':   {'rho': 3,   'sigma': 5,  'scale': [0, 2, 4, 5, 7, 9, 11]},
    'baroque':     {'rho': 12,  'sigma': 8,  'scale': [0, 2, 4, 5, 7, 9, 11]},
    'classical':   {'rho': 18,  'sigma': 10, 'scale': [0, 2, 4, 5, 7, 9, 11]},
    'romantic':    {'rho': 25,  'sigma': 10, 'scale': [0, 2, 3, 5, 7, 8, 11]},
    'jazz':        {'rho': 28,  'sigma': 12, 'scale': [0, 2, 4, 5, 7, 9, 11]},
    'bebop':       {'rho': 35,  'sigma': 12, 'scale': [0, 2, 4, 5, 7, 9, 11]},
    'free_jazz':   {'rho': 45,  'sigma': 15, 'scale': list(range(12))},
    'noise':       {'rho': 55,  'sigma': 15, 'scale': list(range(12))},
}

style_names = list(styles.keys())

# ─── Part 1: Pairwise style transfer ───
print("--- Part 1: Pairwise Style Morphs ---")

transfers = [
    ('classical', 'jazz'),
    ('baroque', 'free_jazz'),
    ('drone', 'noise'),
    ('jazz', 'bebop'),
    ('romantic', 'bebop'),
    ('classical', 'noise'),
]

for style_a, style_b in transfers:
    a = styles[style_a]
    b = styles[style_b]

    morph_steps = 10
    morph_results = []

    for t in np.linspace(0, 1, morph_steps):
        rho = a['rho'] * (1 - t) + b['rho'] * t
        sigma = a['sigma'] * (1 - t) + b['sigma'] * t

        sys = LorenzSystem(rho=rho, sigma=sigma)
        sys.run(2000, 1000)

        div = sys.diversity()
        q = QualityMetrics.from_outputs(sys.outputs)

        # Pitch content
        outputs = np.array(sys.outputs)
        normalized = (outputs - outputs.min()) / (outputs.max() - outputs.min() + 1e-10)
        pitch_classes = (normalized * 12).astype(int) % 12
        unique_pcs = len(set(pitch_classes))

        morph_results.append({
            't': float(t),
            'rho': float(rho),
            'sigma': float(sigma),
            'diversity': div,
            'quality': q.quality,
            'novelty': q.novelty,
            'coherence': q.coherence,
            'unique_pitch_classes': unique_pcs,
        })

    # Find the transition point (largest diversity jump)
    diversities = [m['diversity'] for m in morph_results]
    max_jump = 0
    transition_t = 0.5
    for i in range(1, len(diversities)):
        jump = abs(diversities[i] - diversities[i - 1])
        if jump > max_jump:
            max_jump = jump
            transition_t = morph_results[i]['t']

    print(f"\n  {style_a:12s} → {style_b:12s}:")
    print(f"    transition at t={transition_t:.2f} (ρ={a['rho']*(1-transition_t)+b['rho']*transition_t:.1f})")
    print(f"    quality range: {min(m['quality'] for m in morph_results):.4f} → {max(m['quality'] for m in morph_results):.4f}")
    for m in morph_results:
        bar = '█' * int(m['diversity'] * 20)
        print(f"      t={m['t']:.1f}: ρ={m['rho']:5.1f}, div={m['diversity']:.3f}, q={m['quality']:.4f} {bar}")

# ─── Part 2: Circular style journey ───
print("\n--- Part 2: Circular Style Journey ---")
journey = ['drone', 'baroque', 'classical', 'romantic', 'jazz', 'bebop', 'free_jazz', 'noise',
           'free_jazz', 'bebop', 'jazz', 'romantic', 'classical', 'baroque', 'drone']

journey_results = []
for i in range(len(journey) - 1):
    a = styles[journey[i]]
    b = styles[journey[i + 1]]

    rho = (a['rho'] + b['rho']) / 2
    sigma = (a['sigma'] + b['sigma']) / 2

    sys = LorenzSystem(rho=rho, sigma=sigma)
    sys.run(2000, 1000)

    journey_results.append({
        'from': journey[i],
        'to': journey[i + 1],
        'midpoint_rho': rho,
        'diversity': sys.diversity(),
        'quality': QualityMetrics.from_outputs(sys.outputs).quality,
    })

print("  Journey through musical space:")
for jr in journey_results:
    print(f"    {jr['from']:12s} → {jr['to']:12s}: ρ_mid={jr['midpoint_rho']:5.1f}, "
          f"div={jr['diversity']:.3f}, q={jr['quality']:.4f}")

# ─── Part 3: Novel style discovery ───
print("\n--- Part 3: Novel Style Discovery ---")

hybrids = [
    ('drone', 'bebop', 'Drone Bop'),
    ('baroque', 'noise', 'Baroque Noise'),
    ('gregorian', 'free_jazz', 'Free Chant'),
    ('classical', 'noise', 'Classical Noise'),
    ('romantic', 'free_jazz', 'Free Romance'),
    ('jazz', 'noise', 'Jazz Noise'),
]

print("  Hybrid styles:")
for a_name, b_name, hybrid_name in hybrids:
    a = styles[a_name]
    b = styles[b_name]

    best_t = 0.5
    best_quality = 0

    for t in np.linspace(0.1, 0.9, 20):
        rho = a['rho'] * (1 - t) + b['rho'] * t
        sigma = a['sigma'] * (1 - t) + b['sigma'] * t

        sys = LorenzSystem(rho=rho, sigma=sigma)
        sys.run(2000, 1000)
        q = QualityMetrics.from_outputs(sys.outputs).quality

        if q > best_quality:
            best_quality = q
            best_t = t

    rho_opt = a['rho'] * (1 - best_t) + b['rho'] * best_t
    sigma_opt = a['sigma'] * (1 - best_t) + b['sigma'] * best_t

    sys = LorenzSystem(rho=rho_opt, sigma=sigma_opt)
    sys.run(5000, 2000)
    q = QualityMetrics.from_outputs(sys.outputs)

    print(f"    {hybrid_name:20s} ({a_name}×{b_name}): "
          f"ρ={rho_opt:.1f}, σ={sigma_opt:.1f}, "
          f"novelty={q.novelty:.4f}, coherence={q.coherence:.4f}, quality={q.quality:.6f}")

# ─── Part 4: Rapid style switching ───
print("\n--- Part 4: Rapid Style Switching ---")

switch_intervals = [10, 50, 100, 500, 1000]
style_pairs_switch = [('classical', 'jazz'), ('baroque', 'noise')]

for style_a, style_b in style_pairs_switch:
    print(f"\n  {style_a} ↔ {style_b}:")
    for interval in switch_intervals:
        a = styles[style_a]
        b = styles[style_b]

        sys_a = LorenzSystem(rho=a['rho'], sigma=a['sigma'])
        sys_b = LorenzSystem(rho=b['rho'], sigma=b['sigma'])

        sys_a.run(1000, 500)
        sys_b.run(1000, 500)

        combined = []
        current = 'a'
        for step in range(5000):
            if step % interval == 0:
                current = 'b' if current == 'a' else 'a'

            if current == 'a':
                sys_a.step()
                combined.append(sys_a.outputs[-1])
            else:
                sys_b.step()
                combined.append(sys_b.outputs[-1])

        combined = np.array(combined)
        q = QualityMetrics.from_outputs(combined)

        print(f"    switch_every={interval:4d}: quality={q.quality:.6f}, "
              f"novelty={q.novelty:.4f}, coherence={q.coherence:.4f}")

# ─── Part 5: Style DNA extraction ───
print("\n--- Part 5: Style DNA ---")
print("  Style → (ρ, σ) mapping:")
style_dna = {}
for name, params in sorted(styles.items(), key=lambda x: x[1]['rho']):
    sys = LorenzSystem(rho=params['rho'], sigma=params['sigma'])
    sys.run(5000, 2000)
    q = QualityMetrics.from_outputs(sys.outputs)
    style_dna[name] = {
        'rho': params['rho'],
        'sigma': params['sigma'],
        'diversity': sys.diversity(),
        'quality': q.quality,
    }
    print(f"    {name:12s}: ρ={params['rho']:3d}, σ={params['sigma']:2d}, "
          f"div={sys.diversity():.3f}, q={q.quality:.6f}")

with open('CODE/EXPERIMENT-STYLE-TRANSFER.json', 'w') as f:
    json.dump({
        'styles': {k: v for k, v in styles.items()},
        'journey': journey_results,
        'style_dna': style_dna,
    }, f, indent=2, default=str)

print("\n=== STYLE TRANSFER: CONTINUOUS MORPHING THROUGH MUSICAL SPACE ===")
