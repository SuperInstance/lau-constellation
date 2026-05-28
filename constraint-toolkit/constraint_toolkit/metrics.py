"""
Evaluation metrics for classification and dial-space analysis.

Provides confusion matrices, classification reports, accuracy with
Wilson-score confidence intervals, dial-distance accuracy, Cohen's kappa,
and permutation tests for statistical significance.
"""

from __future__ import annotations

from collections import Counter
from typing import Optional

import numpy as np
from numpy.typing import NDArray


# ---------------------------------------------------------------------------
# Confusion matrix
# ---------------------------------------------------------------------------

def confusion_matrix(
    y_true: list[str],
    y_pred: list[str],
    labels: Optional[list[str]] = None,
) -> tuple[NDArray[np.int64], list[str]]:
    """Compute confusion matrix.

    Parameters
    ----------
    y_true : list of str
        True labels.
    y_pred : list of str
        Predicted labels.
    labels : list of str or None
        Ordered label list. If None, sorted unique labels are used.

    Returns
    -------
    cm : ndarray of shape (n_classes, n_classes)
        Rows = true, columns = predicted.
    labels : list of str
        Label order used.
    """
    if labels is None:
        labels = sorted(set(y_true) | set(y_pred))

    label_to_idx = {l: i for i, l in enumerate(labels)}
    n = len(labels)
    cm = np.zeros((n, n), dtype=np.int64)

    for true, pred in zip(y_true, y_pred):
        ti = label_to_idx.get(true)
        pi = label_to_idx.get(pred)
        if ti is not None and pi is not None:
            cm[ti, pi] += 1

    return cm, labels


# ---------------------------------------------------------------------------
# Classification report
# ---------------------------------------------------------------------------

def classification_report(
    y_true: list[str],
    y_pred: list[str],
    labels: Optional[list[str]] = None,
) -> str:
    """Human-readable classification report with precision/recall/F1.

    Parameters
    ----------
    y_true : list of str
        True labels.
    y_pred : list of str
        Predicted labels.
    labels : list of str or None
        Ordered labels.

    Returns
    -------
    str
        Formatted report.
    """
    if labels is None:
        labels = sorted(set(y_true) | set(y_pred))

    cm, labels = confusion_matrix(y_true, y_pred, labels)
    n = len(labels)

    lines = []
    lines.append(f"{'':>20s} {'precision':>10s} {'recall':>10s} {'f1-score':>10s} {'support':>10s}")
    lines.append("-" * 65)

    total_support = 0
    per_class: list[tuple[str, float, float, float, int]] = []

    for i, label in enumerate(labels):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        support = int(cm[i, :].sum())

        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-10)

        per_class.append((label, precision, recall, f1, support))
        total_support += support

    for label, prec, rec, f1, sup in per_class:
        lines.append(f"{label:>20s} {prec:10.3f} {rec:10.3f} {f1:10.3f} {sup:10d}")

    lines.append("-" * 65)

    # Weighted averages
    all_tp = sum(cm[i, i] for i in range(n))
    accuracy = all_tp / max(len(y_true), 1)

    weighted_prec = sum(p * s for _, p, _, _, s in per_class) / max(total_support, 1)
    weighted_rec = sum(r * s for _, _, r, _, s in per_class) / max(total_support, 1)
    weighted_f1 = sum(f * s for _, _, _, f, s in per_class) / max(total_support, 1)

    lines.append(f"{'accuracy':>20s} {'':>10s} {'':>10s} {accuracy:10.3f} {total_support:10d}")
    lines.append(f"{'weighted avg':>20s} {weighted_prec:10.3f} {weighted_rec:10.3f} {weighted_f1:10.3f} {total_support:10d}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Accuracy with Wilson score CI
# ---------------------------------------------------------------------------

def accuracy_with_ci(
    y_true: list[str],
    y_pred: list[str],
    confidence: float = 0.95,
) -> tuple[float, float, float]:
    """Accuracy with Wilson score confidence interval.

    Parameters
    ----------
    y_true : list of str
        True labels.
    y_pred : list of str
        Predicted labels.
    confidence : float
        Confidence level (default 0.95).

    Returns
    -------
    accuracy, ci_lower, ci_upper : float, float, float
    """
    n = len(y_true)
    if n == 0:
        return 0.0, 0.0, 0.0

    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    p_hat = correct / n

    # Wilson score interval
    from scipy.stats import norm
    z = norm.ppf(1 - (1 - confidence) / 2)

    denom = 1 + z ** 2 / n
    center = (p_hat + z ** 2 / (2 * n)) / denom
    spread = z * np.sqrt(p_hat * (1 - p_hat) / n + z ** 2 / (4 * n ** 2)) / denom

    ci_lower = max(0.0, center - spread)
    ci_upper = min(1.0, center + spread)

    return float(p_hat), float(ci_lower), float(ci_upper)


# ---------------------------------------------------------------------------
# Dial distance accuracy
# ---------------------------------------------------------------------------

def dial_distance_accuracy(
    y_true_dials: list,
    y_pred_dials: list,
    threshold: float = 1.0,
) -> float:
    """Accuracy within threshold distance in dial space.

    Parameters
    ----------
    y_true_dials : list of DialPosition
        True dial positions.
    y_pred_dials : list of DialPosition
        Predicted dial positions.
    threshold : float
        Maximum Euclidean distance to count as correct.

    Returns
    -------
    float
        Fraction of predictions within threshold.
    """
    if not y_true_dials:
        return 0.0

    correct = 0
    for true_d, pred_d in zip(y_true_dials, y_pred_dials):
        dist = float(np.linalg.norm(true_d.to_array() - pred_d.to_array()))
        if dist <= threshold:
            correct += 1

    return correct / len(y_true_dials)


# ---------------------------------------------------------------------------
# Cohen's Kappa
# ---------------------------------------------------------------------------

def pairwise_agreement(
    predictions_a: list[str],
    predictions_b: list[str],
) -> float:
    """Cohen's kappa between two sets of predictions.

    Parameters
    ----------
    predictions_a : list of str
        First set of predictions.
    predictions_b : list of str
        Second set of predictions.

    Returns
    -------
    float
        Cohen's kappa coefficient.
    """
    if not predictions_a or len(predictions_a) != len(predictions_b):
        return 0.0

    labels = sorted(set(predictions_a) | set(predictions_b))
    label_to_idx = {l: i for i, l in enumerate(labels)}
    n_labels = len(labels)
    n = len(predictions_a)

    # Agreement
    observed = sum(1 for a, b in zip(predictions_a, predictions_b) if a == b)
    p_observed = observed / n

    # Expected agreement
    counts_a = Counter(predictions_a)
    counts_b = Counter(predictions_b)
    p_expected = sum(
        (counts_a.get(l, 0) / n) * (counts_b.get(l, 0) / n)
        for l in labels
    )

    if p_expected >= 1.0:
        return 1.0

    kappa = (p_observed - p_expected) / (1.0 - p_expected)
    return float(kappa)


# ---------------------------------------------------------------------------
# Permutation test
# ---------------------------------------------------------------------------

def permutation_test(
    scores_a: list[float] | NDArray[np.float64],
    scores_b: list[float] | NDArray[np.float64],
    n_permutations: int = 10000,
    seed: int = 42,
) -> dict:
    """Permutation test for significance of score difference.

    Tests H0: scores_a and scores_b come from the same distribution.

    Parameters
    ----------
    scores_a : array-like
        Scores from system A (e.g., per-fold accuracies).
    scores_b : array-like
        Scores from system B.
    n_permutations : int
        Number of permutations.
    seed : int
        Random seed.

    Returns
    -------
    dict with 'p_value', 'observed_diff', 'significant_0.05', 'significant_0.01'.
    """
    scores_a = np.asarray(scores_a, dtype=np.float64)
    scores_b = np.asarray(scores_b, dtype=np.float64)

    observed_diff = float(np.mean(scores_a) - np.mean(scores_b))

    combined = np.concatenate([scores_a, scores_b])
    n_a = len(scores_a)
    n_total = len(combined)

    rng = np.random.RandomState(seed)
    count_extreme = 0

    for _ in range(n_permutations):
        perm = rng.permutation(n_total)
        perm_a = combined[perm[:n_a]]
        perm_b = combined[perm[n_a:]]
        perm_diff = float(np.mean(perm_a) - np.mean(perm_b))
        if abs(perm_diff) >= abs(observed_diff):
            count_extreme += 1

    p_value = count_extreme / n_permutations

    return {
        "p_value": float(p_value),
        "observed_diff": observed_diff,
        "significant_0.05": p_value < 0.05,
        "significant_0.01": p_value < 0.01,
    }
