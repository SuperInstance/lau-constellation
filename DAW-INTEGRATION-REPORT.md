# DAW Integration Report — Constraint Theory Music Libraries

> Evaluation of 5 Python music-theory libraries for real-time DAW plugin (VST3/AU) integration.
> Benchmarked on Python 3.10, WSL2 Linux, x64.

---

## 1. Latency Benchmark Results

**Budget:** 256 samples @ 44.1kHz = **5.80ms** per audio buffer.

| Library | Function | Avg Latency | Peak Memory | Within Budget? |
|---|---|---|---|---|
| **constraint-theory-core** | `snap(0.6, 0.8)` | **0.0038ms** | minimal | ✅ 1500x headroom |
| **counterpoint-engine** | `CounterpointGenerator.generate()` | **0.060ms** | moderate | ✅ 97x headroom |
| **holonomy-harmony** | `analyze_progression(["I","IV","V","I"])` | **0.0186ms** | minimal | ✅ 312x headroom |
| **spline-midi-smooth** | `cubic_hermite(100 pts)` | **0.0727ms** | moderate | ✅ 80x headroom |
| **groove-analyzer** | `fit_deadband(GrooveTiming)` | **0.3178ms** | ~46KB | ✅ 18x headroom |

**Verdict:** All five libraries process well within the 5.80ms real-time budget. Even the heaviest (groove-analyzer) has 18x headroom.

---

## 2. Real-Time Feasibility Assessment

### constraint-theory-core ⚡ REAL-TIME READY
- **Latency:** 0.004ms — negligible
- **Memory:** No per-call heap allocation. Pure math (Eisenstein lattice, deadband funnels).
- **Thread safety:** Zero `global` statements. No shared mutable state. Pure functions.
- **Dependencies:** Zero external deps (pure stdlib: `math`, `functools`, `enum`, `dataclasses`).
- **C FFI:** Trivially portable to C — all operations are arithmetic on floats/tuples. A direct C port would be <500 lines.
- **Callback pattern:** `snap()` is a pure function — perfect for pull-based audio callbacks.
- **Rating: ⭐⭐⭐⭐⭐** — drop-in ready for real-time

### holonomy-harmony ⚡ REAL-TIME READY
- **Latency:** 0.019ms — negligible
- **Memory:** Minimal. Builds small dicts/tuples per call.
- **Thread safety:** No globals, no shared state. All pure analysis functions.
- **Dependencies:** Pure stdlib (`re`, `math`). Zero external deps.
- **C FFI:** Straightforward — string parsing (Roman numeral → interval) + graph traversal. Could use ctypes/cffi or port directly.
- **Callback pattern:** `analyze_progression()` returns a result object — stateless, safe for callbacks.
- **Rating: ⭐⭐⭐⭐⭐** — drop-in ready for real-time

### spline-midi-smooth ⚡ REAL-TIME READY (with caveats)
- **Latency:** 0.073ms — well within budget
- **Memory:** Moderate — allocates numpy arrays per call. Could pre-allocate buffers.
- **Thread safety:** No globals. Stateless computations.
- **Dependencies:** `numpy` (C extension — GIL-free for array ops), `mido` (MIDI I/O only, not needed for core math).
- **C FFI:** The core `cubic_hermite`/`catmull_rom`/`bspline` functions are standard spline math — trivially portable. The numpy dependency is only for array convenience.
- **Callback pattern:** Spline evaluation is inherently pull-based. Perfect for per-sample or per-buffer processing.
- **Caveat:** `mido` dependency for MIDI I/O, but core interpolation is numpy-only.
- **Rating: ⭐⭐⭐⭐** — core math is real-time ready; MIDI I/O is offline

### counterpoint-engine ⚡ REAL-TIME READY
- **Latency:** 0.060ms — fast
- **Memory:** Allocates per call (backtracking solver), but amount is bounded and small.
- **Thread safety:** No globals. Generator is instance-based.
- **Dependencies:** `mido` for MIDI output. Core solver is stdlib-only.
- **C FFI:** Backtracking CSP solver ported to C is straightforward. The rule-checking functions are simple integer comparisons.
- **Callback pattern:** Generation is a one-shot operation, not per-sample. Works as "generate on parameter change, output MIDI."
- **Rating: ⭐⭐⭐⭐** — generation is fast enough for real-time parameter changes

### groove-analyzer ✅ REAL-TIME CAPABLE (heaviest)
- **Latency:** 0.318ms — within budget but tightest
- **Memory:** ~46KB peak — allocates lists of timing data.
- **Thread safety:** No globals. Pure analysis functions.
- **Dependencies:** `mido` (MIDI I/O), `numpy`, `matplotlib` (viz only). Core analysis is stdlib + numpy.
- **C FFI:** Statistical analysis (mean, median, MAD, fitting) — portable but non-trivial.
- **Callback pattern:** Analysis is batch-based (processes a groove, returns fit). Not per-sample, but suitable for "analyze on loop capture."
- **Rating: ⭐⭐⭐** — works in real-time but best used for offline analysis or periodic re-analysis

---

## 3. Integration Strategies

### Strategy A: Python Plugin via pybind11 + JUCE (Recommended for Prototyping)

**How it works:**
1. Use [Venom](https://github.com/aszokalski/venom) or [Popsicle](https://github.com/kunitoki/popsicle) to create a JUCE-based VST3/AU shell
2. The JUCE C++ layer handles audio I/O, MIDI, and plugin format
3. Python code runs inside the plugin via embedded CPython
4. `pybind11` bridges C++ ↔ Python

**For our libraries:**
- `constraint_theory_core.snap()` → call from audio callback for real-time pitch quantization
- `holonomy_harmony.analyze_progression()` → call on chord changes for live harmonic analysis
- `spline_midi_smooth.cubic_hermite()` → call for smooth CC/velocity curves
- `counterpoint_engine.CounterpointGenerator` → call on melody input, output counterpoint voice

**GIL management:**
- Release GIL in audio callback with `Py_BEGIN_ALLOW_THREADS`/`Py_END_ALLOW_THREADS`
- Our pure-math functions (snap, holonomy) could be wrapped to release GIL
- Keep Python calls minimal in the hot path

**Pros:** Rapid development, Python ecosystem
**Cons:** GIL overhead, ~1-2ms added latency from Python bridge, distribution complexity (need to bundle Python)

### Strategy B: C Extension Wrapping (Best for Production)

**How it works:**
1. Port the core algorithms to C or use Cython to compile Python → C
2. Link directly into a JUCE/iPlug2 plugin as a static library
3. No Python runtime needed in the final plugin

**For our libraries:**
- `constraint_theory_core` → **Already mostly pure math.** Port `snap()`, `covering_radius()`, `encode_dodecet()` to C. Estimated: ~300 lines of C.
- `holonomy_harmony` → Port the tonal graph + cycle checker. Estimated: ~500 lines of C.
- `spline_midi_smooth` → Port spline interpolation. Standard math libraries exist. Estimated: ~200 lines of C.
- `counterpoint_engine` → Port the CSP solver + rule engine. Estimated: ~800 lines of C.
- `groove_analyzer` → Port statistical fitting. Estimated: ~600 lines of C.

**Alternative: Use `cffi` or `ctypes` to call Python from C:**
- Embed CPython in the plugin host
- Call Python functions via `PyObject_CallObject()`
- This is what PyoPlug does

**Pros:** No GIL issues, zero overhead, native distribution
**Cons:** More development effort, maintenance of C port

### Strategy C: Offline Processing → MIDI File → DAW Import (Easiest, Ship Today)

**How it works:**
1. Run the Python libraries offline to generate/modify MIDI
2. Export as `.mid` file
3. Import into any DAW (Ableton, Logic, Reaper, etc.)

**For our libraries:**
```python
# Generate counterpoint → export MIDI
from counterpoint_engine import CounterpointGenerator
from spline_midi_smooth import smooth_midi_cc, smooth_velocity_curve
from groove_analyzer import synthesize_groove

gen = CounterpointGenerator([60, 62, 64, 65, 67])
result = gen.generate()
# result → MIDI file → DAW

# Apply groove to MIDI
groove = synthesize_groove("swing", bpm=120)
# Apply to MIDI file → export

# Smooth CC curves
smooth_midi_cc("input.mid", "output.mid")
```

**This already works today.** The libraries already output MIDI via `mido`.

**Pros:** Zero DAW integration work, universal compatibility, works with any DAW
**Cons:** Not real-time, no live parameter control, no audio feedback loop

---

## 4. Audio Playback Gap — How to Add Instant Preview

The current libraries generate MIDI but can't produce audible output. Here's how to bridge that gap:

### Option 1: FluidSynth (MIDI → Audio) — RECOMMENDED
- **Library:** `pyfluidsynth` (Python bindings for FluidSynth C library)
- **How:** Load a SoundFont (.sf2), feed MIDI events → get audio samples out
- **Latency:** ~5-10ms with proper buffer settings
- **Integration:** `synth.get_samples(256)` returns audio buffers → feed to sounddevice
- **Best for:** Realistic instrument playback, instant MIDI preview

```python
import fluidsynth
synth = fluidsynth.Synth()
synth.sfload("GeneralUser_GS.sf2")
synth.noteon(0, 60, 80)  # Middle C
samples = synth.get_samples(256)  # Get audio buffer
```

### Option 2: sounddevice (Raw Audio Output)
- **Library:** `sounddevice` (PortAudio bindings)
- **How:** Open an audio output stream, push numpy arrays
- **Latency:** As low as 1-5ms with small buffers
- **Best for:** Custom synthesis, direct audio output

```python
import sounddevice as sd
sd.play(audio_array, samplerate=44100)
```

### Option 3: pyo (Full Audio Framework)
- **Library:** `pyo` (full DSP framework with real-time processing)
- **How:** Build signal processing chains, connect to audio output
- **Latency:** ~10-20ms (higher due to Python overhead)
- **Best for:** Prototyping DSP effects, interactive audio

### Recommended Stack for Instant Preview:
1. **`fluidsynth`** for MIDI→audio rendering (SoundFont-based, realistic)
2. **`sounddevice`** for low-latency audio output
3. Bridge: generate MIDI with our libraries → feed to FluidSynth → output via sounddevice

This gives a complete pipeline: **constraint theory → MIDI → audio → speakers** with <15ms total latency.

---

## 5. Priority Features for Musicians (Top 5)

### 1. 🎹 Real-Time Pitch Snap Plugin (constraint-theory-core)
**The killer feature.** A MIDI plugin that snaps incoming MIDI notes to the nearest Eisenstein lattice point. Like auto-tune for harmony — quantizes to mathematically optimal consonances.

**Why first:** Simplest to build (one function call), most immediately useful, visually compelling (shows lattice in UI), works as both MIDI effect and audio effect.

**Implementation:** JUCE MIDI plugin → `snap()` on incoming note → output snapped note. Could ship in 2-3 days.

### 2. 🎵 Counterpoint Generator Plugin (counterpoint-engine)
A MIDI plugin that takes a melody input and generates a counterpoint voice in real-time. Species counterpoint as a creative tool.

**Why second:** Unique selling point — no other plugin does CSP-based counterpoint generation. Great for composers and students.

**Implementation:** JUCE MIDI plugin → `CounterpointGenerator` on melody buffer → output counterpoint MIDI.

### 3. 🎸 MIDI Smoother Plugin (spline-midi-smooth)
A MIDI CC/velocity smoothing plugin using spline interpolation with deadband theory. Smooths jerky controller data while preserving intentional expression.

**Why third:** Solves a real problem every MIDI musician has (jerky pitch bend, stepped volume). Deadband-aware smoothing is novel.

**Implementation:** JUCE MIDI plugin → `cubic_hermite()` / `smooth_pitch_bend()` on CC stream.

### 4. 📊 Groove Analyzer Standalone (groove-analyzer)
A standalone app or plugin that analyzes recorded MIDI grooves and extracts the "feel" as a deadband funnel profile. Can then apply that feel to other MIDI patterns.

**Why fourth:** "Groove extraction → application" is a sought-after feature. No other tool does mathematical groove analysis.

**Implementation:** Standalone Python app with fluidsynth preview → export groove profile → VST groove quantizer.

### 5. 🎼 Harmonic Analysis Overlay (holonomy-harmony)
A plugin that sits on a MIDI track and provides real-time harmonic analysis — chord detection, modulation detection, and holonomy scoring. Like a smarter chord tracker.

**Why fifth:** Educational tool + compositional aid. Shows "how stable is your harmony right now" as a visual overlay.

**Implementation:** JUCE plugin → `analyze_progression()` on chord stream → display stability scores in UI.

---

## Appendix: Integration Technology Summary

| Technology | Type | Real-time? | VST3/AU? | Python? | Complexity |
|---|---|---|---|---|---|
| **JUCE + pybind11** (Venom) | Plugin framework | ✅ (with care) | ✅ | ✅ | High |
| **Faust** | DSP language → C++ | ✅ native | ✅ | ❌ (generates C++) | Medium |
| **pyo + PyoPlug** | Python DSP → VST | ⚠️ (10-20ms) | ✅ (VST2) | ✅ | Low |
| **Pedalboard** (Spotify) | Python audio FX | ❌ (offline) | ❌ | ✅ | Low |
| **DawDreamer** | Python DAW host | ❌ (offline) | ❌ | ✅ | Medium |
| **iPlug2** | C++ plugin framework | ✅ native | ✅ | ❌ | High |
| **FaustVst** | Live Faust in DAW | ✅ | ✅ (VST3) | ❌ | Low |
| **Cython port** | Python → C | ✅ | ✅ (via JUCE) | ✅ (source) | Medium |

**Recommended path:** Start with Strategy C (offline MIDI) for immediate value, then Strategy B (C port via Cython + JUCE) for production plugins.

---

*Report generated 2026-05-22 by subagent evaluation of constraint-theory music ecosystem.*
