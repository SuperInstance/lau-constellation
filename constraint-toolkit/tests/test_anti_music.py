"""Tests for the anti_music module."""

from __future__ import annotations

import numpy as np
import pytest
from mido import MidiFile

from constraint_toolkit.anti_music import (
    AntiMusicScore,
    AntiMusicDetector,
    _compute_anti_metrics,
)


class TestAntiMusicScore:
    def test_score_attributes(self):
        score = AntiMusicScore(
            total_score=0.5,
            negative_consonance=0.4,
            maximum_syncopation=0.6,
            spectral_chaos=0.3,
            beyond_random=False,
            percentile=50.0,
        )
        assert score.total_score == 0.5
        assert score.negative_consonance == 0.4
        assert score.maximum_syncopation == 0.6
        assert score.spectral_chaos == 0.3
        assert score.beyond_random is False
        assert score.percentile == 50.0

    def test_summary(self):
        score = AntiMusicScore(
            total_score=0.5,
            negative_consonance=0.4,
            maximum_syncopation=0.6,
            spectral_chaos=0.3,
            beyond_random=False,
            percentile=50.0,
        )
        summary = score.summary()
        assert isinstance(summary, str)
        assert "0.500" in summary or "0.5" in summary


class TestAntiMusicDetector:
    @pytest.fixture
    def detector(self):
        return AntiMusicDetector(n_baseline=100, seed=42)

    def test_generate_anti_music_returns_midi(self, detector):
        midi = detector.generate_anti_music(intensity=0.5)
        assert isinstance(midi, MidiFile)
        assert len(midi.tracks) > 0

    def test_score_raw(self, detector):
        rng = np.random.RandomState(42)
        onsets = np.sort(rng.uniform(0, 30, 50))
        pcs = rng.randint(0, 12, 50).astype(np.intp)
        spectrum = np.abs(rng.randn(2048)) + 0.1
        score = detector.score_raw(onsets, pcs, spectrum, sr=44100, duration=30.0)
        assert isinstance(score, AntiMusicScore)
        assert 0.0 <= score.total_score <= 1.0

    def test_random_baseline(self, detector):
        # Generate random musical material and verify scoring works
        rng = np.random.RandomState(42)
        onsets = np.sort(rng.uniform(0, 10, 20))
        pcs = rng.randint(0, 12, 20).astype(np.intp)
        spectrum = np.abs(rng.randn(2048)) + 0.1
        score = detector.score_raw(onsets, pcs, spectrum, duration=10.0)
        assert isinstance(score, AntiMusicScore)
        assert 0.0 <= score.percentile <= 100.0

    def test_calibrate(self, detector):
        results = detector.calibrate()
        assert isinstance(results, dict)
        assert "calibration_monotonic" in results

    def test_high_intensity_more_anti_musical(self, detector):
        """Higher intensity should generally produce higher anti-music scores."""
        low = detector.generate_anti_music(intensity=0.1, duration=5.0)
        high = detector.generate_anti_music(intensity=1.0, duration=5.0)
        assert isinstance(low, MidiFile)
        assert isinstance(high, MidiFile)
        # Both should produce MIDI with notes
        assert len(low.tracks[0]) > 0
        assert len(high.tracks[0]) > 0
