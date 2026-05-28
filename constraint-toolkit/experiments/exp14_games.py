"""
Experiment 14: Musical Games.

Demonstrates DialGuesser, TraditionBattles, and DialExplorer with
interactive-style output.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from constraint_toolkit.games import DialGuesser, TraditionBattles, DialExplorer
from constraint_toolkit.dials import DialPosition, DIAL_RANGES


def main():
    print("\n=== Experiment 14: Musical Games ===\n")

    # --- DialGuesser ---
    print("--- DialGuesser ---")
    guesser = DialGuesser(seed=99)
    print(guesser.new_game())
    print()
    # Simulate a few guesses
    print(guesser.guess("EDM"))
    print()
    print(guesser.guess("Jazz"))
    print()
    # Start another round and solve it
    print(guesser.new_game())
    print()
    # Brute-force solve by using all hints
    print(guesser.guess("Classical"))
    print()
    print(guesser.guess("Classical"))
    print()
    print(guesser.guess("Classical"))
    print()
    print(guesser.guess("Classical"))
    print()
    print(guesser.guess("Classical"))
    print()

    # --- TraditionBattles ---
    print("--- TraditionBattles ---")
    arena = TraditionBattles()
    print(arena.fight("Jazz", "Classical"))
    print()
    print(arena.fight("EDM", "African Polyrhythm"))
    print()
    print(arena.matchup_chart())
    print()

    # --- DialExplorer ---
    print("--- DialExplorer ---")
    explorer = DialExplorer(seed=77)
    centre = DialPosition(harmonic_tension=2.5, rhythmic_complexity=3.5, spectral_density=3.0)
    print(explorer.describe_neighbourhood(centre, radius=1.5))
    print()

    nearby = explorer.nearby(centre, radius=0.8, n_samples=4)
    print("Sampled nearby positions:")
    for i, p in enumerate(nearby, 1):
        print(f"  {i}. ({p.harmonic_tension:.2f}, {p.rhythmic_complexity:.2f}, {p.spectral_density:.2f})")

    print("\n=== Games Complete ===")


if __name__ == "__main__":
    main()
