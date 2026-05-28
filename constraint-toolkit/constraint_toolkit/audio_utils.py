"""
Audio utilities for WAV processing.

Provides loading, spectral analysis, onset detection, pitch-class extraction,
and spectral feature computation using numpy/scipy.
"""

from __future__ import annotations

import struct
import wave
from pathlib import Path
from typing import Optional

import numpy as np
from numpy.typing import NDArray
from scipy import signal as sp_signal


def load_wav(path: str | Path, sr: int = 44100) -> tuple[NDArray[np.float64], int]:
    """Load a WAV file and return mono float audio resampled to target sr.

    Parameters
    ----------
    path : str or Path
        Path to the WAV file.
    sr : int
        Target sample rate.

    Returns
    -------
    audio : ndarray of float64, shape (n_samples,)
        Mono audio data normalized to [-1, 1].
    sample_rate : int
        Actual sample rate used.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file is not a valid WAV.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"WAV file not found: {path}")

    with wave.open(str(path), "rb") as wf:
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        orig_sr = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    # Decode
    if sample_width == 1:
        dtype = np.uint8
        max_val = 128.0
    elif sample_width == 2:
        dtype = np.int16
        max_val = 32768.0
    elif sample_width == 4:
        dtype = np.int32
        max_val = 2147483648.0
    else:
        raise ValueError(f"Unsupported sample width: {sample_width} bytes")

    data = np.frombuffer(raw, dtype=dtype).astype(np.float64)

    # Mix to mono
    if n_channels > 1:
        data = data.reshape(-1, n_channels).mean(axis=1)

    # Normalize
    data = data / max_val

    # Resample if needed
    if orig_sr != sr:
        duration = len(data) / orig_sr
        n_out = int(duration * sr)
        data = sp_signal.resample(data, n_out)

    return data, sr


def compute_spectrum(
    audio: NDArray[np.float64],
    sr: int = 44100,
    n_fft: Optional[int] = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Compute the magnitude spectrum of audio.

    Parameters
    ----------
    audio : ndarray of float64
        Audio samples.
    sr : int
        Sample rate.
    n_fft : int or None
        FFT size. Defaults to next power of 2 above len(audio).

    Returns
    -------
    freqs : ndarray of float64
        Frequency values in Hz.
    magnitude : ndarray of float64
        Magnitude spectrum (positive frequencies only).
    """
    audio = np.asarray(audio, dtype=np.float64)
    if n_fft is None:
        n_fft = 1
        while n_fft < len(audio):
            n_fft *= 2

    # Apply Hann window
    window = np.hanning(len(audio))
    windowed = audio * window

    # Zero-pad
    padded = np.zeros(n_fft, dtype=np.float64)
    padded[: len(windowed)] = windowed

    # FFT
    spectrum = np.fft.rfft(padded)
    magnitude = np.abs(spectrum)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)

    return freqs, magnitude


def detect_onsets(
    audio: NDArray[np.float64],
    sr: int = 44100,
    threshold: float = 0.3,
    frame_size: int = 1024,
    hop_size: int = 512,
) -> NDArray[np.float64]:
    """Detect onsets using spectral flux.

    Parameters
    ----------
    audio : ndarray of float64
        Audio samples.
    sr : int
        Sample rate.
    threshold : float
        Detection threshold (0–1, relative to max flux).
    frame_size : int
        FFT frame size.
    hop_size : int
        Hop size between frames.

    Returns
    -------
    onset_times : ndarray of float64
        Onset times in seconds.
    """
    audio = np.asarray(audio, dtype=np.float64)
    n_frames = max(1, (len(audio) - frame_size) // hop_size + 1)

    # Compute spectral flux
    prev_mag = np.zeros(frame_size // 2 + 1, dtype=np.float64)
    flux = np.zeros(n_frames, dtype=np.float64)

    for i in range(n_frames):
        start = i * hop_size
        end = min(start + frame_size, len(audio))
        frame = np.zeros(frame_size, dtype=np.float64)
        frame[: end - start] = audio[start:end]
        windowed = frame * np.hanning(frame_size)
        spectrum = np.abs(np.fft.rfft(windowed))
        # Half-wave rectified spectral flux
        diff = spectrum - prev_mag
        flux[i] = np.sum(np.maximum(diff, 0))
        prev_mag = spectrum

    # Adaptive threshold
    if flux.max() > 0:
        flux_norm = flux / flux.max()
    else:
        return np.array([], dtype=np.float64)

    # Peak picking
    threshold_val = threshold
    peaks: list[int] = []
    for i in range(1, len(flux_norm) - 1):
        if (
            flux_norm[i] > threshold_val
            and flux_norm[i] > flux_norm[i - 1]
            and flux_norm[i] >= flux_norm[i + 1]
        ):
            # Minimum distance between onsets: 50ms
            min_frame_gap = int(0.05 * sr / hop_size)
            if not peaks or (i - peaks[-1]) >= min_frame_gap:
                peaks.append(i)

    onset_times = np.array([p * hop_size / sr for p in peaks], dtype=np.float64)
    return onset_times


def compute_pitch_classes(
    audio: NDArray[np.float64],
    sr: int = 44100,
    n_fft: int = 4096,
) -> dict[int, float]:
    """Compute pitch class weights from audio using chroma analysis.

    Parameters
    ----------
    audio : ndarray of float64
        Audio samples.
    sr : int
        Sample rate.
    n_fft : int
        FFT size for spectral analysis.

    Returns
    -------
    dict[int, float]
        Mapping from pitch class (0=C, 1=C#, ..., 11=B) to weight.
    """
    audio = np.asarray(audio, dtype=np.float64)

    # Frame-based analysis for long audio
    hop = n_fft // 2
    n_frames = max(1, (len(audio) - n_fft) // hop + 1)

    pitch_classes = np.zeros(12, dtype=np.float64)

    for frame_idx in range(n_frames):
        start = frame_idx * hop
        end = min(start + n_fft, len(audio))
        frame = np.zeros(n_fft, dtype=np.float64)
        frame[:end - start] = audio[start:end]

        windowed = frame * np.hanning(n_fft)
        spectrum = np.abs(np.fft.rfft(windowed))
        freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)

        for freq, mag in zip(freqs, spectrum):
            if freq < 20 or freq > 8000:  # focus on musical range
                continue
            midi = 12 * np.log2(freq / 440.0) + 69
            pc = int(round(midi)) % 12
            pitch_classes[pc] += mag

    # Normalize
    total = pitch_classes.sum()
    if total > 0:
        pitch_classes /= total

    return {i: float(pitch_classes[i]) for i in range(12)}


def compute_spectral_features(
    audio: NDArray[np.float64],
    sr: int = 44100,
) -> dict[str, float]:
    """Compute standard spectral features.

    Parameters
    ----------
    audio : ndarray of float64
        Audio samples.
    sr : int
        Sample rate.

    Returns
    -------
    dict with keys:
        - centroid: Spectral centroid (Hz)
        - bandwidth: Spectral bandwidth (Hz)
        - rolloff: Spectral rolloff frequency (85th percentile, Hz)
        - flux: Mean spectral flux
        - rms: Root mean square energy
    """
    audio = np.asarray(audio, dtype=np.float64)
    freqs, magnitude = compute_spectrum(audio, sr)

    total_mag = magnitude.sum()
    if total_mag < 1e-10:
        return {
            "centroid": 0.0,
            "bandwidth": 0.0,
            "rolloff": 0.0,
            "flux": 0.0,
            "rms": float(np.sqrt(np.mean(audio**2))),
        }

    # Centroid
    centroid = float(np.sum(freqs * magnitude) / total_mag)

    # Bandwidth
    bandwidth = float(
        np.sqrt(np.sum(((freqs - centroid) ** 2) * magnitude) / total_mag)
    )

    # Rolloff (85th percentile of spectral energy)
    cumsum = np.cumsum(magnitude)
    rolloff_idx = np.searchsorted(cumsum, 0.85 * cumsum[-1])
    rolloff_idx = min(rolloff_idx, len(freqs) - 1)
    rolloff = float(freqs[rolloff_idx])

    # Spectral flux
    diff = np.diff(magnitude)
    flux = float(np.mean(np.abs(diff)))

    # RMS
    rms = float(np.sqrt(np.mean(audio**2)))

    return {
        "centroid": centroid,
        "bandwidth": bandwidth,
        "rolloff": rolloff,
        "flux": flux,
        "rms": rms,
    }
