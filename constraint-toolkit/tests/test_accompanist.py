"""Tests for accompanist module."""

import numpy as np
import pytest
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

from constraint_toolkit.accompanist import AutoAccompanist
from constraint_toolkit.dials import DIAL_RANGES


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def accompanist():
    return AutoAccompanist(sr=22050)


@pytest.fixture
def melody_midi():
    """A simple melody MIDI file."""
    mid = MidiFile(ticks_per_beat=480)
    track = MidiTrack()
    track.append(MetaMessage("set_tempo", tempo=bpm2tempo(120), time=0))
    for note in [60, 64, 67, 72, 71, 67, 64, 60]:
        track.append(Message("note_on", note=note, velocity=80, time=0))
        track.append(Message("note_off", note=note, velocity=0, time=480))
    mid.tracks.append(track)
    return mid


# ── Tests ─────────────────────────────────────────────────────────────

def test_accompany_returns_midi(accompanist, melody_midi):
    result = accompanist.accompany(melody_midi, tradition="Jazz", bpm=120)
    assert isinstance(result, MidiFile)


def test_accompany_has_multiple_tracks(accompanist, melody_midi):
    result = accompanist.accompany(melody_midi, tradition="Jazz", bpm=120)
    # Should have: tempo, melody, bass, chords, drums = 5 tracks
    assert len(result.tracks) >= 4


def test_accompany_with_all_traditions(accompanist, melody_midi):
    """Accompaniment should work for all traditions."""
    for tradition in DIAL_RANGES:
        result = accompanist.accompany(melody_midi, tradition=tradition, bpm=120)
        assert isinstance(result, MidiFile)
        assert len(result.tracks) >= 3


def test_suggest_chords_returns_list(accompanist):
    pitches = [60, 64, 67, 72, 71, 67]
    chords = accompanist.suggest_chords(pitches, tradition="Jazz")
    assert isinstance(chords, list)
    assert len(chords) > 0
    for chord in chords:
        assert isinstance(chord, list)
        for note in chord:
            assert isinstance(note, int)


def test_suggest_chords_empty_input(accompanist):
    chords = accompanist.suggest_chords([])
    assert isinstance(chords, list)
    assert len(chords) >= 1


def test_suggest_chords_with_numpy_array(accompanist):
    pitches = np.array([60, 64, 67, 72])
    chords = accompanist.suggest_chords(pitches, tradition="Blues")
    assert isinstance(chords, list)
    assert len(chords) > 0


def test_accompany_invalid_tradition_raises(accompanist, melody_midi):
    with pytest.raises(ValueError, match="Unknown tradition"):
        accompanist.accompany(melody_midi, tradition="NonExistentGenre")


def test_accompany_with_explicit_bars(accompanist, melody_midi):
    result = accompanist.accompany(melody_midi, tradition="Classical", bars=4, bpm=100)
    assert isinstance(result, MidiFile)
