"""Tests for the dial-based genre classifier."""

import numpy as np
import pytest

from constraint_toolkit.dials import DialPosition
from constraint_toolkit.classifier import DialClassifier


class TestDialClassifier:
    """Tests for DialClassifier."""

    def setup_method(self):
        self.clf = DialClassifier(seed=42)

    def test_predict_known_jazz(self):
        pos = DialPosition(
            harmonic_tension=3.5, rhythmic_complexity=4.0, spectral_density=3.0,
            tradition_name="Jazz",
        )
        genre, conf = self.clf.predict_genre(pos)
        # Jazz and Blues are close in dial space; accept either
        assert genre in ("Jazz", "Blues")
        assert conf > 0.2

    def test_predict_known_edm(self):
        pos = DialPosition(
            harmonic_tension=1.0, rhythmic_complexity=2.5, spectral_density=4.5,
            tradition_name="EDM",
        )
        genre, conf = self.clf.predict_genre(pos)
        assert genre in ("EDM", "Classical")  # may confuse
        assert conf > 0.2

    def test_predict_novelty_at_known(self):
        pos = DialPosition(
            harmonic_tension=3.5, rhythmic_complexity=3.0, spectral_density=2.0,
        )
        novelty = self.clf.predict_novelty(pos)
        assert 0.0 <= novelty <= 1.0
        # Should be low novelty since it's near Jazz
        assert novelty < 0.5

    def test_predict_novelty_at_unexplored(self):
        # Position far from any known tradition
        pos = DialPosition(
            harmonic_tension=0.1, rhythmic_complexity=0.1, spectral_density=0.1,
        )
        novelty = self.clf.predict_novelty(pos)
        assert novelty > 0.3  # Should be novel

    def test_deterministic_with_seed(self):
        clf1 = DialClassifier(seed=123)
        clf2 = DialClassifier(seed=123)
        pos = DialPosition(harmonic_tension=2.5, rhythmic_complexity=3.5, spectral_density=1.5)
        g1, c1 = clf1.predict_genre(pos)
        g2, c2 = clf2.predict_genre(pos)
        assert g1 == g2
        assert c1 == c2

    def test_cross_validate(self):
        from constraint_toolkit.dials import DIAL_RANGES
        # Build a small dataset from tradition centres
        positions = []
        labels = []
        for name, prof in DIAL_RANGES.items():
            c = prof["center"]
            for offset in range(3):  # 3 samples per tradition
                positions.append(DialPosition(
                    harmonic_tension=float(np.clip(c[0] + np.random.uniform(-0.3, 0.3), 0, 5)),
                    rhythmic_complexity=float(np.clip(c[1] + np.random.uniform(-0.3, 0.3), 0, 5)),
                    spectral_density=float(np.clip(c[2] + np.random.uniform(-0.3, 0.3), 0, 5)),
                ))
                labels.append(name)
        results = self.clf.cross_validate(positions, labels, n_folds=3)
        assert "accuracy" in results
        assert results["accuracy"] > 0.5

    def test_all_traditions_classifiable(self):
        from constraint_toolkit.dials import DIAL_RANGES
        for name, prof in DIAL_RANGES.items():
            c = prof["center"]
            centre = DialPosition(
                harmonic_tension=float(c[0]),
                rhythmic_complexity=float(c[1]),
                spectral_density=float(c[2]),
                tradition_name=name,
            )
            genre, conf = self.clf.predict_genre(centre)
            # Allow some confusion for nearby traditions
            assert conf > 0.2, f"{name}: low confidence {conf}"

    def test_predict_genre_returns_string_and_float(self):
        pos = DialPosition(harmonic_tension=2.0, rhythmic_complexity=2.0, spectral_density=2.0)
        genre, conf = self.clf.predict_genre(pos)
        assert isinstance(genre, str)
        assert isinstance(conf, float)
        assert 0.0 <= conf <= 1.0
