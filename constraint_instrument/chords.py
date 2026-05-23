"""
ChordProgression module — harmonic framework for constraint-based music.

The #1 user request across ALL testers: real chord changes that guide
melody generation. This module provides:

- Chord: A single chord with root, quality, voicing, and timing
- ChordProgression: A sequence of chords over time with lookup methods
- ChordGenerator: Generate progressions from terrain names or diagnostic reports

Usage:
    from constraint_instrument.chords import ChordGenerator

    gen = ChordGenerator(key='Eb', bpm=140, bars=8)
    prog = gen.generate('bebop')
    print(prog.to_roman())       # ['Imaj7', 'viim7', 'iim7', 'V7', ...]

    # Check what's active at beat 5
    chord = prog.at_beat(5)
    pitches = prog.active_pitches(5)

    # Use with Instrument
    inst = Instrument(mode='parker', terrain='bebop', key='Eb', bpm=140, chords=True)
    notes = inst.perform()  # notes follow the chord changes
"""

import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .goodman import DiagnosticReport

# ── Note Utilities ───────────────────────────────────────────────────

NOTE_MAP = {
    'C': 0, 'C#': 1, 'Db': 1,
    'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6,
    'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10,
    'B': 11,
}

# Pitch class to note name (prefer sharps)
PC_TO_NAME = {0: 'C', 1: 'C#', 2: 'D', 3: 'Eb', 4: 'E', 5: 'F',
              6: 'F#', 7: 'G', 8: 'Ab', 9: 'A', 10: 'Bb', 11: 'B'}

# Major scale intervals from root
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
# Natural minor scale intervals from root
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]
# Harmonic minor
HARMONIC_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 11]
# Melodic minor (ascending)
MELODIC_MINOR_SCALE = [0, 2, 3, 5, 7, 9, 11]
# Dorian
DORIAN_SCALE = [0, 2, 3, 5, 7, 9, 10]
# Mixolydian
MIXOLYDIAN_SCALE = [0, 2, 4, 5, 7, 9, 10]
# Pentatonic major
PENTATONIC_MAJOR = [0, 2, 4, 7, 9]
# Pentatonic minor
PENTATONIC_MINOR = [0, 3, 5, 7, 10]
# Blues scale
BLUES_SCALE = [0, 3, 5, 6, 7, 10]

# Scale families by quality feeling
SCALE_FAMILIES = {
    'major': MAJOR_SCALE,
    'minor': MINOR_SCALE,
    'harmonic_minor': HARMONIC_MINOR_SCALE,
    'melodic_minor': MELODIC_MINOR_SCALE,
    'dorian': DORIAN_SCALE,
    'mixolydian': MIXOLYDIAN_SCALE,
    'pentatonic_major': PENTATONIC_MAJOR,
    'pentatonic_minor': PENTATONIC_MINOR,
    'blues': BLUES_SCALE,
}

# ── Chord Quality Intervals ──────────────────────────────────────────

QUALITY_INTERVALS = {
    'maj': [0, 4, 7],
    'min': [0, 3, 7],
    'dom7': [0, 4, 7, 10],
    'min7': [0, 3, 7, 10],
    'maj7': [0, 4, 7, 11],
    'dim': [0, 3, 6],
    'dim7': [0, 3, 6, 9],
    'aug': [0, 4, 8],
    'sus4': [0, 5, 7],
    'sus2': [0, 2, 7],
    'min9': [0, 3, 7, 10, 14],
    'dom9': [0, 4, 7, 10, 14],
    'maj9': [0, 4, 7, 11, 14],
    'min11': [0, 3, 7, 10, 14, 17],
    '7sus4': [0, 5, 7, 10],
}

# Roman numeral quality suffixes → quality name
ROMAN_QUALITIES = {
    'I': 'maj', 'i': 'min',
    'II': 'maj', 'ii': 'min',
    'III': 'maj', 'iii': 'min',
    'IV': 'maj', 'iv': 'min',
    'V': 'maj', 'v': 'min',
    'VI': 'maj', 'vi': 'min',
    'VII': 'maj', 'vii': 'min',
    # With extensions
    'Imaj7': 'maj7', 'im7': 'min7',
    'iim7': 'min7', 'IImaj7': 'maj7',
    'iiim7': 'min7', 'IIImaj7': 'maj7',
    'IVmaj7': 'maj7', 'ivm7': 'min7',
    'V7': 'dom7', 'vm7': 'min7',
    'vim7': 'min7', 'VImaj7': 'maj7',
    'viim7': 'min7', 'viim7b5': 'dim',
    'VII7': 'dom7',
    # With inversion notation (simplified)
    'bIIImaj7': 'maj7', 'bVIImaj7': 'maj7',
    'bVIIdom7': 'dom7',
}

# Passing tone offsets (semi/chromatics that are "legal" between chord tones)
PASSING_TONES = [-2, -1, 1, 2]


# ── Helper Functions ─────────────────────────────────────────────────

def _pc(pitch: int) -> int:
    """Pitch class (0-11) from MIDI pitch."""
    return pitch % 12


def _resolve_note_name(name: str) -> int:
    """Resolve a note name to a pitch class (0-11)."""
    name = name.strip()
    if name in NOTE_MAP:
        return NOTE_MAP[name]
    # Try capitalizing first letter
    if len(name) >= 2:
        letter = name[0].upper()
        rest = name[1:].lower()
        normalized = letter + rest
        if normalized in NOTE_MAP:
            return NOTE_MAP[normalized]
    raise ValueError(f"Unknown note name: {name}")


def _scale_degrees(key_pc: int, scale: List[int]) -> List[int]:
    """Get all pitch classes in a scale rooted at key_pc."""
    return [(key_pc + interval) % 12 for interval in scale]


def _roman_to_degree(roman: str, key_pc: int, scale: List[int]) -> Tuple[int, str]:
    """Convert a Roman numeral symbol to (root_pitch_class, quality).

    Examples:
        'Imaj7' → (0, 'maj7')
        'viim7' → (11, 'min7')
        'V7' → (7, 'dom7')
        'bVIImaj7' → (10, 'maj7')  # modal interchange
    """
    quality = ROMAN_QUALITIES.get(roman)
    if quality is None:
        # Try to parse it
        quality = 'maj'  # fallback

    # Strip quality suffix to get the roman numeral root
    root_roman = roman
    for suffix in ['maj7', 'm7b5', 'dom7', 'min7', 'm7', 'maj9', 'min9',
                   'dom9', 'min11', '7sus4', '7', 'sus4', 'sus2', 'dim7']:
        if root_roman.endswith(suffix):
            quality = ROMAN_QUALITIES.get(roman, quality)
            root_roman = root_roman[:-len(suffix)]
            break

    # Handle flat prefix (modal interchange)
    flat_prefix = root_roman.startswith('b')
    if flat_prefix:
        root_roman = root_roman[1:]

    # Map roman numeral to scale degree
    roman_to_numeral = {
        'I': 0, 'i': 0,
        'II': 1, 'ii': 1,
        'III': 2, 'iii': 2,
        'IV': 3, 'iv': 3,
        'V': 4, 'v': 4,
        'VI': 5, 'vi': 5,
        'VII': 6, 'vii': 6,
    }

    degree = roman_to_numeral.get(root_roman, 0)
    if degree < len(scale):
        root = (key_pc + scale[degree]) % 12
    else:
        root = key_pc

    if flat_prefix:
        root = (root - 1) % 12

    return root, quality


# ── Chord Dataclass ──────────────────────────────────────────────────

@dataclass
class Chord:
    """A chord with root, quality, and timing.

    Attributes:
        root: MIDI pitch of the root note
        quality: Chord quality ('maj', 'min', 'dom7', 'min7', 'maj7', etc.)
        symbol: Human-readable symbol (e.g. 'Cmaj7', 'Fm7', 'G7')
        start_beat: Beat position where this chord begins
        duration_beats: Duration in beats
        voicing: Actual MIDI pitches in the voicing (auto-generated if empty)
    """
    root: int
    quality: str
    symbol: str
    start_beat: float
    duration_beats: float
    voicing: List[int] = field(default_factory=list)

    def __post_init__(self):
        if not self.voicing:
            self.voicing = self._generate_voicing()

    def _generate_voicing(self, octave: int = 4) -> List[int]:
        """Generate a voicing for this chord.

        Places the root in the given octave (default: octave 4, around middle C).
        Uses close voicing with the root on bottom.
        """
        intervals = QUALITY_INTERVALS.get(self.quality, [0, 4, 7])
        root_pc = _pc(self.root)
        root_in_octave = root_pc + (octave * 12)
        # Make sure we're in a reasonable range
        while root_in_octave < 36:
            root_in_octave += 12
        while root_in_octave > 84:
            root_in_octave -= 12
        return [root_in_octave + i for i in intervals]

    @property
    def pitch_classes(self) -> List[int]:
        """Pitch classes (0-11) in this chord."""
        return [_pc(p) for p in self.voicing]

    def contains_pitch(self, pitch: int) -> bool:
        """Does this chord contain this pitch class?"""
        return _pc(pitch) in self.pitch_classes

    def is_chord_tone(self, pitch: int) -> bool:
        """Is this pitch a chord tone?"""
        return self.contains_pitch(pitch)

    def __repr__(self) -> str:
        return f"Chord({self.symbol}, beat={self.start_beat}, dur={self.duration_beats})"


# ── ChordProgression ─────────────────────────────────────────────────

@dataclass
class ChordProgression:
    """A sequence of chords over time.

    Provides beat-level lookup, active pitch sets, and Roman numeral analysis.

    Attributes:
        key: The key of the progression (e.g. 'C', 'Eb')
        chords: List of Chord objects
        total_bars: Total number of bars
        bpm: Tempo in BPM
    """
    key: str
    chords: List[Chord]
    total_bars: int
    bpm: int = 120

    def at_beat(self, beat: float) -> Optional[Chord]:
        """Which chord is playing at this beat?

        Returns the chord whose time span contains the given beat.
        Returns None if no chord covers that beat.
        """
        for chord in self.chords:
            if chord.start_beat <= beat < chord.start_beat + chord.duration_beats:
                return chord
        # Fall back to the nearest preceding chord
        best = None
        for chord in self.chords:
            if chord.start_beat <= beat:
                best = chord
        return best

    def active_pitches(self, beat: float) -> List[int]:
        """Which pitches are 'legal' at this beat?

        Returns chord tones plus passing tones (chromatic neighbors).
        This gives the full set of "acceptable" pitches for melodic
        generation over the current chord.
        """
        chord = self.at_beat(beat)
        if chord is None:
            return list(range(12))

        # Start with chord tones (as pitch classes)
        chord_pcs = set(chord.pitch_classes)

        # Add passing tones (chromatic neighbors of chord tones)
        passing_pcs = set()
        for pc in chord_pcs:
            for offset in PASSING_TONES:
                passing_pcs.add((pc + offset) % 12)

        # Combine: chord tones + passing tones
        all_pcs = chord_pcs | passing_pcs

        # Expand to full MIDI range (3 octaves centered around the voicing)
        voicing_center = sum(chord.voicing) // len(chord.voicing) if chord.voicing else 60
        center_octave = voicing_center // 12
        pitches = []
        for octave_offset in range(-1, 2):
            base = (center_octave + octave_offset) * 12
            for pc in sorted(all_pcs):
                pitches.append(base + pc)

        return pitches

    def chord_tones_at(self, beat: float) -> List[int]:
        """Just the chord tones at this beat (no passing tones)."""
        chord = self.at_beat(beat)
        if chord is None:
            return []
        return list(chord.voicing)

    def to_roman(self) -> List[str]:
        """Return progression as Roman numerals.

        Example: ['Imaj7', 'viim7', 'iim7', 'V7']
        """
        return [chord.symbol for chord in self.chords]

    @property
    def total_beats(self) -> float:
        """Total duration in beats."""
        return self.total_bars * 4

    @property
    def total_duration(self) -> float:
        """Total duration in seconds."""
        return self.total_beats * 60.0 / self.bpm

    def __repr__(self) -> str:
        romans = ' → '.join(self.to_roman())
        return f"ChordProgression(key={self.key!r}, bars={self.total_bars}, [{romans}])"

    def __len__(self) -> int:
        return len(self.chords)


# ── ChordGenerator ───────────────────────────────────────────────────

class ChordGenerator:
    """Generate chord progressions from terrains.

    Each terrain has characteristic progressions encoded as Roman numerals.
    The generator picks from these and instantiates them in the given key
    with proper timing.

    Usage:
        gen = ChordGenerator(key='Eb', bpm=140, bars=8)
        prog = gen.generate('bebop')
    """

    # Terrain → typical progressions (in Roman numerals)
    TERRAIN_PROGRESSIONS: Dict[str, List[List[str]]] = {
        'delta_blues': [
            ['I', 'I', 'I', 'I', 'IV', 'IV', 'I', 'I', 'V', 'IV', 'I', 'V'],
            ['I7', 'I7', 'I7', 'I7', 'IV7', 'IV7', 'I7', 'I7', 'V7', 'IV7', 'I7', 'V7'],
        ],
        'bebop': [
            ['Imaj7', 'viim7', 'iiim7', 'VImaj7', 'iim7', 'V7', 'Imaj7', 'iim7'],
            ['iim7', 'V7', 'Imaj7', 'viim7', 'iiim7', 'VI7', 'iim7', 'V7'],
            ['Imaj7', 'iiim7', 'viim7', 'Imaj7', 'iim7', 'V7', 'iiim7', 'VI7'],
            ['Imaj7', 'viim7b5', 'iiim7', 'VI7', 'iim7', 'V7', 'Imaj7', 'V7'],
        ],
        'modal_jazz': [
            ['Im7', 'IVm7', 'Im7', 'IVm7'],
            ['Im7', 'bVIImaj7', 'bIIImaj7', 'IVm7'],
            ['Im7', 'Im7', 'bVIImaj7', 'bVIImaj7'],
        ],
        'hip_hop_trap': [
            ['i', 'VI', 'III', 'VII'],
            ['i', 'VII', 'VI', 'VII'],
            ['i', 'VI', 'VII', 'i'],
            ['i', 'i', 'VI', 'VII'],
        ],
        'electronic_techno': [
            ['i', 'i', 'i', 'i'],
            ['i', 'III', 'VII', 'VI'],
            ['i', 'VI', 'VII', 'i'],
        ],
        'classical_counterpoint': [
            ['I', 'IV', 'V', 'I'],
            ['I', 'vi', 'IV', 'V'],
            ['I', 'ii', 'V', 'I'],
            ['I', 'IV', 'viio', 'V'],
        ],
        'gospel': [
            ['I', 'vi', 'ii', 'V'],
            ['IV', 'I', 'V', 'vi'],
            ['I', 'IV', 'V', 'I'],
            ['I', 'iii', 'vi', 'ii', 'V', 'I', 'IV', 'V7'],
        ],
        'afro_cuban': [
            ['Im', 'IVm', 'Im', 'V7'],
            ['Im', 'V7', 'Im', 'IVm'],
        ],
        'indian_raga': [
            ['I', 'I', 'IV', 'I'],
            ['I', 'V', 'I', 'IV'],
        ],
        'chinese_silk_bamboo': [
            ['I', 'V', 'vi', 'III'],
            ['I', 'IV', 'V', 'I'],
        ],
        'free_improvisation': [
            [],  # no prescribed harmony
        ],
        'bluegrass': [
            ['I', 'IV', 'V', 'I'],
            ['I', 'I', 'IV', 'I', 'V', 'IV', 'I', 'V'],
            ['I', 'IV', 'I', 'V'],
        ],
        'modal': [
            ['Im7', 'IV7', 'Im7', 'IV7'],
            ['Im7', 'bVIImaj7', 'Im7', 'bVIImaj7'],
        ],
        'blues': [
            ['I7', 'I7', 'I7', 'I7', 'IV7', 'IV7', 'I7', 'I7', 'V7', 'IV7', 'I7', 'V7'],
            ['I7', 'IV7', 'I7', 'V7'],
        ],
        'free_jazz': [
            [],
        ],
    }

    # Terrain → scale to use
    TERRAIN_SCALES: Dict[str, List[int]] = {
        'delta_blues': BLUES_SCALE,
        'bebop': MAJOR_SCALE,
        'modal_jazz': DORIAN_SCALE,
        'hip_hop_trap': MINOR_SCALE,
        'electronic_techno': MINOR_SCALE,
        'classical_counterpoint': MAJOR_SCALE,
        'gospel': MAJOR_SCALE,
        'afro_cuban': MINOR_SCALE,
        'indian_raga': PENTATONIC_MAJOR,
        'chinese_silk_bamboo': PENTATONIC_MAJOR,
        'free_improvisation': MAJOR_SCALE,
        'bluegrass': MAJOR_SCALE,
        'modal': DORIAN_SCALE,
        'blues': BLUES_SCALE,
        'free_jazz': list(range(12)),
    }

    # Determine if terrain uses minor key
    TERRAIN_MINOR: Dict[str, bool] = {
        'delta_blues': True,
        'bebop': False,
        'modal_jazz': True,
        'hip_hop_trap': True,
        'electronic_techno': True,
        'classical_counterpoint': False,
        'gospel': False,
        'afro_cuban': True,
        'indian_raga': False,
        'chinese_silk_bamboo': False,
        'free_improvisation': False,
        'bluegrass': False,
        'modal': True,
        'blues': True,
        'free_jazz': False,
    }

    def __init__(self, key: str = 'C', bpm: int = 120, bars: int = 8, seed: int = None):
        """Create a chord generator.

        Args:
            key: Musical key (e.g. 'C', 'Eb', 'F#')
            bpm: Tempo in BPM
            bars: Number of bars
            seed: Random seed for reproducibility
        """
        self.key = key.strip()
        self.key_pc = _resolve_note_name(self.key)
        self.bpm = int(bpm)
        self.bars = int(bars)
        self.seed = seed
        self._rng = random.Random(seed)

    def generate(self, terrain: str) -> ChordProgression:
        """Generate a chord progression for a given terrain.

        Args:
            terrain: Terrain name (e.g. 'bebop', 'delta_blues', 'hip_hop_trap')

        Returns:
            ChordProgression with chords timed across the requested bars
        """
        terrain = terrain.lower().strip()

        # Resolve aliases
        terrain_aliases = {
            'blues': 'blues', 'delta': 'delta_blues',
            'bebop_rich': 'bebop',
        }
        terrain = terrain_aliases.get(terrain, terrain)

        progressions = self.TERRAIN_PROGRESSIONS.get(terrain, [['I']])

        # Handle free improvisation / empty progressions
        if not progressions or all(not p for p in progressions):
            return ChordProgression(
                key=self.key,
                chords=[],
                total_bars=self.bars,
                bpm=self.bpm,
            )

        # Pick a progression
        roman_prog = list(self._rng.choice(progressions))

        # Determine scale
        scale = self.TERRAIN_SCALES.get(terrain, MAJOR_SCALE)
        is_minor = self.TERRAIN_MINOR.get(terrain, False)

        # Map Roman numerals to chords
        chords = self._roman_to_chords(roman_prog, scale, is_minor)

        # Time the chords across the bars
        self._time_chords(chords)

        return ChordProgression(
            key=self.key,
            chords=chords,
            total_bars=self.bars,
            bpm=self.bpm,
        )

    def generate_from_diagnostic(self, diagnostic_report) -> ChordProgression:
        """Generate a progression that targets the user's weak spots.

        Strategy:
        - Low direction? Use more harmonic movement (ii-V-I cycles).
        - Low structure? Use clear forms (AABA, 12-bar).
        - Low surprise? Use more substitutions and modal interchange.
        - Low complexity? Add extensions (9ths, 11ths).

        Args:
            diagnostic_report: A GoodmanEngine DiagnosticReport

        Returns:
            ChordProgression tailored to address weaknesses
        """
        # Extract scores from the diagnostic report
        scores = {}
        if hasattr(diagnostic_report, 'orders'):
            for order in diagnostic_report.orders:
                scores[order.order] = getattr(order, 'score', 0.5)
        elif isinstance(diagnostic_report, dict):
            scores = diagnostic_report.get('scores', {})

        # Pick terrain based on weakness
        # Low order-1 (direction) → lots of movement
        # Low order-2 (structure) → clear forms
        # Low order-3 (surprise) → substitutions
        # Default → bebop (good all-around)

        direction_score = scores.get(1, 0.5)
        structure_score = scores.get(2, 0.5)
        surprise_score = scores.get(3, 0.5)

        if direction_score < 0.3:
            # Need harmonic movement → bebop with ii-V-I cycles
            terrain = 'bebop'
        elif structure_score < 0.3:
            # Need clear form → classical or blues
            terrain = 'classical_counterpoint'
        elif surprise_score < 0.3:
            # Need more interest → modal jazz with interchange
            terrain = 'modal_jazz'
        else:
            terrain = 'bebop'

        return self.generate(terrain)

    def _roman_to_chords(self, roman_prog: List[str],
                         scale: List[int], is_minor: bool) -> List[Chord]:
        """Convert Roman numeral progression to Chord objects.

        For minor-key terrains, lowercase roman numerals use the minor scale
        and uppercase use the relative major intervals.
        """
        chords = []
        effective_scale = MINOR_SCALE if is_minor else MAJOR_SCALE

        for roman in roman_prog:
            root_pc, quality = _roman_to_degree(roman, self.key_pc, effective_scale)

            # Generate symbol
            root_name = PC_TO_NAME.get(root_pc, '?')
            quality_suffix = {
                'maj': '', 'min': 'm', 'dom7': '7', 'min7': 'm7',
                'maj7': 'maj7', 'dim': 'dim', 'dim7': 'dim7',
                'aug': 'aug', 'sus4': 'sus4', 'sus2': 'sus2',
                'min9': 'm9', 'dom9': '9', 'maj9': 'maj9',
                'min11': 'm11', '7sus4': '7sus4',
            }.get(quality, '')

            symbol = f"{root_name}{quality_suffix}"

            # Root MIDI pitch (in octave 4)
            root_midi = root_pc + 60
            # Adjust to be in a reasonable range
            while root_midi < 48:
                root_midi += 12
            while root_midi > 72:
                root_midi -= 12

            chord = Chord(
                root=root_midi,
                quality=quality,
                symbol=symbol,
                start_beat=0.0,  # will be set by _time_chords
                duration_beats=4.0,  # default, will be overridden
            )
            chords.append(chord)

        return chords

    def _time_chords(self, chords: List[Chord]) -> None:
        """Distribute chords evenly across the total bars.

        Each chord gets equal time: total_beats / len(chords).
        """
        if not chords:
            return

        total_beats = self.bars * 4
        beats_per_chord = total_beats / len(chords)

        for i, chord in enumerate(chords):
            chord.start_beat = i * beats_per_chord
            chord.duration_beats = beats_per_chord


# ── Chord-aware Note Filtering ───────────────────────────────────────

def constrain_notes_to_progression(notes: List[dict],
                                   progression: ChordProgression,
                                   strictness: float = 0.7) -> List[dict]:
    """Filter/adjust notes to fit a chord progression.

    For each note, checks if it's a chord tone or passing tone at that beat.
    If not (and random check based on strictness), nudges it to the nearest
    chord tone.

    Args:
        notes: List of note dicts with 'pitch', 'start_time', etc.
        progression: The chord progression to follow
        strictness: How strictly to enforce (0.0 = free, 1.0 = only chord tones)

    Returns:
        Adjusted list of note dicts
    """
    if not progression.chords:
        return notes

    adjusted = []
    for n in notes:
        n = dict(n)  # copy
        beat = n['start_time'] * progression.bpm / 60.0
        chord = progression.at_beat(beat)

        if chord is None:
            adjusted.append(n)
            continue

        if chord.is_chord_tone(n['pitch']):
            # It's a chord tone — always keep it
            adjusted.append(n)
        elif self._rng.random() < strictness:
            # Nudge to nearest chord tone
            chord_pcs = chord.pitch_classes
            note_pc = _pc(n['pitch'])

            # Find nearest chord tone pitch class
            best_pc = min(chord_pcs, key=lambda pc: min(abs(pc - note_pc), 12 - abs(pc - note_pc)))

            # Adjust pitch
            octave = n['pitch'] // 12
            n['pitch'] = octave * 12 + best_pc

            # Make sure it's in MIDI range
            if n['pitch'] < 21:
                n['pitch'] += 12
            elif n['pitch'] > 108:
                n['pitch'] -= 12

            adjusted.append(n)
        else:
            # Allow the non-chord tone (passing tone)
            adjusted.append(n)

    return adjusted


# Standalone function (not a method) for external use
def nudge_to_chord_tones(notes: List[dict],
                         progression: ChordProgression,
                         strictness: float = 0.7,
                         rng: random.Random = None) -> List[dict]:
    """Nudge notes toward chord tones based on the progression.

    This is the main entry point for making notes "follow the changes."

    Args:
        notes: List of note dicts
        progression: Chord progression to follow
        strictness: 0.0 (free) to 1.0 (only chord tones)
        rng: Random instance (created if not provided)

    Returns:
        Adjusted list of note dicts
    """
    if rng is None:
        rng = random.Random()

    if not progression.chords:
        return notes

    adjusted = []
    for n in notes:
        n = dict(n)  # copy
        beat = n['start_time'] * progression.bpm / 60.0
        chord = progression.at_beat(beat)

        if chord is None:
            adjusted.append(n)
            continue

        if chord.is_chord_tone(n['pitch']):
            adjusted.append(n)
            continue

        # Non-chord tone — nudge based on strictness
        if rng.random() < strictness:
            chord_pcs = chord.pitch_classes
            note_pc = _pc(n['pitch'])

            # Find nearest chord tone
            best_pc = min(chord_pcs,
                          key=lambda pc: min(abs(pc - note_pc), 12 - abs(pc - note_pc)))

            octave = n['pitch'] // 12
            new_pitch = octave * 12 + best_pc
            if new_pitch < 21:
                new_pitch += 12
            elif new_pitch > 108:
                new_pitch -= 12
            n['pitch'] = new_pitch

        adjusted.append(n)

    return adjusted
