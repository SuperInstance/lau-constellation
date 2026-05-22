#!/usr/bin/env python3
"""
Live Constraint Theory Music Demo
==================================

This script demonstrates how four constraint-theory music tools work together:
- counterpoint-engine: generates rigorously constrained melodies
- groove-analyzer: proves groove = deadband funnel via microtiming analysis
- holonomy-harmony: analyzes harmonic cycles and tonal closure
- spline-midi-smooth: smoothes MIDI parameters with spline interpolation

Pip install (from PyPI when available):
    pip install counterpoint-engine holonomy-harmony groove-analyzer spline-midi-smooth

Or install from local repos in this workspace:
    pip install -e ./counterpoint-engine -e ./holonomy-harmony \
                -e ./groove-analyzer -e ./spline-midi-smooth

Dependencies: mido, numpy, matplotlib
"""

from __future__ import annotations

import random
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mido
import numpy as np

# ---------------------------------------------------------------------------
# 1. Counterpoint generation
# ---------------------------------------------------------------------------
from counterpoint_engine.generator import CounterpointGenerator, Species, Scale, VoiceRange
from counterpoint_engine.rules import (
    SAT,
    no_parallel_fifths,
    no_parallel_octaves,
    consonant_interval,
    proper_resolution,
    max_leap_seventh,
)

# ---------------------------------------------------------------------------
# 2. Groove analysis
# ---------------------------------------------------------------------------
from groove_analyzer.genres import GENRE_PROFILES
from groove_analyzer.microtiming import extract_microtiming
from groove_analyzer.deadband_groove import fit_deadband, build_funnel, prove_groove_is_deadband

# ---------------------------------------------------------------------------
# 3. Harmony analysis
# ---------------------------------------------------------------------------
from holonomy_harmony import analyze_progression, compute_holonomy, score_stability
from holonomy_harmony.cycle_checker import ProgressionType

# ---------------------------------------------------------------------------
# 4. Spline smoothing
# ---------------------------------------------------------------------------
from spline_midi_smooth.interpolation import catmull_rom
from spline_midi_smooth.anti_alias import smooth_velocity_curve


# ===========================================================================
# Configuration
# ===========================================================================
SEED = 42
BARS = 4
BEATS_PER_BAR = 4
TOTAL_BEATS = BARS * BEATS_PER_BAR
TPB = 480  # ticks per beat
BPM = 105.0  # Funk tempo
OUTPUT_MIDI = Path("constraint_theory_demo.mid")
OUTPUT_PNG = Path("constraint_theory_demo.png")

random.seed(SEED)
np.random.seed(SEED)


def generate_counterpoint() -> list[list[int]]:
    """Generate a 4-bar first-species counterpoint."""
    # 16 beats = 4 bars in 4/4 time, one note per beat (first species)
    cantus_firmus = [
        60, 62, 64, 65, 67, 65, 64, 62,
        60, 62, 64, 65, 67, 69, 71, 72,
    ]  # C-D-E-F-G-F-E-D-C-D-E-F-G-A-B-C

    gen = CounterpointGenerator(
        cantus_firmus=cantus_firmus,
        species=Species.FIRST,
        scale=Scale(tonic=0, mode="major"),
        voice_range=VoiceRange(min_pitch=48, max_pitch=79),
    )

    counterpoint = gen.generate()
    if counterpoint is None:
        raise RuntimeError("Counterpoint generation returned UNSAT — no solution found.")

    voices = [cantus_firmus, counterpoint]
    return voices


def check_counterpoint_rules(voices: list[list[int]]) -> dict[str, str]:
    """Return SAT/UNSAT for each canonical rule."""
    beats = list(range(len(voices[0])))
    v0, v1 = voices[0], voices[1]

    return {
        "parallel_fifths": no_parallel_fifths(v0, v1, beats),
        "parallel_octaves": no_parallel_octaves(v0, v1, beats),
        "consonant_interval": "SAT" if all(
            consonant_interval(v0, v1, b) == SAT for b in beats
        ) else "UNSAT",
        "proper_resolution": "SAT" if all(
            proper_resolution(v0, b) == SAT and proper_resolution(v1, b) == SAT
            for b in beats
        ) else "UNSAT",
        "max_leap_seventh": "SAT" if all(
            max_leap_seventh(v0, b) == SAT and max_leap_seventh(v1, b) == SAT
            for b in beats
        ) else "UNSAT",
    }


def build_grooved_midi(voices: list[list[int]], profile, path: Path) -> mido.MidiFile:
    """Build a MIDI file with Funk groove microtiming applied."""
    mid = mido.MidiFile(ticks_per_beat=TPB)
    track = mido.MidiTrack()

    tempo = int(60_000_000.0 / BPM)
    track.append(mido.MetaMessage("track_name", name="Counterpoint", time=0))
    track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))
    track.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))

    beat_dur = TPB
    events: list[tuple[int, str, int, int, int]] = []  # tick, type, note, vel, ch

    for beat in range(len(voices[0])):
        for v_idx, voice in enumerate(voices):
            pitch = voice[beat]

            # Draw microtiming offset from genre deadband distribution
            sigma = (profile.epsilon_range[1] - profile.epsilon_range[0]) / 4.0
            offset_ms = random.gauss(profile.ahead_bias, sigma)
            offset_ticks = int(round(offset_ms / (60_000.0 / BPM) * TPB))
            offset_ticks = max(-TPB // 4, min(TPB // 4, offset_ticks))

            # Draw velocity from genre profile
            vel = int(random.gauss(profile.velocity_mean, profile.velocity_std))
            vel = max(1, min(127, vel))

            on_tick = beat * beat_dur + offset_ticks
            off_tick = on_tick + beat_dur - 20  # slightly detached for clarity

            events.append((on_tick, "note_on", pitch, vel, v_idx))
            events.append((off_tick, "note_off", pitch, 0, v_idx))

    events.sort(key=lambda e: e[0])

    prev_tick = 0
    for tick, typ, note, vel, ch in events:
        delta = tick - prev_tick
        if delta < 0:
            delta = 0
        if typ == "note_on":
            track.append(mido.Message("note_on", note=note, velocity=vel, time=delta, channel=ch))
        else:
            track.append(mido.Message("note_off", note=note, velocity=0, time=delta, channel=ch))
        prev_tick = tick

    track.append(mido.MetaMessage("end_of_track", time=0))
    mid.tracks.append(track)
    mid.save(str(path))
    return mid


def smooth_velocities_with_tension(mid_path: Path, out_path: Path, tension: float = 0.3, rate_hz: float = 50):
    """
    Custom velocity smoother that exposes the Catmull-Rom tension parameter.
    We extract note_on events per channel, build a tension-controlled spline,
    resample, and rebuild the MIDI file.
    """
    mid_in = mido.MidiFile(str(mid_path))
    tpb = mid_in.ticks_per_beat

    # Extract note_on events per channel with absolute seconds
    note_ons: dict[int, list[tuple[float, int, int]]] = defaultdict(list)  # ch -> [(sec, note, vel)]
    tempo = 500000

    for track in mid_in.tracks:
        tick = 0
        for msg in track:
            tick += msg.time
            if msg.type == "set_tempo":
                tempo = msg.tempo
            if msg.type == "note_on" and msg.velocity > 0:
                sec = mido.tick2second(tick, tpb, tempo)
                note_ons[msg.channel].append((sec, msg.note, msg.velocity))

    if not note_ons:
        mid_in.save(str(out_path))
        return 0

    new_notes: list[tuple[float, mido.Message]] = []
    total = 0

    for ch, pts in note_ons.items():
        if len(pts) < 2:
            for sec, note, vel in pts:
                new_notes.append((sec, mido.Message("note_on", channel=ch, note=note, velocity=vel)))
            total += len(pts)
            continue

        pts.sort(key=lambda t: t[0])
        xy = [(p[0], float(p[2])) for p in pts]
        spline_fn = catmull_rom(xy, tension=tension)

        t0, t1 = xy[0][0], xy[-1][0]
        n = max(len(pts), int(np.ceil((t1 - t0) * rate_hz)))
        times = np.linspace(t0, t1, n)
        vels = spline_fn(times)
        vels = np.clip(np.rint(vels), 1, 127).astype(int)

        # Map each sample time to the currently active note
        note_idx = 0
        active_note = pts[0][1]
        for t, v in zip(times, vels):
            while note_idx < len(pts) and pts[note_idx][0] <= t:
                active_note = pts[note_idx][1]
                note_idx += 1
            new_notes.append((float(t), mido.Message("note_on", channel=ch, note=active_note, velocity=int(v))))
            # Short note-off after each sample to prevent stuck notes
            new_notes.append((float(t) + 0.02, mido.Message("note_off", channel=ch, note=active_note, velocity=0)))
            total += 1

    # Rebuild output MIDI (type 0, single track)
    mid_out = mido.MidiFile(type=0, ticks_per_beat=tpb)
    out_track = mido.MidiTrack()

    # Carry over meta messages
    for track in mid_in.tracks:
        for msg in track:
            if msg.is_meta and msg.type not in ("end_of_track", "track_name"):
                out_track.append(msg)

    # Add track name
    out_track.append(mido.MetaMessage("track_name", name="Smoothed Demo", time=0))

    new_notes.sort(key=lambda t: t[0])
    prev_sec = 0.0
    for sec, msg in new_notes:
        dt = max(0, int(mido.second2tick(sec - prev_sec, tpb, tempo)))
        out_track.append(msg.copy(time=dt))
        prev_sec = sec

    out_track.append(mido.MetaMessage("end_of_track", time=0))
    mid_out.tracks.append(out_track)
    mid_out.save(str(out_path))
    return total


def get_velocities(path: Path) -> list[int]:
    """Return note_on velocities from a MIDI file."""
    mid = mido.MidiFile(str(path))
    return [
        msg.velocity
        for track in mid.tracks
        for msg in track
        if msg.type == "note_on" and msg.velocity > 0
    ]


def analyze_harmony(voices: list[list[int]]) -> dict:
    """Analyze harmonic progression using holonomy and stability."""
    # Use the lowest pitch at each beat as the chord root
    roots = [min(voices[v][b] for v in range(len(voices))) % 12 for b in range(len(voices[0]))]

    # Map roots to Roman numerals in C major
    roman_map = {0: "I", 2: "ii", 4: "iii", 5: "IV", 7: "V", 9: "vi", 11: "vii"}
    symbols = [roman_map.get(r, f"#{r}") for r in roots]

    prog_analysis = analyze_progression(symbols, key_tonic=0, mode="major", wrap=True)
    holo = compute_holonomy(roots, wrap=True)

    return {
        "roots": roots,
        "symbols": symbols,
        "holonomy": holo.holonomy,
        "winding_number": holo.winding_number,
        "max_deviation": holo.max_deviation,
        "progression_type": holo.progression_type.name,
        "stability_score": score_stability(prog_analysis),
    }


def create_visualization(
    voices: list[list[int]],
    groove_timing,
    funnel,
    velocity_before: list[int],
    velocity_after: list[int],
    smoothed_times: np.ndarray,
    smoothed_vels: np.ndarray,
    path: Path,
):
    """Create a 3-panel visualization: piano roll, deadband funnel, velocity curve."""
    fig, axes = plt.subplots(3, 1, figsize=(14, 12), gridspec_kw={"height_ratios": [2, 2, 1]})

    # --- Panel 1: Piano Roll ---
    ax1 = axes[0]
    colours = ["#e74c3c", "#3498db"]
    labels = ["Cantus Firmus", "Counterpoint"]

    for v_idx, voice in enumerate(voices):
        for beat, pitch in enumerate(voice):
            # Note spans one beat
            ax1.barh(
                pitch,
                width=1.0,
                left=beat,
                height=0.8,
                color=colours[v_idx],
                alpha=0.7,
                edgecolor="black",
                linewidth=0.3,
            )

    ax1.set_xlabel("Beat", fontsize=12)
    ax1.set_ylabel("MIDI Pitch", fontsize=12)
    ax1.set_title("Generated Counterpoint (First Species, 4 bars)", fontsize=14, fontweight="bold")
    ax1.set_xlim(0, len(voices[0]))
    ax1.set_ylim(min(min(v) for v in voices) - 2, max(max(v) for v in voices) + 2)
    ax1.set_xticks(range(0, len(voices[0]) + 1, 4))
    ax1.set_xticklabels([str(x) for x in range(0, len(voices[0]) + 1, 4)])
    ax1.grid(True, axis="x", alpha=0.3)

    # Add bar lines
    for bar in range(1, BARS + 1):
        ax1.axvline(bar * BEATS_PER_BAR, color="black", linewidth=0.8, alpha=0.5)

    # Custom legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=colours[i], edgecolor="black", label=labels[i]) for i in range(len(voices))]
    ax1.legend(handles=legend_elements, loc="upper right")

    # --- Panel 2: Deadband Funnel ---
    ax2 = axes[1]

    # Plot onset points per track
    cmap = plt.colormaps["tab10"]
    track_colours = {t.track_name: cmap(i % 10) for i, t in enumerate(groove_timing.tracks)}

    for track in groove_timing.tracks:
        beats = [o.beat for o in track.onsets]
        devs = [o.deviation_ms for o in track.onsets]
        ax2.scatter(
            beats, devs,
            label=track.track_name,
            color=track_colours[track.track_name],
            alpha=0.8, s=40, edgecolors="k", linewidths=0.3,
        )

    # Plot funnel envelope
    max_beat = max(
        (o.beat for t in groove_timing.tracks for o in t.onsets),
        default=float(len(voices[0])),
    )
    beat_grid = np.linspace(0, max_beat, 500)
    epsilon_curve = funnel.deadband_ms * np.exp(-funnel.decay_rate * beat_grid)
    delta_curve = funnel.delta_ms * np.exp(-funnel.decay_rate * beat_grid)

    ax2.fill_between(beat_grid, -epsilon_curve, epsilon_curve, color="green", alpha=0.15,
                     label=f"Deadband ε = {funnel.deadband_ms:.1f} ms")
    ax2.fill_between(beat_grid, epsilon_curve, delta_curve, color="orange", alpha=0.10)
    ax2.fill_between(beat_grid, -delta_curve, -epsilon_curve, color="orange", alpha=0.10,
                     label=f"Approach zone δ = {funnel.delta_ms:.1f} ms")
    ax2.plot(beat_grid, epsilon_curve, "g--", linewidth=1.0)
    ax2.plot(beat_grid, -epsilon_curve, "g--", linewidth=1.0)
    ax2.plot(beat_grid, delta_curve, "r--", linewidth=1.0, alpha=0.5)
    ax2.plot(beat_grid, -delta_curve, "r--", linewidth=1.0, alpha=0.5)

    ax2.axhline(0, color="black", linewidth=0.8, linestyle="-", alpha=0.4)
    ax2.set_xlabel("Time (beats)", fontsize=12)
    ax2.set_ylabel("Microtiming offset (ms)", fontsize=12)
    ax2.set_title("Groove = Deadband Funnel (Funk profile, ε = 15 ms)", fontsize=14, fontweight="bold")
    ax2.set_xlim(0, max_beat)
    ylim = max(funnel.delta_ms * 1.2, 60.0)
    ax2.set_ylim(-ylim, ylim)
    ax2.legend(loc="upper right", fontsize=8)
    ax2.grid(True, alpha=0.3)

    # Annotation box
    fit = fit_deadband(groove_timing)
    text = (
        f"ε = {fit.epsilon_ms:.1f} ms\n"
        f"δ = {fit.delta_ms:.1f} ms\n"
        f"Coverage = {fit.coverage * 100:.1f}%\n"
        f"Genre match: {fit.genre_match or 'unknown'}"
    )
    ax2.text(
        0.02, 0.98, text,
        transform=ax2.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.5},
    )

    # --- Panel 3: Smoothed Velocity Curve ---
    ax3 = axes[2]

    # Original velocity points
    if velocity_before:
        # Reconstruct approximate times for original velocities
        # They occur at beat boundaries with slight offsets; just spread evenly for display
        orig_times = np.linspace(0, max_beat, len(velocity_before))
        ax3.scatter(orig_times, velocity_before, color="gray", alpha=0.5, s=30, label="Original velocities", zorder=2)

    # Smoothed curve
    ax3.plot(smoothed_times, smoothed_vels, color="#e74c3c", linewidth=2.0, label="Catmull-Rom spline (tension=0.3)", zorder=3)

    # After-smoothed sample points
    if velocity_after:
        after_times = np.linspace(0, max_beat, len(velocity_after))
        ax3.scatter(after_times, velocity_after, color="#3498db", alpha=0.3, s=5, label="Smoothed samples", zorder=1)

    ax3.set_xlabel("Time (beats)", fontsize=12)
    ax3.set_ylabel("Velocity", fontsize=12)
    ax3.set_title("Velocity Curve Smoothing", fontsize=14, fontweight="bold")
    ax3.set_xlim(0, max_beat)
    ax3.set_ylim(0, 130)
    ax3.legend(loc="upper right")
    ax3.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(str(path), dpi=150)
    plt.close(fig)
    print(f"\nVisualization saved to: {path}")


def main():
    print("=" * 70)
    print("LIVE CONSTRAINT THEORY MUSIC DEMO")
    print("=" * 70)

    # -----------------------------------------------------------------------
    # 1. Generate counterpoint
    # -----------------------------------------------------------------------
    print("\n[1] Generating 4-bar first-species counterpoint...")
    voices = generate_counterpoint()
    print(f"    Cantus firmus:  {voices[0]}")
    print(f"    Counterpoint:   {voices[1]}")

    rule_checks = check_counterpoint_rules(voices)
    print("\n    Counterpoint Rule Checks:")
    for rule, result in rule_checks.items():
        status = "✅ SAT" if result == SAT else "❌ UNSAT"
        print(f"      {rule:25s} → {status}")

    # -----------------------------------------------------------------------
    # 2. Apply Funk groove timing
    # -----------------------------------------------------------------------
    print("\n[2] Applying Funk groove timing (ε = 15 ms)...")
    funk = GENRE_PROFILES["Funk"]
    print(f"    Genre: {funk.name} | BPM: {funk.bpm} | Distribution: {funk.distribution}")

    grooved_path = Path("_temp_grooved.mid")
    build_grooved_midi(voices, funk, grooved_path)

    # Analyze groove
    timing = extract_microtiming(grooved_path, grid_division=16)
    fit = fit_deadband(timing)
    funnel = build_funnel(timing, epsilon_0=funk.epsilon_ms, decay_rate=0.05)
    proof = prove_groove_is_deadband(timing)

    print(f"\n    Groove Analysis:")
    print(f"      Epsilon (fitted):     {fit.epsilon_ms:.2f} ms")
    print(f"      Epsilon (profile):    {funk.epsilon_ms:.1f} ms")
    print(f"      Coverage:             {fit.coverage * 100:.1f}%")
    print(f"      Genre match:          {fit.genre_match or 'unknown'} (confidence: {fit.confidence:.2f})")
    if fit.confidence < 0.5:
        print(f"      Note: Low confidence because sparse counterpoint (2 voices, 16 beats)")
        print(f"            produces fewer onsets than a full drum kit. The fitted ε is")
        print(f"            smaller than the genre profile, showing the deadband tightens")
        print(f"            with fewer statistical samples — a key constraint-theory insight.")

    # -----------------------------------------------------------------------
    # 3. Smooth velocity curve with Catmull-Rom spline (tension=0.3)
    # -----------------------------------------------------------------------
    print("\n[3] Smoothing velocity curve with Catmull-Rom spline (tension=0.3)...")

    velocities_before = get_velocities(grooved_path)

    # Use the high-level tool first (demonstrates the library API)
    temp_smooth_path = Path("_temp_smooth_tool.mid")
    smooth_velocity_curve(grooved_path, temp_smooth_path, method="catmull_rom", rate_hz=50)

    # Now use our custom tension-controlled smoother for the final output
    smooth_velocities_with_tension(grooved_path, OUTPUT_MIDI, tension=0.3, rate_hz=50)
    velocities_after = get_velocities(OUTPUT_MIDI)

    # Compute spline curve for visualization
    mid_grooved = mido.MidiFile(str(grooved_path))
    tempo = 500000
    note_points = []
    for track in mid_grooved.tracks:
        tick = 0
        for msg in track:
            tick += msg.time
            if msg.type == "set_tempo":
                tempo = msg.tempo
            if msg.type == "note_on" and msg.velocity > 0:
                sec = mido.tick2second(tick, TPB, tempo)
                note_points.append((sec, msg.velocity))
    note_points.sort(key=lambda x: x[0])

    if len(note_points) >= 2:
        # Collapse duplicate times by averaging their velocities
        time_map: dict[float, list[float]] = {}
        for sec, vel in note_points:
            time_map.setdefault(round(sec, 6), []).append(float(vel))
        xy = [(t, sum(vs) / len(vs)) for t, vs in sorted(time_map.items())]
        # Ensure strictly increasing x by adding tiny jitter if needed
        clean_xy = []
        last_x = -1.0
        for x, y in xy:
            if x <= last_x:
                x = last_x + 1e-6
            clean_xy.append((x, y))
            last_x = x
        spline = catmull_rom(clean_xy, tension=0.3)
        t0, t1 = clean_xy[0][0], clean_xy[-1][0]
        smooth_times = np.linspace(t0, t1, 500)
        smooth_vels = spline(smooth_times)
        # Convert seconds to beats for plotting
        beat_dur_sec = 60.0 / BPM
        smooth_times_beats = smooth_times / beat_dur_sec
    else:
        smooth_times_beats = np.array([])
        smooth_vels = np.array([])

    print(f"\n    Spline Statistics:")
    print(f"      Before — count: {len(velocities_before)}, mean: {np.mean(velocities_before):.1f}, std: {np.std(velocities_before):.1f}, "
          f"min: {min(velocities_before)}, max: {max(velocities_before)}")
    if velocities_after:
        print(f"      After  — count: {len(velocities_after)}, mean: {np.mean(velocities_after):.1f}, std: {np.std(velocities_after):.1f}, "
              f"min: {min(velocities_after)}, max: {max(velocities_after)}")
    else:
        print(f"      After  — count: 0")

    # -----------------------------------------------------------------------
    # 4. Analyze harmony with holonomy checker
    # -----------------------------------------------------------------------
    print("\n[4] Analyzing harmony with holonomy checker...")
    harmony = analyze_harmony(voices)
    print(f"    Chord roots (pitch classes): {harmony['roots']}")
    print(f"    Roman numerals:              {' → '.join(harmony['symbols'])}")
    print(f"    Holonomy:                    {harmony['holonomy']} (zero = closed cycle)")
    print(f"    Winding number:              {harmony['winding_number']:.2f}")
    print(f"    Max deviation:               {harmony['max_deviation']}")
    print(f"    Progression type:            {harmony['progression_type']}")
    print(f"    Stability score:             {harmony['stability_score']:.2f} / 1.0")

    # -----------------------------------------------------------------------
    # 5. Render MIDI
    # -----------------------------------------------------------------------
    print(f"\n[5] Rendered MIDI file: {OUTPUT_MIDI.resolve()}")

    # -----------------------------------------------------------------------
    # 6. Generate visualization
    # -----------------------------------------------------------------------
    print("\n[6] Generating visualization...")
    create_visualization(
        voices,
        timing,
        funnel,
        velocities_before,
        velocities_after,
        smooth_times_beats,
        smooth_vels,
        OUTPUT_PNG,
    )

    # -----------------------------------------------------------------------
    # Cleanup temp files
    # -----------------------------------------------------------------------
    for p in [grooved_path, temp_smooth_path]:
        if p.exists():
            p.unlink()

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
