# Cross-Repo Dependency Map

## Dependency Graph

```
constraint-theory-core (no deps)
    └── counterpoint-engine
        └── Imports: constraint_theory_core.rigidity, constraint_theory_core.lattice

flux-tensor-midi (no deps, installed from wheel)
    ├── counterpoint-engine
    │   └── Imports: flux_tensor_midi.core.flux.FluxVector, flux_tensor_midi.midi.events.MidiEvent
    └── plato-room-musician
        └── Imports: (via dependency declaration)

groove-analyzer (no cross-repo deps)
    └── Imports: mido, numpy, matplotlib (external)

holonomy-harmony (no cross-repo deps)
    └── Pure Python, no external deps

spline-midi-smooth (no cross-repo deps)
    └── Imports: numpy, mido (external)

plato-room-musician
    └── Imports: mido, numpy (external); depends on flux-tensor-midi

flux-tensor-midi (workspace source is empty scaffolding; actual code in installed wheel)
    └── Workspace directory has empty subdirs: adapters, core, ensemble, git_native, harmony, midi, sidechannel
```

## Installation Order

1. constraint-theory-core
2. flux-tensor-midi (pre-installed from wheel)
3. counterpoint-engine (depends on 1, 2)
4. groove-analyzer
5. holonomy-harmony
6. spline-midi-smooth
7. plato-room-musician (depends on 2)
