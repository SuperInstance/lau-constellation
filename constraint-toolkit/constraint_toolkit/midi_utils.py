"""
MIDI utilities for reading, writing, and manipulating MIDI data.

Uses the mido library for MIDI file I/O.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
from numpy.typing import NDArray

try:
    import mido
    from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo, tempo2bpm
except ImportError:
    raise ImportError("mido is required: pip install mido")


# MIDI note number to pitch class mapping
NOTE_TO_PC = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
}


def midi_note_to_pitch_class(note: int) -> int:
    """Convert a MIDI note number to a pitch class (0–11).

    Parameters
    ----------
    note : int
        MIDI note number (0–127).

    Returns
    -------
    int
        Pitch class 0=C, 1=C#, ..., 11=B.
    """
    return note % 12


def midi_to_onsets(path: str | Path) -> list[tuple[float, int, int]]:
    """Extract note onsets from a MIDI file.

    Parameters
    ----------
    path : str or Path
        Path to the MIDI file.

    Returns
    -------
    list of (time_seconds, pitch, velocity) tuples
        Note onset events sorted by time.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"MIDI file not found: {path}")

    mid = MidiFile(str(path))
    onsets: list[tuple[float, int, int]] = []

    for track in mid.tracks:
        abs_time = 0.0
        for msg in track:
            abs_time += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                time_sec = mido.tick2second(abs_time, mid.ticks_per_beat, bpm2tempo(120))
                onsets.append((time_sec, msg.note, msg.velocity))

    onsets.sort(key=lambda x: x[0])
    return onsets


def onsets_to_midi(
    onsets: list[tuple[float, int, int]],
    bpm: int = 120,
    output_path: Optional[str | Path] = None,
    note_duration: float = 0.25,
) -> MidiFile:
    """Convert onset data to a MIDI file.

    Parameters
    ----------
    onsets : list of (time_seconds, pitch, velocity)
        Note events.
    bpm : int
        Tempo in BPM.
    output_path : str, Path, or None
        If provided, save the MIDI file to this path.
    note_duration : float
        Default note duration in seconds.

    Returns
    -------
    MidiFile
        The generated MIDI file object.
    """
    mid = MidiFile(ticks_per_beat=480)
    track = MidiTrack()
    mid.tracks.append(track)

    tempo = bpm2tempo(bpm)
    track.append(MetaMessage("set_tempo", tempo=tempo, time=0))

    # Convert to MIDI events: (time_ticks, type, note, velocity)
    events: list[tuple[int, str, int, int]] = []
    ticks_per_second = mid.ticks_per_beat * bpm / 60.0

    for time_sec, pitch, velocity in onsets:
        start_tick = int(round(time_sec * ticks_per_second))
        end_tick = int(round((time_sec + note_duration) * ticks_per_second))
        events.append((start_tick, "note_on", pitch, velocity))
        events.append((end_tick, "note_off", pitch, 0))

    events.sort(key=lambda x: (x[0], 0 if x[1] == "note_off" else 1))

    prev_tick = 0
    for tick, msg_type, note, vel in events:
        delta = tick - prev_tick
        track.append(Message(msg_type, note=note, velocity=vel, time=delta))
        prev_tick = tick

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        mid.save(str(output_path))

    return mid


def apply_microtiming(
    midi_data: MidiFile,
    offsets_ms: dict[int, float],
) -> MidiFile:
    """Apply microtiming offsets to note onsets in a MIDI file.

    Parameters
    ----------
    midi_data : MidiFile
        Input MIDI file.
    offsets_ms : dict[int, float]
        Mapping from note index (0-based order of appearance) to offset in ms.
        Positive = late, negative = early.

    Returns
    -------
    MidiFile
        Modified MIDI with microtiming applied.
    """
    mid = MidiFile(ticks_per_beat=midi_data.ticks_per_beat)
    ticks_per_second = midi_data.ticks_per_beat * 120 / 60.0

    for track in midi_data.tracks:
        new_track = MidiTrack()
        note_idx = 0
        for msg in track:
            new_msg = msg.copy()
            if msg.type == "note_on" and msg.velocity > 0:
                if note_idx in offsets_ms:
                    offset_ticks = int(round(offsets_ms[note_idx] * ticks_per_second / 1000.0))
                    # Adjust delta time of this message
                    # We need to shift: subtract from next, add to this
                    new_msg = msg.copy(time=msg.time + offset_ticks)
                note_idx += 1
            new_track.append(new_msg)
        mid.tracks.append(new_track)

    return mid


def quantize_midi(
    midi_data: MidiFile,
    grid: int = 16,
    bpm: int = 120,
) -> MidiFile:
    """Quantize note onsets to a rhythmic grid.

    Parameters
    ----------
    midi_data : MidiFile
        Input MIDI file.
    grid : int
        Grid resolution (4=quarter, 8=eighth, 16=sixteenth, etc.).
    bpm : int
        Tempo assumption for tick conversion.

    Returns
    -------
    MidiFile
        Quantized MIDI file.
    """
    mid = MidiFile(ticks_per_beat=midi_data.ticks_per_beat)
    ticks_per_grid = midi_data.ticks_per_beat * 4 // grid

    for track in midi_data.tracks:
        new_track = MidiTrack()
        abs_tick = 0
        events: list[tuple[int, "Message"]] = []

        for msg in track:
            abs_tick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                # Quantize to nearest grid
                quantized = round(abs_tick / ticks_per_grid) * ticks_per_grid
                events.append((quantized, msg.copy(time=0)))
            else:
                events.append((abs_tick, msg.copy(time=0)))

        # Convert back to delta times
        events.sort(key=lambda x: x[0])
        prev_tick = 0
        for tick, msg in events:
            delta = max(0, tick - prev_tick)
            new_track.append(msg.copy(time=delta))
            prev_tick = tick

        mid.tracks.append(new_track)

    return mid


def extract_onset_times(midi_data: MidiFile, bpm: int = 120) -> NDArray[np.float64]:
    """Extract onset times in seconds from a MidiFile object.

    Parameters
    ----------
    midi_data : MidiFile
        The MIDI file.
    bpm : int
        Tempo assumption.

    Returns
    -------
    ndarray of float64
        Onset times in seconds.
    """
    onsets: list[float] = []
    for track in midi_data.tracks:
        abs_time_ticks = 0
        for msg in track:
            abs_time_ticks += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                time_sec = abs_time_ticks / (midi_data.ticks_per_beat * bpm / 60.0)
                onsets.append(time_sec)
    return np.array(sorted(onsets), dtype=np.float64)


def extract_pitch_classes_from_midi(midi_data: MidiFile) -> NDArray[np.intp]:
    """Extract pitch classes from all note_on events.

    Parameters
    ----------
    midi_data : MidiFile
        The MIDI file.

    Returns
    -------
    ndarray of int
        Pitch class for each note (0–11).
    """
    pcs: list[int] = []
    for track in midi_data.tracks:
        for msg in track:
            if msg.type == "note_on" and msg.velocity > 0:
                pcs.append(msg.note % 12)
    return np.array(pcs, dtype=np.intp)
