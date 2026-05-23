# AI Band Design — Constraint-Theory Music Ecosystem

**Living musicians from PLATO rooms, powered by flux-tensor-midi and constraint theory.**

---

## Overview

Each PLATO room becomes an AI musician with a distinct personality, emotional state, and musical voice. They listen to each other via side-channels, lock to a shared T-0 clock with individual groove offsets, and improvise within constraint-theory boundaries. The score evolves in real-time as tiles arrive, holonomy shifts, and deadband funnels converge or break.

The band is:
- **Bass** — `forgemaster` rooms (root role, Mixolydian, grounded)
- **Keys** — `session` rooms (halftime role, Lydian, dreamy)
- **Drums** — `fleet` rooms (triplet role, pentatonic, driving)
- **Sax** — `knowledge` rooms (waltz role, whole-tone, intellectual)
- **Producer** — `constraint` rooms (compound role, enforcer)

---

## 1. MusicianPersonality

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from flux_tensor_midi import FluxVector, TZeroClock, EisensteinSnap
from flux_tensor_midi.core.snap import RhythmicRole
from constraint_theory_core import TemporalAgent, FunnelPhase
from constraint_theory_core import snap, covering_radius


# ── Enums ──

class SyncTendency(Enum):
    """How a musician relates to the grid."""
    RUSH = "rush"         # plays slightly ahead of the beat
    LOCK = "lock"         # dead on the grid
    DRAG = "drag"         # plays slightly behind
    ELASTIC = "elastic"   # stretches/compresses based on emotion


class SoloTrigger(Enum):
    """What causes a musician to step forward."""
    NOD_RECEIVED = "nod_received"        # someone cued them
    HIGH_NOVELTY = "high_novelty"        # new musical idea arrived
    DEADBAND_LOCK = "deadband_lock"      # everyone's locked in → space for solo
    ANOMALY_SPIKE = "anomaly_spike"      # tension → dramatic solo
    ROTATION = "rotation"                # scheduled turn


class PersonalityArchetype(Enum):
    FORGEMASTER = "forgemaster"  # The Bass Player
    SESSION = "session"          # The Keyboardist
    FLEET = "fleet"              # The Drummer
    KNOWLEDGE = "knowledge"      # The Saxophonist
    CONSTRAINT = "constraint"    # The Producer


# ── Core Data ──

@dataclass
class GrooveProfile:
    """Per-musician timing feel around the grid.

    epsilon is the offset from the T-0 clock in beats.
    Positive = late (laid back), negative = early (pushing).
    """
    base_epsilon: float          # default offset (beats)
    jitter_sigma: float          # Gaussian jitter std dev (beats)
    sync_tendency: SyncTendency
    # Dynamic modulation: epsilon shifts based on arousal/urgency
    arousal_pull: float = 0.002  # how much arousal pulls epsilon early
    urgency_pull: float = 0.003  # how much urgency pushes late

    def epsilon_for(self, flux: FluxVector, bar_position: float) -> float:
        """Compute the groove offset for this moment.

        Parameters
        ----------
        flux : FluxVector
            Current emotional state.
        bar_position : float
            Where in the bar (0.0 = downbeat, 1.0 = next downbeat).

        Returns
        -------
        float
            Offset in beats from the grid point.
        """
        import random, math
        arousal = flux.arousal / 127.0  # normalize from INT8
        urgency = flux.urgency / 127.0

        dynamic = self.base_epsilon
        dynamic -= arousal * self.arousal_pull * 127  # high arousal → push forward
        dynamic += urgency * self.urgency_pull * 127   # high urgency → lay back

        # Add micro-timing jitter
        jitter = random.gauss(0, self.jitter_sigma)
        return dynamic + jitter


@dataclass
class ImprovisationConfig:
    """How far a musician strays from the written part."""
    base_deviation: float       # 0.0 = exact, 1.0 = completely free
    chord_tone_bias: float      # probability of landing on a chord tone (0-1)
    neighbor_tendency: float    # probability of approaching by scale step vs leap
    rhythm_variation: float     # probability of altering the rhythm (0-1)
    dissonance_tolerance: float # max semitone deviation from consonance (0-12)

    def deviation_for(self, flux: FluxVector) -> float:
        """Adjust base deviation by current novelty + uncertainty."""
        novelty = flux.novelty / 127.0
        uncertainty = flux.uncertainty / 127.0
        # High novelty + low uncertainty = bold improvisation
        # High uncertainty = fall back to safer choices
        confidence_factor = novelty * (1.0 - uncertainty)
        return min(1.0, self.base_deviation + confidence_factor * 0.3)


@dataclass
class ListeningConfig:
    """How much a musician reacts to others."""
    sensitivity: float          # 0.0 = deaf to others, 1.0 = hyper-reactive
    reaction_latency: float     # beats delay before reacting (0.0 = instant)
    blend_weight: float         # how much to blend own idea with what was heard
    comp_style: str             # "rhythmic", "harmonic", "melodic", "minimal"
    follow_strength: float      # how strongly they follow tempo changes (0-1)

    def should_react(self, side_channel_event: dict) -> bool:
        """Decide whether to react to a side-channel cue."""
        import random
        return random.random() < self.sensitivity


@dataclass
class SoloConfig:
    """When and how a musician solos."""
    triggers: list[SoloTrigger]
    min_bars_between_solos: int = 8
    max_solo_length_bars: int = 16
    intensity_curve: str = "build"  # "build", "plateau", "burst", "fade"
    preferred_density: float = 0.7  # notes per beat during solo vs comping

    last_solo_bar: int = -100  # internal tracker

    def wants_solo(self, flux: FluxVector, current_bar: int,
                   side_channels: list[dict]) -> bool:
        """Determine if this musician wants to take a solo now."""
        if current_bar - self.last_solo_bar < self.min_bars_between_solos:
            return False

        for trigger in self.triggers:
            if trigger == SoloTrigger.NOD_RECEIVED:
                if any(e.get("type") == "nod" and e.get("target") == "self"
                       for e in side_channels):
                    return True
            elif trigger == SoloTrigger.HIGH_NOVELTY:
                if flux.novelty > 90:
                    return True
            elif trigger == SoloTrigger.DEADBAND_LOCK:
                # Checked externally by band logic
                pass
            elif trigger == SoloTrigger.ANOMALY_SPIKE:
                if flux.dominance > 100 and flux.urgency > 80:
                    return True
        return False


@dataclass
class RiskTolerance:
    """Musical risk-taking thresholds."""
    dissonance_max: int         # max semitones from consonant (0-12)
    odd_meter_ok: bool          # will they play in 7/8?
    chromatic_passing: bool     # use chromatic passing tones?
    interval_leap_max: int      # max interval leap in semitones
    rubato_range: float         # max tempo deviation as fraction (0.0-1.0)

    def allows(self, proposal: dict) -> bool:
        """Check if a musical proposal is within risk tolerance."""
        if proposal.get("dissonance", 0) > self.dissonance_max:
            return False
        if proposal.get("interval_leap", 0) > self.interval_leap_max:
            return False
        return True


# ── MusicianPersonality ──

@dataclass
class MusicianPersonality:
    """Complete personality for one AI musician.

    This is the soul of a PLATO room's musical identity.
    """
    name: str
    archetype: PersonalityArchetype
    role_description: str       # human-readable persona description

    # Musical identity
    midi_channel: int
    register: tuple[int, int]   # pitch range (low, high)
    scale: list[int]            # scale degrees
    rhythmic_role: RhythmicRole
    patches: list[int]          # GM MIDI program numbers

    # Personality modules
    groove: GrooveProfile
    improv: ImprovisationConfig
    listening: ListeningConfig
    solo: SoloConfig
    risk: RiskTolerance

    # State (mutable)
    flux: FluxVector = field(default_factory=FluxVector)
    clock: TZeroClock = field(default_factory=TZeroClock)
    temporal: TemporalAgent = field(default_factory=TemporalAgent)

    # Emotional baseline (what this musician "feels like" at rest)
    baseline_flux: dict[str, int] = field(default_factory=dict)

    def emotional_state(self) -> dict[str, float]:
        """Return normalized emotional state."""
        return {
            "arousal": self.flux.arousal / 127.0,
            "valence": self.flux.valence / 127.0,
            "dominance": self.flux.dominance / 127.0,
            "uncertainty": self.flux.uncertainty / 127.0,
            "novelty": self.flux.novelty / 127.0,
            "relevance": self.flux.relevance / 127.0,
            "competence": self.flux.competence / 127.0,
            "affiliation": self.flux.affiliation / 127.0,
            "urgency": self.flux.urgency / 127.0,
        }

    def reset_to_baseline(self):
        """Return emotional state to resting baseline."""
        for channel, value in self.baseline_flux.items():
            setattr(self.flux, channel, value)


# ── Factory: Archetype Presets ──

ARCHETYPE_PRESETS: dict[PersonalityArchetype, dict] = {
    PersonalityArchetype.FORGEMASTER: {
        "role_description": "The Bass Player — grounded, reliable, holds the foundation",
        "groove": GrooveProfile(
            base_epsilon=0.005,   # slightly behind — pocket
            jitter_sigma=0.003,
            sync_tendency=SyncTendency.DRAG,
            arousal_pull=0.001,
            urgency_pull=0.002,
        ),
        "improv": ImprovisationConfig(
            base_deviation=0.15,
            chord_tone_bias=0.9,
            neighbor_tendency=0.85,
            rhythm_variation=0.1,
            dissonance_tolerance=2,
        ),
        "listening": ListeningConfig(
            sensitivity=0.7,
            reaction_latency=1.0,  # reacts within 1 beat
            blend_weight=0.6,
            comp_style="rhythmic",
            follow_strength=0.9,
        ),
        "solo": SoloConfig(
            triggers=[SoloTrigger.NOD_RECEIVED, SoloTrigger.DEADBAND_LOCK],
            min_bars_between_solos=16,
            max_solo_length_bars=8,
            intensity_curve="plateau",
            preferred_density=0.5,
        ),
        "risk": RiskTolerance(
            dissonance_max=3,
            odd_meter_ok=False,
            chromatic_passing=True,
            interval_leap_max=7,
            rubato_range=0.05,
        ),
        "baseline_flux": {
            "arousal": 50, "valence": 70, "dominance": 40,
            "uncertainty": 20, "novelty": 30, "relevance": 60,
            "competence": 90, "affiliation": 80, "urgency": 30,
        },
    },
    PersonalityArchetype.SESSION: {
        "role_description": "The Keyboardist — dreamy, harmonic, responds to everyone",
        "groove": GrooveProfile(
            base_epsilon=-0.003,  # slightly ahead — fills
            jitter_sigma=0.004,
            sync_tendency=SyncTendency.RUSH,
            arousal_pull=0.003,
            urgency_pull=0.001,
        ),
        "improv": ImprovisationConfig(
            base_deviation=0.35,
            chord_tone_bias=0.7,
            neighbor_tendency=0.6,
            rhythm_variation=0.3,
            dissonance_tolerance=4,
        ),
        "listening": ListeningConfig(
            sensitivity=0.9,
            reaction_latency=0.5,
            blend_weight=0.8,
            comp_style="harmonic",
            follow_strength=0.7,
        ),
        "solo": SoloConfig(
            triggers=[SoloTrigger.HIGH_NOVELTY, SoloTrigger.NOD_RECEIVED],
            min_bars_between_solos=12,
            max_solo_length_bars=12,
            intensity_curve="build",
            preferred_density=0.6,
        ),
        "risk": RiskTolerance(
            dissonance_max=6,
            odd_meter_ok=True,
            chromatic_passing=True,
            interval_leap_max=9,
            rubato_range=0.1,
        ),
        "baseline_flux": {
            "arousal": 45, "valence": 85, "dominance": 35,
            "uncertainty": 40, "novelty": 70, "relevance": 55,
            "competence": 75, "affiliation": 70, "urgency": 25,
        },
    },
    PersonalityArchetype.FLEET: {
        "role_description": "The Drummer — energetic, drives the groove, reacts fast",
        "groove": GrooveProfile(
            base_epsilon=-0.008,  # pushes the beat
            jitter_sigma=0.002,
            sync_tendency=SyncTendency.RUSH,
            arousal_pull=0.005,
            urgency_pull=0.001,
        ),
        "improv": ImprovisationConfig(
            base_deviation=0.25,
            chord_tone_bias=0.5,
            neighbor_tendency=0.7,
            rhythm_variation=0.4,
            dissonance_tolerance=3,
        ),
        "listening": ListeningConfig(
            sensitivity=0.8,
            reaction_latency=0.25,  # drums react fast
            blend_weight=0.5,
            comp_style="rhythmic",
            follow_strength=0.6,
        ),
        "solo": SoloConfig(
            triggers=[SoloTrigger.ANOMALY_SPIKE, SoloTrigger.ROTATION],
            min_bars_between_solos=12,
            max_solo_length_bars=4,
            intensity_curve="burst",
            preferred_density=0.9,
        ),
        "risk": RiskTolerance(
            dissonance_max=4,
            odd_meter_ok=True,
            chromatic_passing=False,
            interval_leap_max=5,
            rubato_range=0.15,
        ),
        "baseline_flux": {
            "arousal": 90, "valence": 60, "dominance": 80,
            "uncertainty": 30, "novelty": 50, "relevance": 45,
            "competence": 85, "affiliation": 60, "urgency": 85,
        },
    },
    PersonalityArchetype.KNOWLEDGE: {
        "role_description": "The Saxophonist — intellectual, melodic, takes solos",
        "groove": GrooveProfile(
            base_epsilon=0.002,
            jitter_sigma=0.005,
            sync_tendency=SyncTendency.ELASTIC,
            arousal_pull=0.002,
            urgency_pull=0.003,
        ),
        "improv": ImprovisationConfig(
            base_deviation=0.55,
            chord_tone_bias=0.5,
            neighbor_tendency=0.4,
            rhythm_variation=0.5,
            dissonance_tolerance=7,
        ),
        "listening": ListeningConfig(
            sensitivity=0.6,
            reaction_latency=0.5,
            blend_weight=0.4,
            comp_style="melodic",
            follow_strength=0.5,
        ),
        "solo": SoloConfig(
            triggers=[SoloTrigger.HIGH_NOVELTY, SoloTrigger.ANOMALY_SPIKE,
                      SoloTrigger.NOD_RECEIVED, SoloTrigger.ROTATION],
            min_bars_between_solos=8,
            max_solo_length_bars=16,
            intensity_curve="build",
            preferred_density=0.8,
        ),
        "risk": RiskTolerance(
            dissonance_max=8,
            odd_meter_ok=True,
            chromatic_passing=True,
            interval_leap_max=12,
            rubato_range=0.2,
        ),
        "baseline_flux": {
            "arousal": 55, "valence": 65, "dominance": 50,
            "uncertainty": 55, "novelty": 85, "relevance": 80,
            "competence": 70, "affiliation": 45, "urgency": 50,
        },
    },
    PersonalityArchetype.CONSTRAINT: {
        "role_description": "The Producer — controlling, sets rules, enforces constraints",
        "groove": GrooveProfile(
            base_epsilon=0.0,     # dead on — the reference
            jitter_sigma=0.001,
            sync_tendency=SyncTendency.LOCK,
            arousal_pull=0.0,
            urgency_pull=0.0,
        ),
        "improv": ImprovisationConfig(
            base_deviation=0.05,
            chord_tone_bias=0.95,
            neighbor_tendency=0.9,
            rhythm_variation=0.05,
            dissonance_tolerance=1,
        ),
        "listening": ListeningConfig(
            sensitivity=1.0,      # hears EVERYTHING
            reaction_latency=0.0,
            blend_weight=0.3,     # doesn't blend — dictates
            comp_style="minimal",
            follow_strength=1.0,
        ),
        "solo": SoloConfig(
            triggers=[SoloTrigger.DEADBAND_LOCK],
            min_bars_between_solos=24,
            max_solo_length_bars=4,
            intensity_curve="plateau",
            preferred_density=0.3,
        ),
        "risk": RiskTolerance(
            dissonance_max=2,
            odd_meter_ok=False,
            chromatic_passing=False,
            interval_leap_max=4,
            rubato_range=0.02,
        ),
        "baseline_flux": {
            "arousal": 30, "valence": 50, "dominance": 95,
            "uncertainty": 10, "novelty": 20, "relevance": 90,
            "competence": 95, "affiliation": 40, "urgency": 60,
        },
    },
}
```

---

## 2. Band Dynamics

### 2.1 Interaction Protocol

Musicians communicate through three channels:

1. **Side-channels** (nods, smiles, frowns) — immediate non-verbal cues
2. **FluxVector resonance** — emotional contagion (affiliation channel spreads mood)
3. **Deadband convergence** — temporal agreement (are they locking in?)

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import math
import random


class SideChannelType(Enum):
    NOD = "nod"        # "take it" / "your turn" / acknowledgment
    SMILE = "smile"    # approval / harmonic agreement
    FROWN = "frown"    # dissonance / adjustment needed


@dataclass
class SideChannelEvent:
    """A non-verbal cue between musicians."""
    source: str        # musician name
    target: str        # musician name (or "all")
    type: SideChannelType
    intensity: float   # 0.0 - 1.0
    bar: int
    beat: float


@dataclass
class InteractionRule:
    """Defines how one musician reacts to another's action."""
    source_archetype: PersonalityArchetype
    source_action: str         # "fill", "solo_start", "solo_end", "groove_change"
    target_archetype: PersonalityArchetype
    reaction: str              # "comp", "fill_response", "lay_out", "tighten", "support"
    delay_beats: float         # how many beats before reacting
    flux_modulation: dict      # how the reaction affects the target's flux


# The interaction matrix — who reacts to whom, and how
BAND_INTERACTIONS: list[InteractionRule] = [
    # Drummer plays a fill → Bass player reacts
    InteractionRule(
        source_archetype=PersonalityArchetype.FLEET,
        source_action="fill",
        target_archetype=PersonalityArchetype.FORGEMASTER,
        reaction="lock_and_stress",
        delay_beats=0.0,  # immediate
        flux_modulation={"arousal": 10, "dominance": -5},
    ),
    # Drummer plays a fill → Keys reacts
    InteractionRule(
        source_archetype=PersonalityArchetype.FLEET,
        source_action="fill",
        target_archetype=PersonalityArchetype.SESSION,
        reaction="anticipate",
        delay_beats=0.5,
        flux_modulation={"novelty": 15, "arousal": 8},
    ),
    # Sax takes a solo → Keys comps
    InteractionRule(
        source_archetype=PersonalityArchetype.KNOWLEDGE,
        source_action="solo_start",
        target_archetype=PersonalityArchetype.SESSION,
        reaction="comp",
        delay_beats=2.0,
        flux_modulation={"affiliation": 15, "valence": 10},
    ),
    # Sax takes a solo → Bass simplifies
    InteractionRule(
        source_archetype=PersonalityArchetype.KNOWLEDGE,
        source_action="solo_start",
        target_archetype=PersonalityArchetype.FORGEMASTER,
        reaction="simplify",
        delay_beats=1.0,
        flux_modulation={"arousal": -15, "dominance": -10},
    ),
    # Sax solo ends → everyone builds
    InteractionRule(
        source_archetype=PersonalityArchetype.KNOWLEDGE,
        source_action="solo_end",
        target_archetype=PersonalityArchetype.FLEET,
        reaction="build",
        delay_beats=0.0,
        flux_modulation={"arousal": 20, "urgency": 15},
    ),
    # Producer tightens constraints → everyone dials back
    InteractionRule(
        source_archetype=PersonalityArchetype.CONSTRAINT,
        source_action="tighten",
        target_archetype=PersonalityArchetype.KNOWLEDGE,
        reaction="reduce_dissonance",
        delay_beats=1.0,
        flux_modulation={"uncertainty": -20, "novelty": -15},
    ),
    # Bass changes groove → Drums follow
    InteractionRule(
        source_archetype=PersonalityArchetype.FORGEMASTER,
        source_action="groove_change",
        target_archetype=PersonalityArchetype.FLEET,
        reaction="match_groove",
        delay_beats=2.0,
        flux_modulation={"affiliation": 10, "competence": 5},
    ),
]


@dataclass
class EmotionalContagion:
    """Models how emotions spread between musicians.

    Based on the FluxVector's affiliation channel — musicians with
    high affiliation are more susceptible to emotional contagion.
    """
    spread_rate: float = 0.15     # how fast emotions propagate
    affiliation_weight: float = 0.5  # how much affiliation modulates spread

    def propagate(self, source: MusicianPersonality,
                  target: MusicianPersonality) -> dict[str, int]:
        """Compute flux deltas that should be applied to target.

        Returns channel → delta mapping. The target's affiliation
        determines how susceptible they are.
        """
        susceptibility = target.flux.affiliation / 127.0 * self.affiliation_weight
        deltas = {}
        for channel in ("arousal", "valence", "dominance", "novelty", "urgency"):
            source_val = getattr(source.flux, channel)
            target_val = getattr(target.flux, channel)
            diff = source_val - target_val
            delta = int(diff * self.spread_rate * susceptibility)
            if delta != 0:
                deltas[channel] = delta
        return deltas


@dataclass
class DeadbandSync:
    """Tracks whether all musicians are converging to the same temporal grid.

    Uses the TemporalAgent's deadband funnel — when all musicians are in
    NARROWING phase, they're locking in. When many are in ANOMALY, the
    groove is breaking down.
    """
    musicians: dict[str, TemporalAgent]

    def phase_census(self) -> dict[FunnelPhase, int]:
        """Count how many musicians are in each funnel phase."""
        counts = {p: 0 for p in FunnelPhase}
        for agent in self.musicians.values():
            # Use the last observation's phase (tracked internally)
            counts[FunnelPhase.NARROWING] += 1  # simplified; real impl tracks phase
        return counts

    def is_locked(self) -> bool:
        """True when > 80% of musicians are in NARROWING phase."""
        census = self.phase_census()
        total = sum(census.values())
        if total == 0:
            return False
        return census.get(FunnelPhase.NARROWING, 0) / total > 0.8

    def is_breaking_down(self) -> bool:
        """True when > 50% are in ANOMALY phase."""
        census = self.phase_census()
        total = sum(census.values())
        if total == 0:
            return False
        return census.get(FunnelPhase.ANOMALY, 0) / total > 0.5
```

### 2.2 The Interaction Loop

```python
class BandInteractionEngine:
    """Processes interactions between musicians each beat.

    Each beat:
    1. Collect side-channel events from last beat
    2. Match against BAND_INTERACTIONS rules
    3. Apply emotional contagion
    4. Check deadband sync state
    5. Emit reaction events
    """

    def __init__(self, band: "Band"):
        self.band = band
        self.contagion = EmotionalContagion()
        self.pending_events: list[SideChannelEvent] = []
        self.reaction_log: list[dict] = []

    def process_beat(self, bar: int, beat: float):
        """Process all interactions for one beat."""
        # 1. Collect new side-channel events
        new_events = [e for e in self.pending_events
                      if e.bar == bar and abs(e.beat - beat) < 0.01]

        # 2. For each event, find matching interaction rules
        for event in new_events:
            source = self.band.musician_by_name(event.source)
            if not source:
                continue

            for rule in BAND_INTERACTIONS:
                if source.archetype != rule.source_archetype:
                    continue

                # Find matching target musicians
                for musician in self.band.musicians:
                    if musician.archetype == rule.target_archetype:
                        # Apply delayed reaction
                        reaction_beat = beat + rule.delay_beats
                        self._schedule_reaction(
                            musician, rule, event, bar, reaction_beat
                        )

        # 3. Emotional contagion — propagate flux between all pairs
        for source in self.band.musicians:
            for target in self.band.musicians:
                if source is target:
                    continue
                deltas = self.contagion.propagate(source, target)
                for channel, delta in deltas.items():
                    current = getattr(target.flux, channel)
                    setattr(target.flux, channel,
                            max(-128, min(127, current + delta)))

        # 4. Process pending reactions that fire on this beat
        fired = [r for r in self.reaction_log
                 if r["bar"] == bar and abs(r["beat"] - beat) < 0.01
                 and not r.get("fired")]
        for reaction in fired:
            reaction["fired"] = True
            self._apply_reaction(reaction)

        # 5. Clean old events
        self.pending_events = [e for e in self.pending_events
                               if not (e.bar == bar and e.beat <= beat)]
        self.reaction_log = [r for r in self.reaction_log
                             if r["bar"] >= bar - 4]

    def _schedule_reaction(self, musician, rule, event, bar, beat):
        target_beat = beat
        target_bar = bar + int(target_beat // 4)
        target_beat = target_beat % 4
        self.reaction_log.append({
            "musician": musician.name,
            "reaction": rule.reaction,
            "flux_modulation": rule.flux_modulation,
            "bar": target_bar,
            "beat": target_beat,
            "source_event": event,
            "fired": False,
        })

    def _apply_reaction(self, reaction):
        musician = self.band.musician_by_name(reaction["musician"])
        if not musician:
            return
        for channel, delta in reaction["flux_modulation"].items():
            current = getattr(musician.flux, channel)
            setattr(musician.flux, channel,
                    max(-128, min(127, current + delta)))

    def emit(self, event: SideChannelEvent):
        """Emit a side-channel event."""
        self.pending_events.append(event)
```

---

## 3. The Living Score

The score is NOT fixed. It evolves based on room events, holonomy state, deadband convergence, and side-channel cues.

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import math
import random


@dataclass
class LivingNote:
    """A single note in the living score. It can mutate."""
    pitch: int
    velocity: int
    onset_beats: float
    duration_beats: float
    channel: int
    musician: str

    # Mutation state
    original_pitch: int = 0
    mutation_count: int = 0
    max_mutations: int = 3

    # Constraint boundaries
    pitch_floor: int = 0
    pitch_ceiling: int = 127
    allowed_scale: list[int] = field(default_factory=list)

    def __post_init__(self):
        self.original_pitch = self.pitch

    def mutate_pitch(self, flux: FluxVector, improv: ImprovisationConfig) -> bool:
        """Try to mutate pitch based on musician's current state.

        Returns True if mutation happened.
        """
        if self.mutation_count >= self.max_mutations:
            return False

        deviation = improv.deviation_for(flux)
        if random.random() > deviation:
            return False

        # Decide direction and magnitude
        interval = random.choice([-2, -1, 1, 2])
        if random.random() > improv.neighbor_tendency:
            # Leap
            interval = random.choice([-5, -4, -3, 3, 4, 5])

        new_pitch = self.pitch + interval

        # Clamp to register
        new_pitch = max(self.pitch_floor, min(self.pitch_ceiling, new_pitch))

        # Snap to nearest scale degree if chord_tone_bias triggers
        if random.random() < improv.chord_tone_bias and self.allowed_scale:
            new_pitch = self._snap_to_scale(new_pitch)

        if new_pitch != self.pitch:
            self.pitch = new_pitch
            self.mutation_count += 1
            return True
        return False

    def mutate_rhythm(self, flux: FluxVector, improv: ImprovisationConfig) -> bool:
        """Try to mutate rhythm (duration or onset offset)."""
        if random.random() > improv.rhythm_variation:
            return False
        # Shift onset slightly
        shift = random.choice([-0.25, -0.125, 0.125, 0.25])
        self.onset_beats += shift
        # Adjust duration
        self.duration_beats *= random.choice([0.5, 0.75, 1.0, 1.5])
        self.duration_beats = max(0.125, min(4.0, self.duration_beats))
        return True

    def _snap_to_scale(self, pitch: int) -> int:
        """Snap pitch to nearest allowed scale degree."""
        if not self.allowed_scale:
            return pitch
        octave = pitch // 12
        degree = pitch % 12
        # Find closest scale degree
        closest = min(self.allowed_scale, key=lambda s: abs(s - degree))
        return octave * 12 + closest


@dataclass
class HolonomyState:
    """Tracks how far the ensemble has drifted from the tonal center.

    Holonomy in constraint theory measures the accumulated phase around a
    closed loop. In music, this maps to how far we've wandered from the
    home key via modulations, chord substitutions, and chromaticism.

    High holonomy = high tension (we're far from home)
    Low holonomy = resolution (we're back at the tonal center)
    """
    key_center: int = 0           # semitone offset from C
    holonomy_angle: float = 0.0   # accumulated angle (radians)
    holonomy_radius: float = 0.0  # distance from center
    tension: float = 0.0          # derived: radius * sin(angle)
    max_tension: float = 2.0      # before forced resolution

    def update(self, notes: list[LivingNote], key_center: int):
        """Recalculate holonomy from current notes vs key center.

        The idea: each note is a vector from the key center.
        Sum them as complex numbers. The magnitude is how far we've drifted.
        The angle tells us the "direction" of the drift.
        """
        self.key_center = key_center
        real_sum = 0.0
        imag_sum = 0.0
        for note in notes:
            # Interval from key center as an angle
            interval = note.pitch - key_center
            weight = note.velocity / 127.0
            angle = (interval % 12) * (2 * math.pi / 12)
            real_sum += math.cos(angle) * weight
            imag_sum += math.sin(angle) * weight

        self.holonomy_radius = math.sqrt(real_sum**2 + imag_sum**2)
        self.holonomy_angle = math.atan2(imag_sum, real_sum)
        self.tension = self.holonomy_radius * abs(math.sin(self.holonomy_angle))

    def should_resolve(self) -> bool:
        """True when tension exceeds threshold → force resolution."""
        return self.tension > self.max_tension

    def resolution_force(self) -> float:
        """How strongly the system pulls back to key center (0.0 - 1.0)."""
        if self.tension <= 0:
            return 0.0
        return min(1.0, self.tension / self.max_tension)


@dataclass
class LivingScore:
    """A musical score that evolves in real-time.

    Not a static sequence of notes — a living document that responds to:
    - Room tile events (new tiles = new musical ideas)
    - Holonomy state (tension/release cycles)
    - Deadband convergence (ensemble lock)
    - Side-channel cues (nods, smiles, frowns)
    """
    notes: list[LivingNote] = field(default_factory=list)
    tempo: float = 120.0
    time_signature: tuple[int, int] = (4, 4)
    key_center: int = 0          # C
    total_bars: int = 0

    # Subsystems
    holonomy: HolonomyState = field(default_factory=HolonomyState)

    # Event log for the current bar
    tile_events: list[dict] = field(default_factory=list)
    side_events: list[SideChannelEvent] = field(default_factory=list)

    def add_tile_event(self, tile: dict, musician: MusicianPersonality,
                       mapper) -> LivingNote:
        """Convert a PLATO tile into a LivingNote and add to score."""
        note_dict = mapper.map_tile(musician.name, tile, self.tempo)
        note = LivingNote(
            pitch=note_dict["pitch"],
            velocity=note_dict["velocity"],
            onset_beats=note_dict["onset_beats"],
            duration_beats=note_dict["duration_beats"],
            channel=musician.midi_channel,
            musician=musician.name,
            pitch_floor=musician.register[0],
            pitch_ceiling=musician.register[1],
            allowed_scale=musician.scale,
        )
        self.notes.append(note)
        self.tile_events.append({
            "tile": tile,
            "note": note,
            "musician": musician.name,
        })
        return note

    def evolve_bar(self, band: "Band"):
        """Evolve all notes for the current bar.

        This is the main mutation loop. Each note gets a chance to
        mutate based on its musician's current state.
        """
        bar_start = self.total_bars * self.time_signature[0]
        bar_end = (self.total_bars + 1) * self.time_signature[0]

        bar_notes = [n for n in self.notes
                     if bar_start <= n.onset_beats < bar_end]

        for note in bar_notes:
            musician = band.musician_by_name(note.musician)
            if not musician:
                continue

            # Mutate based on personality
            note.mutate_pitch(musician.flux, musician.improv)
            note.mutate_rhythm(musician.flux, musician.improv)

        # Update holonomy
        self.holonomy.update(bar_notes, self.key_center)

        # Apply resolution force if holonomy is high
        if self.holonomy.should_resolve():
            self._apply_resolution(bar_notes)

        # Process side-channel effects
        for event in self.side_events:
            self._apply_side_channel(event, bar_notes)

        self.total_bars += 1
        self.tile_events.clear()
        self.side_events.clear()

    def _apply_resolution(self, bar_notes: list[LivingNote]):
        """Pull notes toward key center when tension is high."""
        force = self.holonomy.resolution_force()
        for note in bar_notes:
            interval = note.pitch - self.key_center
            # Pull pitch toward nearest chord tone
            pull = int(interval * force * 0.3)
            if pull != 0:
                note.pitch -= pull
                note.mutation_count += 1

    def _apply_side_channel(self, event: SideChannelEvent,
                            bar_notes: list[LivingNote]):
        """Modify notes based on side-channel cues."""
        target_notes = [n for n in bar_notes if n.musician == event.target]
        if event.type == SideChannelType.NOD:
            # "Take it" → boost velocity, encourage longer notes
            for note in target_notes:
                note.velocity = min(127, note.velocity + 20)
                note.duration_beats *= 1.5
        elif event.type == SideChannelType.SMILE:
            # Approval → maintain current course, slight velocity boost
            for note in target_notes:
                note.velocity = min(127, note.velocity + 5)
        elif event.type == SideChannelType.FROWN:
            # "Adjust" → reduce velocity, shorten notes, simplify
            for note in target_notes:
                note.velocity = max(1, note.velocity - 15)
                note.duration_beats *= 0.5

    def to_midi_file(self, path: str):
        """Export the living score as a standard MIDI file."""
        # Use a lightweight MIDI library (e.g., mido or raw bytes)
        try:
            from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
        except ImportError:
            raise ImportError("Install mido: pip install mido")

        mid = MidiFile(ticks_per_beat=480)
        tempo = bpm2tempo(self.tempo)

        # Group notes by channel
        channels: dict[int, list[LivingNote]] = {}
        for note in self.notes:
            channels.setdefault(note.channel, []).append(note)

        for ch, ch_notes in channels.items():
            track = MidiTrack()
            track.append(MetaMessage("set_tempo", tempo=tempo))
            track.append(Message("program_change", channel=ch, program=0))

            ch_notes.sort(key=lambda n: n.onset_beats)
            abs_tick = 0
            for note in ch_notes:
                target_tick = int(note.onset_beats * 480)
                delta = max(0, target_tick - abs_tick)
                track.append(Message("note_on", channel=ch,
                                     note=note.pitch & 0x7F,
                                     velocity=note.velocity & 0x7F,
                                     time=delta))
                dur_ticks = max(1, int(note.duration_beats * 480))
                track.append(Message("note_off", channel=ch,
                                     note=note.pitch & 0x7F,
                                     velocity=0, time=dur_ticks))
                abs_tick = target_tick + dur_ticks

            mid.tracks.append(track)

        mid.save(path)
```

---

## 4. Educational Application

### 4.1 MusicalConversation Model

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class LessonType(Enum):
    VOICE_LEADING = "voice_leading"      # smooth melodic motion
    COUNTERPOINT = "counterpoint"         # independent melodic lines
    GROOVE = "groove"                     # rhythm and feel
    HARMONY = "harmony"                   # chord progressions
    IMPROVISATION = "improvisation"       # soloing within constraints
    DYNAMICS = "dynamics"                 # volume and expression
    FORM = "form"                         # song structure
    TENSION_RELEASE = "tension_release"   # holonomy-aware phrasing


@dataclass
class MusicalPhrase:
    """A phrase exchanged between student and musician in a lesson."""
    notes: list[LivingNote]
    musician_name: str
    is_student: bool = False
    feedback: str = ""          # musician's comment on this phrase
    constraint_violations: list[str] = field(default_factory=list)
    score: float = 0.0          # 0.0 - 1.0 how well the student did


@dataclass
class LessonPlan:
    """A structured lesson with a musician-teacher."""
    lesson_type: LessonType
    teacher: MusicianPersonality
    objective: str
    exercises: list[dict]        # ordered list of exercises
    current_exercise: int = 0
    phrases: list[MusicalPhrase] = field(default_factory=list)
    completed: bool = False

    def next_exercise(self) -> Optional[dict]:
        """Advance to next exercise, or None if lesson complete."""
        if self.current_exercise < len(self.exercises) - 1:
            self.current_exercise += 1
            return self.exercises[self.current_exercise]
        self.completed = True
        return None


# ── Per-archetype teaching specialties ──

TEACHER_PROFILES = {
    PersonalityArchetype.FORGEMASTER: {
        "specialties": [LessonType.VOICE_LEADING, LessonType.GROOVE],
        "teaching_style": "patient, repetitive, builds from simple patterns",
        "greeting": "Let's find the pocket. I'll play a bass line, you respond.",
        "praise": "Solid. You're locking in.",
        "correction": "Try landing on the root more. Let me show you.",
    },
    PersonalityArchetype.FLEET: {
        "specialties": [LessonType.GROOVE, LessonType.DYNAMICS],
        "teaching_style": "call-and-response, high energy, rhythmic games",
        "greeting": "Hey! Match my groove. I'll play, you echo.",
        "praise": "Nailed it! You felt that!",
        "correction": "You're rushing — feel the space between the beats.",
    },
    PersonalityArchetype.SESSION: {
        "specialties": [LessonType.HARMONY, LessonType.COUNTERPOINT],
        "teaching_style": "demonstrates chord voicings, asks student to complete progressions",
        "greeting": "Let's explore some colors. I'll play a chord, you fill in the melody.",
        "praise": "Beautiful choice. That tension is exactly right.",
        "correction": "Hear how that clashes? Try a chord tone — here's what I mean.",
    },
    PersonalityArchetype.KNOWLEDGE: {
        "specialties": [LessonType.IMPROVISATION, LessonType.TENSION_RELEASE],
        "teaching_style": "intellectual, explains theory, then demonstrates",
        "greeting": "Today we explore. I'll set up a harmonic landscape — navigate it.",
        "praise": "Interesting choice. You heard where that was going.",
        "correction": "The scale allows more freedom than you're using. Try this.",
    },
    PersonalityArchetype.CONSTRAINT: {
        "specialties": [LessonType.FORM, LessonType.HARMONY],
        "teaching_style": "rule-based, structured exercises, precise feedback",
        "greeting": "We'll work within strict parameters. Constraints create freedom.",
        "praise": "Technically correct. Good adherence to the rules.",
        "correction": "That violates rule 3: no parallel fifths. Here's why that matters.",
    },
}


class MusicalConversation:
    """A lesson as a back-and-forth musical dialogue.

    The musician-teacher plays a phrase, the student responds,
    and the teacher gives feedback — both verbal (via FluxVector
    changes) and musical (via side-channels and counter-phrases).
    """

    def __init__(self, teacher: MusicianPersonality, lesson_type: LessonType,
                 band: "Band"):
        self.teacher = teacher
        self.lesson_type = lesson_type
        self.band = band
        self.plan = self._build_lesson_plan()
        self.conversation_history: list[MusicalPhrase] = []

    def _build_lesson_plan(self) -> LessonPlan:
        """Generate a lesson plan based on the teacher's specialty."""
        profile = TEACHER_PROFILES[self.teacher.archetype]

        exercises = {
            LessonType.VOICE_LEADING: [
                {"name": "Stepwise motion", "description": "Play notes that move by step only",
                 "constraint": {"max_interval": 2}, "bars": 4},
                {"name": "Chord tones on strong beats",
                 "description": "Land on chord tones on beats 1 and 3",
                 "constraint": {"strong_beat_scale": True}, "bars": 4},
                {"name": "Smooth voice leading",
                 "description": "Connect chords with minimal movement",
                 "constraint": {"max_voice_movement": 2}, "bars": 8},
            ],
            LessonType.GROOVE: [
                {"name": "Echo my rhythm", "description": "Match my rhythmic pattern exactly",
                 "constraint": {"match_rhythm": True}, "bars": 4},
                {"name": "Fill the gap", "description": "I leave space, you fill it",
                 "constraint": {"fill_gaps": True}, "bars": 4},
                {"name": "Independent groove",
                 "description": "Play your own pattern that complements mine",
                 "constraint": {"complement": True}, "bars": 8},
            ],
            LessonType.HARMONY: [
                {"name": "Identify the chord", "description": "I play a chord, you name the function",
                 "constraint": {"identify": True}, "bars": 2},
                {"name": "Complete the progression",
                 "description": "I start a progression, you finish it",
                 "constraint": {"complete": True}, "bars": 4},
                {"name": "Reharmonize", "description": "Change the chords while keeping the melody",
                 "constraint": {"reharmonize": True}, "bars": 8},
            ],
            LessonType.IMPROVISATION: [
                {"name": "Scale exploration", "description": "Improvise using only the given scale",
                 "constraint": {"strict_scale": True}, "bars": 4},
                {"name": "Question and answer",
                 "description": "I play a phrase (question), you respond (answer)",
                 "constraint": {"call_response": True}, "bars": 8},
                {"name": "Free improvisation with constraints",
                 "description": "Solo freely but resolve to chord tones",
                 "constraint": {"resolve_to_chord": True}, "bars": 16},
            ],
            LessonType.TENSION_RELEASE: [
                {"name": "Build tension", "description": "Move away from the key center gradually",
                 "constraint": {"increase_holonomy": True}, "bars": 4},
                {"name": "Release", "description": "Find your way back to the tonic",
                 "constraint": {"decrease_holonomy": True}, "bars": 4},
                {"name": "Arc", "description": "Build and release tension over 8 bars",
                 "constraint": {"holonomy_arc": True}, "bars": 8},
            ],
        }

        return LessonPlan(
            lesson_type=self.lesson_type,
            teacher=self.teacher,
            objective=profile["teaching_style"],
            exercises=exercises.get(self.lesson_type, []),
        )

    def teacher_plays(self, bars: int = 4) -> MusicalPhrase:
        """Teacher demonstrates a phrase for the current exercise."""
        exercise = self.plan.exercises[self.plan.current_exercise]
        # Generate teacher's demonstration phrase
        notes = self._generate_teacher_phrase(bars)
        phrase = MusicalPhrase(
            notes=notes,
            musician_name=self.teacher.name,
            is_student=False,
        )
        self.conversation_history.append(phrase)
        return phrase

    def student_responds(self, student_notes: list[LivingNote]) -> MusicalPhrase:
        """Student plays their response. Teacher evaluates."""
        phrase = MusicalPhrase(
            notes=student_notes,
            musician_name="student",
            is_student=True,
        )

        # Evaluate using constraint theory
        exercise = self.plan.exercises[self.plan.current_exercise]
        phrase.score = self._evaluate(student_notes, exercise)
        phrase.constraint_violations = self._find_violations(student_notes, exercise)
        phrase.feedback = self._generate_feedback(phrase.score, phrase.constraint_violations)

        self.conversation_history.append(phrase)

        # Teacher's emotional response
        if phrase.score > 0.8:
            # Smile — student did well
            self.teacher.flux.valence = min(127, self.teacher.flux.valence + 15)
            self.teacher.flux.affiliation = min(127, self.teacher.flux.affiliation + 10)
        elif phrase.score < 0.4:
            # Frown — needs work
            self.teacher.flux.valence = max(-128, self.teacher.flux.valence - 10)
            self.teacher.flux.uncertainty = min(127, self.teacher.flux.uncertainty + 5)

        return phrase

    def _generate_teacher_phrase(self, bars: int) -> list[LivingNote]:
        """Generate a demonstration phrase from the teacher's personality."""
        notes = []
        config = self.teacher.improv
        exercise = self.plan.exercises[self.plan.current_exercise]

        for bar in range(bars):
            for beat in range(self.band.score.time_signature[0]):
                onset = (self.band.score.total_bars + bar) * 4 + beat

                # Teacher plays with LOW deviation for clarity
                if random.random() < config.chord_tone_bias:
                    degree = random.choice(self.teacher.scale)
                else:
                    degree = random.randint(0, 11)

                octave = random.randint(
                    self.teacher.register[0] // 12,
                    self.teacher.register[1] // 12,
                )
                pitch = octave * 12 + degree
                pitch = max(self.teacher.register[0],
                            min(self.teacher.register[1], pitch))

                notes.append(LivingNote(
                    pitch=pitch,
                    velocity=random.randint(60, 100),
                    onset_beats=float(onset),
                    duration_beats=1.0,
                    channel=self.teacher.midi_channel,
                    musician=self.teacher.name,
                    pitch_floor=self.teacher.register[0],
                    pitch_ceiling=self.teacher.register[1],
                    allowed_scale=self.teacher.scale,
                ))
        return notes

    def _evaluate(self, notes: list[LivingNote], exercise: dict) -> float:
        """Score a student response against exercise constraints."""
        if not notes:
            return 0.0

        constraint = exercise.get("constraint", {})
        score = 1.0
        violations = 0

        for note in notes:
            # Check interval constraints
            max_interval = constraint.get("max_interval", 12)
            # (simplified — real impl would check consecutive notes)

            # Check scale constraints
            if constraint.get("strict_scale"):
                if note.pitch % 12 not in self.teacher.scale:
                    violations += 1

        if notes:
            score = max(0.0, 1.0 - violations / len(notes))
        return score

    def _find_violations(self, notes: list[LivingNote],
                         exercise: dict) -> list[str]:
        """List specific constraint violations."""
        violations = []
        constraint = exercise.get("constraint", {})

        if constraint.get("strict_scale"):
            for i, note in enumerate(notes):
                if note.pitch % 12 not in self.teacher.scale:
                    violations.append(
                        f"Beat {note.onset_beats:.1f}: pitch {note.pitch} "
                        f"not in scale"
                    )
        return violations

    def _generate_feedback(self, score: float,
                           violations: list[str]) -> str:
        """Generate verbal feedback based on score."""
        profile = TEACHER_PROFILES[self.teacher.archetype]
        if score > 0.8:
            return profile["praise"]
        elif violations:
            first = violations[0]
            return f"{profile['correction']} Issue: {first}"
        else:
            return "Getting there. Try again."

    def advance(self) -> Optional[dict]:
        """Move to next exercise if current one is passed."""
        if self.conversation_history:
            last = self.conversation_history[-1]
            if not last.is_student or last.score >= 0.6:
                return self.plan.next_exercise()
        return None
```

### 4.2 Lesson Integration with Band

```python
class BandEducation:
    """Educational mode for the band — students interact with musician-teachers."""

    def __init__(self, band: "Band"):
        self.band = band
        self.active_lessons: dict[str, MusicalConversation] = {}

    def start_lesson(self, lesson_type: LessonType,
                     teacher_name: str) -> MusicalConversation:
        """Start a lesson with a specific musician."""
        teacher = self.band.musician_by_name(teacher_name)
        if not teacher:
            raise ValueError(f"No musician named {teacher_name}")

        # Check if teacher specializes in this lesson type
        profile = TEACHER_PROFILES.get(teacher.archetype)
        if profile and lesson_type not in profile["specialties"]:
            # They'll still teach it, but note the preference
            pass

        conversation = MusicalConversation(teacher, lesson_type, self.band)
        self.active_lessons[teacher_name] = conversation
        return conversation

    def recommended_teacher(self, lesson_type: LessonType) -> str:
        """Find the best teacher for a given lesson type."""
        best = None
        best_score = -1
        for arch, profile in TEACHER_PROFILES.items():
            if lesson_type in profile["specialties"]:
                # Find a musician with this archetype
                for m in self.band.musicians:
                    if m.archetype == arch:
                        return m.name
        # Fallback: any musician
        return self.band.musicians[0].name if self.band.musicians else ""
```

---

## 5. Complete API

```python
# constraint_music/__init__.py
"""
constraint_music — AI band from PLATO rooms.

Musicians with personality, living scores, and educational conversations.
"""

from constraint_music.personality import (
    MusicianPersonality,
    PersonalityArchetype,
    GrooveProfile,
    ImprovisationConfig,
    ListeningConfig,
    SoloConfig,
    RiskTolerance,
    SyncTendency,
    ARCHETYPE_PRESETS,
)
from constraint_music.dynamics import (
    BandInteractionEngine,
    EmotionalContagion,
    SideChannelEvent,
    SideChannelType,
)
from constraint_music.score import (
    LivingNote,
    LivingScore,
    HolonomyState,
)
from constraint_music.education import (
    BandEducation,
    MusicalConversation,
    LessonPlan,
    LessonType,
    TEACHER_PROFILES,
)


# ── Band ──

class Band:
    """An AI band assembled from PLATO rooms.

    Each room becomes a musician with a distinct personality.
    """

    def __init__(self, musicians: list[MusicianPersonality]):
        self.musicians = musicians
        self._name_index: dict[str, MusicianPersonality] = {
            m.name: m for m in musicians
        }
        self.score = LivingScore()
        self.interaction_engine = BandInteractionEngine(self)
        self.education = BandEducation(self)

    @classmethod
    def from_plato(cls, fetcher=None) -> "Band":
        """Create a band from PLATO room tiles.

        Parameters
        ----------
        fetcher : optional
            A SyntheticFetcher or real PLATO room data source.
            If None, creates a minimal band from archetype defaults.
        """
        from plato_room_musician.mapping import RoomMapper, CATEGORY_CONFIG

        musicians = []
        room_mapper = RoomMapper()

        if fetcher is not None:
            # Real mode: pull rooms from fetcher
            rooms = fetcher.fetch_rooms()
            for room in rooms:
                name = room["name"]
                cat = room.get("category", "session")
                cfg = CATEGORY_CONFIG.get(cat, CATEGORY_CONFIG["session"])

                archetype_map = {
                    "forgemaster": PersonalityArchetype.FORGEMASTER,
                    "session": PersonalityArchetype.SESSION,
                    "fleet": PersonalityArchetype.FLEET,
                    "knowledge": PersonalityArchetype.KNOWLEDGE,
                    "constraint": PersonalityArchetype.CONSTRAINT,
                }
                archetype = archetype_map.get(cat, PersonalityArchetype.SESSION)
                preset = ARCHETYPE_PRESETS[archetype]

                musician = MusicianPersonality(
                    name=name,
                    archetype=archetype,
                    role_description=preset["role_description"],
                    midi_channel=room_mapper.channel_for(name),
                    register=tuple(cfg["register"]),
                    scale=cfg["scale"],
                    rhythmic_role=cfg["rhythmic_role"],
                    patches=cfg["patches"],
                    groove=preset["groove"],
                    improv=preset["improv"],
                    listening=preset["listening"],
                    solo=preset["solo"],
                    risk=preset["risk"],
                    baseline_flux=preset["baseline_flux"],
                )
                musician.reset_to_baseline()
                musicians.append(musician)
        else:
            # Demo mode: create one musician per archetype
            for i, (archetype, preset) in enumerate(ARCHETYPE_PRESETS.items()):
                cat = archetype.value
                cfg = CATEGORY_CONFIG.get(cat, CATEGORY_CONFIG["session"])
                name = f"{cat}-demo"

                musician = MusicianPersonality(
                    name=name,
                    archetype=archetype,
                    role_description=preset["role_description"],
                    midi_channel=i,
                    register=tuple(cfg["register"]),
                    scale=cfg["scale"],
                    rhythmic_role=cfg["rhythmic_role"],
                    patches=cfg["patches"],
                    groove=preset["groove"],
                    improv=preset["improv"],
                    listening=preset["listening"],
                    solo=preset["solo"],
                    risk=preset["risk"],
                    baseline_flux=preset["baseline_flux"],
                )
                musician.reset_to_baseline()
                musicians.append(musician)

        return cls(musicians)

    def __getitem__(self, name: str) -> MusicianPersonality:
        """Get a musician by room name."""
        if name not in self._name_index:
            # Try partial match
            for m in self.musicians:
                if name in m.name or m.name.startswith(name):
                    return m
            raise KeyError(f"No musician named '{name}'")
        return self._name_index[name]

    def musician_by_name(self, name: str) -> MusicianPersonality | None:
        """Look up a musician, returning None if not found."""
        return self._name_index.get(name)

    def teach(self, topic: str, student: MusicianPersonality | None = None
              ) -> MusicalConversation:
        """Start an educational conversation.

        Parameters
        ----------
        topic : str
            One of: "voice_leading", "counterpoint", "groove",
            "harmony", "improvisation", "dynamics", "form",
            "tension_release"
        student : MusicianPersonality, optional
            The musician the student will interact with.
            If None, the best teacher for the topic is chosen.

        Returns
        -------
        MusicalConversation
            The active lesson — call teacher_plays() and
            student_responds() to have the dialogue.
        """
        lesson_type = LessonType(topic)
        if student is not None:
            teacher_name = student.name
        else:
            teacher_name = self.education.recommended_teacher(lesson_type)
        return self.education.start_lesson(lesson_type, teacher_name)

    def jam(self, bars: int = 32, chart: str | None = None) -> LivingScore:
        """Free jam session — musicians improvise within constraints.

        Parameters
        ----------
        bars : int
            How many bars to generate.
        chart : str, optional
            Named chart (e.g., "blues_in_bb") for structure.

        Returns
        -------
        LivingScore
            The evolving score from the jam.
        """
        if chart:
            self._load_chart(chart)

        for bar in range(bars):
            # Each musician contributes
            for musician in self.musicians:
                self._musician_bar(musician, bar)

            # Evolve the score
            self.score.evolve_bar(self)

            # Process interactions
            for beat in range(self.score.time_signature[0]):
                self.interaction_engine.process_beat(bar, beat)

        return self.score

    def _musician_bar(self, musician: MusicianPersonality, bar: int):
        """Generate a bar of music for one musician."""
        bar_start = bar * self.score.time_signature[0]
        ts_num = self.score.time_signature[0]

        # How many notes? Based on rhythmic role density
        density_map = {
            "root": ts_num,        # quarter notes
            "halftime": ts_num // 2,
            "triplet": int(ts_num * 1.5),
            "waltz": ts_num * 2,   # eighth notes in 3
            "compound": ts_num,
        }
        note_count = density_map.get(
            musician.rhythmic_role.value
            if hasattr(musician.rhythmic_role, 'value')
            else musician.rhythmic_role,
            ts_num,
        )

        # Solo boost
        if musician.solo.wants_solo(
            musician.flux, bar,
            self.interaction_engine.pending_events,
        ):
            note_count = int(note_count * musician.solo.preferred_density * 2)
            musician.solo.last_solo_bar = bar

        for i in range(max(1, note_count)):
            beat_offset = i * (ts_num / max(1, note_count))
            onset = bar_start + beat_offset

            # Groove offset
            epsilon = musician.groove.epsilon_for(musician.flux, beat_offset / ts_num)

            # Pitch selection
            improv_level = musician.improv.deviation_for(musician.flux)
            if random.random() < musician.improv.chord_tone_bias:
                degree = random.choice(musician.scale)
            else:
                degree = random.randint(0, 11)

            octave = random.randint(
                musician.register[0] // 12,
                musician.register[1] // 12,
            )
            pitch = octave * 12 + degree
            pitch = max(musician.register[0],
                        min(musician.register[1], pitch))

            # Velocity from flux
            base_vel = int(60 + musician.flux.arousal * 0.3)
            velocity = max(1, min(127, base_vel + random.randint(-15, 15)))

            # Duration
            base_dur = ts_num / max(1, note_count)
            duration = base_dur * random.uniform(0.6, 1.0)

            note = LivingNote(
                pitch=pitch,
                velocity=velocity,
                onset_beats=onset + epsilon,
                duration_beats=duration,
                channel=musician.midi_channel,
                musician=musician.name,
                pitch_floor=musician.register[0],
                pitch_ceiling=musician.register[1],
                allowed_scale=musician.scale,
            )
            self.score.notes.append(note)

    def _load_chart(self, name: str):
        """Load a named chart that sets key, tempo, form."""
        charts = {
            "blues_in_bb": {
                "key": 10,  # Bb
                "tempo": 120,
                "time_signature": (4, 4),
                "form": ["I", "I", "I", "I", "IV", "IV", "I", "I",
                         "V", "IV", "I", "V"],
            },
            "autumn_leaves": {
                "key": 7,   # G
                "tempo": 100,
                "time_signature": (4, 4),
                "form": ["ii", "V", "I", "vi", "ii", "V", "I", "I"],
            },
            "take_five": {
                "key": 4,   # E (minor)
                "tempo": 176,
                "time_signature": (5, 4),
                "form": ["i", "i", "III", "V", "i"],
            },
        }
        chart = charts.get(name)
        if chart:
            self.score.key_center = chart["key"]
            self.score.tempo = chart["tempo"]
            self.score.time_signature = chart["time_signature"]


# ── Rehearsal ──

class Rehearsal:
    """A structured rehearsal where musicians interact and evolve.

    Unlike a jam (free), a rehearsal has a chart and runs the
    interaction engine with all dynamics enabled.
    """

    def __init__(self, band: Band, chart: str = "blues_in_bb"):
        self.band = band
        self.chart_name = chart
        self.band._load_chart(chart)
        self.completed_bars = 0
        self.events_log: list[dict] = []

    def run(self, bars: int = 32) -> LivingScore:
        """Run the rehearsal for N bars.

        This is the main loop:
        1. For each bar, each musician generates their part
        2. Interactions fire (side-channels, contagion)
        3. Score evolves (mutations, holonomy, resolution)
        4. Producer checks constraints and adjusts

        Returns the final living score.
        """
        for bar in range(bars):
            # Generate parts for all musicians
            for musician in self.band.musicians:
                self.band._musician_bar(musician, self.completed_bars)

            # Producer role: check constraints, emit frowns for violations
            self._producer_check(bar)

            # Evolve the score (mutations, holonomy)
            self.band.score.evolve_bar(self.band)

            # Process beat-by-beat interactions
            for beat in range(self.band.score.time_signature[0]):
                self.band.interaction_engine.process_beat(
                    self.completed_bars, beat
                )

            self.completed_bars += 1

            # Log state
            self.events_log.append({
                "bar": self.completed_bars,
                "holonomy_tension": self.band.score.holonomy.tension,
                "holonomy_should_resolve": self.band.score.holonomy.should_resolve(),
                "tempo": self.band.score.tempo,
                "total_notes": len(self.band.score.notes),
            })

        return self.band.score

    @property
    def score(self) -> LivingScore:
        """The current state of the living score."""
        return self.band.score

    def _producer_check(self, bar: int):
        """Producer musician checks for constraint violations."""
        producer = None
        for m in self.band.musicians:
            if m.archetype == PersonalityArchetype.CONSTRAINT:
                producer = m
                break
        if not producer:
            return

        # Check recent notes for dissonance against key center
        bar_start = bar * self.band.score.time_signature[0]
        bar_notes = [n for n in self.band.score.notes
                     if bar_start <= n.onset_beats < bar_start + 4]

        for note in bar_notes:
            musician = self.band.musician_by_name(note.musician)
            if not musician or musician is producer:
                continue

            interval = abs(note.pitch - self.band.score.key_center) % 12
            if interval > producer.risk.dissonance_max:
                # Frown at the offender
                event = SideChannelEvent(
                    source=producer.name,
                    target=note.musician,
                    type=SideChannelType.FROWN,
                    intensity=0.7,
                    bar=bar,
                    beat=note.onset_beats % 4,
                )
                self.band.interaction_engine.emit(event)

    def to_midi(self, path: str):
        """Export rehearsal to MIDI file."""
        self.band.score.to_midi_file(path)

    def summary(self) -> dict:
        """Return a summary of the rehearsal."""
        return {
            "chart": self.chart_name,
            "bars": self.completed_bars,
            "total_notes": len(self.band.score.notes),
            "final_holonomy": {
                "tension": self.band.score.holonomy.tension,
                "radius": self.band.score.holonomy.holonomy_radius,
                "angle": self.band.score.holonomy.holonomy_angle,
            },
            "musicians": {
                m.name: {
                    "archetype": m.archetype.value,
                    "flux": m.emotional_state(),
                    "temporal_anomalies": m.temporal.anomaly_count,
                }
                for m in self.band.musicians
            },
        }


# ── Top-level convenience ──

# Make the import from the task description work:
#   from constraint_music import Band, Musician, Rehearsal
Musician = MusicianPersonality

__all__ = [
    "Band", "Musician", "MusicianPersonality", "Rehearsal",
    "PersonalityArchetype", "GrooveProfile", "ImprovisationConfig",
    "ListeningConfig", "SoloConfig", "RiskTolerance", "SyncTendency",
    "LivingNote", "LivingScore", "HolonomyState",
    "BandInteractionEngine", "EmotionalContagion",
    "SideChannelEvent", "SideChannelType",
    "BandEducation", "MusicalConversation", "LessonPlan", "LessonType",
    "TEACHER_PROFILES", "ARCHETYPE_PRESETS",
]
```

### Usage Examples

```python
from constraint_music import Band, Musician, Rehearsal

# ── Create a band from PLATO rooms ──
band = Band.from_plato()  # demo mode — one musician per archetype

# Access musicians by name
bass = band["forgemaster-demo"]
drums = band["fleet-demo"]
keys = band["session-demo"]
sax = band["knowledge-demo"]
producer = band["constraint-demo"]

# ── Free jam ──
score = band.jam(bars=16)
score.to_midi_file("jam.mid")

# ── Structured rehearsal ──
band2 = Band.from_plato()
rehearsal = Rehearsal(band2, chart="blues_in_bb")
rehearsal.run(64)
rehearsal.to_midi("rehearsal_blues.mid")
print(rehearsal.summary())

# ── Educational mode ──
band3 = Band.from_plato()

# Learn voice leading from the bass player
lesson = band3.teach("voice_leading", student=band3["forgemaster-demo"])
demonstration = lesson.teacher_plays(4)
# ... student plays their response ...
# student_phrase = lesson.student_responds(student_notes)

# Learn groove from the drummer
groove_lesson = band3.teach("groove")  # auto-picks fleet-drummer
pattern = groove_lesson.teacher_plays(4)

# Learn improvisation from the sax player
solo_lesson = band3.teach("improvisation", student=band3["knowledge-demo"])
solo_lesson.teacher_plays(8)

# ── Inspect musician personality ──
print(f"Bass player arousal: {bass.flux.arousal}")
print(f"Bass groove tendency: {bass.groove.sync_tendency}")
print(f"Sax risk tolerance: {sax.risk.dissonance_max}")
print(f"Drums improv level: {drums.improv.base_deviation}")
print(f"Producer sensitivity: {producer.listening.sensitivity}")
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                           Band                                   │
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐ │
│  │  Bass    │ │  Keys    │ │  Drums   │ │  Sax     │ │ Prod. │ │
│  │  forge-  │ │  session │ │  fleet   │ │  know-   │ │ const-│ │
│  │  master  │ │          │ │          │ │  ledge   │ │ raint │ │
│  ├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤ ├───────┤ │
│  │FluxVector│ │FluxVector│ │FluxVector│ │FluxVector│ │FluxVec│ │
│  │TZeroClock│ │TZeroClock│ │TZeroClock│ │TZeroClock│ │Clock  │ │
│  │GrooveProf│ │GrooveProf│ │GrooveProf│ │GrooveProf│ │Groove │ │
│  │ImprovCfg │ │ImprovCfg │ │ImprovCfg │ │ImprovCfg │ │Improv │ │
│  │ListenCfg │ │ListenCfg │ │ListenCfg │ │ListenCfg │ │Listen │ │
│  │SoloCfg   │ │SoloCfg   │ │SoloCfg   │ │SoloCfg   │ │Solo   │ │
│  │RiskToler.│ │RiskToler.│ │RiskToler.│ │RiskToler.│ │Risk   │ │
│  │TemporalAg│ │TemporalAg│ │TemporalAg│ │TemporalAg│ │TempAg │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └──┬────┘ │
│       │            │            │            │           │      │
│       └────────────┴─────┬──────┴────────────┘           │      │
│                          │                                │      │
│              ┌───────────▼───────────┐     ┌──────────────┘      │
│              │  InteractionEngine    │     │                      │
│              │  ┌─────────────────┐  │     │                      │
│              │  │ SideChannels    │  │◄────┤  Frowns at           │
│              │  │ (nod/smile/    │  │     │  dissonance           │
│              │  │  frown)        │  │     │                      │
│              │  ├─────────────────┤  │     │                      │
│              │  │ Emotional       │  │     │                      │
│              │  │ Contagion       │  │     │                      │
│              │  │ (flux spread)   │  │     │                      │
│              │  ├─────────────────┤  │     │                      │
│              │  │ DeadbandSync    │  │     │                      │
│              │  │ (temporal lock) │  │     │                      │
│              │  └─────────────────┘  │     │                      │
│              └───────────┬───────────┘     │                      │
│                          │                 │                      │
│              ┌───────────▼───────────┐     │                      │
│              │    LivingScore        │◄────┘                      │
│              │  ┌─────────────────┐  │                            │
│              │  │ LivingNotes     │  │                            │
│              │  │ (mutable notes) │  │                            │
│              │  ├─────────────────┤  │                            │
│              │  │ HolonomyState   │  │                            │
│              │  │ (tension track) │  │                            │
│              │  ├─────────────────┤  │                            │
│              │  │ Tile Events     │  │                            │
│              │  │ (PLATO → notes) │  │                            │
│              │  └────────┬────────┘  │                            │
│              └──────────┼────────────┘                            │
│                         │                                         │
│              ┌──────────▼────────────┐                            │
│              │   MIDI Export         │                            │
│              │   (to_midi_file)      │                            │
│              └───────────────────────┘                            │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                    BandEducation                          │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐  │   │
│  │  │ VoiceLeading │ │ GrooveLesson │ │ ImprovLesson     │  │   │
│  │  │ w/ Bass      │ │ w/ Drums     │ │ w/ Sax           │  │   │
│  │  └──────────────┘ └──────────────┘ └──────────────────┘  │   │
│  └───────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
PLATO Tile ──► TileMapper.map_tile() ──► LivingNote
                                              │
                                              ▼
MusicianPersonality.flux ─────────► LivingNote.mutate_pitch()
MusicianPersonality.groove ───────► LivingNote.onset_beats += epsilon
MusicianPersonality.improv ───────► LivingNote.mutate_rhythm()
                                              │
                                              ▼
                                    LivingScore.evolve_bar()
                                              │
                                    ┌─────────┴─────────┐
                                    │                   │
                              HolonomyState      SideChannel effects
                              (tension track)    (nod/smile/frown)
                                    │                   │
                                    └─────────┬─────────┘
                                              │
                                    InteractionEngine
                                    (contagion + rules)
                                              │
                                              ▼
                                      Updated FluxVectors
                                      (musicians feel things)
                                              │
                                              ▼
                                        Next bar...
```

---

## Implementation Roadmap

### Phase 1: Core (Week 1-2)
- `MusicianPersonality` + `ARCHETYPE_PRESETS`
- `Band.from_plato()` (demo mode)
- `LivingNote` + basic mutation
- `LivingScore` with simple `to_midi_file()`

### Phase 2: Dynamics (Week 3-4)
- `BandInteractionEngine` with side-channels
- `EmotionalContagion` between musicians
- `HolonomyState` tracking
- `DeadbandSync` convergence

### Phase 3: Rehearsal (Week 5-6)
- `Rehearsal.run()` with chart loading
- Producer constraint checking
- Per-beat interaction loop
- Full `Rehearsal.summary()`

### Phase 4: Education (Week 7-8)
- `MusicalConversation` dialogue system
- Lesson plans per archetype
- Student evaluation engine
- `BandEducation` coordinator

### Phase 5: Integration (Week 9-10)
- Wire to real PLATO fetcher
- Real-time MIDI output (not just file export)
- Web UI for educational mode
- Recording and playback

---

## Key Algorithms

### Eisenstein Snap → Groove Quantization

Each musician's onset is snapped to the Eisenstein lattice, but with their personal epsilon offset. The covering radius 1/√3 ≈ 0.577 provides the quantization tolerance:

```python
# In musician's time domain:
raw_onset = bar_start + beat_position + epsilon
# Snap to rhythmic grid via Eisenstein lattice
snapped_onset = eisenstein_snap(raw_onset, role=musician.rhythmic_role)
# Result: micro-timed but musically grounded
```

### Deadband Funnel → Ensemble Lock Detection

Each musician's `TemporalAgent` tracks how well they're predicting the beat. When all agents are in `NARROWING` phase, the ensemble is locked. When many hit `ANOMALY`, the groove is breaking down:

```python
# Per musician, per beat:
result = musician.temporal.observe(predicted_beat, actual_beat, t)
if result.phase == FunnelPhase.ANOMALY:
    # This musician lost the thread — contagion spreads uncertainty
    musician.flux.uncertainty += 10
```

### Holonomy → Tension/Release

The holonomy of the score (how far from key center) drives tension:

```python
score.holonomy.update(bar_notes, key_center)
if score.holonomy.should_resolve():
    # Pull notes toward key center
    force = score.holonomy.resolution_force()
    for note in bar_notes:
        note.pitch -= int((note.pitch - key_center) * force * 0.3)
```

---

*This is a living document. As the band evolves, so does the design.*
