"""Tests for the datasets module."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest

from constraint_toolkit.datasets import label_from_filename, Dataset, AudioSample
from constraint_toolkit.dials import DialPosition
from constraint_toolkit.features import FeatureVector


def _make_feature_vector(seed=0):
    rng = np.random.RandomState(seed)
    return FeatureVector(
        mfccs=rng.randn(13),
        chroma=rng.rand(12),
        spectral_contrast=rng.rand(6),
        rhythmic=rng.rand(6),
        tonal=rng.rand(5),
    )


def _make_audio_sample(label="Jazz", seed=0):
    fv = _make_feature_vector(seed)
    return AudioSample(
        path=Path(f"test_{seed}.wav"),
        label=label,
        audio=np.zeros(1000),
        sr=22050,
        features={"feature_vector": fv},
        dial_position=DialPosition(2.5, 2.5, 2.5),
    )


class TestLabelFromFilename:
    def test_jazz_label(self):
        assert label_from_filename("jazz_bebop_C.wav") == "Jazz"

    def test_edm_label(self):
        assert label_from_filename("techno_electronic_techno_C.wav") == "EDM"

    def test_blues_label(self):
        assert label_from_filename("blues_delta_sample.wav") == "Blues"

    def test_classical_label(self):
        assert label_from_filename("fugue_baroque_sample.wav") == "Classical"

    def test_unknown_label(self):
        assert label_from_filename("random_noise.wav") == "Unknown"

    def test_hindustani_label(self):
        assert label_from_filename("hindustani_raga_test.wav") == "Hindustani"


class TestDatasetSplit:
    def test_split_sizes_sum_correctly(self):
        ds = Dataset()
        for i in range(20):
            ds.audio_samples.append(
                _make_audio_sample("Jazz" if i < 10 else "Blues", seed=i)
            )
        train, test = ds.split(ratio=0.8)
        assert train.size + test.size == ds.size


class TestBootstrappedAccuracy:
    def test_bootstrapped_accuracy_returns_dict(self):
        ds = Dataset()
        for i in range(10):
            label = "Jazz" if i < 5 else "Blues"
            ds.audio_samples.append(_make_audio_sample(label, seed=i))

        from constraint_toolkit.classifier import DialClassifier
        result = ds.bootstrapped_accuracy(DialClassifier, n=10, seed=42)
        assert "mean" in result
        assert "ci_lower" in result
        assert "ci_upper" in result


class TestLoadWorkspaceWavs:
    def test_load_workspace_wavs_empty_dir(self):
        ds = Dataset()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ds.load_workspace_wavs(tmpdir)
            assert isinstance(result, dict)
            assert len(result) == 0
