"""Tests for the Dial Oracle."""

import pytest

from constraint_toolkit.oracle import DialOracle
from constraint_toolkit.dials import DialPosition, DIAL_RANGES


class TestDialOracle:
    """Tests for DialOracle snark engine."""

    def test_what_tradition_am_i_known(self):
        oracle = DialOracle(seed=1)
        for name, profile in DIAL_RANGES.items():
            pos = DialPosition.from_array(profile["center"])
            result = oracle.what_tradition_am_i(pos)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_what_tradition_am_i_rebel(self):
        oracle = DialOracle(seed=2)
        # Far from everything
        rebel = DialPosition(harmonic_tension=0.1, rhythmic_complexity=0.1, spectral_density=0.1)
        result = oracle.what_tradition_am_i(rebel)
        assert isinstance(result, str)
        assert "closest" in result.lower() or "tradition" in result.lower() or "own" in result.lower()

    def test_will_these_blend_returns_string(self):
        oracle = DialOracle(seed=3)
        a = DialPosition.from_array(DIAL_RANGES["Jazz"]["center"])
        b = DialPosition.from_array(DIAL_RANGES["Blues"]["center"])
        result = oracle.will_these_blend(a, b)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_will_these_blend_close_vs_far(self):
        oracle = DialOracle(seed=4)
        close_a = DialPosition.from_array(DIAL_RANGES["Jazz"]["center"])
        close_b = DialPosition.from_array(DIAL_RANGES["Blues"]["center"])
        far_a = DialPosition.from_array(DIAL_RANGES["Classical"]["center"])
        far_b = DialPosition.from_array(DIAL_RANGES["EDM"]["center"])

        close_result = oracle.will_these_blend(close_a, close_b)
        far_result = oracle.will_these_blend(far_a, far_b)
        assert isinstance(close_result, str)
        assert isinstance(far_result, str)

    def test_rate_my_groove_structure(self):
        oracle = DialOracle(seed=5)
        pos = DialPosition(harmonic_tension=2.5, rhythmic_complexity=3.0, spectral_density=2.5)
        result = oracle.rate_my_groove(pos)
        assert isinstance(result, str)
        assert "Overall:" in result

    def test_rate_my_groove_varied_positions(self):
        oracle = DialOracle(seed=6)
        positions = [
            DialPosition(1.0, 1.0, 1.0),
            DialPosition(4.5, 4.5, 4.5),
            DialPosition(2.5, 2.5, 2.5),
        ]
        for pos in positions:
            result = oracle.rate_my_groove(pos)
            assert "Overall:" in result

    def test_reproducibility(self):
        oracle1 = DialOracle(seed=42)
        oracle2 = DialOracle(seed=42)
        pos = DialPosition.from_array(DIAL_RANGES["Jazz"]["center"])
        # Same seed should draw same template
        assert oracle1.what_tradition_am_i(pos) == oracle2.what_tradition_am_i(pos)

    def test_all_traditions_covered(self):
        oracle = DialOracle(seed=7)
        for name in DIAL_RANGES:
            pos = DialPosition.from_array(DIAL_RANGES[name]["center"])
            result = oracle.what_tradition_am_i(pos)
            assert len(result) > 0
