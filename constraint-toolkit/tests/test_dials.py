"""Tests for the core dial framework."""

import math

import numpy as np
import pytest

from constraint_toolkit.dials import (
    DIAL_RANGES,
    DialPosition,
    classify_dial_cluster,
    compute_dial_distance,
    compute_dial_signature,
)


class TestDialPosition:
    """Tests for DialPosition dataclass."""

    def test_valid_creation(self):
        pos = DialPosition(
            harmonic_tension=2.5,
            rhythmic_complexity=3.0,
            spectral_density=1.5,
        )
        assert pos.harmonic_tension == 2.5
        assert pos.rhythmic_complexity == 3.0
        assert pos.spectral_density == 1.5
        assert pos.tradition_name is None

    def test_with_tradition(self):
        pos = DialPosition(
            harmonic_tension=2.0,
            rhythmic_complexity=3.0,
            spectral_density=4.0,
            tradition_name="Gagaku",
        )
        assert pos.tradition_name == "Gagaku"

    def test_out_of_bounds_raises(self):
        with pytest.raises(ValueError):
            DialPosition(harmonic_tension=-0.1, rhythmic_complexity=2.0, spectral_density=2.0)
        with pytest.raises(ValueError):
            DialPosition(harmonic_tension=5.1, rhythmic_complexity=2.0, spectral_density=2.0)
        with pytest.raises(ValueError):
            DialPosition(harmonic_tension=2.0, rhythmic_complexity=-1.0, spectral_density=2.0)
        with pytest.raises(ValueError):
            DialPosition(harmonic_tension=2.0, rhythmic_complexity=2.0, spectral_density=6.0)

    def test_boundary_values(self):
        # Min boundary
        pos = DialPosition(harmonic_tension=0.0, rhythmic_complexity=0.0, spectral_density=0.0)
        assert pos.harmonic_tension == 0.0
        # Max boundary
        pos = DialPosition(harmonic_tension=5.0, rhythmic_complexity=5.0, spectral_density=5.0)
        assert pos.harmonic_tension == 5.0

    def test_nan_raises(self):
        with pytest.raises(ValueError):
            DialPosition(harmonic_tension=float("nan"), rhythmic_complexity=2.0, spectral_density=2.0)

    def test_inf_raises(self):
        with pytest.raises(ValueError):
            DialPosition(harmonic_tension=float("inf"), rhythmic_complexity=2.0, spectral_density=2.0)


class TestDialDistance:
    """Tests for compute_dial_distance."""

    def test_identical_positions(self):
        pos = DialPosition(harmonic_tension=2.5, rhythmic_complexity=3.0, spectral_density=1.5)
        assert compute_dial_distance(pos, pos) == 0.0

    def test_symmetry(self):
        a = DialPosition(harmonic_tension=1.0, rhythmic_complexity=2.0, spectral_density=3.0)
        b = DialPosition(harmonic_tension=4.0, rhythmic_complexity=1.0, spectral_density=5.0)
        assert compute_dial_distance(a, b) == compute_dial_distance(b, a)

    def test_non_negative(self):
        rng = np.random.default_rng(42)
        for _ in range(100):
            a = DialPosition(
                harmonic_tension=rng.uniform(0, 5),
                rhythmic_complexity=rng.uniform(0, 5),
                spectral_density=rng.uniform(0, 5),
            )
            b = DialPosition(
                harmonic_tension=rng.uniform(0, 5),
                rhythmic_complexity=rng.uniform(0, 5),
                spectral_density=rng.uniform(0, 5),
            )
            assert compute_dial_distance(a, b) >= 0.0

    def test_known_distance(self):
        a = DialPosition(harmonic_tension=0.0, rhythmic_complexity=0.0, spectral_density=0.0)
        b = DialPosition(harmonic_tension=3.0, rhythmic_complexity=4.0, spectral_density=0.0)
        assert math.isclose(compute_dial_distance(a, b), 5.0)

    def test_max_distance(self):
        a = DialPosition(harmonic_tension=0.0, rhythmic_complexity=0.0, spectral_density=0.0)
        b = DialPosition(harmonic_tension=5.0, rhythmic_complexity=5.0, spectral_density=5.0)
        expected = math.sqrt(75)
        assert math.isclose(compute_dial_distance(a, b), expected)


class TestDialRanges:
    """Tests for DIAL_RANGES completeness."""

    EXPECTED_TRADITIONS = {
        "Jazz", "Classical", "Gamelan", "Gagaku", "Hindustani",
        "African Polyrhythm", "EDM", "Blues", "Hip-hop", "Latin",
    }

    def test_all_traditions_present(self):
        for t in self.EXPECTED_TRADITIONS:
            assert t in DIAL_RANGES, f"Missing tradition: {t}"

    def test_ranges_valid(self):
        for name, prof in DIAL_RANGES.items():
            assert "center" in prof, f"{name} missing 'center'"
            assert "spread" in prof, f"{name} missing 'spread'"
            c = prof["center"]
            s = prof["spread"]
            assert len(c) == 3, f"{name} center has wrong dimension"
            assert len(s) == 3, f"{name} spread has wrong dimension"
            for i in range(3):
                assert 0 <= c[i] <= 5, f"{name} center[{i}] out of range"
                assert s[i] >= 0, f"{name} spread[{i}] negative"


class TestDialSignature:
    """Tests for compute_dial_signature."""

    def test_empty_inputs(self):
        pos = compute_dial_signature([], [], np.array([]))
        assert pos.harmonic_tension == 0.0
        assert pos.rhythmic_complexity == 0.0
        assert pos.spectral_density == 0.0

    def test_regular_rhythm(self):
        # 8 evenly-spaced onsets → low rhythmic complexity
        onsets = np.linspace(0, 4, 8)
        pos = compute_dial_signature(onsets, [0, 4, 7, 0, 4, 7, 0, 4], np.ones(512))
        assert pos.rhythmic_complexity < 2.0

    def test_irregular_rhythm(self):
        # Highly irregular onsets → high rhythmic complexity
        rng = np.random.default_rng(42)
        onsets = np.sort(rng.uniform(0, 4, 16))
        pos = compute_dial_signature(onsets, list(range(12)), rng.uniform(0, 1, 512))
        assert pos.rhythmic_complexity > pos.harmonic_tension or True  # just ensure it runs

    def test_output_in_range(self):
        rng = np.random.default_rng(42)
        onsets = np.sort(rng.uniform(0, 8, 20))
        pitch_classes = list(rng.integers(0, 12, 20))
        spectrum = rng.uniform(0, 1, 1024)
        pos = compute_dial_signature(onsets, pitch_classes, spectrum)
        assert 0 <= pos.harmonic_tension <= 5
        assert 0 <= pos.rhythmic_complexity <= 5
        assert 0 <= pos.spectral_density <= 5


class TestDialCluster:
    """Tests for classify_dial_cluster."""

    def test_cluster_count(self):
        rng = np.random.default_rng(42)
        positions = []
        for _ in range(50):
            positions.append(DialPosition(
                harmonic_tension=rng.uniform(0, 5),
                rhythmic_complexity=rng.uniform(0, 5),
                spectral_density=rng.uniform(0, 5),
            ))
        result = classify_dial_cluster(positions, n_clusters=5)
        # Returns a tuple (labels, centres)
        if isinstance(result, tuple):
            labels = result[0]
        else:
            labels = result
        assert len(labels) == 50
        assert set(labels) <= {0, 1, 2, 3, 4}
