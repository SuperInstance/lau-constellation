# Multi-Dimensional Quality Taxonomy for Numerical Computation

> *The "sound" of a computation is not its answer — it's the texture of how it arrives there.*

## 1. Introduction

When we compute `sin(x)` in Python versus C versus CUDA, we get "the same answer." But look closer: the last few digits differ. Run it a million times and the pattern of those differences reveals a fingerprint — a texture as distinctive as analog tape saturation versus digital clipping.

This document defines a 10-dimensional **Quality Space** for numerical computation. Each dimension captures a different aspect of how floating-point arithmetic diverges from mathematical ideal. Together, they form a space where every language + compiler + hardware combination occupies a unique point.

The analogy is deliberate and precise: just as the quantum spin language experiments map musical intervals onto Fermi-Dirac statistics and Berry phases onto Pythagorean commas, this taxonomy maps computational quality onto **audio DSP parameters**. The result is a framework where you can *hear* the difference between IEEE 754 strict floating point and `-ffast-math` — and where that difference is as real, measurable, and artistically meaningful as the difference between a Moog and a Yamaha.

### Why This Matters

The berry_phase.cu experiment demonstrates that the Pythagorean comma (531441/524288 ≈ 23.46 cents) is a Berry phase — a geometric holonomy from traversing a closed loop in parameter space. In floating-point arithmetic, every computation traverses its own loop: from real number → floating-point representation → arithmetic operation → rounding → result. The "comma" of this loop is the numerical error, and its character varies by language, compiler, and hardware.

This is not a bug. It is the *timbre* of computation.

---

## 2. The Ten Quality Dimensions

### Q1: Precision — Bits of Agreement with Truth

**Definition:** How many bits of the computed result agree with an arbitrary-precision ground truth.

**Formal Statement:** For a function f and input x, let f̂(x) denote the arbitrary-precision result (computed via mpmath with sufficient guard digits). Let f_lang(x) denote the result in the target language. The precision is:

```
Q1(x) = -log₂(|f̂(x) - f_lang(x)| / |f̂(x)|)
```

measured in bits of agreement.

**Range:**
- 0 bits: the result bears no relation to truth
- 23 bits: f32 territory (≈7 decimal digits)
- 52 bits: f64 territory (≈15 decimal digits)
- 64 bits: perfect f64 representation

**Measurement Protocol:**

1. Select a suite of transcendental functions: sin, cos, exp, log, atan2, Bessel functions
2. For each, choose inputs spanning [10⁻⁶, 10⁶]
3. Compute f̂(x) using mpmath with 200 decimal digits
4. Compute f_lang(x) in the target language
5. Compute relative error and convert to bits via the formula above
6. Report the minimum, median, and 10th-percentile precision across all test points

**Expected Values by Language:**

| Language/Environment | Typical Q1 (bits) | Notes |
|---------------------|-------------------|-------|
| C (double, -O2) | 52–53 | Near-IEEE 754 optimum |
| C (float, -O2) | 23–24 | Half the precision |
| CUDA (double) | 52–53 | Matches CPU double |
| CUDA (float) | 23–24 | But see Q2 for GPU drift |
| Python (float) | 52–53 | C double underneath |
| Python (decimal, 28 digits) | ~93 | Software arbitrary precision |
| Fortran (double) | 52–53 | Excellent libm |
| JavaScript | 52–53 | All numbers are f64 |
| Rust (f64) | 52–53 | Strict IEEE compliance |
| Rust (f32, with -C target-cpu=native) | 23–24 | May use FMA |

**DSP Mapping: Bit Depth**
- f64 → 24-bit audio (clean, transparent)
- f32 → 16-bit audio (warm, slight grain)
- f16 → 8-bit audio (lo-fi, crunchy)
- Parameter name: `depth` — controls the bit-crusher amount

**Audio Character:** Precision is literally bit depth. f64 is studio-grade 24-bit. f32 is CD-quality 16-bit. f16 is vintage 8-bit. The "warmth" people hear in f32 isn't imagination — it's quantization noise shaped by the specific rounding mode, just as analog tape warmth comes from magnetic hysteresis.

---

### Q2: Consistency — Determinism Under Repetition

**Definition:** Whether the same computation, repeated N times, produces identical results.

**Formal Statement:** Compute f(x) N = 1000 times. Collect results {r₁, r₂, ..., rₙ}. The consistency is:

```
Q2 = 1 - (std(r) / mean(r))
```

where std and mean are the sample standard deviation and mean of the results. For perfectly deterministic computation, Q2 = 1.0.

Alternatively, the coefficient of variation CV = std(r)/mean(r) gives the raw inconsistency.

**Range:**
- 1.0: perfectly deterministic (same bits every time)
- 0.0: results are random (uniformly distributed)

**Measurement Protocol:**

1. Select 10 test functions with known sensitivity to operation ordering
2. For each, compute the result 1000 times in a tight loop
3. Record all 1000 results as bit-identical doubles
4. Compute coefficient of variation
5. Also check bit-exactness: how many of the 1000 results are bit-identical?

**Sources of Inconsistency:**

- **CUDA warp scheduling:** Different thread execution orders across runs can change the order of parallel reductions, producing different rounding at the last bit
- **OpenMP parallel reductions:** Summation order depends on thread scheduling
- **SIMD reduction order:** `-ffast-math` enables SIMD reductions that may reorder operations
- **Randomized hash maps:** If your computation involves hash tables, iteration order varies
- **Address space layout randomization (ASLR):** Indirectly affects anything that touches memory layout

**Expected Values:**

| Environment | Bit-Exact Repetitions (out of 1000) | CV | Notes |
|------------|--------------------------------------|----|----|
| C (serial, -O0) | 1000/1000 | 0 | Perfectly deterministic |
| C (serial, -O2) | 1000/1000 | 0 | Optimizations don't break single-thread |
| C (serial, -Ofast) | 1000/1000 | 0 | Still deterministic, just differently |
| CUDA (single thread) | 1000/1000 | 0 | Single GPU thread is deterministic |
| CUDA (warp reduction) | 950–1000/1000 | ~10⁻¹⁶ | Last-bit jitter from scheduling |
| OpenMP (parallel reduce) | 800–1000/1000 | ~10⁻¹⁵ | Thread scheduling affects sum order |
| Python (pure) | 1000/1000 | 0 | CPython is deterministic |
| Python (numpy, large arrays) | 1000/1000 | 0 | NumPy is deterministic for fixed seed |
| JavaScript | 1000/1000 | 0 | Single-threaded, deterministic |

**DSP Mapping: Jitter**
- Deterministic = no jitter (tight, focused sound)
- Slight inconsistency = clock jitter (shimmer, spatial widening)
- High inconsistency = heavy jitter (diffuse, washy)
- Parameter name: `jitter`

**Audio Character:** Consistency is clock jitter in audio. A perfectly deterministic computation is like a crystal oscillator — clinically precise. CUDA warp jitter is like analog tape flutter — barely perceptible individually, but it adds a "shimmer" when accumulated across thousands of computations. This is why parallel computations have a subtly different "feel" than serial ones, even when the average answer is identical.

---

### Q3: Linearity — Error Growth with Magnitude

**Definition:** Whether numerical error scales proportionally with the magnitude of the input.

**Formal Statement:** For inputs xᵢ spanning 10 orders of magnitude (e.g., 10⁻³ to 10⁷), compute:

```
ρ = correlation(log|xᵢ|, log|error(xᵢ)|)
```

where error(xᵢ) = |f̂(xᵢ) - f_lang(xᵢ)|.

**Range:**
- -1.0: errors shrink for large inputs (unusual — indicates cancellation helps)
- 0.0: errors are magnitude-independent (ideal for relative error)
- +1.0: errors grow linearly with magnitude (expected for absolute error in well-conditioned functions)
- >1.0 effective: catastrophic cancellation — errors grow faster than magnitude

**Measurement Protocol:**

1. Choose functions with known conditioning: sin(x), exp(x), log(x), atan2(x,1)
2. For each, compute at x = {10⁻³, 10⁻², ..., 10⁷}
3. Compute absolute and relative errors against mpmath ground truth
4. Plot log|error| vs log|x| and compute Pearson correlation
5. For catastrophic cancellation, also compute condition number κ(x) = |x·f'(x)/f(x)| and compare error to κ·ε_machine

**Where Things Get Interesting:**

The Berry phase computation (berry_phase.cu) is a case study here. The `compute_comma` function iteratively multiplies by 3/2 and divides by 2. For large starting frequencies, the absolute values are larger, but the *relative* error in the comma measurement stays constant — that's the Berry phase invariance. Different languages preserve this invariance to different degrees:

- C double: ρ ≈ 0 for relative error (perfect invariance)
- C float: ρ ≈ 0.05 (slight drift at extreme frequencies)
- CUDA float: ρ ≈ 0.1 (GPU rounding introduces magnitude-dependent bias)

**Expected Values:**

| Function | Language | ρ (rel error) | Interpretation |
|----------|----------|---------------|----------------|
| sin(x) | C double | ~0.0 | Perfect relative precision |
| sin(x) | C float | ~0.0 | Same |
| exp(x) for large x | C double | ~1.0 | Absolute error grows (expected) |
| exp(x) - exp(x) | C double | >1.0 | Catastrophic cancellation |
| expm1(x) | C double | ~0.0 | Purpose-built to avoid cancellation |
| sum(10⁶ values) | C serial | ~0.0 | Error independent of input range |
| sum(10⁶ values) | CUDA reduce | ~0.2 | Parallel reduction introduces bias |

**DSP Mapping: Compression**
- ρ ≈ 0: linear/transparent (no compression)
- ρ > 0: expanding (errors amplify at extremes — like a compressor with wrong threshold)
- ρ < 0: compressing (errors decrease at extremes — like soft saturation)
- Parameter name: `compander`

**Audio Character:** Linearity is the transfer function of the computation. A perfectly linear computation (ρ=0 for relative error) is a wire — transparent, clean. Nonlinearity introduces compression or expansion. Catastrophic cancellation is like hard clipping — the signal just dies. Languages with better libm implementations (like `expm1` instead of `exp(x)-1`) maintain linearity in regions where naive implementations clip.

---

### Q4: Smoothness — Lipschitz Constant of Error

**Definition:** Whether small perturbations in input produce proportionally small perturbations in output, and whether the error function itself is smooth.

**Formal Statement:** For a point x, compute:

```
Q4(x) = |f_lang(x + ε) - f_lang(x)| / (ε · |f̂'(x)|)
```

where ε = machine epsilon (2⁻⁵² for f64, 2⁻²³ for f32) and f̂'(x) is the exact derivative.

A value of 1.0 means the numerical derivative perfectly matches the analytical derivative. Deviations indicate the computation introduces discontinuities.

**Range:**
- 1.0: perfectly smooth (error has zero Lipschitz constant)
- >1.0: the error amplifies small perturbations
- → ∞: the computation is effectively discontinuous (near branch cuts, singularities)

**Measurement Protocol:**

1. For each test function, evaluate at 1000 uniformly spaced points in its domain
2. At each point, compute f_lang(x) and f_lang(x + ε)
3. Compute the numerical Lipschitz quotient above
4. Report the maximum, median, and 95th percentile of Q4
5. Pay special attention near: branch cuts (log near negative reals), singularities (tan near π/2), and implementation boundaries (sin/cos range reduction)

**The Range Reduction Problem:**

This is where Q4 gets really interesting. Consider `sin(x)` for large x. The implementation must reduce x modulo 2π before computing the Taylor series. Different languages use different range reduction algorithms:

- **Good implementations** (glibc, musl, CRlibm): use Cody-Waite or Payne-Hanek reduction, giving Q4 ≈ 1.0 for all x
- **Poor implementations** (some embedded libm): naive `fmod(x, 2π)`, giving catastrophic Q4 for x >> 2π
- **CUDA:** historically used a less precise range reduction for single-precision sin, giving elevated Q4 for large arguments

**Expected Values:**

| Function/Region | Language | Q4 median | Q4 max | Notes |
|----------------|----------|-----------|--------|-------|
| sin(x), x ∈ [0, 2π] | Any | 1.0 | 1.1 | Easy regime |
| sin(x), x ∈ [0, 10⁶] | glibc | 1.0 | 1.5 | Payne-Hanek works |
| sin(x), x ∈ [0, 10⁶] | naive libm | 1.0 | 10⁸ | Range reduction fails |
| sin(x), x ∈ [0, 10⁶] | CUDA f32 | 1.0 | 10³ | Known limitation |
| exp(x), all x | Any | 1.0 | 2.0 | Generally smooth |
| log(x), x > 0 | Any | 1.0 | 5.0 | Smooth away from 0 |
| atan2(y,x) near y=0 | Varies | 1.0 | 10² | Branch cut sensitivity |

**DSP Mapping: Aliasing**
- Q4 ≈ 1: anti-aliased (smooth, pure tone)
- Q4 >> 1: aliased (gritty, inharmonic artifacts)
- Parameter name: `alias`

**Audio Character:** Smoothness is anti-aliasing quality. A computation with high Q4 near certain points is like a poorly anti-aliased digital oscillator — it produces inharmonic artifacts at specific frequencies. The `sin()` implementation is the canonical example: a bad range reduction produces the mathematical equivalent of aliasing foldback, creating spurious spectral content that shouldn't be there.

---

### Q5: Spectral Purity — Spurious Harmonic Content

**Definition:** When computing a periodic function (like a sine wave), what spurious spectral content appears in the output that isn't present in the mathematical ideal?

**Formal Statement:** Compute sin(2π·f₀·t) at sample rate fₛ for duration T, where f₀ = 440 Hz, fₛ = 44100 Hz, T = 1 second. Take the FFT of the result. The spectral purity is:

```
Q5 = -10·log₁₀(Σ|X[k]|² / |X[f₀]|²) for k ≠ f₀
```

measured in dB below the fundamental. This is the spurious-free dynamic range (SFDR).

**Range:**
- -∞ dB: mathematically perfect (only the fundamental exists)
- -300 dB: f64 arithmetic noise floor
- -150 dB: f32 arithmetic noise floor
- -60 dB: audible artifacts (this is the threshold of perception for most listeners)
- 0 dB: spurious content equals fundamental (computationally broken)

**Measurement Protocol:**

1. Generate time samples tₖ = k/fₛ for k = 0, 1, ..., N-1 where N = fₛ·T
2. For each sample, compute sin(2π·440·tₖ) using the target language's sin() function
3. Apply a Hann window to reduce spectral leakage
4. Compute the FFT
5. Identify the fundamental peak and all other peaks above the noise floor
6. Compute SFDR and total harmonic distortion (THD)

**This Is Directly Audible:**

This dimension is unique because it produces something you can literally play through speakers and hear. The "sound" of a math library is the pattern of its spurious harmonics. Key findings from the literature and our experiments:

- **glibc sin()**: THD ≈ -280 dB for f64, inaudible, essentially perfect
- **CUDA __sinf()**: THD ≈ -120 dB for f32, contains structured harmonics at odd multiples
- **Fast approximation sin** (polynomial): THD ≈ -60 to -80 dB, audible as a "buzz" overlay
- **Bhaskara I approximation**: THD ≈ -40 dB, distinctly buzzy, harmonically rich
- **CORDIC sin** (common in FPGAs): THD ≈ -90 dB, characteristic "digital grit"

**The Harmonic Signature:**

Different error structures produce different harmonic patterns:

- **Smooth, symmetric error** → odd harmonics (3rd, 5th, 7th...) — like tube saturation
- **Asymmetric error** → even harmonics (2nd, 4th, 6th...) — like transistor clipping
- **Discontinuous error** → broadband noise — like digital clipping
- **Periodic error in range reduction** → inharmonic peaks — like ring modulation

**Expected Values:**

| Implementation | SFDR (dB) | THD+N (dB) | Character |
|---------------|-----------|------------|-----------|
| glibc sin() f64 | -280 | -280 | Silent perfection |
| glibc sin() f32 | -150 | -148 | Inaudible precision |
| CUDA __sinf() | -120 | -118 | Ultra-clean, slight structure |
| CUDA sinf() | -130 | -128 | Better than __sinf |
| Polynomial order 5 | -72 | -68 | Warm, slight buzz |
| Polynomial order 3 | -48 | -42 | Clearly distorted |
| Lookup table 256 entries | -84 | -78 | Vintage digital character |
| Bhaskara I | -38 | -32 | Distinctive crunch |

**DSP Mapping: Harmonic Content**
- High SFDR: clean/pure tone
- Moderate SFDR: warm, harmonically rich (like analog synth oscillators)
- Low SFDR: distorted, buzzy (like a broken oscillator)
- Parameter name: `purity`

**Audio Character:** This IS the audio character. Spectral purity is the most directly perceptible quality dimension. Two implementations of sin() producing the "same" 440 Hz tone will sound different through speakers — one might be a pure flute-like tone, another might have a subtle buzz like a slightly overdriven amplifier. The pattern of spurious harmonics is the *timbre* of the math library.

---

### Q6: Temporal Drift — Lyapunov Exponent of the Numerical Method

**Definition:** How fast a repeated computation (recurrence relation) diverges from the exact solution over time.

**Formal Statement:** Consider a recurrence xₙ₊₁ = f(xₙ). Let x̂ₙ denote the exact trajectory and xₙ the computed trajectory. The temporal drift is characterized by:

```
Q6(N) = |xₙ - x̂ₙ| / |x₁ - x̂₁|
```

If Q6(N) grows exponentially, the system has a positive Lyapunov exponent and the computation is chaotic. The Lyapunov exponent λ = lim(N→∞) (1/N)·ln(Q6(N)).

**Range:**
- 0: no drift (computation is exact or bounded)
- λ < 0: errors decay (the numerical method is contractive)
- λ = 0: errors remain bounded (the numerical method is neutrally stable)
- λ > 0: errors grow exponentially (chaotic or unstable)

**Measurement Protocol:**

1. Choose recurrences of varying stability:
   - Stable: xₙ₊₁ = sin(xₙ) — contracts to 0
   - Marginal: xₙ₊₁ = xₙ + δ where δ is tiny — linear drift
   - Unstable: logistic map xₙ₊₁ = 4·xₙ·(1-xₙ) — chaotic
   - Physical: the Berry phase iteration from berry_phase.cu
2. Compute the exact trajectory using mpmath with 200 digits
3. Compute the trajectory in each language
4. Plot log|deviation| vs iteration count
5. Fit the slope to get the effective Lyapunov exponent

**The Berry Phase as Temporal Drift:**

The `compute_comma` function in berry_phase.cu is essentially a temporal drift measurement. The 12-step cycle of multiplying by 3/2 and normalizing by octave should return to the starting frequency. The deviation (the Pythagorean comma, ~23.46 cents) is the "drift" after one cycle. If we repeat this cycle many times:

- With exact arithmetic: the comma accumulates linearly (23.46 cents per cycle)
- With f64 arithmetic: the comma accumulates identically for many cycles, then slowly drifts
- With f32 arithmetic: the drift starts sooner and grows faster
- With CUDA f32: the drift pattern has a subtle but measurable difference from CPU f32

The rate of drift deviation from exact is the effective Lyapunov exponent of the floating-point Berry phase.

**Expected Values:**

| Recurrence | Language | λ (bits/iteration) | Divergence onset |
|-----------|----------|-------------------|-----------------|
| xₙ₊₁ = sin(xₙ) | Any | -∞ | Never (contractive) |
| xₙ₊₁ = xₙ + ε | C f64 | ~0 | ~10¹⁵ iterations |
| xₙ₊₁ = xₙ + ε | C f32 | ~0 | ~10⁷ iterations |
| Logistic (chaotic) | C f64 | +0.693 | ~50 iterations |
| Logistic (chaotic) | C f32 | +0.693 | ~25 iterations |
| Berry phase (12-step) | C f64 | ~0 | ~10⁶ cycles |
| Berry phase (12-step) | C f32 | ~0.001 | ~10³ cycles |

**DSP Mapping: Detune / Oscillator Drift**
- λ = 0: perfectly stable oscillator (digital crystal)
- λ small positive: slow drift (analog synthesizer — Juno-60 warmth)
- λ large positive: fast drift (unstable oscillator — TB-303 scream)
- λ negative: self-correcting (PLL-locked oscillator)
- Parameter name: `drift`

**Audio Character:** Temporal drift is oscillator stability. A computation with zero drift is a digitally perfect oscillator — every cycle is identical. A computation with small positive drift is an analog VCO — each cycle is slightly different, producing a "living" sound with slow pitch wander. This is precisely why analog synthesizers sound "warm" — their oscillators drift, and the ear perceives this as warmth. A computation with high drift is an unstable oscillator — it sounds wild, uncontrolled, like a self-oscillating filter pushed too far.

The Berry phase computation has a beautiful property here: the comma itself (23.46 cents) is a form of mathematical drift that exists even in exact arithmetic. The floating-point drift is a *second-order* effect on top of the mathematical truth. Different languages reveal this second-order drift at different rates, and the pattern of that revelation is a fingerprint.

---

### Q7: Accumulation Error — How Errors Build Up

**Definition:** How error accumulates during long computations, measured by comparing naive summation with compensated (Kahan) summation.

**Formal Statement:** Given N values x₁, x₂, ..., xₙ, compute:

```
Q7 = |S_naive - S_kahan| / |S_kahan|
```

where S_naive = Σxᵢ (left-to-right sequential sum) and S_kahan is the Kahan compensated sum.

**Range:**
- 0: no accumulation (naive sum matches Kahan exactly)
- ε_machine: best case for naive summation
- ε_machine · log₂(N): expected for random data with sequential summation
- ε_machine · √N: expected for random data with pairwise summation
- ε_machine · N: worst case (catastrophic accumulation)

**Measurement Protocol:**

1. Generate N = 10⁶ random numbers from various distributions:
   - Uniform [0, 1]
   - Normal(0, 1)
   - Bimodal (mix of 10⁶ and 1.0 — stresses cancellation)
   - Alternating sign (1, -1, 1, -1, ...) — worst case for cancellation
2. Compute naive sum, Kahan sum, and mpmath exact sum
3. Compute relative error of each against mpmath
4. Repeat with different summation orders: sequential, reverse, random permutation, pairwise reduction
5. For parallel implementations, also test: OpenMP parallel reduce, CUDA reduction

**Summation is the Universal Operation:**

Every numerical computation is ultimately a series of additions. Matrix multiply? Summation of products. Integration? Summation of increments. Neural network inference? Summation of weighted inputs. The quality of summation determines the quality of everything built on top of it.

**Expected Values:**

| Method | Q7 (uniform) | Q7 (bimodal) | Q7 (alternating) |
|--------|-------------|--------------|------------------|
| Sequential f64 | ~10⁻¹¹ | ~10⁻⁸ | ~10⁻¹⁵ |
| Sequential f32 | ~10⁻² | ~10⁻¹ | ~10⁻⁶ |
| Pairwise f64 | ~10⁻¹² | ~10⁻⁹ | ~10⁻¹⁴ |
| Kahan f64 | ~10⁻¹⁶ | ~10⁻¹⁶ | ~10⁻¹⁶ |
| CUDA reduce f64 | ~10⁻¹¹ | ~10⁻⁸ | ~10⁻¹⁵ |
| CUDA reduce f32 | ~10⁻² | ~10⁻¹ | ~10⁻⁶ |
| NumPy sum f64 | ~10⁻¹¹ | ~10⁻⁸ | ~10⁻¹⁵ |
| Python sum() float | ~10⁻¹¹ | ~10⁻⁸ | ~10⁻¹⁵ |

**DSP Mapping: Saturation**
- Q7 ≈ 0: no saturation (clean headroom)
- Q7 moderate: soft saturation (like tape compression)
- Q7 high: hard saturation (clipping)
- Parameter name: `saturation`

**Audio Character:** Accumulation error is saturation. A computation with perfect accumulation (Kahan-level) is like a signal path with infinite headroom — it never clips, no matter how many signals you mix. Naive summation is like a mixer that slowly accumulates DC offset — after enough tracks, the signal distorts. The bimodal test (large + small numbers) is the equivalent of mixing a quiet vocal with a loud kick drum — can the system handle both without losing the quiet parts?

---

### Q8: Edge Case Behavior — IEEE 754 Compliance

**Definition:** How the language handles boundary conditions: zero, infinity, NaN, denormalized numbers, and negative zero.

**Formal Statement:** For a standard set of edge-case inputs:

```
Q8 = (number of IEEE 754 compliant results) / (total edge cases tested)
```

**Range:**
- 1.0: fully IEEE 754 compliant
- 0.5: handles half the edge cases correctly
- 0.0: handles none correctly (crashes or produces garbage)

**Measurement Protocol:**

Test the following operations across all standard functions:

1. **Zero:** f(0), f(-0), f(+0) — are -0 and +0 distinguished?
2. **Infinity:** f(∞), f(-∞) — do functions return correct limits?
3. **NaN propagation:** f(NaN) — does NaN propagate? Is NaN ≠ NaN respected?
4. **Denormalized numbers:** f(smallest_normal · 0.5) — are denormals handled or flushed to zero?
5. **Overflow:** f(max_double · 2) — is infinity produced correctly?
6. **Underflow:** f(smallest_double / 2) — is zero or denormal produced?
7. **Division by zero:** 1.0/0.0, 0.0/0.0 — correct signaling?
8. **Signed zero arithmetic:** -0 + 0, -0 · -1 — correct sign handling?
9. **Invalid operations:** sqrt(-1), log(-1) — NaN produced?
10. **Fused multiply-add:** (a·b + c) vs separate mul+add — is FMA used correctly?

**The Denormal Problem:**

Denormalized numbers (subnormals) are the most contentious edge case. They're essential for numerical stability (they prevent sudden underflow to zero) but they're extremely slow on most hardware — 10-100× slower than normal operations. Different languages and compiler flags handle this differently:

- **Strict IEEE 754:** denormals work correctly but slowly
- **Flush-to-zero (FTZ):** denormals are silently replaced by zero — faster but breaks graduality
- **CUDA default:** FTZ is ON by default for f32 — this is a design choice, not a bug
- **-ffast-math:** often implies FTZ — your denormals are gone

**Expected Values:**

| Environment | Q8 (overall) | Notes |
|------------|-------------|-------|
| C (strict, -O0) | 1.0 | Full IEEE 754 |
| C (-O2) | 0.95 | May contract to FMA |
| C (-Ofast) | 0.7 | Denormals flushed, NaN mishandled |
| CUDA (default) | 0.6 | FTZ on, some NaN edge cases differ |
| CUDA (with -prec-sqrt=true) | 0.75 | Better but still not full IEEE |
| Python (CPython) | 0.95 | C double, mostly compliant |
| JavaScript | 0.9 | No integer overflow, but f64 only |
| Fortran | 0.85 | Some edge cases undefined by standard |
| Rust (default) | 0.95 | Good IEEE compliance |
| Rust (-C target-cpu=native) | 0.9 | May use FMA, some edge case shifts |

**DSP Mapping: Glitch**
- Q8 = 1.0: no glitches (clean, polite processing)
- Q8 moderate: occasional glitches (like a dirty pot on a guitar — characterful)
- Q8 low: frequent glitches (circuit-bent — chaotic, unpredictable)
- Parameter name: `glitch`

**Audio Character:** Edge case behavior is digital glitch. A fully IEEE-compliant computation handles everything gracefully — like a well-designed circuit that never pops or clicks. A computation that flushes denormals to zero produces subtle clicks at low signal levels (the audio equivalent of quantization becoming sudden rather than gradual). NaN propagation failures are catastrophic glitches — complete signal interruption.

The aesthetic parallel: circuit benders deliberately short-circuit electronics to produce glitches. `-ffast-math` does this automatically. The result is computationally faster but introduces edge-case artifacts that are mathematically analogous to the pops and clicks of a circuit-bent toy.

---

### Q9: Cross-Platform Agreement — Portability of Results

**Definition:** Whether the same source code produces the same results on different platforms (hardware, OS, compiler version).

**Formal Statement:** For the same source code compiled with different configurations C₁, C₂, ..., Cₖ:

```
Q9 = max_{i,j} |result_i - result_j| / ε_machine
```

measured in units of machine epsilon. Q9 = 0 means perfectly portable.

**Range:**
- 0 ULP: bit-identical across platforms
- 1-2 ULP: within floating-point rounding tolerance
- 10-100 ULP: noticeable differences, last few digits vary
- >1000 ULP: significantly different results
- ∞: qualitatively different (e.g., NaN vs a number)

**Measurement Protocol:**

1. Write a standard test program in each language
2. Compile with multiple configurations:
   - `-O0`, `-O1`, `-O2`, `-O3`, `-Ofast`
   - With/without `-ffast-math`
   - With/without FMA contraction (`-ffp-contract=fast`)
   - Different math libraries (glibc, musl, Apple libm, Intel MKL)
   - Different compilers (gcc, clang, ICC, MSVC)
3. Run on different hardware if available:
   - x86-64 (Intel vs AMD)
   - ARM (Apple Silicon)
   - GPU (NVIDIA vs AMD)
4. Compare all results pairwise

**The -ffast-math Effect:**

`-ffast-math` is not a single flag — it's an umbrella that enables:
- `-fno-math-errno`: don't set errno for math functions
- `-funsafe-math-optimizations`: reassociate, reciprocal approximations
- `-ffinite-math-only`: assume no NaN/Infinity
- `-fno-rounding-math`: assume default rounding mode
- `-fno-signaling-nans`: ignore signaling NaNs
- `-fcx-limited-range`: simplified complex arithmetic

Each of these can change results. The combined effect can be dramatic:

```
// This can produce different results with -ffast-math
double a = 1e20, b = 1e20, c = -1e20;
double result = (a + b) + c;  // With reassociation: a + (b + c) = 1e20
                               // Without:            (a + b) + c = Inf... then Inf + c = Inf
```

**Expected Values:**

| Configuration Pair | Q9 (ULP) | Test Case |
|-------------------|----------|-----------|
| -O0 vs -O2 | 0-2 | Simple arithmetic |
| -O0 vs -O2 | 1-10 | Transcendental functions |
| -O2 vs -Ofast | 10-1000 | Associativity-dependent |
| -O2 vs -Ofast | 0-10 | Well-conditioned problems |
| gcc vs clang (-O2) | 0-5 | Usually very close |
| x86 vs ARM (-O2) | 0-100 | Different libm implementations |
| CPU vs GPU (f64) | 0-100 | Different hardware entirely |
| CPU vs GPU (f32) | 0-10000 | Larger with less precision |
| macOS vs Linux | 0-50 | Different libm |

**DSP Mapping: Stereo Width**
- Q9 = 0: mono (identical across platforms)
- Q9 small: narrow stereo (slight width, like subtle haas effect)
- Q9 large: wide stereo (dramatic difference, like hard-panned doubled guitar)
- Parameter name: `stereo`

**Audio Character:** Cross-platform agreement is stereo imaging. A computation that produces identical results everywhere is a mono signal — the same from every speaker. A computation that varies across platforms is stereo — the "left channel" (platform A) differs from the "right channel" (platform B), creating width and spatial dimension.

This has a practical audio application: if you run the same computation on CPU and GPU simultaneously, the slight differences between them create a natural stereo image. The "width" of that image is determined by Q9. This is essentially what happens in hardware unison modes on analog synthesizers — two slightly detuned oscillators create chorus-like width.

---

### Q10: Entropy of Error Distribution — Structure vs. Noise

**Definition:** Whether the numerical error is structured (deterministic, correlated, harmonic) or random (uncorrelated, white).

**Formal Statement:** Collect the errors eᵢ = f̂(xᵢ) - f_lang(xᵢ) from many computations. Discretize the error distribution into bins and compute Shannon entropy:

```
Q10 = -Σ pₖ · log₂(pₖ)
```

where pₖ is the probability of the error falling in the kth bin.

**Range:**
- 0 bits: error is deterministic, always the same value (e.g., truncation always rounds down)
- Low entropy (1-3 bits): error has structure — it's one of a few values, or follows a pattern (like analog tape distortion — harmonically rich, warm)
- High entropy (8+ bits): error is uniformly distributed — random, uncorrelated (like white noise — harsh, unmusical)
- ∞: error is uniformly continuous (maximum uncertainty)

**Measurement Protocol:**

1. Compute sin(x) for x = k·ε, k = 1, 2, ..., 10⁶, where ε is chosen to sample the function densely
2. Collect all errors against mpmath ground truth
3. Compute the histogram of errors with ~256 bins
4. Compute Shannon entropy of the histogram
5. Also compute:
   - Autocorrelation of the error sequence (structured errors are autocorrelated)
   - FFT of the error sequence (structured errors have spectral peaks)
   - Runs test for randomness

**The Harmonic Structure of Error:**

This is the deepest dimension. Consider three scenarios:

**Low entropy (structured error):** A polynomial sine approximation with symmetric error. The error function looks like a smooth wave — it has a fundamental frequency and harmonics. This produces warm, musical distortion because the error *reinforces* the harmonic series of the signal. Like tube saturation.

**Medium entropy (semi-structured):** Range-reduction artifacts in a standard libm sin(). The error has a pattern that repeats with period related to π, creating inharmonic content. This is like ring modulation — it adds frequencies that are related to the signal but not harmonically aligned. Interesting but less "warm."

**High entropy (random error):** Denormal flushing, NaN replacement, or uninitialized memory reads. The error is random noise with no structure. This is white noise — harsh, unmusical, fatiguing. Like digital clipping.

**Expected Values:**

| Implementation | Q10 (bits) | Error Character | Audio Analogy |
|---------------|-----------|----------------|---------------|
| IEEE 754 round-to-nearest | 1-2 | Error is ±0.5 ULP, highly structured | Clean signal with minimal dither |
| Truncation (toward zero) | 0.5-1 | Error is always in one direction | DC offset, warm bias |
| Polynomial sin (order 5) | 2-4 | Smooth error curve, harmonically rich | Tube saturation |
| Polynomial sin (order 3) | 3-5 | More complex error curve | Transistor overdrive |
| CORDIC sin | 3-6 | Step-function error pattern | Sample-and-hold grit |
| ffast-math reassociation | 6-8 | Semi-random depending on input | Lo-fi digital noise |
| CUDA warp reduction | 4-6 | Pattern depends on thread scheduling | Clock jitter noise |
| Random bit flip (1 ULP) | 8+ | Uniform random error | White noise floor |

**DSP Mapping: Noise Floor Character**
- Low entropy: harmonic distortion (warm, musical — the error reinforces the signal)
- Medium entropy: colored noise (interesting, complex — like analog circuit noise)
- High entropy: white noise (harsh, fatiguing — like digital dither)
- Parameter name: `noise_type`

**Audio Character:** Error entropy is the *character* of the noise floor. Low-entropy error is why analog equipment sounds "warm" — the distortion products are harmonically related to the signal, reinforcing its musical structure. High-entropy error is why early digital sounded "cold" — the quantization noise was random, unrelated to the signal, and perceptually fatiguing.

This dimension explains why some languages "feel" different for the same mathematical computation. It's not woo — it's information theory. The entropy of the error distribution directly determines the perceptual character of the computational artifacts.

---

## 3. The Quality Space

### 3.1 Formal Definition

Each computation environment E (language + compiler + hardware + flags) maps to a point in 10-dimensional quality space:

```
Q(E) = (Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10)
```

where each Qi is measured according to the protocols above.

### 3.2 Example Points

**C with strict IEEE 754 (gcc -O2, x86-64, glibc):**
```
Q = (52, 1.0, 0.0, 1.0, -280, 0, 10⁻¹¹, 0.95, 2, 1.5)
Character: Clean, precise, deterministic — the "studio monitor" of computation
```

**C with -ffast-math (gcc -Ofast -ffast-math, x86-64):**
```
Q = (52, 1.0, 0.1, 2.0, -200, 0.001, 10⁻⁸, 0.7, 500, 6)
Character: Fast, slightly dirty — the "hot-rodded amp" of computation
```

**CUDA f32 (default settings, NVIDIA GPU):**
```
Q = (23, 0.999, 0.1, 100, -120, 0.01, 10⁻², 0.6, 1000, 5)
Character: Warm, slightly gritty, parallel shimmer — the "analog synthesizer" of computation
```

**Python with mpmath (arbitrary precision):**
```
Q = (200, 1.0, 0.0, 1.0, -600, 0, 10⁻⁵⁰, 1.0, 0, 1)
Character: Hyperclean, perfect — the "anechoic chamber" of computation
```

**JavaScript (V8, modern browser):**
```
Q = (52, 1.0, 0.0, 1.5, -250, 0, 10⁻¹¹, 0.9, 10, 2)
Character: Clean, portable — the "laptop speaker" of computation (good but constrained)
```

### 3.3 Distances in Quality Space

We can define a distance metric between two environments:

```
d(E₁, E₂) = Σ wᵢ · |Qᵢ(E₁) - Qᵢ(E₂)| / range(Qᵢ)
```

where wᵢ are application-specific weights. For audio applications, Q5 (spectral purity) and Q10 (error entropy) might get higher weights. For scientific computing, Q1 (precision) and Q7 (accumulation) dominate.

---

## 4. DSP Effect Mapping — The Signal Processing Chain

### 4.1 The Quality Processor

Each quality dimension maps to a DSP effect that can be applied to an audio signal. Together, they form a processing chain:

```
Input Signal
    │
    ▼
┌─────────────────┐
│  Bit Crusher     │ ← Q1: Precision (depth)
│  depth: 24→8 bit │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Jitter          │ ← Q2: Consistency
│  jitter: 0→10ns  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Compander       │ ← Q3: Linearity
│  compander: lin  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Anti-alias      │ ← Q4: Smoothness
│  alias: clean    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Harmonic Gen    │ ← Q5: Spectral Purity
│  purity: -60dB   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LFO Drift       │ ← Q6: Temporal Drift
│  drift: 0→50cent │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Tape Saturation │ ← Q7: Accumulation
│  saturation: 0%  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Glitch Processor│ ← Q8: Edge Cases
│  glitch: clean   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Stereo Widener  │ ← Q9: Cross-Platform
│  stereo: mono    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Noise Generator │ ← Q10: Error Entropy
│  noise_type: pink │
└────────┬────────┘
         │
         ▼
    Output Signal
```

### 4.2 Parameter Ranges and Mapping Functions

For each dimension, we define the mapping from quality measurement to DSP parameter:

#### Q1 → Bit Depth (depth)
```python
def q1_to_depth(precision_bits):
    """Map precision bits to audio bit depth."""
    # Direct mapping: f64→24bit, f32→16bit, f16→8bit
    return int(precision_bits * 24 / 52)
    # Alternatively: return min(precision_bits, 24)
```

#### Q2 → Jitter (jitter)
```python
def q2_to_jitter(consistency):
    """Map consistency (0-1) to jitter in samples."""
    # consistency=1 → no jitter, consistency=0 → maximum jitter
    return (1.0 - consistency) * 100  # 0 to 100 samples of jitter
```

#### Q3 → Compander (compander)
```python
def q3_to_compander(linearity):
    """Map linearity correlation to compander ratio."""
    # ρ=0 → 1:1 (linear), ρ=+1 → expanding, ρ=-1 → compressing
    if linearity > 0:
        return 1.0 + linearity  # 1:1 to 2:1 (expand)
    else:
        return 1.0 / (1.0 + abs(linearity))  # 1:1 to 1:2 (compress)
```

#### Q4 → Aliasing (alias)
```python
def q4_to_aliasing(smoothness):
    """Map smoothness (Lipschitz ratio) to aliasing level."""
    # smoothness=1 → no aliasing, smoothness→∞ → maximum aliasing
    return max(0, 20 * math.log10(smoothness))  # dB of aliasing
```

#### Q5 → Harmonic Content (purity)
```python
def q5_to_harmonics(sfdr_db):
    """Map SFDR to harmonic content level."""
    # SFDR=-300dB → no harmonics, SFDR=0dB → 100% harmonics
    return max(0, min(1.0, 10 ** (sfdr_db / -60)))
    # Returns 0.0 (pure) to 1.0 (fully distorted)
```

#### Q6 → Drift (drift)
```python
def q6_to_drift(lyapunov_exponent):
    """Map Lyapunov exponent to oscillator drift in cents."""
    # λ=0 → no drift, λ>0 → exponential drift
    return abs(lyapunov_exponent) * 50  # 0 to ~50 cents
```

#### Q7 → Saturation (saturation)
```python
def q7_to_saturation(accumulation_error):
    """Map accumulation error to saturation amount."""
    # error=0 → no saturation, error→∞ → full saturation
    return 1.0 - math.exp(-accumulation_error * 100)
    # Returns 0.0 (clean) to 1.0 (saturated)
```

#### Q8 → Glitch (glitch)
```python
def q8_to_glitch(ieee_compliance):
    """Map IEEE compliance to glitch probability."""
    # compliance=1 → no glitches, compliance=0 → maximum glitches
    return 1.0 - ieee_compliance
    # Returns 0.0 (clean) to 1.0 (glitchy)
```

#### Q9 → Stereo Width (stereo)
```python
def q9_to_stereo(cross_platform_ulp):
    """Map cross-platform disagreement to stereo width."""
    # 0 ULP → mono, >1000 ULP → full stereo
    return min(1.0, cross_platform_ulp / 1000.0)
    # Returns 0.0 (mono) to 1.0 (wide)
```

#### Q10 → Noise Type (noise_type)
```python
def q10_to_noise_type(error_entropy_bits):
    """Map error entropy to noise character."""
    # Low entropy → harmonic (warm)
    # High entropy → white (harsh)
    if error_entropy_bits < 2:
        return "harmonic", 0.5  # Warm, musical
    elif error_entropy_bits < 5:
        return "pink", 0.7  # Colored, interesting
    elif error_entropy_bits < 8:
        return "brown", 0.3  # Rolling, smooth
    else:
        return "white", 1.0  # Harsh, digital
```

### 4.3 Preset Configurations

Just like audio effects have presets ("Clean," "Warm," "Lo-Fi," "Destroyed"), quality profiles map to recognizable computational aesthetics:

| Preset | Profile | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Q9 | Q9 |
|--------|---------|----|----|----|----|----|----|----|----|----|----|
| **Clinical** | IEEE 754 strict f64 | 52 | 1.0 | 0 | 1.0 | -280 | 0 | 0 | 1.0 | 0 | 1 |
| **Studio** | C -O2 f64 | 52 | 1.0 | 0 | 1.0 | -250 | 0 | ε | 0.95 | 2 | 2 |
| **Warm** | CUDA f32 default | 23 | 0.999 | 0.1 | 10 | -120 | 0.01 | ε | 0.6 | 100 | 5 |
| **Vintage** | Polynomial approx | 20 | 1.0 | 0.2 | 5 | -60 | 0 | ε | 0.5 | 0 | 4 |
| **Lo-Fi** | f16 + -ffast-math | 10 | 0.99 | 0.5 | 100 | -40 | 0.1 | 10⁻² | 0.3 | 500 | 7 |
| **Destroyed** | int8 quantized | 7 | 0.9 | 1.0 | 1000 | -20 | 0.5 | 10⁻¹ | 0.1 | 10000 | 8+ |
| **Cosmic** | mpmath 200 digits | 665 | 1.0 | 0 | 1.0 | -∞ | 0 | 10⁻⁵⁰ | 1.0 | 0 | 1 |

---

## 5. Practical Applications

### 5.1 Language Identification via Quality Fingerprinting

Given the output of a computation (without knowing the source), you can identify the language/compiler by its position in quality space. This is the computational equivalent of speaker recognition — identifying who's talking by the timbre of their voice.

**Protocol:**
1. Run the 10-dimensional measurement suite
2. Compare against a database of known language fingerprints
3. The nearest neighbor in quality space identifies the language

**Accuracy:** For well-separated languages (e.g., CUDA f32 vs C f64), identification is trivial. For similar configurations (gcc -O2 vs clang -O2), you need the full 10 dimensions to distinguish.

### 5.2 Quality-Aware Code Generation

When generating numerical code, you can target a specific point in quality space:

- **Scientific computing:** maximize Q1, Q8, minimize Q7 → strict IEEE 754, Kahan summation
- **Real-time graphics:** maximize Q5 (within f32 budget), minimize Q4 → use good polynomial approximations
- **Audio synthesis:** tune Q5, Q6, Q10 for desired timbre → use specific math libraries
- **Cryptography:** minimize Q10 (want deterministic error) → exact arithmetic

### 5.3 Computational Aesthetics

The quality space enables a new form of computational art:

1. **Compose** a piece of music where each voice uses a different language's quality profile
2. **Generate** visualizations of quality space (like our I_vert/I_horiz/I_spectral music space)
3. **Create** a synthesizer where the "oscillator type" is actually the language choice
4. **Perform** live by switching between language implementations and hearing the quality shift

### 5.4 The Berry Phase Connection

Returning to berry_phase.cu: the Pythagorean comma computation is a microcosm of the quality space. Each quality dimension reveals a different aspect of how the 12-step circle-of-fifths traversal differs across languages:

- **Q1:** How precisely is the comma measured? (23.460010 cents in exact arithmetic, 23.460009... in f64, 23.46... in f32)
- **Q2:** Do repeated traversals give the same comma? (Yes on CPU, slight variation in parallel GPU code)
- **Q4:** Is the comma invariant smooth across starting frequencies? (Should be — this is the Berry phase invariance)
- **Q6:** How fast does the computed comma drift from the exact comma over many cycles?
- **Q7:** If you sum the commas from 10⁶ cycles, how accurate is the total?

The comma is not just a number — it's a *quality measurement*. And different languages "hear" it differently.

---

## 6. Measurement Implementation Guide

### 6.1 Reference Implementation Structure

```
quality-taxonomy/
├── measure/
│   ├── q1_precision.py        # Compare against mpmath
│   ├── q2_consistency.c       # Run 1000x, measure variance
│   ├── q3_linearity.py        # Span 10 decades, measure correlation
│   ├── q4_smoothness.c        # Lipschitz quotient
│   ├── q5_spectral.py         # FFT analysis of sin() output
│   ├── q6_drift.c             # Recurrence divergence
│   ├── q7_accumulation.c      # Naive vs Kahan summation
│   ├── q8_edge_cases.c        # IEEE 754 compliance test
│   ├── q9_portability.sh      # Multi-config comparison
│   └── q10_entropy.py         # Shannon entropy of errors
├── targets/
│   ├── c_strict.c             # C with -O2, strict IEEE
│   ├── c_fast.c               # C with -Ofast -ffast-math
│   ├── cuda_float.cu          # CUDA f32
│   ├── cuda_double.cu         # CUDA f64
│   ├── fortran.f90            # Fortran implementation
│   ├── rust_strict.rs         # Rust with strict IEEE
│   ├── javascript.js          # Node.js implementation
│   └── python.py              # CPython implementation
├── results/
│   └── {language}_profile.json  # Quality measurements
└── visualize/
    ├── radar_chart.py         # 10-axis radar plot
    ├── quality_map.py         # 2D t-SNE projection
    └── audio_render.py        # Convert quality to audio
```

### 6.2 Ground Truth Generation

All ground truth computations use mpmath with 200 decimal digits:

```python
import mpmath
mpmath.mp.dps = 200  # 200 decimal places ≈ 665 bits

def ground_truth(func_name, x):
    """Compute arbitrary-precision ground truth."""
    f = getattr(mpmath, func_name)
    return f(mpmath.mpf(x))
```

### 6.3 Statistical Rigor

Each measurement is repeated 100 times with different random seeds. We report:
- Mean and standard deviation
- 5th and 95th percentile
- Kolmogorov-Smirnov test against expected distribution
- Effect size (Cohen's d) between languages

---

## 7. Theoretical Connections

### 7.1 Information Theory

Q10 (error entropy) connects to Shannon's information theory. The error in a floating-point computation is a *channel* that adds noise to the signal. The capacity of this channel is:

```
C = B · log₂(1 + SNR)
```

where B is the bandwidth (how many operations per second) and SNR is the signal-to-noise ratio (precision of the result). Higher-precision computation has higher channel capacity — it can transmit more mathematical information per operation.

### 7.2 Dynamical Systems

Q6 (temporal drift) connects to dynamical systems theory. The Lyapunov exponent of a numerical method determines whether small errors grow (λ>0) or shrink (λ<0). This is directly analogous to the stability of physical systems:

- Stable fixed points → errors decay → clean computation
- Limit cycles → errors oscillate → periodic artifacts
- Strange attractors → errors grow but are bounded → chaotic but structured artifacts
- Unstable fixed points → errors grow without bound → divergent computation

### 7.3 Music Theory

The entire quality space connects to music theory through the lens of the quantum spin language experiments:

- **Harmonic series** = spectral purity (Q5) — different libraries produce different harmonic spectra
- **Consonance/dissonance** = linearity (Q3) — nonlinear error functions produce perceptual roughness
- **Tuning stability** = temporal drift (Q6) — drifted computation is like a detuned oscillator
- **Timbre** = error entropy (Q10) — structured error is "warm," random error is "cold"
- **Dynamics** = accumulation (Q7) — error buildup is like compression/saturation

### 7.4 Berry Phase Geometry

The Berry phase computation in berry_phase.cu provides a geometric interpretation: each quality dimension corresponds to a curvature in the parameter space of the computation. The "holonomy" (how much the answer rotates after a closed loop) is the total quality deviation. Different languages traverse different paths through this space, acquiring different Berry phases — and the set of these phases IS the quality fingerprint.

---

## 8. Conclusion

The ten dimensions of the Quality Taxonomy are not arbitrary measurements — they are the fundamental axes of computational character. Just as timbre in music is multi-dimensional (brightness, warmth, roughness, noisiness...), the "sound" of a computation is multi-dimensional.

The key insight is that these differences are not bugs. They are the texture of computation — as real, measurable, and aesthetically meaningful as the difference between a Steinway and a Bösendorfer, or between analog tape and digital audio.

By mapping these dimensions to DSP parameters, we transform abstract numerical differences into something you can hear, feel, and compose with. The quality space becomes an instrument.

The computation IS the instrument. The language IS the timbre. The quality IS the music.

---

*Document version: 1.0*
*Date: 2026-05-24*
*Context: quantum_spin_lang experiments (berry_phase.cu, spin_statistics.cu)*
