# Changelog

All notable changes to constraint-toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2025-05-25

### Added

- **Web demo** (`demo.py`) — zero-dependency browser interface with:
  - WAV upload → analysis → genre prediction
  - Interactive 3D dial space visualization (isometric SVG)
  - Click-to-compose: generate music at any point in dial space
  - Tradition explorer with 10 profiled traditions
  - Conservation comparison tool
  - Dark theme with responsive mobile layout
- **CLI entry point** (`constraint-toolkit` command) with subcommands: `analyze`, `classify`, `compose`, `demo`, `traditions`
- **`__main__.py`** for `python -m constraint_toolkit` support
- **API documentation** (`docs/api.md`) — complete reference for all public functions
- **This changelog** (`CHANGELOG.md`)
- Additional modules: `recommender.py`, `style_transfer.py`, `accompanist.py`, `synthesizer.py`, `benchmarks.py`

### Changed

- Updated `pyproject.toml` to v0.2.0 with PyPI classifiers, `[project.scripts]` entry point, and `[tool.setuptools.packages.find]`
- Expanded `README.md` with architecture diagram, comprehensive usage examples, experiment results table, and full API reference

### Experiments Completed

1. **Genre classification** — 13 WAV files tested; classifier operational
2. **Conservation stress test** — 10,000 random sequences; CV 11.1%, correlation +0.738
3. **Dial space mapping** — 10 traditions fully profiled; unexplored fraction measured
4. **Groove optimization** — Simulated annealing converges on rhythmic complexity dimension
5. **Cross-cultural analysis** — Comparative profiles across all traditions

### Tests

- 71 tests passing across all core modules

## [0.1.0] — 2025-05-24

### Added

- Core dial framework (`dials.py`) — `DialPosition`, distance metrics, clustering, 10 tradition profiles
- Genre classifier (`classifier.py`) — KNN on dial positions, Mahalanobis on features
- Feature extraction (`features.py`) — 42-dim vectors: MFCCs, chroma, spectral contrast, rhythmic, tonal
- Audio analysis (`analyzer.py`) — WAV/MIDI → dial positions
- Groove optimizer (`optimizer.py`) — Simulated annealing for microtiming
- Constraint composer (`composer.py`) — Arc consistency for voice leading and harmony
- Conservation module (`conservation.py`) — Tension measurement, meantone/ET comparison
- Audio utilities (`audio_utils.py`) — WAV loading, spectrum, onset detection, pitch classes
- MIDI utilities (`midi_utils.py`) — Onset extraction, microtiming, quantization
- 5 experiment scripts
- Test suite with pytest
- Initial `pyproject.toml` and `README.md`

### Known Research Constants

- V_K / H_onset correlation: r = −0.935
- Tradition recognition rate: 98%
- Unexplored dial space: 82%
- Most pleasing point: (2.61, 2.33, 4.0) — Gagaku
- Conservation ratio: ~1.003

[0.2.0]: https://github.com/user/constraint-toolkit/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/user/constraint-toolkit/releases/tag/v0.1.0
