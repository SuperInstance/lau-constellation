# The Tropical Cell: How Living Computation Works

*Speculative Research Essay — May 2026*

---

Biology has no peer reviewers. For four billion years, evolution has been solving optimization problems that would make a mathematician weep—protein folding, morphogenesis, immune recognition, ecological stability—using nothing but chemistry, thermodynamics, and iterative selection on a planet-sized GPU. The algorithms it has discovered are not approximate hacks. They are, I will argue, precise implementations of mathematical structures that mathematicians independently discovered in the last century: tropical geometry, sheaf theory, symplectic mechanics, persistent homology, optimal transport, lattice statistical mechanics, and geometric algebra.

This is not metaphor. A metaphor suggests that biology *resembles* these structures. My claim is stronger: biology *is* these structures, instantiated in carbon. Each section below states a hypothesis and a testable prediction. If the predictions fail, the essay fails with them.

---

## 1. Tropical Gene Expression

### The Hypothesis

The tropical semiring $(\mathbb{R} \cup \{-\infty\}, \oplus, \otimes)$ replaces addition with $\max$ and multiplication with $+$. Tropical polynomials are piecewise-linear functions whose zero sets are polyhedral complexes.

Gene regulatory networks compute in this semiring. Consider a gene $G$ regulated by transcription factors $T_1, \ldots, T_n$, each with binding affinity $a_i$ and concentration $[T_i]$. The expression level of $G$ is:

$$E(G) = \bigoplus_{i=1}^{n} a_i \otimes [T_i] = \max_i (a_i + [T_i])$$

This is a tropical monomial sum. The $\max$ operation is not an approximation—it is the correct model because transcription factor binding is competitive: the strongest bound factor wins the promoter. Cooperative binding is tropical multiplication (affinities add). Repression is tropical subtraction (negation of the coefficient). The full expression landscape of a genome with 20,000 genes is a tropical polynomial in 20,000 variables, and the phenotype is the tropical variety it defines.

Evolution edits the coefficients ($a_i$) through mutation and the variables ($[T_i]$) through regulation. A point mutation that changes a binding site edits one coefficient of one monomial. A gene duplication adds a monomial. A knockout removes one.

### Testable Prediction

If gene expression is tropical, then single-cell RNA-seq data should exhibit piecewise-linear geometry. Specifically, the Pareto front of gene expression states in a differentiating cell population should lie on a tropical hypersurface—a union of affine hyperplanes with rational slopes. This can be tested by fitting piecewise-linear models to single-cell expression data and comparing goodness-of-fit against smooth (non-piecewise-linear) alternatives using Bayesian model selection. The tropical model should win.

A concrete experiment: profile mouse embryonic stem cells differentiating into neural crest over 72 hours using scRNA-seq with ~50,000 cells. Extract the top 50 variable genes. Fit both a tropical polynomial (piecewise-linear with $\max$ structure) and a standard polynomial regression. The tropical model should achieve lower BIC with fewer effective parameters, because the $\max$-structure enforces the correct sparsity.

---

## 2. Sheaf Embryology

### The Hypothesis

A sheaf $(X, \mathcal{F})$ assigns data (stalks) to open sets of a topological space, with restriction maps between them that satisfy gluing conditions. If local sections agree on overlaps, they glue to a global section.

An embryo is a sheaf. The base space is the developing organism as a topological manifold. The stalk at each cell is its gene expression state—a vector in $\mathbb{R}^{20000}$. The restriction maps are signaling pathways: Wnt, Hedgehog, Notch, BMP, FGF. When a cell sends a Wnt signal to its neighbor, it is applying a restriction map—projecting its local section onto the overlap region (the extracellular interface) and transporting it to the neighbor's stalk.

The sheaf condition—that compatible local sections glue to a global section—is the developmental constraint. Neighboring cells with compatible expression states (correct restriction maps) develop into coherent tissue. Birth defects are sheaf cohomology failures: local sections that cannot be glued. $H^1(X, \mathcal{F}) \neq 0$ means the embryo cannot resolve local expression states into a global body plan.

The power of this framing is that it predicts which developmental failures are possible. The cohomology group $H^1$ classifies the inequivalent ways gluing can fail. Different signaling pathway disruptions correspond to different cohomology classes.

### Testable Prediction

Sheaf cohomology predicts that birth defect phenotypes should cluster into discrete equivalence classes corresponding to $H^1$ generators, not form a continuum. Specifically: disruptions to the Notch pathway (lateral inhibition) should produce a different *class* of defect than disruptions to Wnt (anterior-posterior patterning), and double disruptions should produce defects that are *sums* (in the cohomology group) of the individual defects.

This can be tested in zebrafish. Use CRISPR to partially disrupt Notch and Wnt signaling independently and in combination. Quantify the resulting morphological defects using high-resolution imaging and dimensionality reduction (UMAP on morphological features). The prediction: defects will cluster into discrete groups, and combined disruptions will produce morphologies that are additive combinations (in feature space) of the individual disruptions—corresponding to addition in $H^1$. A continuous distribution of defects would falsify the sheaf model.

---

## 3. Symplectic Metabolism

### The Hypothesis

A symplectic manifold $(M, \omega)$ carries a closed, non-degenerate 2-form $\omega$. Hamiltonian flow preserves $\omega$—this is conservation of energy, angular momentum, and all the structured invariants of classical mechanics.

The metabolic network of a healthy cell is a Hamiltonian system. ATP is the symplectic form. More precisely: the phase space is the space of metabolic concentrations $(x_1, \ldots, x_n, p_1, \ldots, p_n)$ where $x_i$ are substrate concentrations and $p_i$ are enzyme activities. The symplectic form is:

$$\omega = \sum_i d(ATP_i) \wedge d(reaction\_flux_i)$$

ATP couples substrates to fluxes the way the canonical symplectic form couples position to momentum. Healthy metabolism preserves $\omega$: every ATP molecule produced is consumed, every reaction flux is balanced, and the total metabolic energy is conserved across the network.

Cancer is symplectic violation. The Warburg effect—anaerobic glycolysis despite oxygen availability—is not merely inefficient. It breaks the symplectic form. Cancer cells produce ATP but do not couple it to balanced fluxes; they dump lactate, breaking the $d(ATP) \wedge d(flux)$ pairing. The symplectic form is no longer closed: $d\omega \neq 0$. Metabolic energy leaks instead of circulating.

### Testable Prediction

If healthy metabolism is symplectic, metabolic flux analysis data should satisfy Hamilton's equations with ATP as the symplectic potential. Concretely: in a healthy cell, the time derivative of any metabolic observable $f$ should satisfy $\dot{f} = \{f, H\}$ where $\{~,~\}$ is the Poisson bracket defined by the ATP-flux symplectic form and $H$ is the total Gibbs free energy. This means metabolic time courses should trace orbits in phase space that are level sets of $H$, and these orbits should be closed loops (Liouville's theorem).

Test: perform continuous metabolic flux analysis on cultured hepatocytes using $^{13}$C tracing over 24 hours, measuring concentrations and fluxes of the top 50 metabolites at 15-minute intervals. Project the trajectory into phase space $(x_i, p_i)$. Healthy cells should trace closed or quasi-periodic orbits. Cancer cells (hepatocellular carcinoma line) should trace non-conservative spirals—phase space volumes should expand (Liouville violation), corresponding to $d\omega \neq 0$.

---

## 4. Persistent Morphology

### The Hypothesis

Persistent homology tracks how topological features (connected components, loops, voids) appear and disappear as a space is filtered—built up through increasing scale or density. The resulting barcode or persistence diagram is a topological summary of shape.

Organ development is a filtration. The limb bud starts as a 0-simplex (a clump of mesenchymal cells, day ~14 in mouse). It extends into a 1-simplex (the arm bud, day ~21). The hand plate forms as branching—new 1-simplices attached to the end. Digits separate as the webbing between them undergoes apoptosis—this is the death of 2-simplices that were filled in during earlier filtration steps.

The Betti numbers of the developing limb track its topological complexity:
- $\beta_0$ (connected components): starts at 1, stays at 1 (the limb is one piece)
- $\beta_1$ (loops): increases when the hand plate forms a paddle (boundary of the paddle is a loop), then decreases when digits separate
- $\beta_2$ (voids): briefly nonzero when the hand plate is a thick 3D paddle

Thalidomide, I hypothesize, kills higher simplices before they form. It prevents the filtration from proceeding past a certain scale. The limb stays at a low-dimensional stage—a stump instead of a branching structure. This is not a chemical insult to specific cells; it is a topological truncation of the developmental filtration.

### Testable Prediction

If thalidomide truncates the filtration, then:
1. The Betti number trajectory of thalidomide-exposed limb buds should plateau at a lower dimension than controls.
2. Earlier exposure should produce lower-dimensional limbs (arm truncation), later exposure should produce higher-dimensional but still truncated limbs (hand truncation, missing fingers).
3. Different teratogens should truncate at different filtration stages—producing a taxonomy of birth defects isomorphic to a taxonomy of filtration truncations.

Test: use light-sheet microscopy to image developing zebrafish fins (analogous to limbs) at 6-hour intervals from bud formation to full fin development, with and without thalidomide exposure. Reconstruct the 3D shape at each time point. Compute persistent homology barcodes at each stage. The prediction is that the control fins show a characteristic barcode sequence (increasing $\beta_1$ during paddle formation, splitting into multiple shorter bars during digit separation), while thalidomide-exposed fins show barcodes that terminate early—the long bars of the control are replaced by short bars that die at the truncation time.

---

## 5. Wasserstein Immunity

### The Hypothesis

Optimal transport theory studies how to move mass from one distribution to another at minimum cost. The Wasserstein distance $W_p(\mu, \nu)$ measures the cheapest way to transform distribution $\mu$ into $\nu$.

The immune system is an optimal transport network. T-cells transport pathogen information (antigen distributions) from tissue to lymph node and, in return, transport effector responses (antibody distributions, cytotoxic T-cell distributions) back. The cost function is biological: it is the metabolic and temporal cost of expanding a clone specific to antigen $a_j$ and deploying it to tissue site $x_i$.

The transport plan $\gamma(i, j)$ is the clone size of T-cells with receptor $j$ deployed to tissue $i$. A healthy immune response minimizes:

$$W_1(\mu_{pathogen}, \nu_{response}) = \min_{\gamma} \sum_{i,j} c(i,j) \gamma(i,j)$$

where $\mu_{pathogen}$ is the spatial antigen distribution and $\nu_{response}$ is the immune effector distribution.

Autoimmune disease is friendly fire: the transport plan $\gamma$ has significant mass on pairs $(i, j)$ where antigen $j$ is self. The optimal transport is computing the correct map but the cost function is wrong—it assigns low cost to attacking self. Long COVID is a transport bottleneck: the pathogen distribution $\mu$ is too complex (too many antigen variants across too many tissues) for the available T-cell repertoire to transport efficiently. The Wasserstein distance between $\mu$ and the achievable $\nu$ is large, and the immune system gets stuck trying to close the gap, producing chronic inflammation.

### Testable Prediction

If autoimmune disease is a cost function error, then:
1. Autoimmune-prone individuals (e.g., lupus, type 1 diabetes) should have T-cell repertoires whose Wasserstein distance to self-antigen distributions is anomalously low—meaning the transport plan finds it "cheap" to target self.
2. Correcting the cost function should ameliorate autoimmunity. This is what immune checkpoint inhibitors do (in reverse—they increase the cost of self-attack for cancer patients who need reduced self-tolerance).

Test: perform TCR sequencing on matched blood and tissue samples from lupus patients and controls. Compute the Wasserstein-1 distance between the TCR repertoire distribution and the self-peptide-MHC presentation profile (measured by mass spectrometry immunopeptidomics). Lupus patients should show significantly lower $W_1$ to self-antigens—meaning their transport plan has lower cost for self-targeting. This can be validated prospectively: patients with lower $W_1$ to self should have more severe flares.

---

## 6. Lattice Protein Folding

### The Hypothesis

The Ising model on a lattice has spins $\sigma_i \in \{-1, +1\}$ with energy $E = -J \sum_{\langle i,j \rangle} \sigma_i \sigma_j - h \sum_i \sigma_i$. The Potts model generalizes to $q$ states. Phase transitions occur as temperature crosses critical thresholds.

A protein is an Ising/Potts model on a residue lattice. Each residue $i$ occupies a lattice site with conformational state $\sigma_i \in \{1, \ldots, q\}$ where $q$ is the number of Ramachandran-accessible states (roughly 3: $\alpha$-helix, $\beta$-sheet, coil). The interaction $J_{ij}$ between residues $i$ and $j$ depends on their amino acid types and spatial proximity. Folding is the system finding its ground state.

This is not a new idea—lattice protein models date to Dill (1985). The novel claim: prions are metastable Potts states in the wrong phase. A prion is a protein that has two stable conformations (native and scrapie). In the Potts model language, the native state is the global ground state at physiological temperature, and the scrapie form is a metastable local minimum that becomes the ground state at a different temperature or in the presence of a seed. The seed is a domain wall in the Potts lattice—it nucleates a phase transition from the native phase to the scrapie phase.

The phase transition is first-order: a critical nucleus of scrapie conformation must form before the rest of the protein flips. This is why prion diseases have long incubation periods (the nucleus must reach critical size) and why they propagate by seeding (the nucleus provides the critical domain wall).

### Testable Prediction

If prion conversion is a Potts phase transition, then:
1. The energy barrier between native and scrapie states should scale as $\sigma^{d-1}$ where $\sigma$ is the surface tension between the two phases and $d$ is the effective dimensionality of the protein's contact map. This is classical nucleation theory.
2. Mutations that cause familial prion diseases should lower the surface tension $\sigma$, reducing the critical nucleus size and hence the incubation period.
3. Anti-prion drugs should act as Potts impurities—pinning sites that raise the barrier to phase transition.

Test: perform molecular dynamics simulations of prion protein (PrP) folding using a coarse-grained Potts model parameterized by experimental contact maps. Compute the free energy barrier between native and scrapie states as a function of nucleus size. Fit to classical nucleation theory to extract $\sigma$ and $d$. Then test known pathogenic mutations (E200K, D178N, P102L) and predict that each lowers $\sigma$ by a quantifiable amount, proportional to the known reduction in incubation period. Validate against incubation time data from transgenic mouse models.

---

## 7. Geometric Ecology

### The Hypothesis

Conformal geometric algebra $\text{Cl}(n, 0)$ provides a unified language for rotations, reflections, and translations in $n$ dimensions. Multivectors are sums of scalars, vectors, bivectors (plane elements), trivectors (volume elements), and higher. Rotors are exponentials of bivectors and represent rotations. Reflections are implemented by grade-1 vectors.

An ecosystem of $n$ species has dynamics expressible in $\text{Cl}(n, 0)$. Each species is a basis vector $e_i$. Predator-prey interactions are bivectors $e_i \wedge e_j$—rotational dynamics in the $(i, j)$ plane. The Lotka-Volterra equations:

$$\dot{x}_i = x_i(a_i - \sum_j b_{ij} x_j)$$

are, in the geometric algebra, the equation:

$$\dot{X} = X \cdot B$$

where $X = \sum_i x_i e_i$ is the population multivector and $B = \sum_{i<j} b_{ij} (e_i \wedge e_j)$ is the interaction bivector. The dot product with $B$ generates rotations in the $(i, j)$ plane for each predator-prey pair—exactly the oscillatory dynamics observed in nature (lynx-hare cycles).

Symbiosis is a rotor: two species co-rotate, their population vectors rotating *together* rather than against each other. The symbiosis rotor $R = e^{+\theta_{ij} (e_i \wedge e_j)}$ generates correlated growth. Parasitism is a reflection: the parasite reflects the host's growth vector, producing anti-correlated dynamics where host gain is parasite's opportunity. The full food web is a multivector in $\text{Cl}(n, 0)$, and ecosystem stability corresponds to the condition that the total interaction multivector has no growing exponentials—i.e., the food web is a rotational system with bounded orbits.

### Testable Prediction

If ecosystem dynamics live in geometric algebra, then:
1. Predator-prey pairs should trace elliptical orbits in phase space—exactly the rotor prediction. This is already known (Lotka-Volterra produces periodic orbits).
2. The novel prediction: adding a third species interacting with both should produce dynamics that are the geometric product of the two pairwise rotors. The geometric product $R_{12} R_{23}$ contains not only the pairwise rotations but a scalar term (correlated growth of species 1 and 3) and a trivector term (three-body interaction). The trivector term predicts a specific three-body oscillation that is not the sum of pairwise oscillations.
3. Ecosystems with high biodiversity should be more stable because higher-grade multivectors (trivectors, $k$-vectors) provide more rotational degrees of freedom to absorb perturbations.

Test: analyze long-term ecological time series from the Hubbell plot at Barro Colorado Island (25 ha, >300 species, 40+ years of census data). Extract population trajectories for trios of interacting species. Compute the trivector component of their joint dynamics: $\langle e_i \wedge e_j \wedge e_k \rangle$. The prediction is that this trivector is non-zero and oscillatory with a frequency distinct from any pairwise frequency. This three-body oscillation should be detectable via spectral analysis of the triad's joint trajectory. Its absence would indicate that pairwise models suffice (falsifying the GA prediction) or that the trivector is negligible at ecological timescales.

---

## Coda: Why This Matters

These seven hypotheses share a structural claim: biology is not *analogous* to advanced mathematics—it *is* advanced mathematics, running on wetware. The reason evolution converges on these structures is that they are the correct solutions to the problems life faces. Tropical geometry is the right algebra for competitive regulation. Sheaf theory is the right framework for local-to-global consistency. Symplectic mechanics is the right language for constrained optimization. Persistent homology is the right tool for tracking topological change. Optimal transport is the right framework for resource allocation. Statistical mechanics on lattices is the right model for cooperative folding. Geometric algebra is the right language for multi-body rotational dynamics.

None of this required a mathematician. Evolution discovered tropical polynomials three billion years before Einsiedler, Kapranov, and Lind. It discovered sheaf cohomology before Leray. It discovered symplectic forms before Lagrange. It discovered persistent homology before Edelsbrunner and Harer. It discovered optimal transport before Monge and Kantorovich. It discovered the Ising model before Ising.

Mathematics is not a human invention applied to nature. It is nature's operating system, and we are finally learning to read the source code.

---

*Each prediction in this essay is falsifiable. I hope some of them are wrong—that is how we learn. But I suspect many are right, and that the next decade of biology will be the decade of mathematical structure.*

---

**Acknowledgments**: This essay draws on ideas from tropical geometry (Maclagan & Sturmfels), sheaf theory (Kashiwara & Schapira), symplectic topology (Arnol'd), persistent homology (Edelsbrunner & Harer), optimal transport (Villani), lattice models (Baxter), and geometric algebra (Dorst, Fontijne & Mann). The synthesis—and any errors—is my own.
