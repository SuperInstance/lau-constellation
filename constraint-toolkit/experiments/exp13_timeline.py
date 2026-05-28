"""
Experiment 13: Musical Timeline.

Renders the full ASCII timeline, looks up specific years, and prints the
2030 speculative forecast.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from constraint_toolkit.timeline import MusicalTimeline


def main():
    print("\n=== Experiment 13: Musical Timeline ===\n")

    timeline = MusicalTimeline(width=80)

    # Full plot
    print(timeline.plot_history())
    print("\n")

    # Look up specific years
    years = [1420, 1605, 1967, 1992, 2018]
    print("--- what_was_happening ---")
    for year in years:
        print(f"\n{timeline.what_was_happening(year)}")

    # 2030 forecast
    print("\n" + "=" * 60)
    print(timeline.predict_2030())
    print("=" * 60)


if __name__ == "__main__":
    main()
