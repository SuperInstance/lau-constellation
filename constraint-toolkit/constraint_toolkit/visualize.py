"""
Terminal-friendly ASCII visualizations for experiment results.

Provides scatter plots, confusion matrices, dial-space projections,
bar charts, tables, and heatmaps — all rendered as plain text.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from numpy.typing import NDArray


def ascii_scatter(
    x: NDArray[np.float64] | list[float],
    y: NDArray[np.float64] | list[float],
    labels: Optional[list[str]] = None,
    width: int = 80,
    height: int = 20,
    title: str = "",
) -> str:
    """ASCII art scatter plot.

    Parameters
    ----------
    x, y : array-like
        Data coordinates.
    labels : list of str or None
        Point labels (first char used).
    width, height : int
        Canvas dimensions.
    title : str
        Plot title.

    Returns
    -------
    str
        ASCII art scatter plot.
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)

    if len(x) == 0:
        return "(no data)"

    # Normalize to canvas
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    if x_max - x_min < 1e-10:
        x_min -= 0.5
        x_max += 0.5
    if y_max - y_min < 1e-10:
        y_min -= 0.5
        y_max += 0.5

    x_norm = (x - x_min) / (x_max - x_min)
    y_norm = (y - y_min) / (y_max - y_min)

    # Map to canvas coordinates (y inverted)
    cx = np.clip((x_norm * (width - 3)).astype(int), 0, width - 1)
    cy = np.clip(((1 - y_norm) * (height - 1)).astype(int), 0, height - 1)

    # Create canvas
    canvas = [[" " for _ in range(width)] for _ in range(height)]

    # Plot points
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*#+@&%$"
    for i in range(len(x)):
        char = chars[i % len(chars)]
        if labels and i < len(labels):
            char = labels[i][0].upper()
        canvas[cy[i]][cx[i]] = char

    # Build output
    lines = []
    if title:
        lines.append(title.center(width))
        lines.append("")

    # Y-axis label
    lines.append(f"{y_max:.2f} ┌{'─' * (width - 3)}┐")
    for row in range(height - 1):
        line = f"{'':>6s} │{''.join(canvas[row])}│"
        lines.append(line)
    lines.append(f"{y_min:.2f} └{'─' * (width - 3)}┘")
    lines.append(f"       {x_min:.2f}{' ' * (width - 16)}{x_max:.2f}")

    # Legend
    if labels:
        legend_items = []
        for i in range(min(len(labels), 12)):
            char = labels[i][0].upper()
            legend_items.append(f"{char}={labels[i]}")
        if len(labels) > 12:
            legend_items.append(f"... +{len(labels) - 12} more")
        legend_line = "  ".join(legend_items)
        # Wrap if too long
        while len(legend_line) > width:
            cut = legend_line[:width].rfind("  ")
            if cut < 10:
                break
            lines.append(legend_line[:cut])
            legend_line = "  " + legend_line[cut:].strip()
        lines.append(legend_line)

    return "\n".join(lines)


def ascii_confusion_matrix(
    cm: NDArray[np.int64],
    labels: list[str],
    title: str = "Confusion Matrix",
) -> str:
    """Pretty-print confusion matrix.

    Parameters
    ----------
    cm : ndarray of shape (n, n)
        Confusion matrix (rows=true, cols=predicted).
    labels : list of str
        Class labels.
    title : str
        Title.

    Returns
    -------
    str
        Formatted confusion matrix.
    """
    n = len(labels)
    max_label = max(len(l) for l in labels) if labels else 5
    max_val = int(cm.max()) if cm.size > 0 else 0
    cell_w = max(max_label, len(str(max_val)), 4) + 2

    lines = [title]
    lines.append("")

    # Header
    header = " " * (max_label + 3) + "Predicted"
    lines.append(header)
    header2 = " " * (max_label + 3)
    for label in labels:
        header2 += f"{label:>{cell_w}s}"
    lines.append(header2)
    lines.append(" " * (max_label + 3) + "─" * (cell_w * n))

    # Rows
    for i, label in enumerate(labels):
        row_str = f"{'True':>4s} {label:>{max_label}s} │"
        for j in range(n):
            val = int(cm[i, j])
            row_str += f"{val:>{cell_w}d}"
        lines.append(row_str)

    return "\n".join(lines)


def ascii_dial_space(
    positions: list,
    traditions: list[str],
    width: int = 80,
    height: int = 40,
    title: str = "Dial Space Projection (H × R)",
) -> str:
    """ASCII art 2D projection of dial space.

    Projects 3D dial positions onto harmonic_tension × rhythmic_complexity plane.

    Parameters
    ----------
    positions : list of DialPosition
        Positions to plot.
    traditions : list of str
        Tradition labels.
    width, height : int
        Canvas dimensions.
    title : str
        Title.

    Returns
    -------
    str
        ASCII art scatter plot.
    """
    if not positions:
        return "(no data)"

    h_vals = [p.harmonic_tension for p in positions]
    r_vals = [p.rhythmic_complexity for p in positions]

    return ascii_scatter(
        h_vals, r_vals,
        labels=traditions,
        width=width,
        height=height,
        title=title,
    )


def ascii_bar_chart(
    data: dict[str, float] | list[float],
    labels: Optional[list[str]] = None,
    width: int = 60,
    title: str = "",
) -> str:
    """ASCII art horizontal bar chart.

    Parameters
    ----------
    data : dict or list
        Data values. If dict, keys are labels.
    labels : list of str or None
        Labels (required if data is a list).
    width : int
        Maximum bar width in characters.
    title : str
        Chart title.

    Returns
    -------
    str
        ASCII bar chart.
    """
    if isinstance(data, dict):
        labels = list(data.keys())
        values = list(data.values())
    else:
        values = list(data)
        if labels is None:
            labels = [str(i) for i in range(len(values))]

    if not values:
        return "(no data)"

    max_val = max(abs(v) for v in values) if values else 1.0
    if max_val < 1e-10:
        max_val = 1.0

    max_label_len = max(len(l) for l in labels) if labels else 5
    bar_width = width - max_label_len - 10

    lines = []
    if title:
        lines.append(title)
        lines.append("")

    for label, val in zip(labels, values):
        bar_len = int(abs(val) / max_val * bar_width)
        bar = "█" * bar_len
        sign = "+" if val >= 0 else "-"
        lines.append(f"{label:>{max_label_len}s} │{bar:<{bar_width}s}│ {sign}{abs(val):.3f}")

    return "\n".join(lines)


def format_results_table(
    results: list[dict],
    columns: list[str],
    title: str = "",
) -> str:
    """Pretty-print results as aligned table.

    Parameters
    ----------
    results : list of dict
        Each dict is a row.
    columns : list of str
        Column keys (and headers).
    title : str
        Table title.

    Returns
    -------
    str
        Formatted table.
    """
    if not results:
        return "(no data)"

    # Compute column widths
    widths: dict[str, int] = {}
    for col in columns:
        widths[col] = len(col)
        for row in results:
            val = row.get(col, "")
            if isinstance(val, float):
                val_str = f"{val:.4f}"
            else:
                val_str = str(val)
            widths[col] = max(widths[col], len(val_str))

    lines = []
    if title:
        total_w = sum(widths.values()) + 3 * (len(columns) - 1)
        lines.append(title.center(total_w))
        lines.append("")

    # Header
    header = " | ".join(f"{col:>{widths[col]}s}" for col in columns)
    lines.append(header)
    lines.append("-+-".join("-" * widths[col] for col in columns))

    # Rows
    for row in results:
        cells = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                val_str = f"{val:.4f}"
            elif isinstance(val, bool):
                val_str = "Yes" if val else "No"
            else:
                val_str = str(val)
            cells.append(f"{val_str:>{widths[col]}s}")
        lines.append(" | ".join(cells))

    return "\n".join(lines)


def ascii_heatmap(
    matrix: NDArray[np.float64],
    x_labels: list[str],
    y_labels: list[str],
    width: int = 60,
    height: int = 20,
    title: str = "",
) -> str:
    """ASCII art heatmap.

    Parameters
    ----------
    matrix : ndarray of shape (n_y, n_x)
        Data matrix.
    x_labels : list of str
        Column labels.
    y_labels : list of str
        Row labels.
    width, height : int
        Approximate canvas size.
    title : str
        Title.

    Returns
    -------
    str
        ASCII heatmap.
    """
    matrix = np.asarray(matrix, dtype=np.float64)
    if matrix.size == 0:
        return "(no data)"

    n_y, n_x = matrix.shape

    # Characters for intensity (dark to light)
    chars = " .:-=+*#%@"

    # Normalize
    vmin = matrix.min()
    vmax = matrix.max()
    if vmax - vmin < 1e-10:
        normalized = np.zeros_like(matrix)
    else:
        normalized = (matrix - vmin) / (vmax - vmin)

    max_y_label = max(len(l) for l in y_labels) if y_labels else 5

    lines = []
    if title:
        lines.append(title)
        lines.append("")

    # Column headers (rotated would be complex, just print short labels)
    header = " " * (max_y_label + 3)
    for j in range(n_x):
        label = x_labels[j][:6] if j < len(x_labels) else str(j)
        header += f"{label:>7s}"
    lines.append(header)
    lines.append(" " * (max_y_label + 3) + "─" * (n_x * 7))

    # Rows
    for i in range(n_y):
        label = y_labels[i] if i < len(y_labels) else str(i)
        row_str = f"{label:>{max_y_label}s} │"
        for j in range(n_x):
            val = normalized[i, j]
            idx = int(val * (len(chars) - 1))
            idx = max(0, min(idx, len(chars) - 1))
            row_str += f"  {chars[idx]}{matrix[i, j]:5.2f}"
        lines.append(row_str)

    # Scale bar
    lines.append("")
    scale = "Scale: "
    for c in chars:
        scale += c
    scale += f"  [{vmin:.2f} - {vmax:.2f}]"
    lines.append(scale)

    return "\n".join(lines)
