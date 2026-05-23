# User Guide — constraint-viz

Multi-scale visualization of musical constraint structures. The same underlying constraint geometry rendered at four levels simultaneously.

## Installation

```bash
pip install constraint-viz
```

Requires Python 3.10+, `numpy`, `matplotlib`, `mido`.

## Quick Start

```python
from constraint_viz import ConstraintOscilloscope

scope = ConstraintOscilloscope()

# Generate a 4-panel visualization
output = scope.visualize_midi(
    midi_path="my_song.mid",
    output_path="my_song_scope.png",
    title="My Song — Constraint Analysis",
)
print(f"Saved to {output}")
```

## The Four Panels

| Panel | Scale | What It Shows |
|-------|-------|---------------|
| **Sample** (top-left) | Audio waveform | Lattice snap geometry — how the signal snaps to discrete lattice directions |
| **Note** (top-right) | Piano roll | Pitch lattice & timing grid — which scale degrees are active, Eisenstein quantization |
| **Phrase** (bottom-left) | Holonomy trajectory | Key drift over time — circle-of-fifths path showing modulations |
| **Piece** (bottom-right) | Note density | Structural arc — how information density evolves across the whole piece |

### Sample Level

The waveform panel reveals the lattice geometry underlying the audio. For a constraint-synth output, you can literally see the Eisenstein snap structure — the signal snaps to hexagonal lattice directions rather than flowing smoothly.

### Note Level

The piano roll shows which pitch lattice points are occupied and how they're quantized. Timing deviations from the Eisenstein lattice appear as offsets from the grid.

### Phrase Level

The holonomy trajectory traces the piece's journey through tonal space. A piece that stays in one key traces a tight cluster; modulations appear as excursions. The holonomy of the tonal path measures how far from the tonal center the piece wanders.

### Piece Level

The density panel shows how much musical information is present over time. Peaks correspond to climaxes; valleys to sparse passages. This is the piece's structural arc visualized as a constraint profile.

## API Reference

### ConstraintOscilloscope

| Method | Description |
|--------|-------------|
| `.visualize_midi(midi_path, output_path, title)` | Generate full 4-panel visualization |

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `midi_path` | `str` | required | Path to MIDI file |
| `output_path` | `str` | `"constraint_scope.png"` | Output image path |
| `title` | `str \| None` | `None` | Custom title (auto-generated if None) |

## Output

The oscilloscope produces a 20×16 inch PNG at 150 DPI (3000×2400 pixels). Each panel is labeled and titled. The output is suitable for embedding in papers, presentations, or documentation.
