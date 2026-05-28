"""
Audio synthesis engine for constraint-toolkit.

Generates audio from dial parameters using additive/subtractive synthesis
with ADSR envelopes, effects chain (reverb, chorus), and anti-aliasing.
"""

from __future__ import annotations

import struct
import wave
from pathlib import Path
from typing import Optional

import numpy as np
from numpy.typing import NDArray

try:
    from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
except ImportError:
    raise ImportError("mido is required: pip install mido")

from .dials import DIAL_RANGES, DialPosition
from .midi_utils import extract_onset_times, extract_pitch_classes_from_midi


class ConstraintSynth:
    """Synthesizer that generates audio from dial parameters.

    Uses additive/subtractive synthesis with harmonics controlled by
    spectral_density and harmonic_tension dials. Includes ADSR envelopes,
    delay-based reverb, and chorus effects.

    Parameters
    ----------
    sr : int
        Sample rate in Hz (default 44100).
    """

    def __init__(self, sr: int = 44100) -> None:
        self.sr = sr

    # ------------------------------------------------------------------
    # Core synthesis
    # ------------------------------------------------------------------

    def _generate_harmonics(
        self,
        freq: float,
        duration: float,
        velocity: float,
        spectral_density: float,
        harmonic_tension: float,
    ) -> NDArray[np.float64]:
        """Generate a tone with additive harmonics.

        Parameters
        ----------
        freq : float
            Fundamental frequency in Hz.
        duration : float
            Duration in seconds.
        velocity : float
            MIDI velocity 0-127, mapped to amplitude.
        spectral_density : float
            Dial value 0-5 controlling number and brightness of harmonics.
        harmonic_tension : float
            Dial value 0-5 controlling harmonic content and inharmonicity.

        Returns
        -------
        ndarray of float64
            Synthesized tone, normalized to [-1, 1].
        """
        n_samples = int(np.ceil(duration * self.sr))
        if n_samples <= 0 or freq <= 0:
            return np.zeros(max(n_samples, 1), dtype=np.float64)

        t = np.arange(n_samples, dtype=np.float64) / self.sr

        # Amplitude from velocity
        amplitude = (velocity / 127.0) * 0.8  # headroom for effects

        # Determine number of harmonics from spectral_density
        if spectral_density < 1.0:
            n_harmonics = 2  # fundamental + 2nd harmonic (flute-like)
        elif spectral_density < 3.0:
            n_harmonics = 8  # up to 8th harmonic (piano-like)
        else:
            n_harmonics = 32  # bright spectrum (brass-like)

        # Nyquist limit: don't generate harmonics above sr/2
        max_harmonic = int(self.sr / 2.0 / freq)
        n_harmonics = min(n_harmonics, max_harmonic)
        if n_harmonics < 1:
            n_harmonics = 1

        # Build the tone
        tone = np.zeros(n_samples, dtype=np.float64)

        for h in range(1, n_harmonics + 1):
            harmonic_freq = freq * h

            # Amplitude rolloff: 1/n for medium, adjusted by density
            if spectral_density < 1.0:
                # Flute-like: fundamental dominant, weak overtones
                harm_amp = 1.0 / (h ** 2)
            elif spectral_density < 3.0:
                # Piano-like: 1/n rolloff
                harm_amp = 1.0 / h
            else:
                # Brass-like: slower rolloff, brighter
                harm_amp = 1.0 / (h ** 0.5)

            # Harmonic tension controls which harmonics are present
            if harmonic_tension < 1.5:
                # Low tension: prefer even harmonics (clarinet-like, warm)
                if h > 1 and h % 2 == 1:
                    harm_amp *= 0.15  # suppress odd harmonics
            elif harmonic_tension > 3.5:
                # High tension: all harmonics + slight inharmonicity (bell-like)
                inharmonicity = 1.0 + 0.002 * harmonic_tension * (h - 1)
                harmonic_freq *= inharmonicity
            # Medium tension (1.5-3.5): all harmonics equally, no modification

            # Generate sine for this harmonic
            phase = 2.0 * np.pi * harmonic_freq * t
            tone += harm_amp * np.sin(phase)

        # Normalize per-harmonic sum to prevent excessive amplitude
        if n_harmonics > 0:
            # Peak theoretical amplitude from harmonic sum
            peak = sum(1.0 / max(1, h) for h in range(1, n_harmonics + 1))
            tone /= max(peak, 1.0)

        tone *= amplitude
        return tone

    def _apply_adsr(
        self,
        audio: NDArray[np.float64],
        rhythmic_complexity: float,
        duration: float,
    ) -> NDArray[np.float64]:
        """Apply ADSR envelope shaped by rhythmic_complexity.

        Low complexity: long sustain, slow attack (pad-like).
        High complexity: short attack, fast decay (percussive).

        Parameters
        ----------
        audio : ndarray
            Input audio.
        rhythmic_complexity : float
            Dial value 0-5.
        duration : float
            Note duration in seconds.

        Returns
        -------
        ndarray
            Enveloped audio.
        """
        n = len(audio)
        if n == 0:
            return audio

        # Map rhythmic_complexity to envelope parameters
        # Attack: 5-50ms for high complexity, 100-500ms for low
        attack_time = 0.5 * (1.0 - rhythmic_complexity / 5.0) + 0.005
        # Decay: 50-200ms for high complexity, 200-500ms for low
        decay_time = 0.3 * (1.0 - rhythmic_complexity / 5.0) + 0.05
        # Sustain level: 0.3-0.7
        sustain_level = 0.3 + 0.4 * (1.0 - rhythmic_complexity / 5.0)
        # Release: 20-200ms
        release_time = 0.15 * (1.0 - rhythmic_complexity / 5.0) + 0.02

        # Ensure attack + decay + release < duration
        total_env = attack_time + decay_time + release_time
        if total_env > duration * 0.9:
            scale = (duration * 0.9) / total_env
            attack_time *= scale
            decay_time *= scale
            release_time *= scale

        envelope = np.ones(n, dtype=np.float64)

        attack_samples = min(int(attack_time * self.sr), n)
        decay_samples = min(int(decay_time * self.sr), n)
        release_samples = min(int(release_time * self.sr), n)

        # Attack: 0 -> 1
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0.0, 1.0, attack_samples)

        # Decay: 1 -> sustain_level
        decay_start = attack_samples
        decay_end = min(decay_start + decay_samples, n)
        if decay_end > decay_start:
            envelope[decay_start:decay_end] = np.linspace(
                1.0, sustain_level, decay_end - decay_start
            )

        # Sustain: constant
        sustain_start = decay_end
        release_start = max(n - release_samples, sustain_start)
        if release_start > sustain_start:
            envelope[sustain_start:release_start] = sustain_level

        # Release: sustain_level -> 0
        if release_samples > 0 and n - release_samples < n:
            rs = n - release_samples
            if rs < sustain_start:
                rs = sustain_start
            remaining = n - rs
            if remaining > 0:
                envelope[rs:] = np.linspace(sustain_level, 0.0, remaining)

        return audio * envelope

    def _apply_reverb(
        self,
        audio: NDArray[np.float64],
        wet: float = 0.25,
    ) -> NDArray[np.float64]:
        """Apply simple delay-based reverb (3 taps).

        Parameters
        ----------
        audio : ndarray
            Input audio.
        wet : float
            Wet/dry mix (0-1).

        Returns
        -------
        ndarray
            Audio with reverb.
        """
        n = len(audio)
        if n == 0:
            return audio

        # Three delay taps at ~30ms, ~60ms, ~90ms with decreasing gain
        delays = [
            (int(0.030 * self.sr), 0.5),
            (int(0.060 * self.sr), 0.3),
            (int(0.090 * self.sr), 0.15),
        ]

        output = audio.copy()
        for delay_samples, gain in delays:
            if delay_samples >= n:
                continue
            delayed = np.zeros(n, dtype=np.float64)
            delayed[delay_samples:] = audio[: n - delay_samples] * gain
            output += delayed

        # Mix wet/dry
        output = (1.0 - wet) * audio + wet * output

        return output

    def _apply_chorus(
        self,
        audio: NDArray[np.float64],
        depth: float = 0.5,
        rate: float = 1.5,
    ) -> NDArray[np.float64]:
        """Apply chorus effect using modulated delay.

        Parameters
        ----------
        audio : ndarray
            Input audio.
        depth : float
            Chorus depth (0-1).
        rate : float
            LFO rate in Hz.

        Returns
        -------
        ndarray
            Audio with chorus.
        """
        n = len(audio)
        if n == 0:
            return audio

        t = np.arange(n, dtype=np.float64) / self.sr
        # LFO: modulate delay between 5-15ms
        base_delay = int(0.010 * self.sr)
        mod_range = int(0.005 * self.sr * depth)

        # Generate modulated delay signal
        lfo = np.sin(2.0 * np.pi * rate * t)
        mod_delay = (base_delay + mod_range * lfo).astype(int)

        chorus = np.zeros(n, dtype=np.float64)
        for i in range(n):
            d = int(mod_delay[i])
            src = i - d
            if 0 <= src < n:
                chorus[i] = audio[src]

        # Mix: 70% dry + 30% chorus
        output = 0.7 * audio + 0.3 * chorus
        return output

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def synthesize_note(
        self,
        freq: float,
        duration: float,
        velocity: int = 80,
        spectral_density: float = 2.5,
        harmonic_tension: float = 2.5,
        rhythmic_complexity: float = 2.5,
    ) -> NDArray[np.float64]:
        """Synthesize a single note with harmonics controlled by dial parameters.

        Parameters
        ----------
        freq : float
            Frequency in Hz.
        duration : float
            Duration in seconds.
        velocity : int
            MIDI velocity 0-127.
        spectral_density : float
            Controls harmonic richness (0-5).
        harmonic_tension : float
            Controls harmonic content (0-5).
        rhythmic_complexity : float
            Controls ADSR envelope shape (0-5).

        Returns
        -------
        ndarray of float64
            Audio samples normalized to [-1, 1].
        """
        if freq <= 0 or duration <= 0:
            return np.zeros(int(duration * self.sr) if duration > 0 else 1, dtype=np.float64)

        # Generate harmonics
        tone = self._generate_harmonics(
            freq, duration, float(velocity), spectral_density, harmonic_tension
        )

        # Apply ADSR envelope
        tone = self._apply_adsr(tone, rhythmic_complexity, duration)

        # Normalize to [-1, 1]
        peak = np.max(np.abs(tone))
        if peak > 1e-10:
            tone = tone / peak * min(peak, 1.0)
            # Final safety clamp
            tone = np.clip(tone, -1.0, 1.0)

        return tone

    def render_midi(
        self,
        midi_data: MidiFile,
        dial_target: Optional[DialPosition] = None,
        bpm: int = 120,
    ) -> NDArray[np.float64]:
        """Render a full MIDI file to audio numpy array.

        Parameters
        ----------
        midi_data : MidiFile
            Input MIDI data.
        dial_target : DialPosition or None
            Target dial position for synthesis parameters.
            If None, uses defaults (2.5, 2.5, 2.5).
        bpm : int
            Tempo in BPM.

        Returns
        -------
        ndarray of float64
            Rendered audio normalized to [-1, 1].
        """
        if dial_target is None:
            dial_target = DialPosition(2.5, 2.5, 2.5)

        sd = dial_target.spectral_density
        ht = dial_target.harmonic_tension
        rc = dial_target.rhythmic_complexity

        # Extract all note events: (start_time, pitch, velocity, duration)
        ticks_per_second = midi_data.ticks_per_beat * bpm / 60.0
        note_events: list[tuple[float, int, int, float]] = []

        for track in midi_data.tracks:
            abs_tick = 0
            # Track active notes for duration computation
            active_notes: dict[int, tuple[int, int]] = {}  # note -> (start_tick, velocity)

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
                            dur_sec = 0.25  # minimum note duration
                        note_events.append((start_sec, msg.note, vel, dur_sec))

        # Handle any remaining active notes (no note_off)
        for track in midi_data.tracks:
            abs_tick = 0
            active_notes: dict[int, tuple[int, int]] = {}
            for msg in track:
                abs_tick += msg.time
                if msg.type == "note_on" and msg.velocity > 0:
                    active_notes[msg.note] = (abs_tick, msg.velocity)

        if not note_events:
            # No notes found, try extracting just onset-based
            onset_times = extract_onset_times(midi_data, bpm)
            pitch_classes = extract_pitch_classes_from_midi(midi_data)
            if len(onset_times) == 0:
                return np.zeros(1, dtype=np.float64)

            default_dur = 0.3
            for i, (ot, pc) in enumerate(zip(onset_times, pitch_classes)):
                midi_note = 60 + pc  # Default to octave 4
                note_events.append((ot, midi_note, 80, default_dur))

        if not note_events:
            return np.zeros(1, dtype=np.float64)

        # Find total duration
        max_time = max(ne[0] + ne[3] for ne in note_events)
        total_samples = int(np.ceil(max_time * self.sr)) + int(self.sr * 0.5)  # +0.5s tail

        # Mix all notes
        output = np.zeros(total_samples, dtype=np.float64)

        for start_sec, midi_note, velocity, dur_sec in note_events:
            freq = 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
            note_audio = self.synthesize_note(
                freq, dur_sec, velocity, sd, ht, rc
            )

            start_sample = int(start_sec * self.sr)
            end_sample = start_sample + len(note_audio)
            if end_sample > total_samples:
                end_sample = total_samples
                note_audio = note_audio[: end_sample - start_sample]

            if start_sample < total_samples and len(note_audio) > 0:
                output[start_sample:end_sample] += note_audio

        # Apply effects chain
        output = self._apply_reverb(output, wet=0.2)

        if sd > 3.0:
            output = self._apply_chorus(output, depth=0.3)

        # Final normalization
        peak = np.max(np.abs(output))
        if peak > 1e-10:
            output = output / peak * min(peak, 0.95)
        output = np.clip(output, -1.0, 1.0)

        return output

    def render_composition(
        self,
        dial_target: DialPosition,
        bars: int = 8,
        tempo: int = 120,
    ) -> NDArray[np.float64]:
        """Generate and render audio for a dial position.

        Creates a composition targeting the given dial position,
        then renders it to audio.

        Parameters
        ----------
        dial_target : DialPosition
            Target dial position.
        bars : int
            Number of bars.
        tempo : int
            Tempo in BPM.

        Returns
        -------
        ndarray of float64
            Rendered audio.
        """
        from .composer import ConstraintComposer

        composer = ConstraintComposer(seed=42)
        midi = composer.compose(dial_target, bars=bars, tempo=tempo)
        return self.render_midi(midi, dial_target=dial_target, bpm=tempo)

    def save_wav(
        self,
        audio: NDArray[np.float64],
        path: str | Path,
        sr: Optional[int] = None,
    ) -> None:
        """Save audio array as WAV file.

        Parameters
        ----------
        audio : ndarray of float64
            Audio samples in [-1, 1].
        path : str or Path
            Output file path.
        sr : int or None
            Sample rate. Defaults to self.sr.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if sr is None:
            sr = self.sr

        audio = np.clip(audio, -1.0, 1.0)
        # Convert to 16-bit PCM
        pcm = (audio * 32767.0).astype(np.int16)

        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(pcm.tobytes())

    def load_wav(self, path: str | Path, sr: Optional[int] = None) -> tuple[NDArray[np.float64], int]:
        """Load a WAV file.

        Parameters
        ----------
        path : str or Path
            Path to WAV file.
        sr : int or None
            Target sample rate. Defaults to self.sr.

        Returns
        -------
        audio : ndarray of float64
        sr : int
        """
        if sr is None:
            sr = self.sr
        from .audio_utils import load_wav as _load_wav
        return _load_wav(path, sr)
