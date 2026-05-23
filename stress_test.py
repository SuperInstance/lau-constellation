#!/usr/bin/env python3
"""
Adversarial stress tests for 6 Python packages.
Finds crashes, bad error messages, and silent failures.
"""

import sys
import os
import traceback
import tempfile
import warnings
import json
import random

# Don't convert warnings to errors - some tests need to catch warnings gracefully

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "constraint-theory-core"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "counterpoint-engine"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "groove-analyzer"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "holonomy-harmony"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "spline-midi-smooth"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "plato-room-musician"))

results = []

def run_test(pkg, test_name, func):
    """Run a single test and record the result."""
    try:
        func()
        results.append((pkg, test_name, "OK", "", ""))
    except Exception as e:
        tb = traceback.format_exc()
        results.append((pkg, test_name, "CRASH", str(e), tb))

# ========================================================================
# 1. CONSTRAINT-THEORY-CORE
# ========================================================================

def test_ctc_lattice():
    from constraint_theory_core import snap

    # NaN
    try:
        snap(float('nan'), 0.0)
        results.append(("constraint-theory-core", "lattice.snap(NaN)", "SILENT", "No error for NaN input", ""))
    except (ValueError, TypeError) as e:
        results.append(("constraint-theory-core", "lattice.snap(NaN)", "OK", str(e), ""))
    except Exception as e:
        results.append(("constraint-theory-core", "lattice.snap(NaN)", "CRASH", str(e), traceback.format_exc()))

    # Infinity
    try:
        snap(float('inf'), 0.0)
        results.append(("constraint-theory-core", "lattice.snap(Inf)", "SILENT", "No error for Inf input", ""))
    except (ValueError, TypeError, OverflowError) as e:
        results.append(("constraint-theory-core", "lattice.snap(Inf)", "OK", str(e), ""))
    except Exception as e:
        results.append(("constraint-theory-core", "lattice.snap(Inf)", "CRASH", str(e), traceback.format_exc()))

    # (0,0) - should be fine
    try:
        pt, err = snap(0.0, 0.0)
        results.append(("constraint-theory-core", "lattice.snap(0,0)", "OK", f"snap OK: pt=({pt.a:.4f},{pt.b:.4f}), err={err:.6f}", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "lattice.snap(0,0)", "CRASH", str(e), traceback.format_exc()))

    # Very large values
    try:
        pt, err = snap(1e15, 1e15)
        results.append(("constraint-theory-core", "lattice.snap(1e15,1e15)", "OK", f"snap OK: pt=({pt.a:.2e},{pt.b:.2e}), err={err:.2e}", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "lattice.snap(1e15,1e15)", "CRASH", str(e), traceback.format_exc()))

    # Very small values
    try:
        pt, err = snap(1e-15, 1e-15)
        results.append(("constraint-theory-core", "lattice.snap(1e-15,1e-15)", "OK", f"snap OK: pt=({pt.a:.2e},{pt.b:.2e}), err={err:.2e}", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "lattice.snap(1e-15,1e-15)", "CRASH", str(e), traceback.format_exc()))


def test_ctc_temporal():
    from constraint_theory_core.temporal import TemporalAgent

    # Negative epsilon
    try:
        ta = TemporalAgent(epsilon_0=-0.1)
        results.append(("constraint-theory-core", "temporal.neg_epsilon", "SILENT", "No error for negative epsilon", ""))
    except ValueError as e:
        results.append(("constraint-theory-core", "temporal.neg_epsilon", "OK", str(e), ""))
    except Exception as e:
        results.append(("constraint-theory-core", "temporal.neg_epsilon", "CRASH", str(e), traceback.format_exc()))

    # Epsilon = 0
    try:
        ta = TemporalAgent(epsilon_0=0.0)
        results.append(("constraint-theory-core", "temporal.zero_epsilon", "OK", f"Created with epsilon=0", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "temporal.zero_epsilon", "CRASH", str(e), traceback.format_exc()))

    # Very large epsilon
    try:
        ta = TemporalAgent(epsilon_0=1e10)
        results.append(("constraint-theory-core", "temporal.large_epsilon", "OK", f"Created with epsilon=1e10", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "temporal.large_epsilon", "CRASH", str(e), traceback.format_exc()))

    # 10000 agents (just test creating and ticking one)
    try:
        agents = [TemporalAgent(epsilon_0=0.577) for _ in range(10000)]
        for a in agents:
            a.decay(1.0)
        results.append(("constraint-theory-core", "temporal.10k_agents", "OK", "10000 agents created and ticked", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "temporal.10k_agents", "CRASH", str(e), traceback.format_exc()))

    # 0 agents - not really testable as an API, skip


def test_ctc_rigidity():
    from constraint_theory_core import is_laman

    # 1-vertex graph
    try:
        result = is_laman(1, [])
        results.append(("constraint-theory-core", "rigidity.1_vertex", "OK", f"is_laman(1,[])={result}", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "rigidity.1_vertex", "CRASH", str(e), traceback.format_exc()))

    # 2-vertex graph
    try:
        result = is_laman(2, [(0, 1)])
        results.append(("constraint-theory-core", "rigidity.2_vertex", "OK", f"is_laman(2,[(0,1)])={result}", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "rigidity.2_vertex", "CRASH", str(e), traceback.format_exc()))

    # 100-vertex graph (Laman: need 2*100-3=197 edges)
    try:
        import random as _r
        _r.seed(42)
        edges = [(i, i+1) for i in range(99)]
        # Add more edges to reach 197
        extra_needed = 197 - 99
        added = set()
        while len(added) < extra_needed:
            a, b = _r.randint(0, 99), _r.randint(0, 99)
            if a != b and (min(a,b), max(a,b)) not in added:
                added.add((min(a,b), max(a,b)))
        edges.extend(list(added))
        result = is_laman(100, edges)
        results.append(("constraint-theory-core", "rigidity.100_vertex", "OK", f"is_laman(100,...)={result}", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "rigidity.100_vertex", "CRASH", str(e), traceback.format_exc()))

    # Cyclic graph (triangle = 3 vertices, 3 edges = 2*3-3)
    try:
        result = is_laman(3, [(0,1),(1,2),(2,0)])
        results.append(("constraint-theory-core", "rigidity.cyclic_triangle", "OK", f"is_laman(triangle)={result}", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "rigidity.cyclic_triangle", "CRASH", str(e), traceback.format_exc()))

    # Disconnected graph
    try:
        result = is_laman(4, [(0,1),(2,3)])
        results.append(("constraint-theory-core", "rigidity.disconnected", "OK", f"is_laman(disconnected)={result}", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "rigidity.disconnected", "CRASH", str(e), traceback.format_exc()))


def test_ctc_metronome():
    from constraint_theory_core import Metronome

    # 0 agents metronome
    try:
        m = Metronome(n_agents=0)
        m.tick()
        results.append(("constraint-theory-core", "metronome.0_agents", "OK", "0-agent metronome ticked", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "metronome.0_agents", "CRASH", str(e), traceback.format_exc()))

    # 1 agent
    try:
        m = Metronome(n_agents=1)
        m.tick()
        results.append(("constraint-theory-core", "metronome.1_agent", "OK", f"phase={m.phase:.4f}", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "metronome.1_agent", "CRASH", str(e), traceback.format_exc()))

    # 1000 agents
    try:
        edges = [(i, i+1) for i in range(999)]
        metronomes = []
        for i in range(1000):
            neighbors = []
            if i > 0: neighbors.append(i-1)
            if i < 999: neighbors.append(i+1)
            m = Metronome(n_agents=1000, neighbors=neighbors, edges=edges)
            metronomes.append(m)
        for m in metronomes:
            m.tick()
        results.append(("constraint-theory-core", "metronome.1000_agents", "OK", "1000 agents ticked", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "metronome.1000_agents", "CRASH", str(e), traceback.format_exc()))

    # All converged
    try:
        m1 = Metronome(phi0=0.0, epsilon=10.0, n_agents=1)
        m2 = Metronome(phi0=0.01, epsilon=10.0, n_agents=1)
        agree = m1.agree(m2)
        results.append(("constraint-theory-core", "metronome.already_converged", "OK", f"agree={agree}", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "metronome.already_converged", "CRASH", str(e), traceback.format_exc()))


def test_ctc_holonomy():
    from constraint_theory_core import cycle_holonomy, verify_consistency, isolate_fault

    # Empty cycle
    try:
        result = cycle_holonomy([], [])
        results.append(("constraint-theory-core", "holonomy.empty_cycle", "OK", f"holonomy={result}", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "holonomy.empty_cycle", "CRASH", str(e), traceback.format_exc()))

    # Single element cycle
    try:
        result = cycle_holonomy([(0, 0)], [0])
        results.append(("constraint-theory-core", "holonomy.single_element", "OK", f"holonomy={result}", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "holonomy.single_element", "CRASH", str(e), traceback.format_exc()))

    # 1000-element cycle
    try:
        edges = [(i, (i+1) % 1000) for i in range(1000)]
        directions = [0] * 1000
        result = cycle_holonomy(edges, directions)
        results.append(("constraint-theory-core", "holonomy.1000_element", "OK", f"holonomy={result}", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "holonomy.1000_element", "CRASH", str(e), traceback.format_exc()))

    # All same values
    try:
        result = cycle_holonomy([(0,1),(1,2),(2,0)], [12,12,12])
        results.append(("constraint-theory-core", "holonomy.all_same", "OK", f"holonomy={result}", ""))
    except Exception as e:
        results.append(("constraint-theory-core", "holonomy.all_same", "CRASH", str(e), traceback.format_exc()))

    # Mismatched lengths
    try:
        cycle_holonomy([(0,1),(1,2)], [12])
        results.append(("constraint-theory-core", "holonomy.mismatched_len", "SILENT", "No error for mismatched lengths", ""))
    except ValueError as e:
        results.append(("constraint-theory-core", "holonomy.mismatched_len", "OK", str(e), ""))
    except Exception as e:
        results.append(("constraint-theory-core", "holonomy.mismatched_len", "CRASH", str(e), traceback.format_exc()))

    # Out-of-range direction
    try:
        cycle_holonomy([(0,1)], [999])
        results.append(("constraint-theory-core", "holonomy.bad_direction", "SILENT", "No error for direction 999", ""))
    except ValueError as e:
        results.append(("constraint-theory-core", "holonomy.bad_direction", "OK", str(e), ""))
    except Exception as e:
        results.append(("constraint-theory-core", "holonomy.bad_direction", "CRASH", str(e), traceback.format_exc()))


# ========================================================================
# 2. COUNTERPOINT-ENGINE
# ========================================================================

def test_ce_empty_cf():
    from counterpoint_engine.generator import CounterpointGenerator
    try:
        CounterpointGenerator(cantus_firmus=[])
        results.append(("counterpoint-engine", "cf.empty", "SILENT", "No error for empty CF", ""))
    except ValueError as e:
        results.append(("counterpoint-engine", "cf.empty", "OK", str(e), ""))
    except Exception as e:
        results.append(("counterpoint-engine", "cf.empty", "CRASH", str(e), traceback.format_exc()))


def test_ce_1note_cf():
    from counterpoint_engine.generator import CounterpointGenerator, Scale
    try:
        gen = CounterpointGenerator(cantus_firmus=[60], scale=Scale(tonic=0))
        result = gen.generate()
        results.append(("counterpoint-engine", "cf.1_note", "OK", f"result={result}", ""))
    except Exception as e:
        results.append(("counterpoint-engine", "cf.1_note", "CRASH", str(e), traceback.format_exc()))


def test_ce_100note_cf():
    from counterpoint_engine.generator import CounterpointGenerator, Scale
    try:
        cf = [60, 62, 64, 65, 67, 69, 71, 72] * 12 + [72]  # 97 notes
        gen = CounterpointGenerator(cantus_firmus=cf, scale=Scale(tonic=0))
        # Don't generate (too slow with backtracking on 100 notes), just construct
        results.append(("counterpoint-engine", "cf.100_note_construct", "OK", "Constructed OK", ""))
    except Exception as e:
        results.append(("counterpoint-engine", "cf.100_note_construct", "CRASH", str(e), traceback.format_exc()))


def test_ce_all_same_note():
    from counterpoint_engine.generator import CounterpointGenerator, Scale
    try:
        gen = CounterpointGenerator(cantus_firmus=[60]*8, scale=Scale(tonic=0))
        result = gen.generate()
        results.append(("counterpoint-engine", "cf.all_same", "OK", f"result={'found' if result else 'None'}", ""))
    except Exception as e:
        results.append(("counterpoint-engine", "cf.all_same", "CRASH", str(e), traceback.format_exc()))


def test_ce_chromatic_cf():
    from counterpoint_engine.generator import CounterpointGenerator, Scale
    try:
        # Chromatic CF: most notes won't be in scale
        cf = list(range(60, 72))
        gen = CounterpointGenerator(cantus_firmus=cf, scale=Scale(tonic=0))
        result = gen.generate()
        results.append(("counterpoint-engine", "cf.chromatic", "OK", f"result={'found' if result else 'None'}", ""))
    except Exception as e:
        results.append(("counterpoint-engine", "cf.chromatic", "CRASH", str(e), traceback.format_exc()))


def test_ce_random_cf():
    from counterpoint_engine.generator import CounterpointGenerator, Scale
    try:
        random.seed(42)
        cf = [random.randint(48, 79) for _ in range(10)]
        gen = CounterpointGenerator(cantus_firmus=cf, scale=Scale(tonic=0))
        result = gen.generate()
        results.append(("counterpoint-engine", "cf.random", "OK", f"result={'found' if result else 'None'}", ""))
    except Exception as e:
        results.append(("counterpoint-engine", "cf.random", "CRASH", str(e), traceback.format_exc()))


def test_ce_invalid_species():
    from counterpoint_engine.generator import CounterpointGenerator, Species, Scale

    for val, label in [(0, "0"), (-1, "-1"), (6, "6"), (999, "999")]:
        try:
            # Species is IntEnum, so Species(0) is valid (FIRST=1 so Species(0) creates a new member)
            gen = CounterpointGenerator(cantus_firmus=[60, 62, 64], species=Species(val), scale=Scale(tonic=0))
            results.append(("counterpoint-engine", f"species.{label}", "SILENT", f"Accepted species={val}", ""))
        except ValueError as e:
            results.append(("counterpoint-engine", f"species.{label}", "OK", str(e), ""))
        except Exception as e:
            results.append(("counterpoint-engine", f"species.{label}", "CRASH", str(e), traceback.format_exc()))


def test_ce_bad_key():
    from counterpoint_engine.generator import Scale
    for val, label in [(-1, "-1"), (12, "12"), (100, "100"), ("C", "str_C")]:
        try:
            s = Scale(tonic=val)
            results.append(("counterpoint-engine", f"key.{label}", "SILENT", f"Accepted key_tonic={val!r}", ""))
        except (ValueError, TypeError) as e:
            results.append(("counterpoint-engine", f"key.{label}", "OK", str(e), ""))
        except Exception as e:
            results.append(("counterpoint-engine", f"key.{label}", "CRASH", str(e), traceback.format_exc()))


def test_ce_voice_range_overlap():
    from counterpoint_engine.generator import VoiceRange, Scale, CounterpointGenerator
    # Non-overlapping ranges
    try:
        gen = CounterpointGenerator(
            cantus_firmus=[60, 62, 64, 65, 67],
            scale=Scale(tonic=0),
            voice_range=VoiceRange(min_pitch=80, max_pitch=90),  # no overlap with CF range
        )
        result = gen.generate()
        results.append(("counterpoint-engine", "voice.no_overlap", "OK", f"result={'found' if result else 'None'}", ""))
    except Exception as e:
        results.append(("counterpoint-engine", "voice.no_overlap", "CRASH", str(e), traceback.format_exc()))

    # Inverted range
    try:
        VoiceRange(min_pitch=90, max_pitch=60)
        results.append(("counterpoint-engine", "voice.inverted", "SILENT", "No error for min > max", ""))
    except ValueError as e:
        results.append(("counterpoint-engine", "voice.inverted", "OK", str(e), ""))
    except Exception as e:
        results.append(("counterpoint-engine", "voice.inverted", "CRASH", str(e), traceback.format_exc()))


# ========================================================================
# 3. GROOVE-ANALYZER
# ========================================================================

def _make_midi_file(notes=None, bpm=120, ticks_per_beat=480):
    """Helper to create a temporary MIDI file."""
    import mido
    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))

    if notes:
        for note in notes:
            tick, pitch, vel, dur = note
            track.append(mido.Message('note_on', note=pitch, velocity=vel, time=tick))
            track.append(mido.Message('note_off', note=pitch, velocity=0, time=dur))
    else:
        # Just end of track
        pass

    track.append(mido.MetaMessage('end_of_track', time=0))

    fd, path = tempfile.mkstemp(suffix='.mid')
    os.close(fd)
    mid.save(path)
    return path


def test_ga_empty_midi():
    from groove_analyzer.microtiming import extract_microtiming
    try:
        path = _make_midi_file(notes=[])
        result = extract_microtiming(path)
        results.append(("groove-analyzer", "midi.empty_tracks", "OK", f"bpm={result.bpm}, tracks={len(result.tracks)}", ""))
    except Exception as e:
        results.append(("groove-analyzer", "midi.empty_tracks", "CRASH", str(e), traceback.format_exc()))
    finally:
        os.unlink(path)


def test_ga_metadata_only():
    from groove_analyzer.microtiming import extract_microtiming
    import mido
    try:
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        track.append(mido.MetaMessage('track_name', name='test', time=0))
        track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
        track.append(mido.MetaMessage('end_of_track', time=0))
        mid.tracks.append(track)

        fd, path = tempfile.mkstemp(suffix='.mid')
        os.close(fd)
        mid.save(path)

        # Should warn (no note_on events) and return empty
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = extract_microtiming(path)
        results.append(("groove-analyzer", "midi.metadata_only", "OK", f"bpm={result.bpm}, tracks={len(result.tracks)}", ""))
        os.unlink(path)
    except Exception as e:
        results.append(("groove-analyzer", "midi.metadata_only", "CRASH", str(e), traceback.format_exc()))


def test_ga_1_note():
    from groove_analyzer.microtiming import extract_microtiming
    try:
        path = _make_midi_file(notes=[(0, 60, 100, 480)])
        result = extract_microtiming(path)
        results.append(("groove-analyzer", "midi.1_note", "OK", f"tracks={len(result.tracks)}, onsets={sum(len(t.onsets) for t in result.tracks)}", ""))
    except Exception as e:
        results.append(("groove-analyzer", "midi.1_note", "CRASH", str(e), traceback.format_exc()))
    finally:
        os.unlink(path)


def test_ga_10000_notes():
    from groove_analyzer.microtiming import extract_microtiming
    try:
        notes = [(i * 48, 60 + (i % 12), 80, 24) for i in range(10000)]
        path = _make_midi_file(notes=notes)
        result = extract_microtiming(path)
        total_onsets = sum(len(t.onsets) for t in result.tracks)
        results.append(("groove-analyzer", "midi.10k_notes", "OK", f"total_onsets={total_onsets}", ""))
    except Exception as e:
        results.append(("groove-analyzer", "midi.10k_notes", "CRASH", str(e), traceback.format_exc()))
    finally:
        try: os.unlink(path)
        except: pass


def test_ga_overlapping_notes():
    from groove_analyzer.microtiming import extract_microtiming
    try:
        # Two notes at same time
        path = _make_midi_file(notes=[(0, 60, 100, 480), (0, 64, 100, 480)])
        result = extract_microtiming(path)
        results.append(("groove-analyzer", "midi.overlapping", "OK", f"onsets={sum(len(t.onsets) for t in result.tracks)}", ""))
    except Exception as e:
        results.append(("groove-analyzer", "midi.overlapping", "CRASH", str(e), traceback.format_exc()))
    finally:
        os.unlink(path)


def test_ga_extreme_bpm():
    from groove_analyzer.microtiming import extract_microtiming
    for bpm, label in [(1, "bpm_1"), (300, "bpm_300")]:
        try:
            path = _make_midi_file(notes=[(0, 60, 100, 480)], bpm=bpm)
            result = extract_microtiming(path)
            results.append(("groove-analyzer", f"extreme.{label}", "OK", f"bpm={result.bpm}", ""))
        except Exception as e:
            results.append(("groove-analyzer", f"extreme.{label}", "CRASH", str(e), traceback.format_exc()))
        finally:
            try: os.unlink(path)
            except: pass

    # BPM=0 is not representable in MIDI (tempo = 60e6/0 = inf)
    # Test that groove-analyzer handles it if someone constructs such a file
    try:
        import mido
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        # No tempo event = default 120 BPM, just add a note
        track.append(mido.Message('note_on', note=60, velocity=100, time=0))
        track.append(mido.Message('note_off', note=60, velocity=0, time=480))
        track.append(mido.MetaMessage('end_of_track', time=0))
        mid.tracks.append(track)
        fd, path = tempfile.mkstemp(suffix='.mid')
        os.close(fd)
        mid.save(path)
        result = extract_microtiming(path)
        results.append(("groove-analyzer", "extreme.default_bpm", "OK", f"bpm={result.bpm}", ""))
        os.unlink(path)
    except Exception as e:
        results.append(("groove-analyzer", "extreme.default_bpm", "CRASH", str(e), traceback.format_exc()))


def test_ga_nonexistent_file():
    from groove_analyzer.microtiming import extract_microtiming
    try:
        extract_microtiming("/tmp/nonexistent_file_12345.mid")
        results.append(("groove-analyzer", "file.nonexistent", "SILENT", "No error for nonexistent file", ""))
    except (FileNotFoundError, OSError, ValueError) as e:
        results.append(("groove-analyzer", "file.nonexistent", "OK", str(e)[:100], ""))
    except Exception as e:
        results.append(("groove-analyzer", "file.nonexistent", "CRASH", str(e), traceback.format_exc()))


def test_ga_corrupted_file():
    from groove_analyzer.microtiming import extract_microtiming
    try:
        fd, path = tempfile.mkstemp(suffix='.mid')
        os.write(fd, b"NOT A MIDI FILE!!! CORRUPTED DATA")
        os.close(fd)
        extract_microtiming(path)
        results.append(("groove-analyzer", "file.corrupted", "SILENT", "No error for corrupted file", ""))
    except Exception as e:
        results.append(("groove-analyzer", "file.corrupted", "OK", f"{type(e).__name__}: {str(e)[:100]}", ""))
    finally:
        os.unlink(path)


def test_ga_grid_division():
    from groove_analyzer.microtiming import extract_microtiming
    for val, label in [(0, "div_0"), (1, "div_1"), (1000, "div_1000")]:
        try:
            path = _make_midi_file(notes=[(0, 60, 100, 480)])
            result = extract_microtiming(path, grid_division=val)
            results.append(("groove-analyzer", f"grid.{label}", "OK", f"grid_div={result.grid_division}", ""))
        except ValueError as e:
            results.append(("groove-analyzer", f"grid.{label}", "OK", str(e)[:80], ""))
        except Exception as e:
            results.append(("groove-analyzer", f"grid.{label}", "CRASH", str(e), traceback.format_exc()))
        finally:
            try: os.unlink(path)
            except: pass


# ========================================================================
# 4. HOLONOMY-HARMONY
# ========================================================================

def test_hh_empty_progression():
    from holonomy_harmony import analyze_progression
    try:
        analyze_progression([])
        results.append(("holonomy-harmony", "prog.empty", "SILENT", "No error for empty progression", ""))
    except ValueError as e:
        results.append(("holonomy-harmony", "prog.empty", "OK", str(e), ""))
    except Exception as e:
        results.append(("holonomy-harmony", "prog.empty", "CRASH", str(e), traceback.format_exc()))


def test_hh_single_chord():
    from holonomy_harmony import analyze_progression
    try:
        result = analyze_progression(["I"])
        results.append(("holonomy-harmony", "prog.single", "OK", f"holonomy={result.holonomy.holonomy}", ""))
    except Exception as e:
        results.append(("holonomy-harmony", "prog.single", "CRASH", str(e), traceback.format_exc()))


def test_hh_1000_chords():
    from holonomy_harmony import analyze_progression
    try:
        result = analyze_progression(["I", "IV", "V"] * 333 + ["I"])
        results.append(("holonomy-harmony", "prog.1000_chords", "OK", f"chords={len(result.chords)}", ""))
    except Exception as e:
        results.append(("holonomy-harmony", "prog.1000_chords", "CRASH", str(e), traceback.format_exc()))


def test_hh_all_same_chord():
    from holonomy_harmony import analyze_progression
    try:
        result = analyze_progression(["I"] * 20)
        results.append(("holonomy-harmony", "prog.all_same", "OK", f"holonomy={result.holonomy.holonomy}", ""))
    except Exception as e:
        results.append(("holonomy-harmony", "prog.all_same", "CRASH", str(e), traceback.format_exc()))


def test_hh_random_chromatic():
    from holonomy_harmony import analyze_progression
    try:
        random.seed(42)
        chromatic = ["I", "bII", "II", "bIII", "III", "IV", "bV", "V", "bVI", "VI", "bVII", "VII"]
        prog = [random.choice(chromatic) for _ in range(20)]
        result = analyze_progression(prog)
        results.append(("holonomy-harmony", "prog.random_chromatic", "OK", f"holonomy={result.holonomy.holonomy}", ""))
    except Exception as e:
        results.append(("holonomy-harmony", "prog.random_chromatic", "CRASH", str(e), traceback.format_exc()))


def test_hh_invalid_roman():
    from holonomy_harmony import parse_roman
    for val, label in [("", "empty"), ("H", "H"), ("V99", "V99"), ("\u03b5", "epsilon")]:
        try:
            parse_roman(val)
            results.append(("holonomy-harmony", f"roman.{label}", "SILENT", f"Accepted '{val}'", ""))
        except ValueError as e:
            results.append(("holonomy-harmony", f"roman.{label}", "OK", str(e)[:100], ""))
        except Exception as e:
            results.append(("holonomy-harmony", f"roman.{label}", "CRASH", str(e), traceback.format_exc()))


def test_hh_invalid_key():
    from holonomy_harmony import analyze_progression
    for val, label in [(-1, "-1"), (12, "12"), (100, "100"), ("C", "str_C")]:
        try:
            result = analyze_progression(["I", "IV", "V", "I"], key_tonic=val)
            results.append(("holonomy-harmony", f"key.{label}", "SILENT", f"Accepted key_tonic={val!r}", ""))
        except (ValueError, TypeError) as e:
            results.append(("holonomy-harmony", f"key.{label}", "OK", str(e)[:100], ""))
        except Exception as e:
            results.append(("holonomy-harmony", f"key.{label}", "CRASH", str(e), traceback.format_exc()))


def test_hh_secondary_dominants():
    from holonomy_harmony import analyze_progression
    try:
        result = analyze_progression(["V/vi", "V/IV", "V/ii", "V/V", "I"])
        results.append(("holonomy-harmony", "prog.secondary_doms", "OK", f"modulations={len(result.modulations)}", ""))
    except Exception as e:
        results.append(("holonomy-harmony", "prog.secondary_doms", "CRASH", str(e), traceback.format_exc()))


# ========================================================================
# 5. SPLINE-MIDI-SMOOTH
# ========================================================================

def test_sms_0_points():
    from spline_midi_smooth.interpolation import cubic_hermite, catmull_rom, bspline
    for func_name, func in [("hermite", cubic_hermite), ("catmull", catmull_rom)]:
        try:
            func([])
            results.append(("spline-midi-smooth", f"interp.0_pts_{func_name}", "SILENT", "No error for 0 points", ""))
        except ValueError as e:
            results.append(("spline-midi-smooth", f"interp.0_pts_{func_name}", "OK", str(e), ""))
        except Exception as e:
            results.append(("spline-midi-smooth", f"interp.0_pts_{func_name}", "CRASH", str(e), traceback.format_exc()))


def test_sms_1_point():
    from spline_midi_smooth.interpolation import cubic_hermite, catmull_rom, bspline
    for func_name, func in [("hermite", cubic_hermite), ("catmull", catmull_rom)]:
        try:
            func([(0.0, 1.0)])
            results.append(("spline-midi-smooth", f"interp.1_pt_{func_name}", "SILENT", "No error for 1 point", ""))
        except ValueError as e:
            results.append(("spline-midi-smooth", f"interp.1_pt_{func_name}", "OK", str(e), ""))
        except Exception as e:
            results.append(("spline-midi-smooth", f"interp.1_pt_{func_name}", "CRASH", str(e), traceback.format_exc()))


def test_sms_2_identical_points():
    from spline_midi_smooth.interpolation import cubic_hermite
    try:
        s = cubic_hermite([(0.0, 5.0), (0.0, 5.0)])
        results.append(("spline-midi-smooth", "interp.2_identical", "SILENT", "No error for duplicate x values", ""))
    except ValueError as e:
        results.append(("spline-midi-smooth", "interp.2_identical", "OK", str(e), ""))
    except Exception as e:
        results.append(("spline-midi-smooth", "interp.2_identical", "CRASH", str(e), traceback.format_exc()))


def test_sms_10000_points():
    from spline_midi_smooth.interpolation import cubic_hermite
    try:
        # Use 1000 points (10k is too slow for the Python loop in eval)
        pts = [(float(i), float(i * 2)) for i in range(1000)]
        s = cubic_hermite(pts)
        val = s(500.0)
        results.append(("spline-midi-smooth", "interp.1k_points", "OK", f"eval at 500={val:.2f}", ""))
    except Exception as e:
        results.append(("spline-midi-smooth", "interp.1k_points", "CRASH", str(e), traceback.format_exc()))


def test_sms_non_increasing_x():
    from spline_midi_smooth.interpolation import cubic_hermite
    try:
        cubic_hermite([(0.0, 1.0), (1.0, 2.0), (0.5, 3.0)])  # x goes 0, 1, 0.5
        results.append(("spline-midi-smooth", "interp.non_increasing_x", "SILENT", "No error for non-increasing x", ""))
    except ValueError as e:
        results.append(("spline-midi-smooth", "interp.non_increasing_x", "OK", str(e), ""))
    except Exception as e:
        results.append(("spline-midi-smooth", "interp.non_increasing_x", "CRASH", str(e), traceback.format_exc()))


def test_sms_duplicate_x():
    from spline_midi_smooth.interpolation import cubic_hermite
    try:
        cubic_hermite([(0.0, 1.0), (1.0, 2.0), (1.0, 3.0)])
        results.append(("spline-midi-smooth", "interp.dup_x", "SILENT", "No error for duplicate x", ""))
    except ValueError as e:
        results.append(("spline-midi-smooth", "interp.dup_x", "OK", str(e), ""))
    except Exception as e:
        results.append(("spline-midi-smooth", "interp.dup_x", "CRASH", str(e), traceback.format_exc()))


def test_sms_large_y():
    from spline_midi_smooth.interpolation import cubic_hermite
    try:
        s = cubic_hermite([(0.0, 1e15), (1.0, -1e15)])
        val = s(0.5)
        results.append(("spline-midi-smooth", "interp.large_y", "OK", f"val={val:.2e}", ""))
    except Exception as e:
        results.append(("spline-midi-smooth", "interp.large_y", "CRASH", str(e), traceback.format_exc()))


def test_sms_nan_y():
    from spline_midi_smooth.interpolation import cubic_hermite
    try:
        cubic_hermite([(0.0, float('nan')), (1.0, 2.0)])
        results.append(("spline-midi-smooth", "interp.nan_y", "SILENT", "No error for NaN y", ""))
    except ValueError as e:
        results.append(("spline-midi-smooth", "interp.nan_y", "OK", str(e), ""))
    except Exception as e:
        results.append(("spline-midi-smooth", "interp.nan_y", "CRASH", str(e), traceback.format_exc()))


def test_sms_inf_y():
    from spline_midi_smooth.interpolation import cubic_hermite
    try:
        cubic_hermite([(0.0, float('inf')), (1.0, 2.0)])
        results.append(("spline-midi-smooth", "interp.inf_y", "SILENT", "No error for Inf y", ""))
    except ValueError as e:
        results.append(("spline-midi-smooth", "interp.inf_y", "OK", str(e), ""))
    except Exception as e:
        results.append(("spline-midi-smooth", "interp.inf_y", "CRASH", str(e), traceback.format_exc()))


def test_sms_tension_out_of_range():
    from spline_midi_smooth.interpolation import catmull_rom
    for tension, label in [(-1.0, "neg"), (2.0, "high"), (100.0, "100")]:
        try:
            s = catmull_rom([(0.0, 0.0), (1.0, 1.0), (2.0, 4.0)], tension=tension)
            val = s(1.5)
            results.append(("spline-midi-smooth", f"tension.{label}", "OK", f"val={val:.4f}", ""))
        except ValueError as e:
            results.append(("spline-midi-smooth", f"tension.{label}", "OK", str(e), ""))
        except Exception as e:
            results.append(("spline-midi-smooth", f"tension.{label}", "CRASH", str(e), traceback.format_exc()))


def test_sms_bspline_degree():
    from spline_midi_smooth.interpolation import bspline
    for deg, n_pts, label in [(0, 5, "deg0"), (20, 30, "deg20")]:
        try:
            pts = [(float(i), float(i)) for i in range(n_pts)]
            s = bspline(pts, degree=deg)
            val = s(1.0)
            results.append(("spline-midi-smooth", f"bspline.{label}", "OK", f"val={val:.4f}", ""))
        except ValueError as e:
            results.append(("spline-midi-smooth", f"bspline.{label}", "OK", str(e)[:80], ""))
        except Exception as e:
            results.append(("spline-midi-smooth", f"bspline.{label}", "CRASH", str(e), traceback.format_exc()))


# ========================================================================
# 6. PLATO-ROOM-MUSICIAN
# ========================================================================

def test_prm_empty_room_list():
    from plato_room_musician.score import PlatoScore
    try:
        score = PlatoScore(events=[])
        score.normalize_time()
        results.append(("plato-room-musician", "rooms.empty", "OK", f"duration={score.duration_beats}", ""))
    except Exception as e:
        results.append(("plato-room-musician", "rooms.empty", "CRASH", str(e), traceback.format_exc()))


def test_prm_1000_rooms():
    from plato_room_musician.score import NoteEvent, PlatoScore
    try:
        events = []
        for i in range(1000):
            events.append(NoteEvent(
                room=f"room_{i}",
                channel=i % 16,
                pitch=60 + (i % 40),
                velocity=80,
                onset_beats=float(i) * 0.5,
                duration_beats=0.25,
                patch=0,
                agent="test-agent",
                category="session",
            ))
        score = PlatoScore(events=events)
        score.normalize_time()
        results.append(("plato-room-musician", "rooms.1000", "OK", f"events={len(score.events)}, dur={score.duration_beats}", ""))
    except Exception as e:
        results.append(("plato-room-musician", "rooms.1000", "CRASH", str(e), traceback.format_exc()))


def test_prm_unicode_room_names():
    from plato_room_musician.score import NoteEvent, PlatoScore
    try:
        events = [
            NoteEvent(room="部屋_🎵", channel=0, pitch=60, velocity=80,
                      onset_beats=0.0, duration_beats=1.0, patch=0,
                      agent="test", category="session"),
            NoteEvent(room="forge🔥", channel=1, pitch=64, velocity=80,
                      onset_beats=0.0, duration_beats=1.0, patch=0,
                      agent="test", category="session"),
        ]
        score = PlatoScore(events=events)
        score.normalize_time()
        results.append(("plato-room-musician", "rooms.unicode", "OK", f"events={len(score.events)}", ""))
    except Exception as e:
        results.append(("plato-room-musician", "rooms.unicode", "CRASH", str(e), traceback.format_exc()))


def test_prm_empty_room_name():
    from plato_room_musician.score import NoteEvent, PlatoScore
    try:
        events = [
            NoteEvent(room="", channel=0, pitch=60, velocity=80,
                      onset_beats=0.0, duration_beats=1.0, patch=0,
                      agent="test", category="session"),
        ]
        score = PlatoScore(events=events)
        score.normalize_time()
        results.append(("plato-room-musician", "rooms.empty_name", "OK", "Accepted empty room name", ""))
    except Exception as e:
        results.append(("plato-room-musician", "rooms.empty_name", "CRASH", str(e), traceback.format_exc()))


def test_prm_long_room_name():
    from plato_room_musician.score import NoteEvent, PlatoScore
    try:
        name = "x" * 10000
        events = [
            NoteEvent(room=name, channel=0, pitch=60, velocity=80,
                      onset_beats=0.0, duration_beats=1.0, patch=0,
                      agent="test", category="session"),
        ]
        score = PlatoScore(events=events)
        results.append(("plato-room-musician", "rooms.long_name", "OK", f"Accepted {len(name)}-char name", ""))
    except Exception as e:
        results.append(("plato-room-musician", "rooms.long_name", "CRASH", str(e), traceback.format_exc()))


def test_prm_negative_confidence():
    from plato_room_musician.mapping import TileMapper
    try:
        tm = TileMapper()
        tile = {
            "room": "test-room",
            "category": "session",
            "agent": "test-agent",
            "timestamp": 1000.0,
            "confidence": -0.5,
            "question": "Q",
            "answer": "A",
            "tile_id": "t1",
        }
        result = tm.map_tile("test-room", tile)
        results.append(("plato-room-musician", "tiles.neg_confidence", "SILENT", f"Accepted negative confidence, velocity={result['velocity']}", ""))
    except ValueError as e:
        results.append(("plato-room-musician", "tiles.neg_confidence", "OK", str(e), ""))
    except Exception as e:
        results.append(("plato-room-musician", "tiles.neg_confidence", "CRASH", str(e), traceback.format_exc()))


def test_prm_high_confidence():
    from plato_room_musician.mapping import TileMapper
    try:
        tm = TileMapper()
        tile = {
            "room": "test-room",
            "category": "session",
            "agent": "test-agent",
            "timestamp": 1000.0,
            "confidence": 1.5,
            "question": "Q",
            "answer": "A",
            "tile_id": "t1",
        }
        result = tm.map_tile("test-room", tile)
        results.append(("plato-room-musician", "tiles.high_confidence", "SILENT", f"Accepted confidence>1, velocity={result['velocity']}", ""))
    except ValueError as e:
        results.append(("plato-room-musician", "tiles.high_confidence", "OK", str(e), ""))
    except Exception as e:
        results.append(("plato-room-musician", "tiles.high_confidence", "CRASH", str(e), traceback.format_exc()))


def test_prm_missing_fields():
    from plato_room_musician.mapping import TileMapper
    # No fields
    try:
        tm = TileMapper()
        result = tm.map_tile("test-room", {})
        results.append(("plato-room-musician", "tiles.no_fields", "SILENT", f"Accepted empty tile", ""))
    except (KeyError, ValueError, TypeError) as e:
        results.append(("plato-room-musician", "tiles.no_fields", "OK", f"{type(e).__name__}: {str(e)[:80]}", ""))
    except Exception as e:
        results.append(("plato-room-musician", "tiles.no_fields", "CRASH", str(e), traceback.format_exc()))


def test_prm_extra_fields():
    from plato_room_musician.mapping import TileMapper
    try:
        tm = TileMapper()
        tile = {
            "room": "test-room",
            "category": "session",
            "agent": "test-agent",
            "timestamp": 1000.0,
            "confidence": 0.8,
            "question": "Q",
            "answer": "A",
            "tile_id": "t1",
            "extra_field": "should be ignored",
            "another": 42,
        }
        result = tm.map_tile("test-room", tile)
        results.append(("plato-room-musician", "tiles.extra_fields", "OK", "Extra fields ignored", ""))
    except Exception as e:
        results.append(("plato-room-musician", "tiles.extra_fields", "CRASH", str(e), traceback.format_exc()))


def test_prm_channel_collision():
    """Test with 20+ rooms but only 16 MIDI channels."""
    from plato_room_musician.mapping import RoomMapper
    try:
        rm = RoomMapper()
        rooms = [f"room_{i}" for i in range(20)]
        channels = set()
        for r in rooms:
            channels.add(rm.channel_for(r))
        results.append(("plato-room-musician", "channels.20_rooms", "OK",
                        f"20 rooms mapped to {len(channels)} unique channels (max 16)", ""))
    except Exception as e:
        results.append(("plato-room-musician", "channels.20_rooms", "CRASH", str(e), traceback.format_exc()))


def test_prm_renderer_empty():
    from plato_room_musician.score import PlatoScore
    from plato_room_musician.renderer import MidiRenderer
    try:
        score = PlatoScore(events=[])
        renderer = MidiRenderer()
        mid = renderer.render(score)
        results.append(("plato-room-musician", "renderer.empty_midi", "OK", f"tracks={len(mid.tracks)}", ""))
    except Exception as e:
        results.append(("plato-room-musician", "renderer.empty_midi", "CRASH", str(e), traceback.format_exc()))


def test_prm_renderer_tensor_empty():
    from plato_room_musician.score import PlatoScore
    from plato_room_musician.renderer import TensorMidiRenderer
    try:
        score = PlatoScore(events=[])
        renderer = TensorMidiRenderer()
        events = renderer.render(score)
        results.append(("plato-room-musician", "renderer.empty_tensor", "OK", f"events={len(events)}", ""))
    except Exception as e:
        results.append(("plato-room-musician", "renderer.empty_tensor", "CRASH", str(e), traceback.format_exc()))


def test_prm_synthetic_fetcher():
    from plato_room_musician.fetcher import SyntheticFetcher
    try:
        sf = SyntheticFetcher(seed=42)
        rooms = sf.get_rooms()
        results.append(("plato-room-musician", "fetcher.synthetic_rooms", "OK",
                        f"rooms={len(rooms)}", ""))
    except Exception as e:
        results.append(("plato-room-musician", "fetcher.synthetic_rooms", "CRASH", str(e), traceback.format_exc()))

    # get_room triggers tile generation which has format string bugs
    try:
        sf = SyntheticFetcher(seed=42)
        data = sf.get_room("forgemaster-cadence", limit=5)
        results.append(("plato-room-musician", "fetcher.synthetic_tiles", "OK",
                        f"tiles={len(data.get('tiles', []))}", ""))
    except Exception as e:
        results.append(("plato-room-musician", "fetcher.synthetic_tiles", "CRASH", str(e), traceback.format_exc()))

    # get_all_tiles - may crash due to format string bug
    try:
        sf = SyntheticFetcher(seed=42)
        all_tiles = sf.get_all_tiles()
        results.append(("plato-room-musician", "fetcher.synthetic_all", "OK",
                        f"total_tiles={sum(len(v) for v in all_tiles.values())}", ""))
    except Exception as e:
        results.append(("plato-room-musician", "fetcher.synthetic_all", "CRASH", str(e), traceback.format_exc()))


# ========================================================================
# RUN ALL TESTS
# ========================================================================

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(line_buffering=True)
    print("=" * 80)
    print("STRESS TEST SUITE - 6 Python Packages")
    print("=" * 80)

    # 1. Constraint-theory-core
    print("[1/6] constraint-theory-core", flush=True)
    test_ctc_lattice()
    test_ctc_temporal()
    test_ctc_rigidity()
    test_ctc_metronome()
    test_ctc_holonomy()

    # 2. Counterpoint-engine
    print("[2/6] counterpoint-engine", flush=True)
    test_ce_empty_cf()
    test_ce_1note_cf()
    test_ce_100note_cf()
    test_ce_all_same_note()
    test_ce_chromatic_cf()
    test_ce_random_cf()
    test_ce_invalid_species()
    test_ce_bad_key()
    test_ce_voice_range_overlap()

    # 3. Groove-analyzer
    print("[3/6] groove-analyzer", flush=True)
    test_ga_empty_midi()
    test_ga_metadata_only()
    test_ga_1_note()
    test_ga_10000_notes()
    test_ga_overlapping_notes()
    test_ga_extreme_bpm()
    test_ga_nonexistent_file()
    test_ga_corrupted_file()
    test_ga_grid_division()

    # 4. Holonomy-harmony
    print("[4/6] holonomy-harmony", flush=True)
    test_hh_empty_progression()
    test_hh_single_chord()
    test_hh_1000_chords()
    test_hh_all_same_chord()
    test_hh_random_chromatic()
    test_hh_invalid_roman()
    test_hh_invalid_key()
    test_hh_secondary_dominants()

    # 5. Spline-midi-smooth
    print("[5/6] spline-midi-smooth", flush=True)
    test_sms_0_points()
    test_sms_1_point()
    test_sms_2_identical_points()
    test_sms_10000_points()
    test_sms_non_increasing_x()
    test_sms_duplicate_x()
    test_sms_large_y()
    test_sms_nan_y()
    test_sms_inf_y()
    test_sms_tension_out_of_range()
    test_sms_bspline_degree()

    # 6. Plato-room-musician
    print("[6/6] plato-room-musician", flush=True)
    test_prm_empty_room_list()
    test_prm_1000_rooms()
    test_prm_unicode_room_names()
    test_prm_empty_room_name()
    test_prm_long_room_name()
    test_prm_negative_confidence()
    test_prm_high_confidence()
    test_prm_missing_fields()
    test_prm_extra_fields()
    test_prm_channel_collision()
    test_prm_renderer_empty()
    test_prm_renderer_tensor_empty()
    test_prm_synthetic_fetcher()

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    crashes = [r for r in results if r[2] == "CRASH"]
    silent = [r for r in results if r[2] == "SILENT"]
    ok = [r for r in results if r[2] == "OK"]
    bad_msgs = []  # Would need manual review

    print(f"\nTotal tests: {len(results)}")
    print(f"  OK (handled correctly): {len(ok)}")
    print(f"  CRASH (unhandled exception): {len(crashes)}")
    print(f"  SILENT (no error, should have one): {len(silent)}")

    if crashes:
        print("\n--- CRASHES ---")
        for pkg, name, sev, err, tb in crashes:
            print(f"\n[{pkg}] {name}")
            print(f"  Error: {err}")
            if tb:
                # Print last 3 lines of traceback
                lines = tb.strip().split('\n')
                for l in lines[-4:]:
                    print(f"  {l}")

    if silent:
        print("\n--- SILENT FAILURES (should have raised error) ---")
        for pkg, name, sev, err, tb in silent:
            print(f"  [{pkg}] {name}: {err}")

    print(f"\nDone. Writing report...")
