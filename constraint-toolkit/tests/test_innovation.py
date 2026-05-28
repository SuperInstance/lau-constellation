"""Tests for the innovation module."""

from __future__ import annotations

import pytest

from constraint_toolkit.innovation import (
    InnovationTracker,
    CyclePhase,
    PhaseScore,
    HISTORICAL_PHASES,
)
from constraint_toolkit.dials import DIAL_RANGES


@pytest.fixture
def tracker():
    return InnovationTracker()


class TestAnalyzeTradition:
    def test_returns_phase_score(self, tracker):
        result = tracker.analyze_tradition("Jazz")
        assert isinstance(result, PhaseScore)
        assert isinstance(result.dominant_phase, CyclePhase)

    def test_valid_phase_string(self, tracker):
        valid_phases = {"Discovery", "Codification", "Ubiquity", "Boredom", "Rebellion"}
        for tradition in ["Jazz", "EDM", "Blues", "Gamelan"]:
            result = tracker.analyze_tradition(tradition)
            assert result.dominant_phase.value in valid_phases

    def test_invalid_tradition_raises(self, tracker):
        with pytest.raises(ValueError, match="Unknown tradition"):
            tracker.analyze_tradition("NonExistentGenre")


class TestMapAllTraditions:
    def test_returns_all_traditions(self, tracker):
        result = tracker.map_all_traditions()
        assert isinstance(result, dict)
        assert len(result) == len(DIAL_RANGES)
        for name in DIAL_RANGES:
            assert name in result


class TestPredictNextPhase:
    def test_returns_dict(self, tracker):
        result = tracker.predict_next_phase("Jazz")
        assert isinstance(result, dict)
        assert "next_phase" in result
        assert "current_phase" in result

    def test_all_traditions_have_prediction(self, tracker):
        for name in DIAL_RANGES:
            result = tracker.predict_next_phase(name)
            assert "next_phase" in result
            assert isinstance(result["next_phase"], str)


class TestFormatCycleChart:
    def test_chart_is_string(self, tracker):
        chart = tracker.format_cycle_chart()
        assert isinstance(chart, str)
        assert "INNOVATION CYCLE" in chart


class TestFindRebellionCandidates:
    def test_returns_list(self, tracker):
        candidates = tracker.find_rebellion_candidates()
        assert isinstance(candidates, list)
        for c in candidates:
            assert "tradition" in c
            assert "readiness" in c
