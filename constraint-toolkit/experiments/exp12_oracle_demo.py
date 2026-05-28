"""
Experiment 12: Dial Oracle Demo.

Puts the snarky DialOracle through its paces on random dial positions,
known traditions, and deliberately absurd blends.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from constraint_toolkit.oracle import DialOracle
from constraint_toolkit.dials import DialPosition, DIAL_RANGES


def main():
    print("\n=== Experiment 12: Dial Oracle Demo ===\n")

    oracle = DialOracle(seed=1337)
    rng = np.random.RandomState(42)

    # --- what_tradition_am_i ---
    print("--- what_tradition_am_i ---")
    for name, profile in DIAL_RANGES.items():
        pos = DialPosition.from_array(profile["center"], tradition_name=name)
        print(f"\n{name}:")
        print(f"  {oracle.what_tradition_am_i(pos)}")

    # Mystery position
    mystery = DialPosition(harmonic_tension=0.5, rhythmic_complexity=4.8, spectral_density=4.9)
    print(f"\nMystery position (0.5, 4.8, 4.9):")
    print(f"  {oracle.what_tradition_am_i(mystery)}")

    # --- will_these_blend ---
    print("\n--- will_these_blend ---")
    pairs = [
        ("Jazz", "Blues"),
        ("Classical", "EDM"),
        ("Gagaku", "African Polyrhythm"),
        ("Hip-hop", "Latin"),
    ]
    for a_name, b_name in pairs:
        a = DialPosition.from_array(DIAL_RANGES[a_name]["center"])
        b = DialPosition.from_array(DIAL_RANGES[b_name]["center"])
        print(f"\n{a_name} + {b_name}:")
        print(f"  {oracle.will_these_blend(a, b)}")

    # --- rate_my_groove ---
    print("\n--- rate_my_groove ---")
    test_positions = [
        DialPosition(1.0, 1.0, 1.0, tradition_name="Sparse"),
        DialPosition(4.5, 4.5, 4.5, tradition_name="Dense"),
        DialPosition(2.5, 3.5, 3.0, tradition_name="Balanced"),
    ]
    for pos in test_positions:
        print(f"\nPosition ({pos.harmonic_tension}, {pos.rhythmic_complexity}, {pos.spectral_density}):")
        print(f"  {oracle.rate_my_groove(pos)}")

    print("\n=== Oracle Demo Complete ===")


if __name__ == "__main__":
    main()
