# Constraint Solver Viz

Real-time visualisations of constraint solving using `constraint-theory-core`.

## Modules

- `lattice_viz.py` — points snapping to the Eisenstein A₂ lattice with Voronoi cells
- `funnel_viz.py` — deadband funnel narrowing with anomaly detection
- `rigidity_viz.py` — Laman graph construction and rigidity matrix
- `metronome_viz.py` — 9-agent phase consensus on the unit circle
- `holonomy_viz.py` — circle-of-fifths walk with cumulative holonomy

## Usage

Each module is runnable standalone and saves output to `viz_output/`:

```bash
python -m constraint_solver_viz.lattice_viz
python -m constraint_solver_viz.funnel_viz
python -m constraint_solver_viz.rigidity_viz
python -m constraint_solver_viz.metronome_viz
python -m constraint_solver_viz.holonomy_viz
```

## Dependencies

- `matplotlib`
- `numpy`
- `scipy`
- `constraint-theory-core`
