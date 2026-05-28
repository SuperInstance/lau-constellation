"""
Innovation cycle tracker for musical traditions.

Models the Discovery → Codification → Ubiquity → Boredom → Rebellion cycle
based on dial position clustering, spread analysis, and historical data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import numpy as np

from .dials import DIAL_RANGES, DialPosition


class CyclePhase(Enum):
    """Phases of the innovation cycle.

    Each phase represents a stage in how a musical tradition evolves
    through exploration and exploitation.
    """

    DISCOVERY = "Discovery"
    CODIFICATION = "Codification"
    UBIQUITY = "Ubiquity"
    BOREDOM = "Boredom"
    REBELLION = "Rebellion"

    @property
    def emoji(self) -> str:
        """Emoji representation of the phase."""
        emojis = {
            CyclePhase.DISCOVERY: "🔍",
            CyclePhase.CODIFICATION: "📜",
            CyclePhase.UBIQUITY: "🌍",
            CyclePhase.BOREDOM: "😴",
            CyclePhase.REBELLION: "🔥",
        }
        return emojis.get(self, "❓")

    @property
    def description(self) -> str:
        """Human-readable description of the phase."""
        descriptions = {
            CyclePhase.DISCOVERY: "Still being explored, new sounds emerging",
            CyclePhase.CODIFICATION: "Rules and conventions forming",
            CyclePhase.UBIQUITY: "Widely adopted, mainstream presence",
            CyclePhase.BOREDOM: "Overused, predictable, ripe for change",
            CyclePhase.REBELLION: "Breaking conventions, new forms emerging",
        }
        return descriptions.get(self, "Unknown phase")


@dataclass
class PhaseScore:
    """Score for a tradition on each phase of the innovation cycle.

    Parameters
    ----------
    tradition : str
        Name of the tradition.
    discovery : float
        Discovery phase score [0, 1].
    codification : float
        Codification phase score [0, 1].
    ubiquity : float
        Ubiquity phase score [0, 1].
    boredom : float
        Boredom phase score [0, 1].
    rebellion : float
        Rebellion phase score [0, 1].
    dominant_phase : CyclePhase
        The phase with the highest score.
    """

    tradition: str
    discovery: float
    codification: float
    ubiquity: float
    boredom: float
    rebellion: float
    dominant_phase: CyclePhase

    @property
    def scores(self) -> dict[str, float]:
        """Return all scores as a dict."""
        return {
            "discovery": self.discovery,
            "codification": self.codification,
            "ubiquity": self.ubiquity,
            "boredom": self.boredom,
            "rebellion": self.rebellion,
        }

    @property
    def dominant_score(self) -> float:
        """Return the score of the dominant phase."""
        return self.scores[self.dominant_phase.name.lower()]


# Historical annotations for traditions
HISTORICAL_PHASES: dict[str, CyclePhase] = {
    "EDM": CyclePhase.BOREDOM,
    "Hip-hop": CyclePhase.UBIQUITY,
    "Gamelan": CyclePhase.DISCOVERY,
    "Gagaku": CyclePhase.DISCOVERY,
    "Jazz": CyclePhase.REBELLION,
    "Classical": CyclePhase.CODIFICATION,
    "Blues": CyclePhase.CODIFICATION,
    "Hindustani": CyclePhase.CODIFICATION,
    "African Polyrhythm": CyclePhase.DISCOVERY,
    "Latin": CyclePhase.UBIQUITY,
}


def _compute_phase_scores(
    center: np.ndarray,
    spread: np.ndarray,
    historical_phase: Optional[CyclePhase] = None,
) -> tuple[float, float, float, float, float, CyclePhase]:
    """Compute innovation cycle phase scores from dial profile.

    Scoring heuristics:
    - Discovery: high spread, low center magnitude → still being explored
    - Codification: medium spread, established center → rules forming
    - Ubiquity: tight spread, popular center → widely used
    - Boredom: very tight spread → overused
    - Rebellion: spread expanding, center shifting → new forms emerging

    Parameters
    ----------
    center : ndarray
        Center position [H, R, S].
    spread : ndarray
        Spread [σ_H, σ_R, σ_S].
    historical_phase : CyclePhase or None
        Known historical phase for calibration.

    Returns
    -------
    tuple of (discovery, codification, ubiquity, boredom, rebellion, dominant)
    """
    mean_spread = float(np.mean(spread))
    mean_center = float(np.mean(center))
    spread_range = float(np.max(spread) - np.min(spread))

    # Discovery: high spread means still exploring
    discovery = np.clip(mean_spread / 0.6, 0, 1)
    # Also boost if tradition is in less-charted territory
    discovery *= 1.0 + 0.3 * np.clip(1.0 - mean_center / 5.0, 0, 1)

    # Codification: medium spread, established center
    codification = np.clip(1.0 - abs(mean_spread - 0.45) / 0.3, 0, 1)
    codification *= np.clip(mean_center / 3.0, 0.3, 1.0)

    # Ubiquity: tight spread, moderate-high center values
    ubiquity = np.clip(1.0 - mean_spread / 0.5, 0, 1)
    ubiquity *= np.clip(mean_center / 3.5, 0.3, 1.0)

    # Boredom: very tight spread (over-constrained)
    boredom = np.clip(1.0 - mean_spread / 0.35, 0, 1)

    # Rebellion: wide spread range (asymmetric exploration)
    rebellion = np.clip(spread_range / 0.3, 0, 1)
    # Also high if center is at extremes
    rebellion *= 1.0 + 0.3 * np.clip(abs(mean_center - 2.5) / 2.5, 0, 1)

    # Normalize so they don't all sum to >1
    total = discovery + codification + ubiquity + boredom + rebellion
    if total > 0:
        discovery /= total
        codification /= total
        ubiquity /= total
        boredom /= total
        rebellion /= total

    # Historical phase boost
    if historical_phase is not None:
        phase_map = {
            CyclePhase.DISCOVERY: discovery,
            CyclePhase.CODIFICATION: codification,
            CyclePhase.UBIQUITY: ubiquity,
            CyclePhase.BOREDOM: boredom,
            CyclePhase.REBELLION: rebellion,
        }
        target = phase_map[historical_phase]
        # Boost the historical phase by 30%
        phase_map[historical_phase] = target * 1.3
        # Renormalize
        total = sum(phase_map.values())
        if total > 0:
            discovery = phase_map[CyclePhase.DISCOVERY] / total
            codification = phase_map[CyclePhase.CODIFICATION] / total
            ubiquity = phase_map[CyclePhase.UBIQUITY] / total
            boredom = phase_map[CyclePhase.BOREDOM] / total
            rebellion = phase_map[CyclePhase.REBELLION] / total

    # Determine dominant phase
    scores = {
        CyclePhase.DISCOVERY: discovery,
        CyclePhase.CODIFICATION: codification,
        CyclePhase.UBIQUITY: ubiquity,
        CyclePhase.BOREDOM: boredom,
        CyclePhase.REBELLION: rebellion,
    }
    dominant = max(scores, key=scores.get)  # type: ignore[arg-type]

    return discovery, codification, ubiquity, boredom, rebellion, dominant


class InnovationTracker:
    """Track where traditions sit in the innovation cycle.

    The innovation cycle models how musical traditions evolve:
    Discovery → Codification → Ubiquity → Boredom → Rebellion → Discovery

    Each tradition is scored on all five phases based on its dial position,
    spread, and historical context.
    """

    def analyze_tradition(self, tradition: str) -> PhaseScore:
        """Determine what phase a tradition is in.

        Parameters
        ----------
        tradition : str
            Name of the tradition (must be in DIAL_RANGES).

        Returns
        -------
        PhaseScore
            Scored phases for the tradition.

        Raises
        ------
        ValueError
            If tradition is unknown.
        """
        if tradition not in DIAL_RANGES:
            raise ValueError(
                f"Unknown tradition '{tradition}'. "
                f"Available: {list(DIAL_RANGES.keys())}"
            )

        profile = DIAL_RANGES[tradition]
        center = profile["center"]
        spread = profile["spread"]
        historical = HISTORICAL_PHASES.get(tradition)

        disc, codif, ubiq, bored, rebel, dominant = _compute_phase_scores(
            center, spread, historical
        )

        return PhaseScore(
            tradition=tradition,
            discovery=disc,
            codification=codif,
            ubiquity=ubiq,
            boredom=bored,
            rebellion=rebel,
            dominant_phase=dominant,
        )

    def predict_next_phase(self, tradition: str) -> dict:
        """Predict when and how a tradition will transition.

        Based on current phase scores and the innovation cycle direction.

        Parameters
        ----------
        tradition : str
            Tradition name.

        Returns
        -------
        dict with keys:
            - current_phase: str
            - next_phase: str
            - transition_readiness: float (0-1, how ready for transition)
            - predicted_direction: str (description of expected change)
        """
        if tradition not in DIAL_RANGES:
            raise ValueError(f"Unknown tradition: {tradition}")

        score = self.analyze_tradition(tradition)

        # Cycle order: Discovery → Codification → Ubiquity → Boredom → Rebellion
        cycle = [
            CyclePhase.DISCOVERY,
            CyclePhase.CODIFICATION,
            CyclePhase.UBIQUITY,
            CyclePhase.BOREDOM,
            CyclePhase.REBELLION,
        ]

        current_idx = cycle.index(score.dominant_phase)
        next_idx = (current_idx + 1) % len(cycle)
        next_phase = cycle[next_idx]

        # Transition readiness: how close the next phase score is to current
        next_score = score.scores[next_phase.name.lower()]
        current_score = score.dominant_score
        readiness = next_score / max(current_score, 0.01)
        readiness = float(np.clip(readiness, 0, 1))

        # Predicted direction in dial space
        center = DIAL_RANGES[tradition]["center"]
        spread = DIAL_RANGES[tradition]["spread"]

        directions = {
            CyclePhase.DISCOVERY: "Expanding range, exploring new territory",
            CyclePhase.CODIFICATION: "Converging on core patterns, establishing rules",
            CyclePhase.UBIQUITY: "Standardizing, losing distinctive features",
            CyclePhase.BOREDOM: "Constraining further, audience fatigue growing",
            CyclePhase.REBELLION: "Breaking conventions, seeking novelty",
        }

        return {
            "tradition": tradition,
            "current_phase": score.dominant_phase.value,
            "current_score": current_score,
            "next_phase": next_phase.value,
            "next_score": next_score,
            "transition_readiness": readiness,
            "predicted_direction": directions[next_phase],
            "dial_center": center.tolist(),
            "dial_spread": spread.tolist(),
        }

    def map_all_traditions(self) -> dict[str, PhaseScore]:
        """Map all traditions to their cycle phases.

        Returns
        -------
        dict mapping tradition name to PhaseScore.
        """
        return {
            name: self.analyze_tradition(name) for name in DIAL_RANGES
        }

    def format_cycle_chart(self) -> str:
        """Generate an ASCII art visualization of the innovation cycle.

        Returns
        -------
        str
            ASCII art cycle chart.
        """
        mapping = self.map_all_traditions()

        lines = [
            "",
            "  ╔══════════════════════════════════════════════════════╗",
            "  ║          INNOVATION CYCLE — TRADITION MAP           ║",
            " ╔╝                                                      ╚╗",
            f" ║  🔍 Discovery        📜 Codification       🌍 Ubiquity ║",
        ]

        # Group traditions by phase
        by_phase: dict[CyclePhase, list[str]] = {}
        for name, score in mapping.items():
            by_phase.setdefault(score.dominant_phase, []).append(
                f"{name} ({score.dominant_score:.0%})"
            )

        for phase in [
            CyclePhase.DISCOVERY,
            CyclePhase.CODIFICATION,
            CyclePhase.UBIQUITY,
            CyclePhase.BOREDOM,
            CyclePhase.REBELLION,
        ]:
            traditions = by_phase.get(phase, [])
            if traditions:
                line = f" ║   {phase.emoji} {phase.value:<14s}: {', '.join(traditions)}"
            else:
                line = f" ║   {phase.emoji} {phase.value:<14s}: (none)"
            lines.append(line)

        lines.append(" ║                                                        ║")
        lines.append(" ║  Cycle: Discovery → Codification → Ubiquity            ║")
        lines.append(" ║         → Boredom → Rebellion → Discovery              ║")
        lines.append(" ╚══════════════════════════════════════════════════════════╝")

        return "\n".join(lines)

    def find_rebellion_candidates(self) -> list[dict]:
        """Identify traditions ripe for rebellion/innovation.

        Returns traditions that are in the Boredom or late-Ubiquity phase
        and have high rebellion scores.

        Returns
        -------
        list of dict with keys:
            - tradition: str
            - phase: str
            - boredom_score: float
            - rebellion_score: float
            - readiness: float
        """
        mapping = self.map_all_traditions()
        candidates = []

        for name, score in mapping.items():
            # High boredom + rising rebellion = ripe for change
            if score.boredom > 0.15 or (
                score.ubiquity > 0.2 and score.rebellion > 0.15
            ):
                readiness = score.boredom * 0.5 + score.rebellion * 0.5
                candidates.append(
                    {
                        "tradition": name,
                        "phase": score.dominant_phase.value,
                        "boredom_score": score.boredom,
                        "rebellion_score": score.rebellion,
                        "readiness": readiness,
                    }
                )

        candidates.sort(key=lambda x: x["readiness"], reverse=True)
        return candidates
