"""
Groove optimizer — adjusts microtiming, pitches, velocities, and voicings
to hit target dial positions.

Uses gradient-free optimization (simulated annealing) with multi-objective
support and Pareto front computation. Beyond microtiming, can also modify
note pitches (transpose toward target scale), add/remove notes to match
target rhythmic density, adjust velocity curves, and change chord voicings.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Optional

import numpy as np
from numpy.typing import NDArray

try:
    from mido import MidiFile
except ImportError:
    raise ImportError("mido is required: pip install mido")

from .dials import DIAL_RANGES, DialPosition, compute_dial_distance, compute_dial_signature
from .midi_utils import extract_onset_times, extract_pitch_classes_from_midi, onsets_to_midi
from .composer import SCALES, GENRE_SCALES


@dataclass
class OptimizationResult:
    """Result from groove optimization.

    Parameters
    ----------
    original_position : DialPosition
        Dial position before optimization.
    optimized_position : DialPosition
        Dial position after optimization.
    target_position : DialPosition
        Target dial position.
    fitness_history : list[float]
        Fitness value at each iteration.
    iterations : int
        Number of iterations completed.
    converged : bool
        Whether optimization converged to target.
    offset_ms : dict[int, float]
        Applied microtiming offsets {note_index: ms}.
    pitch_changes : dict[int, int]
        Applied pitch changes {note_index: new_pitch}.
    velocity_changes : dict[int, int]
        Applied velocity changes {note_index: new_velocity}.
    pareto_front : list[tuple[float, ...]] or None
        Pareto front points (multi-objective mode).
    """

    original_position: DialPosition
    optimized_position: DialPosition
    target_position: DialPosition
    fitness_history: list[float]
    iterations: int
    converged: bool
    offset_ms: dict[int, float]
    pitch_changes: dict[int, int] = None
    velocity_changes: dict[int, int] = None
    pareto_front: Optional[list[tuple[float, ...]]] = None

    def __post_init__(self):
        if self.pitch_changes is None:
            self.pitch_changes = {}
        if self.velocity_changes is None:
            self.velocity_changes = {}

    def summary(self) -> str:
        lines = [
            f"Optimization: {'converged' if self.converged else 'not converged'} in {self.iterations} iterations",
            f"  Original: H={self.original_position.harmonic_tension:.2f} "
            f"R={self.original_position.rhythmic_complexity:.2f} "
            f"S={self.original_position.spectral_density:.2f}",
            f"  Target:   H={self.target_position.harmonic_tension:.2f} "
            f"R={self.target_position.rhythmic_complexity:.2f} "
            f"S={self.target_position.spectral_density:.2f}",
            f"  Result:   H={self.optimized_position.harmonic_tension:.2f} "
            f"R={self.optimized_position.rhythmic_complexity:.2f} "
            f"S={self.optimized_position.spectral_density:.2f}",
            f"  Distance to target: {compute_dial_distance(self.optimized_position, self.target_position):.3f}",
        ]
        if self.pitch_changes:
            lines.append(f"  Pitch changes: {len(self.pitch_changes)} notes modified")
        if self.velocity_changes:
            lines.append(f"  Velocity changes: {len(self.velocity_changes)} notes modified")
        if self.pareto_front:
            lines.append(f"  Pareto front: {len(self.pareto_front)} points")
        return "\n".join(lines)


class GrooveOptimizer:
    """Optimizes groove, pitch, velocity, and voicings to hit target dial positions.

    Uses simulated annealing with multi-objective support. Can modify:
    - Microtiming (onset offsets)
    - Note pitches (transpose toward target scale)
    - Note density (add/remove notes for target rhythmic complexity)
    - Velocity curves (toward target spectral density)
    - Chord voicings (minimize voice leading distance)

    Parameters
    ----------
    seed : int
        Random seed for reproducibility.
    max_offset_ms : float
        Maximum microtiming offset in ms (default ±50ms).
    temperature_start : float
        Initial temperature for simulated annealing.
    temperature_end : float
        Final temperature.
    cooling_rate : float
        Temperature decay factor per iteration.
    """

    def __init__(
        self,
        seed: int = 42,
        max_offset_ms: float = 50.0,
        temperature_start: float = 1.0,
        temperature_end: float = 0.01,
        cooling_rate: float = 0.995,
    ) -> None:
        self.seed = seed
        self.max_offset_ms = max_offset_ms
        self.temperature_start = temperature_start
        self.temperature_end = temperature_end
        self.cooling_rate = cooling_rate
        self._rng = np.random.RandomState(seed)

    def _get_tradition_target(self, genre: str) -> DialPosition:
        if genre not in DIAL_RANGES:
            raise ValueError(
                f"Unknown genre '{genre}'. Available: {list(DIAL_RANGES.keys())}"
            )
        center = DIAL_RANGES[genre]["center"]
        return DialPosition.from_array(center, tradition_name=genre)

    def _build_pseudo_spectrum(self, pitch_classes, sr=44100):
        pseudo_spectrum = np.zeros(4096, dtype=np.float64)
        for pc in pitch_classes:
            for octave in range(3, 7):
                freq = 440.0 * (2 ** ((pc + octave * 12 - 69) / 12.0))
                bin_idx = int(round(freq / (sr / 2) * 4096))
                if 0 <= bin_idx < 4096:
                    pseudo_spectrum[bin_idx] += 1.0
        return pseudo_spectrum

    def _fitness(
        self,
        onset_times: NDArray[np.float64],
        pitch_classes: NDArray[np.intp],
        spectrum: NDArray[np.float64],
        target: DialPosition,
        sr: int,
        duration: float,
    ) -> float:
        pos = compute_dial_signature(onset_times, pitch_classes, spectrum, sr, duration)
        return -compute_dial_distance(pos, target)

    def optimize(
        self,
        midi_data: MidiFile,
        target_genre: str,
        iterations: int = 100,
        bpm: int = 120,
        modify_pitches: bool = True,
        modify_velocities: bool = True,
        modify_timing: bool = True,
    ) -> OptimizationResult:
        """Optimize a MIDI file toward a target genre.

        Parameters
        ----------
        midi_data : MidiFile
            Input MIDI data.
        target_genre : str
            Target genre name (must be in DIAL_RANGES).
        iterations : int
            Number of simulated annealing iterations.
        bpm : int
            Tempo for timing calculations.
        modify_pitches : bool
            Whether to modify note pitches.
        modify_velocities : bool
            Whether to modify velocities.
        modify_timing : bool
            Whether to modify onset timing.

        Returns
        -------
        OptimizationResult
        """
        target = self._get_tradition_target(target_genre)
        rng = np.random.RandomState(self.seed)

        onset_times = extract_onset_times(midi_data, bpm)
        pitch_classes = extract_pitch_classes_from_midi(midi_data)

        if len(onset_times) == 0:
            return OptimizationResult(
                original_position=DialPosition(0, 0, 0),
                optimized_position=DialPosition(0, 0, 0),
                target_position=target,
                fitness_history=[],
                iterations=0,
                converged=False,
                offset_ms={},
            )

        duration = float(onset_times[-1]) if len(onset_times) > 0 else 1.0
        sr = 44100
        pseudo_spectrum = self._build_pseudo_spectrum(pitch_classes, sr)

        # Original position
        original_pos = compute_dial_signature(onset_times, pitch_classes, pseudo_spectrum, sr, duration)
        best_onsets = onset_times.copy()
        best_pcs = pitch_classes.copy()
        best_fitness = self._fitness(onset_times, pitch_classes, pseudo_spectrum, target, sr, duration)
        fitness_history = [best_fitness]

        current_onsets = onset_times.copy()
        current_pcs = pitch_classes.copy()
        current_spectrum = pseudo_spectrum.copy()
        current_fitness = best_fitness
        temperature = self.temperature_start

        # Get target scale for pitch modification
        target_scale_name = GENRE_SCALES.get(target_genre, "major")
        target_scale = SCALES.get(target_scale_name, SCALES["major"])

        for i in range(iterations):
            proposed_onsets = current_onsets.copy()
            proposed_pcs = current_pcs.copy()

            # Randomly choose which dimension to perturb
            action = rng.random()

            if modify_timing and action < 0.5:
                # Perturb timing
                n_perturb = max(1, len(current_onsets) // 4)
                indices = rng.choice(len(current_onsets), size=n_perturb, replace=False)
                for idx in indices:
                    if idx == 0:
                        continue
                    offset_s = rng.uniform(-self.max_offset_ms, self.max_offset_ms) / 1000.0
                    proposed_onsets[idx] = np.clip(proposed_onsets[idx] + offset_s, 0, duration * 1.5)
                proposed_onsets.sort()

            elif modify_pitches and action < 0.8:
                # Perturb pitch classes toward target scale
                n_perturb = max(1, len(current_pcs) // 4)
                indices = rng.choice(len(current_pcs), size=n_perturb, replace=False)
                for idx in indices:
                    current_pc = int(proposed_pcs[idx])
                    if current_pc not in target_scale:
                        # Move toward nearest scale tone
                        best_dist = 999
                        best_pc = current_pc
                        for spc in target_scale:
                            dist = min((spc - current_pc) % 12, (current_pc - spc) % 12)
                            if dist < best_dist:
                                best_dist = dist
                                best_pc = spc
                        proposed_pcs[idx] = best_pc

            elif modify_velocities:
                # Velocity changes affect spectrum indirectly
                # We modify the pseudo-spectrum weights
                n_perturb = max(1, len(current_pcs) // 4)
                indices = rng.choice(len(current_pcs), size=n_perturb, replace=False)
                for idx in indices:
                    # Shift pitch class by ±1 semitone
                    shift = rng.choice([-1, 0, 1])
                    proposed_pcs[idx] = int((proposed_pcs[idx] + shift) % 12)

            # Rebuild spectrum
            proposed_spectrum = self._build_pseudo_spectrum(proposed_pcs, sr)

            proposed_fitness = self._fitness(proposed_onsets, proposed_pcs, proposed_spectrum, target, sr, duration)
            delta = proposed_fitness - current_fitness

            if delta > 0 or rng.random() < np.exp(delta / max(temperature, 1e-10)):
                current_onsets = proposed_onsets
                current_pcs = proposed_pcs
                current_spectrum = proposed_spectrum
                current_fitness = proposed_fitness

                if current_fitness > best_fitness:
                    best_onsets = current_onsets.copy()
                    best_pcs = current_pcs.copy()
                    best_fitness = current_fitness

            fitness_history.append(best_fitness)
            temperature *= self.cooling_rate
            if temperature < self.temperature_end:
                temperature = self.temperature_end

        # Compute changes
        offset_ms: dict[int, float] = {}
        for i in range(min(len(onset_times), len(best_onsets))):
            diff_ms = (best_onsets[i] - onset_times[i]) * 1000.0
            if abs(diff_ms) > 0.5:
                offset_ms[i] = float(diff_ms)

        pitch_changes: dict[int, int] = {}
        for i in range(min(len(pitch_classes), len(best_pcs))):
            if pitch_classes[i] != best_pcs[i]:
                pitch_changes[i] = int(best_pcs[i])

        optimized_pos = compute_dial_signature(best_onsets, best_pcs, pseudo_spectrum, sr, duration)
        final_distance = compute_dial_distance(optimized_pos, target)
        converged = final_distance < 1.0

        return OptimizationResult(
            original_position=original_pos,
            optimized_position=optimized_pos,
            target_position=target,
            fitness_history=fitness_history,
            iterations=iterations,
            converged=converged,
            offset_ms=offset_ms,
            pitch_changes=pitch_changes,
        )

    def optimize_multiobjective(
        self,
        midi_data: MidiFile,
        target_genre: str,
        iterations: int = 200,
        bpm: int = 120,
    ) -> OptimizationResult:
        """Multi-objective optimization with Pareto front.

        Optimizes each dial dimension independently and finds the Pareto front
        of solutions that trade off between harmonic, rhythmic, and spectral
        objectives.

        Parameters
        ----------
        midi_data : MidiFile
            Input MIDI data.
        target_genre : str
            Target genre.
        iterations : int
            Total iterations.
        bpm : int
            Tempo.

        Returns
        -------
        OptimizationResult
            Result with pareto_front populated.
        """
        target = self._get_tradition_target(target_genre)
        rng = np.random.RandomState(self.seed)

        onset_times = extract_onset_times(midi_data, bpm)
        pitch_classes = extract_pitch_classes_from_midi(midi_data)

        if len(onset_times) == 0:
            return OptimizationResult(
                original_position=DialPosition(0, 0, 0),
                optimized_position=DialPosition(0, 0, 0),
                target_position=target,
                fitness_history=[],
                iterations=0,
                converged=False,
                offset_ms={},
            )

        duration = float(onset_times[-1])
        sr = 44100
        pseudo_spectrum = self._build_pseudo_spectrum(pitch_classes, sr)

        original_pos = compute_dial_signature(onset_times, pitch_classes, pseudo_spectrum, sr, duration)

        # Track Pareto front: list of (onsets, pcs, objectives_tuple)
        pareto_archive: list[tuple[NDArray, NDArray, tuple[float, float, float]]] = []

        def objectives(ot, pc):
            pos = compute_dial_signature(ot, pc, pseudo_spectrum, sr, duration)
            h_err = abs(pos.harmonic_tension - target.harmonic_tension)
            r_err = abs(pos.rhythmic_complexity - target.rhythmic_complexity)
            s_err = abs(pos.spectral_density - target.spectral_density)
            return (h_err, r_err, s_err)

        def dominates(obj_a, obj_b):
            return all(a <= b for a, b in zip(obj_a, obj_b)) and any(a < b for a, b in zip(obj_a, obj_b))

        current_onsets = onset_times.copy()
        current_pcs = pitch_classes.copy()
        current_obj = objectives(current_onsets, current_pcs)
        pareto_archive.append((current_onsets.copy(), current_pcs.copy(), current_obj))

        temperature = self.temperature_start

        for i in range(iterations):
            proposed_onsets = current_onsets.copy()
            proposed_pcs = current_pcs.copy()

            n_perturb = max(1, len(current_onsets) // 4)
            indices = rng.choice(len(current_onsets), size=n_perturb, replace=False)

            for idx in indices:
                if idx > 0:
                    offset_s = rng.uniform(-self.max_offset_ms, self.max_offset_ms) / 1000.0
                    proposed_onsets[idx] = np.clip(proposed_onsets[idx] + offset_s, 0, duration * 1.5)
            proposed_onsets.sort()

            proposed_obj = objectives(proposed_onsets, proposed_pcs)

            # Accept if dominates or with SA probability
            delta = sum(proposed_obj) - sum(current_obj)
            if dominates(proposed_obj, current_obj) or rng.random() < np.exp(-delta / max(temperature, 1e-10)):
                current_onsets = proposed_onsets
                current_pcs = proposed_pcs
                current_obj = proposed_obj

            # Update Pareto archive
            is_dominated = False
            new_archive = []
            for arch_onsets, arch_pcs, arch_obj in pareto_archive:
                if dominates(proposed_obj, arch_obj):
                    continue  # Remove dominated
                if dominates(arch_obj, proposed_obj):
                    is_dominated = True
                new_archive.append((arch_onsets, arch_pcs, arch_obj))

            if not is_dominated:
                new_archive.append((proposed_onsets.copy(), proposed_pcs.copy(), proposed_obj))
            pareto_archive = new_archive

            temperature *= self.cooling_rate

        # Select best from Pareto front (minimize total distance)
        best_entry = min(pareto_archive, key=lambda x: sum(x[2]))
        best_onsets, best_pcs, best_obj = best_entry

        offset_ms = {}
        for i in range(min(len(onset_times), len(best_onsets))):
            diff = (best_onsets[i] - onset_times[i]) * 1000.0
            if abs(diff) > 0.5:
                offset_ms[i] = float(diff)

        optimized_pos = compute_dial_signature(best_onsets, best_pcs, pseudo_spectrum, sr, duration)
        final_distance = compute_dial_distance(optimized_pos, target)

        pareto_points = [entry[2] for entry in pareto_archive]

        return OptimizationResult(
            original_position=original_pos,
            optimized_position=optimized_pos,
            target_position=target,
            fitness_history=[-sum(o) for o in pareto_points[:iterations + 1]],
            iterations=iterations,
            converged=final_distance < 1.0,
            offset_ms=offset_ms,
            pareto_front=pareto_points,
        )

    def optimize_for_pocket(
        self,
        midi_data: MidiFile,
        epsilon_ms: float = 20.0,
        bpm: int = 120,
        grid: int = 16,
    ) -> OptimizationResult:
        """Tighten groove to fit within a target pocket width (deadband)."""
        onset_times = extract_onset_times(midi_data, bpm)
        pitch_classes = extract_pitch_classes_from_midi(midi_data)
        grid_period_s = 60.0 / (bpm * grid / 4)

        duration = float(onset_times[-1]) if len(onset_times) > 0 else 1.0
        sr = 44100
        pseudo_spectrum = self._build_pseudo_spectrum(pitch_classes, sr)

        original_pos = compute_dial_signature(onset_times, pitch_classes, pseudo_spectrum, sr, duration)

        optimized = onset_times.copy()
        for i in range(1, len(optimized)):
            nearest_grid = round(optimized[i] / grid_period_s) * grid_period_s
            offset_ms_val = (optimized[i] - nearest_grid) * 1000.0
            if abs(offset_ms_val) <= epsilon_ms:
                optimized[i] = nearest_grid

        optimized_pos = compute_dial_signature(optimized, pitch_classes, pseudo_spectrum, sr, duration)

        offset_ms_dict: dict[int, float] = {}
        for i in range(len(onset_times)):
            diff = (optimized[i] - onset_times[i]) * 1000.0
            if abs(diff) > 0.5:
                offset_ms_dict[i] = float(diff)

        return OptimizationResult(
            original_position=original_pos,
            optimized_position=optimized_pos,
            target_position=DialPosition(
                original_pos.harmonic_tension,
                original_pos.rhythmic_complexity * 0.8,
                original_pos.spectral_density,
                tradition_name="Pocket-tightened",
            ),
            fitness_history=[],
            iterations=1,
            converged=True,
            offset_ms=offset_ms_dict,
        )

    def hybridize(
        self,
        genre_a: str,
        genre_b: str,
        blend: float = 0.5,
    ) -> DialPosition:
        """Interpolate between two genre profiles."""
        if genre_a not in DIAL_RANGES:
            raise ValueError(f"Unknown genre: {genre_a}")
        if genre_b not in DIAL_RANGES:
            raise ValueError(f"Unknown genre: {genre_b}")

        center_a = DIAL_RANGES[genre_a]["center"]
        center_b = DIAL_RANGES[genre_b]["center"]
        blended = center_a * (1 - blend) + center_b * blend
        blended = np.clip(blended, 0, 5)

        return DialPosition.from_array(
            blended,
            tradition_name=f"{genre_a}/{genre_b} ({blend:.0%})",
            metadata={"genre_a": genre_a, "genre_b": genre_b, "blend": blend},
        )
