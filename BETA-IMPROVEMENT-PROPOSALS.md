# Beta Test Improvement Proposals

**Date:** 2026-05-22  
**Tester:** Professional music technology developer evaluating for DAW plugin integration  
**Pipeline tested:** Counterpoint → Harmony → Groove → Spline smoothing → MIDI render

---

## Pipeline Test Results Summary

| Step | Module | Status | Notes |
|------|--------|--------|-------|
| 1 | counterpoint-engine | ✅ OK | 4-voice counterpoint generated in ~2s. API was discoverable. |
| 2 | holonomy-harmony | ⚠️ Minor issue | `HolonomyResult` has `.progression_type` not `.classification` — inconsistent naming with docs |
| 3 | groove-analyzer | ✅ OK | Funk groove generated, deadband fit correctly identified genre. |
| 4 | spline-midi-smooth | ⚠️ Minor issue | `smooth_velocity_curve()` requires `(input_path, output_path)` but the name suggests in-memory operation. No pure-data API. |
| 5 | MIDI render | ✅ OK | Standard mido-based render worked. 32 notes across 4 voices. |

**Critical finding:** The pipeline works but the repos feel like 6 separate libraries, not one integrated system. Data must be manually converted between formats at each step.

---

## 1. constraint-theory-core

### Top 3 Improvements

#### 1.1 Add a `MusicalQuantizer` convenience class
- **What:** A high-level class that wraps `snap()`, `is_safe()`, and `covering_radius()` into a musically-aware quantizer. Input: float pitch/frequency. Output: quantized MIDI note + error bound.
- **Why:** The raw A₂ lattice API is mathematically elegant but requires users to understand Eisenstein lattice theory just to quantize a pitch. Real users need `quantizer.snap_pitch(440.2) → (A4, safe)`.
- **Effort:** Medium — needs pitch-to-lattice mapping layer
- **Reference:** `music21.pitch.Pitch` provides seamless pitch <-> frequency <-> MIDI conversion. We should match that ergonomics level.

#### 1.2 Expose `TemporalmusicAgent` with beat/bar awareness
- **What:** Extend `TemporalAgent` and `FunnelResult` with musical time units (beats, bars) instead of abstract phase/time. Add `FunnelPhase` mappings like `NARROWING = "in_pocket"`, `APPROACH = "drifting"`, `ANOMALY = "out_of_time"`.
- **Why:** The temporal funnel theory is the theoretical backbone, but the naming is pure math. DAW plugin developers need musical semantics.
- **Effort:** Easy — thin wrapper with renaming
- **Reference:** Ableton Live's groove pool uses similar timing deviation thresholds but with musical UI labels.

#### 1.3 Add serialization (JSON/MessagePack) for all core types
- **What:** `A2Point.to_dict()`, `FunnelResult.to_json()`, `MetronomeState.serialize()`. Round-trippable.
- **Why:** Any DAW plugin needs to pass data between processes (plugin ↔ host). Currently every consumer has to write their own serialization. This is table stakes for real-time audio work.
- **Effort:** Easy — dataclass fields are all primitive
- **Reference:** `pretty_midi` has `PrettyMIDI.write()` and loads from both files and bytes. `mido` has `MidiFile.save()`.

---

## 2. counterpoint-engine

### Top 3 Improvements

#### 2.1 Export to standard MIDI directly (no mido dependency chain)
- **What:** Add `CounterpointGenerator.to_midi(path, bpm=120, program=0)` that returns or saves a `mido.MidiFile`. Also `to_midi_bytes() → bytes`.
- **Why:** Step 5 of the pipeline required 40+ lines of manual MIDI construction. Every user will need this. The engine already knows voices, beats, and pitches — it should own the output.
- **Effort:** Easy — mido is already a transitive dependency
- **Reference:** `music21` has `stream.write("midi", fp=path)` — one-liner output. `pretty_midi` has `PrettyMIDI.write(path)`.

#### 2.2 Add rhythmic variation (species 2-5 actually work)
- **What:** Implement `Species.SECOND` through `Species.FIFTH` generation. Currently only `FIRST` (note-against-note) produces correct output. The enum exists but the generator doesn't use species in its logic.
- **Why:** Real music isn't all whole notes. Species counterpoint with rhythmic variation is what composers actually use. Without this, the engine is a proof-of-concept, not a tool.
- **Effort:** Hard — requires significant new backtracking logic for subdivisions, suspensions, and florid motion
- **Reference:** `music21`'s `speciesCounterpoint` module handles all 5 species. The `counterpoint` GitHub project (davidhfriedman/counterpoint) implements Fuxian rules for species 1-4.

#### 2.3 Performance: add constraint propagation / arc consistency
- **What:** Replace brute-force backtracking with forward-checking or MAC (Maintaining Arc Consistency). The current `_check_all` evaluates every constraint on every candidate pitch.
- **Why:** 4-voice generation with 8 notes took ~2s. For 16+ notes or 6+ voices, this will be too slow for interactive use in a DAW. Real-time counterpoint suggestion requires <100ms.
- **Effort:** Medium — standard CSP optimization
- **Reference:** The CS literature on CSP solvers (MAC, forward checking) is mature. `python-constraint` library implements these. music21's counterpoint module uses similar optimization.

---

## 3. groove-analyzer

### Top 3 Improvements

#### 3.1 Apply groove to existing MIDI (not just analyze)
- **What:** Add `apply_groove(midi_path, genre, output_path)` that takes a quantized MIDI file and injects microtiming offsets from a genre profile. Also `extract_groove(midi_path) → GrooveProfile` that captures the timing DNA of a performance.
- **Why:** The analyzer can generate and analyze grooves but can't *apply* a groove to user-provided MIDI. This is the #1 use case for groove tools: "make my stiff MIDI feel funky." The `synthesize_groove()` function creates from scratch, but real users have existing material.
- **Effort:** Medium — read MIDI, compute deviations, apply offsets, write back
- **Reference:** Ableton's groove pool, Reaper's "Humanize" function. GrooveToolbox (fredbru/GrooveToolbox) extracts groove features but also doesn't apply them — this is a gap we could fill.

#### 3.2 Add `analyze_groove_from_events()` for in-memory data
- **What:** Accept a list of `(beat, pitch, velocity)` tuples or a `mido.MidiFile` object directly, not just a file path. Currently `extract_microtiming()` requires a file on disk.
- **Why:** In a DAW plugin, MIDI data is in memory. Writing to disk and re-reading is a dealbreaker for latency-sensitive workflows.
- **Effort:** Easy — refactor internal API to accept both paths and objects
- **Reference:** `pretty_midi.PrettyMIDI(midi_file=mido.MidiFile())` accepts in-memory objects.

#### 3.3 Velocity groove profiles (not just timing)
- **What:** Add velocity contour profiles to `GenreProfile`. Funk has specific accent patterns (strong 1, ghost notes on 16ths). Jazz ride cymbal has specific velocity shapes. Add `velocity_pattern: List[float]` per genre.
- **Why:** Groove is timing AND dynamics. Current profiles have `velocity_mean` and `velocity_std` but no pattern — just random gaussians. Real funk isn't random velocity; it's very specific accent placement.
- **Effort:** Medium — research + implement accent patterns per genre
- **Reference:** The Groove MIDI Dataset (Google Magenta) includes per-instrument velocity patterns. GrooveToolbox computes "velocity features" including syncopation-weighted velocity.

---

## 4. holonomy-harmony

### Top 3 Improvements

#### 4.1 Analyze from MIDI pitches directly (not just Roman numerals)
- **What:** Add `analyze_from_pitches(pitches_per_beat, key_tonic=0, mode="major")` that accepts MIDI note arrays and auto-detects chords before analyzing. Also `detect_key(notes) -> (tonic, mode)`.
- **Why:** Currently requires pre-parsed Roman numeral strings. In the pipeline test, I had to manually convert counterpoint output to Roman numerals. This is a showstopper for integration — the counterpoint engine outputs MIDI pitches, not chord symbols.
- **Effort:** Medium — chord detection from pitch sets, then key detection (Krumhansl-Schmuckler or similar)
- **Reference:** `music21` has `chordify()` + `roman.romanNumeralFromChord()`. `chordparser` auto-detects chords from note sets. `music-harmony-analysis` computes harmonic states from raw notes.

#### 4.2 Rename `.progression_type` → `.classification` (or vice versa, but be consistent)
- **What:** The `HolonomyResult` attribute is `progression_type` (returns a `ProgressionType` enum), but the natural name based on the theory docs would be `classification`. Pick one and use it everywhere.
- **Why:** During testing I wrote `.classification` (from the theory docs) and got an AttributeError. This will bite every new user.
- **Effort:** Trivial — rename + deprecation path
- **Reference:** N/A — internal consistency

#### 4.3 Add chord voicing suggestions
- **What:** Given a chord progression analysis, suggest specific voicings (which pitches on which beats) that minimize voice-leading distance (holonomy).
- **Why:** The theory proves that good voice leading = low holonomy. But the analyzer doesn't use this insight to *generate* voicings — it only *analyzes*. The natural next step is: "here's a progression, here's the optimal voicing."
- **Effort:** Hard — requires search over voicing space with holonomy as cost function
- **Reference:** `musicpy` has voice-leading generation. `music21` can compute voice-leading distance via `voiceLeading.VoiceLeadingQuartet`.

---

## 5. spline-midi-smooth

### Top 3 Improvements

#### 5.1 Add in-memory smoothing API (no file I/O required)
- **What:** `smooth_velocity_curve_values(velocities: List[int], times: List[float]) -> List[int]` that takes and returns plain lists. Similarly `smooth_cc_values(values, times) -> values`.
- **Why:** `smooth_velocity_curve()` requires file paths. `smooth_midi_cc()` requires file paths. In a DAW plugin, you have arrays in memory. The interpolation functions (`cubic_hermite`, etc.) already work on arrays — just expose this at the musical level.
- **Effort:** Easy — the interpolation layer already exists
- **Reference:** NumPy-based signal processing libraries all offer both file and in-memory APIs.

#### 5.2 Support multi-track MIDI preservation
- **What:** When smoothing a multi-track MIDI file, preserve the original track structure. Currently `smooth_midi_cc()` collapses to Type 0 (single track). This breaks multi-instrument MIDI files.
- **Why:** A 4-voice counterpoint MIDI has 5 tracks (meta + 4 voices). Running it through the smoother produces a single track. All voice separation is lost. This makes the smoother unusable for multi-track MIDI without manual reconstruction.
- **Effort:** Medium — rewrite output to preserve track structure
- **Reference:** `mido` supports both Type 0 and Type 1. `pretty_midi` always preserves instruments.

#### 5.3 Add configurable smoothing strength / deadband integration
- **What:** `smooth_velocity_curve(..., smoothing=0.5)` where 0.0 = no smoothing (pass-through) and 1.0 = maximum smoothing. Integrate with deadband: don't smooth within the deadband, only smooth transitions that exceed it.
- **Why:** Currently smoothing is all-or-nothing. Real producers want control: "smooth the transitions but keep the intentional accents." The deadband theory in constraint-theory-core provides the perfect theoretical basis: smooth outside ε, preserve inside ε.
- **Effort:** Medium — parameterize the spline tension / add deadband gating
- **Reference:** Ableton's automation smoothing has a "amount" knob. Cubase's MIDI processing has smoothing percentage controls.

---

## 6. plato-room-musician

### Top 3 Improvements

#### 6.1 Accept external NoteEvent sequences (decouple from PLATO rooms)
- **What:** Add `PlatoScore.from_counterpoint_voices(voices, voice_names=None)` and `PlatoScore.from_midi_file(path)` constructors.
- **Why:** Currently `PlatoScore` is tightly coupled to PLATO room/tile data. But the renderer (`MidiRenderer`, `TensorMidiRenderer`, `VMSRenderer`) is generically useful. The counterpoint engine output should feed directly into the score and then to any renderer. Without this, plato-room-musician is isolated.
- **Effort:** Easy — `NoteEvent` already has generic fields; just add alternative constructors
- **Reference:** `music21.stream.Stream` accepts notes, chords, or MIDI files interchangeably.

#### 6.2 Add MIDI import round-trip
- **What:** `PlatoScore.from_midi_file(path)` → parse a MIDI file into `NoteEvent` objects. Then `PlatoScore.to_midi_file(path)`. Verify round-trip fidelity.
- **Why:** The `MidiRenderer` can write but can't read. For a DAW plugin, you need to read the host's MIDI, process it, and write it back. The renderers are write-only today.
- **Effort:** Medium — mido parsing + NoteEvent construction
- **Reference:** `pretty_midi` round-trips MIDI → internal → MIDI. `mido` itself is read-write.

#### 6.3 Add MusicXML output (sheet music)
- **What:** `MusicXmlRenderer.render(score) -> str` that produces MusicXML. This enables sheet music display in any notation software.
- **Why:** MIDI is for playback. For composition workflows, musicians need to *see* the score. MusicXML is the standard interchange format for notation. The VMS JSON format is custom and unsupported by any existing tool.
- **Effort:** Medium — MusicXML has a clear spec; `music21` has a reference implementation
- **Reference:** `music21` writes MusicXML, LilyPond, and MIDI. `mingus` uses LilyPond for notation output.

---

## Integration Improvements

### 7.1 Unified Package / Namespace

**Problem:** Currently 6 separate pip packages with no cross-dependencies. Users must discover and install each independently.

**Proposal:** Create a `tensor-midi` (or `ensemble-theory`) umbrella package:
```python
# Instead of:
from counterpoint_engine import CounterpointGenerator
from holonomy_harmony import analyze_progression
from groove_analyzer.genres import synthesize_groove

# One import:
from tensor_midi import counterpoint, harmony, groove, smooth, render
# Or:
from tensor_midi import CounterpointGenerator, analyze_progression
```

**Effort:** Medium — create umbrella package with lazy imports

### 7.2 Pipeline Class

**Problem:** The pipeline test required ~100 lines of glue code to connect the 6 modules.

**Proposal:**
```python
from tensor_midi import Pipeline

result = (
    Pipeline()
    .counterpoint(cantus_firmus=[60, 62, 64, 65, 67, 69, 71, 72], n_voices=4)
    .analyze_harmony(key="C", mode="major")
    .apply_groove(genre="Funk", bpm=105)
    .smooth_velocity(method="catmull_rom")
    .render_midi("output.mid")
)

# Access intermediate results:
result.voices          # [[60,62,...], [36,41,...], ...]
result.harmony         # ProgressionAnalysis
result.groove_timing   # GrooveTiming
result.midi_file       # mido.MidiFile
```

**Effort:** Medium — design fluent API, handle data format conversions internally

### 7.3 Shared Data Types

**Problem:** Each module defines its own representation of notes/events. `NoteEvent` (plato-room-musician) ≠ `TensorMIDIEvent` (counterpoint-engine) ≠ `OnsetEvent` (groove-analyzer) ≠ `CcPoint` (spline-midi-smooth).

**Proposal:** Define shared types in `constraint-theory-core` (already the base package):
```python
from constraint_theory_core.types import Note, Voice, Performance
# Note(pitch, velocity, onset_beats, duration_beats, channel)
# Voice(notes, name, channel, range)
# Performance(voices, bpm, time_signature)
```

Each module should accept and return these shared types, with conversion functions for their internal representations.

**Effort:** Medium — define types + add conversion functions to each module

### 7.4 Missing Convenience Functions

| Function | Module | Description |
|----------|--------|-------------|
| `voices_to_midi(voices, bpm)` | counterpoint-engine | Direct MIDI export from voice arrays |
| `analyze_harmony_from_voices(voices, key)` | holonomy-harmony | Skip Roman numeral parsing, accept MIDI pitches |
| `apply_groove_to_midi(midi, genre)` | groove-analyzer | Modify timing of existing MIDI |
| `smooth_velocities_in_memory(vels, times)` | spline-midi-smooth | No file I/O needed |
| `score_from_voices(voices, names)` | plato-room-musician | Create score from counterpoint output |

---

## Documentation Improvements

### 8.1 What Was Confusing

1. **`tensor_output.py` requires `flux_tensor_midi`** — this dependency isn't documented anywhere. It's an external package that must be installed separately. If it's missing, you get a cryptic import error at the module level (not when calling the function).

2. **`groove_analyzer/__init__.py` exports nothing** — it has only `__version__`. All public API requires knowing the internal module structure (`groove_analyzer.genres`, `groove_analyzer.microtiming`, `groove_analyzer.deadband_groove`). Compare with `holonomy-harmony` which re-exports everything from `__init__.py`.

3. **`HolonomyResult.progression_type` vs the theory docs saying "classification"** — terminology mismatch between code and theory docs.

4. **`smooth_velocity_curve()` sounds like it operates on arrays** — but it actually reads/writes MIDI files. The name suggests NumPy-style array processing.

5. **`PlatoScore` is PLATO-specific** — but the renderers (MidiRenderer, VMSRenderer) are generic. The tight coupling to room/tile data makes it unclear how to use the renderers independently.

### 8.2 Missing Examples

1. **"Full musical pipeline" tutorial** — A single Jupyter notebook showing all 6 modules working together, from cantus firmus to rendered MIDI with groove and smooth dynamics. This is THE most important missing piece.

2. **"Generate a 4-bar funk bass line from a chord progression"** — The canonical music tech demo. Input: `['I', 'IV', 'V', 'I']`, output: funky bass MIDI. Currently impossible without writing significant glue code.

3. **"Analyze your own MIDI file's groove"** — How to load a real performance MIDI and get its deadband profile. The microtiming analyzer works but no example shows this flow.

4. **"Custom constraint rules"** — How to add your own counterpoint rules. The constraint system is extensible but no docs show extending it.

5. **"Real-time usage patterns"** — How to use these libraries in a latency-sensitive context (DAW plugin, live coding). What to cache, what's expensive, what's fast.

### 8.3 Tutorials That Would Help

| Tutorial | Audience | Covers |
|----------|----------|--------|
| "Counterpoint in 5 minutes" | Composers | Generate 2-voice counterpoint, render to MIDI, play it |
| "Understanding your groove" | Producers | Load a drum loop, analyze microtiming, understand the deadband |
| "Smooth MIDI dynamics" | MIDI programmers | Read quantized MIDI, apply spline smoothing, hear the difference |
| "Build a chord progression analyzer" | Music theorists | Parse Roman numerals, compute holonomy, detect modulations |
| "The full pipeline: theory to audio" | Researchers | Cantus firmus → 4 voices → harmony → groove → smooth → render |
| "Integrating with a DAW" | Plugin developers | In-memory APIs, serialization, performance tips |

---

## Competitor Analysis

### music21 (MIT)
- **What they do better:** Massive music theory coverage, notation, MusicXML, corpus analysis, 20+ years of development, huge academic community. The `voiceLeading` module checks standard counterpoint rules.
- **What we do better:** Mathematical rigor (Laman rigidity, holonomy), groove analysis (music21 has zero microtiming support), spline smoothing, the unified constraint theory narrative.
- **Features to add:** Chord detection from pitch sets, key detection (Krumhansl-Schmuckler), MusicXML output.

### pretty_midi
- **What they do better:** Clean MIDI I/O, piano roll visualization, instrument management, robust tempo handling, in-memory operation throughout.
- **What we do better:** We actually generate and analyze music (pretty_midi is just I/O), groove theory, spline smoothing.
- **Features to add:** In-memory APIs everywhere, better tempo map handling in smoothing.

### GrooveToolbox
- **What they do better:** Perceptually-motivated rhythm features, microtiming deviation matrices, velocity features, comprehensive drum loop analysis.
- **What we do better:** Deadband funnel theory (novel), genre-based groove generation, the mathematical proof that groove = deadband.
- **Features to add:** Perceptual features (syncopation weighting, groove salience), velocity accent patterns per genre.

### musicpy
- **What they do better:** Music-as-code paradigm, comprehensive chord/scale operations, built-in MIDI I/O, concise syntax for musical ideas.
- **What we do better:** Mathematical foundations, constraint-based generation (musicpy is more imperative), holonomy-based harmony analysis.
- **Features to add:** Chord progression builder, key detection, voicing suggestions.

### pychord / chordparser
- **What they do better:** Robust chord parsing from symbols (Cmaj7, Am7b5, etc.), chord transposition, scale-chord relationships.
- **What we do better:** Roman numeral analysis, holonomy-based progression quality scoring, modulation detection.
- **Features to add:** Support for jazz chord symbols (b9, #11, alt), chord spelling from pitch sets.

---

## Priority Ranking (Impact × Effort)

| Priority | Improvement | Impact | Effort | Score |
|----------|------------|--------|--------|-------|
| 🔴 P0 | Pipeline class (7.2) | Critical | Medium | 10 |
| 🔴 P0 | `groove_analyzer/__init__.py` re-exports | Critical | Trivial | 10 |
| 🔴 P0 | Full pipeline tutorial (8.2.1) | Critical | Easy | 9 |
| 🟡 P1 | In-memory smoothing API (5.1) | High | Easy | 8 |
| 🟡 P1 | `counterpoint.to_midi()` (2.1) | High | Easy | 8 |
| 🟡 P1 | `analyze_from_pitches()` (4.1) | High | Medium | 7 |
| 🟡 P1 | Shared data types (7.3) | High | Medium | 7 |
| 🟡 P1 | Apply groove to MIDI (3.1) | High | Medium | 7 |
| 🟢 P2 | Multi-track preservation (5.2) | Medium | Medium | 5 |
| 🟢 P2 | Species 2-5 (2.2) | Medium | Hard | 4 |
| 🟢 P2 | Chord voicing suggestions (4.3) | Medium | Hard | 4 |
| 🟢 P2 | MusicXML output (6.3) | Medium | Medium | 5 |
| 🔵 P3 | Constraint propagation (2.3) | Low | Medium | 3 |
| 🔵 P3 | Unified namespace (7.1) | Low | Medium | 3 |
