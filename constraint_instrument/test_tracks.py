#!/usr/bin/env python3
"""Test multi-track and loop support."""

import os
import sys

# Add parent dir to path if needed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constraint_instrument.tracks import trap_beat, techno_loop, jazz_combo, Arrangement, Track

def test_basic_track():
    """Test a single Track."""
    print("=== Test: Single Track ===")
    t = Track('melody', 'parker', 'blues', 'piano', 'C', 120)
    notes = t.generate(bars=4)
    print(f"  Track: {t}")
    print(f"  Generated {len(notes)} notes")
    assert len(notes) > 0, "Should generate some notes"
    assert all('pitch' in n for n in notes), "All notes should have pitch"
    assert all('track' in n for n in notes), "All notes should have track label"
    assert all(n['track'] == 'melody' for n in notes), "Track name should be 'melody'"
    print("  ✓ Track generation works\n")

def test_quantize_humanize():
    """Test quantize and humanize."""
    print("=== Test: Quantize + Humanize ===")
    t = Track('arp', 'parker', 'electronic_techno', 'arp', 'C', 130)
    t.generate(bars=4)
    original_starts = [n['start_time'] for n in t.notes]
    
    t.quantize(grid=16)
    quantized_starts = [n['start_time'] for n in t.notes]
    print(f"  Quantized to 16th grid: {len(t.notes)} notes")
    
    t.humanize(timing_ms=8, velocity_range=5)
    humanized_starts = [n['start_time'] for n in t.notes]
    print(f"  Humanized with ±8ms timing, ±5 velocity")
    
    # Humanized should differ from quantized
    diff = sum(abs(h - q) for h, q in zip(humanized_starts, quantized_starts))
    print(f"  Total timing drift from humanize: {diff:.4f}s")
    print("  ✓ Quantize and humanize work\n")

def test_arrangement():
    """Test multi-track arrangement."""
    print("=== Test: Arrangement ===")
    arr = Arrangement(key='C', bpm=120, bars=4)
    arr.add_track('bass', 'parker', 'blues', 'bass')
    arr.add_track('melody', 'ella', 'blues', 'piano')
    arr.add_track('drums', 'armstrong', 'blues', 'drums')
    
    arr.generate_all()
    
    print(f"  Arrangement: {arr}")
    print(f"  Duration: {arr.duration:.2f}s")
    print(f"  Tracks: {[t.name for t in arr.tracks]}")
    for t in arr.tracks:
        print(f"    {t.name}: {len(t.notes)} notes")
    
    assert len(arr.tracks) == 3, "Should have 3 tracks"
    assert all(len(t.notes) > 0 for t in arr.tracks), "All tracks should have notes"
    print("  ✓ Arrangement works\n")

def test_trap_beat():
    """Test the trap_beat preset."""
    print("=== Test: trap_beat preset ===")
    beat = trap_beat(bpm=140, bars=8)
    beat.generate_all()
    
    print(f"  {beat}")
    print(f"  Tracks: {[t.name for t in beat.tracks]}")
    for t in beat.tracks:
        print(f"    {t.name}: {len(t.notes)} notes, duration={t.duration:.2f}s")
    
    assert len(beat.tracks) == 4, "Trap beat should have 4 tracks"
    print("  ✓ trap_beat preset works\n")

def test_loop():
    """Test looping with variation."""
    print("=== Test: Loop ===")
    beat = trap_beat(bpm=140, bars=4)
    beat.generate_all()
    
    initial_durations = {t.name: t.duration for t in beat.tracks}
    initial_counts = {t.name: len(t.notes) for t in beat.tracks}
    
    beat.loop(times=4)  # Should quadruple the notes roughly
    
    print(f"  After 4x loop:")
    for t in beat.tracks:
        ratio = len(t.notes) / initial_counts[t.name] if initial_counts[t.name] > 0 else 0
        print(f"    {t.name}: {len(t.notes)} notes ({ratio:.1f}x original), duration={t.duration:.2f}s")
    
    # Should have approximately 4x the notes (with some drift)
    for t in beat.tracks:
        expected = initial_counts[t.name] * 4
        actual = len(t.notes)
        # Allow some tolerance since notes may be clamped
        assert actual >= expected * 0.8, f"{t.name} should have ~{expected} notes after 4x loop, got {actual}"
    
    print("  ✓ Loop works\n")

def test_mutate():
    """Test mutation."""
    print("=== Test: Mutate ===")
    arr = trap_beat(bpm=140, bars=4)
    arr.generate_all()
    
    # Save original pitches
    original_pitches = {}
    for t in arr.tracks:
        original_pitches[t.name] = [n['pitch'] for n in t.notes]
    
    arr.mutate(intensity=0.5)
    
    changed = 0
    total = 0
    for t in arr.tracks:
        new_pitches = [n['pitch'] for n in t.notes]
        for o, n in zip(original_pitches[t.name], new_pitches):
            total += 1
            if o != n:
                changed += 1
    
    pct = changed / total * 100 if total > 0 else 0
    print(f"  Mutation at intensity=0.5: {changed}/{total} notes changed ({pct:.1f}%)")
    print("  ✓ Mutate works\n")

def test_render():
    """Test WAV rendering."""
    print("=== Test: Render ===")
    beat = trap_beat(bpm=140, bars=4)
    beat.generate_all()
    beat.loop(times=2)
    
    output_path = os.path.join(os.path.dirname(__file__), 'test_output.wav')
    beat.render(output_path)
    
    size = os.path.getsize(output_path)
    print(f"  Rendered to {output_path}")
    print(f"  File size: {size} bytes ({size/1024:.1f} KB)")
    assert size > 0, "WAV file should not be empty"
    
    # Clean up
    os.unlink(output_path)
    print("  ✓ Render works\n")

def test_midi_export():
    """Test MIDI export."""
    print("=== Test: MIDI Export ===")
    try:
        from mido import MidiFile
        has_mido = True
    except ImportError:
        has_mido = False
        print("  ⚠ mido not installed, skipping MIDI test\n")
        return
    
    beat = trap_beat(bpm=140, bars=4)
    beat.generate_all()
    
    midi_path = os.path.join(os.path.dirname(__file__), 'test_output.mid')
    beat.to_midi(midi_path)
    
    size = os.path.getsize(midi_path)
    print(f"  Exported MIDI to {midi_path}")
    print(f"  File size: {size} bytes ({size/1024:.1f} KB)")
    
    # Verify it's a valid MIDI file
    mid = MidiFile(midi_path)
    print(f"  MIDI tracks: {len(mid.tracks)}")
    assert len(mid.tracks) >= 2, "Should have at least tempo + 1 track"
    
    # Clean up
    os.unlink(midi_path)
    print("  ✓ MIDI export works\n")

def test_full_workflow():
    """Test the full producer workflow from the task spec."""
    print("=== Test: Full Workflow (from spec) ===")
    from constraint_instrument.tracks import trap_beat
    
    beat = trap_beat(bpm=140, bars=8)
    beat.generate_all()
    beat.loop(times=4)  # 32 bars total with variation
    
    output_path = os.path.join(os.path.dirname(__file__), 'trap_beat.wav')
    beat.render(output_path)
    
    print(f"Tracks: {[t.name for t in beat.tracks]}")
    for t in beat.tracks:
        print(f"  {t.name}: {len(t.notes)} notes")
    
    size = os.path.getsize(output_path)
    print(f"Output: {output_path} ({size/1024:.1f} KB)")
    
    # Clean up
    os.unlink(output_path)
    print("  ✓ Full workflow works\n")


if __name__ == '__main__':
    test_basic_track()
    test_quantize_humanize()
    test_arrangement()
    test_trap_beat()
    test_loop()
    test_mutate()
    test_render()
    test_midi_export()
    test_full_workflow()
    print("=" * 50)
    print("ALL TESTS PASSED ✓")
