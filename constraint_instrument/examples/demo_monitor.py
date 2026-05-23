#!/usr/bin/env python3
"""
Demo: Monitor Flow Engine

Simulates a performer who starts rough, finds their groove,
and achieves deep flow. The Monitor adapts its assistance
level throughout — and eventually vanishes.

    python -m constraint_instrument.examples.demo_monitor
"""

import random
import sys
import os

# Add parent to path for direct execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from constraint_instrument.instrument import Instrument
from constraint_instrument.monitor import Monitor


def make_notes(pitches, start=0.0, duration=0.5, velocity=80):
    notes = []
    t = start
    for p in pitches:
        notes.append({
            "pitch": p,
            "velocity": velocity,
            "start": round(t, 3),
            "duration": round(duration, 3),
        })
        t += duration
    return notes


def bar_line(bar_num):
    return f"  │ {'─' * 50} │ Bar {bar_num}"


def flow_bar(flow, width=40):
    """Draw a flow state bar."""
    filled = int(flow * width)
    empty = width - filled
    if flow > 0.8:
        fill_char = "█"
    elif flow > 0.5:
        fill_char = "▓"
    elif flow > 0.3:
        fill_char = "▒"
    else:
        fill_char = "░"
    return f"[{fill_char * filled}{' ' * empty}] {flow:.1%}"


def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║          MONITOR FLOW ENGINE — Live Demo                ║")
    print("║  The invisible engineer: present when needed,           ║")
    print("║  gone when not.                                         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    instrument = Instrument(mode="ella", terrain="blues")
    monitor = Monitor(instrument, sensitivity=0.6)

    print(f"Monitor created: {monitor}")
    print(f"Sensitivity: {monitor.sensitivity}")
    print()

    # ── Phase 1: Rough Start ──────────────────────────────────────
    print("━━━ PHASE 1: ROUGH START ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Performer is unsure — random pitches, erratic timing")
    print()

    for bar in range(1, 6):
        rough = []
        t = (bar - 1) * 4.0
        for i in range(8):
            rough.append({
                "pitch": random.randint(20, 120),
                "velocity": random.randint(30, 127),
                "start": round(t + i * 0.5 + random.uniform(-0.3, 0.3), 3),
                "duration": round(random.uniform(0.1, 1.0), 3),
            })

        assessment = monitor.listen(rough)
        candidates = [
            {"pitch": 60, "score": 0.5},
            {"pitch": 90, "score": 0.5},
            {"pitch": 40, "score": 0.5},
        ]
        assisted = monitor.assist(candidates)
        guided = any(c.get("_monitor_guided") for c in assisted)

        print(bar_line(bar))
        print(f"  │ Flow:  {flow_bar(assessment['flow_state'])}")
        print(f"  │ Errors: {assessment['error_rate']:.1%}  "
              f"Consistency: {assessment['consistency']:.1%}  "
              f"Exploration: {assessment['exploration']:.1%}")
        print(f"  │ Recommendation: {assessment['recommendation']}")
        print(f"  │ Assist: {'GUIDED (added correction)' if guided else 'reordered' if assisted != candidates else 'hands-off'}")
        print(f"  │ {monitor}")
        print()

    print(f"  After rough phase — Flow: {monitor.flow_state:.1%}")
    print(f"  Interventions so far: {monitor.intervention_count}")
    print()

    # ── Phase 2: Finding the Groove ───────────────────────────────
    print("━━━ PHASE 2: FINDING THE GROOVE ━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Performer settles into the blues scale, timing steadies")
    print()

    blues_scale = [60, 63, 65, 66, 67, 70, 72, 75]

    for bar in range(6, 16):
        # Gradually more consistent
        consistency_factor = (bar - 6) / 10.0  # 0.0 → 0.9
        base_velocity = 75 + int(consistency_factor * 10)

        notes = []
        t = (bar - 6) * 4.0
        for i in range(8):
            # Mix of scale tones with decreasing randomness
            if random.random() < (1.0 - consistency_factor) * 0.3:
                pitch = random.randint(55, 80)  # occasional random
            else:
                pitch = blues_scale[i % len(blues_scale)]

            notes.append({
                "pitch": pitch,
                "velocity": base_velocity + random.randint(-5, 5),
                "start": round(t + i * 0.5, 3),
                "duration": 0.45,
            })

        assessment = monitor.listen(notes)
        candidates = [
            {"pitch": 60, "interval": 3, "score": 0.5},
            {"pitch": 63, "interval": 3, "score": 0.6},
            {"pitch": 67, "interval": 4, "score": 0.7},
            {"pitch": 90, "interval": 7, "score": 0.4},
        ]
        assisted = monitor.assist(candidates)
        guided = any(c.get("_monitor_guided") for c in assisted)
        reordered = not guided and assisted != candidates

        print(bar_line(bar))
        print(f"  │ Flow:  {flow_bar(assessment['flow_state'])}")
        print(f"  │ Errors: {assessment['error_rate']:.1%}  "
              f"Consistency: {assessment['consistency']:.1%}")
        print(f"  │ Recommendation: {assessment['recommendation']}")
        print(f"  │ Assist: {'GUIDED' if guided else 'reordered' if reordered else 'hands-off'}")
        print()

    print(f"  After groove phase — Flow: {monitor.flow_state:.1%}")
    print(f"  Learned register: {monitor.learned_tendencies.register_preference}")
    print(f"  Exploration style: {monitor.learned_tendencies.exploration_style}")
    print()

    # ── Phase 3: Deep Flow ────────────────────────────────────────
    print("━━━ PHASE 3: DEEP FLOW ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Performer is locked in — the music plays itself")
    print()

    vanished_at = None

    for bar in range(16, 46):
        # Very consistent, expressive blues phrases
        patterns = [
            [60, 63, 65, 67, 70, 72, 70, 67],
            [65, 66, 67, 70, 72, 75, 72, 70],
            [60, 62, 63, 67, 65, 63, 60, 63],
            [72, 70, 67, 65, 63, 60, 63, 65],
        ]
        pattern = patterns[bar % len(patterns)]
        notes = make_notes(pattern, start=(bar - 16) * 4.0, duration=0.5, velocity=85)

        assessment = monitor.listen(notes)

        candidates = [
            {"pitch": 60, "score": 0.5},
            {"pitch": 67, "score": 0.7},
            {"pitch": 72, "score": 0.6},
        ]
        assisted = monitor.assist(candidates)
        untouched = assisted == candidates

        if bar % 5 == 0 or monitor.is_vanished:
            print(bar_line(bar))
            print(f"  │ Flow:  {flow_bar(assessment['flow_state'])}")
            print(f"  │ Recommendation: {assessment['recommendation']}")
            print(f"  │ Assist: {'HANDS-OFF (flow is high)' if untouched else 'adapting'}")

            if monitor.is_vanished and vanished_at is None:
                vanished_at = bar
                print(f"  │")
                print(f"  │  🔇  MONITOR HAS VANISHED at bar {bar}")
                print(f"  │  The performer has internalized the constraints.")
                print(f"  │  The depth sounder you stop looking at.")
                print(f"  │")
            print()

        if vanished_at and bar > vanished_at + 5:
            break

    # ── Final Report ──────────────────────────────────────────────
    print("━━━ FINAL REPORT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    report = monitor.report()
    print(f"  Flow state:     {report.flow_state:.1%}")
    print(f"  Vanished:       {'Yes 🔇' if report.is_vanished else 'No'}")
    if vanished_at:
        print(f"  Vanished at:    Bar {vanished_at}")
    print(f"  Interventions:  {report.interventions_total}")
    print(f"  Snapshots:      {report.snapshots_analyzed}")
    print(f"  Register:       {report.tendencies.register_preference}")
    print(f"  Avg velocity:   {report.tendencies.average_velocity:.0f}")
    print(f"  Exploration:    {report.tendencies.exploration_style}")
    print(f"  Top intervals:  {dict(list(report.tendencies.favorite_intervals.items())[:5])}")
    print()

    # Show adaptive surface
    surface = monitor.get_adaptive_surface()
    print("  Adaptive Surface:")
    print(f"    Recommended sensitivity: {surface['recommended_sensitivity']:.2f}")
    print(f"    Temporal density:        {surface['temporal_density']:.2f} notes/sec")
    print(f"    Phrase length:           {surface['phrase_length']:.1f} notes")
    print()
    print("  " + str(monitor))
    print()


if __name__ == "__main__":
    main()
