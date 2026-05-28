"""
Auto-accompaniment generator.

Generates bass, chord, and drum accompaniment that fits a given melody,
using Krumhansl-Schmuckler key detection, circle-of-fifths chord suggestion,
and tradition-specific rhythmic patterns.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from numpy.typing import NDArray

try:
    from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
except ImportError:
    raise ImportError("mido is required: pip install mido")

from .dials import DIAL_RANGES, DialPosition
from .midi_utils import extract_onset_times, extract_pitch_classes_from_midi, onsets_to_midi
from .composer import SCALES, GENRE_SCALES


# Krumhansl-Schmuckler key profiles (major and minor)
KS_MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KS_MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

# Common chord progressions by tradition
CHORD_PROGRESSIONS: dict[str, list[list[int]]] = {
    "Jazz": [[2, 5, 1, 1], [1, 6, 2, 5], [1, 4, 2, 5]],  # ii-V-I, I-vi-ii-V, etc.
    "Blues": [[1, 1, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5]],  # 12-bar blues
    "Classical": [[1, 5, 6, 3, 4, 1, 4, 5], [1, 4, 5, 1]],
    "EDM": [[1, 5, 6, 4], [6, 4, 1, 5]],
    "Hip-hop": [[1, 4, 5, 4], [1, 6, 4, 5]],
    "Latin": [[1, 4, 5, 1], [1, 5, 4, 1]],
    "Gamelan": [[1, 1, 5, 5]],
    "Gagaku": [[1, 1, 1, 1]],
    "Hindustani": [[1, 1, 4, 4, 5, 5, 1, 1]],
    "African Polyrhythm": [[1, 1, 1, 1]],
}

# Roman numeral → semitone intervals from root
CHORD_INTERVALS = {
    1: [0, 4, 7],       # I major
    2: [2, 5, 9],       # ii minor
    3: [4, 7, 11],      # iii minor
    4: [5, 9, 12],      # IV major
    5: [7, 11, 14],     # V major
    6: [9, 12, 16],     # vi minor
    7: [11, 14, 17],    # vii diminished
}

# Drum patterns: (offset_in_16ths, note, velocity)
# GM drum map: 36=bass drum, 38=snare, 42=closed hi-hat, 46=open hi-hat, 49=crash
DRUM_PATTERNS: dict[str, list[list[tuple[int, int, int]]]] = {
    "Jazz": [
        # Swing ride pattern with hi-hat on 2 and 4
        [(0, 51, 80), (3, 51, 60), (4, 42, 50), (6, 51, 70), (8, 51, 80), (11, 51, 60), (12, 42, 50), (14, 51, 70)],
    ],
    "Blues": [
        # Shuffle
        [(0, 36, 90), (0, 42, 70), (2, 42, 50), (4, 38, 90), (4, 42, 70), (6, 42, 50),
         (8, 36, 90), (8, 42, 70), (10, 42, 50), (12, 38, 90), (12, 42, 70), (14, 42, 50)],
    ],
    "Classical": [
        # Simple orchestral
        [(0, 36, 70), (4, 36, 60), (8, 36, 70), (12, 36, 60)],
    ],
    "EDM": [
        # Four-on-the-floor
        [(0, 36, 100), (0, 42, 80), (2, 42, 60), (4, 36, 100), (4, 42, 80), (4, 38, 90),
         (6, 42, 60), (8, 36, 100), (8, 42, 80), (10, 42, 60), (12, 36, 100), (12, 42, 80),
         (12, 38, 90), (14, 42, 60)],
    ],
    "Hip-hop": [
        # Boom-bap
        [(0, 36, 100), (0, 42, 70), (2, 42, 50), (4, 42, 70), (6, 38, 90), (6, 42, 50),
         (8, 36, 90), (8, 42, 70), (10, 42, 50), (12, 42, 70), (14, 38, 80)],
    ],
    "Latin": [
        # Clave-based
        [(0, 36, 90), (0, 42, 70), (3, 42, 60), (4, 42, 70), (6, 36, 80), (8, 42, 70),
         (10, 42, 60), (11, 38, 80), (12, 42, 70), (14, 36, 90)],
    ],
    "Gamelan": [
        [(0, 36, 80), (4, 36, 60), (8, 36, 80), (12, 36, 60)],
    ],
    "Gagaku": [
        [(0, 36, 70), (8, 36, 70)],
    ],
    "Hindustani": [
        [(0, 36, 80), (2, 42, 60), (4, 42, 70), (6, 42, 60), (8, 36, 80), (10, 42, 60), (12, 42, 70), (14, 42, 60)],
    ],
    "African Polyrhythm": [
        # Polyrhythmic pattern (3 against 2 feel)
        [(0, 36, 90), (0, 42, 80), (2, 42, 60), (3, 36, 70), (4, 42, 80), (6, 42, 60),
         (8, 36, 90), (8, 42, 80), (9, 36, 70), (10, 42, 60), (12, 42, 80), (14, 42, 60)],
    ],
}


def _detect_key(pitch_classes: NDArray[np.intp]) -> tuple[int, str]:
    """Detect key using Krumhansl-Schmuckler algorithm.

    Parameters
    ----------
    pitch_classes : ndarray of int
        Pitch class array.

    Returns
    -------
    (root_pc, mode) : tuple
        Root pitch class (0-11) and mode ("major" or "minor").
    """
    if len(pitch_classes) == 0:
        return 0, "major"

    # Build pitch class distribution
    pc_hist = np.bincount(pitch_classes, minlength=12).astype(np.float64)

    best_correlation = -999.0
    best_root = 0
    best_mode = "major"

    for root in range(12):
        rotated = np.roll(pc_hist, -root)

        # Correlate with major profile
        if np.std(rotated) > 0 and np.std(KS_MAJOR_PROFILE) > 0:
            corr = float(np.corrcoef(rotated, KS_MAJOR_PROFILE)[0, 1])
        else:
            corr = 0.0
        if corr > best_correlation:
            best_correlation = corr
            best_root = root
            best_mode = "major"

        # Correlate with minor profile
        if np.std(rotated) > 0 and np.std(KS_MINOR_PROFILE) > 0:
            corr = float(np.corrcoef(rotated, KS_MINOR_PROFILE)[0, 1])
        else:
            corr = 0.0
        if corr > best_correlation:
            best_correlation = corr
            best_root = root
            best_mode = "minor"

    return best_root, best_mode


def _voice_lead_chords(
    chords: list[list[int]],
    root_pc: int,
) -> list[list[int]]:
    """Apply voice leading to minimize total semitone movement.

    Parameters
    ----------
    chords : list of list of int
        Chord intervals from root.
    root_pc : int
        Root pitch class.

    Returns
    -------
    list of list of int
        Voiced chords as absolute MIDI note numbers.
    """
    voiced: list[list[int]] = []
    prev_notes: list[int] = []

    for chord_intervals in chords:
        # Root the chord
        root_note = 48 + root_pc  # Bass octave
        candidates = [root_note + iv for iv in chord_intervals]

        if not prev_notes:
            # First chord: use close voicing around middle C
            voiced_chord = sorted(candidates)
        else:
            # Find voicing that minimizes total movement
            # Simple approach: for each note, find closest to previous
            voiced_chord = []
            used = set()
            for prev in prev_notes:
                best_note = candidates[0]
                best_dist = 999
                for c in candidates:
                    dist = abs(c - prev)
                    if c not in used and dist < best_dist:
                        best_dist = dist
                        best_note = c
                voiced_chord.append(best_note)
                used.add(best_note)
            # Add any remaining notes
            for c in candidates:
                if c not in used:
                    voiced_chord.append(c)

        voiced.append(sorted(voiced_chord))
        prev_notes = voiced[-1]

    return voiced


class AutoAccompanist:
    """Generate accompaniment that fits a given melody.

    Provides bass lines, chord progressions, and drum patterns
    based on tradition profiles and the melody's key.

    Parameters
    ----------
    sr : int
        Sample rate (for potential audio rendering).
    """

    def __init__(self, sr: int = 44100) -> None:
        self.sr = sr

    def _get_chord_progression(
        self,
        tradition: str,
        n_bars: int,
        root_pc: int,
        mode: str,
    ) -> list[tuple[int, list[int]]]:
        """Get a chord progression for the tradition.

        Returns list of (bar_index, chord_intervals) tuples.
        """
        progressions = CHORD_PROGRESSIONS.get(tradition, CHORD_PROGRESSIONS["Classical"])
        prog = progressions[0]  # Use first progression

        # Build per-bar chords
        chords: list[tuple[int, list[int]]] = []
        prog_len = len(prog)

        # Adjust intervals for minor mode
        for bar in range(n_bars):
            numeral = prog[bar % prog_len]
            intervals = list(CHORD_INTERVALS.get(numeral, [0, 4, 7]))

            # Minor mode adjustments
            if mode == "minor" and numeral in (1, 4, 5):
                # In minor: i, iv, V (lower 3rd of i and iv)
                if numeral == 1:
                    intervals = [iv - 1 if iv == 4 else iv for iv in intervals]
                elif numeral == 4:
                    intervals = [iv - 1 if iv == 4 else iv for iv in intervals]

            chords.append((bar, intervals))

        return chords

    def _generate_bass_line(
        self,
        chords: list[tuple[int, list[int]]],
        root_pc: int,
        bar_duration: float,
        tradition: str,
    ) -> list[tuple[float, int, int]]:
        """Generate bass line from chord progression.

        Parameters
        ----------
        chords : list of (bar, intervals)
            Chord progression.
        root_pc : int
            Key root pitch class.
        bar_duration : float
            Duration of one bar in seconds.
        tradition : str
            Tradition for style.

        Returns
        -------
        list of (time, pitch, velocity) onset tuples.
        """
        bass_onsets: list[tuple[float, int, int]] = []
        rng = np.random.RandomState(42)

        for bar_idx, (bar, intervals) in enumerate(chords):
            root_note = 36 + (root_pc + intervals[0]) % 12  # Bass in low octave

            # Complexity based on tradition
            rc = DIAL_RANGES.get(tradition, {}).get("center", np.array([2.5, 2.5, 2.5]))[1]

            if rc < 2.0:
                # Simple bass: root on beat 1
                bass_onsets.append((bar * bar_duration, root_note, 90))
            elif rc < 3.5:
                # Medium: root + fifth
                bass_onsets.append((bar * bar_duration, root_note, 90))
                fifth = root_note + 7
                bass_onsets.append((bar * bar_duration + bar_duration * 0.5, fifth, 75))
            else:
                # Complex: walking bass
                bass_onsets.append((bar * bar_duration, root_note, 90))
                third = root_note + (intervals[1] - intervals[0])
                fifth = root_note + 7
                octave = root_note + 12
                bass_onsets.append((bar * bar_duration + bar_duration * 0.25, third, 70))
                bass_onsets.append((bar * bar_duration + bar_duration * 0.5, fifth, 75))
                bass_onsets.append((bar * bar_duration + bar_duration * 0.75, octave, 65))

        return bass_onsets

    def _generate_chords(
        self,
        chords: list[tuple[int, list[int]]],
        root_pc: int,
        bar_duration: float,
        tradition: str,
    ) -> list[tuple[float, int, int]]:
        """Generate chord onsets from chord progression.

        Returns onset tuples for chord tones.
        """
        chord_onsets: list[tuple[float, int, int]] = []

        # Get voiced chords
        raw_intervals = [intervals for _, intervals in chords]
        voiced = _voice_lead_chords(raw_intervals, root_pc)

        for (bar_idx, (_, intervals)), chord_voicing in zip(enumerate(chords), voiced):
            # Hit chord on beat 1 of each bar
            for note in chord_voicing:
                # Map to reasonable MIDI range
                note_mapped = note % 12 + 60  # Middle octave
                chord_onsets.append((bar_idx * bar_duration, note_mapped, 65))

        return chord_onsets

    def _generate_drums(
        self,
        n_bars: int,
        bar_duration: float,
        tradition: str,
    ) -> list[tuple[float, int, int]]:
        """Generate drum pattern onsets.

        Parameters
        ----------
        n_bars : int
            Number of bars.
        bar_duration : float
            Duration per bar in seconds.
        tradition : str
            Tradition for drum pattern.

        Returns
        -------
        list of (time, note, velocity) onset tuples.
        """
        patterns = DRUM_PATTERNS.get(tradition, DRUM_PATTERNS["Classical"])
        pattern = patterns[0]

        sixteenth_duration = bar_duration / 16.0
        drum_onsets: list[tuple[float, int, int]] = []

        for bar in range(n_bars):
            for offset_16ths, note, velocity in pattern:
                time = bar * bar_duration + offset_16ths * sixteenth_duration
                drum_onsets.append((time, note, velocity))

        return drum_onsets

    def accompany(
        self,
        melody_midi: MidiFile,
        tradition: str = "Jazz",
        bars: Optional[int] = None,
        bpm: int = 120,
    ) -> MidiFile:
        """Generate bass + chords + drums for a melody.

        Parameters
        ----------
        melody_midi : MidiFile
            Input melody MIDI.
        tradition : str
            Tradition for accompaniment style.
        bars : int or None
            Number of bars. If None, inferred from melody.
        bpm : int
            Tempo.

        Returns
        -------
        MidiFile
            Multi-track MIDI with melody, bass, chords, and drums.
        """
        if tradition not in DIAL_RANGES:
            raise ValueError(
                f"Unknown tradition '{tradition}'. Available: {list(DIAL_RANGES.keys())}"
            )

        bar_duration = 4.0 * 60.0 / bpm

        # Extract melody features
        onset_times = extract_onset_times(melody_midi, bpm)
        pitch_classes = extract_pitch_classes_from_midi(melody_midi)

        # Detect key
        root_pc, mode = _detect_key(pitch_classes)

        # Determine number of bars
        if bars is None:
            if len(onset_times) > 0:
                total_duration = float(onset_times[-1]) + bar_duration
                bars = max(1, int(np.ceil(total_duration / bar_duration)))
            else:
                bars = 4

        # Get chord progression
        chords = self._get_chord_progression(tradition, bars, root_pc, mode)

        # Generate parts
        bass_onsets = self._generate_bass_line(chords, root_pc, bar_duration, tradition)
        chord_onsets = self._generate_chords(chords, root_pc, bar_duration, tradition)
        drum_onsets = self._generate_drums(bars, bar_duration, tradition)

        # Build multi-track MIDI
        result = MidiFile(ticks_per_beat=480)
        ticks_per_second = result.ticks_per_beat * bpm / 60.0

        # Tempo track
        tempo_track = MidiTrack()
        tempo_track.append(MetaMessage("set_tempo", tempo=bpm2tempo(bpm), time=0))
        result.tracks.append(tempo_track)

        # Extract melody note events for proper duration tracking
        melody_onsets: list[tuple[float, int, int]] = []
        melody_durations: list[float] = []

        for track in melody_midi.tracks:
            abs_tick = 0
            active: dict[int, tuple[int, int]] = {}
            for msg in track:
                abs_tick += msg.time
                if msg.type == "note_on" and msg.velocity > 0:
                    active[msg.note] = (abs_tick, msg.velocity)
                elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                    if msg.note in active:
                        st, vel = active.pop(msg.note)
                        start_sec = st / ticks_per_second
                        dur = (abs_tick - st) / ticks_per_second
                        if dur < 0.05:
                            dur = 0.25
                        melody_onsets.append((start_sec, msg.note, vel))
                        melody_durations.append(dur)

        if not melody_onsets:
            for ot, pc in zip(onset_times, pitch_classes):
                melody_onsets.append((ot, 60 + pc, 80))
                melody_durations.append(0.3)

        # Add melody track
        melody_track = MidiTrack()
        melody_track.append(MetaMessage("track_name", name="Melody", time=0))
        result.tracks.append(melody_track)

        # Add bass track
        bass_track = MidiTrack()
        bass_track.append(MetaMessage("track_name", name="Bass", time=0))
        result.tracks.append(bass_track)

        # Add chord track
        chord_track = MidiTrack()
        chord_track.append(MetaMessage("track_name", name="Chords", time=0))
        result.tracks.append(chord_track)

        # Add drum track (channel 9)
        drum_track = MidiTrack()
        drum_track.append(MetaMessage("track_name", name="Drums", time=0))
        result.tracks.append(drum_track)

        # Convert onsets to events for each track
        def build_events(onset_list, durations_list=None, default_dur=0.3):
            events = []
            for i, (t, note, vel) in enumerate(onset_list):
                dur = default_dur
                if durations_list and i < len(durations_list):
                    dur = durations_list[i]
                start_tick = int(round(t * ticks_per_second))
                end_tick = int(round((t + dur) * ticks_per_second))
                events.append((start_tick, "note_on", note, vel))
                events.append((end_tick, "note_off", note, 0))
            events.sort(key=lambda x: (x[0], 0 if x[1] == "note_off" else 1))
            return events

        # Build all events
        melody_events = build_events(melody_onsets, melody_durations)
        bass_events = build_events(bass_onsets, default_dur=bar_duration / 4)
        chord_events = build_events(chord_onsets, default_dur=bar_duration)
        drum_events = build_events(drum_onsets, default_dur=0.1)

        def write_track(track, events, channel=0):
            prev_tick = 0
            for tick, msg_type, note, vel in events:
                delta = max(0, tick - prev_tick)
                track.append(Message(msg_type, note=note, velocity=vel, time=delta, channel=channel))
                prev_tick = tick

        write_track(melody_track, melody_events, channel=0)
        write_track(bass_track, bass_events, channel=1)
        write_track(chord_track, chord_events, channel=2)
        write_track(drum_track, drum_events, channel=9)

        return result

    def suggest_chords(
        self,
        melody_pitches: list[int] | NDArray[np.intp],
        tradition: str = "Jazz",
    ) -> list[list[int]]:
        """Suggest chord progression from melody notes.

        Parameters
        ----------
        melody_pitches : list of int or ndarray
            MIDI note numbers of melody.
        tradition : str
            Tradition for chord style.

        Returns
        -------
        list of list of int
            Suggested chords as lists of MIDI note numbers.
        """
        if isinstance(melody_pitches, np.ndarray):
            melody_pitches = melody_pitches.tolist()

        if not melody_pitches:
            return [[60, 64, 67]]  # C major

        pitch_classes = np.array([p % 12 for p in melody_pitches], dtype=np.intp)
        root_pc, mode = _detect_key(pitch_classes)

        # Get progression
        n_bars = max(4, len(melody_pitches) // 4)
        chords = self._get_chord_progression(tradition, n_bars, root_pc, mode)

        # Convert to MIDI note numbers
        raw_intervals = [intervals for _, intervals in chords]
        voiced = _voice_lead_chords(raw_intervals, root_pc)

        # Remap to proper octave
        result = []
        for chord_voicing in voiced:
            result.append([n % 12 + 60 for n in chord_voicing])

        return result
