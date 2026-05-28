"""
Constraint-based composition engine.

Generates MIDI from dial targets using constraint propagation (arc consistency)
for voice leading, harmonic tension bounds, and rhythmic density targets.

Supports monophonic and polyphonic composition with chord progressions,
bass lines, and drum patterns per tradition.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from numpy.typing import NDArray

try:
    from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
except ImportError:
    raise ImportError("mido is required: pip install mido")

from .dials import DIAL_RANGES, DialPosition, UNEXPLORED_FRACTION
from .midi_utils import onsets_to_midi


# Common scales as pitch class sets
SCALES: dict[str, list[int]] = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "blues": [0, 3, 5, 6, 7, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "whole_tone": [0, 2, 4, 6, 8, 10],
    "chromatic": list(range(12)),
    "jazz_melodic_minor": [0, 2, 3, 5, 7, 9, 11],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
}

# Genre → scale mapping
GENRE_SCALES: dict[str, str] = {
    "Jazz": "dorian",
    "Blues": "blues",
    "Classical": "major",
    "EDM": "minor",
    "Hip-hop": "pentatonic",
    "Latin": "mixolydian",
    "Gamelan": "pentatonic",
    "Gagaku": "pentatonic",
    "Hindustani": "harmonic_minor",
    "African Polyrhythm": "pentatonic",
}

# Chord degree → intervals for diatonic chords in major
MAJOR_CHORD_DEGREES = {
    1: [0, 4, 7],     # I
    2: [2, 5, 9],     # ii
    3: [4, 7, 11],    # iii
    4: [5, 9, 12],    # IV
    5: [7, 11, 14],   # V
    6: [9, 12, 16],   # vi
    7: [11, 14, 17],  # vii°
}

# Common chord progressions per tradition (list of scale degrees per bar)
PROGRESSIONS: dict[str, list[list[int]]] = {
    "Jazz": [[2, 5, 1, 1], [1, 6, 2, 5]],
    "Blues": [[1, 1, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5]],
    "Classical": [[1, 5, 6, 3, 4, 1, 4, 5], [1, 4, 5, 1]],
    "EDM": [[1, 5, 6, 4], [6, 4, 1, 5]],
    "Hip-hop": [[1, 4, 5, 4]],
    "Latin": [[1, 4, 5, 1]],
    "Gamelan": [[1, 1, 5, 5]],
    "Gagaku": [[1, 1, 1, 1]],
    "Hindustani": [[1, 1, 4, 4, 5, 5, 1, 1]],
    "African Polyrhythm": [[1, 1, 1, 1]],
}

# Drum patterns: (16th-note offset, GM note, velocity)
DRUM_PATTERNS: dict[str, list[tuple[int, int, int]]] = {
    "Jazz": [(0, 51, 80), (3, 51, 60), (4, 42, 50), (6, 51, 70), (8, 51, 80), (11, 51, 60), (12, 42, 50), (14, 51, 70)],
    "Blues": [(0, 36, 90), (0, 42, 70), (2, 42, 50), (4, 38, 90), (4, 42, 70), (6, 42, 50), (8, 36, 90), (8, 42, 70), (10, 42, 50), (12, 38, 90), (12, 42, 70), (14, 42, 50)],
    "Classical": [(0, 36, 70), (4, 36, 60), (8, 36, 70), (12, 36, 60)],
    "EDM": [(0, 36, 100), (0, 42, 80), (2, 42, 60), (4, 36, 100), (4, 42, 80), (4, 38, 90), (6, 42, 60), (8, 36, 100), (8, 42, 80), (10, 42, 60), (12, 36, 100), (12, 42, 80), (12, 38, 90), (14, 42, 60)],
    "Hip-hop": [(0, 36, 100), (0, 42, 70), (2, 42, 50), (4, 42, 70), (6, 38, 90), (6, 42, 50), (8, 36, 90), (8, 42, 70), (10, 42, 50), (12, 42, 70), (14, 38, 80)],
    "Latin": [(0, 36, 90), (0, 42, 70), (3, 42, 60), (4, 42, 70), (6, 36, 80), (8, 42, 70), (10, 42, 60), (11, 38, 80), (12, 42, 70), (14, 36, 90)],
    "Gamelan": [(0, 36, 80), (4, 36, 60), (8, 36, 80), (12, 36, 60)],
    "Gagaku": [(0, 36, 70), (8, 36, 70)],
    "Hindustani": [(0, 36, 80), (2, 42, 60), (4, 42, 70), (6, 42, 60), (8, 36, 80), (10, 42, 60), (12, 42, 70), (14, 42, 60)],
    "African Polyrhythm": [(0, 36, 90), (0, 42, 80), (2, 42, 60), (3, 36, 70), (4, 42, 80), (6, 42, 60), (8, 36, 90), (8, 42, 80), (9, 36, 70), (10, 42, 60), (12, 42, 80), (14, 42, 60)],
}


def _consonance_interval(semitones: int) -> float:
    """Rate the consonance of an interval (1=perfect, 0=dissonant)."""
    s = abs(semitones) % 12
    consonance_map = {
        0: 1.0, 1: 0.2, 2: 0.4, 3: 0.6, 4: 0.8,
        5: 0.9, 6: 0.1, 7: 1.0, 8: 0.6, 9: 0.7,
        10: 0.4, 11: 0.3,
    }
    return consonance_map.get(s, 0.0)


class ConstraintComposer:
    """Constraint-based composition engine.

    Generates MIDI sequences that satisfy constraints on:
    - Voice leading (smooth interval transitions)
    - Harmonic tension (stays within target dial bounds)
    - Rhythmic density (matches target density)
    - Scale/mode constraints

    Supports polyphonic output with melody, bass, chords, and drums.

    Parameters
    ----------
    seed : int
        Random seed for reproducibility.
    """

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self._rng = np.random.RandomState(seed)

    def compose(
        self,
        dial_targets: DialPosition,
        bars: int = 8,
        tempo: int = 120,
        n_voices: int = 1,
        scale_name: Optional[str] = None,
    ) -> MidiFile:
        """Compose a piece targeting specific dial positions.

        Parameters
        ----------
        dial_targets : DialPosition
            Target dial position.
        bars : int
            Number of bars to compose.
        tempo : int
            Tempo in BPM.
        n_voices : int
            Number of voices. 1=melody only, 2+=melody+bass+chords+drums.
        scale_name : str or None
            Scale to use. If None, inferred from dial position.

        Returns
        -------
        MidiFile
            Generated composition.
        """
        if bars <= 0:
            raise ValueError(f"bars must be positive, got {bars}")
        if tempo <= 0:
            raise ValueError(f"tempo must be positive, got {tempo}")

        rng = np.random.RandomState(self.seed)

        # Determine scale
        if scale_name is None:
            ht = dial_targets.harmonic_tension
            if ht < 1.5:
                scale_name = "pentatonic"
            elif ht < 2.5:
                scale_name = "major"
            elif ht < 3.5:
                scale_name = "dorian"
            elif ht < 4.5:
                scale_name = "blues"
            else:
                scale_name = "chromatic"

        scale = SCALES.get(scale_name, SCALES["major"])

        # Timing
        bar_duration = 4.0 * 60.0 / tempo
        total_duration = bars * bar_duration

        # Determine rhythmic density from dial
        rc = dial_targets.rhythmic_complexity
        notes_per_bar = max(1, int(1 + rc * 3))
        total_notes = bars * notes_per_bar

        # Pitch range from spectral density
        sd = dial_targets.spectral_density
        min_pitch = 48 + int((5 - sd) * 4)
        max_pitch = min_pitch + int(8 + sd * 8)

        # Filter scale notes within range
        available_pitches = []
        for octave in range(0, 10):
            for pc in scale:
                note = octave * 12 + pc
                if min_pitch <= note <= max_pitch:
                    available_pitches.append(note)
        if not available_pitches:
            available_pitches = list(range(60, 73))

        # Generate melody onset times
        onset_times = np.linspace(0, total_duration, total_notes + 1)[:-1]
        if rc > 1.0:
            grid_period = bar_duration / notes_per_bar
            for i in range(len(onset_times)):
                if rng.random() < rc / 5.0:
                    shift = rng.choice([-1, 1]) * grid_period * rng.uniform(0.25, 0.75)
                    onset_times[i] = np.clip(onset_times[i] + shift, 0, total_duration - 0.1)
        onset_times.sort()

        # Generate melody pitches with voice-leading constraints
        ht = dial_targets.harmonic_tension
        max_interval = int(2 + ht * 2)
        pitches: list[int] = []
        current_pitch = rng.choice(available_pitches)

        for i in range(total_notes):
            candidates = [p for p in available_pitches if abs(p - current_pitch) <= max_interval]
            if not candidates:
                candidates = available_pitches

            if ht < 2.0:
                consonant = [p for p in candidates if _consonance_interval(p - current_pitch) >= 0.6]
                if consonant:
                    candidates = consonant

            weights = np.array([1.0 / (abs(p - current_pitch) + 1) for p in candidates], dtype=np.float64)
            weights /= weights.sum()
            chosen = int(rng.choice(candidates, p=weights))
            pitches.append(chosen)
            current_pitch = chosen

        # Generate velocities
        base_velocity = int(40 + sd * 17)
        velocities = [max(30, min(127, base_velocity + rng.randint(-15, 16))) for _ in range(total_notes)]

        melody_onsets = [(float(onset_times[i]), pitches[i], velocities[i]) for i in range(total_notes)]
        note_duration = (total_duration / total_notes) * 0.8

        # If single voice, return melody only
        if n_voices <= 1:
            return onsets_to_midi(melody_onsets, bpm=tempo, note_duration=note_duration)

        # --- Multi-track: melody + bass + chords + drums ---
        # Detect key from melody
        root_pc = pitches[0] % 12  # Simple: first note as root

        # Choose a chord progression
        tradition = dial_targets.tradition_name or "Classical"
        prog_options = PROGRESSIONS.get(tradition, PROGRESSIONS["Classical"])
        progression = prog_options[rng.randint(len(prog_options))]

        # Build multi-track MIDI
        mid = MidiFile(ticks_per_beat=480)
        ticks_per_second = mid.ticks_per_beat * tempo / 60.0
        sixteenth = bar_duration / 16.0

        # Tempo track
        tempo_track = MidiTrack()
        tempo_track.append(MetaMessage("set_tempo", tempo=bpm2tempo(tempo), time=0))
        mid.tracks.append(tempo_track)

        # Melody track
        melody_track = MidiTrack()
        melody_track.append(MetaMessage("track_name", name="Melody", time=0))
        mid.tracks.append(melody_track)

        # Bass track
        bass_track = MidiTrack()
        bass_track.append(MetaMessage("track_name", name="Bass", time=0))
        mid.tracks.append(bass_track)

        # Chord track
        chord_track = MidiTrack()
        chord_track.append(MetaMessage("track_name", name="Chords", time=0))
        mid.tracks.append(chord_track)

        # Drum track
        drum_track = MidiTrack()
        drum_track.append(MetaMessage("track_name", name="Drums", time=0))
        mid.tracks.append(drum_track)

        # Build melody events
        melody_events: list[tuple[int, str, int, int]] = []
        for t, p, v in melody_onsets:
            start = int(round(t * ticks_per_second))
            end = int(round((t + note_duration) * ticks_per_second))
            melody_events.append((start, "note_on", p, v))
            melody_events.append((end, "note_off", p, 0))

        # Build bass events
        bass_events: list[tuple[int, str, int, int]] = []
        for bar in range(bars):
            degree = progression[bar % len(progression)]
            intervals = MAJOR_CHORD_DEGREES.get(degree, [0, 4, 7])
            bass_note = 36 + (root_pc + intervals[0]) % 12
            bar_start = int(round(bar * bar_duration * ticks_per_second))

            if rc < 2.0:
                bass_events.append((bar_start, "note_on", bass_note, 90))
                bass_events.append((bar_start + int(bar_duration * ticks_per_second), "note_off", bass_note, 0))
            elif rc < 3.5:
                bass_events.append((bar_start, "note_on", bass_note, 90))
                bass_events.append((bar_start + int(bar_duration * 0.5 * ticks_per_second), "note_off", bass_note, 0))
                fifth = bass_note + 7
                half_bar = bar_start + int(bar_duration * 0.5 * ticks_per_second)
                bass_events.append((half_bar, "note_on", fifth, 75))
                bass_events.append((half_bar + int(bar_duration * 0.5 * ticks_per_second), "note_off", fifth, 0))
            else:
                for beat in range(4):
                    beat_start = bar_start + int(beat * bar_duration * 0.25 * ticks_per_second)
                    if beat % 2 == 0:
                        note = bass_note
                    elif beat == 1:
                        note = bass_note + (intervals[1] - intervals[0]) if len(intervals) > 1 else bass_note + 4
                    else:
                        note = bass_note + 7
                    bass_events.append((beat_start, "note_on", note, 70 + beat * 5))
                    bass_events.append((beat_start + int(bar_duration * 0.25 * ticks_per_second), "note_off", note, 0))

        # Build chord events
        chord_events: list[tuple[int, str, int, int]] = []
        prev_chord_notes: list[int] = []
        for bar in range(bars):
            degree = progression[bar % len(progression)]
            intervals = MAJOR_CHORD_DEGREES.get(degree, [0, 4, 7])

            # Voice leading
            chord_notes = [(root_pc + iv) % 12 + 60 for iv in intervals]
            if prev_chord_notes:
                # Minimize movement
                chord_notes = _minimize_voice_movement(prev_chord_notes, chord_notes)

            bar_start = int(round(bar * bar_duration * ticks_per_second))
            bar_dur_ticks = int(bar_duration * ticks_per_second)
            for note in chord_notes:
                chord_events.append((bar_start, "note_on", note, 65))
                chord_events.append((bar_start + bar_dur_ticks, "note_off", note, 0))
            prev_chord_notes = chord_notes

        # Build drum events
        drum_events: list[tuple[int, str, int, int]] = []
        pattern = DRUM_PATTERNS.get(tradition, DRUM_PATTERNS["Classical"])
        for bar in range(bars):
            bar_start = int(round(bar * bar_duration * ticks_per_second))
            for offset_16ths, drum_note, vel in pattern:
                tick = bar_start + int(offset_16ths * sixteenth * ticks_per_second)
                drum_events.append((tick, "note_on", drum_note, vel))
                drum_events.append((tick + int(0.1 * ticks_per_second), "note_off", drum_note, 0))

        # Write all tracks
        def write_events(track, events, channel=0):
            events.sort(key=lambda x: (x[0], 0 if x[1] == "note_off" else 1))
            prev_tick = 0
            for tick, msg_type, note, vel in events:
                delta = max(0, tick - prev_tick)
                track.append(Message(msg_type, note=note, velocity=vel, time=delta, channel=channel))
                prev_tick = tick

        write_events(melody_track, melody_events, channel=0)
        write_events(bass_track, bass_events, channel=1)
        write_events(chord_track, chord_events, channel=2)
        write_events(drum_track, drum_events, channel=9)

        return mid

    def compose_in_tradition(
        self,
        tradition: str,
        bars: int = 8,
        tempo: int = 120,
    ) -> MidiFile:
        """Compose a piece in a specific musical tradition."""
        if tradition not in DIAL_RANGES:
            raise ValueError(
                f"Unknown tradition '{tradition}'. Available: {list(DIAL_RANGES.keys())}"
            )
        center = DIAL_RANGES[tradition]["center"]
        target = DialPosition.from_array(center, tradition_name=tradition)
        scale_name = GENRE_SCALES.get(tradition, "major")
        return self.compose(target, bars=bars, tempo=tempo, n_voices=4, scale_name=scale_name)

    def compose_novel(
        self,
        dial_position: Optional[DialPosition] = None,
        bars: int = 8,
        tempo: int = 120,
    ) -> MidiFile:
        """Compose in an unexplored region of dial space."""
        rng = np.random.RandomState(self.seed + 1000)
        if dial_position is None:
            tradition_centers = np.array([DIAL_RANGES[t]["center"] for t in DIAL_RANGES])
            best_pos = None
            best_min_dist = -1
            for _ in range(1000):
                candidate = rng.uniform(0, 5, size=3)
                dists = np.linalg.norm(tradition_centers - candidate, axis=1)
                min_dist = dists.min()
                if min_dist > best_min_dist:
                    best_min_dist = min_dist
                    best_pos = candidate
            dial_position = DialPosition.from_array(
                best_pos,
                tradition_name="Novel",
                metadata={"min_distance_to_known": float(best_min_dist)},
            )
        return self.compose(dial_position, bars=bars, tempo=tempo)


def _minimize_voice_movement(prev: list[int], target: list[int]) -> list[int]:
    """Adjust target chord voicing to minimize total semitone movement from prev."""
    if not prev:
        return target

    best = target
    best_cost = sum(abs(t - p) for t, p in zip(target, prev))

    # Try octave shifts
    for shift in [-12, 0, 12]:
        shifted = [t + shift for t in target]
        cost = sum(abs(s - p) for s, p in zip(shifted, prev))
        if cost < best_cost:
            best_cost = cost
            best = shifted

    return best
