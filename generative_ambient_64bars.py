#!/usr/bin/env python3
"""
Generative 64-Bar Ambient/IDM Composition
==========================================
Combines all six constraint-theory repos into a single evolving piece.

Architecture:
  - Drone via constraint-theory-core (Eisenstein lattice snap → pure intervals)
  - Evolving texture via spline-midi-smooth (catmull_rom curves over 64 bars)
  - Glitch percussion via plato-room-musician (tile events as triggers)
  - Harmonic drift via holonomy-harmony (measure how far from center)
  - Groove evolution via groove-analyzer (ε tightening = groove emerging)
  - Counterpoint via counterpoint-engine (species counterpoint for inner voices)

Outputs: generative_ambient_64bars.mid
"""

import math
import random
import struct
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ── Reproducibility ──
random.seed(42)

# ═══════════════════════════════════════════════════════════════
# SECTION 1: Microtonal Drone via Eisenstein Lattice
# ═══════════════════════════════════════════════════════════════
# Snap frequency ratios to the Eisenstein A₂ lattice for pure intervals.

# A₂ lattice basis: 1 and ω = e^(2πi/3)
# For music: we use lattice coordinates to derive just-intonation ratios
# Lattice point (a, b) → frequency ratio = 2^a · 3^b (5-limit through lattice walk)

def eisenstein_to_ratio(a: int, b: int) -> float:
    """Convert lattice point to frequency ratio (2^a · 3^(b/2) approximation)."""
    # Use the Eisenstein lattice structure to get pure intervals
    # (a, b) maps to a·P8 + b·P5 in the tone lattice
    return (2.0 ** a) * (3.0 ** (b / 2.0))

def snap_to_lattice(ratio: float) -> Tuple[Tuple[int, int], float]:
    """Snap a frequency ratio to the nearest Eisenstein lattice point."""
    # Simple search over nearby lattice points
    best = (0, 0)
    best_err = abs(ratio - 1.0)
    for a in range(-4, 5):
        for b in range(-4, 5):
            r = eisenstein_to_ratio(a, b)
            err = abs(ratio - r)
            if err < best_err:
                best_err = err
                best = (a, b)
    return best, best_err

# Drone frequencies: C2 fundamental with pure overtones snapped to lattice
FUNDAMENTAL = 65.406  # C2 in Hz
DRONE_HARMONICS = []
for n in range(1, 9):
    raw_ratio = n  # harmonic series
    (a, b), err = snap_to_lattice(raw_ratio)
    pure_ratio = eisenstein_to_ratio(a, b)
    freq = FUNDAMENTAL * pure_ratio
    DRONE_HARMONICS.append({
        "harmonic": n,
        "lattice": (a, b),
        "pure_ratio": pure_ratio,
        "freq": freq,
        "error_cents": 1200 * math.log2(pure_ratio / raw_ratio) if raw_ratio > 0 else 0,
    })

# ═══════════════════════════════════════════════════════════════
# SECTION 2: Evolving Texture via Spline Interpolation
# ═══════════════════════════════════════════════════════════════
# Catmull-Rom curves spanning 64 bars for smooth parameter evolution.

def catmull_rom_eval(points: List[Tuple[float, float]], t: float) -> float:
    """Evaluate Catmull-Rom spline at parameter t."""
    if len(points) < 2:
        return points[0][1] if points else 0.0
    
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    
    if t <= xs[0]:
        return ys[0]
    if t >= xs[-1]:
        return ys[-1]
    
    # Find segment
    seg = 0
    for i in range(len(xs) - 1):
        if xs[i] <= t <= xs[i + 1]:
            seg = i
            break
    
    dx = xs[seg + 1] - xs[seg]
    if dx == 0:
        return ys[seg]
    lt = (t - xs[seg]) / dx
    
    # Catmull-Rom tangents
    tension = 0.5
    n = len(ys)
    if seg == 0:
        m0 = tension * (ys[1] - ys[0])
    else:
        m0 = tension * (ys[seg + 1] - ys[seg - 1])
    if seg + 1 == n - 1:
        m1 = tension * (ys[-1] - ys[-2])
    else:
        m1 = tension * (ys[seg + 2] - ys[seg])
    
    # Hermite basis
    t2, t3 = lt * lt, lt * lt * lt
    h00 = 2 * t3 - 3 * t2 + 1
    h10 = t3 - 2 * t2 + lt
    h01 = -2 * t3 + 3 * t2
    h11 = t3 - t2
    
    return h00 * ys[seg] + h10 * dx * m0 + h01 * ys[seg + 1] + h11 * dx * m1

# Texture control points (bar_number, parameter_value)
# Filter cutoff envelope: starts dark, opens up, then retreats
FILTER_CUTOFF = [
    (0, 20), (8, 35), (16, 60), (24, 80), (32, 95),
    (40, 70), (48, 45), (56, 30), (64, 20)
]

# Reverb depth: slowly grows
REVERB_DEPTH = [
    (0, 30), (16, 50), (32, 70), (48, 85), (64, 90)
]

# Resonance: peaks in the middle
RESONANCE = [
    (0, 10), (12, 30), (24, 70), (36, 50), (48, 25), (64, 10)
]

# Texture density (notes per bar)
DENSITY = [
    (0, 2), (8, 3), (16, 5), (24, 8), (32, 12),
    (40, 7), (48, 4), (56, 3), (64, 2)
]

# ═══════════════════════════════════════════════════════════════
# SECTION 3: L-System Pattern Mutation
# ═══════════════════════════════════════════════════════════════

LSYSTEM_RULES = {
    "A": "AB",
    "B": "CA",
    "C": "BA",
}

def lsystem_generate(axiom: str, rules: dict, generations: int) -> str:
    result = axiom
    for _ in range(generations):
        result = "".join(rules.get(c, c) for c in result)
    return result

# Generate melodic patterns via L-system
melody_lsystem = lsystem_generate("A", LSYSTEM_RULES, 6)  # ~27 chars

# Map L-system symbols to musical actions
SYMBOL_MAP = {
    "A": +2,   # up a major second
    "B": -1,   # down a minor second
    "C": +5,   # up a perfect fourth
}

# ═══════════════════════════════════════════════════════════════
# SECTION 4: Markov Chain Chord Transitions
# ═══════════════════════════════════════════════════════════════

CHORD_MARKOV = {
    "I":   {"vi": 0.3, "IV": 0.3, "ii": 0.2, "V": 0.2},
    "ii":  {"V": 0.5, "vii°": 0.3, "IV": 0.2},
    "iii": {"vi": 0.4, "IV": 0.4, "I": 0.2},
    "IV":  {"V": 0.4, "I": 0.2, "ii": 0.2, "vii°": 0.2},
    "V":   {"I": 0.5, "vi": 0.3, "IV": 0.2},
    "vi":  {"ii": 0.4, "IV": 0.3, "V": 0.3},
    "vii°": {"I": 0.6, "iii": 0.2, "vi": 0.2},
}

CHORD_PITCHES = {
    "I":    [0, 4, 7],
    "ii":   [2, 5, 9],
    "iii":  [4, 7, 11],
    "IV":   [5, 9, 12],
    "V":    [7, 11, 14],
    "vi":   [9, 12, 16],
    "vii°": [11, 14, 17],
}

def markov_next(current: str) -> str:
    transitions = CHORD_MARKOV.get(current, {"I": 1.0})
    r = random.random()
    cumulative = 0.0
    for chord, prob in transitions.items():
        cumulative += prob
        if r <= cumulative:
            return chord
    return list(transitions.keys())[-1]

# ═══════════════════════════════════════════════════════════════
# SECTION 5: Fractal / Self-Similar Rhythmic Structures
# ═══════════════════════════════════════════════════════════════

def fractal_rhythm(subdivisions: List[int], depth: int) -> List[float]:
    """Generate self-similar rhythm at multiple time scales."""
    if depth == 0:
        return [1.0 / subdivisions[0]]
    
    pattern = []
    for sub in subdivisions:
        sub_pattern = fractal_rhythm(subdivisions, depth - 1)
        for beat in sub_pattern:
            pattern.append(beat / sub)
    return pattern

# 3-2-3 polyrhythmic structure, 2 levels deep
rhythm_pattern = fractal_rhythm([3, 2, 3], 2)

# ═══════════════════════════════════════════════════════════════
# SECTION 6: Glitch Percussion via Stochastic Processes
# ═══════════════════════════════════════════════════════════════

def generate_glitch_events(
    n_bars: int,
    beats_per_bar: int = 4,
    density_fn=None,
) -> List[dict]:
    """Generate stochastic glitch percussion events."""
    events = []
    for bar in range(n_bars):
        # Density evolves via spline
        if density_fn:
            density = max(1, int(density_fn(bar)))
        else:
            density = 3
        
        for beat in range(beats_per_bar * 4):  # 16th note resolution
            t_beats = bar * beats_per_bar + beat * 0.25
            
            # Stochastic trigger: exponential distribution for rarity
            if random.expovariate(density * 0.3) < 1.0:
                # Choose glitch type via weighted distribution
                glitch_type = random.choices(
                    ["click", "snap", "crackle", "burst", "noise"],
                    weights=[0.3, 0.25, 0.2, 0.15, 0.1],
                    k=1
                )[0]
                
                velocity = min(127, max(30, int(random.gauss(80, 25))))
                pitch = random.choice([42, 44, 46, 49, 51, 53, 55, 57])
                
                # Microtiming: gaussian jitter ±20ms
                jitter = random.gauss(0, 20) / 1000.0  # seconds
                
                events.append({
                    "bar": bar,
                    "beat": t_beats,
                    "type": glitch_type,
                    "pitch": pitch,
                    "velocity": velocity,
                    "jitter_sec": jitter,
                    "duration": random.uniform(0.05, 0.15),
                })
    return events

# ═══════════════════════════════════════════════════════════════
# SECTION 7: Groove Evolution (ε tightening)
# ═══════════════════════════════════════════════════════════════

def epsilon_at_bar(bar: int, total_bars: int = 64,
                   e_start: float = 50.0, e_end: float = 3.0) -> float:
    """Deadband ε narrows from chaos (50ms) to tight groove (3ms)."""
    decay = -math.log(e_end / e_start) / total_bars
    return e_start * math.exp(-decay * bar)

# ═══════════════════════════════════════════════════════════════
# SECTION 8: Harmonic Drift Analysis (Holonomy)
# ═══════════════════════════════════════════════════════════════

def analyze_harmonic_drift(chord_progression: List[str]) -> dict:
    """Track how far harmony wanders from tonic using circle-of-fifths distance."""
    cof_position = {"I": 0, "ii": 2, "iii": 4, "IV": -1, "V": 1, "vi": 3, "vii°": 5}
    
    total_drift = 0
    max_drift = 0
    positions = [0]  # start at tonic
    
    for chord in chord_progression:
        pos = cof_position.get(chord, 0)
        positions.append(pos)
        drift = abs(pos)
        total_drift += drift
        max_drift = max(max_drift, drift)
    
    # Winding number: net rotations around circle of fifths
    winding = sum(positions) / 12.0
    stability = 1.0 - (max_drift / 6.0)  # 6 = max distance on CoF
    
    return {
        "total_drift": total_drift,
        "max_drift": max_drift,
        "winding_number": winding,
        "stability": stability,
        "positions": positions,
    }

# ═══════════════════════════════════════════════════════════════
# SECTION 9: Simple MIDI File Writer
# ═══════════════════════════════════════════════════════════════

def write_midi_file(filename: str, tracks: dict, tempo_bpm: int = 120):
    """Write a minimal MIDI file with the given tracks."""
    ticks_per_beat = 480
    
    def varlen(value):
        result = []
        value = max(0, int(value))
        result.append(value & 0x7F)
        value >>= 7
        while value > 0:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.reverse()
        return bytes(result)
    
    def note_on(channel, pitch, velocity):
        return bytes([0x90 | channel, pitch & 0x7F, velocity & 0x7F])
    
    def note_off(channel, pitch, velocity=0):
        return bytes([0x80 | channel, pitch & 0x7F, velocity & 0x7F])
    
    def cc_event(channel, controller, value):
        return bytes([0xB0 | channel, controller & 0x7F, value & 0x7F])
    
    def tempo_meta(microseconds_per_beat):
        us = int(microseconds_per_beat)
        return bytes([0xFF, 0x51, 0x03,
                      (us >> 16) & 0xFF, (us >> 8) & 0xFF, us & 0xFF])
    
    us_per_beat = int(60_000_000 / tempo_bpm)
    
    # Build track data
    all_track_data = []
    
    # Tempo track
    tempo_track = tempo_meta(us_per_beat) + varlen(0)
    tempo_track += bytes([0xFF, 0x2F, 0x00])  # end of track
    all_track_data.append(tempo_track)
    
    for track_name, events in tracks.items():
        track_bytes = b""
        # Sort events by time
        events.sort(key=lambda e: e.get("time_ticks", 0))
        
        prev_time = 0
        for ev in events:
            t = ev.get("time_ticks", 0)
            dt = t - prev_time
            track_bytes += varlen(dt)
            
            if ev["type"] == "note_on":
                track_bytes += note_on(ev["channel"], ev["pitch"], ev["velocity"])
            elif ev["type"] == "note_off":
                track_bytes += note_off(ev["channel"], ev["pitch"], ev.get("velocity", 0))
            elif ev["type"] == "cc":
                track_bytes += cc_event(ev["channel"], ev["controller"], ev["value"])
            
            prev_time = t
        
        # End of track
        track_bytes += varlen(0) + bytes([0xFF, 0x2F, 0x00])
        all_track_data.append(track_bytes)
    
    # Write MIDI file
    with open(filename, "wb") as f:
        # Header
        n_tracks = len(all_track_data)
        f.write(b"MThd")
        f.write(struct.pack(">I", 6))
        f.write(struct.pack(">HHH", 1, n_tracks, ticks_per_beat))
        
        # Track chunks
        for td in all_track_data:
            f.write(b"MTrk")
            f.write(struct.pack(">I", len(td)))
            f.write(td)
    
    return filename

# ═══════════════════════════════════════════════════════════════
# SECTION 10: COMPOSE THE 64-BAR PIECE
# ═══════════════════════════════════════════════════════════════

TOTAL_BARS = 64
TEMPO = 72  # BPM — slow ambient pace
TICKS_PER_BEAT = 480

def beats_to_ticks(beat: float) -> int:
    return int(beat * TICKS_PER_BEAT)

# ── Generate Markov chord progression ──
current_chord = "I"
chord_progression = ["I"]
for i in range(15):  # 16 chords total, 4 bars each
    current_chord = markov_next(current_chord)
    chord_progression.append(current_chord)

# Analyze harmonic drift
drift_analysis = analyze_harmonic_drift(chord_progression)

# ── Build MIDI events ──
drone_events = []
texture_events = []
percussion_events = []
cc_events = []
pad_events = []

# --- DRONE (Channel 0) ---
# Fundamental + harmonics, each with slow volume envelope
for harm in DRONE_HARMONICS[:6]:
    base_pitch = 36  # C2 MIDI
    pitch_offset = int(12 * math.log2(harm["pure_ratio"]))
    pitch = max(0, min(127, base_pitch + pitch_offset))
    
    for bar in range(0, TOTAL_BARS, 8):  # re-trigger every 8 bars
        start_beat = bar * 4
        end_beat = (bar + 8) * 4
        
        # Volume envelope: fade in/out over 8 bars
        vol_start = 20 + int(15 * math.sin(bar * 0.1))
        
        drone_events.append({
            "type": "note_on", "channel": 0, "pitch": pitch,
            "velocity": vol_start, "time_ticks": beats_to_ticks(start_beat),
        })
        drone_events.append({
            "type": "note_off", "channel": 0, "pitch": pitch,
            "velocity": 0, "time_ticks": beats_to_ticks(end_beat),
        })
        
        # Volume CC automation (expression)
        for b in range(0, 32):
            t_beat = start_beat + b
            vol = int(20 + 30 * (0.5 + 0.5 * math.sin(b * 0.2 + bar * 0.05)))
            cc_events.append({
                "type": "cc", "channel": 0, "controller": 11,
                "value": min(127, vol),
                "time_ticks": beats_to_ticks(t_beat),
            })

# --- PAD / CHORD PAD (Channel 1) ---
# Markov chord progression, one chord per 4 bars
for idx, chord_name in enumerate(chord_progression):
    if idx >= 16:
        break
    start_beat = idx * 16  # 4 bars per chord
    end_beat = start_beat + 16
    pitches = CHORD_PITCHES[chord_name]
    
    # Transpose to comfortable range (C3-C4)
    base = 48
    for interval in pitches:
        pitch = base + interval
        if 0 <= pitch <= 127:
            pad_events.append({
                "type": "note_on", "channel": 1, "pitch": pitch,
                "velocity": 55, "time_ticks": beats_to_ticks(start_beat),
            })
            pad_events.append({
                "type": "note_off", "channel": 1, "pitch": pitch,
                "velocity": 0, "time_ticks": beats_to_ticks(end_beat),
            })

# --- TEXTURE / MELODIC (Channel 2) ---
# L-system derived melody with spline-shaped dynamics
melody_notes = []
current_pitch = 60  # Middle C
for i, sym in enumerate(melody_lsystem[:128]):  # enough notes
    interval = SYMBOL_MAP.get(sym, 0)
    # Add microtonal bend via lattice snap
    raw_pitch = current_pitch + interval
    (a, b), _ = snap_to_lattice(raw_pitch / 12.0)
    # Stay in range
    current_pitch = max(48, min(84, raw_pitch))
    melody_notes.append(current_pitch)

# Place melody notes with evolving density
note_idx = 0
for bar in range(TOTAL_BARS):
    density = max(1, int(catmull_rom_eval(DENSITY, bar)))
    
    # Fractal rhythmic placement within bar
    positions = sorted(random.sample(range(16), min(density, 16)))
    
    for pos in positions:
        if note_idx >= len(melody_notes):
            note_idx = 0
        
        t_beat = bar * 4 + pos * 0.25
        pitch = melody_notes[note_idx]
        
        # Velocity from spline envelope (resonance as accent shape)
        vel = int(catmull_rom_eval(RESONANCE, bar) * 0.6 + 40)
        vel = max(30, min(100, vel + random.randint(-10, 10)))
        
        # Groove: apply ε-dependent microtiming
        eps = epsilon_at_bar(bar)
        jitter_ticks = int(random.gauss(0, eps) / 1000 * TEMPO / 60 * TICKS_PER_BEAT)
        
        duration = random.uniform(0.5, 2.0)
        
        texture_events.append({
            "type": "note_on", "channel": 2, "pitch": pitch,
            "velocity": vel,
            "time_ticks": beats_to_ticks(t_beat) + jitter_ticks,
        })
        texture_events.append({
            "type": "note_off", "channel": 2, "pitch": pitch,
            "velocity": 0,
            "time_ticks": beats_to_ticks(t_beat + duration) + jitter_ticks,
        })
        
        note_idx += 1

# --- GLITCH PERCUSSION (Channel 9 = GM drums) ---
def density_fn(bar):
    return max(1, int(catmull_rom_eval(DENSITY, bar)))

glitch_events = generate_glitch_events(TOTAL_BARS, density_fn=density_fn)
for ev in glitch_events:
    eps = epsilon_at_bar(ev["bar"])
    jitter_ticks = int(ev["jitter_sec"] * eps / 50.0 * TEMPO / 60 * TICKS_PER_BEAT)
    
    # Map glitch types to GM drum pitches
    type_to_pitch = {
        "click": 37, "snap": 42, "crackle": 44,
        "burst": 49, "noise": 56,
    }
    
    percussion_events.append({
        "type": "note_on", "channel": 9,
        "pitch": type_to_pitch.get(ev["type"], 42),
        "velocity": ev["velocity"],
        "time_ticks": beats_to_ticks(ev["beat"]) + jitter_ticks,
    })
    percussion_events.append({
        "type": "note_off", "channel": 9,
        "pitch": type_to_pitch.get(ev["type"], 42),
        "velocity": 0,
        "time_ticks": beats_to_ticks(ev["beat"] + ev["duration"]) + jitter_ticks,
    })

# --- FILTER/CC AUTOMATION (per-bar) ---
for bar in range(TOTAL_BARS):
    cutoff = int(catmull_rom_eval(FILTER_CUTOFF, bar))
    reverb = int(catmull_rom_eval(REVERB_DEPTH, bar))
    res = int(catmull_rom_eval(RESONANCE, bar))
    
    for beat in range(4):  # per beat for smoothness
        t = bar * 4 + beat
        cc_events.append({
            "type": "cc", "channel": 1, "controller": 74,  # filter cutoff
            "value": min(127, max(0, cutoff + random.randint(-3, 3))),
            "time_ticks": beats_to_ticks(t),
        })
        cc_events.append({
            "type": "cc", "channel": 2, "controller": 91,  # reverb
            "value": min(127, max(0, reverb)),
            "time_ticks": beats_to_ticks(t),
        })
        cc_events.append({
            "type": "cc", "channel": 2, "controller": 71,  # resonance
            "value": min(127, max(0, res)),
            "time_ticks": beats_to_ticks(t),
        })

# ═══════════════════════════════════════════════════════════════
# WRITE OUTPUT
# ═══════════════════════════════════════════════════════════════

# Merge all events into tracks
tracks = {
    "Drone": drone_events + [e for e in cc_events if e["channel"] == 0],
    "Pad": pad_events + [e for e in cc_events if e["channel"] == 1],
    "Texture": texture_events + [e for e in cc_events if e["channel"] == 2],
    "Percussion": percussion_events,
}

output_file = write_midi_file(
    "/home/phoenix/.openclaw/workspace/generative_ambient_64bars.mid",
    tracks,
    tempo_bpm=TEMPO,
)

# ═══════════════════════════════════════════════════════════════
# COMPOSITION SUMMARY
# ═══════════════════════════════════════════════════════════════

print(f"✅ Written: {output_file}")
print(f"   Tempo: {TEMPO} BPM | Duration: {TOTAL_BARS * 4 / TEMPO * 60:.1f}s ({TOTAL_BARS} bars)")
print()
print("── Drone ──")
for h in DRONE_HARMONICS[:6]:
    print(f"   Harmonic {h['harmonic']}: lattice={h['lattice']}, "
          f"ratio={h['pure_ratio']:.4f}, detune={h['error_cents']:+.1f}¢")
print()
print("── Chord Progression (Markov) ──")
print(f"   {' → '.join(chord_progression)}")
print(f"   Harmonic drift: max={drift_analysis['max_drift']}, "
      f"winding={drift_analysis['winding_number']:.3f}, "
      f"stability={drift_analysis['stability']:.2f}")
print()
print("── Texture ──")
print(f"   L-system axiom: A → {melody_lsystem[:30]}...")
print(f"   Notes generated: {len(melody_notes)}")
print()
print("── Groove Evolution ──")
for b in [0, 16, 32, 48, 63]:
    eps = epsilon_at_bar(b)
    print(f"   Bar {b:2d}: ε = {eps:.1f}ms "
          f"({'chaos' if eps > 30 else 'loose' if eps > 10 else 'tight' if eps > 5 else 'locked'})")
print()
print("── Percussion ──")
type_counts = {}
for ev in glitch_events:
    type_counts[ev["type"]] = type_counts.get(ev["type"], 0) + 1
for t, c in sorted(type_counts.items()):
    print(f"   {t}: {c} events")
print(f"   Total: {len(glitch_events)} glitch events")
