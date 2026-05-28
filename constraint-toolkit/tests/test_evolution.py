"""Tests for the musical evolution simulator."""

import math

import numpy as np
import pytest

from constraint_toolkit.evolution import MusicalEvolution
from constraint_toolkit.dials import DialPosition


class TestMusicalEvolution:
    """Tests for MusicalEvolution GA."""

    def test_init_population_size(self):
        sim = MusicalEvolution(population_size=30, seed=1)
        assert len(sim.population) == 30

    def test_evolve_returns_history(self):
        sim = MusicalEvolution(population_size=20, seed=2)
        history = sim.evolve(n_generations=10)
        assert len(history) == 10
        for record in history:
            assert "generation" in record
            assert "diversity" in record
            assert "mean_fitness" in record
            assert "phase" in record
            assert "best_position" in record
            assert isinstance(record["best_position"], DialPosition)

    def test_evolve_population_constant(self):
        sim = MusicalEvolution(population_size=25, seed=3)
        sim.evolve(n_generations=5)
        assert len(sim.population) == 25

    def test_detect_phase_valid(self):
        sim = MusicalEvolution(population_size=20, seed=4)
        sim.evolve(n_generations=5)
        phase = sim.detect_phase()
        assert phase in MusicalEvolution.PHASES

    def test_diversity_non_negative(self):
        sim = MusicalEvolution(population_size=20, seed=5)
        sim.evolve(n_generations=5)
        for record in sim.history:
            assert record["diversity"] >= 0.0

    def test_fitness_improves_or_stable(self):
        sim = MusicalEvolution(population_size=20, seed=6)
        history = sim.evolve(n_generations=10)
        # Best fitness should not collapse to zero
        assert history[-1]["mean_fitness"] > 0.0

    def test_predict_rebellion_structure(self):
        sim = MusicalEvolution(population_size=20, seed=7)
        sim.evolve(n_generations=15)
        pred = sim.predict_rebellion(horizon=30)
        assert "predicted_generation" in pred
        assert "confidence" in pred
        assert "current_phase" in pred
        assert 0.0 <= pred["confidence"] <= 1.0
        assert pred["current_phase"] in MusicalEvolution.PHASES

    def test_rebellion_triggered_at_high_gen(self):
        sim = MusicalEvolution(population_size=20, seed=8)
        sim.evolve(n_generations=100)
        phase = sim.detect_phase()
        assert phase in MusicalEvolution.PHASES

    def test_history_accumulates(self):
        sim = MusicalEvolution(population_size=10, seed=9)
        sim.evolve(n_generations=5)
        first_len = len(sim.history)
        sim.evolve(n_generations=3)
        assert len(sim.history) == first_len + 3

    def test_population_in_bounds(self):
        sim = MusicalEvolution(population_size=20, seed=10)
        sim.evolve(n_generations=10)
        for p in sim.population:
            assert 0.0 <= p.harmonic_tension <= 5.0
            assert 0.0 <= p.rhythmic_complexity <= 5.0
            assert 0.0 <= p.spectral_density <= 5.0
