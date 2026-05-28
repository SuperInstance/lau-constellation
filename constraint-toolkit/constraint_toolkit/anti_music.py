"""
Anti-music detector and generator.

Based on the finding that 99.93% of random music is still "beyond random"
(i.e., falls within the random distribution), true anti-music must be
deliberately crafted to break musical expectations.

Provides scoring, comparison against Monte Carlo random baselines,
and anti-music generation at varying intensities.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

try:
    from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
except ImportError:
    raise ImportError("mido is required: pip install mido")

from .analyzer import analyze_midi, analyze_wav
from .conservation import measure_tension
from .dials import DialPosition, compute_dial_signature


@dataclass
class AntiMusicScore:
    """Score measuring how anti-musical a piece is.

    Parameters
    ----------
    total_score : float
        Overall anti-music score [0, 1]. Higher = more anti-musical.
    negative_consonance : float
        How much the piece violates consonance expectations [0, 1].
    maximum_syncopation : float
        How much rhythm is maximally disrupted [0, 1].
    spectral_chaos : float
        How chaotic the spectral content is [0, 1].
    beyond_random : bool
        Whether the score exceeds 99.93% of random baselines.
    percentile : float
        What percentile this score falls in relative to random [0, 100].
    """

    total_score: float
    negative_consonance: float
    maximum_syncopation: float
    spectral_chaos: float
    beyond_random: bool
    percentile: float

    def summary(self) -> str:
        """Human-readable summary."""
        status = "🚫 BEYOND RANDOM" if self.beyond_random else "🎵 musical"
        lines = [
            f"Anti-Music Score: {self.total_score:.3f} ({status})",
            f"  Percentile vs random: {self.percentile:.1f}%",
            f"  Negative consonance:  {self.negative_consonance:.3f}",
            f"  Maximum syncopation:  {self.maximum_syncopation:.3f}",
            f"  Spectral chaos:       {self.spectral_chaos:.3f}",
        ]
        return "\n".join(lines)


def _compute_anti_metrics(
    onset_times: np.ndarray,
    pitch_classes: np.ndarray,
    spectrum: np.ndarray,
    sr: int = 44100,
    duration: float = 30.0,
) -> tuple[float, float, float]:
    """Compute anti-music metrics from raw features.

    Parameters
    ----------
    onset_times : ndarray
        Onset times in seconds.
    pitch_classes : ndarray
        Pitch class for each onset.
    spectrum : ndarray
        Magnitude spectrum.
    sr : int
        Sample rate.
    duration : float
        Duration in seconds.

    Returns
    -------
    tuple of (negative_consonance, maximum_syncopation, spectral_chaos)
    """
    # Negative consonance: how much the piece avoids conventional intervals
    if len(pitch_classes) >= 2:
        # Measure intervals between consecutive pitch classes
        intervals = np.abs(np.diff(pitch_classes.astype(int)))
        # Tritone (6), minor second (1), major seventh (11) are "anti-consonant"
        anti_intervals = [1, 6, 11]
        anti_weight = sum(
            1 for iv in intervals if int(iv) % 12 in anti_intervals
        )
        # Also penalize tritone-heavy distributions
        pc_hist = np.bincount(pitch_classes.astype(int), minlength=12)
        pc_probs = pc_hist / max(pc_hist.sum(), 1)
        # High entropy = avoiding tonal center
        entropy = -np.sum(
            pc_probs[pc_probs > 0] * np.log2(pc_probs[pc_probs > 0])
        )
        max_entropy = np.log2(12)
        negative_consonance = (
            0.5 * anti_weight / max(len(intervals), 1)
            + 0.5 * entropy / max_entropy
        )
    else:
        negative_consonance = 0.0

    # Maximum syncopation: how much rhythm avoids regular patterns
    if len(onset_times) > 2:
        iois = np.diff(onset_times)
        cv = np.std(iois) / max(np.mean(iois), 1e-6)
        # Check for maximally irregular timing
        # Perfect regularity = cv ≈ 0, maximum irregularity = cv > 1
        maximum_syncopation = np.clip(cv / 1.5, 0, 1)

        # Also check for absence of pulse (no periodicity)
        if len(iois) > 4:
            # Autocorrelation of IOIs
            iois_centered = iois - np.mean(iois)
            if np.std(iois_centered) > 0:
                autocorr = np.correlate(iois_centered, iois_centered, mode="full")
                autocorr = autocorr[len(autocorr) // 2 :]
                autocorr_norm = autocorr / max(autocorr[0], 1e-10)
                # Low autocorrelation = no pulse = anti-musical
                if len(autocorr_norm) > 1:
                    pulse_strength = float(np.max(autocorr_norm[1:]))
                    maximum_syncopation = 0.5 * maximum_syncopation + 0.5 * (
                        1.0 - pulse_strength
                    )
    else:
        maximum_syncopation = 0.0

    # Spectral chaos: how noisy/unstructured the spectrum is
    if len(spectrum) > 1:
        spec_safe = spectrum + 1e-10
        log_geo = np.mean(np.log(spec_safe))
        log_ari = np.log(np.mean(spec_safe))
        flatness = np.exp(log_geo - log_ari)  # 0-1, high = noise-like

        # Spectral entropy
        spec_probs = spec_safe / spec_safe.sum()
        spec_entropy = -np.sum(spec_probs[spec_probs > 0] * np.log2(spec_probs[spec_probs > 0]))
        max_spec_entropy = np.log2(len(spectrum))
        entropy_ratio = spec_entropy / max_spec_entropy

        spectral_chaos = 0.5 * flatness + 0.5 * entropy_ratio
    else:
        spectral_chaos = 0.0

    return (
        float(np.clip(negative_consonance, 0, 1)),
        float(np.clip(maximum_syncopation, 0, 1)),
        float(np.clip(spectral_chaos, 0, 1)),
    )


class AntiMusicDetector:
    """Detect whether music is intentionally anti-musical.

    Uses a Monte Carlo random baseline (10K samples) to determine
    whether a piece falls in the "beyond random" category. Known result:
    99.93% of random music is still within the random distribution.

    Parameters
    ----------
    n_baseline : int
        Number of random baseline samples.
    seed : int
        Random seed.
    """

    BEYOND_RANDOM_THRESHOLD = 99.93  # percentile threshold

    def __init__(self, n_baseline: int = 10000, seed: int = 42) -> None:
        self.n_baseline = n_baseline
        self.seed = seed
        self._baseline_scores: Optional[np.ndarray] = None

    def _generate_baseline(self) -> np.ndarray:
        """Generate Monte Carlo random baseline scores.

        Uses vectorized numpy for speed.

        Returns
        -------
        ndarray
            Anti-music scores for random samples.
        """
        rng = np.random.RandomState(self.seed)
        n = self.n_baseline

        # Vectorized generation of random musical features
        # Random pitch classes (0-11)
        random_pcs = rng.randint(0, 12, size=(n, 50))
        # Random onset times (exponential distribution)
        random_iois = rng.exponential(0.3, size=(n, 50))
        random_onsets = np.cumsum(random_iois, axis=1)
        # Random spectra (exponential noise)
        random_spectra = np.abs(rng.exponential(1.0, size=(n, 2048)))

        scores = np.zeros(n, dtype=np.float64)

        for i in range(n):
            nc, ms, sc = _compute_anti_metrics(
                random_onsets[i],
                random_pcs[i],
                random_spectra[i],
                sr=44100,
                duration=30.0,
            )
            scores[i] = 0.35 * nc + 0.30 * ms + 0.35 * sc

        return scores

    def _ensure_baseline(self) -> np.ndarray:
        """Lazily compute and cache baseline scores."""
        if self._baseline_scores is None:
            self._baseline_scores = self._generate_baseline()
        return self._baseline_scores

    def score(self, audio_or_midi: str | Path) -> AntiMusicScore:
        """Score how anti-musical a piece is.

        Parameters
        ----------
        audio_or_midi : str or Path
            Path to WAV or MIDI file.

        Returns
        -------
        AntiMusicScore
        """
        path = Path(audio_or_midi)
        suffix = path.suffix.lower()

        if suffix in (".mid", ".midi"):
            result = analyze_midi(path)
        else:
            result = analyze_wav(path)

        dp = result.dial_position

        # Reconstruct approximate features from the analysis result
        # We need raw metrics, so we compute from the dial position
        # and available features

        # Build approximate onset/pitch/spectrum from the stored metadata
        n_onsets = result.onset_count
        duration = max(result.duration, 0.1)

        # Use spectral features to reconstruct approximate spectrum
        centroid = result.spectral_features.get("centroid", 1000)
        bandwidth = result.spectral_features.get("bandwidth", 500)

        # Synthetic spectrum matching features
        sr = 44100
        freqs = np.linspace(0, sr / 2, 2048)
        spectrum = np.exp(-0.5 * ((freqs - centroid) / max(bandwidth, 1)) ** 2)
        spectrum = np.abs(spectrum) + 0.01

        # Synthetic onsets from dial position
        rng = np.random.RandomState(self.seed)
        rc = dp.rhythmic_complexity
        n_approx = max(10, int(rc * 10))
        iois = rng.exponential(duration / n_approx, size=n_approx)
        onset_times = np.cumsum(iois)
        onset_times = onset_times[onset_times < duration]

        # Pitch classes from distribution
        pc_dist = result.pitch_class_distribution
        pc_values = np.array([pc_dist.get(i, 0) for i in range(12)])
        pc_values = pc_values / max(pc_values.sum(), 1e-10)
        pitch_classes = rng.choice(12, size=len(onset_times), p=pc_values)

        nc, ms, sc = _compute_anti_metrics(
            onset_times, pitch_classes, spectrum, sr, duration
        )

        total = 0.35 * nc + 0.30 * ms + 0.35 * sc

        # Compare against baseline
        baseline = self._ensure_baseline()
        percentile = float(np.mean(baseline <= total) * 100)
        beyond_random = percentile >= self.BEYOND_RANDOM_THRESHOLD

        return AntiMusicScore(
            total_score=float(np.clip(total, 0, 1)),
            negative_consonance=nc,
            maximum_syncopation=ms,
            spectral_chaos=sc,
            beyond_random=beyond_random,
            percentile=percentile,
        )

    def score_raw(
        self,
        onset_times: np.ndarray,
        pitch_classes: np.ndarray,
        spectrum: np.ndarray,
        sr: int = 44100,
        duration: float = 30.0,
    ) -> AntiMusicScore:
        """Score from raw musical features.

        Parameters
        ----------
        onset_times : ndarray
            Onset times in seconds.
        pitch_classes : ndarray
            Pitch class for each onset.
        spectrum : ndarray
            Magnitude spectrum.
        sr : int
            Sample rate.
        duration : float
            Duration in seconds.

        Returns
        -------
        AntiMusicScore
        """
        nc, ms, sc = _compute_anti_metrics(
            onset_times, pitch_classes, spectrum, sr, duration
        )
        total = 0.35 * nc + 0.30 * ms + 0.35 * sc

        baseline = self._ensure_baseline()
        percentile = float(np.mean(baseline <= total) * 100)
        beyond_random = percentile >= self.BEYOND_RANDOM_THRESHOLD

        return AntiMusicScore(
            total_score=float(np.clip(total, 0, 1)),
            negative_consonance=nc,
            maximum_syncopation=ms,
            spectral_chaos=sc,
            beyond_random=beyond_random,
            percentile=percentile,
        )

    def generate_anti_music(
        self, intensity: float = 1.0, duration: float = 30.0, bpm: int = 120
    ) -> MidiFile:
        """Generate deliberately anti-musical content.

        Parameters
        ----------
        intensity : float
            Anti-music intensity [0, 1]. 0 = barely anti-musical,
            1 = maximally anti-musical.
        duration : float
            Duration in seconds.
        bpm : int
            Base tempo (will be subverted).

        Returns
        -------
        MidiFile
            Generated anti-music.
        """
        rng = np.random.RandomState(self.seed)
        intensity = float(np.clip(intensity, 0, 1))

        mid = MidiFile(ticks_per_beat=480)
        track = MidiTrack()
        mid.tracks.append(track)

        tempo = bpm2tempo(bpm)
        track.append(MetaMessage("set_tempo", tempo=tempo, time=0))

        ticks_per_second = mid.ticks_per_beat * bpm / 60.0
        total_ticks = int(duration * ticks_per_second)

        # Generate notes with anti-musical properties
        n_notes = int(10 + intensity * 40)  # 10-50 notes
        base_interval = total_ticks / max(n_notes, 1)

        events = []

        for i in range(n_notes):
            # Anti-musical timing: increasingly irregular with intensity
            regularity = 1.0 - intensity * 0.9
            tick = int(i * base_interval + rng.randn() * base_interval * (1 - regularity))
            tick = max(0, min(tick, total_ticks))

            # Anti-musical pitch: avoid tonal center, prefer dissonant intervals
            if intensity > 0.5:
                # Strong anti-music: prefer tritones, minor seconds
                anti_pitches = [0, 1, 6, 11]  # C, C#, F#, B
                pitch = rng.choice(anti_pitches) + rng.choice([36, 48, 60, 72, 84])
            else:
                # Milder: random chromatic
                pitch = rng.randint(36, 96)

            # Add pitch randomness proportional to intensity
            pitch += int(rng.randn() * intensity * 6)
            pitch = max(0, min(127, pitch))

            velocity = int(40 + rng.randint(0, 80) * intensity + (1 - intensity) * 40)
            velocity = max(20, min(127, velocity))

            # Short, abrasive notes at high intensity
            note_ticks = int(
                ticks_per_second * 0.3 * (1 - intensity * 0.7)
            )

            events.append((tick, "note_on", pitch, velocity))
            events.append((tick + max(1, note_ticks), "note_off", pitch, 0))

        # Sort by time, with note_off before note_on at same tick
        events.sort(key=lambda x: (x[0], 0 if x[1] == "note_off" else 1))

        prev_tick = 0
        for tick, msg_type, note, vel in events:
            delta = max(0, tick - prev_tick)
            track.append(Message(msg_type, note=note, velocity=vel, time=delta))
            prev_tick = tick

        return mid

    def compare_to_random(self, audio_or_midi: str | Path) -> dict:
        """Compare a piece's metrics to random baselines.

        Parameters
        ----------
        audio_or_midi : str or Path
            Path to the file.

        Returns
        -------
        dict with comparison statistics.
        """
        score = self.score(audio_or_midi)
        baseline = self._ensure_baseline()

        return {
            "piece_score": score.total_score,
            "piece_negative_consonance": score.negative_consonance,
            "piece_maximum_syncopation": score.maximum_syncopation,
            "piece_spectral_chaos": score.spectral_chaos,
            "piece_percentile": score.percentile,
            "piece_beyond_random": score.beyond_random,
            "baseline_mean": float(np.mean(baseline)),
            "baseline_std": float(np.std(baseline)),
            "baseline_median": float(np.median(baseline)),
            "baseline_p95": float(np.percentile(baseline, 95)),
            "baseline_p99": float(np.percentile(baseline, 99)),
            "baseline_p99_93": float(np.percentile(baseline, 99.93)),
            "n_baseline": len(baseline),
        }

    def calibrate(self) -> dict:
        """Test calibration: verify known anti-music scores as anti-music.

        Generates test pieces at known intensities and verifies the
        detector correctly identifies them.

        Returns
        -------
        dict with calibration results.
        """
        results = {}

        # Test at multiple intensities
        for intensity in [0.0, 0.25, 0.5, 0.75, 1.0]:
            midi = self.generate_anti_music(intensity=intensity, duration=10.0)

            # Extract features from generated MIDI
            onsets = []
            pitches = []
            for track in midi.tracks:
                abs_time = 0.0
                for msg in track:
                    abs_time += msg.time
                    if msg.type == "note_on" and msg.velocity > 0:
                        time_sec = abs_time / (midi.ticks_per_beat * 120 / 60.0)
                        onsets.append(time_sec)
                        pitches.append(msg.note % 12)

            onset_arr = np.array(sorted(onsets), dtype=np.float64)
            pitch_arr = np.array(pitches, dtype=np.intp)

            # Build pseudo-spectrum
            pseudo_spectrum = np.abs(np.random.RandomState(42).exponential(1.0, 2048))

            score = self.score_raw(
                onset_arr, pitch_arr, pseudo_spectrum, duration=10.0
            )

            results[f"intensity_{intensity:.2f}"] = {
                "intensity": intensity,
                "total_score": score.total_score,
                "percentile": score.percentile,
                "beyond_random": score.beyond_random,
                "negative_consonance": score.negative_consonance,
                "maximum_syncopation": score.maximum_syncopation,
                "spectral_chaos": score.spectral_chaos,
            }

        # Check monotonicity: higher intensity should score higher
        scores_list = [
            results[f"intensity_{i:.2f}"]["total_score"]
            for i in [0.0, 0.25, 0.5, 0.75, 1.0]
        ]
        is_monotonic = all(scores_list[i] <= scores_list[i + 1] for i in range(len(scores_list) - 1))

        results["calibration_monotonic"] = is_monotonic

        return results
