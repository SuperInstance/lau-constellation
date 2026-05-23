# Musical DNA — Style Extraction & Transfer System

**Decomposing a composer's style into constraint-theory parameters so it becomes a PLATO tile that can transform generations.**

---

## 0. Foundations

This system sits at the intersection of four existing codebases:

| Repo | What it gives us |
|------|-----------------|
| `constraint-theory-core` | Eisenstein lattice snap, holonomy verification, Laman rigidity, deadband funnels |
| `flux-tensor-midi` | 4D tensor representation, FluxVector (9-channel emotion), T-0 clocks, side-channels |
| `holonomy-harmony` | Chord parsing, tonal graphs, holonomy computation, modulation detection, stability scoring |
| `groove-analyzer` | GenreProfile deadband parameters, microtiming distributions, swing factor |
| `plato-room-musician` | CATEGORY_CONFIG (register, scale, rhythmic role per PLATO archetype) |
| `counterpoint-engine` | Species counterpoint rules as FLUX constraints (parallel fifths, voice independence, etc.) |
| `AI-BAND-DESIGN` | MusicianPersonality, GrooveProfile, ImprovisationConfig, RiskTolerance, FluxVector baselines |

A **StyleTile** is the natural extension: instead of defining a *genre's* deadband (as `GENRE_PROFILES` does), we define a *specific composer's* full musical fingerprint — holonomy, deadband, rigidity, melodic DNA, rhythmic DNA, harmonic DNA, register DNA, and emotional baseline — as a single frozen data structure that plugs into every layer of the system.

---

## 1. StyleTile Dataclass

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import json


@dataclass(frozen=True)
class StyleTile:
    """
    A composer's musical DNA, extracted from a corpus of MIDI files.

    This is a frozen, serializable snapshot of every musical parameter
    that the constraint-theory ecosystem cares about. It can be used to:
    - Generate music in a composer's style (StyleMorpher)
    - Compare composers (cosine distance in high-dimensional DNA space)
    - Blend styles (weighted interpolation of DNA vectors)
    - Let artists extract and evolve their own style
    """

    # ── Identity ──
    composer: str
    era: str               # "baroque", "classical", "romantic", "jazz", "modern", etc.
    corpus_size: int       # number of MIDI files analyzed
    total_bars: int        # total bars across corpus

    # ── Holonomy DNA (from holonomy-harmony) ──
    # How far does the composer drift from tonic? How do they modulate?
    holonomy_range: Tuple[float, float]       # (min, max) holonomy value across corpus
    holonomy_mean: float                      # average holonomy (0 = always returns to tonic)
    modulation_frequency: float               # modulations per 100 bars
    key_center_drift: float                   # average semitone distance from tonic per chord
    preferred_progressions: Tuple[Tuple[str, ...], ...]  # top 10 chord sequences (Roman numerals)
    stability_score: float                    # 0.0 = highly chromatic, 1.0 = purely diatonic
    secondary_dominant_rate: float            # V/x chords per 100 bars
    modal_interchange_rate: float             # borrowed chords per 100 bars

    # ── Deadband DNA (from groove-analyzer) ──
    # How tight is the timing? What's the feel?
    epsilon_range: Tuple[float, float]        # (min, max) deadband half-width in ms
    epsilon_mean: float                       # average deadband
    swing_factor: float                       # 0.0 = straight, 1.0 = full swing
    rubato_variance: float                    # tempo fluctuation (coefficient of variation)
    ahead_bias: float                         # ms: negative = pushes, positive = lays back
    microtiming_distribution: str             # "uniform", "triangular", "gaussian"
    velocity_mean: float                      # average MIDI velocity
    velocity_std: float                       # velocity standard deviation

    # ── Rigidity DNA (from counterpoint-engine) ──
    # How many voices? How strict are the rules?
    typical_voices: int                       # average number of independent voices
    voice_count_range: Tuple[int, int]        # (min, max) voices
    constraint_tightness: float               # 0.0 = loose, 1.0 = strict species counterpoint
    parallel_fifth_rate: float                # parallel fifths per 100 voice-pairs
    parallel_octave_rate: float               # parallel octaves per 100 voice-pairs
    dissonance_tolerance: float               # 0.0 = no dissonance, 1.0 = free dissonance
    max_leap_preference: int                  # preferred max melodic leap (semitones)

    # ── Melodic DNA ──
    interval_distribution: Dict[int, float]   # semitone distance → frequency (0=unison, 1=m2, ... 12=octave)
    contour_shapes: Dict[str, float]          # "ascending", "descending", "arch", "inverted_arch", "V" → frequency
    melodic_range: Tuple[int, int]            # (min, max) typical range in semitones
    climax_position: float                    # where high point occurs in phrase (0.0-1.0)
    step_vs_leap_ratio: float                 # fraction of melodic motions that are steps (≤2 semitones)
    average_interval: float                   # average absolute interval between consecutive notes
    repeated_note_rate: float                 # fraction of consecutive notes at same pitch

    # ── Rhythmic DNA ──
    duration_distribution: Dict[float, float]  # note value (beats) → frequency
    # e.g. {0.25: 0.15, 0.5: 0.35, 1.0: 0.30, 2.0: 0.15, 4.0: 0.05}
    syncopation_rate: float                    # fraction of notes landing on weak beats
    density_mean: float                        # average notes per beat
    density_variance: float                    # variance of density over time
    density_curve: Tuple[float, ...]           # normalized density over 8-beat phrase (sums to 1.0)
    rest_rate: float                           # fraction of beats that are rests
    dotted_note_rate: float                    # fraction of notes with dotted durations
    triplet_rate: float                        # fraction of notes in triplet subdivisions

    # ── Harmonic DNA ──
    chord_quality_distribution: Dict[str, float]  # "maj", "min", "7", "maj7", "min7", "dim", "aug" → frequency
    cadence_patterns: Tuple[Tuple[str, ...], ...]  # top 10 cadence sequences (last 2-4 chords)
    dissonance_rate: float                         # fraction of chords containing non-diatonic tones
    harmonic_rhythm: float                         # chord changes per beat
    seventh_chord_rate: float                      # fraction of chords that are 7ths
    extended_chord_rate: float                     # fraction that are 9ths, 11ths, 13ths

    # ── Register DNA ──
    preferred_register: Tuple[int, int]        # (low, high) MIDI pitch range (25th-75th percentile)
    register_span: int                         # typical range width in semitones
    register_centroid: float                   # average MIDI pitch
    register_distribution: Dict[int, float]    # octave (0-10) → fraction of notes

    # ── FluxVector Baseline (emotional personality, from AI-BAND-DESIGN) ──
    arousal: float       # energy level baseline (0.0-1.0)
    valence: float       # positive/negative emotional baseline (0.0-1.0)
    dominance: float     # control vs submission (0.0-1.0)
    uncertainty: float   # ambiguity tolerance (0.0-1.0)
    novelty: float       # propensity for new ideas (0.0-1.0)

    # ── Metadata ──
    extraction_timestamp: str = ""            # ISO 8601
    source_repo_version: str = "0.1.0"

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps({
            k: (list(v) if isinstance(v, tuple) else v)
            for k, v in self.__dict__.items()
        }, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, data: str) -> "StyleTile":
        """Deserialize from JSON string."""
        raw = json.loads(data)
        # Convert lists back to tuples where needed
        tuple_fields = {
            "holonomy_range", "epsilon_range", "voice_count_range",
            "melodic_range", "preferred_register", "holonomy_range",
            "preferred_progressions", "cadence_patterns", "density_curve",
        }
        for f in tuple_fields:
            if f in raw and isinstance(raw[f], list):
                if f in ("preferred_progressions", "cadence_patterns"):
                    raw[f] = tuple(tuple(x) if isinstance(x, list) else x for x in raw[f])
                else:
                    raw[f] = tuple(raw[f])
        return cls(**raw)
```

---

## 2. StyleExtractor

The extraction pipeline. Each method operates on a single MIDI file, then results are aggregated across the corpus.

### 2.1 Core Architecture

```python
from __future__ import annotations

import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Sequence

import mido

from holonomy_harmony.analyzer import (
    analyze_progression, parse_roman, Chord, ProgressionAnalysis
)
from groove_analyzer.genres import GenreProfile
from constraint_theory_core import snap, covering_radius
from counterpoint_engine.rules import (
    no_parallel_fifths, no_parallel_octaves, max_leap_seventh,
    consonant_interval, voice_independence
)


# ── Internal accumulation structures ──

@dataclass
class _HolonomyAccum:
    """Accumulator for holonomy measurements across corpus."""
    holonomy_values: List[float] = field(default_factory=list)
    modulation_counts: List[int] = field(default_factory=list)  # per piece
    drift_values: List[float] = field(default_factory=list)
    progression_counter: Counter = field(default_factory=Counter)
    stability_scores: List[float] = field(default_factory=list)
    secondary_dom_counts: List[int] = field(default_factory=list)
    modal_interchange_counts: List[int] = field(default_factory=list)
    bar_counts: List[int] = field(default_factory=list)


@dataclass
class _DeadbandAccum:
    """Accumulator for timing measurements."""
    offsets_ms: List[float] = field(default_factory=list)
    tempos: List[float] = field(default_factory=list)
    velocities: List[int] = field(default_factory=list)
    beat_ratios: List[float] = field(default_factory=list)  # for swing detection


@dataclass
class _MelodyAccum:
    """Accumulator for melodic measurements."""
    intervals: List[int] = field(default_factory=list)
    contours: List[str] = field(default_factory=list)
    ranges: List[Tuple[int, int]] = field(default_factory=list)
    climax_positions: List[float] = field(default_factory=list)
    pitches: List[int] = field(default_factory=list)


@dataclass
class _RhythmAccum:
    """Accumulator for rhythmic measurements."""
    durations: List[float] = field(default_factory=list)
    beat_positions: List[float] = field(default_factory=list)  # position within beat (0.0-1.0)
    densities: List[float] = field(default_factory=list)  # notes per beat per bar
    density_curves: List[List[float]] = field(default_factory=list)


@dataclass
class _HarmonyAccum:
    """Accumulator for harmonic measurements."""
    qualities: List[str] = field(default_factory=list)
    cadences: List[Tuple[str, ...]] = field(default_factory=list)
    dissonance_flags: List[bool] = field(default_factory=list)
    seventh_flags: List[bool] = field(default_factory=list)
    extended_flags: List[bool] = field(default_factory=list)
    chord_changes_per_beat: List[float] = field(default_factory=list)


@dataclass
class _RegisterAccum:
    """Accumulator for register measurements."""
    pitches: List[int] = field(default_factory=list)


@dataclass
class _RigidityAccum:
    """Accumulator for counterpoint rigidity measurements."""
    voice_counts: List[int] = field(default_factory=list)
    parallel_fifths: List[int] = field(default_factory=list)
    parallel_octaves: List[int] = field(default_factory=list)
    leap_sizes: List[int] = field(default_factory=list)
    dissonance_flags: List[bool] = field(default_factory=list)
```

### 2.2 The Extractor

```python
class StyleExtractor:
    """
    Extract StyleTile from a corpus of MIDI files.

    Usage:
        ext = StyleExtractor()
        tile = ext.extract(["bach_fugue_1.mid", "bach_fugue_2.mid", ...], composer="Bach")
    """

    def __init__(self, ticks_per_beat: int = 480):
        self.tpb = ticks_per_beat

    # ── Main entry point ──

    def extract(self, midi_paths: List[str], composer: str, era: str = "") -> StyleTile:
        """
        Analyze a corpus of MIDI files and extract style DNA.

        Parameters
        ----------
        midi_paths : List[str]
            Paths to MIDI files representing the composer's corpus.
        composer : str
            Composer name (e.g. "Bach", "Chopin").
        era : str
            Musical era classification. Auto-detected if empty.

        Returns
        -------
        StyleTile
        """
        if not era:
            era = self._detect_era(composer)

        # Accumulators
        hol = _HolonomyAccum()
        db = _DeadbandAccum()
        mel = _MelodyAccum()
        rhy = _RhythmAccum()
        har = _HarmonyAccum()
        reg = _RegisterAccum()
        rig = _RigidityAccum()

        total_bars = 0
        valid_files = 0

        for path in midi_paths:
            try:
                mid = mido.MidiFile(path)
            except Exception:
                continue

            notes = self._extract_notes(mid)
            if not notes:
                continue

            beats = self._estimate_beats(mid)
            bars = max(1, int(beats / 4))
            total_bars += bars
            valid_files += 1

            # Run each extraction
            self._extract_holonomy(mid, notes, bars, hol)
            self._extract_deadband(mid, notes, db)
            self._extract_melody(notes, mel)
            self._extract_rhythm(notes, beats, bars, rhy)
            self._extract_harmony(mid, notes, bars, har)
            self._extract_register(notes, reg)
            self._extract_rigidity(mid, notes, rig)

        if valid_files == 0:
            raise ValueError(f"No valid MIDI files found in {len(midi_paths)} paths")

        return self._aggregate(composer, era, valid_files, total_bars,
                               hol, db, mel, rhy, har, reg, rig)

    # ── Note extraction ──

    def _extract_notes(self, mid: mido.MidiFile) -> List[dict]:
        """
        Parse MIDI into a sorted list of note events.

        Each note: {
            'pitch': int, 'velocity': int,
            'onset_tick': int, 'offset_tick': int,
            'onset_beat': float, 'offset_beat': float,
            'duration_beats': float, 'channel': int,
            'track': int,
        }
        """
        tpb = mid.ticks_per_beat
        notes = []
        active = {}  # (channel, pitch) -> (note_on_tick, velocity, track)

        for track_idx, track in enumerate(mid.tracks):
            abs_tick = 0
            for msg in track:
                abs_tick += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    active[(msg.channel, msg.note)] = (abs_tick, msg.velocity, track_idx)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    key = (msg.channel, msg.note)
                    if key in active:
                        start_tick, vel, trk = active.pop(key)
                        dur_ticks = abs_tick - start_tick
                        if dur_ticks > 0:
                            notes.append({
                                'pitch': msg.note,
                                'velocity': vel,
                                'onset_tick': start_tick,
                                'offset_tick': abs_tick,
                                'onset_beat': start_tick / tpb,
                                'offset_beat': abs_tick / tpb,
                                'duration_beats': dur_ticks / tpb,
                                'channel': msg.channel,
                                'track': trk,
                            })

        notes.sort(key=lambda n: (n['onset_tick'], n['pitch']))
        return notes

    def _estimate_beats(self, mid: mido.MidiFile) -> float:
        """Estimate total number of beats from MIDI file."""
        tpb = mid.ticks_per_beat
        total_ticks = sum(
            sum(msg.time for msg in track) for track in mid.tracks
        )
        # Use the longest track
        max_ticks = max(sum(msg.time for msg in track) for track in mid.tracks)
        return max_ticks / tpb

    def _detect_era(self, composer: str) -> str:
        """Simple era detection from composer name."""
        era_map = {
            "Bach": "baroque", "Handel": "baroque", "Vivaldi": "baroque",
            "Scarlatti": "baroque", "Monteverdi": "baroque", "Corelli": "baroque",
            "Mozart": "classical", "Haydn": "classical", "Beethoven": "classical",
            "Clementi": "classical", "Gluck": "classical",
            "Chopin": "romantic", "Liszt": "romantic", "Schumann": "romantic",
            "Brahms": "romantic", "Wagner": "romantic", "Schubert": "romantic",
            "Tchaikovsky": "romantic", "Dvorak": "romantic", "Mendelssohn": "romantic",
            "Debussy": "modern", "Ravel": "modern", "Stravinsky": "modern",
            "Schoenberg": "modern", "Bartok": "modern",
            "Joplin": "ragtime", "Morton": "jazz", "Ellington": "jazz",
            "Parker": "jazz", "Monk": "jazz", "Davis": "jazz",
            "Coltrane": "jazz",
        }
        lower = composer.lower()
        for name, era in era_map.items():
            if name.lower() in lower:
                return era
        return "unknown"

    # ── Holonomy extraction ──

    def _extract_holonomy(self, mid, notes, bars, acc: _HolonomyAccum):
        """
        Measure harmonic drift from tonic using holonomy-harmony.

        Algorithm:
        1. Detect key from pitch class distribution (Krumhansl-Schmuckler)
        2. Segment notes into beat-level chord slices
        3. Identify each chord's root and quality
        4. Track cumulative root movement in semitones from tonic
        5. The holonomy is the net drift after a full section/cycle

        Measurements:
        - holonomy: cumulative semitone drift from tonic over each phrase
        - modulation count: number of key changes detected
        - drift: average absolute semitone distance from tonic
        - progressions: n-gram chord sequences
        """
        if bars < 4 or not notes:
            return

        # Step 1: Key detection via pitch class distribution
        pc_counts = Counter()
        for n in notes:
            pc_counts[n['pitch'] % 12] += 1

        key_tonic, mode = self._detect_key(pc_counts)

        # Step 2: Segment into beat-level windows, detect chords
        chords_raw = self._detect_chords_beatwise(notes, key_tonic, mode)

        if len(chords_raw) < 4:
            return

        # Step 3: Compute holonomy — track cumulative root drift
        cumulative = 0.0
        phrase_drifts = []
        for i, chord in enumerate(chords_raw):
            interval = (chord['root'] - key_tonic) % 12
            # Use shortest path on circle of fifths
            if interval > 6:
                interval -= 12
            cumulative += interval * 0.1  # scale down for smoothing
            phrase_drifts.append(abs(interval))

            # Reset at cadence points (V-I, IV-I)
            if i >= 1:
                prev_root = chords_raw[i - 1]['root']
                curr_root = chord['root']
                # Perfect cadence: root movement of 5→0 or 7→0 semitones
                if (prev_root - curr_root) % 12 == 7:
                    acc.holonomy_values.append(cumulative)
                    cumulative = 0.0

        # Average drift from tonic
        acc.drift_values.extend(phrase_drifts)
        acc.bar_counts.append(bars)

        # Step 4: Extract progressions (3-grams)
        roots = [c['root_name'] for c in chords_raw]
        for i in range(len(roots) - 3):
            trigram = tuple(roots[i:i+3])
            acc.progression_counter[trigram] += 1

        # Step 5: Estimate modulations
        # A modulation is where the dominant pitch class shifts for >4 beats
        mod_count = self._count_modulations(chords_raw, key_tonic)
        acc.modulation_counts.append(mod_count)

        # Step 6: Stability score (reuse holonomy-harmony logic)
        roman_symbols = self._infer_roman_numerals(chords_raw, key_tonic, mode)
        if len(roman_symbols) >= 4:
            try:
                analysis = analyze_progression(roman_symbols, key_tonic, mode)
                acc.stability_scores.append(analysis.stability_score)
                sec_dom = sum(1 for c in analysis.chords if c.is_secondary_dominant)
                modal_int = sum(1 for c in analysis.chords
                               if not c.is_diatonic and not c.is_secondary_dominant)
                acc.secondary_dom_counts.append(sec_dom)
                acc.modal_interchange_counts.append(modal_int)
            except Exception:
                pass

    def _detect_key(self, pc_counts: Counter) -> Tuple[int, str]:
        """
        Krumhansl-Schmuckler key-finding algorithm.

        Correlate pitch class distribution against major/minor key profiles.
        Returns (tonic_pc, "major"|"minor").
        """
        # Krumhansl-Kessler key profiles
        major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19,
                         2.39, 3.66, 2.29, 2.88]
        minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75,
                         3.98, 2.69, 3.34, 3.17]

        total = sum(pc_counts.values()) or 1
        distribution = [pc_counts.get(i, 0) / total for i in range(12)]

        best_corr = -1.0
        best_key = (0, "major")

        for shift in range(12):
            for profile, mode in [(major_profile, "major"), (minor_profile, "minor")]:
                rotated = [profile[(i + shift) % 12] for i in range(12)]
                # Pearson correlation
                n = 12
                sum_x = sum(distribution)
                sum_y = sum(rotated)
                sum_xy = sum(distribution[i] * rotated[i] for i in range(n))
                sum_x2 = sum(x * x for x in distribution)
                sum_y2 = sum(y * y for y in rotated)
                denom = math.sqrt(max(0, (n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2)))
                corr = (n * sum_xy - sum_x * sum_y) / denom if denom > 0 else 0
                if corr > best_corr:
                    best_corr = corr
                    best_key = (shift, mode)

        return best_key

    def _detect_chords_beatwise(self, notes, key_tonic, mode) -> List[dict]:
        """
        Segment notes into beat-aligned windows and detect chords.

        Algorithm:
        1. Create 1-beat windows from first note onset to last offset
        2. For each window, collect all sounding pitches
        3. Determine chord root via bass note (lowest pitch) or PC frequency
        4. Determine quality by interval analysis
        """
        if not notes:
            return []

        min_beat = math.floor(notes[0]['onset_beat'])
        max_beat = math.ceil(notes[-1]['offset_beat'])

        PITCH_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        chords = []
        for beat in range(int(min_beat), int(max_beat)):
            # Collect pitches sounding during this beat
            sounding = set()
            for n in notes:
                if n['onset_beat'] <= beat + 0.5 and n['offset_beat'] > beat:
                    sounding.add(n['pitch'] % 12)

            if len(sounding) < 2:
                continue

            pcs = sorted(sounding)
            root = self._detect_chord_root(pcs)
            quality = self._detect_chord_quality(pcs, root)

            chords.append({
                'beat': beat,
                'root': root,
                'root_name': PITCH_NAMES[root],
                'quality': quality,
                'pcs': pcs,
            })

        return chords

    def _detect_chord_root(self, pcs: List[int]) -> int:
        """
        Detect chord root from pitch classes.
        Strategy: bass note (lowest) + verify against common chord templates.
        """
        if not pcs:
            return 0

        # Try each PC as root, score against chord templates
        templates = {
            0: [0, 4, 7],      # major triad
            1: [0, 3, 7],      # minor triad
            2: [0, 4, 7, 10],  # dominant 7th
            3: [0, 3, 7, 10],  # minor 7th
            4: [0, 4, 7, 11],  # major 7th
            5: [0, 3, 6],      # diminished
        }

        best_score = -1
        best_root = pcs[0]

        for candidate_root in pcs:
            intervals = sorted((pc - candidate_root) % 12 for pc in pcs)
            for template in templates.values():
                score = sum(1 for t in template if t in intervals)
                if score > best_score:
                    best_score = score
                    best_root = candidate_root

        return best_root

    def _detect_chord_quality(self, pcs: List[int], root: int) -> str:
        """Detect chord quality from intervals above root."""
        intervals = set((pc - root) % 12 for pc in pcs)
        has_m3 = 3 in intervals
        has_M3 = 4 in intervals
        has_P5 = 7 in intervals
        has_m7 = 10 in intervals
        has_M7 = 11 in intervals
        has_dim5 = 6 in intervals

        if has_M3 and has_P5 and has_M7:
            return "maj7"
        if has_M3 and has_P5 and has_m7:
            return "7"
        if has_m3 and has_P5 and has_m7:
            return "m7"
        if has_m3 and has_P5:
            return "min"
        if has_M3 and has_P5:
            return "maj"
        if has_m3 and has_dim5:
            return "dim"
        if has_M3 and has_dim5:
            return "aug"
        if has_m3:
            return "min"
        if has_M3:
            return "maj"
        return "maj"

    def _count_modulations(self, chords, key_tonic) -> int:
        """Count modulations by tracking sustained root shifts."""
        if len(chords) < 8:
            return 0

        modulations = 0
        window_size = 8  # Look at 8-beat windows
        for i in range(len(chords) - window_size):
            window = chords[i:i + window_size]
            roots = [c['root'] for c in window]
            # If >60% of roots center on a non-tonic pitch class
            most_common = Counter(roots).most_common(1)[0][0]
            if most_common != key_tonic:
                # Check if this new center persists
                if i + window_size < len(chords):
                    next_window = chords[i + window_size // 2:i + window_size + window_size // 2]
                    if next_window:
                        next_common = Counter(c['root'] for c in next_window).most_common(1)[0][0]
                        if next_common == most_common:
                            modulations += 1
                            i += window_size  # skip past this modulation
                            break

        return min(modulations, len(chords) // 16)  # cap reasonable modulations

    def _infer_roman_numerals(self, chords, key_tonic, mode) -> List[str]:
        """Convert detected chords back to Roman numeral symbols."""
        major_scale = [0, 2, 4, 5, 7, 9, 11]
        minor_scale = [0, 2, 3, 5, 7, 8, 10]
        scale = major_scale if mode == "major" else minor_scale

        ROMAN_MAJOR = ["I", "II", "III", "IV", "V", "VI", "VII"]
        ROMAN_MINOR = ["i", "ii", "III", "iv", "v", "VI", "VII"]

        romans = []
        for chord in chords:
            root = chord['root']
            interval = (root - key_tonic) % 12

            if mode == "major":
                if interval in scale:
                    degree = scale.index(interval)
                    roman = ROMAN_MAJOR[degree]
                else:
                    # Chromatic — use b/# prefix
                    closest_below = max((s for s in scale if s <= interval), default=0)
                    degree = scale.index(closest_below) if closest_below in scale else 0
                    roman = ("b" if interval - closest_below == 1 else "#") + ROMAN_MAJOR[degree]
            else:
                if interval in scale:
                    degree = scale.index(interval)
                    roman = ROMAN_MINOR[degree]
                else:
                    closest_below = max((s for s in scale if s <= interval), default=0)
                    degree = scale.index(closest_below) if closest_below in scale else 0
                    roman = ("b" if interval - closest_below == 1 else "#") + ROMAN_MINOR[degree]

            # Append quality suffix
            quality = chord['quality']
            if quality in ("7", "maj7", "m7", "dim", "aug"):
                roman += quality if quality != "m7" else "7"
            romans.append(roman)

        return romans

    # ── Deadband extraction ──

    def _extract_deadband(self, mid, notes, acc: _DeadbandAccum):
        """
        Measure timing precision — the deadband epsilon.

        Algorithm:
        1. Snap each note's onset to the nearest 16th-note grid
        2. Measure the offset between actual onset and grid position
        3. The 90th percentile of |offset| is the deadband epsilon
        4. Analyze off-beat ratio for swing detection
        5. Velocity statistics for dynamics profile
        6. Inter-onset intervals for rubato measurement
        """
        if len(notes) < 10:
            return

        tpb = mid.ticks_per_beat
        grid_ticks = tpb // 4  # 16th note grid

        # Tempo from MIDI
        tempo_us = 500000  # default 120 BPM
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    tempo_us = msg.tempo
                    break
        bpm = 60_000_000 / tempo_us
        ms_per_tick = tempo_us / (tpb * 1000)
        acc.tempos.append(bpm)

        # Microtiming offsets
        offsets = []
        for n in notes:
            onset = n['onset_tick']
            nearest_grid = round(onset / grid_ticks) * grid_ticks
            offset_ticks = onset - nearest_grid
            offset_ms = offset_ticks * ms_per_tick
            offsets.append(offset_ms)
            acc.offsets_ms.append(offset_ms)

        # Beat position analysis (for swing)
        for n in notes:
            beat_pos = (n['onset_beat'] % 1.0)
            acc.beat_ratios.append(beat_pos)

        # Velocity
        for n in notes:
            acc.velocities.append(n['velocity'])

        # Inter-onset intervals for rubato
        # (already captured via offsets — variance is rubato)

    # ── Melody extraction ──

    def _extract_melody(self, notes, acc: _MelodyAccum):
        """
        Extract melodic DNA from the highest voice (or all voices).

        Algorithm:
        1. Separate notes into voices by pitch proximity (voice separation)
        2. For each voice, compute interval sequence
        3. Classify contour shapes within 8-note windows
        4. Find climax position within phrases
        5. Measure step vs leap ratio
        """
        if len(notes) < 4:
            return

        # Voice separation: group by pitch proximity
        voices = self._separate_voices(notes)

        for voice in voices:
            if len(voice) < 4:
                continue

            pitches = [n['pitch'] for n in voice]

            # Intervals
            for i in range(1, len(pitches)):
                interval = abs(pitches[i] - pitches[i - 1])
                acc.intervals.append(min(interval, 12))  # fold compound intervals
                acc.pitches.append(pitches[i])

            acc.pitches.append(pitches[0])

            # Range
            acc.ranges.append((min(pitches), max(pitches)))

            # Contour shapes (8-note windows)
            window = 8
            for i in range(0, len(pitches) - window + 1, window // 2):
                segment = pitches[i:i + window]
                contour = self._classify_contour(segment)
                acc.contours.append(contour)

            # Climax position within phrases
            # A phrase is ~16 notes; find the highest note's position
            phrase_len = 16
            for i in range(0, len(pitches) - phrase_len + 1, phrase_len):
                phrase = pitches[i:i + phrase_len]
                max_pitch = max(phrase)
                climax_idx = phrase.index(max_pitch)
                acc.climax_positions.append(climax_idx / len(phrase))

    def _separate_voices(self, notes: List[dict]) -> List[List[dict]]:
        """
        Separate notes into independent voices using pitch proximity.

        Algorithm (skyline + greedy assignment):
        1. Sort notes by onset
        2. Maintain a list of active voice endpoints
        3. Assign each note to the nearest voice by pitch distance
        4. If no voice is within 12 semitones, create a new voice
        """
        if not notes:
            return []

        voices: List[List[dict]] = [[notes[0]]]
        # Track the last pitch in each voice
        endpoints: List[int] = [notes[0]['pitch']]

        for note in notes[1:]:
            best_voice = -1
            best_dist = 999

            for v, ep in enumerate(endpoints):
                # Check temporal overlap — voice must be free
                last = voices[v][-1]
                if note['onset_tick'] < last['offset_tick'] - 10:
                    continue  # voice is still sounding
                dist = abs(note['pitch'] - ep)
                if dist < best_dist:
                    best_dist = dist
                    best_voice = v

            if best_voice >= 0 and best_dist <= 12:
                voices[best_voice].append(note)
                endpoints[best_voice] = note['pitch']
            else:
                voices.append([note])
                endpoints.append(note['pitch'])

        return [v for v in voices if len(v) >= 3]

    def _classify_contour(self, pitches: List[int]) -> str:
        """
        Classify a pitch segment into a contour shape.

        Shapes:
        - "ascending": monotonic increase
        - "descending": monotonic decrease
        - "arch": rises then falls (climax in middle 50%)
        - "inverted_arch": falls then rises
        - "V": steep fall then steep rise
        """
        if len(pitches) < 3:
            return "ascending"

        n = len(pitches)
        first, last = pitches[0], pitches[-1]
        mid_min = min(pitches[n // 4: 3 * n // 4])
        mid_max = max(pitches[n // 4: 3 * n // 4])

        # Find climax index
        climax_idx = pitches.index(max(pitches))
        nadir_idx = pitches.index(min(pitches))

        climax_norm = climax_idx / (n - 1)  # 0.0-1.0
        nadir_norm = nadir_idx / (n - 1)

        # Ascending: climax near end
        if climax_norm > 0.75 and last > first:
            return "ascending"
        # Descending: climax near start
        if climax_norm < 0.25 and last < first:
            return "descending"
        # Arch: climax in middle
        if 0.25 <= climax_norm <= 0.75 and mid_max > first and mid_max > last:
            return "arch"
        # Inverted arch: nadir in middle
        if 0.25 <= nadir_norm <= 0.75 and mid_min < first and mid_min < last:
            return "inverted_arch"
        # V: nadir in middle, both sides roughly equal
        if nadir_norm > 0.25 and nadir_norm < 0.75:
            return "V"

        return "ascending" if last >= first else "descending"

    # ── Rhythm extraction ──

    def _extract_rhythm(self, notes, beats, bars, acc: _RhythmAccum):
        """
        Extract rhythmic DNA.

        Algorithm:
        1. Duration distribution: histogram of note durations (in beats)
        2. Syncopation: notes with onset on weak 16th subdivisions
        3. Density: notes per beat, computed per bar
        4. Density curve: average density pattern over an 8-beat phrase
        """
        if not notes or bars < 1:
            return

        # Duration distribution
        for n in notes:
            dur = n['duration_beats']
            # Quantize to common values
            quantized = round(dur * 4) / 4  # snap to 16th
            if quantized > 0:
                acc.durations.append(quantized)

        # Syncopation: beat position analysis
        for n in notes:
            beat_frac = n['onset_beat'] % 1.0
            acc.beat_positions.append(beat_frac)

        # Density per bar
        beats_per_bar = 4.0
        for bar in range(bars):
            bar_start = bar * beats_per_bar
            bar_end = bar_start + beats_per_bar
            count = sum(1 for n in notes
                        if bar_start <= n['onset_beat'] < bar_end)
            density = count / beats_per_bar
            acc.densities.append(density)

        # Density curve over 8-beat phrases
        phrase_len = 8.0
        for p in range(int(beats / phrase_len)):
            p_start = p * phrase_len
            curve = []
            for beat in range(int(phrase_len)):
                b_start = p_start + beat
                b_end = b_start + 1.0
                count = sum(1 for n in notes
                            if b_start <= n['onset_beat'] < b_end)
                curve.append(float(count))
            total = sum(curve) or 1
            acc.density_curves.append([c / total for c in curve])

    # ── Harmony extraction ──

    def _extract_harmony(self, mid, notes, bars, acc: _HarmonyAccum):
        """
        Extract harmonic DNA.

        Algorithm:
        1. Detect chords at each beat (reuse holonomy chord detection)
        2. Histogram of chord qualities
        3. Cadence detection: last 2-4 chords before a root resolution
        4. Seventh/extended chord rates
        5. Harmonic rhythm: chord changes per beat
        """
        if not notes or bars < 2:
            return

        pc_counts = Counter(n['pitch'] % 12 for n in notes)
        key_tonic, mode = self._detect_key(pc_counts)
        chords = self._detect_chords_beatwise(notes, key_tonic, mode)

        if not chords:
            return

        # Quality distribution
        for c in chords:
            acc.qualities.append(c['quality'])

            is_diatonic = c['root'] in [
                (key_tonic + s) % 12
                for s in ([0, 2, 4, 5, 7, 9, 11] if mode == "major"
                          else [0, 2, 3, 5, 7, 8, 10])
            ]
            acc.dissonance_flags.append(not is_diatonic)
            acc.seventh_flags.append(c['quality'] in ('7', 'maj7', 'm7', 'm7b5', 'dim7'))
            acc.extended_flags.append(c['quality'] in ('dom9', 'maj9', 'min9', 'dom11', 'dom13'))

        # Cadence patterns: extract from end of 4-bar phrases
        phrase_beats = 16  # 4 bars of 4/4
        for p in range(0, len(chords) - 1, min(16, max(1, len(chords) // 4))):
            segment = chords[p:p + min(4, len(chords) - p)]
            if len(segment) >= 2:
                cadence = tuple(c['root_name'] + c['quality'] for c in segment[-3:])
                acc.cadences.append(cadence)

        # Harmonic rhythm
        if len(chords) > 1:
            total_beats = chords[-1]['beat'] - chords[0]['beat']
            if total_beats > 0:
                acc.chord_changes_per_beat.append(len(chords) / total_beats)

    # ── Register extraction ──

    def _extract_register(self, notes, acc: _RegisterAccum):
        """
        Extract register DNA — where does the composer write?

        Simple: collect all pitches, compute statistics.
        """
        for n in notes:
            acc.pitches.append(n['pitch'])

    # ── Rigidity extraction ──

    def _extract_rigidity(self, mid, notes, acc: _RigidityAccum):
        """
        Extract counterpoint rigidity — how strict are the voice rules?

        Algorithm:
        1. Voice count = number of simultaneous independent voices
        2. Check parallel fifths/octaves between voice pairs
        3. Measure average leap size
        4. Rate of dissonant intervals at strong beats
        """
        voices = self._separate_voices(notes)

        if not voices:
            return

        acc.voice_counts.append(len(voices))

        # Voice pairs for parallel check
        voice_pitches = {}
        for v_idx, voice in enumerate(voices):
            voice_pitches[v_idx] = [n['pitch'] for n in voice]

        # Check pairs for parallel fifths/octaves
        pf_count = 0
        po_count = 0
        pairs_checked = 0

        for a in range(len(voices)):
            for b in range(a + 1, len(voices)):
                va = voice_pitches.get(a, [])
                vb = voice_pitches.get(b, [])
                min_len = min(len(va), len(vb))
                if min_len < 2:
                    continue

                beats = list(range(min_len))
                result_pf = no_parallel_fifths(va, vb, beats)
                result_po = no_parallel_octaves(va, vb, beats)
                pairs_checked += 1

                if result_pf.name == "UNSAT":
                    pf_count += 1
                if result_po.name == "UNSAT":
                    po_count += 1

        if pairs_checked > 0:
            acc.parallel_fifths.append(pf_count)
            acc.parallel_octaves.append(po_count)

        # Leap sizes
        for voice in voices:
            pitches = [n['pitch'] for n in voice]
            for i in range(1, len(pitches)):
                leap = abs(pitches[i] - pitches[i - 1])
                acc.leap_sizes.append(min(leap, 24))
                acc.dissonance_flags.append(leap > 7)

    # ── Aggregation ──

    def _aggregate(self, composer, era, n_files, total_bars,
                   hol, db, mel, rhy, har, reg, rig) -> StyleTile:
        """Aggregate all accumulators into a single StyleTile."""
        from datetime import datetime, timezone

        # ── Holonomy ──
        hol_values = hol.holonomy_values or [0.0]
        total_bars_sum = sum(hol.bar_counts) or 1

        top_progressions = tuple(
            tuple(prog) for prog, _ in hol.progression_counter.most_common(10)
        )

        total_mods = sum(hol.modulation_counts)
        total_sec_dom = sum(hol.secondary_dom_counts)
        total_modal_int = sum(hol.modal_interchange_counts)

        # ── Deadband ──
        abs_offsets = [abs(o) for o in db.offsets_ms] if db.offsets_ms else [20.0]
        sorted_offsets = sorted(abs_offsets)
        p90_idx = int(len(sorted_offsets) * 0.9)
        epsilon_90 = sorted_offsets[min(p90_idx, len(sorted_offsets) - 1)]

        # Swing factor: measure asymmetry of off-beat placement
        swing = self._compute_swing_factor(db.beat_ratios) if db.beat_ratios else 0.0

        # Ahead bias: mean offset direction
        ahead = statistics.mean(db.offsets_ms) if db.offsets_ms else 0.0

        # Rubato: tempo variation (CV of inter-beat intervals)
        rubato = self._compute_rubato(db.tempos) if len(db.tempos) > 1 else 0.0

        vel_mean = statistics.mean(db.velocities) if db.velocities else 80.0
        vel_std = statistics.stdev(db.velocities) if len(db.velocities) > 1 else 10.0

        # ── Melody ──
        interval_counter = Counter(mel.intervals)
        total_intervals = sum(interval_counter.values()) or 1
        interval_dist = {k: v / total_intervals for k, v in sorted(interval_counter.items())}

        contour_counter = Counter(mel.contours)
        total_contours = sum(contour_counter.values()) or 1
        contour_dist = {k: v / total_contours for k, v in contour_counter.items()}

        ranges = mel.ranges or [(60, 72)]
        mel_range = (min(r[0] for r in ranges), max(r[1] for r in ranges))

        climax = statistics.mean(mel.climax_positions) if mel.climax_positions else 0.5

        step_count = sum(1 for i in mel.intervals if i <= 2)
        step_ratio = step_count / len(mel.intervals) if mel.intervals else 0.5

        avg_interval = statistics.mean(mel.intervals) if mel.intervals else 3.0

        repeats = sum(1 for i in mel.intervals if i == 0)
        repeat_rate = repeats / len(mel.intervals) if mel.intervals else 0.0

        # ── Rhythm ──
        dur_counter = Counter(rhy.durations)
        total_durs = sum(dur_counter.values()) or 1
        dur_dist = {k: v / total_durs for k, v in sorted(dur_counter.items())}

        # Syncopation: notes on weak 16ths (positions 0.25, 0.75 within beat)
        syncopated = sum(1 for bp in rhy.beat_positions
                         if 0.1 < (bp % 0.5) < 0.4 or 0.6 < (bp % 0.5) < 0.9)
        sync_rate = syncopated / len(rhy.beat_positions) if rhy.beat_positions else 0.0

        density_mean = statistics.mean(rhy.densities) if rhy.densities else 1.0
        density_var = statistics.variance(rhy.densities) if len(rhy.densities) > 1 else 0.0

        # Average density curve
        if rhy.density_curves:
            n_curves = len(rhy.density_curves)
            curve_len = len(rhy.density_curves[0])
            avg_curve = [
                sum(c[i] for c in rhy.density_curves if i < len(c)) / n_curves
                for i in range(curve_len)
            ]
            total_c = sum(avg_curve) or 1
            density_curve = tuple(c / total_c for c in avg_curve)
        else:
            density_curve = tuple([1.0 / 8] * 8)

        # Rest rate: estimate from gaps
        rest_rate = max(0.0, 1.0 - density_mean * 0.5)

        # Dotted/triplet rates from duration distribution
        dotted_rate = sum(v for k, v in dur_dist.items()
                          if 0.6 < k < 0.9 or 1.2 < k < 1.6)  # 0.75, 1.5
        triplet_rate = sum(v for k, v in dur_dist.items()
                           if abs(k - 1/3) < 0.05 or abs(k - 2/3) < 0.05)

        # ── Harmony ──
        quality_counter = Counter(har.qualities)
        total_qual = sum(quality_counter.values()) or 1
        quality_dist = {k: v / total_qual for k, v in quality_counter.items()}

        cadence_counter = Counter(har.cadences)
        top_cadences = tuple(cadence_counter.most_common(10))
        cadence_patterns = tuple(c for c, _ in top_cadences)

        dissonance_rate = (sum(har.dissonance_flags) / len(har.dissonance_flags)
                           if har.dissonance_flags else 0.0)
        seventh_rate = (sum(har.seventh_flags) / len(har.seventh_flags)
                        if har.seventh_flags else 0.0)
        extended_rate = (sum(har.extended_flags) / len(har.extended_flags)
                         if har.extended_flags else 0.0)
        harm_rhythm = (statistics.mean(har.chord_changes_per_beat)
                       if har.chord_changes_per_beat else 0.25)

        # ── Register ──
        if reg.pitches:
            sorted_pitches = sorted(reg.pitches)
            p25 = sorted_pitches[len(sorted_pitches) // 4]
            p75 = sorted_pitches[3 * len(sorted_pitches) // 4]
            register = (p25, p75)
            span = p75 - p25
            centroid = statistics.mean(reg.pitches)

            octave_counter = Counter(p // 12 for p in reg.pitches)
            total_oct = sum(octave_counter.values()) or 1
            octave_dist = {k: v / total_oct for k, v in sorted(octave_counter.items())}
        else:
            register = (60, 79)
            span = 19
            centroid = 69.5
            octave_dist = {4: 0.5, 5: 0.5}

        # ── Rigidity ──
        typical_voices = (statistics.mode(rig.voice_counts)
                          if rig.voice_counts else 1)
        voice_range = (min(rig.voice_counts) if rig.voice_counts else 1,
                       max(rig.voice_counts) if rig.voice_counts else 4)

        pf_rate = (sum(rig.parallel_fifths) / len(rig.parallel_fifths) * 100
                   if rig.parallel_fifths else 0.0)
        po_rate = (sum(rig.parallel_octaves) / len(rig.parallel_octaves) * 100
                   if rig.parallel_octaves else 0.0)

        dissonance_tol = (sum(rig.dissonance_flags) / len(rig.dissonance_flags)
                          if rig.dissonance_flags else 0.0)

        max_leap = (statistics.mean(rig.leap_sizes)
                    if rig.leap_sizes else 5.0)
        constraint_tight = max(0.0, 1.0 - dissonance_tol - pf_rate * 0.01 - po_rate * 0.01)

        # ── FluxVector baseline (heuristic from style features) ──
        arousal = min(1.0, max(0.0, density_mean * 0.5 + vel_mean / 254))
        valence = min(1.0, max(0.0, 0.5 + quality_dist.get('maj', 0) * 0.5
                                - quality_dist.get('min', 0) * 0.3
                                - quality_dist.get('dim', 0) * 0.5))
        dominance = min(1.0, max(0.0, typical_voices / 8 + constraint_tight * 0.3))
        uncertainty = min(1.0, max(0.0, dissonance_rate * 0.7 + rubato * 0.3))
        novelty = min(1.0, max(0.0, total_mods / total_bars_sum * 50
                               + seventh_rate * 0.3 + step_ratio * 0.2))

        # Detect microtiming distribution
        if db.offsets_ms:
            skew = statistics.mean(db.offsets_ms)
            kurt = self._kurtosis(db.offsets_ms)
            if kurt > 3.5:
                microtiming_dist = "uniform"
            elif abs(skew) < 1.0:
                microtiming_dist = "gaussian"
            else:
                microtiming_dist = "triangular"
        else:
            microtiming_dist = "gaussian"

        return StyleTile(
            composer=composer,
            era=era,
            corpus_size=n_files,
            total_bars=total_bars,
            holonomy_range=(min(hol_values), max(hol_values)),
            holonomy_mean=statistics.mean(hol_values),
            modulation_frequency=total_mods / total_bars_sum * 100,
            key_center_drift=statistics.mean(hol.drift_values) if hol.drift_values else 0.0,
            preferred_progressions=top_progressions,
            stability_score=statistics.mean(hol.stability_scores) if hol.stability_scores else 0.5,
            secondary_dominant_rate=total_sec_dom / total_bars_sum * 100,
            modal_interchange_rate=total_modal_int / total_bars_sum * 100,
            epsilon_range=(min(abs_offsets), max(abs_offsets)),
            epsilon_mean=epsilon_90,
            swing_factor=swing,
            rubato_variance=rubato,
            ahead_bias=ahead,
            microtiming_distribution=microtiming_dist,
            velocity_mean=vel_mean,
            velocity_std=vel_std,
            typical_voices=typical_voices,
            voice_count_range=voice_range,
            constraint_tightness=constraint_tight,
            parallel_fifth_rate=pf_rate,
            parallel_octave_rate=po_rate,
            dissonance_tolerance=dissonance_tol,
            max_leap_preference=int(max_leap),
            interval_distribution=interval_dist,
            contour_shapes=contour_dist,
            melodic_range=mel_range,
            climax_position=climax,
            step_vs_leap_ratio=step_ratio,
            average_interval=avg_interval,
            repeated_note_rate=repeat_rate,
            duration_distribution=dur_dist,
            syncopation_rate=sync_rate,
            density_mean=density_mean,
            density_variance=density_var,
            density_curve=density_curve,
            rest_rate=rest_rate,
            dotted_note_rate=dotted_rate,
            triplet_rate=triplet_rate,
            chord_quality_distribution=quality_dist,
            cadence_patterns=cadence_patterns,
            dissonance_rate=dissonance_rate,
            harmonic_rhythm=harm_rhythm,
            seventh_chord_rate=seventh_rate,
            extended_chord_rate=extended_rate,
            preferred_register=register,
            register_span=span,
            register_centroid=centroid,
            register_distribution=octave_dist,
            arousal=round(arousal, 3),
            valence=round(valence, 3),
            dominance=round(dominance, 3),
            uncertainty=round(uncertainty, 3),
            novelty=round(novelty, 3),
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
        )

    # ── Utility methods ──

    def _compute_swing_factor(self, beat_ratios: List[float]) -> float:
        """
        Detect swing from beat position ratios.

        In swung 8th notes, the off-beat note is delayed toward the triplet.
        We measure: of notes in the (0.4, 0.6) range (off-beat 8ths),
        what's their average position?
        0.5 = straight, 0.667 = full triplet swing.
        """
        off_beats = [r for r in beat_ratios if 0.35 < r < 0.75]
        if len(off_beats) < 5:
            return 0.0
        avg = statistics.mean(off_beats)
        # Map 0.5 → 0.0, 0.667 → 1.0
        swing = max(0.0, min(1.0, (avg - 0.5) / (2/3 - 0.5)))
        return swing

    def _compute_rubato(self, tempos: List[float]) -> float:
        """Compute tempo variation as coefficient of variation."""
        if len(tempos) < 2:
            return 0.0
        mean = statistics.mean(tempos)
        if mean == 0:
            return 0.0
        return statistics.stdev(tempos) / mean

    def _kurtosis(self, values: List[float]) -> float:
        """Compute excess kurtosis."""
        if len(values) < 4:
            return 0.0
        n = len(values)
        mean = statistics.mean(values)
        std = statistics.stdev(values)
        if std == 0:
            return 0.0
        m4 = sum((x - mean) ** 4 for x in values) / n
        m2 = std ** 2
        return (m4 / (m2 ** 2)) - 3.0
```

---

## 3. StyleMorpher

The inverse operation — apply a StyleTile to transform generated music.

```python
class StyleMorpher:
    """
    Transform notes toward a target StyleTile.

    The morpher adjusts timing, intervals, durations, harmony, and register
    to make generic generated music sound like a specific composer.

    Usage:
        morpher = StyleMorpher()
        bach_notes = morpher.morph(generated_notes, bach_tile, blend=0.8)
    """

    def __init__(self, ticks_per_beat: int = 480):
        self.tpb = ticks_per_beat

    def morph(
        self,
        notes: List[dict],
        target_style: StyleTile,
        blend: float = 1.0,
    ) -> List[dict]:
        """
        Transform notes toward a target style.

        Parameters
        ----------
        notes : List[dict]
            Input note events (same format as extractor output).
        target_style : StyleTile
            Target composer style.
        blend : float
            1.0 = full transformation, 0.0 = unchanged.

        Returns
        -------
        List[dict]
            Transformed notes (copies, original unchanged).
        """
        import copy
        result = copy.deepcopy(notes)

        result = self.apply_register_style(result, target_style, blend)
        result = self.apply_melodic_style(result, target_style, blend)
        result = self.apply_rhythmic_style(result, target_style, blend)
        result = self.apply_deadband_style(result, target_style, blend)
        result = self.apply_velocity_style(result, target_style, blend)

        return result

    # ── Register morphing ──

    def apply_register_style(
        self,
        notes: List[dict],
        style: StyleTile,
        blend: float,
    ) -> List[dict]:
        """
        Shift notes into the composer's preferred register.

        Algorithm:
        1. Compute current register centroid
        2. Compute target register centroid from style
        3. Transpose all notes by the difference × blend
        4. Clamp to style's preferred range
        """
        if not notes:
            return notes

        current_centroid = statistics.mean(n['pitch'] for n in notes)
        target_centroid = style.register_centroid

        shift = round((target_centroid - current_centroid) * blend)

        for n in notes:
            n['pitch'] = n['pitch'] + shift
            # Clamp to preferred register with some margin
            lo, hi = style.preferred_register
            margin = 12  # allow an octave beyond
            n['pitch'] = max(lo - margin, min(hi + margin, n['pitch']))
            n['pitch'] = max(0, min(127, n['pitch']))

        return notes

    # ── Melodic morphing ──

    def apply_melodic_style(
        self,
        notes: List[dict],
        style: StyleTile,
        blend: float,
    ) -> List[dict]:
        """
        Adjust intervals to match the composer's melodic DNA.

        Algorithm:
        1. For each pair of consecutive notes in the same voice:
        a. Measure the current interval
        b. Sample from the target interval_distribution
        c. Interpolate: new_interval = old × (1-blend) + target × blend
        d. Apply contour correction: if the composer prefers arches,
           reshape the phrase toward arch contour
        2. Respecting max_leap_preference
        """
        if len(notes) < 2:
            return notes

        # Group into voices by channel
        voices = defaultdict(list)
        for n in notes:
            voices[n['channel']].append(n)

        for channel, voice_notes in voices.items():
            # Sort by onset
            voice_notes.sort(key=lambda n: n['onset_tick'])

            for i in range(1, len(voice_notes)):
                current_interval = voice_notes[i]['pitch'] - voice_notes[i - 1]['pitch']
                abs_interval = abs(current_interval)
                direction = 1 if current_interval >= 0 else -1

                # Sample target interval from distribution
                target_interval = self._sample_interval(style)

                # Blend: reduce or increase interval toward target
                if abs_interval > 0:
                    # Scale the interval
                    ratio = 1.0 + (target_interval / max(abs_interval, 1) - 1.0) * blend
                    new_interval = round(abs_interval * ratio)
                else:
                    # Repeated note: maybe change it based on repeated_note_rate
                    if blend > style.repeated_note_rate:
                        new_interval = target_interval
                    else:
                        new_interval = 0

                # Enforce max leap
                max_leap = style.max_leap_preference
                new_interval = min(new_interval, max_leap)

                # Apply step bias
                if style.step_vs_leap_ratio > 0.7 and new_interval > 4:
                    if blend > 0.5:
                        # Fill in with scale steps (simplified: reduce to step)
                        new_interval = min(new_interval, 2)

                voice_notes[i]['pitch'] = voice_notes[i - 1]['pitch'] + new_interval * direction
                voice_notes[i]['pitch'] = max(0, min(127, voice_notes[i]['pitch']))

        return notes

    def _sample_interval(self, style: StyleTile) -> int:
        """Sample a melodic interval from the style's distribution."""
        import random
        if not style.interval_distribution:
            return 2  # default step

        intervals = list(style.interval_distribution.keys())
        weights = list(style.interval_distribution.values())
        total = sum(weights) or 1
        weights = [w / total for w in weights]

        return random.choices(intervals, weights=weights, k=1)[0]

    # ── Rhythmic morphing ──

    def apply_rhythmic_style(
        self,
        notes: List[dict],
        style: StyleTile,
        blend: float,
    ) -> List[dict]:
        """
        Adjust note durations to match the composer's rhythmic DNA.

        Algorithm:
        1. For each note, sample a target duration from the style's distribution
        2. Blend current duration toward target
        3. Apply density curve: shift notes to match the composer's
           preferred density pattern over the phrase
        4. Apply syncopation: if the style has high syncopation,
           shift some onsets to weak beats
        """
        import random

        if not notes:
            return notes

        # Duration morphing
        available_durations = sorted(style.duration_distribution.keys())
        dur_weights = [style.duration_distribution.get(d, 0.1) for d in available_durations]

        for n in notes:
            current_dur = n['duration_beats']

            # Sample target duration
            if available_durations:
                target_dur = random.choices(available_durations, weights=dur_weights, k=1)[0]
                new_dur = current_dur * (1 - blend) + target_dur * blend
                n['duration_beats'] = max(0.125, new_dur)
                n['offset_beat'] = n['onset_beat'] + n['duration_beats']
                n['offset_tick'] = n['onset_tick'] + int(n['duration_beats'] * self.tpb)

        # Syncopation morphing
        if style.syncopation_rate > 0.3:
            for n in notes:
                beat_pos = n['onset_beat'] % 1.0
                # If this is on a strong beat and we want more syncopation
                if beat_pos < 0.1 or (0.45 < beat_pos < 0.55):
                    if random.random() < style.syncopation_rate * blend * 0.3:
                        # Shift to a weak 16th
                        shift_beats = 0.25 * blend
                        n['onset_beat'] += shift_beats
                        n['onset_tick'] += int(shift_beats * self.tpb)

        return notes

    # ── Deadband morphing ──

    def apply_deadband_style(
        self,
        notes: List[dict],
        style: StyleTile,
        blend: float,
    ) -> List[dict]:
        """
        Apply timing feel — the deadband epsilon and microtiming.

        Algorithm:
        1. Compute how far each note is from the nearest grid point
        2. Generate a target offset from the style's deadband profile
        3. Interpolate the offset
        4. Apply swing factor to off-beat notes
        5. Apply ahead_bias
        """
        import random

        if not notes:
            return notes

        grid_ticks = self.tpb // 4  # 16th note grid

        # Style parameters
        epsilon = style.epsilon_mean  # ms
        swing = style.swing_factor
        bias = style.ahead_bias  # ms (negative = ahead)

        # Estimate ms per tick (assume 120 BPM default, should use actual tempo)
        ms_per_tick = (500000 / (self.tpb * 1000))  # 120 BPM

        for n in notes:
            onset = n['onset_tick']
            nearest_grid = round(onset / grid_ticks) * grid_ticks

            # Current offset from grid
            current_offset_ticks = onset - nearest_grid

            # Generate style offset
            if style.microtiming_distribution == "gaussian":
                sigma_ms = epsilon / 1.645
                target_offset_ms = random.gauss(bias * 0.25, sigma_ms)
            elif style.microtiming_distribution == "triangular":
                r = epsilon / 0.684
                target_offset_ms = random.triangular(-r, r, 0) + bias * 0.25
            else:  # uniform
                r = epsilon / 0.9
                target_offset_ms = random.uniform(-r, r) + bias * 0.25

            target_offset_ticks = target_offset_ms / ms_per_tick

            # Blend: interpolate between current and target
            new_offset = current_offset_ticks * (1 - blend) + target_offset_ticks * blend
            n['onset_tick'] = nearest_grid + int(round(new_offset))
            n['onset_beat'] = n['onset_tick'] / self.tpb

            # Apply swing to off-beat 8ths
            beat_frac = n['onset_beat'] % 1.0
            if 0.4 < beat_frac < 0.7:  # off-beat 8th
                swing_delay = swing * (1.0 / 3.0) * 0.5 * self.tpb * blend
                n['onset_tick'] += int(swing_delay)
                n['onset_beat'] = n['onset_tick'] / self.tpb

        return notes

    # ── Velocity morphing ──

    def apply_velocity_style(
        self,
        notes: List[dict],
        style: StyleTile,
        blend: float,
    ) -> List[dict]:
        """
        Adjust dynamics to match the composer's velocity profile.

        Simple Gaussian resampling toward the target mean/std.
        """
        import random

        for n in notes:
            current_vel = n['velocity']
            target_vel = int(random.gauss(style.velocity_mean, style.velocity_std))
            target_vel = max(1, min(127, target_vel))
            n['velocity'] = int(round(current_vel * (1 - blend) + target_vel * blend))
            n['velocity'] = max(1, min(127, n['velocity']))

        return notes
```

### 3.1 Example: "Make this sound more like Bach"

```python
# What actually happens when you call:
# morpher.morph(generated_notes, bach_tile, blend=0.8)

# 1. REGISTER: All notes shift toward Bach's preferred register (MIDI 48-84,
#    centroid ~66). The bass gets pushed down, the soprano up. The typical
#    4-voice spacing of Bach emerges.

# 2. MELODIC: Interval distribution is reshaped:
#    - Steps (1-2 semitones) become dominant: ~65% of all intervals
#    - Large leaps (>7 semitones) are reduced: Bach rarely leaps more than an octave
#    - Repeated notes increase (Bach's sequences often repeat pitches)
#    - Contour shifts toward "arch" shapes (Bach's phrases typically rise then fall)

# 3. RHYTHM: Duration distribution converges to Bach's:
#    - {0.25: 0.20, 0.5: 0.35, 1.0: 0.30, 2.0: 0.10, 4.0: 0.05}
#    - Eighth and quarter notes dominate
#    - Syncopation drops to ~0.05 (Bach is remarkably on-beat)
#    - Density stabilizes around 2-3 notes per beat (4 voices × moderate rhythm)

# 4. DEADBAND: Timing tightens dramatically:
#    - epsilon drops to ~8ms (Bach is nearly metronomic)
#    - swing_factor → 0.0 (dead straight)
#    - ahead_bias → 0.0 (no push, no drag)
#    - rubato_variance → 0.02 (minimal tempo fluctuation)

# 5. VELOCITY: Dynamics narrow:
#    - mean → 72, std → 8 (Bach's harpsichord-like evenness)
#    - Less dynamic range than Chopin or jazz
```

---

## 4. Composer Comparison Matrix

Predicted StyleTile values for five contrasting composers.

### 4.1 Summary Table

| Parameter | Bach | Mozart | Chopin | Joplin | Debussy |
|-----------|------|--------|---------|--------|---------|
| **Era** | baroque | classical | romantic | ragtime | modern |
| **Holonomy** | | | | | |
| holonomy_range | (-0.3, 0.4) | (-0.2, 0.3) | (-0.8, 1.2) | (-0.1, 0.2) | (-1.5, 2.0) |
| holonomy_mean | 0.05 | 0.03 | 0.15 | 0.02 | 0.40 |
| modulation_freq/100bars | 1.5 | 2.0 | 4.5 | 0.5 | 6.0 |
| key_center_drift | 1.8 | 1.5 | 3.2 | 1.2 | 4.5 |
| stability_score | 0.82 | 0.88 | 0.55 | 0.90 | 0.30 |
| **Deadband** | | | | | |
| epsilon_range (ms) | (2, 12) | (3, 15) | (10, 80) | (5, 25) | (15, 60) |
| epsilon_mean (ms) | 8 | 10 | 35 | 15 | 30 |
| swing_factor | 0.0 | 0.0 | 0.10 | 0.65 | 0.05 |
| rubato_variance | 0.02 | 0.03 | 0.15 | 0.04 | 0.08 |
| ahead_bias (ms) | 0.0 | -2.0 | 15.0 | 3.0 | 5.0 |
| **Rigidity** | | | | | |
| typical_voices | 4 | 2 | 1 | 2 | 3 |
| constraint_tightness | 0.95 | 0.80 | 0.40 | 0.60 | 0.25 |
| parallel_fifth_rate | 0.0 | 0.5 | 5.0 | 2.0 | 8.0 |
| max_leap_preference | 8 | 7 | 14 | 10 | 16 |
| dissonance_tolerance | 0.05 | 0.08 | 0.25 | 0.10 | 0.45 |
| **Melodic** | | | | | |
| step_vs_leap_ratio | 0.72 | 0.75 | 0.55 | 0.60 | 0.45 |
| average_interval | 2.3 | 2.1 | 3.8 | 2.8 | 4.2 |
| climax_position | 0.55 | 0.50 | 0.65 | 0.70 | 0.45 |
| repeated_note_rate | 0.12 | 0.08 | 0.03 | 0.06 | 0.04 |
| melodic_range (semi) | (24, 36) | (20, 30) | (36, 52) | (24, 36) | (30, 48) |
| **Rhythmic** | | | | | |
| syncopation_rate | 0.05 | 0.08 | 0.20 | 0.55 | 0.15 |
| density_mean | 2.5 | 1.8 | 2.2 | 2.8 | 1.5 |
| rest_rate | 0.15 | 0.20 | 0.25 | 0.10 | 0.35 |
| dotted_note_rate | 0.05 | 0.08 | 0.20 | 0.30 | 0.10 |
| triplet_rate | 0.02 | 0.03 | 0.15 | 0.05 | 0.08 |
| **Harmonic** | | | | | |
| dissonance_rate | 0.08 | 0.05 | 0.25 | 0.10 | 0.40 |
| harmonic_rhythm | 0.5 | 0.25 | 0.75 | 0.5 | 1.0 |
| seventh_chord_rate | 0.10 | 0.05 | 0.30 | 0.20 | 0.50 |
| **Register** | | | | | |
| preferred_register | (48, 84) | (55, 81) | (36, 96) | (40, 84) | (36, 96) |
| register_centroid | 66 | 68 | 66 | 62 | 66 |
| register_span | 36 | 26 | 48 | 36 | 48 |
| **FluxVector** | | | | | |
| arousal | 0.55 | 0.45 | 0.60 | 0.65 | 0.40 |
| valence | 0.70 | 0.80 | 0.45 | 0.80 | 0.50 |
| dominance | 0.80 | 0.60 | 0.40 | 0.55 | 0.35 |
| uncertainty | 0.10 | 0.08 | 0.35 | 0.15 | 0.55 |
| novelty | 0.25 | 0.20 | 0.50 | 0.30 | 0.70 |

### 4.2 Detailed DNA Profiles

#### Bach — The Architect

```
Holonomy DNA: Bach modulates methodically, usually to closely related keys
(fifth up/down, relative minor). His holonomy is low — he always returns home.
Modulations are structural (at section boundaries), not whimsical.

Deadband DNA: Near-metronomic. Harpsichord and organ don't sustain, so
attack precision matters. epsilon ≈ 8ms. Zero swing. Zero rubato.

Rigidity DNA: THE gold standard of strict counterpoint. 4 voices typical
(in fugues). Parallel fifths/octaves are EXILED. Constraint tightness ≈ 0.95.
Max leap ≈ 8 semitones (minor seventh). Dissonance only on prepared suspensions.

Melodic DNA: 72% stepwise motion. Intervals: {1: 0.30, 2: 0.25, 3: 0.15,
4: 0.12, 5: 0.08, 7: 0.05, 8: 0.03, 12: 0.02}. Contours heavily "arch"
(phrase rises to midpoint, descends). Climax at 55% through phrase.
12% repeated notes (sequences, pedal points).

Rhythmic DNA: Even 16th/eighth note motion dominates. Duration distribution:
{0.25: 0.20, 0.5: 0.35, 1.0: 0.30, 2.0: 0.10, 4.0: 0.05}.
Very low syncopation (5%). Density ≈ 2.5 notes/beat (4 voices, moderate rhythm).

Harmonic DNA: Predominantly diatonic triads with occasional secondary
dominants. Stability ≈ 0.82. Seventh chords rare (10%). Harmonic rhythm
≈ 0.5 changes/beat. Preferred progressions: I-IV-V-I, I-vi-ii-V,
circle-of-fifths sequences.

Register DNA: C3-C6 (MIDI 48-84). Centroid at F#3 (66). Even distribution
across 4 voices: bass C2-G3, tenor G2-C4, alto C4-G4, soprano G4-C6.
```

#### Mozart — The Elegant Classicist

```
Holonomy DNA: Even more stable than Bach. Mozart rarely modulates far.
stability_score ≈ 0.88. Modulations are tasteful — usually to dominant
or relative major/minor, and always signaled well in advance.

Deadband DNA: Slightly more relaxed than Bach but still tight.
epsilon ≈ 10ms. Very slight push (ahead_bias = -2ms). Zero swing.
Minimal rubato (0.03).

Rigidity DNA: Less strict than Bach. Typically 2 voices (melody + accompaniment).
Parallel fifths occasionally tolerated in non-contrapuntal passages.
Constraint tightness ≈ 0.80. Max leap ≈ 7 semitones.

Melodic DNA: Highest step ratio (75%). Smooth, singable lines.
average_interval ≈ 2.1 semitones. Contours balanced between ascending and arch.
Climax at exactly the midpoint (0.50). Very Mozartean symmetry.

Rhythmic DNA: Similar to Bach but simpler. Density ≈ 1.8 (fewer voices).
More quarter notes, fewer 16ths. Duration: {0.25: 0.10, 0.5: 0.40,
1.0: 0.35, 2.0: 0.12, 4.0: 0.03}. Low syncopation (8%).
Higher rest rate (20%) — Mozart breathes.

Harmonic DNA: The I-V-I and I-IV-V-I cadences dominate. Very diatonic.
Seventh chords only at cadences (5%). Harmonic rhythm ≈ 0.25 (slow changes).
Cadence patterns: V-I, IV-V-I, ii-V-I.

Register DNA: Slightly narrower than Bach. MIDI 55-81. Centroid at Ab3 (68).
More concentrated in the treble — melody dominates, accompaniment is light.
```

#### Chopin — The Romantic Voice

```
Holonomy DNA: Chopin wanders. His modulations through remote keys are famous.
holonomy_mean ≈ 0.15, range up to 1.2. Modulation frequency ≈ 4.5/100bars.
He visits bII, bIII, bVI, bVII freely (Chopin-style chromatic mediants).
stability_score ≈ 0.55.

Deadband DNA: RUBATO. This is the defining feature.
epsilon ≈ 35ms with range up to 80ms. rubato_variance ≈ 0.15.
The left hand stays relatively steady while the right hand floats.
ahead_bias ≈ +15ms (melody lays back over the accompaniment).
swing_factor ≈ 0.10 (not swing, but flexible rubato).

Rigidity DNA: Single voice (piano solo). No counterpoint constraints.
Constraint tightness ≈ 0.40. Leaps up to 14 semitones (Chopin's wide arpeggios).
Dissonance tolerance ≈ 0.25 (augmented 6ths, Neapolitan chords).

Melodic DNA: Step ratio drops to 55%. Wide intervals common.
average_interval ≈ 3.8 semitones. Climax at 65% (Chopin builds, then peaks late).
Contour: heavily "ascending" and "arch" — the bel canto influence.
Repeated notes rare (3%). Melodic range up to 52 semitones (4+ octaves).

Rhythmic DNA: Duration distribution spreads wide:
{0.125: 0.05, 0.25: 0.15, 0.5: 0.25, 1.0: 0.25, 1.5: 0.10, 2.0: 0.10, 4.0: 0.10}
Dotted notes at 20%. Triplets at 15% (Chopin's famous 3-against-2).
Syncopation ≈ 20%. Density ≈ 2.2 but highly variable.

Harmonic DNA: Rich. Seventh chords at 30%. Extended chords appear.
dissonance_rate ≈ 0.25. Harmonic rhythm ≈ 0.75 (fast changes).
Cadence patterns: ii-V-I, bVI-V-i, iv-V-i, Chopin's beloved bII-I (Neapolitan).
Chord qualities: {maj: 0.25, min: 0.25, 7: 0.15, maj7: 0.10, min7: 0.10,
dom7: 0.05, dim: 0.05, aug: 0.05}

Register DNA: WIDE. MIDI 36-96 (C2-C7). Span of 48 semitones.
He uses the entire keyboard. Centroid ≈ 66 (middle).
Bass arpeggios down to C2, filigree up to C7.
```

#### Joplin — The Ragtime King

```
Holonomy DNA: Very stable. Ragtime form is strict (AA BB A CC D).
stability_score ≈ 0.90. Rarely modulates — mostly I, IV, V with
occasional vi. modulation_frequency ≈ 0.5/100bars.

Deadband DNA: Tighter than jazz but with character.
epsilon ≈ 15ms. SWING_FACTOR ≈ 0.65 — this is the defining ragtime swing.
The dotted-eighth/sixteenth pattern is everywhere.
ahead_bias ≈ +3ms (slight lay-back on the right hand).
Minimal rubato (0.04) — ragtime is steady.

Rigidity DNA: 2 voices (left hand stride, right hand melody).
Constraint tightness ≈ 0.60. Max leap ≈ 10 semitones.
Parallel fifths tolerated in stride patterns. Dissonance low (0.10).

Melodic DNA: Step ratio ≈ 0.60. Syncopated melodies with frequent leaps.
average_interval ≈ 2.8. Contours: "V" shape common (drop and bounce back).
Climax at 70% (ragtime melodies peak late in the strain).
Repeated notes at 6% (banjo influence). Range: 24-36 semitones.

Rhythmic DNA: THE defining feature. Duration distribution:
{0.125: 0.10, 0.25: 0.30, 0.5: 0.25, 0.75: 0.15, 1.0: 0.10, 2.0: 0.10}
The 0.75 (dotted quarter / syncopated pattern) is highly characteristic.
Syncopation at 55% — the highest of any composer here.
dotted_note_rate ≈ 0.30. Density ≈ 2.8 (constant motion).
Triplet rate low (5%) — ragtime is more about dotted rhythms than triplets.

Harmonic DNA: Simple. {maj: 0.50, min: 0.15, 7: 0.20, dom7: 0.10, other: 0.05}
Seventh chords at 20% (the "ragtime seventh"). Harmonic rhythm ≈ 0.5.
Progressions: I-IV-I-V-I, I-vi-ii-V-I, circle-of-fifths (ragtime cliché).

Register DNA: MIDI 40-84 (E1-C6). Stride bass jumps between 40-52 (bass note)
and 55-67 (chord). Right hand melody 67-84. Centroid ≈ 62.
```

#### Debussy — The Impressionist

```
Holonomy DNA: Floating. Debussy avoids traditional tonal centers.
holonomy_mean ≈ 0.40, range up to 2.0. Modulation frequency ≈ 6.0/100bars.
He drifts through keys without establishing them.
stability_score ≈ 0.30. Key center drift ≈ 4.5 semitones.

Deadband DNA: Loose and flowing. epsilon ≈ 30ms, range up to 60ms.
rubato_variance ≈ 0.08 (moderate — Debussy is flexible but not Chopin-level).
ahead_bias ≈ +5ms. swing_factor ≈ 0.05. The timing has a "floating" quality —
neither pushed nor dragged, just... unmoored.

Rigidity DNA: 2-3 voices, loosely structured.
Constraint tightness ≈ 0.25. Max leap ≈ 16 semitones (wide piano leaps).
Dissonance tolerance ≈ 0.45 (parallel chords, unresolved dissonances).
Parallel fifths and octaves at 8% — Debussy USES them deliberately.

Melodic DNA: Step ratio drops to 45%. Wide intervals common (4.2 avg).
Contour: "inverted_arch" and "V" are common — Debussy's melodies
often descend into the middle then float. Climax at 45% (early or diffuse).
Repeated notes at 4% (he prefers motion). Range: 30-48 semitones.

Rhythmic DNA: Duration distribution is FLAT compared to others:
{0.25: 0.15, 0.5: 0.25, 1.0: 0.25, 1.5: 0.10, 2.0: 0.10, 3.0: 0.05, 4.0: 0.10}
Long notes (3.0, 4.0 beats) are more common than any other composer.
Syncopation at 15%. Density ≈ 1.5 (very sparse compared to Bach).
Rest rate ≈ 0.35 — silence is structural in Debussy.
Triplet rate at 8% (subdivisions in "Golliwog's Cakewalk", etc.).

Harmonic DNA: {maj: 0.15, min: 0.10, maj7: 0.20, min7: 0.15, 7: 0.10,
dim: 0.05, aug: 0.05, sus4: 0.10, dom9: 0.05, other: 0.05}
Seventh chords at 50%. Extended chords at 15%. Harmonic rhythm ≈ 1.0
(fast — Debussy changes chords almost every beat).
Cadence patterns: often avoids traditional cadences entirely.
Instead: parallel chord movement, whole-tone sequences, unresolved dominant 7ths.

Register DNA: WIDE. MIDI 36-96 (C2-C7). Span 48 semitones.
Centroid ≈ 66. Debussy uses the full piano range — low bass rumbles
and high bell-like tones coexist. Register distribution is bimodal:
heavy in low bass AND high treble, with a gap in the middle.
```

---

## 5. Self-Style Extraction

Tools for artists to decompose their own music.

```python
class SelfStyleExtractor:
    """
    Artists point this at their own compositions to discover their style DNA.

    Usage:
        extractor = SelfStyleExtractor()
        my_style = extractor.extract_my_style("~/my_midi_compositions/")
        similarities = extractor.compare_to_known(my_style)
        # → [("Chopin", 0.72), ("Debussy", 0.45), ("Bach", 0.12), ...]
    """

    def __init__(self):
        self.base_extractor = StyleExtractor()
        self._known_tiles: Dict[str, StyleTile] = {}

    def load_known_composers(self, tiles_dir: str):
        """Load pre-computed StyleTiles for comparison."""
        for path in Path(tiles_dir).glob("*.json"):
            tile = StyleTile.from_json(path.read_text())
            self._known_tiles[tile.composer] = tile

    def extract_my_style(self, my_midi_folder: str, name: str = "Me") -> StyleTile:
        """
        Analyze an artist's own compositions into a StyleTile.

        Parameters
        ----------
        my_midi_folder : str
            Path to folder containing the artist's MIDI files.
        name : str
            Artist name for the StyleTile.

        Returns
        -------
        StyleTile
        """
        folder = Path(my_midi_folder)
        midi_paths = [str(p) for p in folder.glob("**/*.mid")]
        midi_paths += [str(p) for p in folder.glob("**/*.midi")]

        if not midi_paths:
            raise ValueError(f"No MIDI files found in {my_midi_folder}")

        return self.base_extractor.extract(midi_paths, composer=name, era="personal")

    def compare_to_known(self, my_style: StyleTile) -> List[Tuple[str, float]]:
        """
        Compare your style to known composers using cosine similarity
        across the high-dimensional DNA feature vector.

        Returns list of (composer_name, similarity_score) sorted by similarity.
        """
        my_vec = self._style_to_vector(my_style)
        results = []

        for name, tile in self._known_tiles.items():
            their_vec = self._style_to_vector(tile)
            similarity = self._cosine_similarity(my_vec, their_vec)
            results.append((name, similarity))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def evolve_style(
        self,
        base: StyleTile,
        influences: List[Tuple[StyleTile, float]],
    ) -> StyleTile:
        """
        Blend your style with influences. Each influence has a weight.

        This creates a new StyleTile that's a weighted interpolation.

        Example:
            evolved = extractor.evolve_style(
                my_style,
                [(bach_tile, 0.3), (chopin_tile, 0.2)]
            )
            # 50% you + 30% Bach + 20% Chopin

        Algorithm:
        For numeric fields: weighted average.
        For distribution fields: weighted mixture.
        For tuple fields: weighted average per element.
        """
        # Normalize weights
        total_influence = sum(w for _, w in influences)
        base_weight = max(0.0, 1.0 - total_influence)

        # Collect all tiles with weights
        weighted = [(base, base_weight)] + influences

        # Interpolate numeric fields
        numeric_fields = [
            'holonomy_mean', 'modulation_frequency', 'key_center_drift',
            'stability_score', 'secondary_dominant_rate', 'modal_interchange_rate',
            'epsilon_mean', 'swing_factor', 'rubato_variance', 'ahead_bias',
            'velocity_mean', 'velocity_std',
            'typical_voices', 'constraint_tightness', 'parallel_fifth_rate',
            'parallel_octave_rate', 'dissonance_tolerance', 'max_leap_preference',
            'climax_position', 'step_vs_leap_ratio', 'average_interval',
            'repeated_note_rate',
            'syncopation_rate', 'density_mean', 'density_variance',
            'rest_rate', 'dotted_note_rate', 'triplet_rate',
            'dissonance_rate', 'harmonic_rhythm', 'seventh_chord_rate',
            'extended_chord_rate', 'register_span', 'register_centroid',
            'arousal', 'valence', 'dominance', 'uncertainty', 'novelty',
        ]

        result_dict = {}
        for field in numeric_fields:
            value = sum(getattr(tile, field) * w for tile, w in weighted)
            result_dict[field] = value

        # Interpolate range fields
        range_fields = [
            'holonomy_range', 'epsilon_range', 'voice_count_range',
            'melodic_range', 'preferred_register',
        ]
        for field in range_fields:
            lo = sum(getattr(tile, field)[0] * w for tile, w in weighted)
            hi = sum(getattr(tile, field)[1] * w for tile, w in weighted)
            result_dict[field] = (lo, hi)

        # Interpolate distribution fields
        dist_fields = [
            'interval_distribution', 'contour_shapes',
            'duration_distribution', 'chord_quality_distribution',
            'register_distribution',
        ]
        for field in dist_fields:
            merged = defaultdict(float)
            for tile, w in weighted:
                for k, v in getattr(tile, field).items():
                    merged[k] += v * w
            result_dict[field] = dict(merged)

        # Interpolate tuple fields
        result_dict['preferred_progressions'] = base.preferred_progressions
        result_dict['cadence_patterns'] = base.cadence_patterns
        result_dict['density_curve'] = tuple(
            sum(c[i] * w if i < len(c) else 0 for c, w in
                [(getattr(t, 'density_curve'), w) for t, w in weighted])
            for i in range(min(len(getattr(t, 'density_curve', ())) for t, _ in weighted) if weighted else 8)
        )

        # Identity
        result_dict['composer'] = f"{base.composer} (evolved)"
        result_dict['era'] = base.era
        result_dict['corpus_size'] = base.corpus_size
        result_dict['total_bars'] = base.total_bars
        result_dict['microtiming_distribution'] = base.microtiming_distribution

        return StyleTile(**result_dict)

    def generate_variations(
        self,
        my_style: StyleTile,
        n: int = 10,
        mutation_scale: float = 0.15,
    ) -> List[StyleTile]:
        """
        Generate variations of a style by adding Gaussian noise.

        This explores the musical space around your style —
        some variations will sound like you, some won't, and
        the interesting ones are in the boundary.

        Parameters
        ----------
        my_style : StyleTile
            Base style to vary around.
        n : int
            Number of variations to generate.
        mutation_scale : float
            How much to mutate (0.0 = identical, 1.0 = unrecognizable).

        Returns
        -------
        List[StyleTile]
        """
        import random

        variations = []
        for i in range(n):
            # Start from the base and perturb
            base_dict = {
                k: v for k, v in my_style.__dict__.items()
            }

            # Mutate numeric fields
            mutable_fields = [
                ('epsilon_mean', 0.3), ('swing_factor', 0.2),
                ('rubato_variance', 0.3), ('ahead_bias', 5.0),
                ('syncopation_rate', 0.1), ('density_mean', 0.3),
                ('step_vs_leap_ratio', 0.1), ('average_interval', 0.5),
                ('climax_position', 0.1), ('dissonance_tolerance', 0.1),
                ('harmonic_rhythm', 0.1), ('seventh_chord_rate', 0.1),
                ('arousal', 0.1), ('valence', 0.1), ('dominance', 0.1),
                ('uncertainty', 0.1), ('novelty', 0.1),
                ('modulation_frequency', 0.5), ('key_center_drift', 0.3),
            ]

            for field, sigma in mutable_fields:
                current = base_dict[field]
                noise = random.gauss(0, sigma * mutation_scale)
                base_dict[field] = max(0.0, min(1.0 if field not in
                    ('epsilon_mean', 'ahead_bias', 'average_interval',
                     'modulation_frequency', 'key_center_drift') else 999,
                    current + noise))

            # Clamp specific fields
            base_dict['swing_factor'] = max(0.0, min(1.0, base_dict['swing_factor']))
            base_dict['syncopation_rate'] = max(0.0, min(1.0, base_dict['syncopation_rate']))

            base_dict['composer'] = f"{my_style.composer} var.{i+1}"
            variations.append(StyleTile(**base_dict))

        return variations

    # ── Internal helpers ──

    def _style_to_vector(self, tile: StyleTile) -> List[float]:
        """Convert a StyleTile to a feature vector for comparison."""
        return [
            tile.holonomy_mean,
            tile.modulation_frequency / 10.0,
            tile.key_center_drift / 6.0,
            tile.stability_score,
            tile.epsilon_mean / 50.0,
            tile.swing_factor,
            tile.rubato_variance,
            tile.ahead_bias / 30.0,
            tile.velocity_mean / 127.0,
            tile.typical_voices / 8.0,
            tile.constraint_tightness,
            tile.dissonance_tolerance,
            tile.max_leap_preference / 16.0,
            tile.step_vs_leap_ratio,
            tile.average_interval / 12.0,
            tile.climax_position,
            tile.syncopation_rate,
            tile.density_mean / 5.0,
            tile.rest_rate,
            tile.dissonance_rate,
            tile.harmonic_rhythm / 2.0,
            tile.seventh_chord_rate,
            tile.register_centroid / 127.0,
            tile.register_span / 60.0,
            tile.arousal,
            tile.valence,
            tile.dominance,
            tile.uncertainty,
            tile.novelty,
        ]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Cosine similarity between two feature vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a)) or 1e-10
        mag_b = math.sqrt(sum(x * x for x in b)) or 1e-10
        return dot / (mag_a * mag_b)
```

---

## 6. Implementation Roadmap

### Phase 1: StyleExtractor (Weeks 1-3)

**Build on:** `holonomy-harmony`, `groove-analyzer`, `counterpoint-engine`

| Week | Task | Deliverable |
|------|------|-------------|
| 1 | Core note extraction, key detection, voice separation | `StyleExtractor._extract_notes()`, `_detect_key()`, `_separate_voices()` |
| 1 | Melody + rhythm extractors | `_extract_melody()`, `_extract_rhythm()` with full algorithms |
| 2 | Holonomy + harmony extractors | `_extract_holonomy()` integrated with `holonomy-harmony.analyzer.analyze_progression()` |
| 2 | Deadband + register extractors | `_extract_deadband()` integrated with `groove-analyzer` concepts |
| 3 | Rigidity extractor | `_extract_rigidity()` using `counterpoint_engine.rules` constraints |
| 3 | Aggregation + serialization | `_aggregate()` + JSON save/load |

**New repo:** `style-dna/`

```
style-dna/
├── style_dna/
│   ├── __init__.py
│   ├── tile.py              # StyleTile dataclass
│   ├── extractor.py         # StyleExtractor
│   ├── morpher.py           # StyleMorpher
│   ├── self_style.py        # SelfStyleExtractor
│   └── presets/             # Pre-computed composer tiles
│       ├── bach.json
│       ├── mozart.json
│       └── ...
├── tests/
├── corpora/                 # MIDI test corpora
│   ├── bach/
│   ├── chopin/
│   └── ...
└── pyproject.toml
```

**Dependencies:** `mido`, `holonomy-harmony`, `groove-analyzer`, `counterpoint-engine`, `constraint-theory-core`

### Phase 2: Pre-computed Composer Tiles (Weeks 4-5)

**First 20 composers:**

| # | Composer | Era | Why first? |
|---|----------|-----|------------|
| 1 | Bach | Baroque | Constraint theory poster child |
| 2 | Mozart | Classical | Baseline classical style |
| 3 | Beethoven | Classical/Romantic | Bridge era, dramatic contrast |
| 4 | Chopin | Romantic | Rubato, wide intervals |
| 5 | Debussy | Impressionist | Floating tonality |
| 6 | Joplin | Ragtime | Swing, syncopation |
| 7 | Brahms | Romantic | Strict counterpoint in romantic era |
| 8 | Liszt | Romantic | Virtuosic, extreme range |
| 9 | Schubert | Romantic | Lieder, harmonic surprise |
| 10 | Vivaldi | Baroque | Fast motoric rhythm |
| 11 | Handel | Baroque | Orchestral counterpoint |
| 12 | Haydn | Classical | Surprise humor, formal play |
| 13 | Scarlatti | Baroque | Keyboard virtuosity |
| 14 | Ravel | Impressionist | Precision within color |
| 15 | Satie | Modern | Minimalism prototype |
| 16 | Monk | Jazz | Dissonant, angular melody |
| 17 | Ellington | Jazz | Orchestrated jazz harmony |
| 18 | Bartók | Modern | Folk + dissonance |
| 19 | Tchaikovsky | Romantic | Emotional extremes |
| 20 | Mendelssohn | Romantic | Bach revival + romantic color |

**Corpus sources:** IMSLP MIDI downloads, KernScores, MuseScore open scores.
Target: 10-20 pieces per composer, covering major genres (fugues, sonatas, etc.)

### Phase 3: StyleMorpher (Weeks 6-7)

**Build on:** `flux-tensor-midi` (FluxVector, T-0 clocks), `plato-room-musician` (mapping)

- Implement `StyleMorpher` with all five morphing layers
- Test roundtrip: extract Bach tile → generate generic → morph to Bach → extract again → compare tiles
- Integration with `plato-room-musician`: StyleTile as a PLATO tile that configures a room's musical identity
- StyleTile → CATEGORY_CONFIG mapping: era/archetype → register, scale, rhythmic_role

**Key insight:** A StyleTile is a PLATO tile. When it enters a room, it reconfigures that room's:
- `GrooveProfile` (from deadband DNA)
- `ImprovisationConfig` (from melodic/rhythmic DNA)
- `RiskTolerance` (from rigidity DNA)
- `baseline_flux` (from FluxVector baseline)

### Phase 4: Self-Style Tools (Weeks 8-9)

**Build on:** All previous phases

- `SelfStyleExtractor` for artists
- Web UI / CLI: point at your MIDI folder, get a StyleTile
- Comparison dashboard: "Your music is 72% Chopin, 18% Debussy, 10% Bach"
- Style evolution: blend your style with influences
- Variation generator: explore nearby musical spaces
- Export: StyleTile → JSON → share with collaborators

### Phase 5: AI Band Integration (Weeks 10-12)

**Build on:** `AI-BAND-DESIGN`

Each AI Band member gets a StyleTile that defines their musical personality:

```python
# Example: The "Bach Band" — every musician has Bach DNA filtered through their role

bach_tile = StyleTile.from_json("presets/bach.json")

# Bass (forgemaster) — Bach's bass lines are pedal points and walking patterns
bass_personality = MusicianPersonality.from_style_tile(
    bach_tile,
    archetype=PersonalityArchetype.FORGEMASTER,
    # Override: Bach's bass is MORE metronomic than his other voices
    groove_overrides={"base_epsilon": 0.001, "jitter_sigma": 0.001},
)

# Keys (session) — Bach's harmonic voice is the continuo
keys_personality = MusicianPersonality.from_style_tile(
    bach_tile,
    archetype=PersonalityArchetype.SESSION,
)

# Drums (fleet) — There are no drums in Bach, so we interpret his
# rhythmic drive as a very tight, motoric percussion pattern
drums_personality = MusicianPersonality.from_style_tile(
    bach_tile,
    archetype=PersonalityArchetype.FLEET,
    # Bach's rhythm is relentless 16th notes
    groove_overrides={"base_epsilon": 0.0, "jitter_sigma": 0.001},
)

# Sax (knowledge) — This is the fugue subject voice
sax_personality = MusicianPersonality.from_style_tile(
    bach_tile,
    archetype=PersonalityArchetype.KNOWLEDGE,
    # The fugue subject gets Bach's full melodic DNA
    improv_overrides={"base_deviation": 0.10, "chord_tone_bias": 0.8},
)
```

The `from_style_tile` factory method maps StyleTile fields to MusicianPersonality fields:

| StyleTile field | MusicianPersonality field |
|-----------------|--------------------------|
| `epsilon_mean` | `groove.base_epsilon` |
| `rubato_variance` | `groove.jitter_sigma` |
| `swing_factor` | (affects EisensteinSnap rhythmic role) |
| `step_vs_leap_ratio` | `improv.neighbor_tendency` |
| `dissonance_tolerance` | `improv.dissonance_tolerance` + `risk.dissonance_max` |
| `max_leap_preference` | `risk.interval_leap_max` |
| `constraint_tightness` | `risk.rubato_range` (inverse) |
| `typical_voices` | determines how many rooms to allocate |
| `arousal/valence/dominance/uncertainty/novelty` | `baseline_flux` |

**Style collision:** When two musicians with different StyleTiles play together:
- Timing: blend their epsilon values weighted by their `dominance` (the producer's clock wins)
- Harmony: the higher `constraint_tightness` sets the rules
- Register: each stays in their archetype's register, but the StyleTile shifts the centroid
- Emotional contagion: FluxVector resonance spreads mood, modulated by `affiliation`

---

## 7. Appendix: Mathematical Foundations

### 7.1 Eisenstein Snap for Rhythm Classification

From `constraint-theory-core`, the Eisenstein lattice A₂ provides optimal 2D quantization with covering radius 1/√3 ≈ 0.577. We use this to classify rhythmic positions:

```
Grid point: (beat_index, subdivision)
Note onset: (beat, fraction)
Snap distance: Eisenstein distance to nearest grid point
```

This gives us rhythmic classification (on-beat, off-beat, syncopated) with theoretical optimality.

### 7.2 Holonomy as Musical Drift

From `holonomy-harmony`, holonomy measures the net tonal drift around a cycle. For composers:

- **Bach**: Holonomy ≈ 0 (always resolves to tonic)
- **Debussy**: Holonomy ≈ high (avoids resolution, drifts through tonal space)
- **Coltrane**: Holonomy ≈ extreme (Giant Steps cycles through 3 key centers)

This directly maps to `stability_score` and `key_center_drift`.

### 7.3 Deadband as Musical Feel

From `groove-analyzer`, the deadband ε captures timing feel:

```
ε = 3ms  → EDM (machine precision)
ε = 8ms  → Bach (metronomic)
ε = 15ms → Funk (tight pocket)
ε = 30ms → Jazz (wide pocket)
ε = 35ms → Chopin (romantic rubato)
ε = 80ms → Free jazz (chaotic timing)
```

### 7.4 Laman Rigidity as Voice Independence

From `counterpoint-engine`, Laman rigidity ensures no voice is redundant. Bach's 4-voice counterpoint with 2N-3 = 5 constraints is a minimally rigid graph. This gives us `constraint_tightness` and `typical_voices`.

---

*"Every composer is a constraint system. We just make it explicit."*
