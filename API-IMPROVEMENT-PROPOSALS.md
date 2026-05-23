# API Improvement Proposals — Constraint-Theory Music Ecosystem

**Author:** API Design Review (subagent)  
**Date:** 2026-05-22  
**Scope:** All 6 repos: `constraint-theory-core`, `counterpoint-engine`, `groove-analyzer`, `holonomy-harmony`, `spline-midi-smooth`, `plato-room-musician`

---

## Part 1: API Consistency Audit

### 1.1 Naming Consistency

**Finding: CRITICAL — No two repos agree on primary verb conventions.**

| Repo | "Analyze" Entry Point | "Generate" Entry Point | "Export" Entry Point |
|---|---|---|---|
| `constraint-theory-core` | N/A (low-level) | N/A | N/A |
| `counterpoint-engine` | N/A | `CounterpointGenerator.generate()` | `voices_to_tensor_events()` |
| `groove-analyzer` | `extract_microtiming()` | `synthesize_groove()` | N/A |
| `holonomy-harmony` | `analyze_progression()` | N/A | N/A |
| `spline-midi-smooth` | N/A | N/A | `smooth_midi_cc()` (writes file) |
| `plato-room-musician` | N/A | N/A | `MidiRenderer.render()` |

**Specific inconsistencies:**

1. **groove-analyzer** uses `extract_microtiming(path)` — verb-first but oddly specific. Should be `analyze()` like holonomy-harmony's `analyze_progression()`.
2. **counterpoint-engine** uses `CounterpointGenerator.generate()` — class method. **holonomy-harmony** uses `analyze_progression()` — free function. **groove-analyzer** uses `extract_microtiming()` — free function. No pattern.
3. **spline-midi-smooth** uses `smooth_midi_cc()` as its main entry — a compound verb that doesn't match any other repo's pattern.
4. **plato-room-musician** uses `render()` on a renderer object — the only repo using the Builder/Renderer pattern.
5. **Deadband fitting** in groove-analyzer is `fit_deadband()` (verb-noun) while **holonomy check** in holonomy-harmony is `compute_holonomy()` (verb-noun) — these are parallel operations but named differently.
6. `prove_groove_is_deadband()` in groove-analyzer — uniquely uses `prove_` prefix. No other repo has `prove_` functions exposed publicly.
7. **counterpoint-engine** uses `CounterpointGraph` while **holonomy-harmony** uses `TonalGraph` — both are graph data structures but one uses the domain name and the other uses the abstract name.
8. `is_laman()` in constraint-theory-core vs `verify_rigidity()` in counterpoint-engine (wraps it) — the wrapper adds no value and creates naming confusion.

### 1.2 Return Types

**Finding: SEVERE — Five different return-type conventions across 6 repos.**

| Repo | Primary Return Types |
|---|---|
| `constraint-theory-core` | `dataclass` (`A2Point`, `FunnelResult`, `MetronomeState`), `Tuple`, `bool`, `float` |
| `counterpoint-engine` | `Optional[List[int]]`, `Tuple[List[TensorMIDIEvent], List[MidiEvent]]`, `str` literal (`SAT`/`UNSAT`) |
| `groove-analyzer` | `dataclass` (`GrooveTiming`, `DeadbandFit`, `EnsembleFunnel`), `Dict[str, float]` |
| `holonomy-harmony` | `dataclass` (`HolonomyResult`, `ProgressionAnalysis`, `Chord`), `Enum` (`ProgressionType`) |
| `spline-midi-smooth` | `Callable` (spline function), `dict[CcTrackKey, int]`, `np.ndarray` tuples |
| `plato-room-musician` | `class` instances (`NoteEvent` — not a dataclass!), `list[dict]`, `mido.MidiFile` |

**Issues:**
- `counterpoint-engine` returns `Optional[List[int]]` — caller must always check for `None`. A result object would be cleaner.
- `groove-analyzer`'s `prove_groove_is_deadband()` returns `Dict[str, float]` — untyped, impossible to autocomplete. Should be a dataclass.
- `plato-room-musician`'s `NoteEvent` is a plain class with `__init__`, not a dataclass. Inconsistent with every other data container in the ecosystem.
- `counterpoint-engine`'s `SAT`/`UNSAT` are string literals, not an enum. `groove-analyzer` correctly uses `TimingClass(str, Enum)`. Inconsistent.
- `spline-midi-smooth` returns `Callable` from its interpolation functions — fine, but `smooth_midi_cc()` returns a `dict` of stats. No typed result object.

### 1.3 Import Ergonomics

**Finding: MODERATE — Some repos are great, some are painful.**

**Simple workflow import count:**

```python
# constraint-theory-core: 1 import (excellent)
from constraint_theory_core import snap, is_safe

# counterpoint-engine: 2-3 imports (okay)
from counterpoint_engine import CounterpointGenerator, Species
from counterpoint_engine import TensorMIDIEvent  # separate if needed

# groove-analyzer: 3-4 imports (painful — nothing re-exported!)
from groove_analyzer.microtiming import extract_microtiming
from groove_analyzer.deadband_groove import fit_deadband, build_funnel
from groove_analyzer.genres import synthesize_groove
from groove_analyzer.visualize import plot_deadband_funnel

# holonomy-harmony: 1-2 imports (good)
from holonomy_harmony import analyze_progression, Chord

# spline-midi-smooth: 1-2 imports (good)
from spline_midi_smooth import smooth_midi_cc, catmull_rom

# plato-room-musician: 3-4 imports (painful)
from plato_room_musician import SyntheticFetcher, RoomMapper, TileMapper
from plato_room_musician import PlatoScore, MidiRenderer
```

**Critical issue:** `groove-analyzer`'s `__init__.py` only exports `__version__`. Every user must know the internal module layout.

### 1.4 Error Handling

**Finding: SEVERE — No shared exception hierarchy.**

| Repo | Error Strategy |
|---|---|
| `constraint-theory-core` | `ValueError` only |
| `counterpoint-engine` | `ValueError` only |
| `groove-analyzer` | `ValueError`, `warnings.warn()`, silently returns empty `GrooveTiming` |
| `holonomy-harmony` | `ValueError` only |
| `spline-midi-smooth` | `ValueError` only |
| `plato-room-musician` | `ConnectionError` (custom use), `ValueError` |

**Issues:**
- No custom exceptions anywhere. `groove-analyzer` warns instead of raising for empty MIDI files — this silently hides problems.
- `plato-room-musician`'s `PlatoFetcher` raises `ConnectionError` — a built-in that doesn't distinguish between "server down" and "room not found."
- `counterpoint-engine` returns `None` on failure instead of raising. This is the worst pattern — silent failure.
- No shared base exception class like `ConstraintTheoryError`.

### 1.5 Type Hints

**Finding: GOOD with gaps.**

| Repo | Type Hints | Quality |
|---|---|---|
| `constraint-theory-core` | ✅ Complete | Excellent — all params and returns typed |
| `counterpoint-engine` | ✅ Complete | Good — `from __future__ import annotations` used |
| `groove-analyzer` | ✅ Mostly complete | Good — uses `Path | str` union syntax |
| `holonomy-harmony` | ✅ Complete | Good |
| `spline-midi-smooth` | ✅ Complete | Good — `Callable` return types specified |
| `plato-room-musician` | ⚠️ Partial | Missing on `NoteEvent` methods, `RoomMapper`, `TileMapper` |

**Issues:**
- `plato-room-musician`'s `NoteEvent` has no type hints on `__init__` parameters or methods.
- Mixed use of `Optional[X]` vs `X | None` across repos — not a functional issue but inconsistent style.
- `groove-analyzer` uses `tuple[float, float]` (lowercase) while `constraint-theory-core` uses `Tuple[float, float]` (uppercase). With `from __future__ import annotations`, lowercase is fine, but it's inconsistent.

### 1.6 Docstrings

**Finding: MODERATE — Three different formats.**

| Repo | Docstring Format | Has Examples? |
|---|---|---|
| `constraint-theory-core` | NumPy-style (Parameters/Returns/Notes/Examples sections) | ✅ Yes |
| `counterpoint-engine` | Short module docstring, Google-ish on classes | ⚠️ Partial |
| `groove-analyzer` | NumPy-style | ✅ Yes |
| `holonomy-harmony` | NumPy-style | ✅ Yes |
| `spline-midi-smooth` | NumPy-style | ✅ Yes |
| `plato-room-musician` | Bare docstrings, no format | ❌ No |

**Issues:**
- `plato-room-musician` has minimal docstrings — `NoteEvent.__init__` has none.
- `counterpoint-engine`'s `rules.py` has good docstrings but `generator.py`'s class docstring is sparse.
- Module-level docstrings vary from thesis statements ("prove the core thesis") to one-liners ("Groove Analyzer — prove groove = deadband funnel").

---

## Part 2: Research — Best-in-Class APIs

### 2.1 mido — What Makes It Good

- **Messages as objects:** `msg = mido.Message('note_on', note=60, velocity=64)` — keyword args, no positional confusion.
- **Flat namespace:** `mido.MidiFile`, `mido.Message`, `mido.MetaMessage` — 2-3 imports max for any workflow.
- **Consistent I/O pattern:** `.save()` on MidiFile, `.play()` on ports — verb on the object.
- **Low-level but complete:** Doesn't try to be a music theory library. Does one thing well.

**Lessons for this ecosystem:**
- Standardize on keyword-arg construction
- Keep top-level imports flat
- Put `.to_midi()`, `.to_bytes()` on result objects, not on separate functions

### 2.2 music21 — What Makes It Discoverable

- **Rich objects:** `stream.Stream()`, `note.Note()`, `chord.Chord()` — everything is a musical concept.
- **Conventional methods:** `.show()`, `.analyze()`, `.transpose()` — verbs that match domain language.
- **Deep hierarchy:** `GeneralNote → Note → NotRest → ...` — learn once, apply everywhere.

**Lessons:**
- Musical domain objects should have musical domain methods
- `.analyze()` should be a universal verb
- `.show()` / `.render()` / `.export()` should follow a convention

### 2.3 NumPy — What Makes It Easy to Learn

- **One convention everywhere:** `np.function(array)` — function-first, data-as-arg.
- **Consistent dtypes:** Always returns ndarray, never mixes types.
- **Broadcasting rules:** Learn once, works everywhere.

**Lessons:**
- Return consistent types
- Don't sometimes return `None`, sometimes return empty list, sometimes raise

### 2.4 Polars vs Pandas — Lessons for the Redesign

- **Immutability wins:** Polars returns new objects; Pandas mutates in place. The ecosystem should favor frozen dataclasses.
- **Consistent verb-noun naming:** Polars uses `.select()`, `.filter()`, `.group_by()` — short, consistent verbs.
- **Schema-first:** Polars knows types before execution. The music ecosystem should validate input types eagerly.
- **Flat imports:** `import polars as pl` → `pl.DataFrame()`, `pl.col()`, `pl.concat()`. One namespace.

---

## Part 3: API Improvement Proposals

### 3.1 Consistency Fixes — All Inconsistencies Found

#### Naming Renames

| Current | Proposed | Repo | Reason |
|---|---|---|---|
| `extract_microtiming()` | `analyze()` | groove-analyzer | Match `analyze_progression()` pattern |
| `synthesize_groove()` | `generate()` | groove-analyzer | Match `CounterpointGenerator.generate()` |
| `smooth_midi_cc()` | `smooth()` | spline-midi-smooth | Simplify; `smooth_midi_volume()` already exists as specialization |
| `fit_deadband()` | `fit()` | groove-analyzer | Unnecessary qualifier in module context |
| `build_funnel()` | `build()` | groove-analyzer | Unnecessary qualifier |
| `prove_groove_is_deadband()` | `_prove_groove_is_deadband()` | groove-analyzer | Internal function, not public API |
| `verify_rigidity()` (wrapper) | Remove — use `is_laman()` directly | counterpoint-engine | Redundant wrapper adds naming confusion |
| ` henneberg_construct()` (wrapper) | Remove — use core's directly | counterpoint-engine | Same |
| `SAT` / `UNSAT` string literals | `ConstraintResult` enum with `SAT`/`UNSAT` | counterpoint-engine | Type safety, consistency with `TimingClass` enum |
| `NoteEvent` (plain class) | `@dataclass(frozen=True, slots=True)` | plato-room-musician | Match ecosystem convention |
| `PlatoScore.find_chords()` returns `list[dict]` | Returns `list[ChordAnnotation]` dataclass | plato-room-musician | Typed return |
| `PlatoScore.find_rests()` returns `list[dict]` | Returns `list[Rest]` dataclass | plato-room-musician | Typed return |
| `PlatoScore.summary()` returns `dict` | Returns `ScoreSummary` dataclass | plato-room-musician | Typed return |
| `plot_deadband_funnel()` | `plot()` | groove-analyzer | Module context makes "deadband_funnel" redundant |
| `plot_groove_comparison()` | `plot_comparison()` | groove-analyzer | Same |
| `TensorMIDIEvent` (in counterpoint-engine AND plato-room-musician) | Single definition, shared | both | Duplicated class |

#### Import Fixes

| Repo | Current | Proposed |
|---|---|---|
| groove-analyzer | Must import from submodules | Re-export everything in `__init__.py` |
| plato-room-musician | `from plato_room_musician.score import PlatoScore` | `from plato_room_musician import PlatoScore` (already works via `__init__.py`, but `NoteEvent` not re-exported) |

### 3.2 Proposed Unified API Pattern

```python
"""
The ideal API for the constraint-theory music ecosystem.

Every module follows the same pattern:
  - analyze() → analyzes existing data, returns result object
  - generate() → creates new music, returns result object
  - Result objects have .to_midi(), .to_dict(), .summary()
  - One flat import per module
"""

# ── constraint-theory-core (foundation, low-level — unchanged mostly) ──
from constraint_theory_core import snap, is_safe, A2Point
pt, err = snap(0.5, 0.3)
assert is_safe(err)

# ── counterpoint-engine ──
from counterpoint_engine import Counterpoint

# Generate first-species counterpoint
result = Counterpoint.generate(
    cantus_firmus=[60, 62, 64, 65, 67],
    species=1,
    key="C major",
)
result.to_midi("counterpoint.mid")
print(result.summary())
# CounterpointResult(n_voices=2, n_beats=5, rigid=True, constraints_satisfied=5)

# ── groove-analyzer ──
from groove_analyzer import Groove

# Analyze microtiming
groove = Groove.analyze("drums.mid")
print(groove.summary())
# GrooveResult(bpm=120.0, tracks=4, epsilon_ms=15.2, genre="Funk")

# Fit deadband model
fit = groove.fit_deadband()
print(fit)
# DeadbandFit(epsilon_ms=15.2, coverage=92%, genre="Funk")

# Generate synthetic groove
synth = Groove.generate("Funk", bars=4, seed=42)
synth.to_midi("funk_groove.mid")

# ── holonomy-harmony ──
from holonomy_harmony import Harmony

# Analyze a progression
analysis = Harmony.analyze(["I", "IV", "V", "I"], key="C major")
print(analysis.stability_score)
# 0.85
print(analysis.holonomy)
# HolonomyResult(holonomy=0, type=DIATONIC)

# ── spline-midi-smooth ──
from spline_midi_smooth import Spline

# Smooth MIDI CC data
result = Spline.smooth("input.mid", method="catmull_rom")
result.to_midi("smooth.mid")
print(result.summary())
# SmoothResult(n_tracks_smoothed=3, total_events=12000)

# ── plato-room-musician ──
from plato_room_musician import Orchestra

# Build score from PLATO rooms
score = Orchestra.from_plato(host="http://147.224.38.131:8847")
score.to_midi("fleet.mid")
score.to_vms("fleet.json")
print(score.summary())
# ScoreSummary(rooms=8, events=234, duration_beats=64.5, chords=12)
```

### 3.3 Missing Convenience Methods

#### constraint-theory-core

| Object | Missing | Proposal |
|---|---|---|
| `A2Point` | `__str__` | `A2Point(a=1, b=2)` → `"A₂(1,2)"` |
| `A2Point` | `.to_midi_pitch()` | Map lattice point to nearest MIDI pitch |
| `FunnelResult` | `.is_narrowing` / `.is_anomaly` | Convenience booleans instead of comparing enums |
| `Metronome` | `.to_dict()` | Serialize state for debugging |
| `MetronomeState` | `__str__` | Human-readable single line |

#### counterpoint-engine

| Object | Missing | Proposal |
|---|---|---|
| `CounterpointGenerator` | `.to_midi()` | Generate and export in one call |
| `CounterpointResult` (new) | Wrap `Optional[List[int]]` | Include metadata: timing, constraints checked, rigidity proof |
| `TensorMIDIEvent` | `__str__` | `"TME(cos=60, sin=-30, beat=4, state=0x12)"` already has repr, add `__format__` |
| `Scale` | `.name` property | `"C major"` instead of `Scale(tonic=0, mode='major')` |
| `VoiceRange` | `.name` property | `"C3-G5"` |
| `Species` | `.description` | `"First species (note against note)"` |

#### groove-analyzer

| Object | Missing | Proposal |
|---|---|---|
| `GrooveTiming` | `.to_dict()` | Serialize for JSON export |
| `GrooveTiming` | `.summary()` | One-line human-readable summary |
| `DeadbandFit` | `.to_dict()` | Serialize for export |
| `EnsembleFunnel` | `.to_dict()` | Serialize |
| `GenreProfile` | `.to_dict()` | Serialize |
| (global) | `.from_midi()` class method on `Groove` | Alias for `analyze()` |

#### holonomy-harmony

| Object | Missing | Proposal |
|---|---|---|
| `Chord` | `.to_music21()` | Export to music21 chord object |
| `Chord` | `.midi_notes()` | Return list of MIDI pitch numbers |
| `ProgressionAnalysis` | `.to_dict()` | Serialize |
| `ProgressionAnalysis` | `.plot()` | Visualize holonomy over time |
| `TonalGraph` | `.to_dot()` | Export Graphviz DOT for visualization |
| `HolonomyResult` | `.to_dict()` | Serialize |

#### spline-midi-smooth

| Object | Missing | Proposal |
|---|---|---|
| `CcPoint` | `__repr__` | Currently missing! |
| `CcTrackKey` | `__repr__` | Currently missing! |
| Result of `smooth_midi_cc()` | Should be a dataclass, not `dict` | `SmoothResult` with `.stats`, `.to_midi()` |
| `deadband_spline()` return | Named tuple or dataclass instead of 4 raw arrays | `DeadbandSplineResult(times, values, upper, lower)` |

#### plato-room-musician

| Object | Missing | Proposal |
|---|---|---|
| `NoteEvent` | Make a frozen dataclass | Match ecosystem |
| `NoteEvent` | `.to_dict()` → already exists as method | ✅ Good |
| `PlatoScore` | `.to_midi(path)` convenience | Currently requires `MidiRenderer(...).render(score, path)` |
| `PlatoScore` | `.to_vms(path)` convenience | Currently requires `VMSRenderer(...).render_to_json(score)` |
| `PlatoScore` | `.to_tensor_midi()` convenience | Currently requires `TensorMidiRenderer().render(score)` |
| `PlatoScore` | `__len__` | Number of events |
| `PlatoScore` | `__repr__` | Summary on one line |
| `RoomMapper` | `__repr__` | Show channel assignments |

### 3.4 Specific PR Descriptions — 5 Concrete PRs

---

#### PR 1: Unify groove-analyzer public API and re-export all symbols

**Title:** `feat: Flatten groove-analyzer API — re-export all public symbols from __init__.py`

**Description:**
Currently, users must know internal module names (`microtiming`, `deadband_groove`, `genres`, `visualize`) to use groove-analyzer. This PR re-exports everything from `__init__.py` and adds convenience aliases.

**Files to change:**
- `groove_analyzer/__init__.py` — Add all public symbols from submodules
- `groove_analyzer/microtiming.py` — Add `analyze` as alias for `extract_microtiming`
- `groove_analyzer/genres.py` — Add `generate` as alias for `synthesize_groove`

**Expected behavior:**
```python
# Before (3 imports, knowledge of internals required)
from groove_analyzer.microtiming import extract_microtiming
from groove_analyzer.deadband_groove import fit_deadband
from groove_analyzer.genres import synthesize_groove

# After (1 import, flat namespace)
from groove_analyzer import analyze, fit_deadband, generate
```

---

#### PR 2: Replace SAT/UNSAT string literals with ConstraintResult enum

**Title:** `feat: Introduce ConstraintResult enum to replace SAT/UNSAT string literals`

**Description:**
`counterpoint_engine.rules` uses bare string literals `"SAT"` and `"UNSAT"` as return values. This is error-prone (typos pass silently) and inconsistent with `groove_analyzer.microtiming.TimingClass(str, Enum)`. This PR introduces a `ConstraintResult` enum.

**Files to change:**
- `counterpoint_engine/rules.py` — Define `ConstraintResult(SAT="SAT", UNSAT="UNSAT")`, update all functions
- `counterpoint_engine/__init__.py` — Export `ConstraintResult` alongside (or instead of) `SAT`/`UNSAT`
- `counterpoint_engine/generator.py` — Update comparisons to use enum
- `tests/test_rules.py` — Update assertions

**Expected behavior:**
```python
from counterpoint_engine import consonant_interval, ConstraintResult

result = consonant_interval([60], [64], 0)
assert result == ConstraintResult.SAT
# Old: assert result == "SAT"  (still works due to str inheritance)
```

---

#### PR 3: Convert plato-room-musician NoteEvent to frozen dataclass + add convenience exports

**Title:** `refactor: Convert NoteEvent to frozen dataclass; add PlatoScore.to_midi() convenience methods`

**Description:**
`NoteEvent` is the only mutable plain class in the ecosystem. Every other data container uses `@dataclass(frozen=True, slots=True)`. This PR converts it and adds convenience export methods to `PlatoScore` so users don't need to instantiate separate renderer objects for basic workflows.

**Files to change:**
- `plato_room_musician/score.py` — Convert `NoteEvent` to `@dataclass(frozen=True, slots=True)`, add `PlatoScore.to_midi()`, `PlatoScore.to_vms()`, `PlatoScore.to_tensor_midi()`
- `plato_room_musician/renderer.py` — Update to work with frozen NoteEvent (should be transparent since renderers only read fields)
- `plato_room_musician/__init__.py` — Re-export `NoteEvent`

**Expected behavior:**
```python
# Before (4 lines, must know renderer classes)
from plato_room_musician import PlatoScore, MidiRenderer
score = PlatoScore.from_mapped_tiles(tiles)
renderer = MidiRenderer(tempo_bpm=120)
renderer.render(score, "output.mid")

# After (2 lines)
from plato_room_musician import PlatoScore
score = PlatoScore.from_mapped_tiles(tiles)
score.to_midi("output.mid", tempo_bpm=120)
```

---

#### PR 4: Add result objects for counterpoint generation and MIDI smoothing

**Title:** `feat: Wrap counterpoint and smoothing results in typed dataclasses`

**Description:**
`CounterpointGenerator.generate()` returns `Optional[List[int]]` — caller must check for `None` and gets no metadata. `smooth_midi_cc()` returns an untyped `dict`. This PR introduces `CounterpointResult` and `SmoothResult` dataclasses.

**Files to change:**
- `counterpoint_engine/generator.py` — Define `CounterpointResult` dataclass with fields: `voices`, `n_beats`, `species`, `rigidity_verified`, `constraints_satisfied`, `generation_time_ms`. Return it from `generate()`.
- `counterpoint_engine/__init__.py` — Export `CounterpointResult`
- `counterpoint_engine/tensor_output.py` — Add `to_midi()` method on result
- `spline_midi_smooth/midi_processor.py` — Define `SmoothResult` dataclass with fields: `stats`, `input_path`, `output_path`, `method`. Return it from `smooth_midi_cc()`.
- `spline_midi_smooth/__init__.py` — Export `SmoothResult`

**Expected behavior:**
```python
# Counterpoint
from counterpoint_engine import Counterpoint
result = Counterpoint.generate(cantus_firmus=[60, 62, 64, 65, 67])
if result:  # __bool__ based on success
    result.to_midi("output.mid")
    print(result.summary())  # "2 voices, 5 beats, species=FIRST, rigid=True"

# Smoothing
from spline_midi_smooth import smooth
result = smooth("input.mid", "output.mid", method="catmull_rom")
print(result.stats)  # SmoothResult(n_tracks=3, events_generated=12000)
```

---

#### PR 5: Establish shared exception hierarchy and validate inputs eagerly

**Title:** `feat: Add constraint_theory_core.exceptions module with base exception classes`

**Description:**
Currently all repos raise bare `ValueError` with no way to catch "this came from the music ecosystem" vs "this came from stdlib". This PR adds a shared exception hierarchy in `constraint-theory-core` that all repos import and use.

**Files to change:**
- `constraint_theory_core/exceptions.py` — NEW FILE: Define `MusicTheoryError(Exception)`, `ConstraintError(MusicTheoryError)`, `GenerationError(MusicTheoryError)`, `AnalysisError(MusicTheoryError)`, `MIDIError(MusicTheoryError)`
- `constraint_theory_core/__init__.py` — Export exceptions
- `counterpoint_engine/generator.py` — Raise `GenerationError` instead of returning `None`
- `groove_analyzer/microtiming.py` — Raise `AnalysisError` instead of warning on empty MIDI
- `holonomy_harmony/analyzer.py` — Raise `AnalysisError` on invalid Roman numerals
- `spline_midi_smooth/midi_processor.py` — Raise `MIDIError` on bad files
- `plato_room_musician/fetcher.py` — Raise `ConnectionError` → `MIDIError` subclass

**Expected behavior:**
```python
from constraint_theory_core import MusicTheoryError
from counterpoint_engine import Counterpoint

try:
    result = Counterpoint.generate(cantus_firmus=[60, 62, 64, 65, 67])
except MusicTheoryError as e:
    print(f"Music engine error: {e}")  # Catches any error from any repo
```

---

## Appendix: Severity Summary

| Issue | Severity | Effort | Impact |
|---|---|---|---|
| groove-analyzer empty `__init__.py` | 🔴 Critical | 1 hour | Every user hits this |
| No shared exception hierarchy | 🔴 Critical | 3 hours | Silent failures in production |
| SAT/UNSAT string literals | 🟡 Medium | 1 hour | Type safety |
| NoteEvent not a dataclass | 🟡 Medium | 30 min | Consistency |
| `generate()` returns `Optional[List[int]]` | 🔴 Critical | 2 hours | Silent failures |
| Dict returns instead of typed objects | 🟡 Medium | 2 hours | IDE support, docs |
| Inconsistent primary verbs | 🟡 Medium | 3 hours | Learnability |
| Missing `__repr__`/`__str__` | 🟢 Low | 1 hour | Debugging |
| No `.to_midi()` convenience | 🟡 Medium | 2 hours | Usability |
| Duplicate TensorMIDIEvent | 🟡 Medium | 30 min | DRY |

**Total estimated effort for all PRs:** ~16 hours
**Recommended priority order:** PR 1 → PR 5 → PR 4 → PR 2 → PR 3
