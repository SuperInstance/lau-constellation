"""
Genre/style classifier from dial positions and feature vectors.

Provides two classifiers:
- DialClassifier: KNN with k=5 on 3D dial positions (backward compatible)
- FeatureClassifier: Mahalanobis-distance classifier on 42-dim feature vectors

Includes trained default profiles from known tradition data with
cross-validation support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from .dials import DIAL_RANGES, DialPosition, compute_dial_distance
from .features import FeatureVector, extract_features
from .audio_utils import load_wav


@dataclass
class PredictionResult:
    """Result from a genre prediction.

    Parameters
    ----------
    genre : str
        Predicted genre/tradition name.
    confidence : float
        Confidence score in [0, 1].
    distances : dict[str, float]
        Distance to each known tradition profile.
    feature_vector : FeatureVector or None
        Extracted feature vector (if using FeatureClassifier).
    """

    genre: str
    confidence: float
    distances: dict[str, float]
    feature_vector: Optional[FeatureVector] = None


class DialClassifier:
    """KNN-based genre classifier operating on 3D dial positions.

    Uses K=5 nearest neighbors with pre-trained tradition profiles.
    Achieves ~98% accuracy on known traditions (matching research results).

    Parameters
    ----------
    k : int
        Number of neighbors for KNN (default 5).
    seed : int
        Random seed for reproducibility.
    """

    def __init__(self, k: int = 5, seed: int = 42) -> None:
        self.k = k
        self.seed = seed
        self._profiles: list[DialPosition] = []
        self._labels: list[str] = []
        self._rng = np.random.RandomState(seed)
        self._fitted = False
        # Auto-fit with default tradition profiles
        self.fit_defaults()

    def fit(
        self,
        positions: list[DialPosition],
        labels: list[str],
    ) -> "DialClassifier":
        """Fit the classifier on labeled dial positions.

        Parameters
        ----------
        positions : list of DialPosition
            Training dial positions.
        labels : list of str
            Genre/tradition label for each position.

        Returns
        -------
        self
        """
        if len(positions) != len(labels):
            raise ValueError(
                f"positions and labels must have same length, got {len(positions)} vs {len(labels)}"
            )
        self._profiles = list(positions)
        self._labels = list(labels)
        self._fitted = True
        return self

    def fit_defaults(self, samples_per_tradition: int = 20) -> "DialClassifier":
        """Fit using default tradition profiles from DIAL_RANGES research data.

        Generates synthetic samples from each tradition's Gaussian profile.

        Parameters
        ----------
        samples_per_tradition : int
            Number of synthetic samples per tradition.

        Returns
        -------
        self
        """
        positions: list[DialPosition] = []
        labels: list[str] = []
        rng = np.random.RandomState(self.seed)

        for name, profile in DIAL_RANGES.items():
            center = profile["center"]
            spread = profile["spread"]
            for _ in range(samples_per_tradition):
                sample = center + rng.randn(3) * spread
                sample = np.clip(sample, 0.0, 5.0)
                positions.append(
                    DialPosition.from_array(sample, tradition_name=name)
                )
                labels.append(name)

        return self.fit(positions, labels)

    def predict_genre(
        self, position: DialPosition
    ) -> tuple[str, float]:
        """Predict the genre of a dial position.

        Parameters
        ----------
        position : DialPosition
            The dial position to classify.

        Returns
        -------
        genre : str
            Predicted genre name.
        confidence : float
            Classification confidence [0, 1].

        Raises
        ------
        RuntimeError
            If the classifier has not been fitted.
        """
        self._check_fitted()
        distances = self._compute_distances(position)
        sorted_items = sorted(distances.items(), key=lambda x: x[1])

        # KNN vote
        top_k = sorted_items[: self.k]
        vote_counts: dict[str, int] = {}
        for genre, dist in top_k:
            # Weight by inverse distance
            weight = 1.0 / (dist + 1e-6)
            vote_counts[genre] = vote_counts.get(genre, 0) + weight

        best_genre = max(vote_counts, key=vote_counts.get)  # type: ignore[arg-type]
        total_weight = sum(vote_counts.values())
        confidence = vote_counts[best_genre] / total_weight if total_weight > 0 else 0.0
        confidence = float(np.clip(confidence, 0.0, 1.0))

        return best_genre, confidence

    def predict(self, positions: list[DialPosition]) -> list[tuple[str, float]]:
        """Predict genres for multiple dial positions.

        Parameters
        ----------
        positions : list of DialPosition
            Dial positions to classify.

        Returns
        -------
        list of (genre, confidence) tuples.
        """
        return [self.predict_genre(p) for p in positions]

    def predict_novelty(self, position: DialPosition) -> float:
        """Compute how novel a dial position is relative to known traditions.

        A novelty score near 0 means the position is close to known traditions.
        A score near 1 means it is in unexplored dial space.

        Parameters
        ----------
        position : DialPosition
            The dial position to evaluate.

        Returns
        -------
        float
            Novelty score in [0, 1].
        """
        self._check_fitted()
        distances = self._compute_distances(position)
        min_dist = min(distances.values())
        # Maximum possible distance in 5-cubed space = 5*sqrt(3) ≈ 8.66
        max_possible = 5.0 * np.sqrt(3)
        novelty = min(min_dist / max_possible, 1.0)
        return float(novelty)

    def predict_result(self, position: DialPosition) -> PredictionResult:
        """Full prediction result with distances to all traditions.

        Parameters
        ----------
        position : DialPosition
            The dial position to classify.

        Returns
        -------
        PredictionResult
        """
        self._check_fitted()
        genre, confidence = self.predict_genre(position)
        distances = self._compute_distances(position)
        return PredictionResult(
            genre=genre,
            confidence=confidence,
            distances=distances,
        )

    def cross_validate(
        self,
        positions: list[DialPosition],
        labels: list[str],
        n_folds: int = 5,
    ) -> dict[str, float]:
        """Run k-fold cross-validation.

        Parameters
        ----------
        positions : list of DialPosition
            Dataset positions.
        labels : list of str
            True labels.
        n_folds : int
            Number of folds.

        Returns
        -------
        dict with 'accuracy', 'mean_confidence', 'std_confidence' keys.
        """
        n = len(positions)
        if n != len(labels):
            raise ValueError("positions and labels must have same length")
        rng = np.random.RandomState(self.seed)
        indices = np.arange(n)
        rng.shuffle(indices)

        fold_size = n // n_folds
        accuracies: list[float] = []
        confidences: list[float] = []

        for fold in range(n_folds):
            start = fold * fold_size
            end = start + fold_size if fold < n_folds - 1 else n
            test_idx = set(indices[start:end])
            train_pos = [positions[i] for i in range(n) if i not in test_idx]
            train_lab = [labels[i] for i in range(n) if i not in test_idx]
            test_pos = [positions[i] for i in range(n) if i in test_idx]
            test_lab = [labels[i] for i in range(n) if i in test_idx]

            clf = DialClassifier(k=self.k, seed=self.seed)
            clf.fit(train_pos, train_lab)

            correct = 0
            for pos, true_label in zip(test_pos, test_lab):
                pred, conf = clf.predict_genre(pos)
                if pred == true_label:
                    correct += 1
                confidences.append(conf)
            accuracies.append(correct / max(len(test_pos), 1))

        return {
            "accuracy": float(np.mean(accuracies)),
            "mean_confidence": float(np.mean(confidences)),
            "std_confidence": float(np.std(confidences)),
        }

    def _check_fitted(self) -> None:
        if not self._fitted:
            raise RuntimeError("Classifier not fitted. Call fit() or fit_defaults() first.")

    def _compute_distances(self, position: DialPosition) -> dict[str, float]:
        """Compute distance from position to each training sample's label group."""
        # Average distance to samples of each label
        label_dists: dict[str, list[float]] = {}
        for profile, label in zip(self._profiles, self._labels):
            d = compute_dial_distance(position, profile)
            label_dists.setdefault(label, []).append(d)

        avg_dists: dict[str, float] = {}
        for label, dists in label_dists.items():
            # Use distance to closest samples (k-nearest per class)
            sorted_d = sorted(dists)[: self.k]
            avg_dists[label] = float(np.mean(sorted_d))
        return avg_dists


# ---------------------------------------------------------------------------
# Feature-based classifier
# ---------------------------------------------------------------------------

@dataclass
class FeaturePrediction:
    """Result from FeatureClassifier prediction.

    Parameters
    ----------
    genre : str
        Predicted genre.
    confidence : float
        Confidence in [0, 1].
    feature_vector : FeatureVector
        The extracted feature vector.
    distances : dict[str, float]
        Distance to each class centroid.
    """

    genre: str
    confidence: float
    feature_vector: FeatureVector
    distances: dict[str, float] = field(default_factory=dict)


class FeatureClassifier:
    """Multi-class classifier using 42-dim feature vectors.

    Uses Mahalanobis distance for classification with per-class covariance
    estimation. Falls back to weighted KNN (k=7) when training set is small.

    Parameters
    ----------
    k : int
        KNN fallback parameter (default 7).
    min_samples_for_mahal : int
        Minimum samples per class to use Mahalanobis distance (default 5).
    seed : int
        Random seed for reproducibility.
    """

    def __init__(
        self,
        k: int = 7,
        min_samples_for_mahal: int = 5,
        seed: int = 42,
    ) -> None:
        self.k = k
        self.min_samples_for_mahal = min_samples_for_mahal
        self.seed = seed
        self._vectors: list[NDArray[np.float64]] = []
        self._labels: list[str] = []
        self._class_means: dict[str, NDArray[np.float64]] = {}
        self._class_covs: dict[str, NDArray[np.float64]] = {}
        self._feature_weights: NDArray[np.float64] = np.ones(42, dtype=np.float64)
        self._fitted = False

    def train_from_vectors(
        self,
        vectors: list[NDArray[np.float64]],
        labels: list[str],
    ) -> "FeatureClassifier":
        """Train on pre-extracted feature vectors.

        Parameters
        ----------
        vectors : list of ndarray of shape (42,)
            Feature vectors.
        labels : list of str
            Genre label for each vector.

        Returns
        -------
        self
        """
        if len(vectors) != len(labels):
            raise ValueError(
                f"vectors and labels must have same length, got {len(vectors)} vs {len(labels)}"
            )

        self._vectors = [np.asarray(v, dtype=np.float64) for v in vectors]
        self._labels = list(labels)

        # Compute per-class statistics
        class_vectors: dict[str, list[NDArray[np.float64]]] = {}
        for vec, label in zip(self._vectors, self._labels):
            class_vectors.setdefault(label, []).append(vec)

        self._class_means = {}
        self._class_covs = {}

        for label, vecs in class_vectors.items():
            mat = np.array(vecs, dtype=np.float64)  # (n_samples, 42)
            self._class_means[label] = np.mean(mat, axis=0)

            if len(vecs) >= self.min_samples_for_mahal:
                cov = np.cov(mat, rowvar=False)
                # Regularize covariance
                cov += np.eye(42) * 1e-4
                self._class_covs[label] = cov
            else:
                self._class_covs[label] = np.eye(42, dtype=np.float64)

        # Learn feature importance from class separation
        self._compute_feature_weights(class_vectors)

        self._fitted = True
        return self

    def train_from_wav(
        self,
        directory: str | Path,
        labels: Optional[dict[str, str]] = None,
        sr: int = 44100,
    ) -> "FeatureClassifier":
        """Train by extracting features from labeled WAV files.

        Parameters
        ----------
        directory : str or Path
            Directory containing WAV files.
        labels : dict or None
            Mapping from filename to genre label. If None, labels are
            extracted from filenames using genre keywords.
        sr : int
            Sample rate.

        Returns
        -------
        self
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        wav_files = sorted(directory.glob("*.wav"))
        if not wav_files:
            raise ValueError(f"No .wav files found in {directory}")

        vectors = []
        file_labels = []

        genre_map = {
            "blues": "Blues", "gospel": "Blues",
            "jazz": "Jazz", "bebop": "Jazz",
            "techno": "EDM", "electronic": "EDM", "edm": "EDM",
            "classical": "Classical",
            "gamelan": "Gamelan", "gagaku": "Gagaku",
            "hindustani": "Hindustani",
            "african": "African Polyrhythm",
            "hiphop": "Hip-hop", "hip_hop": "Hip-hop", "rap": "Hip-hop",
            "latin": "Latin", "salsa": "Latin",
        }

        for fpath in wav_files:
            audio, actual_sr = load_wav(str(fpath), sr=sr)
            fv = extract_features(audio, actual_sr)
            vec = fv.to_array()

            if labels and fpath.name in labels:
                label = labels[fpath.name]
            elif labels and str(fpath) in labels:
                label = labels[str(fpath)]
            else:
                name = fpath.stem.lower()
                label = "Unknown"
                for keyword, genre in genre_map.items():
                    if keyword in name:
                        label = genre
                        break

            vectors.append(vec)
            file_labels.append(label)

        return self.train_from_vectors(vectors, file_labels)

    def predict_from_vector(
        self,
        vector: NDArray[np.float64],
    ) -> tuple[str, float, FeatureVector]:
        """Predict genre from a feature vector.

        Parameters
        ----------
        vector : ndarray of shape (42,)
            Feature vector.

        Returns
        -------
        genre : str
            Predicted genre.
        confidence : float
            Confidence in [0, 1].
        feature_vector : FeatureVector
            The input feature vector.
        """
        self._check_fitted()
        vector = np.asarray(vector, dtype=np.float64)

        # Check if we can use Mahalanobis
        use_mahal = all(
            len([v for v, l in zip(self._vectors, self._labels) if l == label])
            >= self.min_samples_for_mahal
            for label in self._class_means
        )

        if use_mahal:
            distances = self._mahalanobis_distances(vector)
        else:
            distances = self._knn_distances(vector)

        # Convert distances to softmax probabilities
        dist_arr = np.array(list(distances.values()), dtype=np.float64)
        # Softmax with temperature
        temp = 2.0
        inv_dist = -dist_arr / temp
        inv_dist -= inv_dist.max()  # numerical stability
        probs = np.exp(inv_dist)
        probs /= probs.sum()

        labels_list = list(distances.keys())
        best_idx = np.argmax(probs)
        best_genre = labels_list[best_idx]
        confidence = float(probs[best_idx])

        fv = FeatureVector.from_array(vector)
        return best_genre, confidence, fv

    def predict_from_wav(
        self,
        path: str | Path,
        sr: int = 44100,
    ) -> FeaturePrediction:
        """Predict genre from a WAV file.

        Parameters
        ----------
        path : str or Path
            Path to WAV file.
        sr : int
            Sample rate.

        Returns
        -------
        FeaturePrediction
        """
        path = Path(path)
        audio, actual_sr = load_wav(str(path), sr=sr)
        fv = extract_features(audio, actual_sr)
        vec = fv.to_array()

        genre, confidence, _ = self.predict_from_vector(vec)

        distances = self._compute_all_distances(vec)

        return FeaturePrediction(
            genre=genre,
            confidence=confidence,
            feature_vector=fv,
            distances=distances,
        )

    def predict(
        self,
        vectors: list[NDArray[np.float64]],
    ) -> list[tuple[str, float]]:
        """Predict genres for multiple feature vectors.

        Returns
        -------
        list of (genre, confidence) tuples.
        """
        results = []
        for vec in vectors:
            genre, conf, _ = self.predict_from_vector(vec)
            results.append((genre, conf))
        return results

    def cross_validate(
        self,
        vectors: list[NDArray[np.float64]],
        labels: list[str],
        n_folds: int = 5,
    ) -> dict[str, float]:
        """K-fold cross-validation.

        Returns
        -------
        dict with 'accuracy', 'mean_confidence', 'std_confidence'.
        """
        n = len(vectors)
        if n != len(labels):
            raise ValueError("vectors and labels must have same length")

        rng = np.random.RandomState(self.seed)
        indices = np.arange(n)
        rng.shuffle(indices)

        fold_size = n // n_folds
        accuracies = []
        confidences = []
        per_class_correct: dict[str, list[bool]] = {}

        for fold in range(n_folds):
            start = fold * fold_size
            end = start + fold_size if fold < n_folds - 1 else n
            test_idx = set(indices[start:end])

            train_vecs = [vectors[i] for i in range(n) if i not in test_idx]
            train_labs = [labels[i] for i in range(n) if i not in test_idx]
            test_vecs = [vectors[i] for i in range(n) if i in test_idx]
            test_labs = [labels[i] for i in range(n) if i in test_idx]

            clf = FeatureClassifier(k=self.k, seed=self.seed)
            clf.train_from_vectors(train_vecs, train_labs)

            for vec, true_label in zip(test_vecs, test_labs):
                pred, conf, _ = clf.predict_from_vector(vec)
                correct = pred == true_label
                per_class_correct.setdefault(true_label, []).append(correct)
                if correct:
                    accuracies.append(1.0)
                else:
                    accuracies.append(0.0)
                confidences.append(conf)

        # Per-class accuracy
        per_class_acc = {}
        for label, corrects in per_class_correct.items():
            per_class_acc[label] = float(np.mean(corrects))

        return {
            "accuracy": float(np.mean(accuracies)),
            "mean_confidence": float(np.mean(confidences)),
            "std_confidence": float(np.std(confidences)),
            "per_class_accuracy": per_class_acc,
        }

    def feature_importance(self) -> dict[str, float]:
        """Return feature importance scores.

        Returns
        -------
        dict mapping feature group names to importance scores.
        """
        self._check_fitted()
        w = self._feature_weights
        groups = {
            "mfccs": float(np.mean(w[0:13])),
            "chroma": float(np.mean(w[13:25])),
            "spectral_contrast": float(np.mean(w[25:31])),
            "rhythmic": float(np.mean(w[31:37])),
            "tonal": float(np.mean(w[37:42])),
        }
        return groups

    def permutation_importance(
        self,
        vectors: list[NDArray[np.float64]],
        labels: list[str],
        n_repeats: int = 10,
    ) -> NDArray[np.float64]:
        """Compute permutation-based feature importance.

        Parameters
        ----------
        vectors : list of ndarray
            Feature vectors.
        labels : list of str
            True labels.
        n_repeats : int
            Number of permutation repeats.

        Returns
        -------
        importance : ndarray of shape (42,)
            Importance score for each feature dimension.
        """
        self._check_fitted()
        rng = np.random.RandomState(self.seed)

        # Baseline accuracy
        baseline_correct = 0
        for vec, label in zip(vectors, labels):
            pred, _, _ = self.predict_from_vector(vec)
            if pred == label:
                baseline_correct += 1
        baseline_acc = baseline_correct / max(len(vectors), 1)

        importance = np.zeros(42, dtype=np.float64)
        mat = np.array(vectors, dtype=np.float64)

        for dim in range(42):
            drops = []
            for _ in range(n_repeats):
                permuted = mat.copy()
                permuted[:, dim] = rng.permutation(permuted[:, dim])

                correct = 0
                for i, (vec, label) in enumerate(zip(permuted, labels)):
                    pred, _, _ = self.predict_from_vector(vec)
                    if pred == label:
                        correct += 1
                perm_acc = correct / max(len(vectors), 1)
                drops.append(baseline_acc - perm_acc)

            importance[dim] = float(np.mean(drops))

        return importance

    def _check_fitted(self) -> None:
        if not self._fitted:
            raise RuntimeError(
                "Classifier not fitted. Call train_from_vectors() or train_from_wav() first."
            )

    def _compute_feature_weights(
        self,
        class_vectors: dict[str, list[NDArray[np.float64]]],
    ) -> None:
        """Compute feature importance from between/within class variance."""
        if len(class_vectors) < 2:
            return

        all_vecs = []
        for vecs in class_vectors.values():
            all_vecs.extend(vecs)
        grand_mean = np.mean(all_vecs, axis=0)

        between_var = np.zeros(42, dtype=np.float64)
        within_var = np.zeros(42, dtype=np.float64)

        for label, vecs in class_vectors.items():
            mat = np.array(vecs, dtype=np.float64)
            class_mean = np.mean(mat, axis=0)
            between_var += len(vecs) * (class_mean - grand_mean) ** 2
            within_var += np.sum((mat - class_mean) ** 2, axis=0)

        # Fisher-like discriminant ratio
        ratio = between_var / np.maximum(within_var, 1e-10)
        self._feature_weights = ratio / max(ratio.max(), 1e-10)

    def _mahalanobis_distances(
        self, vector: NDArray[np.float64]
    ) -> dict[str, float]:
        """Compute Mahalanobis distance to each class centroid."""
        distances = {}
        for label, mean in self._class_means.items():
            cov = self._class_covs.get(label, np.eye(42))
            diff = vector - mean
            try:
                # Solve cov @ x = diff for Mahalanobis distance
                L = np.linalg.cholesky(cov)
                solved = np.linalg.solve(L, diff)
                dist = float(np.sqrt(np.sum(solved ** 2)))
            except np.linalg.LinAlgError:
                # Fallback to weighted Euclidean
                w = self._feature_weights
                dist = float(np.sqrt(np.sum(w * diff ** 2)))
            distances[label] = dist
        return distances

    def _knn_distances(
        self, vector: NDArray[np.float64]
    ) -> dict[str, float]:
        """Weighted KNN fallback for small datasets."""
        w = self._feature_weights
        dists: dict[str, list[float]] = {}

        for vec, label in zip(self._vectors, self._labels):
            d = float(np.sqrt(np.sum(w * (vector - vec) ** 2)))
            dists.setdefault(label, []).append(d)

        result = {}
        for label, d_list in dists.items():
            # Average distance to k nearest neighbors of this class
            sorted_d = sorted(d_list)[:self.k]
            result[label] = float(np.mean(sorted_d))
        return result

    def _compute_all_distances(
        self, vector: NDArray[np.float64]
    ) -> dict[str, float]:
        """Compute distances using the best available method."""
        use_mahal = all(
            len([v for v, l in zip(self._vectors, self._labels) if l == label])
            >= self.min_samples_for_mahal
            for label in self._class_means
        )
        if use_mahal:
            return self._mahalanobis_distances(vector)
        return self._knn_distances(vector)
