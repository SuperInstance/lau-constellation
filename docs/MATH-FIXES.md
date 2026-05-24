# Mathematical Fixes for CONSERVATION-OF-TENSION.md

**Author:** Technical review and correction — May 2026  
**Status:** Addresses the two Critical issues and one High-priority issue from Appendix A.7

---

## Overview

This document provides:

1. **Fix 1 (Critical — §A.2):** A rigorous treatment of the conservation law, replacing the tautological proof sketch with a proper constrained-optimization framework and formal demotion to a testable hypothesis with falsification criteria.

2. **Fix 2 (Critical — §A.3):** Replacement of the Gabor/Heisenberg argument with the Hirschman entropic uncertainty principle (the correct tool), plus a precise explanation of why the category error in Section 5 cannot be rescued by informal analogy.

3. **Fix 3 (High — §A.5):** Computation of the PCA intrinsic dimension of the meantone and ET consonance fields from the tuning_information.py data, replacing the hand-waving dimensionality argument in Section 7 with numerical results and interpretation.

---

## Fix 1: The Conservation Law — Proof, Hypothesis, and Falsification

### 1.1 What the Current Proof Actually Shows

Section 4.3 ("Proof Sketch: Conservation Under the Information Bottleneck") presents the following argument:

1. Invoke Shannon's channel coding theorem to assert $I_{\text{vert}} + I_{\text{horiz}} \leq \mathcal{C}$.
2. Hypothesize that music operates near capacity: $I_{\text{vert}} + I_{\text{horiz}} \approx \mathcal{C}$.
3. Prove Lemma 4.1: if $E = f(I_{\text{vert}}, I_{\text{horiz}})$ is monotone in both arguments and $E$ is held constant, then $I_{\text{vert}}$ and $I_{\text{horiz}}$ trade off.

**What step (1) actually requires and does not have:** Shannon's theorem requires a *defined channel* — an input alphabet $\mathcal{X}$, output alphabet $\mathcal{Y}$, and conditional distribution $p(y|x)$ representing noise. The paper never specifies what the channel is, what constitutes noise, or what counts as a symbol. Without these, the invocation of $\mathcal{C} = \max_{p(x)} I(X;Y)$ is vacuous.

**What Lemma 4.1 actually proves:** A tautology. If $E$ is nondecreasing in both $I_{\text{vert}}$ and $I_{\text{horiz}}$, and if $E$ is held constant, then decreasing one component must be compensated by increasing the other. This is true for *any* function of two variables and says nothing about whether $E$ is in fact held constant — which is the substantive claim.

**Conclusion:** Section 4.3 establishes only that *if* total expressive content is conserved, *then* the two components trade off. It provides no evidence that the antecedent holds.

---

### 1.2 What a Real Proof Would Require

A rigorous proof of $I_{\text{vert}} + I_{\text{horiz}} \approx T_0$ must establish one of the following:

#### Option A: Constrained Optimization

**Setup.** Model a composer as an agent who maximizes expressive content $E$ subject to a cognitive complexity budget:

$$\max_{I_{\text{vert}},\, I_{\text{horiz}} \geq 0} \; f(I_{\text{vert}}, I_{\text{horiz}}) \quad \text{subject to} \quad g(I_{\text{vert}}, I_{\text{horiz}}) \leq C$$

where:
- $f: \mathbb{R}_{\geq 0}^2 \to \mathbb{R}$ is a utility function (monotone increasing in both arguments, $\partial f / \partial I > 0$)
- $g: \mathbb{R}_{\geq 0}^2 \to \mathbb{R}_{\geq 0}$ is a complexity cost function
- $C > 0$ is the audience's cognitive capacity (a constant for a given cultural moment)

**Claim.** If the constraint is tight (the optimizer operates at $g = C$), and $g$ is additively separable:

$$g(I_{\text{vert}}, I_{\text{horiz}}) = I_{\text{vert}} + I_{\text{horiz}}$$

then any constrained optimum satisfies:

$$I_{\text{vert}} + I_{\text{horiz}} = C$$

**Proof.** On the constraint surface $\{(I_{\text{vert}}, I_{\text{horiz}}) : I_{\text{vert}} + I_{\text{horiz}} = C\}$, the feasible perturbations satisfy $\delta I_{\text{vert}} + \delta I_{\text{horiz}} = 0$, so $\delta I_{\text{horiz}} = -\delta I_{\text{vert}}$. This is the conservation law. The perturbation ratio is:
$$\frac{dI_{\text{horiz}}}{dI_{\text{vert}}}\bigg|_{\text{constraint}} = -1$$
giving exact compensation of any change in $I_{\text{vert}}$ by an equal and opposite change in $I_{\text{horiz}}$. $\square$

**Where the assumptions enter:**

| Assumption | Justification | Status |
|------------|---------------|--------|
| $g = I_{\text{vert}} + I_{\text{horiz}}$ | Pitch and rhythm are independently processed channels; by Shannon, total information from independent sources adds | Approximately valid; experimental support from dual-task cognitive interference studies |
| Constraint is tight ($g = C$, not $< C$) | Music cultures exploit available complexity to the maximum | Empirically plausible but not proved; requires a selection argument (e.g., cultures that under-exploit complexity are driven to greater complexity by competition) |
| $C$ is constant across tuning systems | Audience cognitive capacity is set by neural architecture, not musical conventions | Reasonable on century timescales; $C$ may shift slowly (cultural complexification hypothesis) |
| $f$ is monotone increasing | More information = more expressive; no saturation | Valid locally; at very high complexity, cognitive overload may decrease engagement |

**Critical gap.** The additive separability $g = I_{\text{vert}} + I_{\text{horiz}}$ requires that the two information channels are statistically independent — that the pitch structures and rhythmic structures are generated by independent processes. This is approximately true in Western notation (the time signature and the key signature are set independently), but breaks down when rhythmic patterns are designed to reinforce or contradict harmonic patterns (a common compositional technique). The paper should acknowledge this dependency.

**Partial result (without independence).** If $g$ is strictly convex but not necessarily additive, then the Lagrangian conditions at the constrained optimum give:

$$\frac{\partial f / \partial I_{\text{vert}}}{\partial f / \partial I_{\text{horiz}}} = \frac{\partial g / \partial I_{\text{vert}}}{\partial g / \partial I_{\text{horiz}}}$$

This determines the *ratio* of the components but not their sum. Conservation (exact trade-off with unit coefficient) follows only when $g$ is linear (additive). For other cost functions, the trade-off is monotone but not 1:1.

---

#### Option B: Game-Theoretic Derivation

Model the composer-listener pair as a signaling game. The composer chooses a signal $(I_{\text{vert}}, I_{\text{horiz}})$ to encode expressive intent $\theta \in \Theta$. The listener decodes. In a separating equilibrium (Perfect Bayesian Equilibrium where different $\theta$ map to different signals), the total signaling load is bounded by the listener's decoding bandwidth.

This framework yields a conservation-like result when:
1. The equilibrium is on the Pareto frontier of the complexity-expressive-content tradeoff
2. The listener's bandwidth constraint binds

Neither condition is proved; both require empirical support.

---

#### Option C: Honest Empirical Hypothesis (Recommended)

The most mathematically honest presentation demotes Theorem 8.1 to a hypothesis with explicit falsification criteria. This is Option C from Appendix A.2, made fully precise here.

**Hypothesis 8.1' (Conservation of Musical Tension — Formal Statement).**

*Define the following measurable quantities for a musical corpus $\mathcal{D}$ from historical era $t$:*

**(a) Vertical information:**
$$I_{\text{vert}}(t) \;=\; \log_2 12 - H(\mathcal{K}_t) \;=\; D_{\text{KL}}\!\left(P_{\text{uniform}} \;\|\; P_{\mathcal{K}_t}\right)$$
*where $P_{\mathcal{K}_t}$ is the empirical key-usage distribution in $\mathcal{D}$ and $D_{\text{KL}}$ is the Kullback-Leibler divergence from uniform.*

**(b) Horizontal information:**
$$I_{\text{horiz}}(t) \;=\; H_{\text{onset}}(t) \;=\; -\!\sum_{\mathbf{r} \in \{0,1\}^{16}} \hat{Q}_t(\mathbf{r}) \log_2 \hat{Q}_t(\mathbf{r})$$
*where $\hat{Q}_t(\mathbf{r})$ is the empirical distribution of 16th-note onset patterns in 4/4 measures.*

*The hypothesis asserts: there exists a constant $T_0$ (depending on the musical tradition but not on the tuning system) and a slowly-varying perturbation $\epsilon(t)$ such that:*
$$I_{\text{vert}}(t) + I_{\text{horiz}}(t) = T_0 + \epsilon(t)$$
*where "slowly-varying" is defined as $|\dot{\epsilon}(t)| \ll |\dot{I}_{\text{vert}}(t)|$ — i.e., the residual changes much more slowly than the tuning-induced changes.*

**Falsification criteria.** The hypothesis is **falsified** if any of the following hold in a corpus study:

1. $\frac{d}{dt}[I_{\text{vert}}(t) + I_{\text{horiz}}(t)]$ is significantly positive during the meantone-to-ET transition (i.e., total information *increases* rather than staying constant), with $p < 0.01$ by bootstrap.
2. $I_{\text{vert}}(t)$ and $I_{\text{horiz}}(t)$ are both decreasing during the ET transition (failing even monotone compensation).
3. The cross-correlation between $I_{\text{vert}}(t)$ and $I_{\text{horiz}}(t)$ is positive (they move together, not in opposition), suggesting a shared driver rather than a trade-off.

The hypothesis is **corroborated** if:
- $\text{Corr}(I_{\text{vert}}(t),\; I_{\text{horiz}}(t)) < -0.7$ over the 1600–2000 window
- $\text{Var}[I_{\text{vert}}(t) + I_{\text{horiz}}(t)] < \text{Var}[I_{\text{vert}}(t)] + \text{Var}[I_{\text{horiz}}(t)]$ (the sum is more stable than either component)

---

### 1.3 Required Revision to the Paper

**Section 4.3** should be retitled "A Framework for Testing the Conservation Hypothesis" and restructured as:

1. **Definitions** (Sections 4.1–4.2, largely intact): Define $I_{\text{vert}}$ and $I_{\text{horiz}}$ as measurable information-theoretic quantities.

2. **Optimization interpretation** (Option A above): Show that *if* composers are utility-maximizing agents facing a cognitive load constraint, *and if* the constraint is linear and tight, *then* the conservation law follows as a theorem of constrained optimization. State all four assumptions explicitly.

3. **Empirical hypothesis** (Hypothesis 8.1'): Demote the conservation claim itself from "theorem" to "hypothesis" with the falsification criteria above.

4. **Current evidence**: The numerical estimates in Section 4.4 (0.44 bits vertical, 11 additional syncopation events) constitute *order-of-magnitude consistency* between the hypothesis and the qualitative historical record, not a proof.

**Theorem 8.1** should become **Hypothesis 8.1'** throughout.

---

## Fix 2: Replacing the Gabor/Heisenberg Argument with Hirschman

### 2.1 The Category Error, Made Precise

The original paper (Section 5, Theorem 5.1–5.3) uses the Gabor/Heisenberg limit:
$$\sigma_t \cdot \sigma_\omega \geq \frac{1}{2}$$
where $\sigma_t$ is the temporal spread of a signal $s(t)$ and $\sigma_\omega$ is its spectral spread, to argue that reducing $\sigma_\omega$ (key-color variation in ET) forces $\sigma_t$ (rhythmic complexity) to increase.

**The category error:** The $\sigma_\omega$ in Definition 5.1 is:
$$\sigma_\omega(\mathcal{T}) = \sqrt{\frac{1}{12}\sum_{i=1}^{12}\left(\bar{C}(K_i) - \bar{C}\right)^2}$$
This is the standard deviation of the *consonance function* evaluated at 12 keys — a statistic over a discrete 12-element set of a derived functional. It has units of [consonance score] (dimensionless, bounded in $[0,1]$).

The $\sigma_\omega$ in the Gabor limit is:
$$\sigma_\omega = \sqrt{\int \omega^2 |\hat{s}(\omega)|^2 d\omega - \left(\int \omega |\hat{s}(\omega)|^2 d\omega\right)^2}$$
This is the standard deviation of the *spectral energy density* of a signal. It has units of [rad/s].

**These are different mathematical objects:**
- One is a variance over a 12-element discrete set of a functional computed from acoustics
- The other is the second moment of the probability distribution $|\hat{s}(\omega)|^2$ on $\mathbb{R}$

The product $\sigma_t \cdot \sigma_\omega$ in the Gabor limit is dimensionless (seconds × rad/s = 1) and bounded below by 1/2. The product $\sigma_t \cdot \sigma_\omega(\mathcal{T})$ where $\sigma_\omega(\mathcal{T})$ is Definition 5.1's quantity has units of seconds (or whatever $\sigma_t$'s units are) and has no known lower bound.

**The argument cannot be rescued by informal analogy.** The claim in Section 5.3 that "this is not merely an analogy to quantum mechanics — it is the same mathematics" is precisely what is false. The mathematical objects are different, so the mathematical theorem does not transfer.

---

### 2.2 The Hirschman Entropic Uncertainty Principle

The correct information-theoretic uncertainty principle for $L^2$ functions is due to Hirschman (1957), sharpened to a tight bound by Babenko (1961) and Beckner (1975).

**Theorem (Hirschman-Białynicki-Birula-Mycielski).** Let $f \in L^2(\mathbb{R})$ with $\|f\|_2 = 1$. Use the unitary Fourier transform:
$$\hat{f}(\omega) = \frac{1}{\sqrt{2\pi}} \int_{-\infty}^{\infty} f(t)\, e^{-i\omega t}\, dt$$
so that $\|\hat{f}\|_2 = 1$ by Parseval. Define the differential entropy of the probability densities $p_t(t) = |f(t)|^2$ and $p_\omega(\omega) = |\hat{f}(\omega)|^2$:
$$H_t = -\int_\mathbb{R} |f(t)|^2 \log_2 |f(t)|^2\, dt, \qquad H_\omega = -\int_\mathbb{R} |\hat{f}(\omega)|^2 \log_2 |\hat{f}(\omega)|^2\, d\omega$$
Then:
$$\boxed{H_t + H_\omega \geq \log_2(\pi e) \approx 2.254 \text{ bits}}$$
with equality if and only if $f$ is a Gaussian $f(t) \propto e^{-t^2/(4\sigma^2)}$ for some $\sigma > 0$.

**Proof sketch.** The proof proceeds via the Hausdorff-Young inequality with optimal (Beckner) constants. For $p \in [1,2]$ and $q = p/(p-1)$ the conjugate exponent, the Hausdorff-Young inequality with Beckner's sharp constant $B_p = (p^{1/p}/q^{1/q})^{1/2}$ states:
$$\|\hat{f}\|_q \leq B_p \|f\|_p$$
with equality for Gaussians. Taking the logarithm and differentiating with respect to $p$ at $p=1$ produces the entropy inequality. The Gaussian achieves equality because it simultaneously minimizes both $H_t$ and $H_\omega$ over all distributions with the same variance product $\sigma_t^2 \sigma_\omega^2 = 1/4$. Full proof: Beckner (1975), *Ann. Math.* 102:159–182. $\square$

**Relation to Heisenberg.** The HBBM inequality implies the Heisenberg uncertainty: by the maximum-entropy property of Gaussians, $H_t \leq \frac{1}{2}\log_2(2\pi e \sigma_t^2)$ with equality for Gaussian $p_t$. Therefore:
$$\log_2(\pi e) \leq H_t + H_\omega \leq \frac{1}{2}\log_2(2\pi e \sigma_t^2) + \frac{1}{2}\log_2(2\pi e \sigma_\omega^2)$$
The right side equals $\log_2(2\pi e \sigma_t \sigma_\omega)$, which is bounded below by $\log_2(2\pi e \cdot 1/2) = \log_2(\pi e)$ when $\sigma_t \sigma_\omega = 1/2$. So HBBM is *stronger* than Heisenberg: entropy uncertainty is a sharper constraint than variance uncertainty.

---

### 2.3 What the Hirschman Bound Actually Says About Music

The HBBM inequality applies to a musical signal $s(t) \in L^2(\mathbb{R})$, where:
- $|s(t)|^2$ is the instantaneous power (related to rhythmic density and dynamic envelope)
- $|\hat{s}(\omega)|^2$ is the power spectrum (related to harmonic content, timbre, and tuning)

**Legitimate application:** For a fixed musical signal $s(t)$:

> If the harmonic spectrum is spectrally concentrated (few distinct pitch classes, all with similar energy) — i.e., $H_\omega$ is small — then the temporal envelope cannot also be concentrated: $H_t \geq \log_2(\pi e) - H_\omega$. A spectrally concentrated signal must be temporally spread.

This is a genuine mathematical result. For music, it means: a piece that uses only one pitch (or a narrow band of pitches) must occupy a large amount of time to carry any information. This is trivially true and says nothing specific about the meantone-to-ET transition.

**What the Hirschman bound does NOT say:**

It does not say that reducing the *variance of consonance across keys* ($V_\mathcal{K}$ of Definition 7.3') forces *rhythmic onset entropy* to increase. These are different quantities from $H_\omega$ (spectral entropy of the acoustic signal):

| Quantity | Mathematical object | What it measures |
|----------|---------------------|------------------|
| $\sigma_\omega(\mathcal{T})$ (Definition 5.1) | Std. dev. of consonance scores over $\mathbb{Z}_{12}$ | Key-color variation in a tuning system |
| $H_\omega(s)$ (HBBM) | Differential entropy of $\|\hat{s}\|^2$ over $\mathbb{R}$ | Spectral spread of a specific acoustic signal |
| $H_{\text{onset}}$ (Definition 4.2) | Shannon entropy of onset pattern distribution | Rhythmic complexity of a corpus |

The HBBM inequality connects $H_\omega(s)$ (spectral entropy of a signal) to $H_t(s)$ (temporal entropy of the same signal), not to $\sigma_\omega(\mathcal{T})$ or $H_{\text{onset}}$.

---

### 2.4 A Correct Uncertainty-Type Statement for the Musical Context

The following proposition is rigorous and captures the spirit of the paper's Section 5 argument, without the category error.

**Proposition (Discrete Entropic Uncertainty for Key-Space and Onset-Space).**

Let $\mathbf{x} \in \mathbb{C}^{12}$ be a complex vector representing the distribution of key-weighted consonance over the 12 pitch classes, normalized so $\|\mathbf{x}\|_2 = 1$. Let $\hat{\mathbf{x}} = F\mathbf{x}$ be its discrete Fourier transform, where $F$ is the $12 \times 12$ DFT matrix ($F_{jk} = \omega^{jk}/\sqrt{12}$, $\omega = e^{2\pi i/12}$). Define:
$$H_K(\mathbf{x}) = -\sum_{j=0}^{11} |x_j|^2 \log_2 |x_j|^2, \qquad H_{\hat{K}}(\mathbf{x}) = -\sum_{k=0}^{11} |\hat{x}_k|^2 \log_2 |\hat{x}_k|^2$$

**Lemma (Donoho-Stark, discrete version).** If $|\text{supp}(\mathbf{x})| = s$ (number of nonzero key-weights) and $|\text{supp}(\hat{\mathbf{x}})| = \hat{s}$, then $s \cdot \hat{s} \geq 12$.

**Corollary (Entropic form).** By the maximum-entropy bound for distributions on $k$ atoms: $H \leq \log_2 k$, so:
$$H_K(\mathbf{x}) + H_{\hat{K}}(\mathbf{x}) \geq \log_2 12 \approx 3.585 \text{ bits}$$
with equality when $\mathbf{x}$ is the uniform vector (all keys equally weighted, i.e., equal temperament).

**Proof.** For $\mathbf{x}$ uniform: $x_j = 1/\sqrt{12}$ for all $j$, so $|x_j|^2 = 1/12$ and $H_K = \log_2 12$. The DFT of the uniform vector is the delta function: $\hat{x}_k = \delta_{k,0}$, so $H_{\hat{K}} = 0$. Sum = $\log_2 12$. For a non-uniform $\mathbf{x}$: $H_K < \log_2 12$ (Shannon entropy is maximized at uniformity), but $\hat{\mathbf{x}}$ is more spread (the DFT of a peaked function is spread out), so $H_{\hat{K}} > 0$. The lower bound $H_K + H_{\hat{K}} \geq \log_2 12$ follows from the Maassen-Uffink inequality for the DFT. $\square$

**Musical interpretation.** In ET, the key-weight distribution $\mathbf{x}$ is uniform: $H_K = \log_2 12 = 3.585$ bits and $H_{\hat{K}} = 0$. In meantone, $\mathbf{x}$ is non-uniform (C major strongly preferred, F♯/G♭ rarely used): $H_K < 3.585$ bits and $H_{\hat{K}} > 0$. The sum stays $\geq \log_2 12$.

**What this proves and what it doesn't:**
- ✓ Proves: ET achieves the maximum $H_K = \log_2 12$ (key-choice entropy is maximized at equal temperament)
- ✓ Proves: Meantone's non-uniform key usage means its "key-space DFT" has non-trivial structure  
- ✗ Does NOT prove: That $H_K + H_{\hat{K}}$ is conserved across eras (the bound is a lower bound, not an equality)
- ✗ Does NOT connect $H_{\hat{K}}$ to rhythmic complexity $H_{\text{onset}}$ — these are different quantities

---

### 2.5 The Right Framework: Information Allocation, Not Uncertainty

The uncertainty principle provides a lower bound on joint entropy. The conservation law claims approximate constancy of a sum. These require different mathematical tools:

| Claim type | Mathematical tool | Status in paper |
|------------|------------------|-----------------|
| Lower bound on $H_t + H_\omega$ | Hirschman inequality | Correct, but proves less than claimed |
| Upper bound on $I_{\text{vert}} + I_{\text{horiz}}$ | Cognitive capacity / channel capacity | Requires empirical grounding |
| Conservation $I_{\text{vert}} + I_{\text{horiz}} \approx C$ | Constrained optimization (Fix 1) OR empirical hypothesis (Hypothesis 8.1') | The paper must choose one |

**Recommended Section 5 replacement:**

> **Proposition 5.1' (Hirschman Bound for Musical Signals).** *For any acoustic musical signal $s(t) \in L^2(\mathbb{R})$ with unit norm, the spectral entropy $H_\omega$ and temporal entropy $H_t$ satisfy $H_t + H_\omega \geq \log_2(\pi e) \approx 2.254$ bits. In ET, the power spectrum $|\hat{s}(\omega)|^2$ is more uniform across pitch classes than in meantone (because all intervals are equally tempered), so $H_\omega^{\text{ET}} \geq H_\omega^{\text{meantone}}$. The Hirschman bound implies $H_t^{\text{ET}} \geq \log_2(\pi e) - H_\omega^{\text{ET}}$, but since $H_\omega^{\text{ET}}$ is larger, the lower bound on $H_t$ is actually looser (smaller). The Hirschman inequality therefore does not compel greater temporal complexity in ET — it is consistent with both more and less rhythmic complexity.*

> *The correct framework for the conservation claim is the constrained-optimization model of Section 4 (Option A above), or, failing a proof of the capacity-saturation assumption, the empirical hypothesis of Hypothesis 8.1'.*

---

## Fix 3: PCA Intrinsic Dimension of the Consonance Field

### 3.1 Setup and Feature Extraction

Following Proposition 7.1'' from Appendix A.5, we represent each of the 12 major keys as a feature vector of diatonic consonance scores. For each key $K_i \in \mathcal{K}$, we define:

$$\mathbf{x}_{K_i} = \left(C_{\text{uni}}(K_i),\; C_{\text{M2}}(K_i),\; C_{\text{M3}}(K_i),\; C_{\text{P4}}(K_i),\; C_{\text{P5}}(K_i),\; C_{\text{M6}}(K_i),\; C_{\text{M7}}(K_i)\right) \in \mathbb{R}^7$$

where $C_{\text{deg}}(K_i)$ is the consonance score of the nearest available meantone interval to degree `deg` above key $K_i$. Consonance scores use the Tenney-height exponential: $C(p/q) = e^{-\frac{1}{2}(\log_2 p + \log_2 q)}$ for $p/q$ in lowest terms.

**Computation.** Quarter-comma meantone assigns pitch classes via $n$ fifths from C:
$$\text{cents}(K) = \left(n_K \cdot \left(701.955 - \frac{21.506}{4}\right)\right) \bmod 1200 = \left(n_K \cdot 696.578\right) \bmod 1200$$

where $n_K$ is the number of fifths from C to key $K$ on the circle of fifths. The syntonic comma is $81/80 \approx 21.506$ cents.

### 3.2 The 12×7 Feature Matrices

**Table 1: Meantone quarter-comma consonance features (from tuning_information.py data)**

| Key | Unison | Maj2 | **Maj3** | Perf4 | Perf5 | **Maj6** | Maj7 |
|-----|--------|------|----------|-------|-------|----------|------|
| C   | 1.0000 | 0.0155 | **0.1152** | 0.0021 | 0.0019 | 0.0017 | 0.0017 |
| G   | 1.0000 | 0.0155 | **0.1152** | 0.0021 | 0.0019 | 0.0017 | 0.0017 |
| D   | 1.0000 | 0.0155 | **0.1152** | 0.0021 | 0.0019 | 0.0017 | 0.0017 |
| A   | 1.0000 | 0.0155 | **0.1152** | 0.0021 | 0.0019 | 0.0017 | 0.0022 |
| E   | 1.0000 | 0.0155 | **0.0026** | 0.0021 | 0.0019 | 0.0017 | 0.0037 |
| B   | 1.0000 | 0.0155 | **0.0081** | 0.0021 | 0.0019 | **0.0699** | 0.0037 |
| F♯  | 1.0000 | 0.0028 | **0.0081** | 0.0021 | 0.0019 | 0.0019 | 0.0037 |
| C♯  | 1.0000 | 0.0024 | **0.0081** | 0.0021 | 0.0022 | 0.0019 | 0.0037 |
| G♭  | 1.0000 | 0.0025 | **0.1152** | 0.0030 | 0.0019 | 0.0017 | 0.0017 |
| E♭  | 1.0000 | 0.0155 | **0.1152** | 0.0020 | 0.0019 | 0.0017 | 0.0017 |
| B♭  | 1.0000 | 0.0155 | **0.1152** | 0.0021 | 0.0019 | 0.0017 | 0.0017 |
| F   | 1.0000 | 0.0155 | **0.1152** | 0.0021 | 0.0019 | 0.0017 | 0.0017 |

**Table 2: Equal temperament (all rows identical)**

| Key | Unison | Maj2 | Maj3 | Perf4 | Perf5 | Maj6 | Maj7 |
|-----|--------|------|------|-------|-------|------|------|
| any | 1.0000 | 0.0034 | 0.0030 | 0.1665 | 0.2746 | 0.0080 | 0.0016 |

**Note on ET values:** The ET intervals use exact DFT-uniform tuning (100¢ per semitone). The consonance scores are computed via nearest simple ratio: P4 → 4/3 (score 0.1665), P5 → 3/2 (score 0.2746). These are substantially higher than in the meantone column because the ET P4/P5 are closer to simple ratios than meantone's version at those degrees (meantone's P4/P5 are computed as the nearest available note to the target, which often has a large denominator in the simple-ratio approximation).

**Modeling caveat:** The consonance scores for meantone intervals are computed by finding the nearest meantone note to each scale degree target, then computing the consonance of the actual interval. This introduces artifacts when the nearest note has a large-denominator simple ratio (e.g., G at 696.578¢ finds 91/61 ≈ 692.4¢ as a better-fitting ratio than 3/2 ≈ 701.955¢, giving spuriously low consonance). A more acoustically correct method would use the just ratio being approximated (3/2 for the meantone fifth) with a small detuning penalty. However, this artifact is consistent across all keys in Table 1 (since the Perf5 column is uniform at 0.0019), so it does not affect the variance structure used for PCA.

### 3.3 PCA Results

**Per-degree variance in meantone:**

| Degree | Variance | % of Total |
|--------|----------|------------|
| Unison | 0.000000 | 0.00% |
| Maj2   | 0.000034 | 1.05% |
| **Maj3** | **0.002857** | **87.12%** |
| Perf4  | 0.000000 | 0.01% |
| Perf5  | 0.000000 | 0.00% |
| **Maj6** | **0.000387** | **11.80%** |
| Maj7   | 0.000001 | 0.03% |
| **Total** | **0.003279** | **100.00%** |

**Eigendecomposition of the 7×7 covariance matrix:**

| PC | Eigenvalue | Variance Explained | Cumulative | Primary loading |
|----|------------|-------------------|------------|-----------------|
| PC1 | 0.002939 | 89.64% | 89.64% | Maj3 (key-color axis) |
| **PC2** | **0.000316** | **9.63%** | **99.28%** ← 95% threshold | Maj6 (B-key outlier) |
| PC3 | 0.000024 | 0.72% | 100.00% | Maj2 residual |
| PC4–7 | ≈0 | ≈0.00% | 100.00% | — |

**Intrinsic dimension:**

$$d_{\text{int}}(\text{quarter-comma meantone}) = 2 \qquad \text{(2 PCs explain 99.28\% of variance)}$$
$$d_{\text{int}}(\text{ET}) = 0 \qquad \text{(zero variance; all feature vectors identical)}$$

---

### 3.4 Interpretation

**PC1 — The Major Third Axis (89.64%):**

The dominant axis separates keys with a pure meantone major third (score 0.1152) from keys where the major third is degraded (score 0.0026–0.0081). The eight "good" keys {C, G, D, A, G♭, E♭, B♭, F} have M3 ≈ 0.1152; the four "remote" keys {E, B, F♯, C♯} have M3 ≈ 0.0026–0.0081. This is the characteristic signature of quarter-comma meantone, which was specifically designed to give pure 5:4 major thirds in the most-used keys. The major third quality is the primary carrier of key-color information.

**PC2 — The Major Sixth / B-Key Axis (9.63%):**

The secondary axis is dominated by the B key, which has an anomalously high major sixth score (0.0699 vs. 0.0017 for other keys). This occurs because B's scale degree 6 (G♯/A♭) maps to the note G in our meantone tuning at 696.578¢ from C, giving an interval of (696.578 − 1082.892 + 1200)% 1200 = 813.686¢ from B — coincidentally close to the just minor sixth 8/5 = 813.686¢. This is a genuine acoustic feature (B major in meantone has an unusually pure minor sixth/enharmonic major sixth), though it comes at the cost of a degraded major third.

**Dimensionality collapse:**

The result $d_{\text{int}}(\text{ET}) = 0$ confirms Proposition 7.1'' from Appendix A.5: ET collapses the consonance feature manifold to a single point (all keys identical). The meantone manifold has intrinsic dimension 2 — two independent dimensions of variation (M3 quality and M6 quality, with M3 dominant). This replaces the informal "dimension 1 vs. dimension 2" argument of Theorems 7.1–7.2 with a precise, computable statement.

**Revised Theorem 7.1 (using PCA formulation):**

> **Proposition 7.1'' (Confirmed Numerically).** *The intrinsic dimension of the consonance field, computed as the number of principal components required to explain > 95% of the variance in the 12×7 key–interval consonance matrix, is:*
> $$d_{\text{int}}(\text{quarter-comma meantone}) = 2, \qquad d_{\text{int}}(\text{ET}) = 0$$
> *The dominant dimension (PC1, 89.64%) is the major-third quality axis, which separates keys within 3 fifths of C from keys beyond 4 fifths. The secondary dimension (PC2, 9.63%) captures the B-key major-sixth anomaly. Together these explain 99.28% of consonance variance across keys.*

---

### 3.5 Sensitivity Analysis: $I_{\text{vert}}^{\text{eff}}$ vs. $\beta$

The paper's estimate of 0.44 bits uses $\beta = 1$ without justification. The following table shows $I_{\text{vert}}^{\text{eff}}(\beta) = \log_2 12 - H(\mathcal{K}_\beta)$ for the Boltzmann distribution with key qualities from tuning_information.py:

| $\beta$ | $H(\mathcal{K}_\beta)$ (bits) | $I_{\text{vert}}^{\text{eff}}$ (bits) |
|---------|-------------------------------|----------------------------------------|
| 0.1 | 3.5849 | 0.0001 |
| 0.5 | 3.5835 | 0.0014 |
| 1.0 | 3.5788 | 0.0062 |
| 2.0 | 3.5566 | 0.0284 |
| 3.0 | 3.5120 | 0.0729 |
| 5.0 | 3.3289 | 0.2561 |
| 10.0 | 2.2189 | 1.3661 |

The paper's claimed 0.44 bits requires $\beta \approx 6$. This is in the high range of "acoustic properties strongly determine key choice" — plausible for meantone-era harpsichord music but not established empirically. For the more modest $\beta = 1$ (acoustic factors have unit weight among several equal factors), $I_{\text{vert}}^{\text{eff}} \approx 0.006$ bits — negligible.

**Critical consequence:** The paper's quantitative prediction in Section 4.4 (44 bits total vertical information loss, requiring ~11 additional syncopation events) is highly sensitive to $\beta$. At $\beta = 1$, the predicted effect is $\sim 100 \times 0.006 = 0.6$ bits total — smaller than one syncopation event. The argument requires $\beta \geq 5$ to generate a detectable effect.

**Required action:** Section 2.3 must be rewritten to present $I_{\text{vert}}^{\text{eff}}(\beta)$ as a function of the sensitivity parameter $\beta$, with the range $\beta \in [3, 10]$ representing the "strong acoustic influence" regime that makes the conservation effect detectable.

---

## Summary Table: What Is Now Fixed

| Issue | Original Status | Fixed Status |
|-------|----------------|--------------|
| Conservation law proof | Tautological lemma + undefined channel capacity | Option A (constrained optimization with explicit assumptions) + Hypothesis 8.1' with falsification criteria |
| Gabor/Heisenberg argument | Category error: consonance variance ≠ spectral spread | Replaced with HBBM entropy uncertainty (rigorous) + discrete Donoho-Stark uncertainty (applicable to key-space DFT) |
| Section 5 conclusion | "ET forces temporal complexity to increase" (unproved) | "HBBM provides a lower bound that is consistent with but does not compel greater temporal complexity in ET" |
| Intrinsic dimension argument | Hand-waving "2 vs. 1 degrees of freedom" | PCA gives $d_{\text{int}} = 2$ (meantone), $d_{\text{int}} = 0$ (ET), confirmed numerically |
| 0.44 bits estimate | Point estimate, $\beta = 1$ unjustified | Sensitivity table: range 0.0001 to 1.37 bits depending on $\beta$ |
| Theorem 8.1 | Presented as a proved theorem | Should be Hypothesis 8.1' with falsification criteria |

---

## References Added

- Beckner, W. (1975). "Inequalities in Fourier Analysis." *Ann. Math.* 102(1):159–182. [HBBM proof]
- Białynicki-Birula, I. & Mycielski, J. (1975). "Uncertainty Relations for Information Entropy in Wave Mechanics." *Commun. Math. Phys.* 44:129–132. [Entropic UP]
- Donoho, D. L. & Stark, P. B. (1989). "Uncertainty Principles and Signal Recovery." *SIAM J. Appl. Math.* 49(3):906–931. [Discrete UP]
- Hirschman, I. I. (1957). "A Note on Entropy." *Amer. J. Math.* 79(1):152–156. [Original result]
- Maassen, H. & Uffink, J. B. M. (1988). "Generalized Entropic Uncertainty Relations." *Phys. Rev. Lett.* 60(12):1103–1106. [Discrete version]
- McFadden, D. (1974). "Conditional Logit Analysis of Qualitative Choice Behavior." In Zarembka (ed.), *Frontiers in Econometrics.* Academic Press. [Discrete choice model for key selection]
- Cowan, N. (2001). "The Magical Number 4 in Short-Term Memory." *Behav. Brain Sci.* 24:87–185. [Cognitive capacity bound]

---

*End of Mathematical Fixes.*
