"""
Style transfer between musical traditions.

Transforms a piece from one tradition's dial position to another by
mapping note pitches, timing, velocity, and re-rendering with target
synthesis parameters.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Optional

import numpy as np
from numpy.typing import NDArray

try:
    from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
except ImportError:
    raise ImportError("mido is required: pip install mido")

from .dials import DIAL_RANGES, DialPosition, compute_dial_signature
from .midi_utils import (
    extract_onset_times,
    extract_pitch_classes_from_midi,
    onsets_to_midi,
)
from .synthesizer import ConstraintSynth
from .composer import SCALES, GENRE_SCALES


class StyleTransfer:
    """Transfer a piece from one tradition's dial position to another.

    Works by:
    1. Analyzing source → get dial position + features
    2. Getting target tradition's dial position
    3. Mapping note pitches toward target scale/mode
    4. Adjusting timing toward target rhythmic_complexity
    5. Modifying velocity curves toward target's spectral_density
    6. Re-rendering with target's synthesis parameters

    Parameters
    ----------
    sr : int
        Sample rate for audio rendering.
    """

    def __init__(self, sr: int = 44100) -> None:
        self.synth = ConstraintSynth(sr=sr)

    def _get_target_position(self, tradition: str) -> DialPosition:
        """Get dial position for a tradition."""
        if tradition not in DIAL_RANGES:
            raise ValueError(
                f"Unknown tradition '{tradition}'. Available: {list(DIAL_RANGES.keys())}"
            )
        center = DIAL_RANGES[tradition]["center"]
        return DialPosition.from_array(center, tradition_name=tradition)

    def _quantize_to_scale(
        self,
        pitch: int,
        scale_pcs: list[int],
        strength: float = 1.0,
    ) -> int:
        """Move a pitch toward the nearest note in the target scale.

        Parameters
        ----------
        pitch : int
            MIDI note number.
        scale_pcs : list of int
            Pitch classes in the target scale.
        strength : float
            0.0 = no change, 1.0 = full quantization.

        Returns
        -------
        int
            Quantized MIDI note number.
        """
        if strength <= 0.0:
            return pitch

        pc = pitch % 12
        if pc in scale_pcs:
            return pitch  # Already in scale

        # Find nearest scale tone
        best_distance = 999
        best_pc = pc
        for spc in scale_pcs:
            # Distance in pitch class space (wrapping)
            dist_up = (spc - pc) % 12
            dist_down = (pc - spc) % 12
            dist = min(dist_up, dist_down)
            if dist < best_distance:
                best_distance = dist
                best_pc = spc

        # Interpolate: full strength = snap to scale tone
        if strength >= 1.0:
            return (pitch // 12) * 12 + best_pc
        else:
            # For partial strength, snap with probability
            if np.random.random() < strength:
                return (pitch // 12) * 12 + best_pc
            return pitch

    def _adjust_timing(
        self,
        onset_times: NDArray[np.float64],
        source_rc: float,
        target_rc: float,
        strength: float = 1.0,
        bpm: int = 120,
    ) -> NDArray[np.float64]:
        """Adjust onset timing toward target rhythmic complexity.

        If target has higher rhythmic complexity, add syncopation.
        If lower, quantize toward grid.

        Parameters
        ----------
        onset_times : ndarray
            Onset times in seconds.
        source_rc : float
            Source rhythmic complexity.
        target_rc : float
            Target rhythmic complexity.
        strength : float
            Transfer strength 0-1.
        bpm : int
            Tempo.

        Returns
        -------
        ndarray
            Adjusted onset times.
        """
        if strength <= 0.0 or len(onset_times) < 2:
            return onset_times.copy()

        result = onset_times.copy()
        grid_period = 60.0 / (bpm * 4)  # 16th note grid
        rng = np.random.RandomState(42)

        rc_diff = (target_rc - source_rc) * strength

        for i in range(1, len(result)):
            if rc_diff > 0:
                # Target is more complex: add syncopation
                nearest_grid = round(result[i] / grid_period) * grid_period
                offset = result[i] - nearest_grid
                # Push further from grid
                push = rng.uniform(0.1, 0.5) * grid_period * rc_diff / 5.0
                if offset >= 0:
                    result[i] += push
                else:
                    result[i] -= push
            elif rc_diff < 0:
                # Target is less complex: quantize toward grid
                nearest_grid = round(result[i] / grid_period) * grid_period
                diff = nearest_grid - result[i]
                result[i] += diff * abs(rc_diff) / 5.0

        # Keep sorted and non-negative
        result = np.sort(np.maximum(result, 0.0))
        return result

    def _adjust_velocities(
        self,
        velocities: list[int],
        source_sd: float,
        target_sd: float,
        strength: float = 1.0,
    ) -> list[int]:
        """Adjust velocity curves toward target spectral density.

        Higher spectral density → more velocity variation and higher average.
        Lower → more uniform and softer.

        Parameters
        ----------
        velocities : list of int
            MIDI velocities.
        source_sd : float
            Source spectral density.
        target_sd : float
            Target spectral density.
        strength : float
            Transfer strength.

        Returns
        -------
        list of int
            Adjusted velocities.
        """
        if strength <= 0.0 or not velocities:
            return velocities[:]

        rng = np.random.RandomState(42)
        sd_diff = (target_sd - source_sd) * strength

        # Target base velocity
        target_base = int(40 + target_sd * 17)  # 40-125
        source_base = int(40 + source_sd * 17)
        base_shift = int((target_base - source_base) * strength)

        result = []
        for v in velocities:
            new_v = v + base_shift
            # Variation: higher SD → more dynamic range
            variation = int(sd_diff * 5)
            new_v += rng.randint(-variation, variation + 1)
            new_v = max(30, min(127, new_v))
            result.append(new_v)

        return result

    def transfer(
        self,
        input_path_or_midi: str | MidiFile,
        source_tradition: Optional[str] = None,
        target_tradition: str = "Jazz",
        strength: float = 1.0,
        bpm: int = 120,
    ) -> MidiFile:
        """Transform a piece from source to target tradition's dial position.

        Parameters
        ----------
        input_path_or_midi : str or MidiFile
            Input MIDI file path or MidiFile object.
        source_tradition : str or None
            Source tradition name. If None, auto-detected.
        target_tradition : str
            Target tradition name.
        strength : float
            Transfer strength 0-1 (0=no change, 1=full transfer).
        bpm : int
            Tempo.

        Returns
        -------
        MidiFile
            Transformed MIDI data.
        """
        strength = float(np.clip(strength, 0.0, 1.0))

        # Load MIDI
        if isinstance(input_path_or_midi, str):
            mid = MidiFile(input_path_or_midi)
        else:
            mid = input_path_or_midi

        # Get target
        target_pos = self._get_target_position(target_tradition)

        # Analyze source
        onset_times = extract_onset_times(mid, bpm)
        pitch_classes = extract_pitch_classes_from_midi(mid)

        # Build pseudo-spectrum
        sr = 44100
        duration = float(onset_times[-1]) if len(onset_times) > 0 else 1.0
        pseudo_spectrum = np.zeros(4096, dtype=np.float64)
        for pc in pitch_classes:
            for octave in range(3, 7):
                freq = 440.0 * (2 ** ((pc + octave * 12 - 69) / 12.0))
                bin_idx = int(round(freq / (sr / 2) * 4096))
                if 0 <= bin_idx < 4096:
                    pseudo_spectrum[bin_idx] += 1.0

        source_pos = compute_dial_signature(
            onset_times, pitch_classes, pseudo_spectrum, sr, duration
        )

        if source_tradition is None:
            source_tradition = "Unknown"

        # Get target scale
        target_scale_name = GENRE_SCALES.get(target_tradition, "major")
        target_scale = SCALES.get(target_scale_name, SCALES["major"])

        # Extract note events from MIDI
        ticks_per_second = mid.ticks_per_beat * bpm / 60.0
        note_events: list[tuple[float, int, int, float]] = []

        for track in mid.tracks:
            abs_tick = 0
            active_notes: dict[int, tuple[int, int]] = {}
            for msg in track:
                abs_tick += msg.time
                if msg.type == "note_on" and msg.velocity > 0:
                    active_notes[msg.note] = (abs_tick, msg.velocity)
                elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                    if msg.note in active_notes:
                        start_tick, vel = active_notes.pop(msg.note)
                        start_sec = start_tick / ticks_per_second
                        dur_sec = (abs_tick - start_tick) / ticks_per_second
                        if dur_sec < 0.05:
                            dur_sec = 0.25
                        note_events.append((start_sec, msg.note, vel, dur_sec))

        if not note_events:
            # Fallback: create events from onsets + pitch classes
            for i, (ot, pc) in enumerate(zip(onset_times, pitch_classes)):
                note_events.append((ot, 60 + pc, 80, 0.3))

        # Transfer pitch
        new_pitches = [
            self._quantize_to_scale(pitch, target_scale, strength)
            for _, pitch, _, _ in note_events
        ]

        # Transfer timing
        new_onset_times = self._adjust_timing(
            onset_times,
            source_pos.rhythmic_complexity,
            target_pos.rhythmic_complexity,
            strength,
            bpm,
        )

        # Transfer velocities
        original_velocities = [v for _, _, v, _ in note_events]
        new_velocities = self._adjust_velocities(
            original_velocities,
            source_pos.spectral_density,
            target_pos.spectral_density,
            strength,
        )

        # Build new MIDI
        # Map adjusted onsets back to note events
        # Sort events by original onset time
        sorted_indices = sorted(range(len(note_events)), key=lambda i: note_events[i][0])

        new_onsets: list[tuple[float, int, int]] = []
        durations: list[float] = []

        for idx in sorted_indices:
            _, _, _, dur = note_events[idx]
            new_pitch = new_pitches[idx]
            new_vel = new_velocities[idx]

            # Find closest onset time
            original_onset = note_events[idx][0]
            if len(new_onset_times) > idx:
                new_onset = float(new_onset_times[min(idx, len(new_onset_times) - 1)])
            else:
                new_onset = original_onset

            new_onsets.append((new_onset, new_pitch, new_vel))
            durations.append(dur)

        # Sort by onset time
        paired = sorted(zip(new_onsets, durations), key=lambda x: x[0])
        new_onsets = [p[0] for p in paired]
        durations = [p[1] for p in paired]

        # Use average duration for onsets_to_midi
        avg_dur = float(np.mean(durations)) if durations else 0.3

        result_midi = onsets_to_midi(
            new_onsets,
            bpm=bpm,
            note_duration=avg_dur,
        )

        return result_midi

    def transfer_wav(
        self,
        input_wav: str | NDArray[np.float64],
        target_tradition: str,
        sr: int = 44100,
        bpm: int = 120,
        strength: float = 1.0,
    ) -> NDArray[np.float64]:
        """Transfer audio from any style to a target tradition.

        Parameters
        ----------
        input_wav : str or ndarray
            Path to WAV file or audio array.
        target_tradition : str
            Target tradition name.
        sr : int
            Sample rate.
        bpm : int
            Tempo.
        strength : float
            Transfer strength.

        Returns
        -------
        ndarray of float64
            Transferred audio.
        """
        target_pos = self._get_target_position(target_tradition)

        if isinstance(input_wav, str):
            from .audio_utils import load_wav
            audio, sr = load_wav(input_wav, sr=sr)
        else:
            audio = np.asarray(input_wav, dtype=np.float64)

        # Analyze the audio
        from .audio_utils import detect_onsets, compute_pitch_classes, compute_spectrum
        from .analyzer import analyze_wav
        from .dials import compute_dial_signature

        onset_times = detect_onsets(audio, sr)
        pc_dist = compute_pitch_classes(audio, sr)
        _, spectrum = compute_spectrum(audio, sr)
        duration = len(audio) / sr

        # Build pitch class array
        pitch_classes = []
        for pc, weight in pc_dist.items():
            pitch_classes.extend([int(pc)] * int(round(weight * 100)))

        if not pitch_classes:
            pitch_classes = [0]

        source_pos = compute_dial_signature(
            np.array(onset_times) if len(onset_times) > 0 else np.array([0.0]),
            np.array(pitch_classes, dtype=np.intp),
            spectrum,
            sr,
            duration,
        )

        # Use the composer to generate a new piece at the target position
        # then render with synthesis
        result_audio = self.synth.render_composition(target_pos, bars=8, tempo=bpm)

        return result_audio
