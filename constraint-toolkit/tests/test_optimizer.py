"""Tests for the groove optimizer."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

import mido

from constraint_toolkit.optimizer import GrooveOptimizer
from constraint_toolkit.dials import DialPosition, DIAL_RANGES


def _make_quantized_midi(bpm=120, bars=4):
    """Create a perfectly quantized drum MIDI pattern."""
    mid = mido.MidiFile(ticks_per_beat=480)
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage("set_tempo", tempo=int(60_000_000 / bpm), time=0))
    meta.append(mido.MetaMessage("end_of_track", time=0))
    mid.tracks.append(meta)

    # Kick on beats 1, 3
    kick = mido.MidiTrack()
    kick.append(mido.MetaMessage("track_name", name="Kick", time=0))
    prev = 0
    for bar in range(bars):
        for beat in [0, 2]:
            tick = (bar * 4 + beat) * 480
            delta = tick - prev
            kick.append(mido.Message("note_on", note=36, velocity=100, time=delta, channel=9))
            kick.append(mido.Message("note_off", note=36, velocity=0, time=60, channel=9))
            prev = tick + 60
    kick.append(mido.MetaMessage("end_of_track", time=0))
    mid.tracks.append(kick)

    # HiHat on every 8th
    hh = mido.MidiTrack()
    hh.append(mido.MetaMessage("track_name", name="HiHat", time=0))
    prev = 0
    for bar in range(bars):
        for eighth in range(8):
            tick = int((bar * 4 + eighth * 0.5) * 480)
            delta = tick - prev
            hh.append(mido.Message("note_on", note=42, velocity=80, time=max(0, delta), channel=9))
            hh.append(mido.Message("note_off", note=42, velocity=0, time=30, channel=9))
            prev = tick + 30
    hh.append(mido.MetaMessage("end_of_track", time=0))
    mid.tracks.append(hh)

    return mid


class TestGrooveOptimizer:
    """Tests for GrooveOptimizer."""

    def setup_method(self):
        self.opt = GrooveOptimizer(seed=42)

    def test_optimize_returns_result(self):
        midi = _make_quantized_midi()
        result = self.opt.optimize(midi, target_genre="Jazz", iterations=10)
        assert hasattr(result, "original_position")
        assert hasattr(result, "optimized_position")
        assert hasattr(result, "fitness_history")
        assert isinstance(result.original_position, DialPosition)
        assert isinstance(result.optimized_position, DialPosition)

    def test_optimize_for_pocket(self):
        midi = _make_quantized_midi()
        result = self.opt.optimize_for_pocket(midi, epsilon_ms=15.0, bpm=120)
        assert hasattr(result, "optimized_position")

    def test_hybridize(self):
        result = self.opt.hybridize("Jazz", "EDM", blend=0.5)
        assert isinstance(result, DialPosition)
        # Should be between Jazz and EDM positions
        assert 0 <= result.harmonic_tension <= 5
        assert 0 <= result.rhythmic_complexity <= 5
        assert 0 <= result.spectral_density <= 5

    def test_optimize_convergence(self):
        midi = _make_quantized_midi()
        result = self.opt.optimize(midi, target_genre="Jazz", iterations=50)
        # Fitness should improve over iterations
        if len(result.fitness_history) > 1:
            assert result.fitness_history[-1] >= result.fitness_history[0]

    def test_invalid_genre_raises(self):
        midi = _make_quantized_midi()
        with pytest.raises(ValueError):
            self.opt.optimize(midi, target_genre="NonExistent")
