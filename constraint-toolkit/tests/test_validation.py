"""Tests for the validation module."""

from __future__ import annotations

import pytest

from constraint_toolkit.validation import (
    validate_vk_h_correlation,
    validate_conservation,
    validate_meantone_et_ratio,
    validate_tradition_recognition,
    validate_unexplored_fraction,
    validate_jnd_ratio,
    validate_pleasing_peak,
    run_all_validations,
    ValidationResult,
    ValidationReport,
)


class TestVKHCorrelation:
    def test_returns_result(self):
        result = validate_vk_h_correlation()
        assert isinstance(result, ValidationResult)
        assert result.name == "V_K/H_onset correlation"
        assert bool(result.passed) is not None  # accepts numpy.bool_ too
        assert bool(result.marginal) is not None
        assert "pearson_r" in result.details
        assert isinstance(result.details["pearson_r"], float)

    def test_correlation_is_computed(self):
        result = validate_vk_h_correlation()
        # Pearson r should be a valid float in [-1, 1]
        assert -1.0 <= result.details["pearson_r"] <= 1.0


class TestConservation:
    def test_returns_result(self):
        result = validate_conservation(n=500, seed=42)
        assert isinstance(result, ValidationResult)
        assert result.name == "Conservation hypothesis"
        assert "correlation" in result.details
        assert "cv" in result.details
        assert isinstance(result.details["correlation"], float)
        assert isinstance(result.details["cv"], float)

    def test_has_length_breakdown(self):
        result = validate_conservation(n=500, seed=42)
        assert "by_length" in result.details
        by_length = result.details["by_length"]
        for length_str in ["4", "8", "16", "32"]:
            assert length_str in by_length
            assert "correlation" in by_length[length_str]


class TestMeantoneETRatio:
    def test_returns_result(self):
        result = validate_meantone_et_ratio(n=200, seed=42)
        assert isinstance(result, ValidationResult)
        assert result.name == "Meantone/ET ratio"
        assert "mean_ratio" in result.details
        assert "ci_low" in result.details
        assert "ci_high" in result.details
        assert result.details["ci_low"] < result.details["ci_high"]


class TestTraditionRecognition:
    def test_returns_result(self):
        result = validate_tradition_recognition(n_samples=50, seed=42)
        assert isinstance(result, ValidationResult)
        assert result.name == "Tradition recognition"
        assert "overall_rate" in result.details
        assert "per_tradition" in result.details

    def test_above_50(self):
        result = validate_tradition_recognition(n_samples=50, seed=42)
        # With 10 traditions, recognition should be well above chance (10%)
        assert result.details["overall_rate"] > 0.50


class TestUnexploredFraction:
    def test_returns_result(self):
        result = validate_unexplored_fraction(n=5000, seed=42)
        assert isinstance(result, ValidationResult)
        assert result.name == "Unexplored fraction"
        assert "fraction" in result.details
        assert 0 <= result.details["fraction"] <= 1

    def test_has_threshold_curve(self):
        result = validate_unexplored_fraction(n=5000, seed=42)
        assert "threshold_curve" in result.details
        # Fraction unexplored should decrease as threshold increases
        fractions = [result.details["threshold_curve"][t]["fraction"] for t in ["1.0", "1.5", "2.0", "2.5"]]
        for i in range(len(fractions) - 1):
            assert fractions[i] >= fractions[i + 1]


class TestJNDRatio:
    def test_returns_result(self):
        result = validate_jnd_ratio(n=200, seed=42)
        assert isinstance(result, ValidationResult)
        assert result.name == "JND ratio (I_vert vs I_spectral)"
        assert "jnd_ratio" in result.details
        assert result.details["jnd_ratio"] > 0


class TestPleasingPeak:
    def test_returns_result(self):
        result = validate_pleasing_peak(n_grid=20)
        assert isinstance(result, ValidationResult)
        assert result.name == "Most pleasing point"
        assert "found_point" in result.details
        assert "distance" in result.details
        assert result.details["distance"] >= 0


class TestRunAll:
    def test_run_all_returns_report(self):
        report = run_all_validations()
        assert isinstance(report, ValidationReport)
        assert len(report.results) == 7
        assert report.n_pass + report.n_marginal + report.n_fail == 7
        assert isinstance(report.summary, str)

    def test_all_results_have_details(self):
        report = run_all_validations()
        for result in report.results:
            assert isinstance(result.details, dict), f"{result.name} missing details"
            assert len(result.details) > 0, f"{result.name} has empty details"
