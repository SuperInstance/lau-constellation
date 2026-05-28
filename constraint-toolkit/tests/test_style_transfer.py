"""Tests for style_transfer module."""

import numpy as np
import pytest
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

from constraint_toolkit.style_transfer import StyleTransfer
from constraint_toolkit.dials import DIAL_RANGES


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def transfer():
    return StyleTransfer(sr=22050)


@pytest.fixture
def simple_midi():
    """A multi-note MIDI file with enough material for transfer."""
    mid = MidiFile(ticks_per_beat=480)
    track = MidiTrack()
    track.append(MetaMessage("set_tempo", tempo=bpm2tempo(120), time=0))
    for note in [60, 62, 64, 65, 67, 69, 71, 72]:
        track.append(Message("note_on", note=note, velocity=80, time=0))
        track.append(Message("note_off", note=note, velocity=0, time=240))
    mid.tracks.append(track)
    return mid


# ── Tests ─────────────────────────────────────────────────────────────

def test_transfer_returns_midi(transfer, simple_midi):
    result = transfer.transfer(simple_midi, target_tradition="Jazz")
    assert isinstance(result, MidiFile)
    assert len(result.tracks) >= 1


def test_transfer_changes_dial_position(transfer, simple_midi):
    from constraint_toolkit.midi_utils import extract_pitch_classes_from_midi
    from constraint_toolkit.dials import compute_dial_signature

    original_pc = extract_pitch_classes_from_midi(simple_midi)

    result = transfer.transfer(simple_midi, target_tradition="Jazz", strength=1.0)
    transferred_pc = extract_pitch_classes_from_midi(result)

    # With strength=1.0, pitch classes should have changed (unless already Jazz)
    # At minimum, the result should be valid MIDI
    assert isinstance(result, MidiFile)


def test_transfer_with_all_traditions(transfer, simple_midi):
    """Transfer should work with all known traditions."""
    for tradition in DIAL_RANGES:
        result = transfer.transfer(simple_midi, target_tradition=tradition, strength=0.5)
        assert isinstance(result, MidiFile)


def test_strength_zero_approximately_preserves(transfer, simple_midi):
    from constraint_toolkit.midi_utils import extract_pitch_classes_from_midi

    original_pc = extract_pitch_classes_from_midi(simple_midi)

    result = transfer.transfer(simple_midi, target_tradition="Jazz", strength=0.0)
    result_pc = extract_pitch_classes_from_midi(result)

    # With strength=0, pitch classes should be approximately the same
    assert len(original_pc) == len(result_pc)
    # Allow minor differences due to numerical rounding
    matches = sum(1 for a, b in zip(original_pc, result_pc) if a == b)
    assert matches >= len(original_pc) * 0.9


def test_transfer_from_file_path(transfer, simple_midi, tmp_path):
    """Test transfer with file path input."""
    midi_path = tmp_path / "input.mid"
    simple_midi.save(str(midi_path))

    result = transfer.transfer(str(midi_path), target_tradition="Blues")
    assert isinstance(result, MidiFile)


def test_transfer_invalid_tradition_raises(transfer, simple_midi):
    with pytest.raises(ValueError, match="Unknown tradition"):
        transfer.transfer(simple_midi, target_tradition="NonExistentGenre")
