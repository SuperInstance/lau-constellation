# Retro Sunset Plato Extraction Summary

**Date:** 2026-05-28
**Source:** `forgemaster` branch `retro-sunset-plato` (1,332 files)
**Action:** Extracted three standalone repos with real code and documentation

---

## 1. analog-spline-theory
**Repo:** [SuperInstance/analog-spline-theory](https://github.com/SuperInstance/analog-spline-theory)
**Commit:** `798126a` — Added 7 files (712 lines) on top of existing content

### What was added
| File | Description |
|------|-------------|
| `galois-connection-proof.md` | Standalone Galois connection proof (110 lines) |
| `galois-connection-proof-deepseek.md` | DeepSeek's formal proof of the Galois adjunction |
| `flux_galois_coq.v` | Coq formalization of the Galois connection (115 lines) |
| `galois-unification-visualizer.py` | Python visualizer for Galois unification (193 lines) |
| `SPLINE-PHYSICS-SYNERGY.md` | Connections between spline theory and physics (137 lines) |
| `HPDF-PPDF-SPLINE-RETRIEVAL.md` | HPDF/PPDF spline retrieval analysis (147 lines) |

### Key math
- **Shipwright's Theorem**: Physical batten ↔ computational Bézier curve equivalence (δ/20 error bound)
- **Galois Connection**: Categorical adjunction between constraint lattice and curve lattice
- **O(h⁴) convergence**: Quartic convergence rate for uniform pin spacing

---

## 2. eisenstein-triples
**Repo:** [SuperInstance/eisenstein-triples](https://github.com/SuperInstance/eisenstein-triples)
**Commit:** `aa8259d` — Initial release with 7 files (2,148 lines)

### Contents
| File | Description |
|------|-------------|
| `eisenstein_triples.py` | Core library: generation, D₆ orbit, primitivity testing |
| `analyze.py` | Statistical analysis: Eisenstein vs Pythagorean distributions |
| `verify_proofs.py` | Verification of mathematical claims about Z[ω] |
| `verify_eisenstein_snap_falsification.py` | Falsification tests for snap-lattice alignment |
| `eisenstein-prime-norms.md` | Eisenstein prime norm factorization analysis |
| `EISENSTEIN-VS-Z2-BENCHMARK.md` | Z[ω] vs Z² benchmark comparison |

### Key math
- **Eisenstein norm**: a² − ab + b² = c², the hexagonal Pythagorean analog
- **D₆ Weyl orbit**: 12-element symmetry group (6 rotations × conjugation)
- **Parametric form**: m > n > 0, gcd(m,n)=1, 3 ∤ (m−n)

---

## 3. constraint-instrument
**Repo:** [SuperInstance/constraint-instrument](https://github.com/SuperInstance/constraint-instrument)
**Commit:** `79e7917` — Added 22 files (8,413 lines) to existing repo

### What was added
**10 new Python modules:**
`genre_brain.py`, `chords.py`, `texture.py`, `liner_notes.py`, `exercises.py`, `nomenclature.py`, `terrain_morph.py`, `seed_manager.py`, `analyzer.py`, `tracks.py`

**Documentation & site:**
- `docs/INVISIBLE-ENGINEER.md` — "The Invisible Engineer" design essay (monitor engineering metaphor)
- `docs/NOMENCLATURE.md` — Musical nomenclature reference (1,011 lines)
- `docs/USER-REPORTS/` — 4 practitioner reports (jazz, hip-hop, electronic, math education)
- `site/` — Web playground (index.html, playground.html, audio demo)

**1 new example:** `demo_terrain_morph.py`

### Total repo size after extraction
- 54 Python source files
- 17 terrains, 7 modes
- Web playground with audio demos
- Full documentation suite

---

## Tags Applied

| Repo | Topics |
|------|--------|
| analog-spline-theory | `spline-theory`, `galois-connection`, `formal-proofs`, `shipwright-theorem`, `bezier-curves`, `euler-bernoulli`, `mathematical-proofs`, `conservation-spectral` |
| eisenstein-triples | `eisenstein-integers`, `number-theory`, `hexagonal-lattice`, `d6-symmetry`, `weyl-group`, `pythagorean-triples`, `conservation-spectral` |
| constraint-instrument | `constraint-music`, `jazz`, `generative-music`, `bathymetric-terrain`, `monitor-engineering`, `conservation-spectral`, `web-audio`, `midi` |
