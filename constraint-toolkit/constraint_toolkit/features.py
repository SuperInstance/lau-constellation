"""
Advanced feature extraction for audio analysis.

Extracts a 42-dimensional feature vector from audio signals using only
numpy and scipy. Features include MFCCs, chroma, spectral contrast,
rhythmic features, and tonal features.

All features are normalized to [0, 1] or [-1, 1].
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from numpy.typing import NDArray
from scipy.fft import dct


# ---------------------------------------------------------------------------
# Feature vector container
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FeatureVector:
    """42-dimensional feature vector from audio analysis.

    Dimensions:
        0-12:   MFCCs (13)
        13-24:  Chroma features (12)
        25-30:  Spectral contrast (6)
        31-36:  Rhythmic features (6)
        37-41:  Tonal features (5)
    """
    mfccs: NDArray[np.float64]       # (13,)
    chroma: NDArray[np.float64]      # (12,)
    spectral_contrast: NDArray[np.float64]  # (6,)
    rhythmic: NDArray[np.float64]    # (6,)
    tonal: NDArray[np.float64]       # (5,)

    def to_array(self) -> NDArray[np.float64]:
        """Concatenate all features into a single 42-dim vector."""
        return np.concatenate([
            self.mfccs,
            self.chroma,
            self.spectral_contrast,
            self.rhythmic,
            self.tonal,
        ])

    @classmethod
    def from_array(cls, arr: NDArray[np.float64]) -> "FeatureVector":
        """Construct from a 42-dim array."""
        arr = np.asarray(arr, dtype=np.float64)
        if arr.shape != (42,):
            raise ValueError(f"Expected shape (42,), got {arr.shape}")
        return cls(
            mfccs=arr[0:13].copy(),
            chroma=arr[13:25].copy(),
            spectral_contrast=arr[25:31].copy(),
            rhythmic=arr[31:37].copy(),
            tonal=arr[37:42].copy(),
        )

    @property
    def dim(self) -> int:
        return 42


# ---------------------------------------------------------------------------
# Helper: mel scale conversions
# ---------------------------------------------------------------------------

def _hz_to_mel(freq: float) -> float:
    """Convert frequency in Hz to mel scale."""
    return 2595.0 * np.log10(1.0 + freq / 700.0)


def _mel_to_hz(mel: float) -> float:
    """Convert mel scale to frequency in Hz."""
    return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)


def _mel_filterbank(
    n_filters: int = 26,
    n_fft: int = 2048,
    sr: int = 44100,
    fmin: float = 0.0,
    fmax: Optional[float] = None,
) -> NDArray[np.float64]:
    """Create a mel-scale triangular filter bank.

    Parameters
    ----------
    n_filters : int
        Number of mel filters.
    n_fft : int
        FFT size used for spectrum computation.
    sr : int
        Sample rate.
    fmin : float
        Minimum frequency (Hz).
    fmax : float or None
        Maximum frequency (Hz). Defaults to sr/2.

    Returns
    -------
    filterbank : ndarray of shape (n_filters, n_fft//2 + 1)
    """
    if fmax is None:
        fmax = sr / 2.0

    mel_min = _hz_to_mel(fmin)
    mel_max = _hz_to_mel(fmax)
    mel_points = np.linspace(mel_min, mel_max, n_filters + 2)
    hz_points = np.array([_mel_to_hz(m) for m in mel_points])

    bin_points = np.floor((n_fft + 1) * hz_points / sr).astype(int)

    n_bins = n_fft // 2 + 1
    filterbank = np.zeros((n_filters, n_bins), dtype=np.float64)

    for i in range(n_filters):
        left = bin_points[i]
        center = bin_points[i + 1]
        right = bin_points[i + 2]

        # Rising slope
        if center > left:
            for j in range(left, center):
                filterbank[i, j] = (j - left) / (center - left)

        # Peak
        filterbank[i, min(center, n_bins - 1)] = 1.0

        # Falling slope
        if right > center:
            for j in range(center, right):
                filterbank[i, j] = (right - j) / (right - center)

    return filterbank


# ---------------------------------------------------------------------------
# MFCC extraction
# ---------------------------------------------------------------------------

def _extract_mfccs(
    audio: NDArray[np.float64],
    sr: int = 44100,
    n_mfcc: int = 13,
    n_filters: int = 26,
    n_fft: int = 2048,
    hop_length: Optional[int] = None,
) -> NDArray[np.float64]:
    """Extract MFCCs from audio.

    Parameters
    ----------
    audio : ndarray
        Audio samples in [-1, 1].
    sr : int
        Sample rate.
    n_mfcc : int
        Number of MFCCs to return.
    n_filters : int
        Number of mel filters.
    n_fft : int
        FFT window size.
    hop_length : int or None
        Hop between frames. Defaults to n_fft // 4.

    Returns
    -------
    mfccs : ndarray of shape (n_mfcc,)
        Mean MFCCs normalized to [0, 1].
    """
    if hop_length is None:
        hop_length = n_fft // 4

    # Frame-based analysis
    n_frames = max(1, (len(audio) - n_fft) // hop_length + 1)

    if n_frames == 0 or len(audio) < n_fft:
        # Pad audio if too short
        audio = np.pad(audio, (0, max(0, n_fft - len(audio))))

    filterbank = _mel_filterbank(n_filters, n_fft, sr)

    all_mfccs = np.zeros((n_frames, n_mfcc), dtype=np.float64)

    for i in range(n_frames):
        start = i * hop_length
        end = min(start + n_fft, len(audio))
        frame = np.zeros(n_fft, dtype=np.float64)
        frame[:end - start] = audio[start:end]

        # Windowed FFT
        windowed = frame * np.hanning(n_fft)
        spectrum = np.abs(np.fft.rfft(windowed))

        # Apply mel filterbank
        mel_energies = np.dot(filterbank, spectrum)
        mel_energies = np.maximum(mel_energies, 1e-10)

        # Log energies
        log_energies = np.log(mel_energies)

        # DCT to get MFCCs
        mfcc_frame = dct(log_energies, type=2, norm='ortho')[:n_mfcc]
        all_mfccs[i] = mfcc_frame

    # Average across frames
    mean_mfccs = np.mean(all_mfccs, axis=0)

    # Normalize to [0, 1] using sigmoid-like transform
    # MFCCs are unbounded; use tanh normalization
    normalized = 0.5 * (1.0 + np.tanh(mean_mfccs / 10.0))

    return normalized


# ---------------------------------------------------------------------------
# Chroma features
# ---------------------------------------------------------------------------

def _extract_chroma(
    audio: NDArray[np.float64],
    sr: int = 44100,
    n_fft: int = 4096,
    hop_length: Optional[int] = None,
) -> NDArray[np.float64]:
    """Extract chroma features mapping spectrum to 12 pitch classes.

    Uses Gaussian weighting around each pitch class centre with sigma=0.5 semitones.

    Parameters
    ----------
    audio : ndarray
        Audio samples.
    sr : int
        Sample rate.
    n_fft : int
        FFT size.
    hop_length : int or None
        Hop between frames.

    Returns
    -------
    chroma : ndarray of shape (12,)
        Chroma vector summing to 1.
    """
    if hop_length is None:
        hop_length = n_fft // 4

    n_frames = max(1, (len(audio) - n_fft) // hop_length + 1)

    if len(audio) < n_fft:
        audio = np.pad(audio, (0, max(0, n_fft - len(audio))))

    chroma_accum = np.zeros(12, dtype=np.float64)

    for i in range(n_frames):
        start = i * hop_length
        end = min(start + n_fft, len(audio))
        frame = np.zeros(n_fft, dtype=np.float64)
        frame[:end - start] = audio[start:end]

        windowed = frame * np.hanning(n_fft)
        spectrum = np.abs(np.fft.rfft(windowed))
        freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)

        sigma = 0.5  # semitones

        for freq, mag in zip(freqs, spectrum):
            if freq < 20.0 or freq > 8000.0:
                continue

            midi_float = 12.0 * np.log2(freq / 440.0) + 69.0
            pc_float = midi_float % 12.0

            # Gaussian-weighted contribution to all 12 pitch classes
            for pc in range(12):
                # Circular distance in semitones
                dist = min(abs(pc_float - pc), 12.0 - abs(pc_float - pc))
                weight = np.exp(-0.5 * (dist / sigma) ** 2)
                chroma_accum[pc] += mag * weight

    # Normalize to sum to 1
    total = chroma_accum.sum()
    if total > 0:
        chroma_accum /= total
    else:
        chroma_accum = np.ones(12, dtype=np.float64) / 12.0

    return chroma_accum


# ---------------------------------------------------------------------------
# Spectral contrast
# ---------------------------------------------------------------------------

def _extract_spectral_contrast(
    audio: NDArray[np.float64],
    sr: int = 44100,
    n_fft: int = 2048,
    hop_length: Optional[int] = None,
) -> NDArray[np.float64]:
    """Extract spectral contrast in 6 sub-bands.

    Sub-bands: [0-200], [200-400], [400-800], [800-1600], [1600-3200], [3200-sr/2] Hz

    Parameters
    ----------
    audio : ndarray
        Audio samples.
    sr : int
        Sample rate.
    n_fft : int
        FFT size.
    hop_length : int or None
        Hop between frames.

    Returns
    -------
    contrast : ndarray of shape (6,)
        Valley/peak ratio for each sub-band, normalized to [0, 1].
    """
    if hop_length is None:
        hop_length = n_fft // 4

    sub_band_edges = [0, 200, 400, 800, 1600, 3200, sr // 2]

    n_frames = max(1, (len(audio) - n_fft) // hop_length + 1)

    if len(audio) < n_fft:
        audio = np.pad(audio, (0, max(0, n_fft - len(audio))))

    contrast_accum = np.zeros(6, dtype=np.float64)
    valid_frames = 0

    for i in range(n_frames):
        start = i * hop_length
        end = min(start + n_fft, len(audio))
        frame = np.zeros(n_fft, dtype=np.float64)
        frame[:end - start] = audio[start:end]

        windowed = frame * np.hanning(n_fft)
        spectrum = np.abs(np.fft.rfft(windowed))
        freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)

        for band_idx in range(6):
            lo = sub_band_edges[band_idx]
            hi = sub_band_edges[band_idx + 1]

            mask = (freqs >= lo) & (freqs < hi)
            band_vals = spectrum[mask]

            if len(band_vals) < 2:
                continue

            # Peak: 90th percentile, Valley: 10th percentile
            peak = np.percentile(band_vals, 90)
            valley = np.percentile(band_vals, 10)

            if peak > 1e-10:
                # Valley/peak ratio; high contrast = low ratio
                ratio = valley / peak
                contrast_accum[band_idx] += ratio

        valid_frames += 1

    if valid_frames > 0:
        contrast_accum /= valid_frames

    # Already in [0, 1] since valley <= peak
    return np.clip(contrast_accum, 0.0, 1.0)


# ---------------------------------------------------------------------------
# Rhythmic features
# ---------------------------------------------------------------------------

def _extract_rhythmic(
    audio: NDArray[np.float64],
    sr: int = 44100,
) -> NDArray[np.float64]:
    """Extract 6 rhythmic features.

    Features:
        0: Onset density (onsets per second)
        1: Onset regularity (normalized std of inter-onset intervals)
        2: Syncopation score (fraction of onsets on weak beats)
        3: Swing ratio (odd/even 8th note timing)
        4: Tempo estimate (from autocorrelation)
        5: Pulse clarity (peakiness of tempo autocorrelation)

    Parameters
    ----------
    audio : ndarray
        Audio samples.
    sr : int
        Sample rate.

    Returns
    -------
    rhythmic : ndarray of shape (6,)
        All values normalized to [0, 1].
    """
    duration = len(audio) / sr

    # Onset detection using spectral flux
    frame_size = 1024
    hop_size = 512
    n_frames = max(1, (len(audio) - frame_size) // hop_size + 1)

    prev_mag = np.zeros(frame_size // 2 + 1, dtype=np.float64)
    flux = np.zeros(n_frames, dtype=np.float64)

    for i in range(n_frames):
        start = i * hop_size
        end = min(start + frame_size, len(audio))
        frame = np.zeros(frame_size, dtype=np.float64)
        frame[:end - start] = audio[start:end]
        windowed = frame * np.hanning(frame_size)
        spectrum = np.abs(np.fft.rfft(windowed))
        diff = spectrum - prev_mag
        flux[i] = np.sum(np.maximum(diff, 0))
        prev_mag = spectrum

    # Peak picking for onsets
    onset_frames = []
    if flux.max() > 0:
        flux_norm = flux / flux.max()
        threshold = 0.3
        for i in range(1, len(flux_norm) - 1):
            if (flux_norm[i] > threshold
                    and flux_norm[i] > flux_norm[i - 1]
                    and flux_norm[i] >= flux_norm[i + 1]):
                min_gap = int(0.05 * sr / hop_size)
                if not onset_frames or (i - onset_frames[-1]) >= min_gap:
                    onset_frames.append(i)

    onset_times = np.array([f * hop_size / sr for f in onset_frames], dtype=np.float64)
    n_onsets = len(onset_times)

    # 0: Onset density
    onset_density = n_onsets / max(duration, 0.1)
    onset_density_norm = np.clip(onset_density / 15.0, 0, 1)  # 15 onsets/s = max

    # 1: Onset regularity (1 - CV of IOIs, inverted so high = regular)
    if n_onsets >= 3:
        iois = np.diff(onset_times)
        mean_ioi = np.mean(iois)
        if mean_ioi > 0:
            cv = np.std(iois) / mean_ioi
            onset_regularity = np.clip(1.0 - cv / 2.0, 0, 1)
        else:
            onset_regularity = 0.5
    else:
        onset_regularity = 0.5

    # 2: Syncopation score
    if n_onsets >= 2 and duration > 0:
        # Assume 4/4 time; weak beats are off-beat 8th notes
        # Estimate beat period from onset autocorrelation
        beat_period = _estimate_beat_period(onset_times, sr, hop_size)
        if beat_period > 0:
            eighth_period = beat_period / 2.0
            syncopation_count = 0
            for t in onset_times:
                # Position within beat
                pos_in_beat = (t % beat_period) / beat_period
                # Weak if closer to midpoint than start
                if abs(pos_in_beat - 0.5) < abs(pos_in_beat) and pos_in_beat > 0.25:
                    syncopation_count += 1
            syncopation = syncopation_count / max(n_onsets, 1)
        else:
            syncopation = 0.5
    else:
        syncopation = 0.5

    # 3: Swing ratio
    if n_onsets >= 4:
        iois = np.diff(onset_times)
        if len(iois) >= 2:
            # Pair consecutive IOIs
            n_pairs = len(iois) // 2
            ratios = []
            for j in range(n_pairs):
                even_ioi = iois[2 * j]
                odd_ioi = iois[2 * j + 1]
                if odd_ioi > 1e-6:
                    ratios.append(even_ioi / odd_ioi)
            if ratios:
                swing = float(np.median(ratios))
                # Normalize: ratio 1 = no swing, 2 = triplet swing
                swing_ratio = np.clip(abs(swing - 1.0) / 1.0, 0, 1)
            else:
                swing_ratio = 0.0
        else:
            swing_ratio = 0.0
    else:
        swing_ratio = 0.0

    # 4 & 5: Tempo estimate and pulse clarity from onset autocorrelation
    tempo, pulse_clarity = _estimate_tempo(onset_times, duration, sr, hop_size)
    # Normalize tempo: 60-200 BPM mapped to [0, 1]
    tempo_norm = np.clip((tempo - 60) / 140.0, 0, 1)

    return np.array([
        onset_density_norm,
        onset_regularity,
        syncopation,
        swing_ratio,
        tempo_norm,
        pulse_clarity,
    ], dtype=np.float64)


def _estimate_beat_period(
    onset_times: NDArray[np.float64],
    sr: int,
    hop_size: int,
) -> float:
    """Estimate beat period from onset times using IOI histogram.

    Returns
    -------
    beat_period : float
        Estimated beat period in seconds, or 0 if estimation fails.
    """
    if len(onset_times) < 3:
        return 0.0

    iois = np.diff(onset_times)
    if len(iois) == 0:
        return 0.0

    # Build histogram of IOIs (quantized to 10ms bins)
    max_ioi = min(float(np.percentile(iois, 95)), 2.0)
    if max_ioi < 0.05:
        return 0.0

    bins = np.arange(0.05, max_ioi + 0.05, 0.01)
    if len(bins) < 2:
        return float(np.median(iois))

    hist, edges = np.histogram(iois, bins=bins)
    if hist.max() == 0:
        return float(np.median(iois))

    peak_idx = np.argmax(hist)
    beat_period = (edges[peak_idx] + edges[peak_idx + 1]) / 2.0
    return max(beat_period, 0.1)


def _estimate_tempo(
    onset_times: NDArray[np.float64],
    duration: float,
    sr: int,
    hop_size: int,
) -> tuple[float, float]:
    """Estimate tempo and pulse clarity from onset autocorrelation.

    Returns
    -------
    tempo : float
        Estimated tempo in BPM.
    pulse_clarity : float
        Peakiness of autocorrelation in [0, 1].
    """
    if len(onset_times) < 3 or duration < 0.5:
        return 120.0, 0.5  # default

    # Create onset function at 100 Hz resolution
    resample_rate = 100
    n_bins = int(duration * resample_rate) + 1
    onset_func = np.zeros(n_bins, dtype=np.float64)

    for t in onset_times:
        idx = int(t * resample_rate)
        if 0 <= idx < n_bins:
            onset_func[idx] = 1.0

    # Autocorrelation
    n_lag = min(n_bins, int(3.0 * resample_rate))  # up to 3 seconds
    autocorr = np.zeros(n_lag, dtype=np.float64)
    mean_val = onset_func.mean()

    for lag in range(1, n_lag):
        corr = np.mean((onset_func[:n_bins - lag] - mean_val) *
                        (onset_func[lag:] - mean_val))
        autocorr[lag] = corr

    # Look for peaks in tempo range (60-200 BPM → 0.3-1.0 seconds)
    min_lag = max(1, int(0.3 * resample_rate))  # 200 BPM
    max_lag = min(n_lag - 1, int(2.0 * resample_rate))  # 30 BPM

    if max_lag <= min_lag:
        return 120.0, 0.5

    search_region = autocorr[min_lag:max_lag + 1]
    if search_region.max() <= 0:
        return 120.0, 0.5

    # Find peaks
    peak_lag_rel = np.argmax(search_region)
    peak_val = search_region[peak_lag_rel]
    peak_lag = peak_lag_rel + min_lag

    # Tempo from lag
    beat_period = peak_lag / resample_rate
    tempo = 60.0 / max(beat_period, 0.1)

    # Pulse clarity: ratio of peak to mean autocorrelation
    mean_ac = np.mean(np.abs(search_region))
    pulse_clarity = np.clip(peak_val / max(mean_ac, 1e-10), 0, 1)
    # Normalize further
    pulse_clarity = np.clip(pulse_clarity / 5.0, 0, 1)

    return float(np.clip(tempo, 30, 300)), float(pulse_clarity)


# ---------------------------------------------------------------------------
# Tonal features
# ---------------------------------------------------------------------------

# Krumhansl-Kessler key profiles (relative weights for each pitch class)
_MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88],
                          dtype=np.float64)
_MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17],
                          dtype=np.float64)


def _extract_tonal(
    audio: NDArray[np.float64],
    sr: int = 44100,
    n_fft: int = 4096,
    chroma: Optional[NDArray[np.float64]] = None,
) -> NDArray[np.float64]:
    """Extract 5 tonal features.

    Features:
        0: Key clarity (Krumhansl-Schmuckler correlation)
        1: Mode (major vs minor, from relative 3rd degree weight)
        2: Harmonic complexity (entropy of pitch class distribution)
        3: Tonal tension (distance from best key profile)
        4: Modulation frequency (key change rate estimate)

    Parameters
    ----------
    audio : ndarray
        Audio samples.
    sr : int
        Sample rate.
    n_fft : int
        FFT size.
    chroma : ndarray or None
        Pre-computed chroma features (12,). Computed if not provided.

    Returns
    -------
    tonal : ndarray of shape (5,)
        All values normalized to [0, 1].
    """
    if chroma is None:
        chroma = _extract_chroma(audio, sr, n_fft)

    # 0: Key clarity — correlation with best-matching key profile
    best_corr, best_key, best_is_major = _find_best_key(chroma)

    # Key clarity is the absolute correlation value
    key_clarity = np.clip(abs(best_corr) / 1.0, 0, 1)

    # 1: Mode (major=1, minor=0, with intermediate values)
    # Use the relative weight of the 3rd degree (pitch classes 3 or 4)
    # Major 3rd = pc 4, minor 3rd = pc 3
    major_third = chroma[4]
    minor_third = chroma[3]
    if (major_third + minor_third) > 1e-10:
        mode = major_third / (major_third + minor_third)
    else:
        mode = 0.5
    # Also factor in the Krumhansl result
    if best_is_major:
        mode = 0.5 + 0.5 * mode
    else:
        mode = 0.5 * mode

    # 2: Harmonic complexity (entropy of pitch class distribution)
    pc_probs = chroma[chroma > 0]
    if len(pc_probs) > 0:
        entropy = -np.sum(pc_probs * np.log2(pc_probs))
        max_entropy = np.log2(12)  # ≈ 3.585
        harmonic_complexity = np.clip(entropy / max_entropy, 0, 1)
    else:
        harmonic_complexity = 0.5

    # 3: Tonal tension (1 - key clarity, inverted)
    tonal_tension = 1.0 - key_clarity

    # 4: Modulation frequency estimate
    # Frame-based chroma analysis to detect key changes
    hop_length = n_fft // 4
    n_frames = max(1, (len(audio) - n_fft) // hop_length + 1)

    if n_frames > 2:
        # Get key estimates for each frame
        frame_keys = []
        for i in range(n_frames):
            start = i * hop_length
            end = min(start + n_fft, len(audio))
            frame = np.zeros(n_fft, dtype=np.float64)
            frame[:end - start] = audio[start:end]
            frame_chroma = _compute_frame_chroma(frame, sr, n_fft)
            _, key, _ = _find_best_key(frame_chroma)
            frame_keys.append(key)

        # Count key changes
        changes = sum(1 for i in range(1, len(frame_keys))
                      if frame_keys[i] != frame_keys[i - 1])
        modulation_freq = changes / max(duration_from_audio_len(len(audio), sr), 0.1)
        modulation_norm = np.clip(modulation_freq / 2.0, 0, 1)  # 2 changes/sec = max
    else:
        modulation_norm = 0.0

    return np.array([
        key_clarity,
        np.clip(mode, 0, 1),
        harmonic_complexity,
        tonal_tension,
        modulation_norm,
    ], dtype=np.float64)


def _compute_frame_chroma(
    frame: NDArray[np.float64],
    sr: int,
    n_fft: int,
) -> NDArray[np.float64]:
    """Compute chroma for a single frame."""
    windowed = frame * np.hanning(len(frame))
    spectrum = np.abs(np.fft.rfft(windowed))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)

    chroma = np.zeros(12, dtype=np.float64)
    sigma = 0.5

    for freq, mag in zip(freqs, spectrum):
        if freq < 20.0 or freq > 8000.0:
            continue
        midi_float = 12.0 * np.log2(freq / 440.0) + 69.0
        pc_float = midi_float % 12.0
        for pc in range(12):
            dist = min(abs(pc_float - pc), 12.0 - abs(pc_float - pc))
            weight = np.exp(-0.5 * (dist / sigma) ** 2)
            chroma[pc] += mag * weight

    total = chroma.sum()
    if total > 0:
        chroma /= total
    return chroma


def _find_best_key(chroma: NDArray[np.float64]) -> tuple[float, int, bool]:
    """Find the best-matching key using Krumhansl-Schmuckler algorithm.

    Returns
    -------
    correlation : float
        Pearson correlation with the best key profile.
    key : int
        Best key pitch class (0-11).
    is_major : bool
        Whether the best match is major mode.
    """
    best_corr = -2.0
    best_key = 0
    best_is_major = True

    for shift in range(12):
        # Rotate chroma
        rotated = np.roll(chroma, -shift)

        # Major correlation
        corr_major = _pearson_correlation(rotated, _MAJOR_PROFILE)
        if corr_major > best_corr:
            best_corr = corr_major
            best_key = shift
            best_is_major = True

        # Minor correlation
        corr_minor = _pearson_correlation(rotated, _MINOR_PROFILE)
        if corr_minor > best_corr:
            best_corr = corr_minor
            best_key = shift
            best_is_major = False

    return best_corr, best_key, best_is_major


def _pearson_correlation(x: NDArray[np.float64], y: NDArray[np.float64]) -> float:
    """Compute Pearson correlation coefficient."""
    x_mean = x - np.mean(x)
    y_mean = y - np.mean(y)
    num = np.sum(x_mean * y_mean)
    den = np.sqrt(np.sum(x_mean ** 2) * np.sum(y_mean ** 2))
    if den < 1e-10:
        return 0.0
    return float(num / den)


def duration_from_audio_len(n_samples: int, sr: int) -> float:
    """Get duration in seconds from sample count and sample rate."""
    return n_samples / sr


# ---------------------------------------------------------------------------
# Main extraction function
# ---------------------------------------------------------------------------

def extract_features(audio: NDArray[np.float64], sr: int = 44100) -> FeatureVector:
    """Extract a 42-dimensional feature vector from audio.

    Parameters
    ----------
    audio : ndarray of float64
        Audio samples normalized to [-1, 1].
    sr : int
        Sample rate (default 44100).

    Returns
    -------
    FeatureVector
        42-dimensional feature vector with components:
        - MFCCs (13 dims): Mel-frequency cepstral coefficients
        - Chroma (12 dims): Pitch class distribution
        - Spectral contrast (6 dims): Sub-band valley/peak ratios
        - Rhythmic (6 dims): Onset density, regularity, syncopation, etc.
        - Tonal (5 dims): Key clarity, mode, harmonic complexity, etc.

    Notes
    -----
    All features are normalized to [0, 1]. Handles edge cases:
    - Silence returns zeros
    - Very short audio (< 0.1s) returns approximate features
    - Single pitch audio handled gracefully
    """
    audio = np.asarray(audio, dtype=np.float64)

    # Handle silence
    if np.max(np.abs(audio)) < 1e-10:
        return FeatureVector(
            mfccs=np.zeros(13, dtype=np.float64),
            chroma=np.ones(12, dtype=np.float64) / 12.0,
            spectral_contrast=np.zeros(6, dtype=np.float64),
            rhythmic=np.zeros(6, dtype=np.float64),
            tonal=np.zeros(5, dtype=np.float64),
        )

    # Handle very short audio by padding
    min_samples = int(0.1 * sr)
    if len(audio) < min_samples:
        audio = np.pad(audio, (0, min_samples - len(audio)))

    # Extract MFCCs
    mfccs = _extract_mfccs(audio, sr)

    # Extract chroma
    chroma = _extract_chroma(audio, sr)

    # Extract spectral contrast
    spectral_contrast = _extract_spectral_contrast(audio, sr)

    # Extract rhythmic features
    rhythmic = _extract_rhythmic(audio, sr)

    # Extract tonal features (reuses chroma)
    tonal = _extract_tonal(audio, sr, chroma=chroma)

    return FeatureVector(
        mfccs=mfccs,
        chroma=chroma,
        spectral_contrast=spectral_contrast,
        rhythmic=rhythmic,
        tonal=tonal,
    )
