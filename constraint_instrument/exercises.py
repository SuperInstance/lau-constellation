"""
ExerciseGenerator — Targeted practice exercises based on diagnostic results.

The math educator's classroom tool: every student gets personalized exercises
based on their actual weaknesses, not a one-size-fits-all curriculum.

Usage:
    from constraint_instrument.exercises import ExerciseGenerator

    gen = ExerciseGenerator()

    # From diagnostic scores
    exercises = gen.prescribe({'position': 0.89, 'direction': 0.45, 'curvature': 0.72, 'structure': 0.60})

    # For a specific order
    ex = gen.for_order('direction', difficulty=0.7)

    # Full workout
    workout = gen.workout(terrain='bebop', key='Eb', bpm=120)

    # From an Instrument
    inst = Instrument(mode='goodman', terrain='bebop')
    notes = inst.perform()
    exercises = inst.prescribe_exercises()
"""

import json
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .instrument import resolve_terrain, TERRAIN_ALIASES


@dataclass
class Exercise:
    """A single practice exercise."""
    title: str
    description: str       # what to do, plain language
    order: int             # which diagnostic order (0-3) this targets
    difficulty: float      # 0.0-1.0
    duration_bars: int     # suggested duration in bars
    terrain: str           # suggested terrain
    mode: str              # suggested mode
    key: str               # suggested key
    bpm: int               # suggested tempo
    constraints: List[str] # specific rules to follow
    goal: str              # what success looks like
    target_score: float    # what diagnostic score to aim for


class ExerciseGenerator:
    """Generate targeted exercises based on diagnostic weaknesses."""

    ORDER_NAMES = ['position', 'direction', 'curvature', 'structure']

    EXERCISE_TEMPLATES = {
        'position': [
            {
                'title': 'Target Practice',
                'description': 'Play only chord tones. Every note must be a root, 3rd, 5th, or 7th of the current chord.',
                'constraints': ['Only use chord tones', 'No passing notes', 'Hold each note for at least 1 beat'],
                'goal': 'Every note sounds like it belongs',
                'duration_bars': 4,
            },
            {
                'title': 'Root Finder',
                'description': 'Play only roots on beat 1 of every bar. Add one more note per bar each repetition.',
                'constraints': ['Root on beat 1', 'Add 1 note per repetition', 'Maximum 4 notes per bar'],
                'goal': 'Strong harmonic grounding',
                'duration_bars': 8,
            },
            {
                'title': 'Safe Landing',
                'description': 'End every 4-bar phrase on a chord tone. The last note is the most important.',
                'constraints': ['Phrase length = 4 bars', 'Last note must be chord tone', 'No consecutive leaps > 5th'],
                'goal': 'Phrases that resolve confidently',
                'duration_bars': 4,
            },
        ],
        'direction': [
            {
                'title': 'The Arc',
                'description': 'Start low, climb to the peak in bar 3, descend to end. Like telling a story.',
                'constraints': ['Bars 1-2: stay below middle C', 'Bar 3: reach your highest note', 'Bar 4: descend below where you started'],
                'goal': 'Every phrase has a clear shape',
                'duration_bars': 4,
            },
            {
                'title': 'Call and Response',
                'description': 'Play a 2-bar phrase. Then answer it with a related 2-bar phrase. The answer should echo the question.',
                'constraints': ['First phrase ends on a non-tonic', 'Second phrase starts similarly to first', 'Second phrase resolves to tonic'],
                'goal': 'Musical conversation',
                'duration_bars': 4,
            },
            {
                'title': 'Stepwise Commitment',
                'description': 'Move only by step (no leaps) for 4 bars. Then allow one leap per bar. Then free.',
                'constraints': ['Bars 1-4: only steps (1-2 semitones)', 'Bars 5-8: max 1 leap per bar', 'Bars 9-12: free', 'Direction must be intentional'],
                'goal': 'Control over melodic direction',
                'duration_bars': 12,
            },
        ],
        'curvature': [
            {
                'title': 'Velocity Painting',
                'description': 'Play 4 bars of only quarter notes. But vary the volume: beats 1 and 3 strong, 2 and 4 soft.',
                'constraints': ['Only quarter notes', 'Beats 1,3: velocity 80-100', 'Beats 2,4: velocity 40-60', 'Same pitch for all notes'],
                'goal': 'Feel the groove without changing notes',
                'duration_bars': 4,
            },
            {
                'title': 'The Breath',
                'description': 'Play a continuous stream of 8th notes but insert a rest every 4-8 notes. The rest IS the music.',
                'constraints': ['Only 8th notes and rests', 'Rest every 4-8 notes', 'Vary where the rest falls', 'No rhythm pattern can repeat'],
                'goal': 'Controlled breathing in music',
                'duration_bars': 8,
            },
            {
                'title': 'Three Speeds',
                'description': 'Play the same 4-bar phrase three times: once all half notes, once all quarter notes, once all 8th notes. Same notes, different feel.',
                'constraints': ['Same pitches all three times', 'Repetition 1: half notes only', 'Repetition 2: quarter notes', 'Repetition 3: eighth notes'],
                'goal': 'The same music at three different energies',
                'duration_bars': 4,
            },
        ],
        'structure': [
            {
                'title': 'AABA Builder',
                'description': 'Compose an 8-bar AABA form. The A sections share a motif. The B section contrasts completely.',
                'constraints': ['8 bars total', 'Bars 1-2 = A (establish motif)', 'Bars 3-4 = A (repeat/develop)', 'Bars 5-6 = B (contrasting material)', 'Bars 7-8 = A (return home)'],
                'goal': 'Clear architectural form',
                'duration_bars': 8,
            },
            {
                'title': 'Motif Developer',
                'description': 'Create a 3-note motif. Use it as the seed for an entire 8-bar solo. Every phrase relates back to those 3 notes.',
                'constraints': ['Define a 3-note motif in bar 1', 'Every subsequent bar must contain the motif OR a variation', 'Variation = transpose, invert, retrograde, or fragment', 'At least 3 different variations'],
                'goal': 'Unity from a single idea',
                'duration_bars': 8,
            },
            {
                'title': 'The Three Acts',
                'description': 'Structure your solo as a story: Act 1 (introduction, low energy), Act 2 (development, building), Act 3 (climax and resolution).',
                'constraints': ['Act 1 (bars 1-4): sparse, low register', 'Act 2 (bars 5-8): denser, ascending', 'Act 3 (bars 9-12): peak energy, resolve to silence', 'Each act must feel different from the others'],
                'goal': 'A solo that tells a story',
                'duration_bars': 12,
            },
        ],
    }

    # Difficulty adjustments affect tempo, duration, and constraint count
    DIFFICULTY_TEMPO_SCALE = {
        'easy': 0.8,     # slower
        'medium': 1.0,
        'hard': 1.2,     # faster
    }

    def __init__(self):
        pass

    def _difficulty_band(self, difficulty: float) -> str:
        """Classify difficulty into a band."""
        if difficulty < 0.35:
            return 'easy'
        elif difficulty < 0.7:
            return 'medium'
        return 'hard'

    def _pick_template(self, order_name: str, difficulty: float) -> dict:
        """Pick an exercise template appropriate for the difficulty level.

        Easy tends toward simpler templates (index 0), hard toward complex (index 2).
        """
        templates = self.EXERCISE_TEMPLATES[order_name]
        if difficulty < 0.35:
            idx = 0
        elif difficulty < 0.7:
            idx = random.choice([0, 1])
        else:
            idx = random.choice([1, 2])
        return templates[idx]

    def _adjust_bpm(self, base_bpm: int, difficulty: float) -> int:
        """Adjust BPM based on difficulty."""
        band = self._difficulty_band(difficulty)
        scale = self.DIFFICULTY_TEMPO_SCALE[band]
        return max(40, int(base_bpm * scale))

    def _compute_target_score(self, current_score: Optional[float], difficulty: float) -> float:
        """Compute a reasonable target score."""
        if current_score is not None:
            # Target is 0.15-0.30 above current, capped at 1.0
            bump = 0.15 + (difficulty * 0.15)
            return min(1.0, round(current_score + bump, 2))
        # No current score — aim for passing
        return round(0.6 + (difficulty * 0.25), 2)

    def prescribe(self, diagnostic_scores: dict, difficulty: float = 0.5,
                  terrain: str = 'modal_jazz', key: str = 'C', bpm: int = 100) -> List[Exercise]:
        """Generate exercises targeting the weakest diagnostic orders.

        Args:
            diagnostic_scores: {'position': 0.89, 'direction': 0.45, ...}
            difficulty: 0.0 (easy) to 1.0 (hard)
            terrain: Suggested terrain
            key: Suggested key
            bpm: Base tempo

        Returns: 1-3 exercises, targeting the weakest orders first.
        """
        # Sort orders by score ascending (weakest first)
        scored = []
        for name in self.ORDER_NAMES:
            score = diagnostic_scores.get(name)
            if score is None:
                # Missing score means 0 — definitely needs work
                score = 0.0
            scored.append((name, score))

        scored.sort(key=lambda x: x[1])

        # Pick up to 3 weakest orders, but skip any already scoring >= 0.85
        weak = [(name, score) for name, score in scored if score < 0.85]
        if not weak:
            # All strong — give a challenge exercise for the lowest scorer
            weak = [scored[0]]

        exercises = []
        for name, score in weak[:3]:
            ex = self.for_order(name, difficulty=difficulty, current_score=score,
                                terrain=terrain, key=key, bpm=bpm)
            exercises.append(ex)

        return exercises

    def for_order(self, order_name: str, difficulty: float = 0.5,
                  current_score: Optional[float] = None,
                  terrain: str = 'modal_jazz', key: str = 'C', bpm: int = 100) -> Exercise:
        """Generate an exercise for a specific order.

        Args:
            order_name: One of 'position', 'direction', 'curvature', 'structure'
            difficulty: 0.0-1.0
            current_score: Current diagnostic score for this order (if known)
            terrain: Suggested terrain
            key: Suggested key
            bpm: Base tempo

        Returns: A single Exercise.
        """
        order_name = order_name.lower().strip()
        if order_name not in self.ORDER_NAMES:
            raise ValueError(
                f"Unknown order '{order_name}'. Must be one of: {', '.join(self.ORDER_NAMES)}"
            )

        order_idx = self.ORDER_NAMES.index(order_name)
        template = self._pick_template(order_name, difficulty)
        difficulty = max(0.0, min(1.0, difficulty))

        adjusted_bpm = self._adjust_bpm(bpm, difficulty)
        duration = template.get('duration_bars', 4)
        target_score = self._compute_target_score(current_score, difficulty)

        # Adjust constraints for difficulty: easy = fewer, hard = all
        all_constraints = template['constraints']
        if difficulty < 0.35 and len(all_constraints) > 2:
            constraints = all_constraints[:2]
        elif difficulty < 0.7 and len(all_constraints) > 3:
            constraints = all_constraints[:3]
        else:
            constraints = all_constraints

        # Suggest a mode
        mode_suggestions = {
            'position': 'parker',
            'direction': 'miles',
            'curvature': 'ella',
            'structure': 'ellington',
        }

        return Exercise(
            title=template['title'],
            description=template['description'],
            order=order_idx,
            difficulty=round(difficulty, 2),
            duration_bars=duration,
            terrain=terrain,
            mode=mode_suggestions.get(order_name, 'ella'),
            key=key,
            bpm=adjusted_bpm,
            constraints=list(constraints),
            goal=template['goal'],
            target_score=target_score,
        )

    def workout(self, terrain: str = 'modal_jazz', key: str = 'C',
                bpm: int = 100, difficulty: float = 0.5) -> List[Exercise]:
        """Generate a full workout (4 exercises, one per order).

        Args:
            terrain: Musical terrain
            key: Musical key
            bpm: Base tempo
            difficulty: 0.0-1.0

        Returns: List of 4 Exercises, one per order.
        """
        exercises = []
        for order_name in self.ORDER_NAMES:
            ex = self.for_order(order_name, difficulty=difficulty,
                                terrain=terrain, key=key, bpm=bpm)
            exercises.append(ex)
        return exercises

    def from_report_file(self, filepath: str) -> List[Exercise]:
        """Load a diagnostic JSON report and prescribe exercises.

        The JSON should have an 'orders' list with 'name' and 'score' fields,
        or a flat dict of order_name -> score.

        Supports:
            - Goodman DiagnosticReport JSON export
            - Simple {'position': 0.5, ...} dict
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Detect format
        if isinstance(data, dict) and 'orders' in data:
            # Goodman report format
            scores = {}
            for o in data['orders']:
                name = o.get('name', '').lower()
                score = o.get('score', 0.0)
                if name in self.ORDER_NAMES:
                    scores[name] = score
            if not scores:
                raise ValueError("Could not extract order scores from report")
        elif isinstance(data, dict):
            # Simple dict format
            scores = {k: v for k, v in data.items() if k in self.ORDER_NAMES}
            if not scores:
                raise ValueError(f"Expected keys like {self.ORDER_NAMES}, got {list(data.keys())}")
        else:
            raise ValueError(f"Unexpected JSON format: {type(data)}")

        return self.prescribe(scores)


def format_exercise(ex: Exercise) -> str:
    """Format a single exercise for display."""
    order_name = ExerciseGenerator.ORDER_NAMES[ex.order]
    lines = [
        f"🎯 {ex.title}  (targets: {order_name}, difficulty: {ex.difficulty:.0%})",
        f"   {ex.description}",
        f"   Key: {ex.key} | BPM: {ex.bpm} | Bars: {ex.duration_bars} | Mode: {ex.mode} | Terrain: {ex.terrain}",
        f"   Rules:",
    ]
    for c in ex.constraints:
        lines.append(f"     • {c}")
    lines.append(f"   Goal: {ex.goal}")
    lines.append(f"   Target score: {ex.target_score:.0%}")
    return "\n".join(lines)


def format_workout(exercises: List[Exercise]) -> str:
    """Format a workout (list of exercises) for display."""
    lines = [
        "═" * 60,
        "  WORKOUT — Personalized Exercise Plan",
        "═" * 60,
    ]
    for i, ex in enumerate(exercises, 1):
        lines.append(f"\n  Exercise {i}/{len(exercises)}")
        lines.append(format_exercise(ex))
    lines.append(f"\n{'─' * 60}")
    lines.append(f"  Total exercises: {len(exercises)}")
    lines.append("═" * 60)
    return "\n".join(lines)
