"""Tests for the musical timeline."""

import pytest

from constraint_toolkit.timeline import MusicalTimeline, _TIMELINE_DATA


class TestMusicalTimeline:
    """Tests for MusicalTimeline."""

    def test_plot_history_returns_string(self):
        timeline = MusicalTimeline(width=60)
        result = timeline.plot_history()
        assert isinstance(result, str)
        assert "=" in result

    def test_plot_history_highlight(self):
        timeline = MusicalTimeline(width=60)
        result = timeline.plot_history(highlight_year=1965)
        assert ">>>" in result or "1965" in result

    def test_what_was_happening_known_year(self):
        timeline = MusicalTimeline(width=60)
        result = timeline.what_was_happening(1600)
        assert "Baroque" in result
        assert "1600" in result

    def test_what_was_happening_nearby_year(self):
        timeline = MusicalTimeline(width=60)
        result = timeline.what_was_happening(1601)
        assert "Baroque" in result

    def test_what_was_happening_before_timeline(self):
        timeline = MusicalTimeline(width=60)
        result = timeline.what_was_happening(1300)
        assert "Ars Subtilior" in result or "1400" in result

    def test_predict_2030_returns_string(self):
        timeline = MusicalTimeline(width=60)
        result = timeline.predict_2030()
        assert isinstance(result, str)
        assert "2030" in result

    def test_predict_2030_structure(self):
        timeline = MusicalTimeline(width=60)
        result = timeline.predict_2030()
        assert "Forecast" in result or "forecast" in result
        assert "dial position" in result.lower()

    def test_data_not_empty(self):
        assert len(_TIMELINE_DATA) > 0
        for entry in _TIMELINE_DATA:
            assert "year" in entry
            assert "era" in entry
            assert "dial" in entry
            assert "blurb" in entry
            assert len(entry["dial"]) == 3

    def test_years_in_order(self):
        years = [e["year"] for e in _TIMELINE_DATA]
        assert years == sorted(years)

    def test_dial_values_in_range(self):
        for entry in _TIMELINE_DATA:
            h, r, s = entry["dial"]
            assert 0.0 <= h <= 5.0
            assert 0.0 <= r <= 5.0
            assert 0.0 <= s <= 5.0
