"""Tests for the music recommender."""

from __future__ import annotations

import numpy as np
import pytest

from constraint_toolkit.dials import DIAL_RANGES, DialPosition
from constraint_toolkit.recommender import MusicRecommender, Recommendation


class TestMusicRecommender:
    """Test the MusicRecommender class."""

    def test_recommend_returns_list(self) -> None:
        """Recommend from a dial position returns a list of Recommendations."""
        recommender = MusicRecommender(seed=42)
        query_pos = DialPosition.from_array(
            DIAL_RANGES["Jazz"]["center"], tradition_name="Jazz"
        )
        recs = recommender._recommend_from_position(query_pos, n=5)
        assert isinstance(recs, list)
        assert len(recs) == 5
        assert all(isinstance(r, Recommendation) for r in recs)

    def test_recommend_novel_returns_unexplored_positions(self) -> None:
        """Novel recommendations are far from known traditions."""
        recommender = MusicRecommender(seed=42)
        novel = recommender.recommend_novel(n=5)
        assert isinstance(novel, list)
        assert len(novel) == 5
        assert all(isinstance(p, DialPosition) for p in novel)

        # Novel positions should have non-trivial distance to traditions
        for pos in novel:
            min_dist = pos.metadata.get("min_distance_to_tradition", 0)
            assert min_dist > 0.5  # Should be meaningfully far

    def test_explain_returns_string(self) -> None:
        """Explain produces a human-readable string."""
        recommender = MusicRecommender(seed=42)
        query_pos = DialPosition(3.0, 3.0, 3.0)
        recs = recommender._recommend_from_position(query_pos, n=1)
        rec = recs[0]
        assert isinstance(rec.explanation, str)
        assert len(rec.explanation) > 0

    def test_recommend_between_returns_positions(self) -> None:
        """Between-tradition recommendations return valid positions."""
        recommender = MusicRecommender(seed=42)
        positions = recommender.recommend_between("Jazz", "Gamelan", n=3)
        assert len(positions) == 3
        for pos in positions:
            assert 0 <= pos.harmonic_tension <= 5
            assert 0 <= pos.rhythmic_complexity <= 5
            assert 0 <= pos.spectral_density <= 5

    def test_recommend_between_unknown_tradition_raises(self) -> None:
        """Unknown tradition raises ValueError."""
        recommender = MusicRecommender(seed=42)
        with pytest.raises(ValueError):
            recommender.recommend_between("Jazz", "Nonexistent")

    def test_taste_map_returns_string(self) -> None:
        """Taste map produces output even with no files."""
        recommender = MusicRecommender(seed=42)
        result = recommender.taste_map([])
        assert isinstance(result, str)
        assert "Taste Map" in result or "No valid files" in result

    def test_recommendations_are_ranked(self) -> None:
        """Recommendations are sorted by composite score (best first)."""
        recommender = MusicRecommender(seed=42)
        query_pos = DialPosition(3.0, 3.0, 3.0)
        recs = recommender._recommend_from_position(query_pos, n=10)
        # First should be closest
        assert recs[0].distance <= recs[-1].distance
