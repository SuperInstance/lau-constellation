"""Tests for the constraint-based composer."""

import pytest

import mido

from constraint_toolkit.composer import ConstraintComposer
from constraint_toolkit.dials import DialPosition, DIAL_RANGES


class TestConstraintComposer:
    """Tests for ConstraintComposer."""

    def setup_method(self):
        self.comp = ConstraintComposer(seed=42)

    def test_compose_returns_midi(self):
        target = DialPosition(harmonic_tension=2.5, rhythmic_complexity=2.5, spectral_density=2.5)
        result = self.comp.compose(target, bars=4, tempo=120)
        assert isinstance(result, mido.MidiFile)

    def test_compose_correct_bars(self):
        target = DialPosition(harmonic_tension=2.0, rhythmic_complexity=3.0, spectral_density=2.0)
        result = self.comp.compose(target, bars=8, tempo=120)
        # Should have at least one track with notes
        assert len(result.tracks) >= 1
        total_notes = sum(1 for t in result.tracks for m in t if m.type == 'note_on' and m.velocity > 0)
        assert total_notes > 0

    def test_compose_in_tradition_all(self):
        for tradition in DIAL_RANGES:
            result = self.comp.compose_in_tradition(tradition, bars=4)
            assert isinstance(result, mido.MidiFile), f"Failed for {tradition}"
            assert len(result.tracks) >= 1, f"No tracks for {tradition}"

    def test_compose_in_tradition_invalid(self):
        with pytest.raises(ValueError):
            self.comp.compose_in_tradition("NonExistentTradition")

    def test_compose_novel(self):
        # Position far from any tradition
        target = DialPosition(harmonic_tension=0.3, rhythmic_complexity=0.2, spectral_density=4.8)
        result = self.comp.compose_novel(target, bars=4)
        assert isinstance(result, mido.MidiFile)

    def test_velocity_in_range(self):
        target = DialPosition(harmonic_tension=3.0, rhythmic_complexity=3.0, spectral_density=3.0)
        result = self.comp.compose(target, bars=4, tempo=120)
        for track in result.tracks:
            for msg in track:
                if msg.type == "note_on" and msg.velocity > 0:
                    assert 1 <= msg.velocity <= 127

    def test_positive_tempo(self):
        with pytest.raises(ValueError):
            target = DialPosition(harmonic_tension=2.0, rhythmic_complexity=2.0, spectral_density=2.0)
            self.comp.compose(target, bars=4, tempo=0)

    def test_positive_bars(self):
        with pytest.raises(ValueError):
            target = DialPosition(harmonic_tension=2.0, rhythmic_complexity=2.0, spectral_density=2.0)
            self.comp.compose(target, bars=0)

    def test_deterministic_with_seed(self):
        comp1 = ConstraintComposer(seed=99)
        comp2 = ConstraintComposer(seed=99)
        target = DialPosition(harmonic_tension=2.5, rhythmic_complexity=2.5, spectral_density=2.5)
        r1 = comp1.compose(target, bars=4, tempo=120)
        r2 = comp2.compose(target, bars=4, tempo=120)
        # Same seed → same output
        for t1, t2 in zip(r1.tracks, r2.tracks):
            for m1, m2 in zip(t1, t2):
                if m1.type == "note_on" and m2.type == "note_on":
                    assert m1.note == m2.note
                    assert m1.velocity == m2.velocity
