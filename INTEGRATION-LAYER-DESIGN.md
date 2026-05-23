# Integration Layer Design — Constraint-Theory Music Ecosystem

**Date:** 2025-05-22  
**Status:** Design Proposal

## Overview

Six independent packages each own one slice of the constraint-theory music stack:

| Package | Responsibility |
|---|---|
| `constraint-theory-core` | A₂ lattice snap, deadband funnels, Laman rigidity, metronome consensus, holonomy verification |
| `counterpoint-engine` | Species counterpoint as constraint satisfaction, Laman-graph voice leading, tensor-MIDI output |
| `holonomy-harmony` | Chord progression analysis via cycle consistency / holonomy detection |
| `groove-analyzer` | Microtiming extraction, deadband groove fitting, genre synthesis |
| `spline-midi-smooth` | Spline interpolation for MIDI CC/volume/tempo, deadband-spline theory |
| `plato-room-musician` | PLATO room → NoteEvent → Score → MIDI/TensorMIDI/VMS rendering |

These packages are already coupled at the type level (e.g. `counterpoint-engine` imports `constraint_theory_core.lattice`; `plato-room-musician` duplicates `TensorMIDIEvent`). An integration layer provides a **unified pipeline** that composes all six without adding coupling inside individual packages.

---

## Part 1: Shared Types

### The Problem Today

There are **three incompatible note representations** across the repos:

1. **`NoteEvent`** (plato-room-musician): `room, channel, pitch, velocity, onset_beats, duration_beats, patch, agent, category, tile_id`
2. **`OnsetEvent`** (groove-analyzer): `time_sec, beat, pitch, velocity, channel, track_name, grid_line, deviation_ms, timing_class`
3. **`TensorMIDIEvent`** (counterpoint-engine + plato-room-musician): `cos_int8, sin_int8, beat_k, state_byte` — duplicated with slightly different construction logic

And two chord representations:
- **`Chord`** (holonomy-harmony): `root, quality, function, key, is_diatonic, is_secondary_dominant, implied_key`
- Plato's chord detection output: `onset_beats, duration_beats, rooms, notes, type`

### Proposed Shared Types

```python
# constraint_music_types.py — zero-dependency shared type definitions

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Dict, FrozenSet, List, Optional, Sequence, Tuple, Union
)


# ── Fundamental musical atoms ──────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class Note:
    """A single MIDI note event — the lingua franca of the ecosystem.
    
    All repos convert to/from this type. It is deliberately minimal:
    no room, no agent, no track_name. Those are metadata layers.
    """
    pitch: int          # MIDI 0-127
    velocity: int       # 0-127
    start: float        # seconds (absolute)
    duration: float     # seconds
    channel: int        # 0-15

    def __post_init__(self) -> None:
        assert 0 <= self.pitch <= 127
        assert 0 <= self.velocity <= 127
        assert 0 <= self.channel <= 15
        assert self.duration >= 0

    @property
    def end(self) -> float:
        return self.start + self.duration

    @property
    def pitch_class(self) -> int:
        return self.pitch % 12


@dataclass(frozen=True, slots=True)
class TimeSignature:
    numerator: int      # e.g. 4
    denominator: int    # e.g. 4

    @property
    def beats_per_measure(self) -> float:
        return self.numerator * (4.0 / self.denominator)


@dataclass(frozen=True, slots=True)
class KeySignature:
    tonic: int          # pitch class 0-11
    mode: str           # "major" | "minor"


# ── The Score — central data structure ─────────────────────────────────

@dataclass
class Score:
    """A complete musical score that flows through the pipeline.
    
    This is the primary data type. Every pipeline step takes a Score 
    and returns a Score (or an analysis result that wraps a Score).
    
    Inspired by pydub's AudioSegment: immutable-feeling, composable,
    with methods that return new Scores.
    """
    notes: List[Note]
    tempo: float = 120.0                          # BPM
    key: KeySignature = field(default_factory=lambda: KeySignature(0, "major"))
    time_signature: TimeSignature = field(default_factory=lambda: TimeSignature(4, 4))
    metadata: Dict = field(default_factory=dict)

    # ── Factory methods ──

    @classmethod
    def from_midi(cls, path: str) -> "Score":
        """Load from a MIDI file using mido."""
        import mido
        mid = mido.MidiFile(path)
        notes: List[Note] = []
        tempo = 120.0
        ts = TimeSignature(4, 4)
        
        for track in mid.tracks:
            abs_tick = 0
            current_tempo = 500000
            # Convert to absolute time
            pending: Dict[Tuple[int, int], Tuple[int, int]] = {}  # (ch, note) -> (start_tick, vel)
            
            for msg in track:
                abs_tick += msg.time
                if msg.type == "set_tempo":
                    current_tempo = msg.tempo
                    tempo = mido.tempo2bpm(msg.tempo)
                if msg.type == "time_signature":
                    ts = TimeSignature(msg.numerator, msg.denominator)
                if msg.type == "note_on" and msg.velocity > 0:
                    pending[(msg.channel, msg.note)] = (abs_tick, msg.velocity)
                elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                    key = (msg.channel, msg.note)
                    if key in pending:
                        start_tick, vel = pending.pop(key)
                        tpb = mid.ticks_per_beat
                        start_sec = mido.tick2second(start_tick, tpb, current_tempo)
                        end_sec = mido.tick2second(abs_tick, tpb, current_tempo)
                        dur = max(0, end_sec - start_sec)
                        notes.append(Note(
                            pitch=msg.note, velocity=vel,
                            start=start_sec, duration=dur,
                            channel=msg.channel,
                        ))
        
        return cls(notes=notes, tempo=tempo, time_signature=ts)

    def to_midi(self, path: str, ticks_per_beat: int = 480) -> None:
        """Write to a MIDI file."""
        import mido
        mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
        track = mido.MidiTrack()
        track.append(mido.MetaMessage(
            "set_tempo", tempo=mido.bpm2tempo(self.tempo), time=0))
        track.append(mido.MetaMessage(
            "time_signature",
            numerator=self.time_signature.numerator,
            denominator=self.time_signature.denominator,
            time=0))
        
        events: List[Tuple[float, mido.Message]] = []
        for n in self.notes:
            tpb = ticks_per_beat
            tempo_us = mido.bpm2tempo(self.tempo)
            on_tick = int(mido.second2tick(n.start, tpb, tempo_us))
            off_tick = int(mido.second2tick(n.end, tpb, tempo_us))
            events.append((on_tick, mido.Message(
                "note_on", channel=n.channel, note=n.pitch,
                velocity=n.velocity)))
            events.append((off_tick, mido.Message(
                "note_on", channel=n.channel, note=n.pitch,
                velocity=0)))
        
        events.sort(key=lambda e: e[0])
        prev_tick = 0
        for tick, msg in events:
            msg.time = max(0, tick - prev_tick)
            track.append(msg)
            prev_tick = tick
        track.append(mido.MetaMessage("end_of_track", time=0))
        mid.tracks.append(track)
        mid.save(path)

    # ── Transformations (return new Score) ──

    def with_notes(self, notes: List[Note]) -> "Score":
        """Return a copy with different notes (same metadata)."""
        return Score(
            notes=notes, tempo=self.tempo,
            key=self.key, time_signature=self.time_signature,
            metadata={**self.metadata},
        )

    def quantize(self, grid: str = "16th") -> "Score":
        """Quantize note start times to the given grid."""
        grid_map = {"16th": 0.25, "8th": 0.5, "quarter": 1.0, "half": 2.0}
        beat_dur = grid_map.get(grid, 0.25) * (60.0 / self.tempo)
        snapped = []
        for n in self.notes:
            beat_pos = n.start * self.tempo / 60.0
            nearest = round(beat_pos / (beat_dur * self.tempo / 60.0))
            new_start = nearest * beat_dur * self.tempo / 60.0
            snapped.append(Note(
                pitch=n.pitch, velocity=n.velocity,
                start=new_start, duration=n.duration,
                channel=n.channel,
            ))
        return self.with_notes(snapped)

    def slice(self, start: float, end: float) -> "Score":
        """Return notes within [start, end)."""
        return self.with_notes([
            n for n in self.notes if n.start >= start and n.end <= end
        ])

    # ── Properties ──

    @property
    def duration(self) -> float:
        if not self.notes:
            return 0.0
        return max(n.end for n in self.notes)

    @property
    def channels(self) -> FrozenSet[int]:
        return frozenset(n.channel for n in self.notes)

    def __len__(self) -> int:
        return len(self.notes)


# ── Analysis results (not Scores — they're endpoints) ──────────────────

@dataclass(frozen=True, slots=True)
class HarmonyResult:
    """Output of harmonic analysis."""
    chords: List[Dict]           # List of chord dicts from holonomy-harmony
    holonomy_score: float        # Overall holonomy consistency
    modulations: List[Dict]      # Detected key changes
    stability: float             # 0-1 stability score
    adventurousness: float       # 0-1 adventurousness score


@dataclass(frozen=True, slots=True)
class GrooveResult:
    """Output of groove analysis / application."""
    timing: Dict                 # Microtiming summary per channel
    deadband_fit: Dict           # Deadband funnel parameters
    swing_factor: float          # 0-1
    pocket_width_ms: float       # Groove pocket width


@dataclass(frozen=True, slots=True)
class SmoothingResult:
    """Output of spline smoothing."""
    notes: List[Note]            # Smoothed notes
    method: str                  # Which spline was used
    cc_stats: Dict               # Per-CC smoothing stats


# ── Adapter functions: repo-specific ↔ shared types ────────────────────

def note_from_plato(ev: "NoteEvent") -> Note:
    """Convert plato-room-musician NoteEvent → shared Note."""
    # Assumes 120 BPM for beat→second conversion
    beat_to_sec = 60.0 / 120.0  # will need tempo context in practice
    return Note(
        pitch=ev.pitch,
        velocity=ev.velocity,
        start=ev.onset_beats * beat_to_sec,
        duration=ev.duration_beats * beat_to_sec,
        channel=ev.channel,
    )


def note_to_onset_event(n: Note, tempo: float, track_name: str = "") -> "OnsetEvent":
    """Convert shared Note → groove-analyzer OnsetEvent."""
    from groove_analyzer.microtiming import OnsetEvent, TimingClass
    beat = n.start * tempo / 60.0
    return OnsetEvent(
        time_sec=n.start,
        beat=beat,
        pitch=n.pitch,
        velocity=n.velocity,
        channel=n.channel,
        track_name=track_name,
        grid_line=round(beat * 4) / 4,  # 16th note grid
        deviation_ms=0.0,
        timing_class=TimingClass.POCKET,
    )


def counterpoint_result_to_score(result: "CounterpointResult", tempo: float = 120.0) -> Score:
    """Convert counterpoint-engine output → Score."""
    beat_dur = 60.0 / tempo
    notes = []
    for voice_idx, voice in enumerate(result.voices):
        for beat, pitch in enumerate(voice):
            if pitch > 0:  # skip rests (pitch=0 convention)
                notes.append(Note(
                    pitch=pitch,
                    velocity=result.velocities[voice_idx][beat] if hasattr(result, 'velocities') else 100,
                    start=beat * beat_dur,
                    duration=beat_dur,
                    channel=voice_idx,
                ))
    return Score(notes=notes, tempo=tempo)
```

### Why This Design

1. **`Note` is frozen and minimal** — it captures only what *every* repo needs. Room/agent/category are PLATO-specific and go in `Score.metadata`.
2. **`Score` is mutable but copy-friendly** — `with_notes()` returns a new Score, enabling pydub-style chaining without the overhead of full immutability.
3. **`from_midi`/`to_midi` on Score** — I/O lives on the central type, like librosa's `load`/`save`.
4. **Adapter functions** — no circular imports; each repo stays independent. The integration layer owns the glue.

---

## Part 2: Pipeline Designs

### Design A: Method Chaining (pydub-style)

```python
score = (
    Score.from_midi("input.mid")
    .analyze_harmony()              # → Score (harmony attached in metadata)
    .apply_counterpoint(species=4)  # → Score with added voices
    .apply_groove("funk")           # → Score with microtiming deviations
    .smooth_dynamics("catmull_rom") # → Score with smoothed velocity
    .to_midi("output.mid")
)
```

**How it works:** Score has methods that import and delegate to each repo. Each method returns a new `Score`.

```python
# In a mixin or extension module:

class ScorePipelineMixin:
    def analyze_harmony(self) -> "Score":
        from holonomy_harmony import analyze_progression, parse_roman
        from constraint_music_types import HarmonyResult
        
        # Build chord list from simultaneous notes
        chords = self._extract_chords()
        result = analyze_progression(chords, key=self.key)
        
        new_meta = {**self.metadata, "harmony": HarmonyResult(
            chords=result["chords"],
            holonomy_score=result["holonomy_score"],
            modulations=result["modulations"],
            stability=result["stability"],
            adventurousness=result["adventurousness"],
        )}
        return Score(
            notes=self.notes, tempo=self.tempo,
            key=self.key, time_signature=self.time_signature,
            metadata=new_meta,
        )
    
    def apply_groove(self, genre: str) -> "Score":
        from groove_analyzer import synthesize_groove, GENRE_PROFILES
        
        profile = GENRE_PROFILES[genre]
        groove = synthesize_groove(profile, n_beats=self.duration * self.tempo / 60)
        
        deviated_notes = []
        for n in self.notes:
            beat = n.start * self.tempo / 60.0
            offset = groove.get_deviation(beat, n.channel)
            deviated_notes.append(Note(
                pitch=n.pitch, velocity=n.velocity,
                start=n.start + offset, duration=n.duration,
                channel=n.channel,
            ))
        return self.with_notes(deviated_notes)
    
    def smooth_dynamics(self, method: str = "catmull_rom") -> "Score":
        from spline_midi_smooth import smooth_velocity_curve
        
        # Extract velocity curve, smooth it, reapply
        smoothed = smooth_velocity_curve(
            [(n.start, n.velocity) for n in self.notes],
            method=method,
        )
        new_notes = [
            Note(pitch=n.pitch, velocity=int(smoothed[i]),
                 start=n.start, duration=n.duration, channel=n.channel)
            for i, n in enumerate(self.notes)
        ]
        return self.with_notes(new_notes)
```

**Pros:**
- Most readable for simple workflows
- Familiar to anyone who's used pydub or pandas
- IDE autocomplete works well (discoverability)
- Lazy to learn — just `score.method()`

**Cons:**
- Score class becomes a god object with 15+ methods
- Every new package adds methods to Score (open-closed violation)
- Can't easily reorder steps or conditionally skip
- Analysis methods that return non-Score types break the chain
- Testing requires the full Score object

**Best fits:** Quick scripts, notebooks, one-liner demos

---

### Design B: Builder Pattern (fluent API)

```python
score = (
    MusicPipeline()
    .load("input.mid")
    .analyze_harmony(key="C major")
    .add_counterpoint(species=4, n_voices=3)
    .apply_groove("funk", intensity=0.7)
    .smooth_dynamics("catmull_rom")
    .render("output.mid")
    .run()  # or .build() for lazy execution
)
```

**How it works:** A `MusicPipeline` builder accumulates steps, then executes them.

```python
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Protocol


class PipelineStep(Protocol):
    """A single step in the music pipeline."""
    name: str
    
    def process(self, score: "Score") -> "Score":
        ...


@dataclass
class PipelineResult:
    score: "Score"
    artifacts: Dict[str, Any] = field(default_factory=dict)
    log: List[str] = field(default_factory=list)


class MusicPipeline:
    """Fluent builder for music processing pipelines.
    
    Steps are accumulated but not executed until run() or build().
    This allows introspection, reordering, and conditional assembly.
    """
    
    def __init__(self):
        self._steps: List[PipelineStep] = []
        self._config: Dict[str, Any] = {}
    
    # ── Source ──
    
    def load(self, path: str) -> "MusicPipeline":
        self._steps.append(_LoadStep(path))
        return self
    
    def from_score(self, score: "Score") -> "MusicPipeline":
        self._steps.append(_InitStep(score))
        return self
    
    def from_counterpoint(self, cantus_firmus: List[int], species: int = 1) -> "MusicPipeline":
        self._steps.append(_CounterpointSourceStep(cantus_firmus, species))
        return self
    
    # ── Analysis (side effects, don't transform notes) ──
    
    def analyze_harmony(self, **kwargs) -> "MusicPipeline":
        self._steps.append(_HarmonyAnalysisStep(**kwargs))
        return self
    
    def analyze_groove(self) -> "MusicPipeline":
        self._steps.append(_GrooveAnalysisStep())
        return self
    
    # ── Transforms (change the notes) ──
    
    def add_counterpoint(self, species: int = 1, n_voices: int = 1) -> "MusicPipeline":
        self._steps.append(_CounterpointTransformStep(species, n_voices))
        return self
    
    def apply_groove(self, genre: str, intensity: float = 1.0) -> "MusicPipeline":
        self._steps.append(_GrooveApplyStep(genre, intensity))
        return self
    
    def smooth_dynamics(self, method: str = "catmull_rom") -> "MusicPipeline":
        self._steps.append(_SmoothDynamicsStep(method))
        return self
    
    def quantize(self, grid: str = "16th") -> "MusicPipeline":
        self._steps.append(_QuantizeStep(grid))
        return self
    
    def snap_to_lattice(self) -> "MusicPipeline":
        """Snap pitches to nearest A₂ lattice point."""
        self._steps.append(_LatticeSnapStep())
        return self
    
    def apply_deadband(self, semitones: int = 2, velocity_threshold: int = 10) -> "MusicPipeline":
        self._steps.append(_DeadbandFilterStep(semitones, velocity_threshold))
        return self
    
    # ── Sinks ──
    
    def render(self, path: str, format: str = "midi") -> "MusicPipeline":
        self._steps.append(_RenderStep(path, format))
        return self
    
    def render_tensor_midi(self, path: str) -> "MusicPipeline":
        self._steps.append(_TensorMidiRenderStep(path))
        return self
    
    def render_vms(self, path: str) -> "MusicPipeline":
        self._steps.append(_VMSRenderStep(path))
        return self
    
    # ── Execution ──
    
    def run(self) -> PipelineResult:
        """Execute all steps eagerly."""
        result = PipelineResult(score=Score(notes=[]))
        for step in self._steps:
            result.score = step.process(result.score)
            result.log.append(f"✓ {step.name}")
        return result
    
    def build(self) -> "BuiltPipeline":
        """Return a reusable pipeline object (for lazy/repeated execution)."""
        return BuiltPipeline(self._steps[:])
    
    # ── Introspection ──
    
    def describe(self) -> List[str]:
        return [step.name for step in self._steps]
    
    def insert_before(self, target: str, step: PipelineStep) -> "MusicPipeline":
        idx = next(i for i, s in enumerate(self._steps) if s.name == target)
        self._steps.insert(idx, step)
        return self
    
    def remove(self, name: str) -> "MusicPipeline":
        self._steps = [s for s in self._steps if s.name != name]
        return self


class BuiltPipeline:
    """An immutable, reusable pipeline."""
    
    def __init__(self, steps: List[PipelineStep]):
        self._steps = steps
    
    def __call__(self, score: "Score") -> PipelineResult:
        result = PipelineResult(score=score)
        for step in self._steps:
            result.score = step.process(result.score)
            result.log.append(f"✓ {step.name}")
        return result


# ── Concrete step implementations ──

@dataclass
class _LoadStep:
    name: str = "load"
    path: str = ""
    
    def __post_init__(self, path: str = ""):
        if path:
            self.path = path
    
    def process(self, score: "Score") -> "Score":
        return Score.from_midi(self.path)


@dataclass
class _HarmonyAnalysisStep:
    name: str = "analyze_harmony"
    key: Optional[str] = None
    
    def process(self, score: "Score") -> "Score":
        from holonomy_harmony import analyze_progression, Chord
        from constraint_music_types import HarmonyResult
        
        chords = _extract_chords_from_score(score)
        result = analyze_progression(chords, key=score.key)
        
        harmony = HarmonyResult(
            chords=result.get("chords", []),
            holonomy_score=result.get("holonomy_score", 0.0),
            modulations=result.get("modulations", []),
            stability=result.get("stability", 0.0),
            adventurousness=result.get("adventurousness", 0.0),
        )
        new_meta = {**score.metadata, "harmony": harmony}
        return Score(
            notes=score.notes, tempo=score.tempo,
            key=score.key, time_signature=score.time_signature,
            metadata=new_meta,
        )


@dataclass
class _GrooveApplyStep:
    name: str = "apply_groove"
    genre: str = "funk"
    intensity: float = 1.0
    
    def process(self, score: "Score") -> "Score":
        from groove_analyzer import synthesize_groove, GENRE_PROFILES
        
        profile = GENRE_PROFILES[self.genre]
        n_beats = score.duration * score.tempo / 60.0
        groove = synthesize_groove(profile, n_beats=n_beats)
        
        deviated = []
        for n in score.notes:
            beat = n.start * score.tempo / 60.0
            offset_sec = groove.get_deviation(beat, n.channel) * self.intensity * 0.001
            deviated.append(Note(
                pitch=n.pitch, velocity=n.velocity,
                start=n.start + offset_sec, duration=n.duration,
                channel=n.channel,
            ))
        return score.with_notes(deviated)


@dataclass
class _SmoothDynamicsStep:
    name: str = "smooth_dynamics"
    method: str = "catmull_rom"
    
    def process(self, score: "Score") -> "Score":
        from spline_midi_smooth import smooth_velocity_curve
        
        curve = [(n.start, n.velocity) for n in score.notes]
        smoothed = smooth_velocity_curve(curve, method=self.method)
        
        new_notes = [
            Note(pitch=n.pitch, velocity=int(smoothed[i]),
                 start=n.start, duration=n.duration, channel=n.channel)
            for i, n in enumerate(score.notes)
        ]
        return score.with_notes(new_notes)
```

**Pros:**
- Clean separation: Score is data, Pipeline is behavior
- Steps are reusable, testable, composable
- Can inspect/reorder/conditionally add steps before running
- `BuiltPipeline` enables reuse (like sklearn's fitted pipeline)
- Each step can have its own error handling
- New packages just add new step classes — no Score modification

**Cons:**
- More verbose than method chaining
- Two-phase (build then run) is slightly harder to grasp
- Step protocol needs discipline (what goes in artifacts vs metadata)
- More boilerplate per step

**Best fits:** Production workflows, reusable pipelines, complex multi-step chains

---

### Design C: Functional Pipeline (toolz/flupy-style)

```python
from constraint_music_pipeline import pipe, P

result = pipe(
    Score.from_midi("input.mid"),
    P.analyze_harmony(),
    P.add_counterpoint(species=4),
    P.apply_groove("funk"),
    P.smooth_dynamics("catmull_rom"),
    P.render("output.mid"),
)
```

**How it works:** Pure functions + a threading `pipe` combinator.

```python
from functools import wraps
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def pipe(initial: T, *steps: Callable) -> Any:
    """Thread a value through a sequence of transform functions.
    
    Equivalent to: steps[-1](...(steps[1](steps[0](initial))))
    """
    result = initial
    for step in steps:
        result = step(result)
    return result


class P:
    """Namespace for pipeline step factories.
    
    Each method returns a callable (Score → Score or Score → result).
    """
    
    @staticmethod
    def analyze_harmony(**kwargs):
        def step(score):
            from holonomy_harmony import analyze_progression
            chords = _extract_chords_from_score(score)
            result = analyze_progression(chords, key=score.key)
            harmony = HarmonyResult(
                chords=result.get("chords", []),
                holonomy_score=result.get("holonomy_score", 0.0),
                modulations=result.get("modulations", []),
                stability=result.get("stability", 0.0),
                adventurousness=result.get("adventurousness", 0.0),
            )
            return Score(
                notes=score.notes, tempo=score.tempo,
                key=score.key, time_signature=score.time_signature,
                metadata={**score.metadata, "harmony": harmony},
            )
        return step
    
    @staticmethod
    def add_counterpoint(species=1, n_voices=1):
        def step(score):
            from counterpoint_engine import CounterpointGenerator
            # Extract cantus firmus from lowest channel
            bass = [n for n in score.notes if n.channel == 0]
            cf = [n.pitch for n in sorted(bass, key=lambda n: n.start)]
            gen = CounterpointGenerator(species=species)
            result = gen.generate(cf)
            return counterpoint_result_to_score(result, tempo=score.tempo)
        return step
    
    @staticmethod
    def apply_groove(genre: str, intensity: float = 1.0):
        def step(score):
            from groove_analyzer import synthesize_groove, GENRE_PROFILES
            profile = GENRE_PROFILES[genre]
            n_beats = score.duration * score.tempo / 60.0
            groove = synthesize_groove(profile, n_beats=n_beats)
            deviated = [
                Note(pitch=n.pitch, velocity=n.velocity,
                     start=n.start + groove.get_deviation(
                         n.start * score.tempo / 60, n.channel) * intensity * 0.001,
                     duration=n.duration, channel=n.channel)
                for n in score.notes
            ]
            return score.with_notes(deviated)
        return step
    
    @staticmethod
    def smooth_dynamics(method: str = "catmull_rom"):
        def step(score):
            from spline_midi_smooth import smooth_velocity_curve
            curve = [(n.start, n.velocity) for n in score.notes]
            smoothed = smooth_velocity_curve(curve, method=method)
            return score.with_notes([
                Note(pitch=n.pitch, velocity=int(smoothed[i]),
                     start=n.start, duration=n.duration, channel=n.channel)
                for i, n in enumerate(score.notes)
            ])
        return step
    
    @staticmethod
    def render(path: str, format: str = "midi"):
        def step(score):
            score.to_midi(path)
            return score
        return step
    
    @staticmethod
    def tap(fn: Callable):
        """Side-effect step that doesn't modify the score (logging, etc)."""
        def step(score):
            fn(score)
            return score
        return step
    
    @staticmethod
    def filter(predicate: Callable[["Note"], bool]):
        """Keep only notes matching predicate."""
        def step(score):
            return score.with_notes([n for n in score.notes if predicate(n)])
        return step
    
    @staticmethod
    def map_notes(fn: Callable[["Note"], "Note"]):
        """Transform each note individually."""
        def step(score):
            return score.with_notes([fn(n) for n in score.notes])
        return step
```

**Pros:**
- Simplest mental model: value goes in, value comes out
- Composable with any function (`pipe(score, step1, custom_fn, step2)`)
- Easy to add ad-hoc steps inline (lambdas, closures)
- `tap`, `filter`, `map_notes` give functional toolkit
- No classes to learn — just functions
- Works great with type checkers (generic `pipe[T]`)

**Cons:**
- No introspection (can't list steps before running)
- Error messages can be opaque (which step failed?)
- Less discoverable than methods (no autocomplete on `P.`)
- Closures capture args at definition time — subtle bugs possible
- Can't easily serialize/deserialize a pipeline

**Best fits:** Scripts, notebooks, functional-programming fans, quick prototyping

---

## Part 3: Which Design Wins

### Winner: **Design B — Builder Pattern** (with concessions to A and C)

Here's the reasoning:

| Criterion | Method Chaining (A) | Builder (B) | Functional (C) |
|---|---|---|---|
| **Ease of learning** | ⭐⭐⭐⭐⭐ (just call methods) | ⭐⭐⭐⭐ (build→run) | ⭐⭐⭐ (need to understand closures) |
| **Composability** | ⭐⭐ (hard to reorder) | ⭐⭐⭐⭐⭐ (insert/remove/reorder) | ⭐⭐⭐⭐⭐ (any function works) |
| **Error handling** | ⭐⭐⭐ (try/except around chain) | ⭐⭐⭐⭐⭐ (per-step try/except, named steps) | ⭐⭐ (which closure failed?) |
| **Type safety** | ⭐⭐⭐⭐ (methods typed on Score) | ⭐⭐⭐⭐ (PipelineStep protocol) | ⭐⭐⭐ (generic Callable) |
| **Discoverability** | ⭐⭐⭐⭐⭐ (autocomplete) | ⭐⭐⭐⭐ (autocomplete on builder) | ⭐⭐⭐ (P. namespace helps) |
| **Open-closed** | ⭐ (modifies Score) | ⭐⭐⭐⭐⭐ (new Step classes) | ⭐⭐⭐⭐⭐ (any callable) |
| **Reusability** | ⭐⭐⭐ (re-call methods) | ⭐⭐⭐⭐⭐ (BuiltPipeline) | ⭐⭐⭐⭐ (pipe + same steps) |

**Why Builder wins:**

1. **The ecosystem will grow.** Each new package (music-theory-analyzer, tensor-midi-synth, live-performance-engine) adds pipeline steps. The builder pattern means we never touch the Score class — we just add new `_FooStep` dataclasses. This is the open-closed principle at work, and it's why sklearn's Pipeline is more maintainable than a monolithic Estimator.

2. **Error handling matters for music.** A groove application that fails on bar 47 shouldn't silently corrupt the score. Per-step error handling with `result.log` means you get a full audit trail: which steps succeeded, which failed, and the intermediate Score state at each point.

3. **Introspection is table stakes.** `pipeline.describe()` gives you `["load", "analyze_harmony", "add_counterpoint", "apply_groove", "smooth_dynamics", "render"]`. This is essential for debugging and documentation. Neither chaining nor functional gives you this for free.

4. **BuiltPipeline enables sharing.** A user builds a pipeline once, then reuses it on 100 MIDI files. This is the sklearn pattern (fit once, transform many), and it's why sklearn pipelines are so popular.

### The Compromise

We also provide:
- **Design A's convenience** via `Score.quick()` — a shortcut that builds and runs a common pipeline:
  ```python
  score.quick("analyze→groove→smooth", genre="funk").to_midi("out.mid")
  ```
- **Design C's composability** via `pipe()` as a standalone utility for one-off scripts:
  ```python
  from constraint_music_pipeline import pipe, P
  pipe(Score.from_midi("in.mid"), P.apply_groove("funk"), P.render("out.mid"))
  ```

This is the same approach polars takes: you can use the Lazy API (builder), the eager API (chaining), or raw expressions (functional) — they all work on the same DataFrame.

---

## Part 4: Implementation Plan

### File Structure

```
constraint-music-pipeline/          ← new standalone repo
├── pyproject.toml
├── README.md
├── constraint_music_pipeline/
│   ├── __init__.py                 ← public API exports
│   ├── types.py                    ← Note, Score, HarmonyResult, GrooveResult, etc.
│   ├── adapters.py                 ← conversion functions between repos
│   ├── pipeline.py                 ← MusicPipeline, BuiltPipeline, PipelineStep protocol
│   ├── steps/
│   │   ├── __init__.py             ← re-exports all steps
│   │   ├── io.py                   ← _LoadStep, _RenderStep, _InitStep
│   │   ├── harmony.py             ← _HarmonyAnalysisStep
│   │   ├── counterpoint.py        ← _CounterpointSourceStep, _CounterpointTransformStep
│   │   ├── groove.py              ← _GrooveAnalysisStep, _GrooveApplyStep
│   │   ├── smooth.py              ← _SmoothDynamicsStep
│   │   ├── lattice.py             ← _LatticeSnapStep, _DeadbandFilterStep
│   │   └── plato.py               ← _PlatoRoomSourceStep, _VMSRenderStep, _TensorMidiRenderStep
│   ├── functional.py               ← pipe(), P namespace
│   └── quick.py                    ← Score.quick() shortcut mixin
├── tests/
│   ├── test_types.py
│   ├── test_pipeline.py
│   ├── test_functional.py
│   ├── test_adapters.py
│   └── test_integration.py         ← end-to-end with all repos
└── examples/
    ├── basic_pipeline.py
    ├── counterpoint_to_groove.py
    ├── plato_orchestra.py
    └── full_stack.py
```

### Dependencies

```toml
[project]
name = "constraint-music-pipeline"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "mido>=1.3",
    "numpy>=1.24",
]

[project.optional-dependencies]
# Full stack — pulls in everything
all = [
    "constraint-theory-core>=0.1.0",
    "counterpoint-engine>=0.1.0",
    "groove-analyzer>=0.1.0",
    "holonomy-harmony>=0.1.0",
    "spline-midi-smooth>=0.1.0",
    "plato-room-musician>=0.1.0",
]
# Individual — import only what you need
harmony = ["holonomy-harmony>=0.1.0", "constraint-theory-core>=0.1.0"]
counterpoint = ["counterpoint-engine>=0.1.0", "constraint-theory-core>=0.1.0"]
groove = ["groove-analyzer>=0.1.0", "constraint-theory-core>=0.1.0"]
smooth = ["spline-midi-smooth>=0.1.0"]
plato = ["plato-room-musician>=0.1.0"]
dev = ["pytest>=7", "pytest-cov>=4"]
```

Each step does **lazy imports** — if you never call `.apply_groove()`, you don't need `groove-analyzer` installed. This is critical for keeping the dependency graph clean.

### Implementation Order

| Phase | Task | Effort | Depends on |
|---|---|---|---|
| **1** | `types.py` — Note, Score, adapters | 2 days | Nothing |
| **2** | `pipeline.py` — MusicPipeline, PipelineStep protocol | 1 day | Phase 1 |
| **3** | `steps/io.py` — load, render (MIDI) | 1 day | Phase 1 |
| **4** | `steps/harmony.py` — harmony analysis step | 1 day | holonomy-harmony |
| **5** | `steps/counterpoint.py` — counterpoint generation step | 1 day | counterpoint-engine |
| **6** | `steps/groove.py` — groove apply step | 1 day | groove-analyzer |
| **7** | `steps/smooth.py` — dynamics smoothing step | 0.5 day | spline-midi-smooth |
| **8** | `steps/lattice.py` — snap + deadband steps | 0.5 day | constraint-theory-core |
| **9** | `steps/plato.py` — PLATO source + VMS/tensor render | 1 day | plato-room-musician |
| **10** | `functional.py` — pipe(), P namespace | 0.5 day | Phase 2 |
| **11** | `quick.py` — Score.quick() mixin | 0.5 day | Phase 2 |
| **12** | Tests + examples | 2 days | All above |
| **13** | Documentation + README | 1 day | All above |

**Total: ~12 days** for one person, assuming the 6 repos are already stable.

### Key Design Decisions

1. **New repo, not inside constraint-theory-core.** The pipeline depends on all six packages; putting it in any one of them creates a circular dependency. A thin integration repo is the standard pattern (cf. `tensorflow-estimator` vs `tensorflow`).

2. **Lazy imports in steps.** Each step's `process()` method imports its dependency. This means:
   - `pip install constraint-music-pipeline` works with zero sub-dependencies
   - You only install the repos you actually use
   - Missing dependencies raise clear `ImportError` with install instructions

3. **Score owns metadata, not behavior.** The Score type carries `metadata: Dict` for analysis results (harmony, groove, smoothing). It does NOT carry pipeline state. The pipeline owns state.

4. **Adapter functions are bidirectional.** `note_from_plato()` and `plato_events_from_score()` both exist. This lets users enter the pipeline at any point.

5. **`pipe()` is a thin wrapper.** The functional API is just `functools.reduce` over callables. It's there for convenience but the builder is the primary interface.

---

## Appendix: Comparison to Established Patterns

| Pattern | How it works | What we borrow |
|---|---|---|
| **sklearn Pipeline** | `Pipeline([("step1", transformer1), ("step2", estimator)])` — fit/transform/predict | PipelineStep protocol, BuiltPipeline reuse, per-step params |
| **pydub AudioSegment** | `song.fade_in(2000).fade_out(3000) + 6` — method chaining | Score.with_notes() returns new Score, convenience API |
| **polars LazyFrame** | `df.lazy().filter(…).select(…).collect()` — deferred execution | Builder pattern, introspection before execution |
| **toolz/flupy pipe** | `pipe(data, fn1, fn2, fn3)` — function threading | `pipe()` functional API for one-liners |
| **librosa** | Standalone functions (`librosa.stft`, `librosa.feature.mfcc`) | Each step is just a function under the hood; pipeline composes them |

The constraint-music-pipeline combines:
- **sklearn's composability** (steps as objects, reusable pipelines)
- **pydub's readability** (method chaining available via `P.` namespace)
- **polars' deferred execution** (build then run, introspect before executing)

---

## Appendix: Full End-to-End Example

```python
from constraint_music_pipeline import MusicPipeline, Score, pipe, P

# ── Builder pattern (primary API) ──

pipeline = (
    MusicPipeline()
    .load("cantus_firmus.mid")
    .snap_to_lattice()
    .analyze_harmony(key="C major")
    .add_counterpoint(species=4, n_voices=3)
    .apply_groove("jazz_swing", intensity=0.6)
    .smooth_dynamics("catmull_rom")
    .apply_deadband(semitones=1, velocity_threshold=5)
    .render("output.mid")
    .render_tensor_midi("output.tensor.bin")
    .render_vms("output.vms.json")
)

result = pipeline.run()
print(f"Pipeline: {' → '.join(result.log)}")
print(f"Notes: {len(result.score)}, Duration: {result.score.duration:.1f}s")
print(f"Harmony: {result.score.metadata['harmony'].stability:.2f} stability")

# ── Functional API (quick scripts) ──

pipe(
    Score.from_midi("input.mid"),
    P.analyze_harmony(),
    P.apply_groove("funk"),
    P.smooth_dynamics("bspline"),
    P.render("output.mid"),
)

# ── Reusable pipeline ──

standard_pipeline = (
    MusicPipeline()
    .snap_to_lattice()
    .apply_groove("funk")
    .smooth_dynamics()
    .build()
)

# Apply to 100 files
import glob
for midi_file in glob.glob("corpus/*.mid"):
    score = Score.from_midi(midi_file)
    result = standard_pipeline(score)
    result.score.to_midi(f"processed/{midi_file.name}")
```
