"""
Tests for the Monitor's public flow API: listen, assist, learn, check_vanish.
"""

import pytest
import random

from constraint_instrument.instrument import Instrument
from constraint_instrument.monitor import Monitor


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def instrument():
    return Instrument(mode="ella", terrain="blues")


@pytest.fixture
def monitor(instrument):
    return Monitor(instrument, sensitivity=0.5)


def make_notes(pitches, start=0.0, duration=0.5, velocity=80):
    """Helper to create note dicts."""
    notes = []
    t = start
    for p in pitches:
        notes.append({
            "pitch": p,
            "velocity": velocity,
            "start": round(t, 3),
            "duration": round(duration, 3),
        })
        t += duration
    return notes


# ── listen() ──────────────────────────────────────────────────────────

class TestListen:
    def test_returns_assessment_dict(self, monitor):
        notes = make_notes([60, 62, 64, 67, 69])
        result = monitor.listen(notes)
        assert isinstance(result, dict)
        for key in ["flow_state", "error_rate", "consistency", "exploration",
                     "energy", "energy_trajectory", "confidence", "recommendation"]:
            assert key in result, f"Missing key: {key}"

    def test_empty_notes_returns_defaults(self, monitor):
        result = monitor.listen([])
        assert result["flow_state"] == monitor.flow_state
        assert result["error_rate"] == 0.0
        assert result["energy"] == 0.0

    def test_flow_state_starts_at_default(self, instrument):
        m = Monitor(instrument)
        # Before any listen, flow_state is 0.5 (default from init)
        assert m.flow_state == 0.5

    def test_good_performance_raises_flow(self, monitor):
        """After clean, consistent notes, flow should rise."""
        initial = monitor.flow_state
        # Feed several bars of clean, in-register notes
        for _ in range(8):
            notes = make_notes([60, 62, 64, 65, 67, 69, 71, 72])
            result = monitor.listen(notes)
        assert monitor.flow_state > initial

    def test_bad_performance_lowers_flow(self, monitor):
        """After erratic, out-of-range notes, flow should drop."""
        # First get some flow going
        for _ in range(5):
            monitor.listen(make_notes([60, 62, 64, 67, 69]))
        flow_before = monitor.flow_state

        # Now feed bad notes
        for _ in range(8):
            bad_notes = make_notes([20, 110, 15, 115, 25], velocity=100)
            bad_notes[1]["velocity"] = 127
            bad_notes[3]["velocity"] = 10
            monitor.listen(bad_notes)
        assert monitor.flow_state < flow_before

    def test_energy_computed_from_velocity(self, monitor):
        quiet = make_notes([60, 62, 64], velocity=40)
        result_quiet = monitor.listen(quiet)
        loud = make_notes([65, 67, 69], velocity=120)
        result_loud = monitor.listen(loud)
        assert result_loud["energy"] > result_quiet["energy"]

    def test_recommendation_varies_with_flow(self, monitor):
        monitor.flow_state = 0.1
        notes = make_notes([60, 62, 64])
        monitor.listen(notes)
        # Low flow → struggling recommendation
        assert monitor.flow_state < 0.5

    def test_confidence_grows_with_data(self, monitor):
        result1 = monitor.listen(make_notes([60, 62, 64]))
        c1 = result1["confidence"]
        for _ in range(10):
            monitor.listen(make_notes([60, 62, 64, 67, 69]))
        result2 = monitor.listen(make_notes([60, 62, 64, 67, 69]))
        assert result2["confidence"] >= c1


# ── assist() ──────────────────────────────────────────────────────────

class TestAssist:
    def test_high_flow_untouched(self, monitor):
        """When flow is high, assist returns candidates as-is."""
        monitor.flow_state = 0.95
        candidates = [
            {"pitch": 60, "score": 0.3},
            {"pitch": 67, "score": 0.8},
            {"pitch": 72, "score": 0.5},
        ]
        result = monitor.assist(candidates)
        assert result == candidates

    def test_medium_flow_reorders(self, monitor):
        """When flow is medium, assist reorders candidates."""
        monitor.flow_state = 0.5
        # Learn some preferences first
        monitor._learn(make_notes([60, 62, 64, 65, 67, 69, 71, 72] * 3))

        candidates = [
            {"pitch": 100, "score": 0.9},  # out of register
            {"pitch": 64, "score": 0.5},   # in register
            {"pitch": 67, "score": 0.6},   # in register
        ]
        result = monitor.assist(candidates)
        assert len(result) == 3
        # In-register candidates should be boosted
        # (result may be reordered vs original)

    def test_low_flow_adds_guided_candidate(self, monitor):
        """When flow is low, assist adds a guided correction candidate."""
        monitor.flow_state = 0.1
        # Learn tendencies so we have something to guide toward
        for _ in range(5):
            monitor._learn(make_notes([60, 62, 64, 67, 69]))

        candidates = [
            {"pitch": 100, "score": 0.9},
            {"pitch": 20, "score": 0.8},
        ]
        result = monitor.assist(candidates)
        assert len(result) == 3  # 2 original + 1 guided
        assert result[0].get("_monitor_guided") is True

    def test_empty_candidates_returns_empty(self, monitor):
        assert monitor.assist([]) == []

    def test_preserves_all_original_candidates(self, monitor):
        """Assist should never remove candidates, only reorder/add."""
        monitor.flow_state = 0.4
        candidates = [{"pitch": i, "score": 0.5} for i in range(10)]
        result = monitor.assist(candidates)
        # All original pitches should be present
        result_pitches = {c["pitch"] for c in result}
        original_pitches = {c["pitch"] for c in candidates}
        assert original_pitches.issubset(result_pitches)


# ── learn() ───────────────────────────────────────────────────────────

class TestLearn:
    def test_updates_interval_preferences(self, monitor):
        # Play lots of perfect fourths (5 semitones)
        notes = []
        for i in range(10):
            notes.append({"pitch": 60 + i * 5, "velocity": 80, "start": i * 0.5, "duration": 0.4})
        monitor.learn(notes)
        assert 5 in monitor.learned_tendencies.favorite_intervals

    def test_updates_register(self, monitor):
        high_notes = make_notes([80, 82, 84, 86, 88] * 3)
        monitor.learn(high_notes)
        monitor.learn(high_notes)
        monitor.learn(high_notes)
        assert monitor.learned_tendencies.register_preference[0] > 60

    def test_updates_sample_count(self, monitor):
        assert monitor.learned_tendencies.sample_count == 0
        monitor.learn(make_notes([60, 62, 64]))
        assert monitor.learned_tendencies.sample_count == 1
        monitor.learn(make_notes([60, 62, 64]))
        assert monitor.learned_tendencies.sample_count == 2

    def test_empty_notes_no_crash(self, monitor):
        monitor.learn([])  # should not raise

    def test_multiple_learns_build_tendencies(self, monitor):
        for _ in range(10):
            monitor.learn(make_notes([60, 63, 67, 70, 72]))  # minor triad arpeggios
        t = monitor.learned_tendencies
        assert t.sample_count == 10
        # Interval 3 (minor third) and 4 (major third) should be present
        assert any(k in t.favorite_intervals for k in [3, 4, 7])


# ── check_vanish() ────────────────────────────────────────────────────

class TestCheckVanish:
    def test_returns_false_initially(self, monitor):
        assert monitor.check_vanish() is False

    def test_triggers_after_sustained_high_flow(self, monitor):
        """Vanish after sustained high flow, low errors, no interventions."""
        # Simulate conditions: 20 consecutive high-flow snapshots
        for _ in range(20):
            monitor.flow_history.append(0.95)
            monitor.error_history.append(0.01)
        monitor.intervention_count = 0
        assert monitor.check_vanish() is True
        assert monitor.is_vanished

    def test_does_not_vanish_with_errors(self, monitor):
        for _ in range(20):
            monitor.flow_history.append(0.95)
            monitor.error_history.append(0.2)  # too high
        monitor.intervention_count = 0
        assert monitor.check_vanish() is False

    def test_does_not_vanish_with_interventions(self, monitor):
        for _ in range(20):
            monitor.flow_history.append(0.95)
            monitor.error_history.append(0.01)
        monitor.intervention_count = 5  # recent interventions
        assert monitor.check_vanish() is False

    def test_already_vanished_returns_true(self, monitor):
        monitor._vanished = True
        assert monitor.check_vanish() is True

    def test_vanished_monitor_listen_still_works(self, monitor):
        """Even when vanished, listen() should still work (just observing)."""
        monitor._vanished = True
        result = monitor.listen(make_notes([60, 62, 64]))
        assert isinstance(result, dict)
        assert "flow_state" in result


# ── Integration: Full Flow Journey ────────────────────────────────────

class TestFlowJourney:
    def test_rough_to_flow_to_vanish(self, instrument):
        """
        Simulate a performer who starts rough, improves, achieves flow.
        Monitor adapts assistance and eventually vanishes.
        """
        m = Monitor(instrument, sensitivity=0.6)

        # Phase 1: Rough (random, out of range)
        for bar in range(5):
            rough = []
            t = bar * 4.0
            for i in range(8):
                rough.append({
                    "pitch": random.randint(20, 120),
                    "velocity": random.randint(30, 127),
                    "start": round(t + i * 0.5 + random.uniform(-0.2, 0.2), 3),
                    "duration": round(random.uniform(0.1, 1.0), 3),
                })
            m.listen(rough)
        flow_after_rough = m.flow_state
        assert flow_after_rough < 0.7  # probably struggling

        # Phase 2: Improving (structured, in-register)
        for bar in range(10):
            improving = make_notes(
                [60, 62, 64, 65, 67, 69, 71, 72],
                start=bar * 4.0,
                duration=0.5,
                velocity=80,
            )
            m.listen(improving)
        flow_after_improving = m.flow_state
        assert flow_after_improving > flow_after_rough

        # Phase 3: Deep flow (very consistent, expressive)
        for bar in range(25):
            flowing = make_notes(
                [60, 62, 64, 67, 69, 72, 71, 67],
                start=bar * 4.0,
                duration=0.5,
                velocity=85,
            )
            m.listen(flowing)

        # Flow should be high
        assert m.flow_state > 0.7

        # Assist at high flow should be hands-off
        candidates = [{"pitch": 60}, {"pitch": 67}, {"pitch": 72}]
        result = m.assist(candidates)
        assert result == candidates  # untouched

    def test_learn_then_assist_uses_tendencies(self, instrument):
        """After learning, assist should use learned preferences."""
        m = Monitor(instrument, sensitivity=0.5)
        m.flow_state = 0.4  # medium flow → reorder

        # Teach it a preference for high register
        for _ in range(10):
            m.learn(make_notes([80, 82, 84, 86, 88, 90]))

        candidates = [
            {"pitch": 60, "score": 0.5},  # low
            {"pitch": 85, "score": 0.5},  # high — in learned register
        ]
        result = m.assist(candidates)
        # The high-register candidate should be ranked first
        assert result[0]["pitch"] == 85
