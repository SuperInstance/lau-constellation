# constraint-viz — Multi-Scale Constraint Oscilloscope

Visualize the same musical constraint structure at four scales simultaneously: waveform (lattice snap geometry), piano roll (pitch lattice), holonomy trajectory (key drift), and note density (structural arc). One input, four perspectives.

## Install

```bash
pip install constraint-viz
```

Requires Python 3.10+, `numpy`, `matplotlib`, `mido`.

## Quick Start

```python
from constraint_viz import ConstraintOscilloscope

scope = ConstraintOscilloscope()
scope.visualize_midi("song.mid", "song_scope.png")
# → 4-panel PNG (3000×2400 px) saved to song_scope.png
```

## The Key Idea

A piece of music has constraint structure at every scale — from the sample level (how a waveform snaps to lattice directions) to the piece level (how note density reveals form). These aren't separate analyses; they're the same constraint geometry rendered at different resolutions. The oscilloscope shows all four simultaneously so you can see how microstructure (sample) connects to macrostructure (piece).

## The Four Panels

| Panel | Scale | What It Shows |
|-------|-------|---------------|
| **Sample** | Waveform | Lattice snap geometry — how the signal snaps to discrete directions |
| **Note** | Piano roll | Pitch lattice & timing grid — active scale degrees, Eisenstein quantization |
| **Phrase** | Holonomy trajectory | Key drift through circle-of-fifths — modulations appear as excursions |
| **Piece** | Note density | Structural arc — information density across the whole piece |

## API Reference

### ConstraintOscilloscope

```python
scope = ConstraintOscilloscope()
scope.visualize_midi(
    midi_path="song.mid",           # Path to MIDI file
    output_path="scope.png",        # Output PNG path
    title="My Song — Analysis",     # Optional title (auto-generated if None)
) → str  # Returns output path
```

Output: 20×16 inch PNG at 150 DPI (3000×2400 pixels).

## Documentation

- [User Guide](docs/USER-GUIDE.md) — Complete usage documentation
- [Developer Guide](docs/DEVELOPER-GUIDE.md) — Contributing and internals
- [Examples](examples/) — Batch visualization demo

## Related

- [constraint-synth](https://github.com/SuperInstance/constraint-synth) — Lattice-based synthesizer (oscilloscope shows its output beautifully)
- [constraint-theory-core](https://github.com/SuperInstance/constraint-theory-core) — The mathematical primitives
- [flux-tensor-midi](https://github.com/SuperInstance/flux-tensor-midi) — 4D tensor MIDI representation
