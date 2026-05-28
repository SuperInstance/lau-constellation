"""
Musical Games.

Light-weight games for exploring dial space:
- DialGuesser: guess the tradition from dial hints
- TraditionBattles: compare traditions like a fighting-game matchup
- DialExplorer: discover positions near a given point
"""

from __future__ import annotations

import random
from typing import Optional

import numpy as np

from .dials import DialPosition, DIAL_RANGES, compute_dial_distance


class DialGuesser:
    """Guess the musical tradition from incremental dial-space hints.

    Parameters
    ----------
    seed : int
        Random seed for puzzle generation.
    """

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self._rng = random.Random(seed)
        self._target: Optional[str] = None
        self._hints_given = 0

    def new_game(self) -> str:
        """Start a new guessing round.

        Returns
        -------
        str
            A prompt with the first hint.
        """
        self._target = self._rng.choice(list(DIAL_RANGES.keys()))
        self._hints_given = 0
        return self._next_hint()

    def _next_hint(self) -> str:
        """Generate the next hint string."""
        if self._target is None:
            return "Start a new game with new_game()!"

        profile = DIAL_RANGES[self._target]
        centre = profile["center"]
        desc = profile["description"]
        h, r, s = centre

        hints = [
            f"Hint 1 — Description: '{desc}'",
            f"Hint 2 — Harmonic tension is around {h:.1f}.",
            f"Hint 3 — Rhythmic complexity is around {r:.1f}.",
            f"Hint 4 — Spectral density is around {s:.1f}.",
            f"Hint 5 — First letter is '{self._target[0]}'.",
        ]

        if self._hints_given < len(hints):
            hint = hints[self._hints_given]
            self._hints_given += 1
            return f"Guess the tradition! ({self._hints_given}/5 hints used)\n{hint}"
        return f"No more hints! The answer was: {self._target}"

    def guess(self, name: str) -> str:
        """Submit a guess.

        Parameters
        ----------
        name : str
            The tradition name to guess.

        Returns
        -------
        str
            Result message.  If correct, awards points; if wrong, offers
            another hint.
        """
        if self._target is None:
            return "Start a new game with new_game()!"

        if name.strip().lower() == self._target.lower():
            score = max(1, 6 - self._hints_given)
            msg = f"CORRECT! It was {self._target}. Score: {score}/5 points."
            self._target = None
            return msg

        if self._hints_given >= 5:
            msg = f"Wrong, and you're out of hints. It was {self._target}."
            self._target = None
            return msg

        return f"Nope! {self._next_hint()}"


class TraditionBattles:
    """Pit two musical traditions against each other in dial-space combat.

    Like a fighting-game matchup chart, but for harmonic tension.
    """

    def __init__(self) -> None:
        self._stats = {
            "HarmonicTension": lambda p: p.harmonic_tension,
            "RhythmicComplexity": lambda p: p.rhythmic_complexity,
            "SpectralDensity": lambda p: p.spectral_density,
        }

    def _make_pos(self, tradition: str) -> DialPosition:
        """Return a canonical DialPosition for a tradition."""
        if tradition not in DIAL_RANGES:
            raise ValueError(f"Unknown tradition: {tradition}")
        return DialPosition.from_array(
            DIAL_RANGES[tradition]["center"], tradition_name=tradition
        )

    def fight(self, tradition_a: str, tradition_b: str) -> str:
        """Run a three-round battle between two traditions.

        Parameters
        ----------
        tradition_a, tradition_b : str
            The two combatants.

        Returns
        -------
        str
            Play-by-play ASCII battle report.
        """
        pos_a = self._make_pos(tradition_a)
        pos_b = self._make_pos(tradition_b)

        lines: list[str] = []
        lines.append("╔" + "═" * 60 + "╗")
        lines.append(f"║{'TRADITION BATTLE':^60}║")
        lines.append(f"║{tradition_a:^29} VS {tradition_b:^29}║")
        lines.append("╚" + "═" * 60 + "╝")

        a_wins = 0
        b_wins = 0

        for stat_name, getter in self._stats.items():
            val_a = getter(pos_a)
            val_b = getter(pos_b)
            diff = abs(val_a - val_b)

            if val_a > val_b:
                winner = tradition_a
                a_wins += 1
                bar_a = "█" * int(val_a * 8)
                bar_b = "░" * int(val_b * 8)
            elif val_b > val_a:
                winner = tradition_b
                b_wins += 1
                bar_a = "░" * int(val_a * 8)
                bar_b = "█" * int(val_b * 8)
            else:
                winner = "DRAW"
                bar_a = "█" * int(val_a * 8)
                bar_b = "█" * int(val_b * 8)

            lines.append(f"\nRound: {stat_name}")
            lines.append(f"  {tradition_a:<22} │{bar_a:<40s}│ {val_a:.1f}")
            lines.append(f"  {tradition_b:<22} │{bar_b:<40s}│ {val_b:.1f}")
            lines.append(f"  Winner: {winner} (margin {diff:.1f})")

        lines.append("")
        if a_wins > b_wins:
            lines.append(f"🏆 CHAMPION: {tradition_a} ({a_wins}-{b_wins})")
        elif b_wins > a_wins:
            lines.append(f"🏆 CHAMPION: {tradition_b} ({b_wins}-{a_wins})")
        else:
            lines.append(f"🤝 DRAW ({a_wins}-{b_wins})")

        return "\n".join(lines)

    def matchup_chart(self) -> str:
        """Generate a compact win/loss matrix for all traditions.

        Returns
        -------
        str
            ASCII matchup chart.
        """
        names = list(DIAL_RANGES.keys())
        n = len(names)
        # Wins matrix
        wins = np.zeros((n, n), dtype=np.int64)
        for i, a in enumerate(names):
            pos_a = self._make_pos(a)
            for j, b in enumerate(names):
                if i == j:
                    wins[i, j] = -1
                    continue
                pos_b = self._make_pos(b)
                score_a = sum(
                    1
                    for getter in self._stats.values()
                    if getter(pos_a) > getter(pos_b)
                )
                score_b = sum(
                    1
                    for getter in self._stats.values()
                    if getter(pos_b) > getter(pos_a)
                )
                if score_a > score_b:
                    wins[i, j] = 1
                elif score_b > score_a:
                    wins[i, j] = 0
                else:
                    wins[i, j] = 2  # draw

        lines: list[str] = []
        lines.append("Matchup Chart (row = attacker, col = defender)")
        lines.append("W = win, L = loss, D = draw, . = self")
        lines.append("")

        # Header
        header = "           " + " ".join(f"{name[:3]:>3}" for name in names)
        lines.append(header)
        lines.append("           " + "-" * (4 * n))

        for i, name in enumerate(names):
            row = f"{name:<10} "
            for j in range(n):
                if wins[i, j] == -1:
                    row += "  . "
                elif wins[i, j] == 1:
                    row += "  W "
                elif wins[i, j] == 0:
                    row += "  L "
                else:
                    row += "  D "
            lines.append(row)

        return "\n".join(lines)


class DialExplorer:
    """Discover nearby positions in dial space and report what you find."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self._rng = np.random.RandomState(seed)

    def nearby(
        self,
        position: DialPosition,
        radius: float = 1.0,
        n_samples: int = 5,
    ) -> list[DialPosition]:
        """Sample random positions within ``radius`` of ``position``.

        Parameters
        ----------
        position : DialPosition
            Centre point.
        radius : float
            Maximum Euclidean distance.
        n_samples : int
            Number of samples to generate.

        Returns
        -------
        list of DialPosition
            Neighbouring positions, sorted by distance from centre.
        """
        samples: list[DialPosition] = []
        for _ in range(n_samples * 3):  # oversample and filter
            offset = self._rng.randn(3)
            offset = offset / max(np.linalg.norm(offset), 1e-6) * self._rng.uniform(0, radius)
            arr = position.to_array() + offset
            arr = np.clip(arr, 0.0, 5.0)
            samples.append(DialPosition.from_array(arr, tradition_name="Explorer"))

        # Sort by distance and take first n_samples
        samples.sort(key=lambda p: compute_dial_distance(position, p))
        return samples[:n_samples]

    def describe_neighbourhood(self, position: DialPosition, radius: float = 1.5) -> str:
        """Describe what musical traditions live near ``position``.

        Parameters
        ----------
        position : DialPosition
            Centre point to explore.
        radius : float
            Search radius.

        Returns
        -------
        str
            ASCII report of nearby traditions.
        """
        lines: list[str] = []
        lines.append(f"Exploring neighbourhood around ({position.harmonic_tension:.1f}, "
                     f"{position.rhythmic_complexity:.1f}, {position.spectral_density:.1f})")
        lines.append(f"Search radius: {radius:.1f}")
        lines.append("")

        found = []
        for name, profile in DIAL_RANGES.items():
            centre = DialPosition.from_array(profile["center"], tradition_name=name)
            dist = compute_dial_distance(position, centre)
            if dist <= radius:
                found.append((dist, name, centre))

        if not found:
            lines.append("No known traditions in this zone. You are a pioneer!")
            # Suggest nearest
            nearest_name = min(
                DIAL_RANGES.keys(),
                key=lambda n: compute_dial_distance(
                    position,
                    DialPosition.from_array(DIAL_RANGES[n]["center"]),
                ),
            )
            d = compute_dial_distance(
                position,
                DialPosition.from_array(DIAL_RANGES[nearest_name]["center"]),
            )
            lines.append(f"Nearest known tradition: {nearest_name} (distance {d:.2f})")
        else:
            lines.append("Known traditions nearby:")
            found.sort(key=lambda x: x[0])
            for dist, name, centre in found:
                bar = "█" * max(1, int((radius - dist) / radius * 20))
                lines.append(
                    f"  {name:<22} │{bar:<20s}│ d={dist:.2f}  "
                    f"({centre.harmonic_tension:.1f}, {centre.rhythmic_complexity:.1f}, {centre.spectral_density:.1f})"
                )

        return "\n".join(lines)
