#!/usr/bin/env python3
"""
Demo: morph a simple melody through four terrain snapshots.

Takes a basic C-major melody, morphs the terrain underneath it from
delta_blues → bebop_rich → modal_jazz → free_improvisation, and writes
one WAV file per snapshot. Also prints the scale degrees at each step.
"""

import os
import struct
import wave

# Add parent to path so we can import constraint_instrument
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from constraint_instrument.terrain_morph import TerrainMorpher, _snap_note_to_terrain


# ── Simple WAV writer (no numpy dependency) ──────────────────────────

SAMPLE_RATE = 44100
AMPLITUDE = 16000  # 16-bit range max ~32767


def _midi_to_freq(midi_note: int) -> float:
    """Convert MIDI note number to frequency in Hz."""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


def _generate_tone(freq: float, duration: float) -> bytes:
    """Generate a sine wave tone as 16-bit PCM bytes."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n_samples):
        # Sine wave with envelope (fade in/out)
        t = i / SAMPLE_RATE
        env = min(1.0, min(i / 200, (n_samples - i) / 200))
        sample = int(AMPLITUDE * env * 0.5 * (
            # Add a few harmonics for a richer sound
            0.6 * math.sin(2 * math.pi * freq * t) +
            0.2 * math.sin(2 * math.pi * freq * 2 * t) +
            0.1 * math.sin(2 * math.pi * freq * 3 * t) +
            0.05 * math.sin(2 * math.pi * freq * 5 * t)
        ))
        sample = max(-32767, min(32767, sample))
        samples.append(struct.pack("<h", sample))
    return b"".join(samples)


def _write_wav(filename: str, note_data: list):
    """Write a WAV file from a list of (midi_note, duration) tuples."""
    raw_audio = b""
    for midi_note, duration in note_data:
        if midi_note <= 0:
            # Silence
            n_samples = int(SAMPLE_RATE * duration)
            raw_audio += b"\x00\x00" * n_samples
        else:
            raw_audio += _generate_tone(_midi_to_freq(midi_note), duration)
    
    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(raw_audio)


import math  # needed above


# ── The melody ───────────────────────────────────────────────────────

# Simple melody in C major (MIDI note numbers): C E G C' B G E C
MELODY = [60, 64, 67, 72, 71, 67, 64, 60]
NOTE_DURATION = 0.4  # seconds per note
ROOT = 60  # C4


# ── Morph chain ─────────────────────────────────────────────────────

def main():
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # The morph chain: blues → bebop → modal → free
    chain = [
        ("delta_blues", "delta_blues", "00_delta_blues"),
        ("delta_blues", "bebop_rich", "01_blues_to_bebop"),
        ("bebop_rich", "modal_jazz", "02_bebop_to_modal"),
        ("modal_jazz", "free_improvisation", "03_modal_to_free"),
    ]
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Terrain Morph Demo                                         ║")
    print("║  Melody: C E G C' B G E C                                  ║")
    print("║  Chain: delta_blues → bebop → modal → free                 ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    for source, target, label in chain:
        morpher = TerrainMorpher(source, target)
        terrain = morpher.blend(0.5 if source != target else 0.0)
        
        # Snap melody to this terrain
        snapped = [_snap_note_to_terrain(n, terrain.scale_degrees, ROOT) for n in MELODY]
        
        # Write WAV
        wav_path = os.path.join(output_dir, f"{label}.wav")
        note_data = [(n, NOTE_DURATION) for n in snapped]
        _write_wav(wav_path, note_data)
        
        print(f"── {label} ──")
        print(f"   Terrain: {terrain.name}")
        print(f"   Chromatic density: {terrain.chromatic_density:.3f}")
        print(f"   Scale degrees:")
        for sd in terrain.scale_degrees:
            bar_len = int(sd.weight * 30)
            bar = "█" * bar_len + "░" * (30 - bar_len)
            print(f"     {sd.degree:2d} ({sd.name:20s}) {bar} {sd.weight:.3f}")
        print(f"   Original melody: {MELODY}")
        print(f"   Snapped melody:  {snapped}")
        print(f"   → Wrote {wav_path}")
        print()
    
    print(f"✓ Done. {len(chain)} WAV files written to {output_dir}/")


if __name__ == "__main__":
    main()
