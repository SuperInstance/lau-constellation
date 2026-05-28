"""Tests for the musical games module."""

import pytest

from constraint_toolkit.games import DialGuesser, TraditionBattles, DialExplorer
from constraint_toolkit.dials import DialPosition, DIAL_RANGES


class TestDialGuesser:
    """Tests for DialGuesser."""

    def test_new_game_returns_hint(self):
        guesser = DialGuesser(seed=1)
        result = guesser.new_game()
        assert "Hint" in result
        assert "Guess" in result

    def test_guess_correct(self):
        guesser = DialGuesser(seed=2)
        guesser.new_game()
        target = guesser._target
        result = guesser.guess(target)
        assert "CORRECT" in result
        assert guesser._target is None

    def test_guess_wrong_gives_hint(self):
        guesser = DialGuesser(seed=3)
        guesser.new_game()
        result = guesser.guess("DefinitelyNotARealTradition")
        assert "Nope" in result or "Wrong" in result or "answer" in result.lower()

    def test_max_hints(self):
        guesser = DialGuesser(seed=4)
        guesser.new_game()
        for _ in range(6):
            result = guesser.guess("Wrong")
        assert "out of hints" in result or "answer was" in result.lower() or "new_game" in result.lower()

    def test_guess_without_game(self):
        guesser = DialGuesser(seed=5)
        result = guesser.guess("Jazz")
        assert "new_game" in result


class TestTraditionBattles:
    """Tests for TraditionBattles."""

    def test_fight_returns_string(self):
        arena = TraditionBattles()
        result = arena.fight("Jazz", "Classical")
        assert isinstance(result, str)
        assert "CHAMPION" in result or "DRAW" in result

    def test_fight_invalid_tradition_raises(self):
        arena = TraditionBattles()
        with pytest.raises(ValueError):
            arena.fight("Jazz", "NotATradition")

    def test_fight_self_draw(self):
        arena = TraditionBattles()
        result = arena.fight("Blues", "Blues")
        assert "DRAW" in result

    def test_matchup_chart_returns_string(self):
        arena = TraditionBattles()
        result = arena.matchup_chart()
        assert isinstance(result, str)
        assert "Matchup Chart" in result
        for name in DIAL_RANGES:
            assert name[:3] in result or name in result

    def test_matchup_chart_covers_all(self):
        arena = TraditionBattles()
        result = arena.matchup_chart()
        n = len(DIAL_RANGES)
        # Each tradition should appear as a row label
        for name in DIAL_RANGES:
            assert name in result


class TestDialExplorer:
    """Tests for DialExplorer."""

    def test_nearby_returns_list(self):
        explorer = DialExplorer(seed=1)
        centre = DialPosition(harmonic_tension=2.5, rhythmic_complexity=2.5, spectral_density=2.5)
        result = explorer.nearby(centre, radius=1.0, n_samples=3)
        assert isinstance(result, list)
        assert len(result) == 3
        for p in result:
            assert isinstance(p, DialPosition)

    def test_nearby_sorted_by_distance(self):
        explorer = DialExplorer(seed=2)
        centre = DialPosition(harmonic_tension=1.0, rhythmic_complexity=1.0, spectral_density=1.0)
        result = explorer.nearby(centre, radius=2.0, n_samples=5)
        for i in range(len(result) - 1):
            d1 = sum((result[i].to_array() - centre.to_array()) ** 2) ** 0.5
            d2 = sum((result[i + 1].to_array() - centre.to_array()) ** 2) ** 0.5
            assert d1 <= d2 + 1e-6

    def test_nearby_in_bounds(self):
        explorer = DialExplorer(seed=3)
        centre = DialPosition(harmonic_tension=4.9, rhythmic_complexity=4.9, spectral_density=4.9)
        result = explorer.nearby(centre, radius=1.0, n_samples=4)
        for p in result:
            assert 0.0 <= p.harmonic_tension <= 5.0
            assert 0.0 <= p.rhythmic_complexity <= 5.0
            assert 0.0 <= p.spectral_density <= 5.0

    def test_describe_neighbourhood_known_zone(self):
        explorer = DialExplorer(seed=4)
        # Centre of Jazz
        centre = DialPosition.from_array(DIAL_RANGES["Jazz"]["center"])
        result = explorer.describe_neighbourhood(centre, radius=1.5)
        assert isinstance(result, str)
        assert "Jazz" in result or "nearby" in result.lower()

    def test_describe_neighbourhood_empty_zone(self):
        explorer = DialExplorer(seed=5)
        # Corner of dial space likely far from most traditions
        corner = DialPosition(harmonic_tension=0.1, rhythmic_complexity=0.1, spectral_density=0.1)
        result = explorer.describe_neighbourhood(corner, radius=0.3)
        assert "pioneer" in result.lower() or "Nearest" in result
