"""Tests for the benchmark suite."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from constraint_toolkit.benchmarks import BenchmarkReport, BenchmarkResult, BenchmarkSuite


class TestBenchmarkSuite:
    """Test the BenchmarkSuite class."""

    def test_benchmark_suite_runs_all(self) -> None:
        """All benchmarks run without error and return a report."""
        suite = BenchmarkSuite()
        report = suite.run_all()
        assert isinstance(report, BenchmarkReport)
        assert len(report.results) == 6

    def test_dial_distances_returns_correlation(self) -> None:
        """Dial distance benchmark returns a valid correlation."""
        suite = BenchmarkSuite()
        result = suite.benchmark_dial_distances()
        assert isinstance(result, BenchmarkResult)
        assert -1.0 <= result.metric <= 1.0
        assert "actual_correlation" in result.details or "correlation" in result.details

    def test_tradition_recognition_above_chance(self) -> None:
        """Tradition recognition should be well above chance (10%)."""
        suite = BenchmarkSuite()
        result = suite.benchmark_tradition_recognition()
        assert isinstance(result, BenchmarkResult)
        # Should be well above chance (10% for 10 traditions)
        assert result.metric > 0.50

    def test_benchmark_report_has_all_sections(self) -> None:
        """Report includes all expected benchmark sections."""
        suite = BenchmarkSuite()
        report = suite.run_all()
        names = {r.name for r in report.results}
        assert "V_K/H Onset Correlation" in names
        assert "Tradition Recognition" in names
        assert "Conservation CV/r" in names
        assert "Unexplored Fraction" in names
        assert "I_vert/I_spectral JND" in names
        assert "Gagaku Most Pleasing" in names

    def test_benchmark_result_status(self) -> None:
        """BenchmarkResult status property returns correct strings."""
        passed = BenchmarkResult(
            name="test", expected="x", actual="y",
            passed=True, marginal=False, metric=1.0, tolerance=0.1,
        )
        assert passed.status == "✓ PASS"

        marginal = BenchmarkResult(
            name="test", expected="x", actual="y",
            passed=False, marginal=True, metric=1.0, tolerance=0.1,
        )
        assert marginal.status == "~ MARG"

        failed = BenchmarkResult(
            name="test", expected="x", actual="y",
            passed=False, marginal=False, metric=1.0, tolerance=0.1,
        )
        assert failed.status == "✗ FAIL"

    def test_benchmark_report_serialization(self) -> None:
        """Report serializes to JSON-compatible dict."""
        suite = BenchmarkSuite()
        report = suite.run_all()
        d = report.to_dict()
        assert "results" in d
        assert "total_time" in d
        # Ensure JSON-serializable
        json.dumps(d)

    def test_benchmark_report_counts(self) -> None:
        """Report pass/marginal/fail counts are consistent."""
        suite = BenchmarkSuite()
        report = suite.run_all()
        total = report.n_pass + report.n_marginal + report.n_fail
        assert total == len(report.results)

    def test_format_report(self) -> None:
        """Report formatting produces a non-empty string."""
        suite = BenchmarkSuite()
        report = suite.run_all()
        text = report.format_report()
        assert "BENCHMARK RESULTS" in text
        assert len(text) > 100
