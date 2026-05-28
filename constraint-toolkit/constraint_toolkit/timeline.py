"""
Musical Timeline.

Hard-coded historical data from Ars Subtilior (~1400) to AI Music (~2020)
with ASCII-art visualisation, year lookup, and speculative 2030 prediction.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from .dials import DialPosition, DIAL_RANGES


# Hard-coded historical milestones
_TIMELINE_DATA: list[dict] = [
    {"year": 1400, "era": "Ars Subtilior", "dial": (3.8, 3.5, 2.0), "blurb": "Rhythmic puzzles so complex monks needed flowcharts."},
    {"year": 1450, "era": "Renaissance Polyphony", "dial": (2.5, 2.0, 2.5), "blurb": "Josquin makes counterpoint sound easy. It isn't."},
    {"year": 1600, "era": "Baroque", "dial": (3.0, 2.5, 2.5), "blurb": "Bach arrives. Music schools cry tears of joy for centuries."},
    {"year": 1750, "era": "Classical", "dial": (2.0, 2.0, 2.5), "blurb": "Mozart writes symphonies in his sleep. You can't even finish a to-do list."},
    {"year": 1820, "era": "Romantic", "dial": (3.5, 2.5, 3.5), "blurb": "Feelings. All of them. At once. With a full orchestra."},
    {"year": 1900, "era": "Early Jazz", "dial": (3.5, 3.5, 2.5), "blurb": "New Orleans accidentally invents cool."},
    {"year": 1920, "era": "Swing Era", "dial": (3.0, 3.0, 3.0), "blurb": "Big bands, bigger suits, biggest dance floors."},
    {"year": 1945, "era": "Bebop", "dial": (4.0, 4.5, 2.5), "blurb": "Charlie Parker plays so fast physics files a complaint."},
    {"year": 1955, "era": "Rock 'n' Roll", "dial": (2.5, 3.0, 3.5), "blurb": "Teenagers discover distortion. Parents discover fear."},
    {"year": 1965, "era": "Psychedelic", "dial": (3.0, 3.0, 4.5), "blurb": "Colours now have sounds. Sounds now have colours."},
    {"year": 1970, "era": "Funk", "dial": (2.5, 4.0, 3.5), "blurb": "The One. If you don't know where it is, you're already lost."},
    {"year": 1975, "era": "Disco", "dial": (2.0, 3.5, 4.0), "blurb": "Four-on-the-floor forever. Resistance is futile."},
    {"year": 1980, "era": "Post-Punk", "dial": (3.0, 3.5, 4.0), "blurb": "Angst with better hair products."},
    {"year": 1985, "era": "Hip-hop", "dial": (1.5, 3.5, 3.5), "blurb": "Two turntables and a microphone rewrite history."},
    {"year": 1988, "era": "House", "dial": (1.5, 3.0, 4.5), "blurb": "Chicago warehouses become churches of four-on-the-floor."},
    {"year": 1990, "era": "Techno", "dial": (1.0, 3.5, 4.5), "blurb": "Detroit exports the future. Berlin buys it in bulk."},
    {"year": 1995, "era": "Drum & Bass", "dial": (2.0, 4.5, 4.0), "blurb": "Breakbeats at 170 BPM. Heart rates sold separately."},
    {"year": 2000, "era": "Nu-Metal", "dial": (3.0, 3.5, 4.5), "blurb": "Rap and metal hold hands. Purists hold their noses."},
    {"year": 2005, "era": "Blog-House", "dial": (2.0, 3.0, 4.5), "blurb": "Indie kids discover Ableton. Blogs discover hype."},
    {"year": 2010, "era": "Dubstep", "dial": (2.0, 3.5, 4.5), "blurb": "WUB WUB WUB. That's the whole review."},
    {"year": 2015, "era": "Trap", "dial": (1.5, 3.5, 4.5), "blurb": "Hi-hats roll like dice. 808s shake foundations."},
    {"year": 2020, "era": "AI Music", "dial": (2.5, 3.0, 4.0), "blurb": "Neural nets learn Bach. Bach's ghost is mildly amused."},
]


class MusicalTimeline:
    """Interactive musical history from Ars Subtilior to AI.

    Parameters
    ----------
    width : int
        Width of the ASCII timeline in characters.
    """

    def __init__(self, width: int = 80) -> None:
        self.width = width
        self._data = _TIMELINE_DATA

    def _find_entry(self, year: int) -> Optional[dict]:
        """Return the timeline entry closest to ``year``."""
        if not self._data:
            return None
        best = self._data[0]
        best_diff = abs(best["year"] - year)
        for entry in self._data[1:]:
            diff = abs(entry["year"] - year)
            if diff < best_diff:
                best_diff = diff
                best = entry
        return best

    def plot_history(self, highlight_year: Optional[int] = None) -> str:
        """Render an ASCII-art timeline of musical history.

        Parameters
        ----------
        highlight_year : int or None
            If provided, highlights the closest era.

        Returns
        -------
        str
            ASCII timeline.
        """
        lines: list[str] = []
        lines.append("=" * self.width)
        lines.append("MUSICAL HISTORY — Dials Not Laws".center(self.width))
        lines.append("=" * self.width)

        min_year = self._data[0]["year"]
        max_year = self._data[-1]["year"]
        year_range = max_year - min_year if max_year != min_year else 1

        for entry in self._data:
            year = entry["year"]
            era = entry["era"]
            blurb = entry["blurb"]
            dial = entry["dial"]

            # Position on timeline bar
            pos = int((year - min_year) / year_range * (self.width - 20))
            bar = " " * pos + "●"

            is_highlight = highlight_year is not None and self._find_entry(highlight_year) == entry
            marker = ">>> " if is_highlight else "    "

            lines.append("")
            lines.append(f"{marker}{year} — {era}")
            lines.append(f"     Dial (H,R,S): {dial[0]:.1f}, {dial[1]:.1f}, {dial[2]:.1f}")
            lines.append(f"     {bar}")
            lines.append(f"     '{blurb}'")

        lines.append("")
        lines.append("=" * self.width)
        return "\n".join(lines)

    def what_was_happening(self, year: int) -> str:
        """Describe the musical landscape closest to ``year``.

        Parameters
        ----------
        year : int
            The year to look up.

        Returns
        -------
        str
            A human-readable description.
        """
        entry = self._find_entry(year)
        if entry is None:
            return "History hasn't been invented yet."

        diff = year - entry["year"]
        tense = "was" if diff >= 0 else "would be"
        when = f"{abs(diff)} years {'later' if diff >= 0 else 'earlier'}"

        return (
            f"In {year} ({when}), the dominant force {tense} **{entry['era']}**.\n"
            f"Dial position: ({entry['dial'][0]:.1f}, {entry['dial'][1]:.1f}, {entry['dial'][2]:.1f}).\n"
            f"'{entry['blurb']}'"
        )

    def predict_2030(self) -> str:
        """Speculate on the musical landscape of 2030.

        Uses a naïve linear extrapolation of the last three dial positions.

        Returns
        -------
        str
            A speculative report.
        """
        if len(self._data) < 3:
            return "Not enough history to predict the future. Try again in a century."

        recent = self._data[-3:]
        dials = np.array([e["dial"] for e in recent], dtype=np.float64)
        # Linear trend per decade
        decades = np.array([e["year"] for e in recent], dtype=np.float64) / 10.0
        slopes = np.array([
            np.polyfit(decades, dials[:, i], 1)[0]
            for i in range(3)
        ], dtype=np.float64)

        last_decade = recent[-1]["year"] / 10.0
        target_decade = 2030 / 10.0
        delta_decades = target_decade - last_decade
        predicted = dials[-1] + slopes * delta_decades
        predicted = np.clip(predicted, 0.0, 5.0)

        h, r, s = predicted

        # Determine flavour from predicted position
        closest = "Unknown"
        min_dist = float("inf")
        for name, profile in DIAL_RANGES.items():
            dist = float(np.linalg.norm(predicted - profile["center"]))
            if dist < min_dist:
                min_dist = dist
                closest = name

        verdicts = [
            "By 2030, AI-generated hyper-genres will mutate every 17 seconds.",
            "Humans will become the 'vintage' filter on streaming platforms.",
            "The most popular instrument will be the 'thought keyboard'.",
            "Music will be so personalised no two people hear the same song.",
        ]

        report = (
            f"=== 2030 Musical Forecast ===\n"
            f"Predicted dial position: ({h:.2f}, {r:.2f}, {s:.2f})\n"
            f"Closest known tradition: {closest}\n"
            f"Trend direction per decade: H={slopes[0]:+.2f}, R={slopes[1]:+.2f}, S={slopes[2]:+.2f}\n"
            f"\n"
            f"Speculative verdict:\n"
            f"  {np.random.RandomState(2030).choice(verdicts)}\n"
            f"  (Disclaimer: the Oracle is not responsible for tonal shifts caused by"
            f" solar flares or retrograde Mercury.)"
        )
        return report
