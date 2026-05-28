"""Tests for the metrics module."""

from __future__ import annotations

import numpy as np
import pytest

from constraint_toolkit.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_with_ci,
    permutation_test,
    pairwise_agreement,
)


class TestConfusionMatrix:
    def test_shape(self):
        y_true = ["A", "B", "A", "B", "A"]
        y_pred = ["A", "A", "A", "B", "B"]
        cm, labels = confusion_matrix(y_true, y_pred)
        assert cm.shape == (2, 2)
        assert set(labels) == {"A", "B"}

    def test_perfect_predictions(self):
        y_true = ["A", "B", "C", "A", "B", "C"]
        y_pred = ["A", "B", "C", "A", "B", "C"]
        cm, labels = confusion_matrix(y_true, y_pred)
        # Diagonal should have all counts
        for i in range(len(labels)):
            assert cm[i, i] > 0

    def test_custom_labels(self):
        y_true = ["A", "B"]
        y_pred = ["A", "B"]
        cm, labels = confusion_matrix(y_true, y_pred, labels=["B", "A"])
        assert labels == ["B", "A"]
        assert cm.shape == (2, 2)


class TestClassificationReport:
    def test_contains_metrics(self):
        y_true = ["A", "B", "A", "B", "A"]
        y_pred = ["A", "A", "A", "B", "B"]
        report = classification_report(y_true, y_pred)
        assert "precision" in report
        assert "recall" in report
        assert "f1-score" in report

    def test_perfect_report(self):
        y_true = ["A", "B", "C"]
        y_pred = ["A", "B", "C"]
        report = classification_report(y_true, y_pred)
        assert "1.000" in report


class TestAccuracyWithCI:
    def test_returns_tuple(self):
        y_true = ["A", "B", "A", "B"]
        y_pred = ["A", "B", "A", "B"]
        acc, lower, upper = accuracy_with_ci(y_true, y_pred)
        assert isinstance(acc, float)
        assert isinstance(lower, float)
        assert isinstance(upper, float)

    def test_ci_bounds(self):
        # Imperfect predictions for meaningful CI
        y_true = ["A"] * 50 + ["B"] * 50
        y_pred = ["A"] * 45 + ["B"] * 5 + ["A"] * 10 + ["B"] * 40
        acc, lower, upper = accuracy_with_ci(y_true, y_pred)
        assert lower <= acc <= upper

    def test_perfect_accuracy(self):
        y_true = ["A", "B", "C", "A"]
        y_pred = ["A", "B", "C", "A"]
        acc, lower, upper = accuracy_with_ci(y_true, y_pred)
        assert acc == 1.0


class TestPermutationTest:
    def test_returns_dict(self):
        a = [0.8, 0.85, 0.82, 0.79, 0.81]
        b = [0.75, 0.72, 0.78, 0.70, 0.74]
        result = permutation_test(a, b, n_permutations=1000)
        assert "p_value" in result
        assert "observed_diff" in result
        assert isinstance(result["p_value"], float)

    def test_same_distribution_high_p(self):
        rng = np.random.RandomState(42)
        a = rng.normal(0.8, 0.05, 20).tolist()
        b = rng.normal(0.8, 0.05, 20).tolist()
        result = permutation_test(a, b, n_permutations=1000)
        assert result["p_value"] > 0.05


class TestPairwiseAgreement:
    def test_perfect_agreement(self):
        a = ["A", "B", "C", "A", "B"]
        b = ["A", "B", "C", "A", "B"]
        kappa = pairwise_agreement(a, b)
        assert kappa == 1.0

    def test_no_agreement(self):
        a = ["A", "A", "A", "A"]
        b = ["B", "B", "B", "B"]
        kappa = pairwise_agreement(a, b)
        assert kappa == 0.0
