# API Reference — Constraint Toolkit v0.2.0

Complete reference for all public modules, classes, and functions.

---

## Table of Contents

- [dials](#dials)
- [features](#features)
- [classifier](#classifier)
- [analyzer](#analyzer)
- [optimizer](#optimizer)
- [composer](#composer)
- [conservation](#conservation)
- [audio_utils](#audio_utils)
- [midi_utils](#midi_utils)
- [recommender](#recommender)
- [style_transfer](#style_transfer)
- [accompanist](#accompanist)
- [synthesizer](#synthesizer)
- [benchmarks](#benchmarks)

---

## dials

Core dial framework for the Dials Not Laws theory.

### `DialPosition`

```python
@dataclass(frozen=True)
class DialPosition:
    harmonic_tension: float       # 0–5
    rhythmic_complexity: float    # 0–5
    spectral_density: float       # 0–5
    tradition_name: str | None = None
    metadata: dict = field(default_factory=dict)
```

A position in 3D dial space. Values are clamped to [0, 5].

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `to_array()` | `NDArray[np.float64]` | 3-element array [H, R, S] |
| `from_array(arr, tradition_name?, metadata?)` | `DialPosition` | Construct from array (classmethod) |

**Example:**

```python
from constraint_toolkit.dials import DialPosition

pos = DialPosition(3.5, 4.0, 3.0, tradition_name="Jazz")
arr = pos.to_array()  # array([3.5, 4.0, 3.0])
pos2 = DialPosition.from_array(arr)
```

### Constants

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| `DIAL_RANGES` | `dict[str, dict]` | 10 entries | Tradition profiles with center, spread, description |
| `VK_H_ONSET_CORRELATION` | `float` | −0.935 | V_K / H_onset correlation |
| `TRADITION_RECOGNITION_RATE` | `float` | 0.98 | Classification accuracy on known traditions |
| `UNEXPLORED_FRACTION` | `float` | 0.82 | Fraction of dial space unexplored |
| `MOST_PLEASING_POINT` | `DialPosition` | (2.61, 2.33, 4.0) | Gagaku — highest rated |

### `compute_dial_distance(pos1, pos2)`

```python
def compute_dial_distance(pos1: DialPosition, pos2: DialPosition) -> float
```

Euclidean distance between two dial positions.

**Parameters:**
- `pos1` — First position
- `pos2` — Second position

**Returns:** `float` — Euclidean distance in [0, 8.66]

**Example:**

```python
dist = compute_dial_distance(
    DialPosition(3.5, 4.0, 3.0),
    DialPosition(2.0, 2.0, 2.5)
)  # 2.693
```

### `compute_dial_signature(onset_times, pitch_classes, spectrum)`

```python
def compute_dial_signature(
    onset_times: NDArray[np.float64],
    pitch_classes: NDArray[np.intp],
    spectrum: NDArray[np.float64],
) -> DialPosition
```

Compute a dial position from raw musical data using empirically validated formulas.

**Parameters:**
- `onset_times` — Array of onset timestamps in seconds
- `pitch_classes` — Array of pitch class indices (0–11)
- `spectrum` — Magnitude spectrum

**Returns:** `DialPosition`

### `classify_dial_cluster(positions, k=5)`

```python
def classify_dial_cluster(
    positions: list[DialPosition],
    k: int = 5,
) -> tuple[NDArray[np.intp], list[DialPosition]]
```

K-means clustering on dial positions.

**Parameters:**
- `positions` — List of DialPosition objects
- `k` — Number of clusters

**Returns:** Tuple of (labels array, cluster centers as DialPositions)

---

## features

42-dimensional feature extraction from audio.

### `FeatureVector`

```python
@dataclass
class FeatureVector:
    mfccs: NDArray[np.float64]           # shape (13, n_frames)
    chroma: NDArray[np.float64]           # shape (12, n_frames)
    spectral_contrast: NDArray[np.float64] # shape (6, n_frames)
    rhythmic_features: NDArray[np.float64] # shape (6,)
    tonal_features: NDArray[np.float64]    # shape (5,)
    duration: float
    n_frames: int
```

### `extract_features(audio, sr=44100)`

```python
def extract_features(
    audio: NDArray[np.float64],
    sr: int = 44100,
) -> FeatureVector
```

Extract full feature vector from audio samples.

**Parameters:**
- `audio` — Mono audio array, float64, normalized [-1, 1]
- `sr` — Sample rate

**Returns:** `FeatureVector`

**Example:**

```python
from constraint_toolkit.audio_utils import load_wav
from constraint_toolkit.features import extract_features

audio, sr = load_wav("song.wav")
features = extract_features(audio, sr)
print(features.mfccs.shape)  # (13, n_frames)
print(features.duration)     # seconds
```

---

## classifier

Genre/style classification from dial positions and feature vectors.

### `PredictionResult`

```python
@dataclass
class PredictionResult:
    genre: str
    confidence: float          # [0, 1]
    distances: dict[str, float]
    feature_vector: FeatureVector | None = None
```

### `DialClassifier`

```python
class DialClassifier:
    def __init__(self, k: int = 5, seed: int = 42) -> None
```

KNN classifier on 3D dial positions. Auto-fits with default tradition profiles.

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `fit(positions, labels)` | `self` | Train on labeled positions |
| `fit_defaults()` | `self` | Load 10 built-in tradition profiles |
| `predict(pos)` | `PredictionResult` | Classify a single position |
| `predict_genre(pos)` | `tuple[str, float]` | Get (genre, confidence) tuple |

**Example:**

```python
from constraint_toolkit.classifier import DialClassifier
from constraint_toolkit.dials import DialPosition

clf = DialClassifier(k=5)
pos = DialPosition(3.2, 3.8, 2.8)
result = clf.predict(pos)
print(result.genre)       # "Jazz"
print(result.confidence)  # 0.82
```

### `FeaturePrediction`

```python
@dataclass
class FeaturePrediction:
    genre: str
    confidence: float
    distances: dict[str, float]
    feature_vector: FeatureVector | None
```

### `FeatureClassifier`

```python
class FeatureClassifier:
    def __init__(self, seed: int = 42) -> None
```

Mahalanobis-distance classifier on 42-dimensional feature vectors.

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `fit(feature_vectors, labels)` | `self` | Train on labeled feature vectors |
| `fit_defaults()` | `self` | Load default profiles |
| `predict(features)` | `FeaturePrediction` | Classify from feature vector |
| `predict_from_audio(audio, sr)` | `FeaturePrediction` | Extract features and classify |

---

## analyzer

Real audio/MIDI analysis → dial positions.

### `AnalysisResult`

```python
@dataclass
class AnalysisResult:
    dial_position: DialPosition
    spectral_features: dict[str, float]   # centroid, bandwidth, rolloff, flux, rms
    onset_count: int
    duration: float
    pitch_class_distribution: dict[int, float]
    file_path: str
```

**Methods:**
- `to_dict()` → `dict` — JSON-serializable dict
- `summary()` → `str` — Human-readable summary

### `analyze_wav(path, sr=44100)`

```python
def analyze_wav(path: str | Path, sr: int = 44100) -> AnalysisResult
```

Analyze a WAV file and compute its dial position.

**Parameters:**
- `path` — Path to WAV file
- `sr` — Target sample rate (resampled if needed)

**Returns:** `AnalysisResult`

**Example:**

```python
from constraint_toolkit.analyzer import analyze_wav

result = analyze_wav("song.wav")
print(result.dial_position)
print(result.spectral_features)
print(result.summary())
```

### `analyze_midi(path, bpm=120)`

```python
def analyze_midi(path: str | Path, bpm: int = 120) -> AnalysisResult
```

Analyze a MIDI file.

**Parameters:**
- `path` — Path to MIDI file
- `bpm` — Tempo for onset time calculation

**Returns:** `AnalysisResult`

### `batch_analyze(paths)`

```python
def batch_analyze(paths: list[str | Path], sr: int = 44100) -> list[AnalysisResult]
```

Analyze multiple files. Skips files that fail analysis.

**Parameters:**
- `paths` — List of file paths (WAV or MIDI)

**Returns:** List of `AnalysisResult`

### `compute_dial_from_features(features)`

```python
def compute_dial_from_features(features: FeatureVector) -> DialPosition
```

Map a FeatureVector directly to a DialPosition.

---

## optimizer

Groove optimizer — adjusts microtiming via simulated annealing.

### `OptimizationResult`

```python
@dataclass
class OptimizationResult:
    midi: MidiFile
    optimized_position: DialPosition
    target_position: DialPosition
    distance_to_target: float
    converged: bool
    iterations: int
    fitness_history: list[float]
```

### `GrooveOptimizer`

```python
class GrooveOptimizer:
    def __init__(self, seed: int = 42, deadband: float = 0.05) -> None
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `optimize(midi_path, target, iterations=100)` | `OptimizationResult` | Optimize onset offsets toward target dial position |
| `optimize_audio(audio, sr, target, iterations=100)` | `OptimizationResult` | Optimize from audio array |

**Example:**

```python
from constraint_toolkit.optimizer import GrooveOptimizer
from constraint_toolkit.dials import DialPosition

opt = GrooveOptimizer()
target = DialPosition(3.5, 4.0, 3.0)
result = opt.optimize("input.mid", target, iterations=200)
print(f"Converged: {result.converged}, Distance: {result.distance_to_target:.3f}")
result.midi.save("optimized.mid")
```

---

## composer

Constraint-based composition engine using arc consistency.

### `ConstraintComposer`

```python
class ConstraintComposer:
    def __init__(self, seed: int = 42) -> None
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `compose_in_tradition(name, bars=8, tempo=120)` | `MidiFile` | Generate music in a tradition's style |
| `compose_at_position(pos, bars=4, tempo=120)` | `MidiFile` | Generate at a specific dial position |
| `compose_hybrid(name1, name2, bars=8, tempo=120)` | `MidiFile` | Blend two traditions |

**Example:**

```python
from constraint_toolkit.composer import ConstraintComposer

composer = ConstraintComposer()
midi = composer.compose_in_tradition("Jazz", bars=8, tempo=120)
midi.save("jazz.mid")

# Hybrid
midi = composer.compose_hybrid("Gamelan", "Blues", bars=4)
midi.save("fusion.mid")
```

---

## conservation

Conservation of tension measurements. Tests the hypothesis: I_vertical + I_horizontal ≈ constant.

### `measure_tension(sequence, tuning="ET")`

```python
def measure_tension(
    sequence: list[int],
    tuning: str = "ET",
) -> tuple[float, float]
```

Measure vertical and horizontal tension in a melody.

**Parameters:**
- `sequence` — List of MIDI note numbers or pitch classes
- `tuning` — `"ET"` (equal temperament) or `"meantone"` (quarter-comma meantone)

**Returns:** `(I_vertical, I_horizontal)` — tuple of floats

**Example:**

```python
from constraint_toolkit.conservation import measure_tension

melody = [60, 64, 67, 72, 71, 67, 64, 60]
iv, ih = measure_tension(melody)
print(f"Vertical: {iv:.4f}, Horizontal: {ih:.4f}")
```

### `conservation_ratio(sequence)`

```python
def conservation_ratio(sequence: list[int]) -> float
```

Compare meantone vs ET tension ratios. Known result: ~1.003.

**Returns:** `float` — meantone_total / et_total

### `stress_test(n_sequences=10000)`

```python
def stress_test(n_sequences: int = 10000) -> dict
```

Statistical stress test of conservation hypothesis with random sequences.

**Returns:** `dict` with keys: `mean_sum`, `std_sum`, `cv`, `correlation`, `meantone_ratio`, `n_sequences`, `distribution`

---

## audio_utils

WAV processing utilities.

### `load_wav(path, sr=44100)`

```python
def load_wav(path: str | Path, sr: int = 44100) -> tuple[NDArray[np.float64], int]
```

Load a WAV file, convert to mono, resample to target rate.

**Returns:** `(audio_array, sample_rate)`

### `compute_spectrum(audio, sr)`

```python
def compute_spectrum(audio: NDArray[np.float64], sr: int) -> NDArray[np.float64]
```

Compute magnitude spectrum via FFT.

### `detect_onsets(audio, sr)`

```python
def detect_onsets(audio: NDArray[np.float64], sr: int) -> NDArray[np.float64]
```

Detect note onsets using spectral flux. Returns onset times in seconds.

### `compute_pitch_classes(audio, sr)`

```python
def compute_pitch_classes(audio: NDArray[np.float64], sr: int) -> NDArray[np.intp]
```

Compute pitch class distribution from audio. Returns array of pitch class indices (0–11).

### `compute_spectral_features(audio, sr)`

```python
def compute_spectral_features(audio: NDArray[np.float64], sr: int) -> dict[str, float]
```

Compute spectral features: centroid, bandwidth, rolloff, flux, rms.

**Returns:** `dict` with keys: `centroid`, `bandwidth`, `rolloff`, `flux`, `rms`

---

## midi_utils

MIDI generation and processing utilities.

### `midi_note_to_pitch_class(note)`

```python
def midi_note_to_pitch_class(note: int) -> int
```

Map MIDI note number to pitch class (0–11).

### `midi_to_onsets(path)`

```python
def midi_to_onsets(path: str | Path) -> list[tuple[float, int, int]]
```

Extract onsets from MIDI file. Returns list of `(time_seconds, note, velocity)`.

### `onsets_to_midi(onsets, bpm=120)`

```python
def onsets_to_midi(
    onsets: list[tuple[float, int, int]],
    bpm: int = 120,
) -> MidiFile
```

Create a MIDI file from onset data.

**Parameters:**
- `onsets` — List of `(time, note, velocity)` tuples
- `bpm` — Tempo

**Returns:** `MidiFile`

### `apply_microtiming(midi, offsets)`

```python
def apply_microtiming(
    midi: MidiFile,
    offsets: list[float],
) -> MidiFile
```

Apply timing offsets to MIDI notes for groove feel.

### `quantize_midi(midi, grid=0.25)`

```python
def quantize_midi(midi: MidiFile, grid: float = 0.25) -> MidiFile
```

Snap note times to a rhythmic grid (in beats). Default: 16th note grid (0.25).

### `extract_onset_times(midi, bpm=120)`

```python
def extract_onset_times(midi: MidiFile, bpm: int = 120) -> NDArray[np.float64]
```

Get onset times as a float array in seconds.

### `extract_pitch_classes_from_midi(midi)`

```python
def extract_pitch_classes_from_midi(midi: MidiFile) -> NDArray[np.intp]
```

Extract pitch class array from MIDI data.

---

## recommender

Music recommendation based on dial similarity.

### `Recommendation`

```python
@dataclass
class Recommendation:
    position: DialPosition
    tradition_name: str | None
    similarity: float
    adventure_factor: float
    fusion_viability: float | None
```

### `MusicRecommender`

```python
class MusicRecommender:
    def __init__(self, tradition_profiles: dict | None = None) -> None
```

Suggest traditions and dial positions based on similarity, adventure, and fusion potential.

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `recommend(query, n=5)` | `list[Recommendation]` | Get top-N recommendations |
| `recommend_similar(pos)` | `list[Recommendation]` | Find similar traditions |
| `recommend_adventurous(pos)` | `list[Recommendation]` | Find different-but-interesting positions |
| `recommend_fusion(pos1, pos2)` | `list[Recommendation]` | Find fusion-friendly positions |

---

## style_transfer

Transform a piece's style via dial interpolation.

### `StyleTransfer`

```python
class StyleTransfer:
    def __init__(self) -> None
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `transfer(midi_path, source_tradition, target_tradition, blend=0.5)` | `MidiFile` | Transfer style between traditions |
| `interpolate(pos1, pos2, n_steps=5)` | `list[DialPosition]` | Generate interpolation path |

---

## accompanist

Automatic accompaniment generation.

### `AutoAccompanist`

```python
class AutoAccompanist:
    def __init__(self, seed: int = 42) -> None
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `accompany(melody_midi, style?)` | `MidiFile` | Generate accompaniment for a melody |
| `detect_key(midi)` | `tuple[int, str]` | Detect key from MIDI |

---

## synthesizer

Audio synthesis from constraints.

### `ConstraintSynth`

```python
class ConstraintSynth:
    def __init__(self, sr: int = 44100) -> None
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `synthesize(midi, dial_position?)` | `NDArray[np.float64]` | Render MIDI to audio |
| `synthesize_position(pos, duration)` | `NDArray[np.float64]` | Synthesize audio at a dial position |

---

## benchmarks

Performance benchmarking suite.

### `BenchmarkResult`

```python
@dataclass
class BenchmarkResult:
    name: str
    duration_seconds: float
    memory_peak_mb: float
    success: bool
    details: dict
```

### `BenchmarkReport`

```python
@dataclass
class BenchmarkReport:
    results: list[BenchmarkResult]
    timestamp: str
    version: str
```

### `BenchmarkSuite`

```python
class BenchmarkSuite:
    def __init__(self) -> None
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `run_all()` | `BenchmarkReport` | Run all benchmarks |
| `run(name)` | `BenchmarkResult` | Run a specific benchmark |

### `save_report(report, path)`

```python
def save_report(report: BenchmarkReport, path: str | Path) -> None
```

Save benchmark report to JSON file.
