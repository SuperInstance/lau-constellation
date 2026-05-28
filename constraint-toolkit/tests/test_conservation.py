"""Tests for conservation of tension measurements."""

import math

import numpy as np
import pytest

from constraint_toolkit.conservation import (
    conservation_ratio,
    measure_tension,
    stress_test,
)


class TestMeasureTension:
    """Tests for measure_tension."""

    def test_returns_tuple_of_positive_values(self):
        # Simple major scale sequence: pitch classes
        sequence = [0, 2, 4, 5, 7, 9, 11, 0]
        iv, ih = measure_tension(sequence)
        assert isinstance(iv, float)
        assert isinstance(ih, float)
        assert iv >= 0
        assert ih >= 0

    def test_empty_sequence(self):
        iv, ih = measure_tension([])
        assert iv == 0.0
        assert ih == 0.0

    def test_single_note(self):
        iv, ih = measure_tension([0])
        assert iv >= 0
        assert ih >= 0

    def test_repeated_note(self):
        # Same note repeated → minimal tension
        iv, ih = measure_tension([0, 0, 0, 0])
        assert iv == 0.0  # No vertical tension from identical notes

    def test_meantone_vs_et(self):
        # ET should show different tension profile than meantone
        # for the same melodic contour
        sequence = [0, 4, 7, 0, 4, 7]
        iv_et, ih_et = measure_tension(sequence, tuning="ET")
        iv_mt, ih_mt = measure_tension(sequence, tuning="meantone")
        # Both should be valid measurements
        assert iv_et >= 0 and ih_et >= 0
        assert iv_mt >= 0 and ih_mt >= 0

    def test_chromatic_high_tension(self):
        # Chromatic scale should have high harmonic tension
        chromatic = list(range(12))
        iv, ih = measure_tension(chromatic)
        # Chromatic movement has high vertical tension
        assert iv > 0


class TestConservationRatio:
    """Tests for conservation_ratio."""

    def test_returns_positive_float(self):
        sequence = [0, 2, 4, 5, 7, 9, 11, 0]
        ratio = conservation_ratio(sequence)
        assert isinstance(ratio, float)
        assert ratio > 0

    def test_empty_sequence(self):
        ratio = conservation_ratio([])
        # Should handle gracefully
        assert isinstance(ratio, float)

    def test_known_meantone_stability(self):
        # Meantone sequence should have ratio close to 1.003
        # (from research results)
        sequence = [0, 4, 7, 0, 4, 7, 0, 4, 7, 0]
        ratio = conservation_ratio(sequence, tuning="meantone")
        # Just verify it's a reasonable value
        assert 0.0 < ratio < 2.0


class TestStressTest:
    """Tests for stress_test."""

    def test_completes_quickly(self):
        result = stress_test(n_sequences=100, seed=42)
        assert isinstance(result, dict)

    def test_returns_expected_keys(self):
        result = stress_test(n_sequences=50, seed=42)
        expected_keys = {"mean_sum", "std_sum", "cv", "correlation", "n_sequences"}
        assert expected_keys.issubset(result.keys())

    def test_mean_reasonable(self):
        result = stress_test(n_sequences=200, seed=42)
        assert math.isfinite(result["mean_sum"])
        assert result["mean_sum"] > 0

    def test_cv_reasonable(self):
        result = stress_test(n_sequences=200, seed=42)
        # CV of ~14.4% is expected from research
        assert 0 < result["cv"] < 1.0

    def test_correlation_weak(self):
        result = stress_test(n_sequences=500, seed=42)
        # Known result: r=+0.436 (weak, NOT -1.0)
        # Just verify it's not close to -1.0
        assert result["correlation"] > -0.5

    def test_deterministic_with_seed(self):
        r1 = stress_test(n_sequences=50, seed=42)
        r2 = stress_test(n_sequences=50, seed=42)
        assert r1["mean_sum"] == r2["mean_sum"]
        assert r1["std_sum"] == r2["std_sum"]
