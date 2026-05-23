from dataclasses import dataclass
from typing import Dict, Tuple
import json
import math


@dataclass(frozen=True)
class StyleTile:
    """A composer's musical DNA."""
    composer: str
    era: str

    # Melodic DNA
    interval_distribution: Dict[str, float]  # semitone → probability
    melodic_range_semitones: int
    mean_interval: float
    step_vs_leap_ratio: float  # steps (1-2) vs leaps (3+)

    # Rhythmic DNA
    duration_distribution: Dict[str, float]  # "whole","half","quarter","eighth","sixteenth" → prob
    syncopation_rate: float  # 0-1
    mean_note_density: float  # notes per beat
    rhythmic_entropy: float  # complexity measure

    # Harmonic DNA
    consonance_rate: float  # 0-1
    dissonance_rate: float

    # Timing DNA
    timing_precision_ms: float  # how tight the timing is
    swing_factor: float  # 0 straight, 1 full swing

    # Register DNA
    pitch_center: float  # weighted average MIDI pitch
    pitch_range: Tuple[int, int]  # (low, high)

    # Density
    notes_per_bar: float

    def to_json(self, path: str) -> None:
        data = {k: v for k, v in self.__dict__.items()}
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    @classmethod
    def from_json(cls, path: str) -> 'StyleTile':
        with open(path) as f:
            data = json.load(f)
        # Convert pitch_range back to tuple
        if 'pitch_range' in data and isinstance(data['pitch_range'], list):
            data['pitch_range'] = tuple(data['pitch_range'])
        return cls(**data)

    # Field ranges for min-max normalization
    _FIELD_RANGES = [
        ('consonance_rate', 0.0, 1.0),
        ('syncopation_rate', 0.0, 1.0),
        ('mean_interval', 0.0, 12.0),
        ('step_vs_leap_ratio', 0.0, 1.0),
        ('rhythmic_entropy', 0.0, 5.0),
        ('notes_per_bar', 0.0, 20.0),
        ('pitch_center', 20.0, 108.0),
    ]

    def _normalized_vector(self) -> list:
        """Min-max normalized core fields for similarity comparison."""
        vals = {
            'consonance_rate': self.consonance_rate,
            'syncopation_rate': self.syncopation_rate,
            'mean_interval': self.mean_interval,
            'step_vs_leap_ratio': self.step_vs_leap_ratio,
            'rhythmic_entropy': self.rhythmic_entropy,
            'notes_per_bar': self.notes_per_bar,
            'pitch_center': self.pitch_center,
        }
        vec = []
        for name, lo, hi in self._FIELD_RANGES:
            v = vals[name]
            norm = (v - lo) / (hi - lo) if hi > lo else 0.0
            vec.append(max(0.0, min(1.0, norm)))
        return vec

    def _numeric_vector(self) -> list:
        """Extract all numeric fields as a flat vector for comparison."""
        return [
            self.melodic_range_semitones,
            self.mean_interval,
            self.step_vs_leap_ratio,
            self.syncopation_rate,
            self.mean_note_density,
            self.rhythmic_entropy,
            self.consonance_rate,
            self.dissonance_rate,
            self.timing_precision_ms,
            self.swing_factor,
            self.pitch_center,
            self.notes_per_bar,
            self.pitch_range[0],
            self.pitch_range[1],
        ]

    def similarity(self, other: 'StyleTile') -> float:
        """Cosine similarity over min-max normalized fields. 1.0 = identical."""
        v1 = self._normalized_vector()
        v2 = other._normalized_vector()
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a * a for a in v1))
        mag2 = math.sqrt(sum(b * b for b in v2))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return round(dot / (mag1 * mag2), 4)
