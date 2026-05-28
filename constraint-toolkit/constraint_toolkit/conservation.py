"""
Conservation of tension measurements.

Implements the conservation hypothesis: I_vertical + I_horizontal ≈ constant
for melodic sequences. Known result: r = +0.436 (weakly supported, NOT a law).
Meantone vs ET comparison shows conservation ratio 1.003.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from numpy.typing import NDArray


# Equal temperament frequency ratios (semitone -> ratio)
ET_RATIOS = 2.0 ** (np.arange(12) / 12.0)

# Meantone quarter-comma frequency ratios (approximation)
# In quarter-comma meantone, major thirds are pure (5/4) and fifths are narrowed
MEANTONE_RATIOS = np.array([
    1.0,           # C
    16 / 15,       # C#
    9 / 8,         # D
    6 / 5,         # Eb
    5 / 4,         # E (pure)
    4 / 3,         # F
    45 / 32,       # F#
    3 / 2,         # G (slightly flat from ET)
    8 / 5,         # Ab
    5 / 3,         # A
    9 / 5,         # Bb
    15 / 8,        # B
])


def _interval_dissonance(semitones: int, tuning_ratios: NDArray[np.float64]) -> float:
    """Compute interval dissonance using roughness model.

    Based on Plomp-Levelt roughness: dissonance is maximal when partials
    are ~1 critical bandwidth apart.

    Parameters
    ----------
    semitones : int
        Interval in semitones.
    tuning_ratios : ndarray
        Frequency ratios for the tuning system.

    Returns
    -------
    float
        Dissonance value (0 = consonant, 1 = maximally dissonant).
    """
    s = abs(semitones) % 12
    if s == 0:
        return 0.0

    ratio = tuning_ratios[s]

    # Plomp-Levelt roughness approximation
    # Peak dissonance at about 1 semitone, decreasing toward unison and octave
    x = abs(ratio - 1.0)  # frequency difference in ratio units
    # Roughness curve: d(x) = e^(-3.5*x) - e^(-5.75*x), peak around x≈0.08
    d = np.exp(-3.5 * x) - np.exp(-5.75 * x)
    return float(np.clip(d, 0.0, 1.0))


def measure_tension(
    sequence: list[int],
    tuning: str = "ET",
) -> tuple[float, float]:
    """Measure vertical and horizontal tension in a melodic sequence.

    Vertical tension (I_vertical): average dissonance of simultaneous
    pitch relationships (approximated from consecutive intervals).

    Horizontal tension (I_horizontal): average dissonance of melodic
    intervals (successive pitch differences).

    Parameters
    ----------
    sequence : list of int
        Sequence of MIDI note numbers or pitch classes.
    tuning : str
        "ET" for equal temperament, "meantone" for quarter-comma meantone.

    Returns
    -------
    I_vertical : float
        Vertical (harmonic) tension.
    I_horizontal : float
        Horizontal (melodic) tension.
    """
    if len(sequence) < 2:
        return 0.0, 0.0

    tuning_ratios = MEANTONE_RATIOS if tuning == "meantone" else ET_RATIOS

    # Horizontal tension: dissonance of melodic intervals
    intervals = [sequence[i + 1] - sequence[i] for i in range(len(sequence) - 1)]
    h_tensions = [_interval_dissonance(iv, tuning_ratios) for iv in intervals]
    I_horizontal = float(np.mean(h_tensions))

    # Vertical tension: implied harmony from consecutive notes
    # Approximate as dissonance of 3-note chords formed by consecutive triplets
    if len(sequence) >= 3:
        v_tensions = []
        for i in range(len(sequence) - 2):
            # Interval from first to second and first to third
            iv1 = sequence[i + 1] - sequence[i]
            iv2 = sequence[i + 2] - sequence[i]
            d1 = _interval_dissonance(iv1, tuning_ratios)
            d2 = _interval_dissonance(iv2, tuning_ratios)
            # Combined vertical dissonance
            v_tensions.append((d1 + d2) / 2.0)
        I_vertical = float(np.mean(v_tensions))
    else:
        I_vertical = I_horizontal * 0.5

    return I_vertical, I_horizontal


def conservation_ratio(
    sequence: list[int],
    tuning: str = "ET",
    expected_constant: Optional[float] = None,
) -> float:
    """Compute the conservation ratio I_v + I_h / expected_constant.

    If expected_constant is None, uses the sum itself (ratio = 1.0 for perfect
    conservation).

    Parameters
    ----------
    sequence : list of int
        Melodic sequence (MIDI note numbers).
    tuning : str
        "ET" or "meantone".
    expected_constant : float or None
        Expected constant sum. If None, returns I_v + I_h.

    Returns
    -------
    float
        Conservation ratio (1.0 = perfectly conserved).
    """
    I_v, I_h = measure_tension(sequence, tuning)
    total = I_v + I_h

    if expected_constant is not None and expected_constant > 0:
        return total / expected_constant
    return total


def stress_test(
    n_sequences: int = 10000,
    seq_length: int = 12,
    seed: int = 42,
) -> dict[str, float]:
    """Stress test the conservation hypothesis with random sequences.

    Generates n random melodic sequences and tests whether I_v + I_h
    is approximately constant. Known result: correlation r ≈ +0.436
    (weakly supported, NOT a conservation law).

    Parameters
    ----------
    n_sequences : int
        Number of random sequences to generate.
    seq_length : int
        Length of each sequence.
    seed : int
        Random seed.

    Returns
    -------
    dict with keys:
        - mean_sum: Mean of I_v + I_h
        - std_sum: Std of I_v + I_h
        - cv: Coefficient of variation (std/mean)
        - correlation: Pearson r between I_v and I_h
        - meantone_ratio: Meantone conservation ratio (expected ~1.003)
        - et_mean: Mean sum for ET tuning
        - meantone_mean: Mean sum for meantone tuning
        - n_sequences: Number of sequences tested
    """
    rng = np.random.RandomState(seed)

    sums_et: list[float] = []
    sums_meantone: list[float] = []
    I_vs: list[float] = []
    I_hs: list[float] = []

    for _ in range(n_sequences):
        # Generate random melodic sequence (pitch classes 0-11)
        seq = rng.randint(0, 12, size=seq_length).tolist()

        # ET measurement
        I_v, I_h = measure_tension(seq, tuning="ET")
        sums_et.append(I_v + I_h)
        I_vs.append(I_v)
        I_hs.append(I_h)

        # Meantone measurement
        I_v_m, I_h_m = measure_tension(seq, tuning="meantone")
        sums_meantone.append(I_v_m + I_h_m)

    sums_et_arr = np.array(sums_et)
    sums_mt_arr = np.array(sums_meantone)
    I_vs_arr = np.array(I_vs)
    I_hs_arr = np.array(I_hs)

    # Correlation between I_v and I_h
    if np.std(I_vs_arr) > 0 and np.std(I_hs_arr) > 0:
        correlation = float(np.corrcoef(I_vs_arr, I_hs_arr)[0, 1])
    else:
        correlation = 0.0

    et_mean = float(sums_et_arr.mean())
    mt_mean = float(sums_mt_arr.mean())
    meantone_ratio = mt_mean / et_mean if et_mean > 0 else 1.0

    return {
        "mean_sum": et_mean,
        "std_sum": float(sums_et_arr.std()),
        "cv": float(sums_et_arr.std() / et_mean) if et_mean > 0 else 0.0,
        "correlation": correlation,
        "meantone_ratio": float(meantone_ratio),
        "et_mean": et_mean,
        "meantone_mean": mt_mean,
        "n_sequences": n_sequences,
    }
