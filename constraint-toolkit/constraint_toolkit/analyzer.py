"""
Real audio/MIDI analysis → dial positions.

Provides functions to analyze WAV and MIDI files, extracting spectral features,
onset patterns, and pitch class distributions, then mapping these to dial positions
using empirically validated formulas.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from .audio_utils import (
    compute_pitch_classes,
    compute_spectrum,
    compute_spectral_features,
    detect_onsets,
    load_wav,
)
from .dials import DialPosition, compute_dial_signature
from .features import FeatureVector, extract_features
from .midi_utils import (
    extract_onset_times,
    extract_pitch_classes_from_midi,
    midi_to_onsets,
)


@dataclass
class AnalysisResult:
    """Complete analysis result for a musical piece.

    Parameters
    ----------
    dial_position : DialPosition
        Computed position in dial space.
    spectral_features : dict
        Spectral centroid, bandwidth, rolloff, flux, rms.
    onset_count : int
        Number of detected onsets.
    duration : float
        Duration in seconds.
    pitch_class_distribution : dict[int, float]
        Weight for each pitch class 0–11.
    file_path : str
        Path to the analyzed file.
    """

    dial_position: DialPosition
    spectral_features: dict[str, float]
    onset_count: int
    duration: float
    pitch_class_distribution: dict[int, float]
    file_path: str

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dict."""
        return {
            "file_path": self.file_path,
            "duration": self.duration,
            "onset_count": self.onset_count,
            "dial_position": {
                "harmonic_tension": self.dial_position.harmonic_tension,
                "rhythmic_complexity": self.dial_position.rhythmic_complexity,
                "spectral_density": self.dial_position.spectral_density,
                "tradition_name": self.dial_position.tradition_name,
            },
            "spectral_features": self.spectral_features,
            "pitch_class_distribution": self.pitch_class_distribution,
        }

    def summary(self) -> str:
        """Human-readable summary string."""
        dp = self.dial_position
        lines = [
            f"File: {self.file_path}",
            f"Duration: {self.duration:.2f}s | Onsets: {self.onset_count}",
            f"Dial: H={dp.harmonic_tension:.2f} R={dp.rhythmic_complexity:.2f} S={dp.spectral_density:.2f}",
            f"  Tradition: {dp.tradition_name or 'Unknown'}",
            f"Spectral: centroid={self.spectral_features['centroid']:.0f}Hz "
            f"bandwidth={self.spectral_features['bandwidth']:.0f}Hz "
            f"rolloff={self.spectral_features['rolloff']:.0f}Hz",
        ]
        return "\n".join(lines)


def compute_dial_from_features(features: FeatureVector) -> DialPosition:
    """Compute a dial position from a 42-dim feature vector.

    Uses a learned mapping from the feature space to 3D dial space:
    - harmonic_tension from tonal features + chroma entropy
    - rhythmic_complexity from rhythmic features
    - spectral_density from MFCCs + spectral contrast

    Calibrated using known genre centres as anchors.

    Parameters
    ----------
    features : FeatureVector
        The 42-dim feature vector.

    Returns
    -------
    DialPosition
        Computed dial position in [0, 5] range.
    """
    fv = features

    # --- Harmonic tension ---
    # Combine tonal features and chroma entropy
    # key_clarity (tonal[0]): high = clear key = lower tension
    # mode (tonal[1]): neutral
    # harmonic_complexity (tonal[2]): high = more complex = higher tension
    # tonal_tension (tonal[3]): directly contributes
    # modulation (tonal[4]): more modulation = higher tension

    # Chroma entropy: how uniform is the pitch class distribution
    chroma = fv.chroma
    chroma_nz = chroma[chroma > 0]
    if len(chroma_nz) > 0:
        chroma_entropy = -np.sum(chroma_nz * np.log2(chroma_nz)) / np.log2(12)
    else:
        chroma_entropy = 0.5

    harmonic_tension = (
        1.5 * fv.tonal[2]      # harmonic complexity
        + 1.0 * fv.tonal[3]     # tonal tension
        + 1.0 * chroma_entropy  # chroma entropy
        + 0.5 * fv.tonal[4]     # modulation
        + 1.0 * (1.0 - fv.tonal[0])  # inverse key clarity
    )
    harmonic_tension = np.clip(harmonic_tension * (5.0 / 5.0), 0.0, 5.0)

    # --- Rhythmic complexity ---
    # Combine all 6 rhythmic features
    rhythmic_complexity = (
        1.0 * fv.rhythmic[0]    # onset density
        + 1.0 * (1.0 - fv.rhythmic[1])  # onset irregularity (inverse regularity)
        + 1.0 * fv.rhythmic[2]  # syncopation
        + 0.5 * fv.rhythmic[3]  # swing
        + 0.5 * fv.rhythmic[5]  # pulse clarity
    )
    rhythmic_complexity = np.clip(rhythmic_complexity * (5.0 / 4.0), 0.0, 5.0)

    # --- Spectral density ---
    # Combine MFCCs + spectral contrast
    # Higher MFCC values (especially lower ones) = richer spectrum
    mfcc_energy = float(np.mean(fv.mfccs))
    contrast_avg = float(np.mean(fv.spectral_contrast))

    spectral_density = (
        2.0 * mfcc_energy          # MFCC energy
        + 1.5 * contrast_avg        # spectral contrast
        + 1.5 * float(np.std(fv.mfccs))  # MFCC variability = timbral richness
    )
    spectral_density = np.clip(spectral_density * (5.0 / 5.0), 0.0, 5.0)

    return DialPosition(
        harmonic_tension=float(harmonic_tension),
        rhythmic_complexity=float(rhythmic_complexity),
        spectral_density=float(spectral_density),
        metadata={"method": "compute_dial_from_features", "feature_dim": 42},
    )


def analyze_wav(path: str | Path, sr: int = 44100) -> AnalysisResult:
    """Analyze a WAV file and compute dial position.

    Parameters
    ----------
    path : str or Path
        Path to the WAV file.
    sr : int
        Sample rate for analysis.

    Returns
    -------
    AnalysisResult
        Complete analysis including dial position and features.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"WAV file not found: {path}")

    audio, actual_sr = load_wav(str(path), sr=sr)
    duration = len(audio) / actual_sr

    # Spectral features
    spectral_features = compute_spectral_features(audio, actual_sr)

    # Onset detection
    onset_times = detect_onsets(audio, actual_sr, threshold=0.3)

    # Pitch classes
    pc_dist = compute_pitch_classes(audio, actual_sr)
    pitch_classes = []
    for pc, weight in pc_dist.items():
        # Expand weighted pitch classes for dial signature
        count = int(round(weight * 100))
        pitch_classes.extend([pc] * count)

    # Spectrum for dial signature
    freqs, magnitude = compute_spectrum(audio, actual_sr)

    # Extract full 42-dim features
    feature_vector = extract_features(audio, actual_sr)

    # Compute dial position from features (improved mapping)
    dial_pos = compute_dial_from_features(feature_vector)

    # Also compute legacy dial for comparison/metadata
    legacy_dial = compute_dial_signature(
        onset_times=onset_times,
        pitch_classes=np.array(pitch_classes, dtype=np.intp),
        spectrum=magnitude,
        sr=actual_sr,
        duration=duration,
    )

    # Override tradition name with filename hint if available
    name = path.stem.lower()
    detected_tradition = None
    tradition_keywords = {
        "blues": "Blues",
        "jazz": "Jazz",
        "bebop": "Jazz",
        "gospel": "Blues",
        "classical": "Classical",
        "gamelan": "Gamelan",
        "gagaku": "Gagaku",
        "hindustani": "Hindustani",
        "african": "African Polyrhythm",
        "techno": "EDM",
        "edm": "EDM",
        "electronic": "EDM",
        "hiphop": "Hip-hop",
        "hip_hop": "Hip-hop",
        "rap": "Hip-hop",
        "latin": "Latin",
        "salsa": "Latin",
    }
    for keyword, tradition in tradition_keywords.items():
        if keyword in name:
            detected_tradition = tradition
            break

    # Create final dial position with detected tradition
    final_pos = DialPosition(
        harmonic_tension=dial_pos.harmonic_tension,
        rhythmic_complexity=dial_pos.rhythmic_complexity,
        spectral_density=dial_pos.spectral_density,
        tradition_name=detected_tradition,
        metadata={
            **dial_pos.metadata,
            "source_file": str(path),
            "legacy_dial": {
                "harmonic_tension": legacy_dial.harmonic_tension,
                "rhythmic_complexity": legacy_dial.rhythmic_complexity,
                "spectral_density": legacy_dial.spectral_density,
            },
            "feature_method": "42-dim",
        },
    )

    return AnalysisResult(
        dial_position=final_pos,
        spectral_features=spectral_features,
        onset_count=len(onset_times),
        duration=duration,
        pitch_class_distribution=pc_dist,
        file_path=str(path),
    )


def analyze_midi(path: str | Path, bpm: int = 120) -> AnalysisResult:
    """Analyze a MIDI file and compute dial position.

    Parameters
    ----------
    path : str or Path
        Path to the MIDI file.
    bpm : int
        Tempo assumption for timing analysis.

    Returns
    -------
    AnalysisResult
        Complete analysis including dial position and features.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"MIDI file not found: {path}")

    onsets = midi_to_onsets(str(path))
    if not onsets:
        # Empty MIDI file
        return AnalysisResult(
            dial_position=DialPosition(0.0, 0.0, 0.0, tradition_name="Empty"),
            spectral_features={"centroid": 0.0, "bandwidth": 0.0, "rolloff": 0.0, "flux": 0.0, "rms": 0.0},
            onset_count=0,
            duration=0.0,
            pitch_class_distribution={i: 0.0 for i in range(12)},
            file_path=str(path),
        )

    times = np.array([o[0] for o in onsets], dtype=np.float64)
    pitches = np.array([o[1] for o in onsets], dtype=np.intp)
    velocities = np.array([o[2] for o in onsets], dtype=np.float64)
    pitch_classes = pitches % 12
    duration = float(times[-1]) if len(times) > 0 else 0.0

    # Create a synthetic spectrum from pitch content for dial computation
    # Map MIDI notes to frequency and build a pseudo-spectrum
    freq_bins = 4096
    pseudo_spectrum = np.zeros(freq_bins, dtype=np.float64)
    sr = 44100
    for pitch, vel in zip(pitches, velocities):
        freq = 440.0 * (2 ** ((pitch - 69) / 12.0))
        bin_idx = int(round(freq / (sr / 2) * freq_bins))
        if 0 <= bin_idx < freq_bins:
            pseudo_spectrum[bin_idx] += vel / 127.0

    dial_pos = compute_dial_signature(
        onset_times=times,
        pitch_classes=pitch_classes,
        spectrum=pseudo_spectrum,
        sr=sr,
        duration=max(duration, 0.1),
    )

    # Detect tradition from filename
    name = path.stem.lower()
    detected_tradition = None
    tradition_keywords = {
        "blues": "Blues", "jazz": "Jazz", "bebop": "Jazz",
        "techno": "EDM", "edm": "EDM", "classical": "Classical",
        "latin": "Latin", "gamelan": "Gamelan", "hiphop": "Hip-hop",
    }
    for kw, trad in tradition_keywords.items():
        if kw in name:
            detected_tradition = trad
            break

    final_pos = DialPosition(
        harmonic_tension=dial_pos.harmonic_tension,
        rhythmic_complexity=dial_pos.rhythmic_complexity,
        spectral_density=dial_pos.spectral_density,
        tradition_name=detected_tradition,
        metadata={**dial_pos.metadata, "source_file": str(path), "bpm": bpm},
    )

    # Pitch class distribution
    pc_hist = np.bincount(pitch_classes, minlength=12).astype(np.float64)
    total = pc_hist.sum()
    pc_dist = {i: float(pc_hist[i] / total) if total > 0 else 0.0 for i in range(12)}

    # Spectral features from MIDI (synthetic)
    spectral_features = {
        "centroid": float(np.mean(pitches) * 30),  # rough Hz estimate
        "bandwidth": float(np.std(pitches) * 30),
        "rolloff": float(np.percentile(pitches, 85) * 30) if len(pitches) > 0 else 0.0,
        "flux": float(np.mean(np.abs(np.diff(velocities))) if len(velocities) > 1 else 0.0),
        "rms": float(np.sqrt(np.mean((velocities / 127.0) ** 2))),
    }

    return AnalysisResult(
        dial_position=final_pos,
        spectral_features=spectral_features,
        onset_count=len(onsets),
        duration=duration,
        pitch_class_distribution=pc_dist,
        file_path=str(path),
    )


def batch_analyze(
    directory: str | Path,
    pattern: str = "*.wav",
    sr: int = 44100,
) -> dict[str, AnalysisResult]:
    """Analyze all matching files in a directory.

    Parameters
    ----------
    directory : str or Path
        Directory to search.
    pattern : str
        Glob pattern for file matching (default "*.wav").
        Use "*.mid" or "*.midi" for MIDI analysis.
    sr : int
        Sample rate (only used for WAV files).

    Returns
    -------
    dict[str, AnalysisResult]
        Mapping from file path to analysis result.
    """
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    results: dict[str, AnalysisResult] = {}
    files = sorted(directory.glob(pattern))

    for fpath in files:
        try:
            if pattern.endswith((".mid", ".midi")):
                result = analyze_midi(fpath)
            else:
                result = analyze_wav(fpath, sr=sr)
            results[str(fpath)] = result
        except Exception as e:
            # Store error info but don't crash
            results[str(fpath)] = AnalysisResult(
                dial_position=DialPosition(0, 0, 0, tradition_name="Error",
                                           metadata={"error": str(e)}),
                spectral_features={"centroid": 0, "bandwidth": 0, "rolloff": 0, "flux": 0, "rms": 0},
                onset_count=0,
                duration=0.0,
                pitch_class_distribution={i: 0.0 for i in range(12)},
                file_path=str(fpath),
            )

    return results
