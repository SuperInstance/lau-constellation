"""
Dataset loading and management for music analysis experiments.

Provides AudioSample/MidiSample dataclasses, filename-based genre labeling,
train/test splitting with genre stratification, cross-validation, and
bootstrapped accuracy estimation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from .dials import DialPosition
from .features import FeatureVector, extract_features
from .audio_utils import load_wav


# Genre keyword mapping for filename inference
_GENRE_KEYWORDS: list[tuple[list[str], str]] = [
    (["blues", "delta"], "Blues"),
    (["gospel"], "Blues"),
    (["jazz", "bebop", "parker", "miles", "solo"], "Jazz"),
    (["techno", "electronic", "edm"], "EDM"),
    (["fugue", "classical", "baroque"], "Classical"),
    (["gamelan"], "Gamelan"),
    (["gagaku"], "Gagaku"),
    (["hindustani", "raga"], "Hindustani"),
    (["african", "polyrhythm"], "African Polyrhythm"),
    (["hiphop", "hip_hop", "rap"], "Hip-hop"),
    (["latin", "salsa"], "Latin"),
]


@dataclass
class AudioSample:
    """A single audio sample with features and metadata.

    Parameters
    ----------
    path : Path
        File path.
    label : str
        Genre/tradition label.
    audio : ndarray
        Audio samples normalized to [-1, 1].
    sr : int
        Sample rate.
    features : dict
        Dict with 'feature_vector' (FeatureVector) and other derived features.
    dial_position : DialPosition
        Computed dial position.
    """

    path: Path
    label: str
    audio: NDArray[np.float64]
    sr: int
    features: dict
    dial_position: DialPosition

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def feature_array(self) -> NDArray[np.float64]:
        fv = self.features.get("feature_vector")
        if fv is None:
            return np.zeros(42, dtype=np.float64)
        return fv.to_array()


@dataclass
class MidiSample:
    """A single MIDI sample with metadata.

    Parameters
    ----------
    path : Path
        File path.
    label : str
        Genre/tradition label.
    dial_position : DialPosition
        Computed dial position from MIDI analysis.
    """

    path: Path
    label: str
    dial_position: DialPosition

    @property
    def name(self) -> str:
        return self.path.name


def label_from_filename(filename: str) -> str:
    """Infer genre label from a filename.

    Uses keyword matching against known genre patterns.
    Returns 'Unknown' if no match found.

    Parameters
    ----------
    filename : str
        Filename (stem or full path).

    Returns
    -------
    str
        Inferred genre label.
    """
    # Get just the stem
    stem = Path(filename).stem.lower()
    # Remove common suffixes
    stem = re.sub(r"[_-](test|improved|user|sample|demo)$", "", stem)
    stem = re.sub(r"[_-]c$|[_-]ab$|[_-]f$|[_-]fsharp$", "", stem, flags=re.IGNORECASE)

    for keywords, label in _GENRE_KEYWORDS:
        for kw in keywords:
            if kw in stem:
                return label

    return "Unknown"


class Dataset:
    """Load and manage music datasets for analysis.

    Supports loading WAV and MIDI files from a directory, inferring labels
    from filenames, stratified splitting, cross-validation, and bootstrapped
    accuracy estimation.
    """

    def __init__(self) -> None:
        self.audio_samples: list[AudioSample] = []
        self.midi_samples: list[MidiSample] = []

    @property
    def size(self) -> int:
        return len(self.audio_samples) + len(self.midi_samples)

    @property
    def labels(self) -> list[str]:
        return [s.label for s in self.audio_samples] + [s.label for s in self.midi_samples]

    @property
    def unique_labels(self) -> list[str]:
        return sorted(set(self.labels))

    @property
    def label_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for lab in self.labels:
            counts[lab] = counts.get(lab, 0) + 1
        return counts

    def load_workspace_wavs(
        self,
        directory: str | Path,
        pattern: str = "*.wav",
        sr: int = 44100,
    ) -> dict[str, AudioSample]:
        """Load all WAV files from a directory.

        Parameters
        ----------
        directory : str or Path
            Directory to search.
        pattern : str
            Glob pattern (default "*.wav").
        sr : int
            Target sample rate.

        Returns
        -------
        dict[str, AudioSample]
            Mapping from filename to AudioSample.
        """
        directory = Path(directory)
        results: dict[str, AudioSample] = {}

        # Import here to avoid circular imports
        from .analyzer import compute_dial_from_features

        for fpath in sorted(directory.glob(pattern)):
            try:
                audio, actual_sr = load_wav(str(fpath), sr=sr)
                label = label_from_filename(fpath.name)
                fv = extract_features(audio, actual_sr)
                dial = compute_dial_from_features(fv)

                sample = AudioSample(
                    path=fpath,
                    label=label,
                    audio=audio,
                    sr=actual_sr,
                    features={"feature_vector": fv},
                    dial_position=dial,
                )
                self.audio_samples.append(sample)
                results[fpath.name] = sample
            except Exception as e:
                # Skip files that fail to load
                print(f"  Warning: Failed to load {fpath.name}: {e}")

        return results

    def load_workspace_mids(
        self,
        directory: str | Path,
        pattern: str = "*.mid",
    ) -> dict[str, MidiSample]:
        """Load all MIDI files from a directory.

        Parameters
        ----------
        directory : str or Path
            Directory to search.
        pattern : str
            Glob pattern (default "*.mid").

        Returns
        -------
        dict[str, MidiSample]
            Mapping from filename to MidiSample.
        """
        from .analyzer import analyze_midi

        directory = Path(directory)
        results: dict[str, MidiSample] = {}

        for fpath in sorted(directory.glob(pattern)):
            try:
                result = analyze_midi(fpath)
                label = label_from_filename(fpath.name)
                sample = MidiSample(
                    path=fpath,
                    label=label,
                    dial_position=result.dial_position,
                )
                self.midi_samples.append(sample)
                results[fpath.name] = sample
            except Exception as e:
                print(f"  Warning: Failed to load {fpath.name}: {e}")

        return results

    def split(
        self,
        ratio: float = 0.8,
        seed: int = 42,
    ) -> tuple["Dataset", "Dataset"]:
        """Split into train/test preserving genre balance (stratified).

        Parameters
        ----------
        ratio : float
            Fraction for training set (default 0.8).
        seed : int
            Random seed.

        Returns
        -------
        train, test : Dataset, Dataset
        """
        rng = np.random.RandomState(seed)
        train = Dataset()
        test = Dataset()

        # Group audio samples by label
        by_label: dict[str, list[AudioSample]] = {}
        for s in self.audio_samples:
            by_label.setdefault(s.label, []).append(s)

        for label, samples in by_label.items():
            indices = list(range(len(samples)))
            rng.shuffle(indices)
            n_train = max(1, int(len(samples) * ratio))

            for i, idx in enumerate(indices):
                if i < n_train:
                    train.audio_samples.append(samples[idx])
                else:
                    test.audio_samples.append(samples[idx])

        # Same for MIDI
        midi_by_label: dict[str, list[MidiSample]] = {}
        for s in self.midi_samples:
            midi_by_label.setdefault(s.label, []).append(s)

        for label, samples in midi_by_label.items():
            indices = list(range(len(samples)))
            rng.shuffle(indices)
            n_train = max(1, int(len(samples) * ratio))

            for i, idx in enumerate(indices):
                if i < n_train:
                    train.midi_samples.append(samples[idx])
                else:
                    test.midi_samples.append(samples[idx])

        return train, test

    def cross_validate(
        self,
        classifier_class: type,
        k: int = 5,
        seed: int = 42,
        **classifier_kwargs,
    ) -> dict:
        """Run k-fold cross-validation on audio samples.

        Parameters
        ----------
        classifier_class : type
            Classifier class (must implement train_from_vectors + predict).
        k : int
            Number of folds.
        seed : int
            Random seed.
        **classifier_kwargs
            Additional kwargs for the classifier constructor.

        Returns
        -------
        dict with 'accuracy', 'per_fold_accuracies', 'per_class_accuracy',
             'mean_confidence', 'predictions'.
        """
        if len(self.audio_samples) < 2:
            return {
                "accuracy": 0.0,
                "per_fold_accuracies": [],
                "per_class_accuracy": {},
                "mean_confidence": 0.0,
                "predictions": [],
            }

        rng = np.random.RandomState(seed)
        n = len(self.audio_samples)
        indices = np.arange(n)
        rng.shuffle(indices)

        # Build stratified folds
        by_label: dict[str, list[int]] = {}
        for idx in indices:
            lab = self.audio_samples[idx].label
            by_label.setdefault(lab, []).append(int(idx))

        # Assign folds
        fold_assignment = np.zeros(n, dtype=int)
        fold_idx = 0
        for label, idx_list in by_label.items():
            for i, idx in enumerate(idx_list):
                fold_assignment[idx] = i % k

        fold_accuracies: list[float] = []
        all_true: list[str] = []
        all_pred: list[str] = []
        all_conf: list[float] = []
        per_class_correct: dict[str, list[bool]] = {}

        for fold in range(k):
            test_mask = fold_assignment == fold
            train_mask = ~test_mask

            train_vecs = [self.audio_samples[i].feature_array for i in range(n) if train_mask[i]]
            train_labs = [self.audio_samples[i].label for i in range(n) if train_mask[i]]
            test_vecs = [self.audio_samples[i].feature_array for i in range(n) if test_mask[i]]
            test_labs = [self.audio_samples[i].label for i in range(n) if test_mask[i]]

            if not train_vecs or not test_vecs:
                continue

            clf = classifier_class(seed=seed, **classifier_kwargs)
            clf.train_from_vectors(train_vecs, train_labs)

            correct = 0
            for vec, true_lab in zip(test_vecs, test_labs):
                pred, conf, _ = clf.predict_from_vector(vec)
                is_correct = pred == true_lab
                per_class_correct.setdefault(true_lab, []).append(is_correct)
                all_true.append(true_lab)
                all_pred.append(pred)
                all_conf.append(conf)
                if is_correct:
                    correct += 1

            fold_accuracies.append(correct / max(len(test_vecs), 1))

        per_class_acc = {}
        for lab, corrects in per_class_correct.items():
            per_class_acc[lab] = float(np.mean(corrects))

        return {
            "accuracy": float(np.mean(fold_accuracies)) if fold_accuracies else 0.0,
            "per_fold_accuracies": fold_accuracies,
            "per_class_accuracy": per_class_acc,
            "mean_confidence": float(np.mean(all_conf)) if all_conf else 0.0,
            "predictions": list(zip(all_true, all_pred)),
        }

    def bootstrapped_accuracy(
        self,
        classifier_class: type,
        n: int = 100,
        seed: int = 42,
        **classifier_kwargs,
    ) -> dict:
        """Bootstrapped accuracy with confidence intervals.

        Parameters
        ----------
        classifier_class : type
            Classifier class.
        n : int
            Number of bootstrap iterations.
        seed : int
            Random seed.
        **classifier_kwargs
            Additional kwargs for the classifier.

        Returns
        -------
        dict with 'mean', 'std', 'ci_lower', 'ci_upper', 'all_scores'.
        """
        if len(self.audio_samples) < 2:
            return {"mean": 0.0, "std": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "all_scores": []}

        rng = np.random.RandomState(seed)
        m = len(self.audio_samples)
        vectors = [s.feature_array for s in self.audio_samples]
        labels = [s.label for s in self.audio_samples]

        scores = np.zeros(n, dtype=np.float64)

        for i in range(n):
            # Bootstrap sample (with replacement)
            idx = rng.randint(0, m, size=m)
            boot_vecs = [vectors[j] for j in idx]
            boot_labs = [labels[j] for j in idx]

            # Out-of-bag samples
            oob_mask = np.ones(m, dtype=bool)
            oob_mask[idx] = False
            oob_indices = np.where(oob_mask)[0]

            if len(oob_indices) == 0:
                # Use all as both train and test (leave-one-out style)
                oob_indices = np.arange(m)

            train_vecs = boot_vecs
            train_labs = boot_labs
            test_vecs = [vectors[j] for j in oob_indices]
            test_labs = [labels[j] for j in oob_indices]

            try:
                clf = classifier_class(seed=seed + i, **classifier_kwargs)
                clf.train_from_vectors(train_vecs, train_labs)
                correct = 0
                for vec, lab in zip(test_vecs, test_labs):
                    pred, _, _ = clf.predict_from_vector(vec)
                    if pred == lab:
                        correct += 1
                scores[i] = correct / max(len(test_vecs), 1)
            except Exception:
                scores[i] = 0.0

        mean_acc = float(np.mean(scores))
        std_acc = float(np.std(scores))
        ci_lower = float(np.percentile(scores, 2.5))
        ci_upper = float(np.percentile(scores, 97.5))

        return {
            "mean": mean_acc,
            "std": std_acc,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "all_scores": scores.tolist(),
        }

    def get_feature_matrix(self) -> tuple[NDArray[np.float64], list[str]]:
        """Get feature matrix and labels for all audio samples.

        Returns
        -------
        X : ndarray of shape (n_samples, 42)
        y : list of str
        """
        if not self.audio_samples:
            return np.zeros((0, 42), dtype=np.float64), []
        X = np.array([s.feature_array for s in self.audio_samples], dtype=np.float64)
        y = [s.label for s in self.audio_samples]
        return X, y

    def get_dial_matrix(self) -> tuple[NDArray[np.float64], list[str]]:
        """Get dial position matrix and labels.

        Returns
        -------
        D : ndarray of shape (n_samples, 3)
        y : list of str
        """
        if not self.audio_samples:
            return np.zeros((0, 3), dtype=np.float64), []
        D = np.array([s.dial_position.to_array() for s in self.audio_samples], dtype=np.float64)
        y = [s.label for s in self.audio_samples]
        return D, y
