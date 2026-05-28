"""Tests for synthesizer module."""

import tempfile
from pathlib import Path

import numpy as np
import pytest
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

from constraint_toolkit.synthesizer import ConstraintSynth
from constraint_toolkit.dials import DialPosition


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def synth():
    return ConstraintSynth(sr=22050)


@pytest.fixture
def simple_midi():
    """A one-note MIDI file."""
    mid = MidiFile(ticks_per_beat=480)
    track = MidiTrack()
    track.append(MetaMessage("set_tempo", tempo=bpm2tempo(120), time=0))
    track.append(Message("note_on", note=60, velocity=80, time=0))
    track.append(Message("note_off", note=60, velocity=0, time=480))
    mid.tracks.append(track)
    return mid


@pytest.fixture
def multi_note_midi():
    """A multi-note MIDI file."""
    mid = MidiFile(ticks_per_beat=480)
    track = MidiTrack()
    track.append(MetaMessage("set_tempo", tempo=bpm2tempo(120), time=0))
    for note in [60, 64, 67, 72]:
        track.append(Message("note_on", note=note, velocity=80, time=0))
        track.append(Message("note_off", note=note, velocity=0, time=240))
    mid.tracks.append(track)
    return mid


# ── Tests ─────────────────────────────────────────────────────────────

def test_synthesize_note_produces_audio(synth):
    duration = 0.5
    audio = synth.synthesize_note(440.0, duration, velocity=80)
    expected_len = int(np.ceil(duration * synth.sr))
    assert len(audio) == expected_len


def test_no_clipping(synth):
    audio = synth.synthesize_note(440.0, 1.0, velocity=127,
                                  spectral_density=5.0, harmonic_tension=5.0)
    assert np.max(np.abs(audio)) <= 1.0


def test_spectral_density_controls_harmonics(synth):
    # Higher spectral density should produce different harmonic content
    audio_low = synth.synthesize_note(440.0, 0.5, velocity=80, spectral_density=0.5)
    audio_high = synth.synthesize_note(440.0, 0.5, velocity=80, spectral_density=4.5)

    # The two should be noticeably different
    assert not np.allclose(audio_low, audio_high, atol=0.01)


def test_harmonic_tension_controls_content(synth):
    # Different harmonic tension should produce different spectral content
    audio_low = synth.synthesize_note(440.0, 0.5, velocity=80, harmonic_tension=0.5)
    audio_high = synth.synthesize_note(440.0, 0.5, velocity=80, harmonic_tension=4.5)

    # They should be different (not identical)
    assert not np.allclose(audio_low, audio_high)


def test_render_midi_produces_audio(synth, simple_midi):
    audio = synth.render_midi(simple_midi, bpm=120)
    assert len(audio) > 1
    assert np.max(np.abs(audio)) <= 1.0


def test_render_midi_with_dial_target(synth, multi_note_midi):
    dial = DialPosition(harmonic_tension=3.0, rhythmic_complexity=3.0, spectral_density=3.0)
    audio = synth.render_midi(multi_note_midi, dial_target=dial, bpm=120)
    assert len(audio) > 1


def test_save_wav_creates_file(synth):
    audio = synth.synthesize_note(440.0, 0.5, velocity=80)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.wav"
        synth.save_wav(audio, path)
        assert path.exists()
        assert path.stat().st_size > 0


def test_zero_freq_returns_silence(synth):
    audio = synth.synthesize_note(0.0, 0.5, velocity=80)
    assert np.allclose(audio, 0.0)


def test_zero_duration_returns_silence(synth):
    audio = synth.synthesize_note(440.0, 0.0, velocity=80)
    assert len(audio) >= 1
