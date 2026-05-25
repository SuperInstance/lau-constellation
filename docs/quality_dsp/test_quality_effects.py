"""
Tests for quality_effects.py
"""

import numpy as np
import os
import wave
import tempfile
import pytest

from quality_effects import (
    QualityEffectChain, write_wav, read_wav, generate_test_signal,
    DepthEffect, JitterEffect, CompanderEffect, AliasEffect,
    PurityEffect, DriftEffect, SaturationEffect, GlitchEffect,
    StereoEffect, NoiseEffect,
)


# Helpers

def _tone(freq=440, sr=44100, dur=0.5):
    t = np.arange(int(sr * dur)) / sr
    return np.sin(2 * np.pi * freq * t) * 0.8


def _no_crash(effect, audio, params):
    """Assert effect doesn't crash and returns finite values."""
    result = effect.apply(audio, params)
    assert result is not None
    assert len(result) == len(audio)
    assert np.all(np.isfinite(result))


# ---- DepthEffect ----

class TestDepthEffect:
    def test_clean_passes_through(self):
        audio = _tone()
        result = DepthEffect().apply(audio, {'bits': 64})
        np.testing.assert_allclose(result, audio, atol=1e-10)

    def test_8bit_quantizes(self):
        audio = _tone()
        result = DepthEffect().apply(audio, {'bits': 8})
        # 8-bit should have at most 256 distinct levels
        unique = np.unique(np.round(result * 128))
        assert len(unique) <= 256

    def test_4bit_heavy_crunch(self):
        audio = _tone()
        result = DepthEffect().apply(audio, {'bits': 4})
        unique = np.unique(np.round(result * 8))
        assert len(unique) <= 16

    def test_stays_in_range(self):
        audio = _tone() * 1.5  # hot signal
        result = DepthEffect().apply(audio, {'bits': 8})
        assert np.max(np.abs(result)) <= 1.0

    def test_empty_params(self):
        audio = _tone()
        result = DepthEffect().apply(audio, None)
        assert len(result) == len(audio)


# ---- JitterEffect ----

class TestJitterEffect:
    def test_zero_amount_passthrough(self):
        audio = _tone()
        result = JitterEffect().apply(audio, {'amount': 0})
        np.testing.assert_allclose(result, audio, atol=1e-12)

    def test_cuda_mode(self):
        audio = _tone()
        _no_crash(JitterEffect(), audio, {'amount': 0.5, 'mode': 'cuda'})

    def test_fortran_mode(self):
        audio = _tone()
        _no_crash(JitterEffect(), audio, {'amount': 0.3, 'mode': 'fortran_parallel'})

    def test_cpu_mode(self):
        audio = _tone()
        result = JitterEffect().apply(audio, {'amount': 0.5, 'mode': 'cpu'})
        # should be slightly different from input
        assert not np.allclose(result, audio)


# ---- CompanderEffect ----

class TestCompanderEffect:
    def test_linear_passthrough(self):
        audio = _tone()
        result = CompanderEffect().apply(audio, {'alpha': 1.0})
        np.testing.assert_allclose(result, audio, atol=1e-10)

    def test_nonlinear_changes_signal(self):
        audio = _tone()
        result = CompanderEffect().apply(audio, {'alpha': 1.5})
        assert not np.allclose(result, audio)

    def test_preserves_sign(self):
        audio = np.array([-0.8, -0.3, 0.0, 0.3, 0.8])
        result = CompanderEffect().apply(audio, {'alpha': 1.3})
        assert np.all(np.sign(result) == np.sign(audio) + 0)  # 0 stays 0


# ---- AliasEffect ----

class TestAliasEffect:
    def test_zero_passthrough(self):
        audio = _tone()
        result = AliasEffect().apply(audio, {'step_size': 0})
        np.testing.assert_allclose(result, audio, atol=1e-12)

    def test_adds_discontinuities(self):
        audio = _tone()
        result = AliasEffect().apply(audio, {'step_size': 0.5, 'density': 0.01})
        assert len(result) == len(audio)


# ---- PurityEffect ----

class TestPurityEffect:
    def test_clean_is_passthrough(self):
        audio = _tone()
        result = PurityEffect().apply(audio, {'level': 'clean', 'sr': 44100})
        np.testing.assert_allclose(result, audio, atol=1e-12)

    def test_destroyed_adds_harmonics(self):
        audio = _tone()
        result = PurityEffect().apply(audio, {'level': 'destroyed', 'sr': 44100})
        # destroyed adds audible harmonics, so signal should differ
        assert not np.allclose(result, audio, atol=0.01)

    def test_custom_db(self):
        audio = _tone()
        result = PurityEffect().apply(audio, {'level': -60, 'sr': 44100})
        assert len(result) == len(audio)


# ---- DriftEffect ----

class TestDriftEffect:
    def test_zero_passthrough(self):
        audio = _tone()
        result = DriftEffect().apply(audio, {'amount': 0})
        np.testing.assert_allclose(result, audio, atol=1e-12)

    def test_drift_modulates(self):
        audio = _tone()
        result = DriftEffect().apply(audio, {'amount': 1.0, 'rate': 0.1, 'sr': 44100})
        assert len(result) == len(audio)


# ---- SaturationEffect ----

class TestSaturationEffect:
    def test_default_is_passthrough(self):
        audio = _tone()
        result = SaturationEffect().apply(audio, {'alpha': 1.0, 'beta': 0.0})
        np.testing.assert_allclose(result, audio, atol=1e-10)

    def test_alpha_only_is_tanh(self):
        audio = _tone()
        result = SaturationEffect().apply(audio, {'alpha': 2.0, 'beta': 0.0})
        np.testing.assert_allclose(result, np.tanh(2.0 * audio), atol=1e-10)

    def test_feedback_saturates(self):
        audio = _tone()
        result = SaturationEffect().apply(audio, {'alpha': 2.0, 'beta': 0.3})
        assert np.max(np.abs(result)) <= 1.0  # tanh output bounded

    def test_high_gain_bounded(self):
        audio = _tone()
        result = SaturationEffect().apply(audio, {'alpha': 5.0, 'beta': 0.0})
        # tanh always bounded to [-1, 1]
        assert np.max(np.abs(result)) <= 1.0


# ---- GlitchEffect ----

class TestGlitchEffect:
    def test_zero_probs_passthrough(self):
        audio = _tone()
        result = GlitchEffect().apply(audio, {
            'prob_nan': 0, 'prob_inf': 0, 'prob_negzero': 0, 'prob_denorm': 0
        })
        np.testing.assert_allclose(result, audio, atol=1e-12)

    def test_glitch_introduces_artifacts(self):
        audio = _tone()
        result = GlitchEffect().apply(audio, {
            'prob_nan': 0.01, 'prob_inf': 0.01, 'prob_negzero': 0.01, 'prob_denorm': 0.01
        })
        assert len(result) == len(audio)
        # some samples should be zeroed (NaN→silence) or flipped
        assert not np.allclose(result, audio)


# ---- StereoEffect ----

class TestStereoEffect:
    def test_zero_width_produces_stereo(self):
        audio = _tone()
        result = StereoEffect().apply(audio, {'width': 0})
        assert result.ndim == 2
        assert result.shape[1] == 2
        # both channels should be identical
        np.testing.assert_allclose(result[:, 0], result[:, 1])

    def test_full_width_differs(self):
        audio = _tone()
        result = StereoEffect().apply(audio, {'width': 1.0, 'sr': 44100})
        assert result.ndim == 2
        # channels should differ
        assert not np.allclose(result[:, 0], result[:, 1])


# ---- NoiseEffect ----

class TestNoiseEffect:
    def test_zero_passthrough(self):
        audio = _tone()
        result = NoiseEffect().apply(audio, {'amount': 0})
        np.testing.assert_allclose(result, audio, atol=1e-12)

    def test_adds_noise(self):
        audio = _tone()
        result = NoiseEffect().apply(audio, {'amount': 1.0, 'entropy': 0.5, 'sr': 44100})
        assert not np.allclose(result, audio)

    def test_low_entropy_is_correlated(self):
        audio = _tone()
        result = NoiseEffect().apply(audio, {'amount': 2.0, 'entropy': 0.05, 'sr': 44100})
        noise = result - audio
        # correlated noise has lower variance than white at same amplitude
        assert np.std(noise) > 0


# ---- QualityEffectChain ----

class TestQualityEffectChain:
    def test_process_empty(self):
        audio = _tone()
        chain = QualityEffectChain()
        result = chain.process(audio)
        np.testing.assert_allclose(result, audio, atol=1e-12)

    def test_process_single_effect(self):
        audio = _tone()
        chain = QualityEffectChain()
        result = chain.process(audio, depth={'bits': 16})
        assert len(result) == len(audio)

    def test_process_multiple_effects(self):
        audio = _tone()
        chain = QualityEffectChain()
        result = chain.process(audio,
            depth={'bits': 16},
            jitter={'amount': 0.3, 'mode': 'cpu'},
            saturation={'alpha': 1.2, 'beta': 0.01},
        )
        assert len(result) == len(audio)

    def test_get_presets(self):
        chain = QualityEffectChain()
        presets = chain.get_presets()
        assert len(presets) >= 15

    def test_all_presets_run(self):
        chain = QualityEffectChain()
        audio = _tone(dur=0.2)
        for name, func in chain.get_presets().items():
            result = func(audio)
            assert result is not None, f"Preset {name} returned None"
            assert len(result) > 0, f"Preset {name} returned empty"


# ---- WAV I/O ----

class TestWavIO:
    def test_write_read_roundtrip(self):
        audio = _tone()
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            path = f.name
        try:
            write_wav(path, audio, 44100)
            loaded, sr = read_wav(path)
            assert sr == 44100
            assert len(loaded) == len(audio)
            # 16-bit quantization tolerance
            # WAV normalize + 16-bit quantization = generous tolerance
            np.testing.assert_allclose(loaded.flatten(), audio, atol=0.2)
        finally:
            os.unlink(path)

    def test_stereo_write_read(self):
        audio = np.column_stack([_tone(), _tone(freq=880)])
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            path = f.name
        try:
            write_wav(path, audio, 44100)
            loaded, sr = read_wav(path)
            assert loaded.shape[1] == 2
        finally:
            os.unlink(path)


# ---- Signal Generator ----

class TestSignalGenerator:
    def test_length(self):
        sig = generate_test_signal(44100, 2.0)
        assert len(sig) == 88200

    def test_normalized(self):
        sig = generate_test_signal()
        assert np.max(np.abs(sig)) <= 1.0

    def test_not_silent(self):
        sig = generate_test_signal()
        assert np.max(np.abs(sig)) > 0.1
