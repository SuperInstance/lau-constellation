"""Tests for ASCII visualization functions."""

import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from constraint_toolkit.visualize import (
    ascii_scatter,
    ascii_confusion_matrix,
    ascii_dial_space,
    ascii_bar_chart,
    format_results_table,
    ascii_heatmap,
)
from constraint_toolkit.dials import DialPosition


class TestAsciiScatter:
    def test_returns_string(self):
        x = [1.0, 2.0, 3.0]
        y = [4.0, 5.0, 6.0]
        result = ascii_scatter(x, y)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_empty(self):
        result = ascii_scatter([], [])
        assert "no data" in result

    def test_with_labels(self):
        x = [0.0, 1.0, 2.0]
        y = [0.0, 1.0, 0.5]
        result = ascii_scatter(x, y, labels=["Alpha", "Beta", "Gamma"])
        assert "Alpha" in result
        assert "Beta" in result

    def test_title(self):
        result = ascii_scatter([1, 2], [3, 4], title="Test Plot")
        assert "Test Plot" in result

    def test_single_point(self):
        result = ascii_scatter([1.0], [1.0])
        assert isinstance(result, str)


class TestAsciiConfusionMatrix:
    def test_renders(self):
        cm = np.array([[5, 2], [1, 4]], dtype=np.int64)
        labels = ["A", "B"]
        result = ascii_confusion_matrix(cm, labels)
        assert isinstance(result, str)
        assert "A" in result
        assert "B" in result
        assert "Predicted" in result

    def test_single_class(self):
        cm = np.array([[10]], dtype=np.int64)
        labels = ["Only"]
        result = ascii_confusion_matrix(cm, labels)
        assert "10" in result

    def test_three_classes(self):
        cm = np.array([[3, 1, 0], [0, 4, 1], [1, 0, 5]], dtype=np.int64)
        labels = ["X", "Y", "Z"]
        result = ascii_confusion_matrix(cm, labels)
        assert "X" in result
        assert "Y" in result
        assert "Z" in result


class TestAsciiDialSpace:
    def test_renders(self):
        positions = [
            DialPosition(1.0, 2.0, 3.0),
            DialPosition(4.0, 1.0, 2.0),
            DialPosition(2.5, 3.5, 1.0),
        ]
        traditions = ["TradA", "TradB", "TradC"]
        result = ascii_dial_space(positions, traditions)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_empty(self):
        result = ascii_dial_space([], [])
        assert "no data" in result

    def test_single(self):
        result = ascii_dial_space(
            [DialPosition(2.5, 2.5, 2.5)],
            ["Solo"],
        )
        assert isinstance(result, str)


class TestAsciiBarChart:
    def test_dict_input(self):
        data = {"Alpha": 0.8, "Beta": 0.5, "Gamma": 0.3}
        result = ascii_bar_chart(data)
        assert isinstance(result, str)
        assert "Alpha" in result
        assert "0.800" in result

    def test_list_input(self):
        result = ascii_bar_chart([0.5, 0.3, 0.8], labels=["A", "B", "C"])
        assert isinstance(result, str)

    def test_title(self):
        result = ascii_bar_chart({"X": 1.0}, title="My Chart")
        assert "My Chart" in result

    def test_empty(self):
        result = ascii_bar_chart({})
        assert "no data" in result


class TestFormatResultsTable:
    def test_basic(self):
        results = [
            {"Name": "Test1", "Score": 0.95},
            {"Name": "Test2", "Score": 0.87},
        ]
        output = format_results_table(results, ["Name", "Score"])
        assert "Test1" in output
        assert "Test2" in output

    def test_empty(self):
        output = format_results_table([], ["A", "B"])
        assert "no data" in output


class TestAsciiHeatmap:
    def test_renders(self):
        matrix = np.array([[0.1, 0.5, 0.9], [0.8, 0.3, 0.2]], dtype=np.float64)
        result = ascii_heatmap(matrix, ["Col1", "Col2", "Col3"], ["Row1", "Row2"])
        assert isinstance(result, str)
        assert "Col1" in result
        assert "Row1" in result

    def test_empty(self):
        result = ascii_heatmap(np.array([]).reshape(0, 0), [], [])
        assert "no data" in result
