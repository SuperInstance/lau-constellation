-- lakefile.lean — Lean 4 project for Quantum Spin-Music proofs
--
-- Build:
--   lake build
--
-- Note: Requires Lean 4 and Lake. If not installed, the .lean files
-- are valid Lean 4 source and can be verified with:
--   lake env lean BerryPhase.lean
--   lake env lean SpinStatistics.lean
--   lake env lean Entanglement.lean

import Lake
open Lake DSL

package quantumSpinLang where
  leanOptions := #[⟨`autoImplicit, false⟩]

@[default_target]
lean_lib QuantumSpinLang where
  roots := #[`BerryPhase, `SpinStatistics, `Entanglement]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "master"
