"""
Constraint Toolkit — Music analysis and composition based on Dials Not Laws theory.
"""

__version__ = "0.2.0"

from .dials import DialPosition, DIAL_RANGES, compute_dial_distance, compute_dial_signature, classify_dial_cluster
from .classifier import DialClassifier, FeatureClassifier, FeaturePrediction
from .features import FeatureVector, extract_features
from .analyzer import analyze_wav, analyze_midi, batch_analyze, compute_dial_from_features
from .optimizer import GrooveOptimizer
from .composer import ConstraintComposer
from .conservation import measure_tension, conservation_ratio, stress_test
from .evolution import MusicalEvolution
from .oracle import DialOracle
from .timeline import MusicalTimeline
from .games import DialGuesser, TraditionBattles, DialExplorer
from .datasets import Dataset, AudioSample, MidiSample, label_from_filename
from .metrics import (
    confusion_matrix, classification_report, accuracy_with_ci,
    dial_distance_accuracy, pairwise_agreement, permutation_test,
)
from .visualize import (
    ascii_scatter, ascii_confusion_matrix, ascii_dial_space,
    ascii_bar_chart, format_results_table, ascii_heatmap,
)

__all__ = [
    "DialPosition",
    "DIAL_RANGES",
    "compute_dial_distance",
    "compute_dial_signature",
    "classify_dial_cluster",
    "DialClassifier",
    "FeatureClassifier",
    "FeaturePrediction",
    "FeatureVector",
    "extract_features",
    "analyze_wav",
    "analyze_midi",
    "batch_analyze",
    "compute_dial_from_features",
    "GrooveOptimizer",
    "ConstraintComposer",
    "measure_tension",
    "conservation_ratio",
    "stress_test",
    # Dataset & evaluation
    "Dataset",
    "AudioSample",
    "MidiSample",
    "label_from_filename",
    "confusion_matrix",
    "classification_report",
    "accuracy_with_ci",
    "dial_distance_accuracy",
    "pairwise_agreement",
    "permutation_test",
    # Visualization
    "ascii_scatter",
    "ascii_confusion_matrix",
    "ascii_dial_space",
    "ascii_bar_chart",
    "format_results_table",
    "ascii_heatmap",
    # New creative modules
    "MusicalEvolution",
    "DialOracle",
    "MusicalTimeline",
    "DialGuesser",
    "TraditionBattles",
    "DialExplorer",
]
