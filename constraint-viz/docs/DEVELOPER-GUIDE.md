# Developer Guide — constraint-viz

## Architecture

```
constraint_viz/
├── __init__.py        # Public API: ConstraintOscilloscope
└── multi_scale.py     # Full 4-panel visualization
```

### Visualization Pipeline

1. Parse MIDI → extract notes, timing, velocities
2. **Sample panel**: render waveform from note events (sine synthesis)
3. **Note panel**: scatter plot of pitch vs. time
4. **Phrase panel**: compute holonomy trajectory through circle-of-fifths
5. **Piece panel**: compute note density histogram over time

### Extending

To add a new panel type:
1. Implement a `_plot_<name>(self, ax, mid)` method
2. Add it to `visualize_midi()` layout
3. Update the GridSpec accordingly

### Dependencies

- `matplotlib` — all rendering
- `mido` — MIDI parsing
- `numpy` — numerical computation

## Contributing

```bash
git clone https://github.com/SuperInstance/constraint-viz.git
cd constraint-viz
pip install -e .
```

Tests are in `tests/`. Visualization tests verify output file creation, not pixel accuracy.
