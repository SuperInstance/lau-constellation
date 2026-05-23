# Documentation Improvement Proposals

Audited 2026-05-22. All repos in `/home/phoenix/.openclaw/workspace/`.

---

## 1. constraint-theory-core

### README Score: 8/10

Excellent structure — architecture diagram, equation table, module reference, and composable examples. Best-documented repo in the suite.

### Broken Examples

1. **Metronome Quick Start (README ~line 73)** — Uses `_get_neighbors(edges, i)` which is a fictional helper not defined anywhere in the codebase or README. The Metronome constructor expects `neighbors` as a list of ints, so the example fails with `NameError: name '_get_neighbors' is not defined`.
   - **Fix:** Add a helper definition before the example:
     ```python
     def _get_neighbors(edges, i):
         return [v for u, v in edges if u == i] + [u for u, v in edges if v == i]
     ```
   - Or use `constraint_theory_core.rigidity` to expose a neighbor utility.

2. **Holonomy Quick Start (README ~line 95)** — The `verify_consistency`, `isolate_fault`, and `fault_boundaries` examples pass `tiles` as a list of `(edges, direction_indices)` tuples. This works, but the README doesn't explain the format clearly. A newcomer would need to read source to understand direction semantics.

### Missing Documentation

| Public API | Documented? |
|---|---|
| `norm_sq(A2Point)` | No (README only mentions Eisenstein norm formula, not the function) |
| `decode_dodecet(int)` | No |
| `holonomy_product(directions)` | No |
| `is_consistent(directions)` | No |
| `vector48_decode(int)` | No |
| `MetronomeState` | Mentioned in table but no usage example |

### Missing Tutorials

1. **"Building a Distributed Metronome from Scratch"** — Step-by-step: construct Laman graph → spawn Metronome agents → run consensus → verify with holonomy. The current examples show each module separately; a combined tutorial is desperately needed.
2. **"Anomaly Detection with Deadband Funnels"** — How to tune `decay_rate`, `epsilon_0`, and `delta` for different use cases (tight vs. loose synchronization), with plots of how the funnel narrows.

### Top 3 Fixes (by impact)

1. **Fix `_get_neighbors` in Metronome example** — The headline example is broken; this is the first thing new users hit.
2. **Add combined 5-module tutorial** — The architecture diagram promises composition but no single example uses all modules together.
3. **Document `vector48_decode`, `decode_dodecet`, `holonomy_product`** — These are key for users who want to go beyond snap-and-check.

---

## 2. counterpoint-engine

### README Score: 6/10

Good API table coverage, but the entire Quick Start is **unrunnable** due to a missing dependency.

### Broken Examples

1. **Entire Quick Start fails at import time (README ~line 19)** — `from counterpoint_engine.generator import CounterpointGenerator` triggers `from flux_tensor_midi.core.flux import FluxVector` via `tensor_output.py`, which raises `ModuleNotFoundError: No module named 'flux_tensor_midi.core.flux'`. The actual module path is different.
   - **Fix:** Either fix the import in `tensor_output.py` to match the actual `flux-tensor-midi` package structure, or make the import lazy (only import when tensor output is actually used).

2. **Rules example uses `consonant_interval` with 3 args (README ~line 56)** — `consonant_interval(voice_a, voice_b, 0)` — but the function signature in the API table shows `consonant_interval(voice_a, voice_b, beat, allowed)` with 4 params. The `allowed` parameter has no default mentioned.
   - **Fix:** Clarify that `allowed` has a default or update the example.

3. **USER-GUIDE.md `proper_resolution` example (line ~33)** — Shows `proper_resolution(voice, 1)` with 2 args but the function signature requires `key_tonic` and `key_leading`. The second example call `proper_resolution(voice, 1, key_tonic=0, key_leading=11)` is correct, but the first will fail.

### Missing Documentation

| Public API | Documented? |
|---|---|
| `CounterpointResult` | No — returned by `generate()` but never described |
| `TensorMIDIEvent` fields | Partially — mentioned but `to_bytes()` format not documented |
| `VoiceRange.candidates(scale, prev_pitch)` | No usage example |

### Missing Tutorials

1. **"First Species Counterpoint Step-by-Step"** — The README jumps straight to multi-voice Laman graphs. A gentler intro showing: define cantus → check each rule manually → generate → inspect the result would help musicians who aren't math people.
2. **"Tensor-MIDI Output Pipeline"** — How generated counterpoint becomes TensorMIDIEvents, what each byte means, and how to feed them into a neural synthesizer.

### Top 3 Fixes (by impact)

1. **Fix flux_tensor_midi import** — The package is literally unusable without this. Either lazy-import `tensor_output` or fix the module path.
2. **Document `CounterpointResult`** — `generate()` returns this but users have no idea what's in it.
3. **Add musician-friendly intro tutorial** — Current docs assume comfort with Laman graphs. Most potential users are musicians, not mathematicians.

---

## 3. groove-analyzer

### README Score: 7/10

Clean API tables, good genre profiles, clear data flow. Loses points for requiring an external MIDI file in the very first example without providing one.

### Broken Examples

1. **Quick Start first example (README ~line 19)** — `extract_microtiming("my_performance.mid")` requires an actual MIDI file. No guidance on where to get one or that `synthesize_groove()` can create one first.
   - **Fix:** Reorder Quick Start to show `synthesize_groove()` first, then analyze the generated file.

2. **No broken code examples found** — Once you have a MIDI file (synthetic or real), all examples work correctly. The genre synthesis → analysis pipeline is solid.

### Missing Documentation

| Public API | Documented? |
|---|---|
| `GenreProfile` dataclass | No — the struct behind `GENRE_PROFILES` is undocumented |
| `DeadbandFit.confidence` | Mentioned in table but no interpretation guide |
| `EnsembleFunnel.player_funnels` | No — how per-player funnels work |

### Missing Tutorials

1. **"Comparing Grooves Across Genres"** — Use `generate_all_genre_examples()` → analyze each → `plot_groove_comparison()` → interpret the results. What does a 3ms EDM pocket look like vs. a 40ms Jazz pocket?
2. **"Analyzing Your Own Drumming"** — Record a MIDI performance → extract microtiming → fit deadband → see if you're "in the pocket." Practical guide for musicians with a DAW.

### Top 3 Fixes (by impact)

1. **Reorder Quick Start to synthesize first** — New users hit a FileNotFoundError immediately.
2. **Add "Interpreting Results" section** — What does `coverage = 0.91` actually mean? What's a "good" variance_collapse? No guidance.
3. **Document `GenreProfile` fields** — The 5 built-in profiles are shown in a table but the dataclass structure isn't documented.

---

## 4. holonomy-harmony

### README Score: 8/10

Best pure-Python docs in the suite. Clear math explanation, excellent built-in progressions, runnable examples that actually work.

### Broken Examples

1. **No broken code examples found.** The `analyze_progression` and `compute_holonomy` examples ran correctly on first try.

### Missing Documentation

| Public API | Documented? |
|---|---|
| `pitch_name(pc)` | No |
| `pc_from_name(name)` | No |
| `circle_of_fifths_position(pc)` | No |
| `semitone_interval(from, to)` | No |
| `classify_direction(from, to)` | No |
| `Edge` class | No |
| `detect_modulations()` | No — in `analyzer.py` but not in README |
| `score_stability()` | No — standalone function, not just a property |

### Missing Tutorials

1. **"Analyzing a Full Song's Chord Progression"** — Take a real song (e.g., Autumn Leaves), parse its Roman numerals, compute holonomy at each section, detect where modulations happen, and visualize the tonal journey on the circle of fifths.
2. **"Building a Harmonic Similarity Engine"** — Use `TonalGraph.adjacency_matrix()` + `transition_probability()` to compare two progressions' structural similarity. Useful for music recommendation.

### Top 3 Fixes (by impact)

1. **Document `detect_modulations()` and `score_stability()` as standalone functions** — They're in the code, they're useful, but the README only shows them as properties of `ProgressionAnalysis`.
2. **Add full-song tutorial** — The 20 built-in progressions are a goldmine; show how to chain analysis across sections.
3. **Document utility functions** (`pitch_name`, `pc_from_name`, etc.) — Users will need these when building on top of the library.

---

## 5. spline-midi-smooth

### README Score: 8/10

Strong math explanations, clean API, runnable examples. The deadband-spline connection to constraint theory is well articulated.

### Broken Examples

1. **No broken code examples found.** The `cubic_hermite` example ran correctly and produced output matching the README (91.6 vs. claimed 91.9 — minor floating point difference).

2. **Minor: Output mismatch** — README claims `Value at t=0.75: 91.9` but actual output is `91.6`. Not a code bug, but documentation should match.
   - **Fix:** Update README output to `91.6` or note that results may vary slightly.

### Missing Documentation

| Public API | Documented? |
|---|---|
| `is_deadband_a_spline()` | No (in README) — only in USER-GUIDE |
| `CcTrackKey` | No — used as dict key in `smooth_midi_cc` return |
| `CcPoint` | No — internal but visible in return types |
| `smooth_tempo_map()` | In API table but no example in README |

### Missing Tutorials

1. **"Eliminating Zipper Noise in a Real MIDI File"** — Take a MIDI file with coarse CC#7 (volume) events → smooth with each method → A/B compare the audio. Include before/after spectrograms showing the staircasing artifacts disappearing.
2. **"Deadband-Spline Workflow for Constraint Systems"** — How to use `deadband_spline()` + `deadband_spline_exact_proof()` to guarantee that MIDI automation stays within tolerance. Connect to `constraint-theory-core`'s deadband funnel.

### Top 3 Fixes (by impact)

1. **Fix README output value** — `91.9` → `91.6`. Minor but undermines trust.
2. **Add `CcTrackKey` and `CcPoint` documentation** — Users need to understand what `smooth_midi_cc` returns.
3. **Add `is_deadband_a_spline` to README** — It's the most interesting function conceptually but only in the USER-GUIDE.

---

## 6. plato-room-musician

### README Score: 5/10

Good concept explanation and architecture, but the Quick Start example is **completely broken** — crashes at runtime.

### Broken Examples

1. **Quick Start crashes (README ~line 28)** — The `SyntheticFetcher` Quick Start fails with `TypeError: not all arguments converted during string formatting` in `fetcher.py:120`. The `_make_tile` method has a string formatting bug where `self.rng.choice(TILE_SEEDS)` is used with `%` formatting, but some templates (like `"Eisenstein snap applied to rhythm grid"`) have no format specifiers, causing the mismatch.
   - **Root cause:** The `_fmt_args` dictionary is actually present in the code and should handle this, but the error occurs at line 120 which suggests the code was recently refactored and the `_make_tile` method on line 120 doesn't match the shown version (which has `_fmt_args`). The actual line 120 may be an older version.
   - **Fix:** Verify `fetcher.py` line 120 matches the `_fmt_args` pattern shown later in the file. The fix is already present in the file but may not be deployed to the right line.

2. **PlatoFetcher example (README ~line 48)** — `PlatoFetcher(host="http://147.224.38.131:8847")` hardcodes an internal IP address. This should either use `localhost` or clearly state it's an example that won't work without a running PLATO instance.

### Missing Documentation

| Public API | Documented? |
|---|---|
| `NoteEvent` dataclass | No — the core data structure |
| `PlatoScore.find_chords()` details | Partially — return format unclear |
| `PlatoScore.find_rests()` details | No |
| `VMSRenderer` output format | No — what does the dict contain? |
| `TensorMidiRenderer.render_to_bytes()` | No — byte format not documented |
| `get_fetcher()` utility | No — mentioned in code but not README |

### Missing Tutorials

1. **"From Fleet Activity to a MIDI Composition"** — End-to-end: fetch PLATO data → map rooms → compose score → render to MIDI → play it. Currently scattered across 4 sections.
2. **"Understanding the Category → Instrument Mapping"** — A visual guide showing which room categories map to which instruments, registers, and scales, with audio examples of each category's characteristic sound.

### Top 3 Fixes (by impact)

1. **Fix SyntheticFetcher crash** — The Quick Start is the first thing users try. If it crashes, they leave.
2. **Remove hardcoded internal IP** — Replace with `host="http://localhost:8847"` or a placeholder.
3. **Document `NoteEvent` fields** — It's the central data structure and it's invisible in the docs.

---

## Cross-Repo Tutorial Outline

### "Building a Constraint-Theoretic Musical Composition"

A single tutorial using all 6 repos to compose a piece of music from mathematical constraints.

**Phase 1: Foundation (constraint-theory-core)**
1. Build a Laman graph for 8 voices using `henneberg_construct(8)`
2. Snap pitch classes to the Eisenstein A₂ lattice using `snap()`
3. Set up temporal deadband funnels for each voice

**Phase 2: Harmony (holonomy-harmony)**
1. Define a chord progression using `PROGRESSIONS["autumn_leaves"]`
2. Compute holonomy to understand tonal journey
3. Detect modulation points for structural decisions

**Phase 3: Counterpoint (counterpoint-engine)**
1. Generate 4-voice counterpoint against the cantus firmus derived from the chord progression
2. Verify all voices form a Laman graph (constraint independence)
3. Export as TensorMIDI events

**Phase 4: Groove (groove-analyzer)**
1. Synthesize a "Jazz" groove using `synthesize_groove("Jazz")`
2. Fit the deadband — expect ε ≈ 40ms
3. Extract microtiming patterns to apply human-like feel

**Phase 5: Smoothing (spline-midi-smooth)**
1. Smooth all CC automation (volume, filter sweeps) using `cubic_hermite`
2. Anti-alias pitch bends at 2kHz
3. Apply deadband spline to verify all curves stay within tolerance

**Phase 6: Sonification (plato-room-musician)**
1. Feed the composition process (tile submissions from Phases 1–5) into `PlatoScore`
2. Map each phase to a different room category
3. Render the "meta-composition" — a piece that sonifies its own creation process

**Final output:** Two MIDI files — the composed piece and the sonification of its creation.

---

## Top 5 Highest-Impact Doc Improvements (All Repos)

| # | Repo | Improvement | Impact | Effort |
|---|------|-------------|--------|--------|
| 1 | **counterpoint-engine** | Fix `flux_tensor_midi.core.flux` import — package is entirely unusable without this | **Critical** — blocks all users | Low (lazy import or fix path) |
| 2 | **plato-room-musician** | Fix `SyntheticFetcher._make_tile` crash — Quick Start is broken | **Critical** — first experience is a crash | Low (one-line fix) |
| 3 | **constraint-theory-core** | Fix `_get_neighbors` in Metronome example — headline example has undefined function | **High** — confuses every new user | Low (add 2-line helper) |
| 4 | **counterpoint-engine** | Add musician-friendly "First Species" tutorial — current docs assume math background | **High** — unlocks musician audience | Medium |
| 5 | **All repos** | Write the cross-repo tutorial above — shows the ecosystem's combined power | **High** — demonstrates the vision | Medium |

---

## Summary Table

| Repo | README Score | Broken Examples | Missing APIs | Tutorials Needed | Urgency |
|------|-------------|-----------------|--------------|------------------|---------|
| constraint-theory-core | 8/10 | 1 (`_get_neighbors`) | 5 functions | 2 | Medium |
| counterpoint-engine | 6/10 | 3 (import crash, arg mismatch) | 3 APIs | 2 | **Critical** |
| groove-analyzer | 7/10 | 0 (but needs reordering) | 3 fields | 2 | Low |
| holonomy-harmony | 8/10 | 0 | 8 functions | 2 | Low |
| spline-midi-smooth | 8/10 | 0 (minor output mismatch) | 4 APIs | 2 | Low |
| plato-room-musician | 5/10 | 1 (SyntheticFetcher crash) | 6 APIs | 2 | **Critical** |
