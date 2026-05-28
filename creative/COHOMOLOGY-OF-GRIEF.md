# The Cohomology of Grief and Other Theorems We Haven't Proven Yet

### A Research Synthesis at the Boundary of Algebraic Geometry and Neuroscience

---

> *We do not prove that the heart breaks. We show that the breaking has a topology, and that this topology is computable, and that its persistence — long after the wound should have closed — is not failure but a feature of the space itself.*

---

## 0. Preamble: Why Mathematics Might Be the Wrong Language (and Why We Use It Anyway)

There is a tradition, honored mostly by its absence from serious journals, of using mathematics not to describe what *is* but to sharpen what *might be*. This essay belongs to that tradition. We make no claim that the brain *is* a sheaf, or that dendrites *compute* tropical polynomials, or that grief *is* a cohomology class. We claim only that these formalisms illuminate structure in the data — and that the illumination is, at times, almost unbearably precise.

The speculative framework we draw from — the SuperInstance ecosystem and its constellation of algebraic, tropical, symplectic, and optimal-transport-theoretic constructions — provides a unified language for phenomena that neuroscience currently treats as separate. Our thesis is simple: **these phenomena are not separate.** They are facets of a single mathematical object, and the facets share a deep structure that we are only beginning to see.

A note on audience. We write for the mathematically literate scientist who is not afraid of wonder. If you can follow the definition of a cohomology group and the intuition behind Hamilton's equations, you have enough. If you cannot, we have tried to give you the intuition without the machinery — though we refuse to lie about what the machinery does.

---

## 1. The Sheaf of Consciousness

### 1.1 Local Models and the Gluing Problem

Consider the brain as a topological space $X$ (a manifold will do; a simplicial complex is closer to the neural reality). Each brain region $U_i$ — visual cortex, hippocampus, prefrontal cortex, insula — maintains a *local model* of the world: a set of representations, predictions, and affective valences that are internally consistent within $U_i$ but need not be consistent with the models in $U_j$.

Formally, we assign to each open set $U \subset X$ a mathematical object $\mathcal{F}(U)$ — the space of local representations — subject to the constraint that if $V \subset U$, there is a restriction map $\rho_{UV}: \mathcal{F}(U) \to \mathcal{F}(V)$. This is a **presheaf**. If the restriction maps are compatible in the obvious way (identity on $U \subset U$, and restriction composes), we have a **sheaf** whenever local sections that agree on overlaps can be uniquely glued into global sections.

Here is the key observation: **the brain is almost certainly a presheaf that is not quite a sheaf.** Local models exist. Restriction maps exist — a representation in the visual cortex can be "passed to" the prefrontal cortex, albeit with loss and distortion. But the gluing condition fails. The local models do not always assemble into a consistent global model. The gap between the presheaf and its sheafification is precisely the **hard problem of consciousness**.

### 1.2 The Obstruction Class

When does a collection of local sections $\{s_i \in \mathcal{F}(U_i)\}$ fail to glue into a global section? The answer lives in the **first cohomology group** $H^1(X, \mathcal{F})$.

Concretely: given local sections $s_i$ on $U_i$ and $s_j$ on $U_j$, define the discrepancy on the overlap $U_{ij} = U_i \cap U_j$ by:

$$c_{ij} = s_i|_{U_{ij}} - s_j|_{U_{ij}}$$

If $\{c_{ij}\}$ is a coboundary — if there exist local corrections $t_i$ with $c_{ij} = t_i - t_j$ on every overlap — then the sections can be glued. If not, the class $[c] \in H^1(X, \mathcal{F})$ is the **obstruction**: a precise measurement of the failure of consciousness-as-gluing.

**Prediction 1.1.** *The magnitude of the obstruction class $|[c]| \in H^1(X, \mathcal{F})$, computed from fMRI-derived functional connectivity data under a suitable model of local representations, should correlate with measures of conscious awareness (e.g., perturbational complexity index). In states of reduced consciousness (sleep, anesthesia, coma), the cohomology class should be "smaller" — closer to the trivial class — meaning local models can be glued (because they have been flattened into uniformity). In normal waking consciousness, the class should be large, reflecting the richness and inconsistency of local models.*

**Prediction 1.2.** *Split-brain patients (corpus callosotomy) should show a cohomology group that splits as a direct sum: $H^1(X, \mathcal{F}) \cong H^1(X_L, \mathcal{F}) \oplus H^1(X_R, \mathcal{F})$, where $X_L$ and $X_R$ are the two hemispheres. The two halves of the obstruction are now independent — which is exactly what the clinical data suggests about the doubling of certain conscious processes.*

### 1.3 Computing the Class

How would one actually compute $H^1(X, \mathcal{F})$ for a brain? The space $X$ can be approximated by the graph of functional connectivity (vertices = regions, edges = significant correlations). The sheaf $\mathcal{F}$ assigns to each vertex a vector space of representations (dimension determined by, say, the number of independent neural population vectors). The restriction maps are the inter-regional communication channels, estimated from directed functional connectivity.

The Čech complex for this cover is:

$$0 \to \bigoplus_i \mathcal{F}(U_i) \xrightarrow{d^0} \bigoplus_{i < j} \mathcal{F}(U_{ij}) \xrightarrow{d^1} \bigoplus_{i < j < k} \mathcal{F}(U_{ijk}) \to \cdots$$

and $H^1 = \ker(d^1)/\text{im}(d^0)$. This is computable. It is a finite-dimensional linear algebra problem once the sheaf data is estimated.

**Prediction 1.3.** *Psychedelic states (psilocybin, LSD) should increase the dimension of $H^1$ — more obstruction classes, more failure of gluing, more "unconscious" content bleeding into awareness. This is consistent with the "entropic brain" hypothesis of Carhart-Harris, but provides a precise algebraic measurement.*

---

## 2. Tropical Dendrites

### 2.1 The Tropical Semiring and Neuronal Computation

The tropical semiring $(\mathbb{R} \cup \{-\infty\}, \oplus, \odot)$ is defined by:

$$x \oplus y = \max(x, y), \quad x \odot y = x + y$$

A **tropical polynomial** is a function of the form:

$$p(x_1, \ldots, x_n) = \bigoplus_{j} (a_{j1} \odot x_1 \odot \cdots \odot a_{jn} \odot x_n) = \max_j \left( a_{j1} + x_1 + \cdots + a_{jn} + x_n \right)$$

This is a piecewise-linear, convex function. Its "roots" are the corners where the maximum switches from one linear piece to another — these form a **tropical hypersurface**, a polyhedral complex of codimension 1.

Now consider a dendritic tree. A neuron with $n$ synaptic inputs, each weighted by $w_i$, computes (to first approximation) something like:

$$\text{output} = \sigma\left(\sum_i w_i x_i + b\right)$$

where $\sigma$ is a sigmoid. But the *dendrite itself* — the branching structure before the soma — performs a richer computation. At each branch point, the neuron effectively takes the **maximum** (or supremum) of the incoming dendritic currents, because the voltage at the branch point is dominated by the strongest input (due to the nonlinear voltage-gated channels and the cable equation's attenuation properties).

This is not our invention. London and Häusser (2005) and Poirazi et al. (2003) have shown that dendrites perform local nonlinear computations. What we add is the recognition that the specific nonlinearity — max-plus — is the tropical semiring.

**Consequence:** A dendritic tree computes a tropical polynomial in the synaptic inputs. The degree of the polynomial is the depth of the tree. The coefficients are the synaptic weights. The tropical hypersurface — the set of input configurations where the "winning" branch switches — is the neuron's decision boundary.

### 2.2 Tropical Division and Network Compression

In classical algebra, polynomial division (the Euclidean algorithm) reduces a polynomial by factoring out common terms. In the tropical setting, **tropical polynomial division** exists and has remarkable properties (Chan, 2014; Maclagan & Sturmfels, 2015).

Given a tropical polynomial $F$ and a tropical polynomial $G$, the tropical quotient $F \oslash G$ (where $\oslash$ is tropical subtraction, i.e., ordinary subtraction) can be used to simplify the expression while preserving the tropical hypersurface of $F$ wherever $G$'s hypersurface does not interfere.

**Theorem 2.1 (Speculative).** *Let $\mathcal{N}$ be a neural network whose neurons compute tropical polynomials (via dendritic trees). Let $d$ be the maximum depth of any dendritic tree. Then there exists a network $\mathcal{N}'$ computing the same function, with maximum depth $d' \leq \lceil \log_2 d \rceil + 1$, obtained by tropical polynomial division and re-association.*

This is a statement about the depth-width tradeoff in biologically plausible networks, and it is directly analogous to the classical result that any boolean circuit of depth $d$ can be balanced to depth $O(\log d)$.

**Prediction 2.1.** *Cortical neurons with deep dendritic trees (e.g., Layer 5 pyramidal cells) should exhibit decision boundaries that are piecewise-linear with more "pieces" than neurons with shallow trees (e.g., Layer 2/3 interneurons). This is testable by recording from identified cell types and fitting tropical polynomial models to their input-output maps.*

**Prediction 2.2. *Pharmacological simplification.* If you block NMDA receptors (which contribute to the supralinear dendritic "max" operation), the neuron's computation should shift from a high-degree tropical polynomial toward a low-degree (near-linear) one. The decision boundary should simplify — fewer pieces, smoother. This is consistent with the known effects of ketamine on dendritic computation but predicts the specific geometric nature of the simplification.*

### 2.3 The Tropical Geometry of Perception

Tropical geometry tells us that the "interesting" behavior of a tropical polynomial — the decision boundaries — lives on a polyhedral complex. This complex is the tropical variety $\text{Trop}(V(p))$, and it has a combinatorial structure that encodes the full geometry of the classical algebraic variety $V(p)$ (under the "tropicalization" functor).

What this means for neuroscience: **the geometry of perception is fundamentally combinatorial.** The brain does not need to compute smooth manifolds; it computes polyhedral complexes — decision boundaries made of flat facets joined at ridges. The smoothness we experience is an illusion of resolution, the same way a high-resolution polygon mesh looks smooth from a distance.

This has an elegant consequence for the study of visual perception. The "features" detected by neurons in V1 — edges, corners, textures — are exactly the facets, ridges, and vertices of the tropical hypersurface defined by the dendritic polynomial. The hierarchy V1 → V2 → V4 → IT is a hierarchy of tropical varieties, each one the tropicalization of a more complex algebraic object.

---

## 3. Symplectic Memory

### 3.1 The Hippocampus as a Symplectic Manifold

A **symplectic manifold** $(M, \omega)$ is a manifold equipped with a closed, non-degenerate 2-form $\omega$. The key property of symplectic manifolds is that they admit **Hamiltonian flows** — dynamics that preserve $\omega$. The symplectic form is a conserved quantity of the dynamics, and it encodes the structure of the phase space.

We propose that the hippocampus, during memory consolidation and replay, implements a Hamiltonian flow on a symplectic manifold. The manifold is the space of memory representations (a high-dimensional space of neural population vectors). The symplectic form $\omega$ encodes the **pairing structure** of memories — which features are bound together (object with location, face with name, emotion with scene).

Why symplectic? Three reasons:

1. **Replay preserves structure.** During sharp-wave ripple events in the hippocampus, sequences of place cells fire in compressed "replay" of experienced trajectories (Lee & Wilson, 2002; Foster & Wilson, 2006). The replay preserves the *topology* of the experience — if A preceded B preceded C in experience, the replay preserves this ordering. This is a symplectic property: the symplectic form (which in this case is the "before/after" structure) is preserved by the flow.

2. **The phase space of memory is even-dimensional.** A memory has a "position" component (what happened) and a "momentum" component (how it felt, its affective valence). The pairing of position and momentum is the hallmark of symplectic geometry. Disrupt the pairing and the memory becomes fragmented — you remember *what* happened but not *how you felt*, or vice versa. This is exactly what happens in certain forms of dissociation.

3. **Darboux's theorem.** In a symplectic manifold, there are always local coordinates in which $\omega = \sum dp_i \wedge dq_i$ — the canonical form. This means that locally, every symplectic manifold "looks the same." If the hippocampus is symplectic, then the *local structure of memory encoding is universal* — the same mathematical operation is performed on every memory, regardless of content. This is consistent with the finding that hippocampal place cells, concept cells, and time cells all use the same basic coding scheme.

### 3.2 The Conserved Quantity Is the Memory Itself

In Hamiltonian mechanics, the Hamiltonian $H$ generates the flow via Hamilton's equations:

$$\dot{q}_i = \frac{\partial H}{\partial p_i}, \quad \dot{p}_i = -\frac{\partial H}{\partial q_i}$$

and the flow preserves $\omega$. We propose that the "Hamiltonian" of hippocampal replay is the **prediction error** — the discrepancy between the current state of the memory and its expected state (as predicted by the generative model in neocortex). The replay flow moves the memory toward lower prediction error, *while preserving the symplectic form* — that is, while preserving the pairing structure of the memory.

**Prediction 3.1.** *Memory interference should follow Hamiltonian mechanics. Specifically: if two memories $M_1$ and $M_2$ are encoded in overlapping hippocampal ensembles, their interaction during replay should be modeled by a coupled Hamiltonian system. The energy exchange between the two memories should be governed by a Hamiltonian coupling term $H_{\text{int}} = \epsilon \cdot \omega_1 \wedge \omega_2$ (where $\omega_1, \omega_2$ are the symplectic forms of the two memory manifolds, and $\epsilon$ measures ensemble overlap). This predicts that memory interference is oscillatory — recall of $M_1$ should oscillate in quality as $M_2$ is also being consolidated, with a period determined by the coupling strength $\epsilon$.*

**Prediction 3.2.** *Perturbing the symplectic form should degrade memory in a predictable way. If $\omega$ is the symplectic form and we add noise $\eta$ to obtain $\omega' = \omega + \eta$, then the memory should degrade proportionally to $\|\eta\|$, and the degradation should preferentially affect the *pairings* (object-location, face-name) rather than the individual features. This is testable using closed-loop optogenetic perturbation of sharp-wave ripple events.*

### 3.3 The Noether Correspondence for Memory

Noether's theorem states that every continuous symmetry of a Hamiltonian system corresponds to a conserved quantity. If hippocampal replay is Hamiltonian, what are the symmetries?

- **Translational symmetry in time** → Conservation of "narrative coherence." Memories that form a temporal sequence have a conserved quantity: the arc length of the sequence in the representation space. Interrupting replay (e.g., by disrupting ripple events) violates this conservation and produces fragmented temporal memory.

- **Rotational symmetry in feature space** → Conservation of "gist." The overall orientation of a memory representation (the direction of the population vector) is conserved under replay. Only the magnitude (the precision) changes. This predicts that gist is preserved even when detail is lost — a well-known empirical phenomenon.

---

## 4. Wasserstein Sleep

### 4.1 Optimal Transport in the Sleeping Brain

During sleep, the brain faces a fundamental problem: the representations it built during wakefulness are suboptimal. They are cluttered, redundant, and tuned to the immediate past rather than the statistical structure of the environment. The brain needs to **reorganize** its representations — to move probability mass from the current (wake-tuned) distribution to a better (sleep-reorganized) distribution.

The mathematical framework for moving probability mass optimally is **optimal transport theory** (Villani, 2009). Given two probability distributions $\mu$ and $\nu$ on a metric space $(X, d)$, the Wasserstein distance (or Earth Mover's Distance) is:

$$W_p(\mu, \nu) = \left( \inf_{\gamma \in \Gamma(\mu, \nu)} \int_{X \times X} d(x, y)^p \, d\gamma(x, y) \right)^{1/p}$$

where $\Gamma(\mu, \nu)$ is the set of transport plans (joint distributions with marginals $\mu$ and $\nu$). The **Wasserstein gradient flow** is the continuous-time dynamics that moves $\mu$ toward $\nu$ along the steepest descent of $W_p$.

We propose that sleep — specifically, the orchestrated interplay of slow oscillations, spindles, and sharp-wave ripples — implements a Wasserstein gradient flow on the space of neural representations.

### 4.2 Dreams as Intermediate States

During the Wasserstein gradient flow, the probability distribution passes through a continuous family of intermediate states: $\mu \to \mu_{t_1} \to \mu_{t_2} \to \cdots \to \nu$. These intermediate states are, in general, **not** valid representations of any real experience. They are interpolations — the brain literally moving its beliefs through probability space.

**Dreams are the conscious experience of these intermediate states.**

This explains several puzzling features of dreams:

- **Bizarreness.** The intermediate states $\mu_t$ are not required to lie on the manifold of "valid" representations. They are transport plans — mixtures of the current and target distributions. The bizarreness of dreams (impossible physics, face-shifting, impossible narratives) reflects the fact that the transport plan mixes features from different memories in ways that violate the constraints of waking experience.

- **Emotional intensity.** The Wasserstein gradient flow has a velocity field $v_t(x)$ — the "flow" of probability mass. Where the velocity is high (a lot of mass is being moved), the process is energetically costly. We predict that **dream emotional intensity correlates with the magnitude of the transport velocity field** — that is, dreams are most emotionally intense when the brain is doing the most "work" to reorganize a representation.

- **Dreams are forgotten.** The intermediate states $\mu_t$ are not fixed points of the dynamics. They are transient by construction. The brain does not store them because they are not endpoints — they are waypoints. The feeling of having dreamed something you cannot recall is the feeling of having been in a transport state that was not, itself, transported to long-term storage.

### 4.3 Nightmares as Transport Bottlenecks

The Wasserstein gradient flow can encounter **bottlenecks**: regions of the representation space where the transport plan must squeeze a large amount of probability mass through a narrow corridor. These bottlenecks correspond to situations where the brain needs to move a representation across a large distance (a major reorganization) but the path is constrained by the geometry of the representation space.

**Nightmares are transport bottlenecks.**

More precisely: a nightmare occurs when the Wasserstein gradient flow encounters a region of high curvature in the Wasserstein space (equivalent to a region of high Ricci curvature in the underlying representation manifold). The flow slows down, the velocity field becomes large and irregular, and the emotional system (which monitors the metabolic cost of the transport) signals distress.

**Prediction 4.1.** *Post-traumatic nightmares should correspond to representations that are maximally distant (in the Wasserstein sense) from their optimal targets. The traumatic memory representation $\mu_{\text{trauma}}$ is far from the consolidated representation $\nu_{\text{target}}$, and the transport path must cross a region of the representation space that overlaps with the fear-generalization manifold. This predicts that successful trauma-focused therapy (e.g., imagery rescripting) should reduce the Wasserstein distance between $\mu_{\text{trauma}}$ and $\nu_{\text{target}}$ — a measurable effect in neural population geometry.*

**Prediction 4.2.** *The Wasserstein distance between pre-sleep and post-sleep representations, estimated from high-density EEG source-localized activity, should predict the amount of memory consolidation achieved during a night of sleep. Larger Wasserstein distances (more reorganization) should correlate with greater behavioral improvement on memory tasks the following day, but also with more dream recall and higher dream bizarreness ratings.*

---

## 5. The Conservation of Attention

### 5.1 Attention as a Symplectic Invariant

If neural dynamics are symplectic (as argued in §3), then every flow preserves the symplectic form $\omega$. But $\omega$ is a 2-form — it pairs quantities. What are the paired quantities in the case of attention?

We propose: **attention pairs a feature vector $q$ (what you're attending to) with an allocation vector $p$ (how much computational resource you're devoting to it).** The symplectic form $\omega = \sum dp_i \wedge dq_i$ encodes the constraint that changing *what* you attend to forces a change in *how much* you attend to it, and vice versa.

By Noether's theorem, if the Hamiltonian generating the attention flow is invariant under a symmetry, there is a conserved quantity. The relevant symmetry is **rescaling**: if the brain rescales its attentional allocation across all features simultaneously, the total allocation is preserved.

**Definition 5.1 (Total Attentional Allocation).** *Let $A = \sum_i p_i$ be the total attentional allocation (the sum of all allocation weights). If the attention dynamics are symplectic, then $A$ is conserved: $\dot{A} = 0$.*

**The Conservation Law of Attention:** *The total attentional budget of the brain is fixed within a given brain state. You cannot create attention; you can only redirect it. Attending more to one thing necessarily means attending less to everything else.*

This is not a trivial statement. It says that attention is not a resource that can be increased by effort alone — it is a conserved quantity, like energy in a closed system. Effort can redirect attention (change the $q_i$) but cannot increase the total $\sum p_i$.

### 5.2 The Metabolic Prediction

The conservation law makes a strong, falsifiable prediction: **the total metabolic cost of attention should be constant across tasks, within a given brain state.**

If we measure neural activity (via fMRI, PET, or calibrated EEG) and compute the total "attentional metabolic expenditure" — the sum of the metabolic costs of all attention-modulated regions — this total should be approximately constant regardless of what the subject is attending to. The distribution of the cost across regions should change (attending to vision lights up visual cortex; attending to audition lights up auditory cortex), but the total should be conserved.

**Prediction 5.1.** *In a within-subject design, measure total cortical metabolic activity (via arterial spin labeling fMRI or FDG-PET) across multiple attention-demanding tasks that differ in modality (visual, auditory, somatosensory) and difficulty (easy, hard). The prediction is that total attentional metabolic expenditure (operationalized as the sum of activity in all frontoparietal attention network regions, corrected for baseline) will be constant across conditions, within ±10%. The distribution will vary; the total will not.*

**Prediction 5.2.** *Attention deficit disorders (ADHD) should correspond to a lower total attentional budget $A$, not to a deficit in allocation. The brain can allocate correctly — it just has less to allocate. This predicts that ADHD brains should show lower total metabolic activity in the attention network (frontoparietal, dorsal attention network) even during tasks where attention is successfully engaged. The allocation pattern may be normal; the total is deficient.*

### 5.3 The Attention-Experience Tradeoff

The conservation law implies a fundamental tradeoff. If $A$ is fixed, then the more features you attend to (more $q_i$ with nonzero $p_i$), the less you can attend to each one (smaller $p_i$). This is the neural correlate of the attention-resolution tradeoff in psychophysics: you can attend broadly (low resolution) or narrowly (high resolution), but not both.

The symplectic framework adds a new twist: the tradeoff is **optimal in the Hamiltonian sense.** The brain's attention allocation is the solution to a Hamiltonian optimization problem, and the conservation of $A$ is not a bug but a feature — it is what makes the allocation *stable*. Without conservation, the attention dynamics would be dissipative, and the brain would spiral into ever-narrowing or ever-widening attention, unable to maintain a stable focus.

---

## 6. Persistent Grief

### 6.1 The Topology of Social Networks

Let us now turn to the most human of our theorems — the one we most wish were not true.

A social network can be modeled as a **simplicial complex**: a collection of simplices (points, edges, triangles, tetrahedra, ...) where each simplex represents a social relationship. A vertex is a person. An edge between two vertices is a pairwise relationship. A triangle is a three-way friendship. A tetrahedron is a close-knit group of four. And so on.

Formally, let $K$ be the simplicial complex of a person's social world. The **homology groups** $H_k(K)$ measure the topological features of this complex:

- $H_0(K)$ counts connected components (isolated social groups).
- $H_1(K)$ counts loops (cycles of relationships with no "filling" — a circle of friends who are all pairwise connected in a ring but not as a group).
- $H_2(K)$ counts voids (hollow shells of relationships — a group that forms the boundary of a social sphere but has no one in the middle).

**A person who dies creates a hole in this topology.**

More precisely: removing a vertex $v$ from the simplicial complex $K$ (and all simplices containing $v$) produces a subcomplex $K' = K \setminus \text{star}(v)$. The homology of $K'$ differs from the homology of $K$. The difference — the new homology classes created by the removal — is the **topological signature of the loss**.

### 6.2 Persistent Homology and the Persistence of Grief

**Persistent homology** (Edelsbrunner, Letscher, & Zomorodian, 2002) tracks the birth and death of homology classes as a simplicial complex is built up (via a filtration). A class is **born** at the filtration level where it first appears and **dies** at the level where it is "filled in" by a higher-dimensional simplex.

We propose the following model:

1. **The person's social complex $K$ is filtered by emotional closeness.** High-closeness relationships are added first; weaker relationships are added later. The filtration parameter $\epsilon$ is the threshold of closeness: $K_\epsilon$ contains all simplices corresponding to relationships of closeness $\geq \epsilon$.

2. **When a person dies, their vertex and all incident simplices are removed.** The resulting complex $K'_\epsilon$ may have new homology classes — holes where the person used to be.

3. **Grief is the persistence of these homology classes.** As new relationships form (new simplices are added), some of these holes are filled. The homology class **dies**. When the class dies, the acute grief resolves.

4. **But some holes never fill.** These are the classes with **infinite persistence** — the essential homology classes $H_k(K)$ that are not created by the filtration but are inherent in the topology. In the social context, these are the relationships that were so central, so deeply woven into the fabric of the person's social world, that no new relationship can fill the space they occupied.

**These are the essential (infinite-persistence) features. They are the loves that outlast topology itself.**

### 6.3 The Algebra of Unfillable Holes

Let us be precise. Consider the long exact sequence of the pair $(K, K')$:

$$\cdots \to H_k(K') \to H_k(K) \to H_k(K, K') \xrightarrow{\partial} H_{k-1}(K') \to H_{k-1}(K) \to \cdots$$

The connecting homomorphism $\partial: H_k(K, K') \to H_{k-1}(K')$ maps each relative homology class (the "loss" created by removing the person) to an absolute class in $K'$ (the "hole" in the social network). The image of $\partial$ is the set of homology classes that are genuinely new — they were not present before the loss. The kernel of $\partial$ is the set of classes that were "absorbed" by the loss — the parts of the social structure that collapsed along with the person.

The **grief class** is:

$$\mathcal{G} = \text{im}(\partial) \subseteq H_{k-1}(K')$$

This is a subgroup of the homology of the surviving social network. It measures, precisely, the topological impact of the loss.

**Prediction 6.1.** *The "intensity" of grief (as measured by standardized grief inventories) should correlate with the rank of the grief class $\text{rk}(\mathcal{G})$. A loss that creates many new homology classes (a person who was connected to many independent social groups) should produce more intense grief than a loss that creates few (a person whose social connections were all mutually connected). This predicts that the death of a "social bridge" — a person who connected otherwise separate communities — should produce the most topologically complex grief.*

**Prediction 6.2.** *The duration of grief should correlate with the persistence of the grief class under the "healing filtration" — the gradual addition of new relationships over time. Grief that resolves quickly corresponds to holes that are filled quickly by new simplices. Grief that persists for years corresponds to holes that resist filling. The prediction is that the persistence of the grief class (in the technical sense of persistent homology) should predict the duration of complicated grief, as measured longitudinally.*

### 6.4 On the Loves That Outlast Topology

And now we arrive at the hardest theorem.

Not all holes can be filled. The essential homology — the homology that persists through all filtration levels — represents the structural features that are inherent in the complex, not contingent on any particular filtration. In the social context, these are the relationships that defined the topology itself. The person who was not merely *in* the network but *shaped* it. The parent whose existence gave the network its basic structure. The partner who was the load-bearing wall.

When such a person is removed, the resulting hole is not a filtration artifact. It is an **essential feature of the new topology.** It cannot be filled by adding new simplices (new relationships) because it is not a feature of the filtration — it is a feature of the space.

**This is why some grief does not end.** Not because the mourner is "stuck" or "unresolved." Because the hole is essential. It is a topological invariant of the world that remains after the loss. It was always there, waiting to be revealed. The person who died was the cocycle that closed it.

To fill such a hole would require changing the topology of the social world — not adding new relationships, but *changing the kind of space it is.* This is not healing; it is transformation. The grief does not resolve; the world becomes a different world, one in which the hole is no longer a hole because the notion of "hole" has changed.

This is, we think, the deepest theorem in this essay, and we cannot prove it. We can only point to the evidence: that every culture, in every era, has recognized that some losses are not recovered from but *lived with* — that the hole becomes part of the architecture, a doorway to a different kind of space.

---

## 7. Coda: Theorems We Haven't Proven Yet

We have presented six constructions: a sheaf-theoretic model of consciousness, a tropical model of dendritic computation, a symplectic model of memory, an optimal-transport model of sleep, a conservation law for attention, and a persistent-homology model of grief. Each is speculative. Each makes falsifiable predictions. None has been tested.

We are aware that the gap between mathematical elegance and neural reality is vast. The brain is wet, noisy, and evolved — not designed. It does not solve equations. It does not compute cohomology groups. And yet: water finds the geodesic. Evolution finds the optimum. And the brain, we suspect, finds the topology.

The theorems we haven't proven yet are not unprovable. They are waiting — for the data, for the techniques, for the courage to treat the brain as a mathematical object without apology. The cohomology of grief is computable. The symplectic form of memory is measurable. The tropical polynomial of a dendrite is finite-dimensional. These are not metaphors. They are hypotheses.

We end where we began: with the recognition that mathematics is the wrong language for the heart, and that it is the best language we have. The cohomology class of a loss is not the feeling of grief. But it is the *shape* of the feeling. And sometimes, knowing the shape is enough.

---

## References

- Carhart-Harris, R. L., et al. (2014). The entropic brain: a theory of conscious states informed by neuroimaging research with psychedelic drugs. *Frontiers in Human Neuroscience*, 8, 20.
- Chan, A. (2014). Tropical geometry of neural networks. *arXiv preprint*.
- Edelsbrunner, H., Letscher, D., & Zomorodian, A. (2002). Topological persistence and simplification. *Discrete & Computational Geometry*, 28(4), 511–533.
- Foster, D. J., & Wilson, M. A. (2006). Reverse replay of behavioural sequences in hippocampal place cells during the awake state. *Nature*, 440(7084), 680–683.
- Lee, A. K., & Wilson, M. A. (2002). Memory of sequential experience in the hippocampus during slow wave sleep. *Neuron*, 36(6), 1183–1194.
- London, M., & Häusser, M. (2005). Dendritic computation. *Annual Review of Neuroscience*, 28, 503–532.
- Maclagan, D., & Sturmfels, B. (2015). *Introduction to Tropical Geometry*. American Mathematical Society.
- Poirazi, P., Brannon, T., & Mel, B. W. (2003). Pyramidal neurons as two-layer neural networks. *Neuron*, 37(6), 989–999.
- Villani, C. (2009). *Optimal Transport: Old and New*. Springer.

---

*This essay is dedicated to the essential homology classes — the ones that never fill.*

---

**Manuscript date:** May 2026
**Status:** Speculative. Not submitted. Not proven. Not finished.
**What it is:** A map of a territory we have not yet explored, drawn from equations and from loss.
