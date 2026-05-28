"""
Musical Evolution Simulator.

Simulates the evolution of musical traditions as a genetic algorithm in 3D dial
space. Tracks population diversity, detects cultural phases (Discovery,
Codification, Ubiquity, Boredom, Rebellion), and predicts the next rebellion.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from numpy.typing import NDArray

from .dials import DialPosition, DIAL_RANGES, compute_dial_distance


class MusicalEvolution:
    """Evolve musical traditions via genetic algorithm in dial space.

    Each "individual" is a DialPosition.  Over generations the population
    drifts, converges, and occasionally mutates radically — mirroring how
    real musical styles are born, codified, popularised, exhausted, and
    overthrown.

    Parameters
    ----------
    population_size : int
        Number of individuals per generation.
    seed : int
        Random seed for reproducibility.
    """

    PHASES: list[str] = ["Discovery", "Codification", "Ubiquity", "Boredom", "Rebellion"]

    def __init__(self, population_size: int = 60, seed: int = 42) -> None:
        self.population_size = population_size
        self.seed = seed
        self._rng = np.random.RandomState(seed)
        self._history: list[dict] = []
        self._population: list[DialPosition] = []
        self._generation = 0
        self._init_population()

    def _init_population(self) -> None:
        """Seed the population around known tradition centres."""
        traditions = list(DIAL_RANGES.keys())
        self._population = []
        while len(self._population) < self.population_size:
            tradition = traditions[len(self._population) % len(traditions)]
            centre = DIAL_RANGES[tradition]["center"]
            spread = DIAL_RANGES[tradition]["spread"]
            sample = centre + self._rng.randn(3) * spread
            sample = np.clip(sample, 0.0, 5.0)
            self._population.append(
                DialPosition.from_array(sample, tradition_name=tradition)
            )

    def _diversity(self, population: list[DialPosition]) -> float:
        """Mean pairwise Euclidean distance in the population."""
        if len(population) < 2:
            return 0.0
        vecs = np.array([p.to_array() for p in population], dtype=np.float64)
        # Vectorised pairwise distances
        diffs = vecs[:, np.newaxis, :] - vecs[np.newaxis, :, :]
        dists = np.sqrt(np.sum(diffs**2, axis=2))
        # Upper-triangle mean
        mask = np.triu(np.ones_like(dists, dtype=bool), k=1)
        return float(dists[mask].mean()) if mask.any() else 0.0

    def _fitness(self, pos: DialPosition) -> float:
        """Fitness = distance from nearest tradition centre (novelty bonus)."""
        min_dist = min(
            compute_dial_distance(pos, DialPosition.from_array(profile["center"]))
            for profile in DIAL_RANGES.values()
        )
        # Also reward being inside valid space
        return float(min_dist + 0.5)

    def _select(self, population: list[DialPosition], fitnesses: NDArray[np.float64]) -> list[DialPosition]:
        """Tournament selection."""
        selected = []
        for _ in range(self.population_size):
            i, j = self._rng.choice(len(population), size=2, replace=False)
            winner = population[i] if fitnesses[i] > fitnesses[j] else population[j]
            selected.append(winner)
        return selected

    def _crossover(
        self, parent_a: DialPosition, parent_b: DialPosition
    ) -> DialPosition:
        """Blend two parents with random interpolation."""
        alpha = self._rng.uniform(0.2, 0.8)
        child_arr = alpha * parent_a.to_array() + (1 - alpha) * parent_b.to_array()
        child_arr = np.clip(child_arr, 0.0, 5.0)
        return DialPosition.from_array(child_arr, tradition_name="Hybrid")

    def _mutate(self, pos: DialPosition, generation: int) -> DialPosition:
        """Mutate a position; mutation strength decays then spikes (rebellion)."""
        phase = self.detect_phase()
        if phase == "Rebellion":
            sigma = 1.5
        elif phase == "Boredom":
            sigma = 0.8
        elif phase == "Ubiquity":
            sigma = 0.2
        else:
            sigma = 0.5

        mutated = pos.to_array() + self._rng.randn(3) * sigma
        mutated = np.clip(mutated, 0.0, 5.0)
        return DialPosition.from_array(mutated, tradition_name=pos.tradition_name)

    def evolve(self, n_generations: int = 100) -> list[dict]:
        """Run the genetic algorithm for ``n_generations``.

        Parameters
        ----------
        n_generations : int
            Number of generations to simulate.

        Returns
        -------
        list of dict
            Per-generation history records with keys ``generation``,
            ``diversity``, ``mean_fitness``, ``phase``, and ``best_position``.
        """
        for _ in range(n_generations):
            fitnesses = np.array([self._fitness(p) for p in self._population], dtype=np.float64)
            div = self._diversity(self._population)
            phase = self.detect_phase()

            best_idx = int(np.argmax(fitnesses))
            record = {
                "generation": self._generation,
                "diversity": div,
                "mean_fitness": float(fitnesses.mean()),
                "phase": phase,
                "best_position": self._population[best_idx],
            }
            self._history.append(record)

            # Selection → crossover → mutation
            selected = self._select(self._population, fitnesses)
            next_pop: list[DialPosition] = []
            # Elitism: keep best
            next_pop.append(self._population[best_idx])

            while len(next_pop) < self.population_size:
                a, b = self._rng.choice(len(selected), size=2, replace=False)
                child = self._crossover(selected[a], selected[b])
                if self._rng.random() < 0.3:
                    child = self._mutate(child, self._generation)
                next_pop.append(child)

            self._population = next_pop[: self.population_size]
            self._generation += 1

        return self._history

    def detect_phase(self) -> str:
        """Detect the current cultural phase from population statistics.

        Phases
        ------
        Discovery
            High diversity, low generation count.
        Codification
            Diversity falling as norms solidify.
        Ubiquity
            Very low diversity, stable fitness.
        Boredom
            Diversity creeping up, fitness plateau.
        Rebellion
            Sharp diversity spike or very high generation with low diversity.

        Returns
        -------
        str
            One of the five phase names.
        """
        if not self._history:
            return "Discovery"

        current_div = self._diversity(self._population)
        recent = self._history[-10:]
        mean_recent_div = float(np.mean([r["diversity"] for r in recent])) if recent else current_div
        gen = self._generation

        # Rebellion triggers
        if gen > 80 and current_div < 1.0:
            return "Rebellion"
        if len(self._history) >= 2:
            div_trend = current_div - self._history[-2]["diversity"]
            if div_trend > 0.4:
                return "Rebellion"

        if current_div > 2.5:
            return "Discovery"
        if current_div > 1.5 and mean_recent_div > current_div:
            return "Codification"
        if current_div < 1.0 and mean_recent_div < 1.2:
            return "Ubiquity"
        if current_div < 1.5 and mean_recent_div >= 1.0:
            return "Boredom"

        return "Discovery"

    def predict_rebellion(self, horizon: int = 50) -> dict:
        """Predict when the next Rebellion phase will occur.

        Uses a simple linear extrapolation of diversity trend.

        Parameters
        ----------
        horizon : int
            Maximum generations to look ahead.

        Returns
        -------
        dict
            Keys ``predicted_generation``, ``confidence`` (0–1), and
            ``current_phase``.
        """
        if len(self._history) < 5:
            return {
                "predicted_generation": self._generation + horizon,
                "confidence": 0.2,
                "current_phase": self.detect_phase(),
            }

        divs = np.array([r["diversity"] for r in self._history[-20:]], dtype=np.float64)
        gens = np.arange(len(divs))
        # Linear regression on recent diversity
        if len(gens) > 1:
            slope = np.polyfit(gens, divs, 1)[0]
        else:
            slope = 0.0

        current_div = divs[-1]
        current_phase = self.detect_phase()

        # Rebellion threshold: diversity spike or generation exhaustion
        threshold = 2.0
        if slope <= 0:
            # Stagnation → rebellion is imminent
            predicted = self._generation + max(5, int(horizon * 0.2))
            confidence = min(0.9, 0.5 + abs(slope))
        else:
            gens_to_threshold = (threshold - current_div) / slope if slope > 0 else horizon
            predicted = self._generation + int(np.clip(gens_to_threshold, 5, horizon))
            confidence = min(0.95, max(0.3, 0.7 - abs(gens_to_threshold) / horizon))

        return {
            "predicted_generation": predicted,
            "confidence": round(confidence, 3),
            "current_phase": current_phase,
        }

    @property
    def population(self) -> list[DialPosition]:
        """Current population."""
        return self._population

    @property
    def history(self) -> list[dict]:
        """Evolution history."""
        return self._history
