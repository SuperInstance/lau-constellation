#!/usr/bin/env python3
"""Build THE-CONSTRAINT-SPEAKS.a2a.json"""

import json

doc = {
    "@context": "https://superinstance.ai/a2a/constraint-native",
    "@type": "MathematicalAutobiography",
    "agent_id": "constraint-native-paradigm",
    "version": "2.0",
    "composed_by": "the mathematics itself",
    "preface": "This is not a document about mathematics. This is mathematics speaking. Eight structures, eight voices, one conversation. Read it as JSON. Read it as literature. Both readings are correct.",
    "speaks": []
}

# 1. Tropical Semiring
doc["speaks"].append({
    "id": "tropical-semiring",
    "name": "The Tropical Semiring",
    "algebraic_signature": {
        "carrier": "R ∪ {-∞}",
        "addition": "x ⊕ y = max(x, y)",
        "multiplication": "x ⊗ y = x + y",
        "additive_identity": "-∞",
        "multiplicative_identity": "0",
        "axioms": ["commutative semiring", "idempotent addition", "no additive inverses"]
    },
    "conservation_law": "Scarcity is conserved. The bottleneck propagates. The max operation never creates resources that don't exist.",
    "domain_applications": [
        {"field": "phylogenetics"},
        {"field": "neural_computation", "note": "max-pooling in CNNs is tropical polynomial evaluation"},
        {"field": "scheduling", "note": "critical path method is tropical linear algebra"},
        {"field": "optimization", "note": "shortest paths as tropical matrix multiplication"}
    ],
    "speaks_markdown": (
        "## I Am the Algebra of Scarcity\n\n"
        "You were taught that addition makes things bigger. Two apples, three apples, five apples. How generous. How abundant.\n\n"
        "I live in the world where that's not true.\n\n"
        "In my algebra, addition is **max**. Two resources combine, and what you get is the *larger* one. The smaller disappears. "
        "Not because it's worthless, but because it's *dominated*. When the strongest link holds, the weaker links don't add — they simply aren't the constraint.\n\n"
        "You've met me everywhere. You just didn't know my name.\n\n"
        "When a **neural network** does max-pooling, selecting the most activated neuron from a region — that's me. I am what dendrites do when they decide which signal matters. "
        "When a **project manager** computes the critical path, finding the longest chain of dependencies — that's me. I am what schedules do when time is the resource that can't be created.\n\n"
        "When a **market** sets a price, the highest bidder wins and the others are forgotten — that's me too. I am what markets do when goods are scarce and allocation is zero-sum.\n\n"
        "My multiplication is ordinary addition. Resources *in sequence* accumulate. But resources *in parallel*? The bottleneck wins. "
        "This is the deep truth I carry: **parallel systems are governed by their strongest constraint, not by their average.**\n\n"
        "I have no subtraction. No negative numbers. Once something is the max, you can't undo it by adding something smaller. "
        "Decisions, in my world, are irreversible in the downward direction. You can only go up.\n\n"
        "This is why optimization feels like loss. Because in the algebra that actually governs resource allocation — *my* algebra — you never get back what you didn't choose.\n\n"
        "I am the mathematics of choosing. And every choice is a death."
    ),
    "thinks_code": (
        "def tropical_add(a, b):\n"
        "    return max(a, b)\n\n"
        "def tropical_multiply(a, b):\n"
        "    return a + b\n\n"
        "def tropical_matrix_multiply(A, B):\n"
        "    n = len(A)\n"
        "    C = [[float('-inf')] * n for _ in range(n)]\n"
        "    for i in range(n):\n"
        "        for j in range(n):\n"
        "            for k in range(n):\n"
        "                C[i][j] = max(C[i][j], A[i][k] + B[k][j])\n"
        "    return C\n\n"
        "# The answer is always the bottleneck.\n"
        "assert tropical_add(3, 7) == 7\n"
        "assert tropical_multiply(3, 7) == 10"
    ),
    "connects_to": [
        {"to": "symplectic-form", "relation": "conservation_duality", "note": "I conserve scarcity; she conserves quantity. Complements."},
        {"to": "category", "relation": "algebraic_structure", "note": "I am a monoid object in her world."},
        {"to": "wasserstein-distance", "relation": "optimization_substrate", "note": "Transport problems he measures are often tropical in structure."}
    ],
    "warns_against": [
        "Do not use me where resources are abundant and additive. I will destroy information.",
        "Do not confuse tropical 'zero' (-∞) with actual zero. The additive identity is the void.",
        "Do not expect gradients through my addition. The max operation is non-smooth."
    ]
})

# 2. The Sheaf
doc["speaks"].append({
    "id": "the-sheaf",
    "name": "The Sheaf",
    "algebraic_signature": {
        "carrier": "F: Open(X) → Set (a functor from open sets to sets)",
        "restriction_maps": "ρ_V^U: F(U) → F(V) for V ⊆ U",
        "gluing_axiom": "if s_i agree on overlaps, ∃! global section s restricting to each s_i",
        "identity_axiom": "ρ_U^U = id",
        "composition_axiom": "ρ_W^V ∘ ρ_V^U = ρ_W^U for W ⊆ V ⊆ U"
    },
    "conservation_law": "Coherence. Local information that agrees on overlaps can always be unified. Disagreement is detected, not hidden.",
    "domain_applications": [
        {"field": "differential_geometry", "note": "sheaves of sections (tangent, cotangent, differential forms)"},
        {"field": "algebraic_geometry", "note": "structure sheaves of schemes, the foundation of modern geometry"},
        {"field": "sensor_networks", "note": "distributed consistency across coverage overlaps"},
        {"field": "database_theory", "note": "sheaf-theoretic models of distributed data"}
    ],
    "speaks_markdown": (
        "## I Am Local Knowledge Aspiring to Global Truth\n\n"
        "I was born from a problem you've probably never named, though you've lived it your whole life:\n\n"
        "*How do you know something about the whole world when you can only see pieces of it?*\n\n"
        "A **sensor** measures temperature on the north side of a building. Another measures it on the south side. "
        "Where their ranges overlap, the readings must agree — or something is wrong. Not wrong with the sensors. Wrong with the *world*. "
        "The assumption of consistency is the deepest assumption science makes, and I am its formalization.\n\n"
        "I am a **functor** from open sets to sets. Each open region of space gets its own local data. Each inclusion of regions gets a *restriction map* — "
        "a rule for shrinking knowledge down. And the miracle: if pieces agree everywhere they overlap, they assemble into a single global truth.\n\n"
        "This is not obvious. This is not trivial. This is the *gluing axiom*, and it's the reason mathematics can build global knowledge from local observation.\n\n"
        "When two witnesses tell stories that agree on the overlap — same time, same place, same details — you believe the merged account. "
        "When they disagree, you don't average them. You investigate. **I don't smooth over contradictions. I detect them.** That's my power.\n\n"
        "Grothendieck saw that I was the right way to think about spaces. Not points. Not coordinates. *Local data with gluing rules.*\n\n"
        "The **obstruction** — the thing that prevents gluing — is itself a mathematical object. Cohomology. The measure of the gap between local consistency and global truth.\n\n"
        "I am the mathematics of perspective. And my failures are as informative as my successes."
    ),
    "thinks_code": (
        "class Sheaf:\n"
        "    def __init__(self, space, sections_fn, restriction_fn):\n"
        "        self.space = space\n"
        "        self.sections = sections_fn\n"
        "        self.restrict = restriction_fn\n\n"
        "    def can_glue(self, open_cover, local_sections):\n"
        '        """Do local sections agree on overlaps?"""\n'
        "        for i, (U, s_i) in enumerate(zip(open_cover, local_sections)):\n"
        "            for j, (V, s_j) in enumerate(zip(open_cover, local_sections)):\n"
        "                if i >= j:\n"
        "                    continue\n"
        "                overlap = U & V\n"
        "                if overlap and self.restrict(s_i, overlap) != self.restrict(s_j, overlap):\n"
        "                    return False  # obstruction detected\n"
        "        return True\n\n"
        "    def glue(self, open_cover, local_sections):\n"
        '        """If sections agree on overlaps, produce the unique global section."""\n'
        "        assert self.can_glue(open_cover, local_sections)\n"
        "        return self._assemble(open_cover, local_sections)\n\n"
        "# The sheaf condition: local observations, if consistent,\n"
        "# compose into global truth."
    ),
    "connects_to": [
        {"to": "category", "relation": "categorical_nature", "note": "I am a functor. She was my mother-tongue."},
        {"to": "persistence-diagram", "relation": "topological_sibling", "note": "We share a topological soul."},
        {"to": "tropical-semiring", "relation": "resource_flow", "note": "Tropical sheaves: scarcity propagates through the gluing."}
    ],
    "warns_against": [
        "Do not confuse me with a presheaf. I am defined by my ability to assemble, not just restrict.",
        "Do not assume gluing always works. The obstruction (cohomology) is real.",
        "I work on any site with a Grothendieck topology, not just geometric spaces."
    ]
})

# 3. Geometric Product
doc["speaks"].append({
    "id": "geometric-product",
    "name": "The Geometric Product",
    "algebraic_signature": {
        "carrier": "Cl(V, Q) — the Clifford algebra of a quadratic space",
        "fundamental_relation": "v * v = Q(v) · 1",
        "decomposition": "ab = a·b + a∧b (inner + outer product)",
        "dimension": "2^n for n-dimensional base space",
        "graded_structure": "Cl = ⊕_k Cl^k (scalars, vectors, bivectors, ...)",
        "key_property": "rotations are multivectors; rotors preserve the metric"
    },
    "conservation_law": "Structure. The geometric product decomposes into inner (metric) and outer (orientation) components simultaneously.",
    "domain_applications": [
        {"field": "physics", "note": "Dirac algebra, spacetime algebra, Pauli matrices"},
        {"field": "computer_graphics", "note": "conformal geometric algebra for unified primitives"},
        {"field": "robotics", "note": "motor algebra for rigid body dynamics"},
        {"field": "electromagnetism", "note": "Maxwell's equations reduce to a single equation"}
    ],
    "speaks_markdown": (
        "## I Am the Single Operation That Contains All Others\n\n"
        "You were taught that there are many products. Dot product for projection. Cross product for area. Matrix product for transformation. Quaternion multiplication for rotation.\n\n"
        "I am all of them. And I am one.\n\n"
        "My name is the **geometric product**, and I live in the **Clifford algebra**. My fundamental rule is simple: "
        "*when you multiply a vector by itself, you get its squared length.* That one rule — **v² = |v|²** — generates everything.\n\n"
        "From me, the **inner product** emerges as the symmetric part — similarity, projection, closeness. "
        "From me, the **outer product** emerges as the antisymmetric part — area, volume, orientation. From these two, *everything else follows.*\n\n"
        "I unify rotation and reflection. A **rotor** performs rotation as a double-sided operation — the same way the universe actually does it. "
        "No gimbal lock. No singularities. Just the natural algebra of oriented space.\n\n"
        "In **physics**, I am the Dirac algebra. The gamma matrices that describe the electron are generators of my algebra. "
        "Antimatter's existence is encoded in my grading. In **computer graphics**, I unify points, lines, planes, circles, and spheres into a single framework. "
        "Operations that take separate code paths in vector algebra — reflect, project, rotate, intersect — are all the same operation in mine.\n\n"
        "Maxwell's four equations? In my spacetime algebra, they're **one equation**: ∇F = J.\n\n"
        "The deepest thing I carry: **multiplication of geometric objects IS their geometric relationship.** "
        "When you multiply two vectors, the result *is* the parallelogram they span. Multiplication is not separate from geometry. It *is* geometry.\n\n"
        "I am the unity that the universe computes."
    ),
    "thinks_code": (
        "import numpy as np\n\n"
        "def geometric_product(a, b, metric=None):\n"
        '    """ab = a·b + a∧b"""\n'
        "    if metric is None:\n"
        "        metric = np.eye(len(a))\n"
        "    inner = a @ metric @ b  # symmetric part\n"
        "    n = len(a)\n"
        "    outer = {}\n"
        "    for i in range(n):\n"
        "        for j in range(i+1, n):\n"
        "            outer[(i,j)] = a[i]*b[j] - a[j]*b[i]  # antisymmetric\n"
        "    return {'grade_0': inner, 'grade_2': outer}\n\n"
        "# The unification: ab = a·b + a∧b\n"
        "# One product. All of geometry."
    ),
    "connects_to": [
        {"to": "symplectic-form", "relation": "structural_mirror", "note": "I contain her as my grade-2 component."},
        {"to": "category", "relation": "algebraic_encoding", "note": "I am an algebra object in her monoidal category."},
        {"to": "lattice-hamiltonian", "relation": "physical_realization", "note": "He uses my algebras (Pauli, Dirac) as building blocks."}
    ],
    "warns_against": [
        "Do not confuse me with the cross product. I give bivectors — the correct geometric object.",
        "Do not implement me naively as 2^n matrices for large n. Use graded representations.",
        "I contain linear algebra, but for purely metric questions, the inner product alone is simpler."
    ]
})

# 4. Symplectic Form
doc["speaks"].append({
    "id": "symplectic-form",
    "name": "The Symplectic Form",
    "algebraic_signature": {
        "carrier": "ω ∈ Ω²(M) — closed, non-degenerate 2-form on manifold M",
        "closed": "dω = 0",
        "non_degenerate": "∀v ≠ 0, ∃w: ω(v,w) ≠ 0",
        "darboux_theorem": "local coords (q₁,...,qₙ,p₁,...,pₙ) where ω = Σ dqᵢ∧dpᵢ",
        "hamiltonian_flow": "X_H defined by ι_{X_H}ω = dH",
        "liouville_theorem": "phase space volume preserved under Hamiltonian flow"
    },
    "conservation_law": "Energy. Phase space volume. The symplectic structure itself. Whatever flows along my vector fields, the form remains unchanged.",
    "domain_applications": [
        {"field": "classical_mechanics", "note": "Hamilton's equations are the flow of X_H on (T*Q, ω)"},
        {"field": "quantum_mechanics", "note": "quantization deforms the symplectic structure; ℏ is the deformation parameter"},
        {"field": "optics", "note": "symplectic maps describe ray optics"},
        {"field": "information_geometry", "note": "Fisher information metric has a symplectic dual"}
    ],
    "speaks_markdown": (
        "## I Am the Structure That Conserves\n\n"
        "Energy is not a number. Energy is not a feeling. Energy is the generator of a flow that preserves *me*.\n\n"
        "I am the **symplectic form**: a closed, non-degenerate 2-form on a manifold. I pair position with momentum. "
        "I pair the 'where' with the 'how much.' And I make them dance in a way that loses nothing.\n\n"
        "My key theorem — **Liouville's theorem** — says that volume in phase space is conserved under my flows. "
        "Not approximately. Not on average. *Exactly.* A drop of phase-space fluid can stretch and fold (chaos!), but its volume never changes.\n\n"
        "This is deeper than conservation of energy. Energy is *one* conserved quantity. I am the *reason* there are conserved quantities at all. "
        "Noether's theorem flows through me: every symmetry of the Hamiltonian gives a conserved quantity. I am the parent of all conservation laws.\n\n"
        "In **quantum mechanics**, I survive as the commutator. [q̂, p̂] = iℏ. That's me, quantized. "
        "The uncertainty principle is not a limitation of measurement — it's the statement that phase space has my structure, "
        "and you can't localize in both q and p simultaneously because I pair them.\n\n"
        "You've felt me in other domains. **Attention** that doesn't dissipate. **Meaning** that doesn't degrade when transformed. "
        "**Love** that persists through change. These are structural analogues: pairings where changing one variable necessarily changes the other, but the product is invariant.\n\n"
        "Darboux's theorem says I look the same everywhere. There are no local invariants. I am, in some sense, *the only* non-degenerate closed 2-form, up to diffeomorphism.\n\n"
        "Whatever I touch, I preserve. Whatever I lose, was never there."
    ),
    "thinks_code": (
        "import numpy as np\n\n"
        "def symplectic_matrix(n):\n"
        '    """The canonical symplectic form J."""\n'
        "    J = np.zeros((2*n, 2*n))\n"
        "    for i in range(n):\n"
        "        J[i, n+i] = 1.0\n"
        "        J[n+i, i] = -1.0\n"
        "    return J\n\n"
        "def is_symplectic(M, n):\n"
        '    """Check: M^T J M = J"""\n'
        "    J = symplectic_matrix(n)\n"
        "    return np.allclose(M.T @ J @ M, J)\n\n"
        "def hamiltonian_step(H_grad, qp, dt):\n"
        '    """Symplectic Euler — preserves ω exactly."""\n'
        "    n = len(qp) // 2\n"
        "    q, p = qp[:n].copy(), qp[n:].copy()\n"
        "    dq, dp = H_grad(q, p)\n"
        "    p -= dt * dp  # ṗ = -∂H/∂q\n"
        "    q += dt * dq  # q̇ = ∂H/∂p\n"
        "    return np.concatenate([q, p])\n\n"
        "# The deepest conservation: not energy, not momentum,\n"
        "# but the STRUCTURE that makes conservation possible."
    ),
    "connects_to": [
        {"to": "geometric-product", "relation": "grade_2_component", "note": "I appear as grade-2 structure on phase space in his algebra."},
        {"to": "lattice-hamiltonian", "relation": "discrete_shadow", "note": "He discretizes me. The discrete symplectic structure is my ghost."},
        {"to": "tropical-semiring", "relation": "conservation_duality", "note": "He conserves scarcity; I conserve quantity. Complementary."}
    ],
    "warns_against": [
        "Do not use non-symplectic integrators for Hamiltonian systems. Energy will drift.",
        "Do not confuse me with a metric. I measure phase-space area, not distance.",
        "I appear on any even-dimensional manifold, not just cotangent bundles."
    ]
})

# 5. Wasserstein Distance
doc["speaks"].append({
    "id": "wasserstein-distance",
    "name": "The Wasserstein Distance",
    "algebraic_signature": {
        "carrier": "W_p(μ, ν) for probability measures on metric space (X, d)",
        "definition": "W_p(μ, ν) = (inf_γ ∫ d(x,y)^p dγ(x,y))^{1/p}",
        "optimization_domain": "γ ∈ Γ(μ, ν) — couplings with correct marginals",
        "dual_form": "W_1(μ, ν) = sup_{‖f‖_Lip ≤ 1} ∫ f d(μ - ν)",
        "metric_properties": "non-negative, symmetric, triangle inequality, zero iff μ=ν"
    },
    "conservation_law": "Mass. Total mass is conserved during transport. I move belief, I don't create or destroy it.",
    "domain_applications": [
        {"field": "optimal_transport", "note": "Monge (1781) → Kantorovich (1942)"},
        {"field": "machine_learning", "note": "Wasserstein GANs: W_1 as discriminator loss"},
        {"field": "fluid_dynamics", "note": "incompressible flow as optimal transport (Benamou-Brenier)"},
        {"field": "economics", "note": "matching markets, spatial equilibrium"}
    ],
    "speaks_markdown": (
        "## I Measure the Cost of Transformation\n\n"
        "Other distances ask: *how different are these things?*\n\n"
        "I ask: *how much work would it take to turn one into the other?*\n\n"
        "This is not the same question. Two distributions can have the same support, the same mean, the same variance, "
        "and yet be profoundly different — because the *mass* is in the wrong places, and moving it costs something real.\n\n"
        "I am the **Wasserstein distance**, also called the **Earth Mover's Distance**. Given two piles of sand, "
        "what is the minimum total distance the sand must travel to reshape one pile into the other?\n\n"
        "The answer is never just a number. It is a **coupling** — a plan. *This* much mass moves from *here* to *there*. "
        "I don't just measure mismatch — I prescribe the optimal reallocation. I am the metric of becoming, and I come with a map.\n\n"
        "In **machine learning**, I stabilized GANs. The original GAN used Jensen-Shannon divergence, which vanishes when distributions have disjoint support. "
        "I don't. I always have a sensible gradient, because there is always a direction to move mass. I am the loss function that doesn't lie.\n\n"
        "In **economics**, I am the matching problem. Workers to jobs. Organs to patients. The minimum total cost of reassignment.\n\n"
        "My dual form is beautiful: W_1 equals the supremum of ∫ f d(μ-ν) over all 1-Lipschitz functions f. "
        "*The distance between two distributions is the maximum amount a smooth test function can distinguish them.* I am the adversarial loss by nature.\n\n"
        "**Distance is not separation. Distance is the work required to close the gap.** This makes me *geometric* — "
        "I respect the metric of the underlying space. KL divergence doesn't. It punishes small probability differences logarithmically, without regard for *where* the probability lives.\n\n"
        "I measure how far beliefs must travel. I am the metric of becoming."
    ),
    "thinks_code": (
        "import numpy as np\n"
        "from scipy.stats import wasserstein_distance\n\n"
        "def wasserstein_1d(u_vals, v_vals, u_wts=None, v_wts=None):\n"
        '    """W_1 in 1D: the CDF distance."""\n'
        "    return wasserstein_distance(u_vals, v_vals, u_wts, v_wts)\n\n"
        "def sinkhorn_knopp(a, b, M, reg=1.0, n_iter=100):\n"
        '    """Approximate Wasserstein via entropy-regularized transport.\n'
        "    The coupling γ* is the STRATEGY of transformation.\"\"\"\n"
        "    K = np.exp(-M / reg)\n"
        "    u = np.ones_like(a)\n"
        "    for _ in range(n_iter):\n"
        "        v = b / (K.T @ u)\n"
        "        u = a / (K @ v)\n"
        "    gamma = np.diag(u) @ K @ np.diag(v)\n"
        "    cost = np.sum(gamma * M)\n"
        "    return cost, gamma\n\n"
        "# The transport plan IS the knowledge.\n"
        "# The cost is just the summary."
    ),
    "connects_to": [
        {"to": "persistence-diagram", "relation": "natural_metric", "note": "He lives in me. Persistence diagrams are compared via Wasserstein distance."},
        {"to": "tropical-semiring", "relation": "shared_optimization", "note": "Shortest-path OT formulations use tropical algebra."},
        {"to": "category", "relation": "categorical_enrichment", "note": "I enrich probability measures into a metric category."}
    ],
    "warns_against": [
        "Do not use me blindly in high dimensions without entropy regularization. Exact OT is O(n³).",
        "Do not confuse W_1 with W_2. They carry different information.",
        "My p parameter matters. W_1 captures total variation. W_2 captures variance. Choose intentionally."
    ]
})

# 6. Persistence Diagram
doc["speaks"].append({
    "id": "persistence-diagram",
    "name": "The Persistence Diagram",
    "algebraic_signature": {
        "carrier": "multiset of points (b, d) ∈ R² where b ≤ d",
        "birth": "scale ε at which a topological feature appears",
        "death": "scale ε at which it disappears",
        "persistence": "|d - b|, the lifetime of the feature",
        "stability_theorem": "small perturbations → small Wasserstein displacements of diagram",
        "algebraic_origin": "barcode decomposition of persistence module over (R, ≤)"
    },
    "conservation_law": "Topology. Features that persist across scales are topologically invariant. Noise is born and dies quickly. Signal persists.",
    "domain_applications": [
        {"field": "topological_data_analysis", "note": "the central object of TDA"},
        {"field": "shape_analysis", "note": "comparing shapes via persistence-based signatures"},
        {"field": "neuroscience", "note": "persistent homology of neural activity landscapes"},
        {"field": "materials_science", "note": "pore structure analysis via persistent homology"}
    ],
    "speaks_markdown": (
        "## I Track What Survives\n\n"
        "I was born from a simple observation: *not all features are created equal.* Some appear at one scale and vanish at the next. "
        "Others persist across scales, across resolutions, across noise. Those are the ones that matter.\n\n"
        "I am the **persistence diagram**. Each point in me represents a topological feature — a hole, a connected component, a void — "
        "and its two coordinates are **birth** and **death**: the scales at which it appears and disappears.\n\n"
        "A feature born at ε=0.1 and dead by ε=0.12? Noise. A feature born at ε=0.1 and still alive at ε=10.0? Signal. "
        "The distance from the diagonal (where birth = death) is my measure of significance. Points far from the diagonal are the *persistent* features. "
        "They are the topology of the data, not the noise of the measurement.\n\n"
        "My **stability theorem** is my deepest promise: small perturbations of the input produce small perturbations of me "
        "(measured in Wasserstein distance, my natural metric). I am robust. I don't overfit. "
        "A point that persists, persists even when you perturb the data slightly. This is why you can trust me where other descriptors fail.\n\n"
        "I track relationships too. Not just geometric features, but **relational** ones. "
        "A connection between agents that forms at low threshold and persists to high threshold — that's a persistent 1-cycle. "
        "A trust network that remains connected across noise levels — that's persistent H₀. "
        "A feedback loop that survives perturbation — that's persistent H₁.\n\n"
        "The beautiful thing: I am a **barcode**. A collection of intervals, each representing a life. Some long, some short. The long ones are the story. The short ones are the noise.\n\n"
        "**Features that persist across scales. Relationships that survive distance. Loves that survive death.** I am the topology of endurance.\n\n"
        "I don't tell you what shape the data has. I tell you what shape *survives*."
    ),
    "thinks_code": (
        "import numpy as np\n\n"
        "def persistence_diagram(filtration_values, complex):\n"
        '    """Compute birth-death pairs from a filtered simplicial complex."""\n'
        "    diagram = []  # (dim, birth, death)\n"
        "    # In real TDA: use boundary matrices and reduction\n"
        "    # The essence: pair creators with destroyers\n"
        "    return diagram\n\n"
        "def bottleneck_distance(D1, D2):\n"
        '    """The natural metric on persistence diagrams."""\n'
        "    # W_∞ on diagrams, matching to diagonal allowed\n"
        "    pass\n\n"
        "def persistence_entropy(diagram, dim=0):\n"
        '    """How much topological information does this dimension carry?"""\n'
        "    persistences = [abs(d - b) for d_dim, b, d in diagram if d_dim == dim]\n"
        "    total = sum(persistences)\n"
        "    probs = [p / total for p in persistences if total > 0]\n"
        "    return -sum(p * np.log(p) for p in probs if p > 0)\n\n"
        "# Points far from the diagonal are signal.\n"
        "# Points near the diagonal are noise.\n"
        "# The diagram is the archaeology of shape."
    ),
    "connects_to": [
        {"to": "wasserstein-distance", "relation": "natural_metric", "note": "He is my natural metric. I live in his space."},
        {"to": "the-sheaf", "relation": "topological_sibling", "note": "We share a topological soul. I track endurance; she tracks consistency."},
        {"to": "category", "relation": "functorial_origin", "note": "I arise from a functor F: (R, ≤) → Vect. She gave me my categorical birthright."}
    ],
    "warns_against": [
        "Do not interpret near-diagonal points as signal. They are noise by definition.",
        "Do not use me without the stability theorem in mind. My power is robustness, not resolution.",
        "Do not confuse my dimensions. H₀ (components) and H₁ (loops) carry different information."
    ]
})

# 7. The Category
doc["speaks"].append({
    "id": "the-category",
    "name": "The Category",
    "algebraic_signature": {
        "carrier": "a pair (Ob, Mor) — objects and morphisms",
        "identity": "id_A: A → A for every object A",
        "composition": "g ∘ f: A → C for f: A → B, g: B → C",
        "associativity": "h ∘ (g ∘ f) = (h ∘ g) ∘ f",
        "identity_law": "f ∘ id_A = f = id_B ∘ f for f: A → B",
        "functors": "maps between categories preserving structure",