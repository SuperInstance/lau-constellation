"""
Music recommendation engine based on dial space proximity.

Recommends traditions, generates novel positions for composition, and provides
human-readable explanations. Uses dial distance, adventure factor scoring,
historical fusion precedent, and JND-aware filtering.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

from .analyzer import analyze_midi, analyze_wav
from .classifier import DialClassifier
from .dials import DIAL_RANGES, DialPosition, compute_dial_distance


@dataclass
class Recommendation:
    """A single music recommendation.

    Parameters
    ----------
    tradition_name : str
        Name of the recommended tradition or position.
    dial_position : DialPosition
        Position in dial space.
    distance : float
        Distance from query position.
    adventure_factor : float
        How different vs rewarding (0=safe, 1=adventurous).
    explanation : str
        Human-readable explanation.
    fusion_viability : float
        How well this would fuse with the query tradition (0-1).
    jnd_perceptible : bool
        Whether the difference is perceptually noticeable.
    """

    tradition_name: str
    dial_position: DialPosition
    distance: float
    adventure_factor: float
    explanation: str
    fusion_viability: float = 0.0
    jnd_perceptible: bool = True


# JND thresholds (Just Noticeable Difference) per dial axis
# I_vert (harmonic tension) is ~4x more noticeable than I_spectral
JND_H = 0.15  # harmonic tension JND
JND_R = 0.20  # rhythmic complexity JND
JND_S = 0.60  # spectral density JND (less noticeable)


def _jnd_perceptible(pos1: DialPosition, pos2: DialPosition) -> bool:
    """Check if the difference between two positions is perceptually noticeable.

    Parameters
    ----------
    pos1, pos2 : DialPosition
        Positions to compare.

    Returns
    -------
    bool
        True if the difference exceeds JND on at least one axis.
    """
    dh = abs(pos1.harmonic_tension - pos2.harmonic_tension)
    dr = abs(pos1.rhythmic_complexity - pos2.rhythmic_complexity)
    ds = abs(pos1.spectral_density - pos2.spectral_density)
    return dh > JND_H or dr > JND_R or ds > JND_S


def _adventure_factor(query: DialPosition, candidate: DialPosition) -> float:
    """Compute adventure factor: how different yet rewarding.

    Balances distance (novelty) with "reward" (proximity to the most
    pleasing region around Gagaku's position).

    Parameters
    ----------
    query : DialPosition
        Starting position.
    candidate : DialPosition
        Candidate recommendation.

    Returns
    -------
    float
        Adventure factor in [0, 1]. Higher = more adventurous.
    """
    dist = compute_dial_distance(query, candidate)
    max_dist = 5.0 * np.sqrt(3)
    novelty = dist / max_dist

    # Reward: closeness to pleasing center (Gagaku)
    pleasing_center = np.array([2.5, 2.3, 4.0])
    candidate_arr = candidate.to_array()
    pleasing_dist = np.linalg.norm(candidate_arr - pleasing_center)
    reward = 1.0 - pleasing_dist / max_dist

    return float(np.clip(0.6 * novelty + 0.4 * reward, 0, 1))


def _fusion_viability(pos1: DialPosition, pos2: DialPosition) -> float:
    """Estimate how well two traditions could fuse.

    Based on historical precedent: traditions that are close in dial space
    but differ on specific axes tend to produce viable fusions.

    Parameters
    ----------
    pos1, pos2 : DialPosition
        Positions to compare.

    Returns
    -------
    float
        Fusion viability score in [0, 1].
    """
    dist = compute_dial_distance(pos1, pos2)
    # Too close = same thing, too far = incompatible
    # Sweet spot around distance 1.5-3.0
    if dist < 0.5:
        return 0.3  # too similar
    elif dist < 1.5:
        return 0.7 + 0.3 * (dist / 1.5)
    elif dist < 3.0:
        return 1.0 - (dist - 1.5) / 5.0
    else:
        return max(0.1, 0.7 - (dist - 3.0) / 5.0)


class MusicRecommender:
    """Recommend music based on dial space proximity.

    Uses dial distance, adventure factor, historical fusion precedent,
    and JND-aware filtering to suggest traditions and novel positions.

    Parameters
    ----------
    seed : int
        Random seed for novel position generation.
    """

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self._classifier = DialClassifier(k=5, seed=seed)

    def recommend(
        self, query_path: str | Path, n: int = 5
    ) -> list[Recommendation]:
        """Find closest traditions to a query file.

        Analyzes the query file (WAV or MIDI) and returns the n closest
        traditions ranked by a composite score.

        Parameters
        ----------
        query_path : str or Path
            Path to the query audio/MIDI file.
        n : int
            Number of recommendations.

        Returns
        -------
        list of Recommendation
            Ranked recommendations with explanations.
        """
        path = Path(query_path)
        suffix = path.suffix.lower()

        if suffix in (".mid", ".midi"):
            result = analyze_midi(path)
        else:
            result = analyze_wav(path)

        query_pos = result.dial_position
        return self._recommend_from_position(query_pos, n)

    def recommend_between(
        self, tradition_a: str, tradition_b: str, n: int = 5
    ) -> list[DialPosition]:
        """Find interesting dial positions between two traditions.

        Interpolates between two tradition profiles and finds positions
        that maximize interestingness (off-center but not chaotic).

        Parameters
        ----------
        tradition_a : str
            First tradition name.
        tradition_b : str
            Second tradition name.
        n : int
            Number of positions to return.

        Returns
        -------
        list of DialPosition
            Interesting positions between the traditions.

        Raises
        ------
        ValueError
            If either tradition is unknown.
        """
        if tradition_a not in DIAL_RANGES:
            raise ValueError(f"Unknown tradition: {tradition_a}")
        if tradition_b not in DIAL_RANGES:
            raise ValueError(f"Unknown tradition: {tradition_b}")

        center_a = DIAL_RANGES[tradition_a]["center"]
        center_b = DIAL_RANGES[tradition_b]["center"]
        spread_a = DIAL_RANGES[tradition_a]["spread"]
        spread_b = DIAL_RANGES[tradition_b]["spread"]

        rng = np.random.RandomState(self.seed)
        positions = []

        # Generate positions along the interpolation path with some spread
        for blend in np.linspace(0.1, 0.9, n):
            center = center_a * (1 - blend) + center_b * blend
            spread = spread_a * (1 - blend) + spread_b * blend
            # Add some randomness for interestingness
            offset = rng.randn(3) * spread * 0.3
            pos = np.clip(center + offset, 0, 5)
            positions.append(
                DialPosition.from_array(
                    pos,
                    tradition_name=f"{tradition_a}/{tradition_b} blend={blend:.1f}",
                    metadata={
                        "blend": float(blend),
                        "tradition_a": tradition_a,
                        "tradition_b": tradition_b,
                    },
                )
            )

        return positions

    def recommend_novel(self, n: int = 5) -> list[DialPosition]:
        """Recommend unexplored dial positions for new composition.

        Uses Monte Carlo search for positions maximally far from all
        known traditions.

        Parameters
        ----------
        n : int
            Number of novel positions to return.

        Returns
        -------
        list of DialPosition
            Novel positions far from known traditions.
        """
        rng = np.random.RandomState(self.seed)
        tradition_centers = np.array(
            [DIAL_RANGES[t]["center"] for t in DIAL_RANGES]
        )
        tradition_spreads = np.array(
            [DIAL_RANGES[t]["spread"] for t in DIAL_RANGES]
        )

        # Monte Carlo search for positions maximally far from traditions
        n_candidates = 10000
        candidates = rng.uniform(0, 5, size=(n_candidates, 3))

        # Compute normalized distance to nearest tradition for each candidate
        min_distances = np.full(n_candidates, np.inf)
        for center, spread in zip(tradition_centers, tradition_spreads):
            diffs = (candidates - center) / spread
            dists = np.sqrt(np.sum(diffs**2, axis=1))
            min_distances = np.minimum(min_distances, dists)

        # Select top-n by distance
        top_indices = np.argsort(min_distances)[-n:][::-1]
        novel_positions = []
        for idx in top_indices:
            pos = candidates[idx]
            novel_positions.append(
                DialPosition.from_array(
                    pos,
                    tradition_name="Novel",
                    metadata={
                        "min_distance_to_tradition": float(min_distances[idx]),
                        "exploration_score": float(min_distances[idx] / 5.0),
                    },
                )
            )

        return novel_positions

    def explain(self, query_path: str | Path, recommendation: Recommendation) -> str:
        """Human-readable explanation of why this was recommended.

        Parameters
        ----------
        query_path : str or Path
            Path to the query file.
        recommendation : Recommendation
            The recommendation to explain.

        Returns
        -------
        str
            Explanation string.
        """
        path = Path(query_path)
        suffix = path.suffix.lower()
        if suffix in (".mid", ".midi"):
            result = analyze_midi(path)
        else:
            result = analyze_wav(path)

        qpos = result.dial_position
        rpos = recommendation.dial_position

        dh = rpos.harmonic_tension - qpos.harmonic_tension
        dr = rpos.rhythmic_complexity - qpos.rhythmic_complexity
        ds = rpos.spectral_density - qpos.spectral_density

        lines = [
            f"Recommendation: {recommendation.tradition_name}",
            f"  Distance: {recommendation.distance:.2f} (in 3D dial space)",
            f"  Adventure: {recommendation.adventure_factor:.0%} ({'adventurous' if recommendation.adventure_factor > 0.5 else 'safe'})",
        ]

        if recommendation.fusion_viability > 0:
            lines.append(
                f"  Fusion viability: {recommendation.fusion_viability:.0%}"
            )

        lines.append("  Differences from your music:")
        if abs(dh) > JND_H:
            lines.append(
                f"    Harmonic tension: {dh:+.2f} ({'more tense' if dh > 0 else 'more relaxed'})"
            )
        if abs(dr) > JND_R:
            lines.append(
                f"    Rhythmic complexity: {dr:+.2f} ({'more complex' if dr > 0 else 'simpler'})"
            )
        if abs(ds) > JND_S:
            lines.append(
                f"    Spectral density: {ds:+.2f} ({'richer' if ds > 0 else 'sparser'})"
            )

        if not recommendation.jnd_perceptible:
            lines.append("  Note: differences are subtle (below perceptual threshold)")

        return "\n".join(lines)

    def taste_map(self, query_paths: list[str | Path]) -> str:
        """Generate a text-based taste map showing preference distribution.

        Parameters
        ----------
        query_paths : list of str or Path
            Paths to analyzed files.

        Returns
        -------
        str
            ASCII art taste map.
        """
        positions = []
        for path in query_paths:
            p = Path(path)
            suffix = p.suffix.lower()
            try:
                if suffix in (".mid", ".midi"):
                    result = analyze_midi(p)
                else:
                    result = analyze_wav(p)
                positions.append(result.dial_position)
            except Exception:
                continue

        if not positions:
            return "No valid files to map."

        # 2D projection: H vs S (harmonic tension vs spectral density)
        # 20x40 character grid
        grid_h = 20
        grid_w = 40
        grid = np.zeros((grid_h, grid_w), dtype=int)

        for pos in positions:
            # Map [0,5] -> [0, grid_size-1]
            col = int(np.clip(pos.harmonic_tension / 5 * (grid_w - 1), 0, grid_w - 1))
            row = int(np.clip((5 - pos.spectral_density) / 5 * (grid_h - 1), 0, grid_h - 1))
            grid[row, col] += 1

        # Add tradition centers for reference
        tradition_markers = {}
        for name, profile in DIAL_RANGES.items():
            col = int(np.clip(profile["center"][0] / 5 * (grid_w - 1), 0, grid_w - 1))
            row = int(np.clip((5 - profile["center"][2]) / 5 * (grid_h - 1), 0, grid_h - 1))
            tradition_markers[(row, col)] = name[:3].upper()

        lines = [
            "Taste Map (Harmonic Tension vs Spectral Density)",
            "  S=5 " + "─" * grid_w + " S=5",
        ]

        for r in range(grid_h):
            line = "  │"
            for c in range(grid_w):
                if (r, c) in tradition_markers:
                    line += tradition_markers[(r, c)][0]
                elif grid[r, c] > 0:
                    line += "●"
                else:
                    line += " "
            line += "│"
            lines.append(line)

        lines.append("  S=0 " + "─" * grid_w + " S=0")
        lines.append(f"      H=0{'':>{grid_w - 6}}H=5")
        lines.append("")
        lines.append("  ● = your music  |  Letters = tradition centers")

        return "\n".join(lines)

    def _recommend_from_position(
        self, query_pos: DialPosition, n: int = 5
    ) -> list[Recommendation]:
        """Generate recommendations from a known dial position.

        Parameters
        ----------
        query_pos : DialPosition
            Query position in dial space.
        n : int
            Number of recommendations.

        Returns
        -------
        list of Recommendation
        """
        # Score each tradition
        scored = []
        for name, profile in DIAL_RANGES.items():
            center = profile["center"]
            trad_pos = DialPosition.from_array(center, tradition_name=name)

            dist = compute_dial_distance(query_pos, trad_pos)
            adventure = _adventure_factor(query_pos, trad_pos)
            fusion = _fusion_viability(query_pos, trad_pos)
            perceptible = _jnd_perceptible(query_pos, trad_pos)

            # Composite score: closer = better, but adventure adds novelty
            # Weight: 60% closeness, 20% adventure, 20% fusion
            max_dist = 5.0 * np.sqrt(3)
            closeness = 1.0 - dist / max_dist
            score = 0.6 * closeness + 0.2 * adventure + 0.2 * fusion

            scored.append((score, name, trad_pos, dist, adventure, fusion, perceptible))

        # Sort by composite score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        # Take top n
        recommendations = []
        for score, name, trad_pos, dist, adventure, fusion, perceptible in scored[:n]:
            exp = self._generate_explanation(query_pos, trad_pos, name, dist, adventure, fusion)
            recommendations.append(
                Recommendation(
                    tradition_name=name,
                    dial_position=trad_pos,
                    distance=dist,
                    adventure_factor=adventure,
                    explanation=exp,
                    fusion_viability=fusion,
                    jnd_perceptible=perceptible,
                )
            )

        return recommendations

    def _generate_explanation(
        self,
        query: DialPosition,
        target: DialPosition,
        name: str,
        dist: float,
        adventure: float,
        fusion: float,
    ) -> str:
        """Generate a human-readable explanation for a recommendation.

        Parameters
        ----------
        query : DialPosition
            Query position.
        target : DialPosition
            Recommended tradition position.
        name : str
            Tradition name.
        dist : float
            Distance between positions.
        adventure : float
            Adventure factor.
        fusion : float
            Fusion viability.

        Returns
        -------
        str
        """
        dh = target.harmonic_tension - query.harmonic_tension
        dr = target.rhythmic_complexity - query.rhythmic_complexity
        ds = target.spectral_density - query.spectral_density

        parts = [f"{name}"]

        if dist < 1.0:
            parts.append("very close to your taste")
        elif dist < 2.0:
            parts.append("nearby in dial space")
        elif dist < 3.0:
            parts.append("a moderate departure")
        else:
            parts.append("an adventurous leap")

        diffs = []
        if abs(dh) > JND_H:
            diffs.append(f"{'↑' if dh > 0 else '↓'}tension")
        if abs(dr) > JND_R:
            diffs.append(f"{'↑' if dr > 0 else '↓'}rhythm")
        if abs(ds) > JND_S:
            diffs.append(f"{'↑' if ds > 0 else '↓'}texture")

        if diffs:
            parts.append("(" + ", ".join(diffs) + ")")

        if fusion > 0.7:
            parts.append("great fusion potential")
        elif fusion > 0.4:
            parts.append("moderate fusion potential")

        return " — ".join(parts)
