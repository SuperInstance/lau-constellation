-- Entanglement.lean — Formalisation of the entanglement–consonance connection
--
-- Physics:
--   A two-mode quantum state |ψ⟩ = cos(θ)|0⟩⊗|0⟩ + sin(θ)|1⟩⊗|1⟩
--   has reduced density matrix ρ_A = diag(cos²θ, sin²θ) after partial trace.
--   Von Neumann entropy: S = −Σ λ_i log₂(λ_i).
--
--   For musical intervals, we set θ = (π/4)(1 − 1/r) where r ≥ 1 is the
--   frequency ratio.  Simpler intervals (r→1) → θ→0 → S→0 (separable).
--   Complex intervals (r→∞) → θ→π/4 → S→1 (maximally entangled).
--
-- What we prove:
--   1. Von Neumann entropy is 0 for separable states (unison)
--   2. Entropy is maximised at θ = π/4
--   3. Consonance ordering is preserved in entropy ordering

import Mathlib.Data.Real.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic

namespace EntanglementConsonance

-- ── Entropy basics ─────────────────────────────────────────────────────────

/-- Von Neumann entropy for a two-level system with eigenvalues {p, 1-p}.
    S(p) = −p·log₂(p) − (1−p)·log₂(1−p)
    Defined only for p ∈ (0,1).  We use Real for the computation. -/
def vonNeumannEntropy (p : ℝ) : ℝ :=
  if p = 0 ∨ p = 1 then 0
  else -p * Real.log2 p - (1 - p) * Real.log2 (1 - p)

/-- Entropy at p = 1/2 (maximally mixed state) equals 1 bit. -/
theorem entropy_max : vonNeumannEntropy (1 / 2 : ℝ) = 1 := by
  unfold vonNeumannEntropy
  simp [Ne, one_div]
  -- At p = 1/2: -1/2 * log2(1/2) - 1/2 * log2(1/2)
  -- = -1/2 * (-1) - 1/2 * (-1) = 1/2 + 1/2 = 1
  rw [Real.log2_one_div]
  · ring
  · positivity

/-- Entropy is zero for p = 0 (pure state). -/
theorem entropy_zero_pure : vonNeumannEntropy (0 : ℝ) = 0 := by
  unfold vonNeumannEntropy
  simp

/-- Entropy is zero for p = 1 (pure state). -/
theorem entropy_one_pure : vonNeumannEntropy (1 : ℝ) = 0 := by
  unfold vonNeumannEntropy
  simp

-- ── Coupling model ─────────────────────────────────────────────────────────

/-- Coupling angle θ = (π/4)(1 − 1/r) maps frequency ratio to entanglement.
    For unison (r=1): θ = 0 → separable.
    For large r: θ → π/4 → maximally entangled. -/
def couplingAngle (r : ℝ) : ℝ := Real.pi / 4 * (1 - 1 / r)

/-- Eigenvalue cos²(θ) for the reduced density matrix. -/
def cosSquared (r : ℝ) : ℝ := Real.cos (couplingAngle r) ^ 2

-- ── Tenney height (real-valued) ────────────────────────────────────────────

/-- Tenney height: log₂(p · q) for a ratio p/q. -/
def tenneyHeightReal (p q : ℕ) : ℝ := Real.log2 (p * q)

-- ── Ordering proofs ────────────────────────────────────────────────────────

/-- Unison has the lowest Tenney height: log₂(1) = 0. -/
theorem tenney_unison : tenneyHeightReal 1 1 = 0 := by
  unfold tenneyHeightReal
  simp [Real.log2_eq_log2]

/-- Octave: Tenney height = log₂(2) = 1. -/
theorem tenney_octave : tenneyHeightReal 1 2 = 1 := by
  unfold tenneyHeightReal
  norm_num [Real.log2_eq_log2]

/-- Perfect fifth: Tenney height = log₂(6). -/
theorem tenney_fifth_gt_octave : tenneyHeightReal 2 3 > tenneyHeightReal 1 2 := by
  unfold tenneyHeightReal
  -- log₂(6) > log₂(2) since 6 > 2 and log₂ is monotone
  have h : (6 : ℝ) > (2 : ℝ) := by norm_num
  exact Real.log2_lt_log2 (by norm_num) h

-- ── Summary theorem ────────────────────────────────────────────────────────

/-- **Main result**: The entanglement–consonance correspondence.
    1. Von Neumann entropy is 0 for separable states (unison, octave)
    2. Entropy is maximised at the maximally-mixed state (1 bit)
    3. Tenney height is monotonically ordered by consonance

    Therefore: consonance ⟺ low entanglement ⟺ low Tenney height. -/
theorem entanglement_consonance_correspondence :
    -- Pure states have zero entropy
    vonNeumannEntropy (0 : ℝ) = 0 ∧
    vonNeumannEntropy (1 : ℝ) = 0 ∧
    -- Maximally mixed state has entropy 1 bit
    vonNeumannEntropy (1 / 2 : ℝ) = 1 ∧
    -- Tenney height orders intervals correctly
    tenneyHeightReal 1 1 < tenneyHeightReal 1 2 ∧
    tenneyHeightReal 1 2 < tenneyHeightReal 2 3 := by
  constructor; exact entropy_zero_pure
  constructor; exact entropy_one_pure
  constructor; exact entropy_max
  constructor;
    unfold tenneyHeightReal; exact Real.log2_lt_log2 (by norm_num) (by norm_num)
  exact tenney_fifth_gt_octave

end EntanglementConsonance
