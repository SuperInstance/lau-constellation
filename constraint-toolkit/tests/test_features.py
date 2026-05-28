"""Tests for the feature extraction module."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from constraint_toolkit.features import (
    FeatureVector,
    extract_features,
    _extract_mfccs,
    _extract_chroma,
    _extract_spectral_contrast,
    _extract_rhythmic,
    _extract_tonal,
)


def _make_sine(freq=440.0, duration=2.0, sr=44100):
    """Generate a sine wave audio signal."""
    t = np.linspace(0, duration, int(sr * duration), dtype=np.float64)
    return np.sin(2 * np.pi * freq * t) * 0.5


def _make_complex_audio(duration=3.0, sr=44100):
    """Generate audio with multiple harmonics and rhythmic content."""
    t = np.linspace(0, duration, int(sr * duration), dtype=np.float64)
    # Fundamental + harmonics
    audio = (
        0.4 * np.sin(2 * np.pi * 261.63 * t)   # C4
        + 0.3 * np.sin(2 * np.pi * 329.63 * t)  # E4
        + 0.2 * np.sin(2 * np.pi * 392.00 * t)  # G4
        + 0.1 * np.sin(2 * np.pi * 523.25 * t)  # C5
    )
    # Add amplitude modulation for rhythmic content
    am = 0.5 + 0.5 * np.sin(2 * np.pi * 2.0 * t)  # 2 Hz modulation
    return audio * am * 0.5


class TestExtractFeatures:
    """Tests for the main extract_features function."""

    def test_extract_features_returns_42_dims(self):
        audio = _make_sine()
        fv = extract_features(audio)
        arr = fv.to_array()
        assert arr.shape == (42,), f"Expected shape (42,), got {arr.shape}"

    def test_returns_feature_vector(self):
        audio = _make_sine()
        fv = extract_features(audio)
        assert isinstance(fv, FeatureVector)

    def test_all_values_in_range(self):
        audio = _make_complex_audio()
        fv = extract_features(audio)
        arr = fv.to_array()
        assert np.all(arr >= 0.0), f"Min value: {arr.min()}"
        assert np.all(arr <= 1.0), f"Max value: {arr.max()}"

    def test_silence_returns_zeros(self):
        silence = np.zeros(44100, dtype=np.float64)
        fv = extract_features(silence)
        arr = fv.to_array()
        # MFCCs should be zero, chroma uniform, contrast zero, rhythmic zero, tonal zero
        assert np.allclose(fv.mfccs, 0.0)
        assert np.allclose(fv.chroma, 1.0 / 12.0, atol=0.01)
        assert np.allclose(fv.spectral_contrast, 0.0)
        assert np.allclose(fv.rhythmic, 0.0)
        assert np.allclose(fv.tonal, 0.0)

    def test_short_audio_handled(self):
        # Very short audio: 0.05 seconds
        short = _make_sine(freq=440, duration=0.05, sr=44100)
        fv = extract_features(short)
        arr = fv.to_array()
        assert arr.shape == (42,)
        assert not np.any(np.isnan(arr)), "NaN in features for short audio"
        assert not np.any(np.isinf(arr)), "Inf in features for short audio"

    def test_deterministic(self):
        audio = _make_sine()
        fv1 = extract_features(audio)
        fv2 = extract_features(audio)
        np.testing.assert_array_almost_equal(fv1.to_array(), fv2.to_array())

    def test_from_array_roundtrip(self):
        audio = _make_complex_audio()
        fv = extract_features(audio)
        arr = fv.to_array()
        fv2 = FeatureVector.from_array(arr)
        np.testing.assert_array_almost_equal(fv.to_array(), fv2.to_array())

    def test_from_array_wrong_shape_raises(self):
        with pytest.raises(ValueError):
            FeatureVector.from_array(np.zeros(41, dtype=np.float64))


class TestMFCCs:
    """Tests for MFCC extraction."""

    def test_mfccs_reasonable_range(self):
        audio = _make_sine()
        mfccs = _extract_mfccs(audio)
        assert mfccs.shape == (13,)
        assert np.all(mfccs >= 0.0)
        assert np.all(mfccs <= 1.0)

    def test_mfccs_different_signals(self):
        sine = _extract_mfccs(_make_sine(440))
        noise = _extract_mfccs(np.random.RandomState(42).randn(44100).astype(np.float64) * 0.1)
        # They should differ
        assert not np.allclose(sine, noise, atol=0.01)


class TestChroma:
    """Tests for chroma feature extraction."""

    def test_chroma_sums_to_one(self):
        audio = _make_sine(freq=440.0)  # A4
        chroma = _extract_chroma(audio)
        assert chroma.shape == (12,)
        assert abs(chroma.sum() - 1.0) < 0.01, f"Chroma sum: {chroma.sum()}"

    def test_chroma_detects_pitch(self):
        # A4 = 440 Hz → pitch class 9 (A)
        audio = _make_sine(freq=440.0)
        chroma = _extract_chroma(audio)
        # A should be dominant (pitch class 9)
        assert chroma[9] > 0.3, f"Expected A (pc 9) dominant, got: {chroma}"

    def test_chroma_detects_c(self):
        # C4 = 261.63 Hz → pitch class 0
        audio = _make_sine(freq=261.63)
        chroma = _extract_chroma(audio)
        assert chroma[0] > 0.3, f"Expected C (pc 0) dominant, got: {chroma}"

    def test_chroma_non_negative(self):
        audio = _make_complex_audio()
        chroma = _extract_chroma(audio)
        assert np.all(chroma >= 0.0)


class TestSpectralContrast:
    """Tests for spectral contrast extraction."""

    def test_spectral_contrast_in_range(self):
        audio = _make_complex_audio()
        contrast = _extract_spectral_contrast(audio)
        assert contrast.shape == (6,)
        assert np.all(contrast >= 0.0)
        assert np.all(contrast <= 1.0)

    def test_spectral_contrast_sine(self):
        # Pure sine should have high contrast in one band, low in others
        audio = _make_sine(freq=440.0)
        contrast = _extract_spectral_contrast(audio)
        assert contrast.shape == (6,)
        assert np.all(contrast >= 0.0)


class TestRhythmicFeatures:
    """Tests for rhythmic feature extraction."""

    def test_rhythmic_features_with_known_pattern(self):
        # Create audio with regular clicks at 4 Hz (240 BPM 16th notes)
        sr = 44100
        duration = 3.0
        n_samples = int(sr * duration)
        audio = np.zeros(n_samples, dtype=np.float64)

        click_interval = int(sr / 4.0)  # 4 clicks per second
        click_duration = int(0.01 * sr)  # 10ms clicks

        for i in range(0, n_samples, click_interval):
            end = min(i + click_duration, n_samples)
            audio[i:end] = 0.8

        rhythmic = _extract_rhythmic(audio, sr)
        assert rhythmic.shape == (6,)
        assert np.all(rhythmic >= 0.0)
        assert np.all(rhythmic <= 1.0)
        # Should have high onset density
        assert rhythmic[0] > 0.1, f"Expected higher onset density, got {rhythmic[0]}"

    def test_rhythmic_features_silence(self):
        silence = np.zeros(44100, dtype=np.float64)
        rhythmic = _extract_rhythmic(silence)
        assert rhythmic.shape == (6,)
        # Silence: low density, default regularity
        assert rhythmic[0] < 0.1  # low density

    def test_rhythmic_shape(self):
        audio = _make_complex_audio()
        rhythmic = _extract_rhythmic(audio)
        assert rhythmic.shape == (6,)


class TestTonalFeatures:
    """Tests for tonal feature extraction."""

    def test_tonal_features_with_sine_wave(self):
        # A4 sine should have clear key
        audio = _make_sine(freq=440.0)
        chroma = _extract_chroma(audio)
        tonal = _extract_tonal(audio, chroma=chroma)
        assert tonal.shape == (5,)
        assert np.all(tonal >= 0.0)
        assert np.all(tonal <= 1.0)
        # Single pitch should have reasonable key clarity
        assert tonal[0] > 0.0, f"Expected some key clarity, got {tonal[0]}"

    def test_tonal_features_complex(self):
        audio = _make_complex_audio()
        tonal = _extract_tonal(audio)
        assert tonal.shape == (5,)
        assert np.all(tonal >= 0.0)
        assert np.all(tonal <= 1.0)

    def test_mode_feature_in_range(self):
        # Major chord (C-E-G)
        audio = _make_complex_audio()
        tonal = _extract_tonal(audio)
        assert 0.0 <= tonal[1] <= 1.0  # mode

    def test_harmonic_complexity_range(self):
        audio = _make_complex_audio()
        tonal = _extract_tonal(audio)
        assert 0.0 <= tonal[2] <= 1.0  # harmonic complexity


class TestFeatureVector:
    """Tests for FeatureVector dataclass."""

    def test_dim_property(self):
        fv = extract_features(_make_sine())
        assert fv.dim == 42

    def test_component_shapes(self):
        fv = extract_features(_make_complex_audio())
        assert fv.mfccs.shape == (13,)
        assert fv.chroma.shape == (12,)
        assert fv.spectral_contrast.shape == (6,)
        assert fv.rhythmic.shape == (6,)
        assert fv.tonal.shape == (5,)

    def test_single_pitch_audio(self):
        """Single pitch should not crash."""
        audio = _make_sine(freq=440, duration=0.5)
        fv = extract_features(audio)
        assert fv.to_array().shape == (42,)
        assert not np.any(np.isnan(fv.to_array()))
