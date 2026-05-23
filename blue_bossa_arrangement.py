#!/usr/bin/env python3
"""
Blue Bossa Arrangement Generator
Uses: holonomy-harmony, counterpoint-engine, groove-analyzer, spline-midi-smooth
Goal: Generate a full 5-piece jazz combo arrangement from Blue Bossa changes
"""

import sys
import os
import math
import numpy as np

# Setup paths
WORKSPACE = "/home/phoenix/.openclaw/workspace"
for repo in ["holonomy-harmony", "counterpoint-engine", "constraint-theory-core", 
             "groove-analyzer", "spline-midi-smooth"]:
    sys.path.insert(0, os.path.join(WORKSPACE, repo))

import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

# ============================================================
# STEP 1: Analyze Blue Bossa with holonomy-harmony
# ============================================================
print("=" * 60)
print("STEP 1: Analyzing Blue Bossa changes with holonomy-harmony")
print("=" * 60)

from holonomy_harmony import analyze_progression, compute_holonomy, TonalGraph

# Blue Bossa changes (typically in C minor)
# Section A: Cm | Cm | Fm7 | Fm7 | Dm7b5 | G7 | Cmaj7 | Cmaj7
# Section B: Am7 | D7 | Dm7 | G7 | Cm | Cm
# Using Roman numerals in C minor:
blue_bossa_symbols = [
    # Section A (8 bars)
    'i', 'i', 'iv', 'iv', 'iiø', 'V7', 'I', 'I',
    # Section B (6 bars)  
    'VI', 'VII7', 'iiø', 'V7', 'i', 'i',
]

analysis = analyze_progression(blue_bossa_symbols, key_tonic=0, mode='minor')
print(f"Holonomy: {analysis.holonomy.holonomy}")
print(f"Winding: {analysis.holonomy.winding_number}")
print(f"Type: {analysis.holonomy.progression_type}")
print(f"Stability: {analysis.stability_score}")
print(f"Chords: {[(c.root, c.quality, c.function) for c in analysis.chords]}")
print()

# Build tonal graph
graph = analysis.graph
print(f"Tonal graph: {graph}")
print()

# ============================================================
# STEP 2: Define the chord voicings manually
# (None of the repos provide jazz voicing generation)
# ============================================================
print("=" * 60)
print("STEP 2: Defining chord voicings (manual - no API support)")
print("=" * 60)

# Blue Bossa chord changes with MIDI pitch voicings
# Format: (name, bass_note, piano_voicing, guide_tones, sax_line, trumpet_notes)

CHORDS = {
    'Cm7':   {'bass': 36, 'piano': [60, 63, 67, 70], 'guide': [63, 70]},  # Eb G Bb D (rootless)
    'Fm7':   {'bass': 41, 'piano': [60, 63, 65, 68], 'guide': [65, 68]},  # Ab C Eb (rootless)  
    'Dm7b5': {'bass': 38, 'piano': [60, 63, 65, 68], 'guide': [63, 68]},  # F Ab C Eb
    'G7':    {'bass': 43, 'piano': [59, 62, 65, 69], 'guide': [62, 65]},   # B D F A (rootless)
    'G7alt': {'bass': 43, 'piano': [59, 62, 65, 69], 'guide': [62, 65]},   # same for now
    'Cmaj7': {'bass': 36, 'piano': [60, 64, 67, 71], 'guide': [64, 71]},  # C E G B
    'Am7':   {'bass': 45, 'piano': [60, 64, 67, 72], 'guide': [64, 67]},  # C E G C
    'D7':    {'bass': 50, 'piano': [62, 66, 69, 73], 'guide': [66, 73]},  # D F# A C#
    'Dm7':   {'bass': 50, 'piano': [62, 65, 69, 72], 'guide': [65, 72]},  # D F A C
}

# Chord progression for 14-bar form
PROGRESSION = [
    'Cm7', 'Cm7', 'Fm7', 'Fm7',       # bars 1-4
    'Dm7b5', 'G7', 'Cmaj7', 'Cmaj7',  # bars 5-8
    'Am7', 'D7', 'Dm7', 'G7',         # bars 9-12
    'Cm7', 'Cm7',                       # bars 13-14
]

print(f"Chord progression ({len(PROGRESSION)} bars): {' | '.join(PROGRESSION)}")
print("Note: Voicings manually defined — no API generates drop-2, rootless, or quartal voicings")
print()

# ============================================================
# STEP 3: Generate walking bass with counterpoint-engine
# ============================================================
print("=" * 60)
print("STEP 3: Generating walking bass with counterpoint-engine")
print("=" * 60)

from counterpoint_engine.generator import CounterpointGenerator, Species, Scale, VoiceRange

# Create cantus firmus from root notes of the progression
cantus_firmus = [CHORDS[name]['bass'] for name in PROGRESSION]
print(f"Cantus firmus (roots): {cantus_firmus}")

# Use counterpoint engine to generate a bass line
gen = CounterpointGenerator(
    cantus_firmus=cantus_firmus,
    species=Species.FIRST,  # Note: 1 note per bar — we need 4 for walking!
    scale=Scale(tonic=0, mode='major'),
    voice_range=VoiceRange(min_pitch=34, max_pitch=55),
)

result = gen.generate()
print(f"Counterpoint result: {result.voices}")
print(f"Feasible: {result.feasible}")
print()

# FRICTION: counterpoint-engine generates 1 note per cantus note.
# Jazz walking bass needs 4 notes per bar (quarter notes).
# We have to expand manually.

def generate_walking_bass(progression, chords_dict):
    """Generate a walking bass line manually since counterpoint-engine
    only does species counterpoint (1:1 note ratios)."""
    bass_line = []
    for i, chord_name in enumerate(progression):
        root = chords_dict[chord_name]['bass']
        guide = chords_dict[chord_name]['guide']
        
        # Get next root for approach
        next_chord = progression[(i + 1) % len(progression)]
        next_root = chords_dict[next_chord]['bass']
        
        # Walking pattern: root, passing tone, chord tone, approach to next
        # Use scale tones and chromatic approaches
        beat1 = root  # Root on beat 1
        
        # Beat 2: chord tone or scale tone
        scale_tones = [root, root+3, root+5, root+7, root+10, root+12]
        beat2 = root + 5 if root + 5 <= 55 else root - 2  # 5th or leading tone
        
        # Beat 3: chord tone
        beat3 = guide[0] - 12 if guide[0] - 12 >= 34 else root + 7  # Guide tone down an octave
        
        # Beat 4: chromatic approach to next root
        if next_root > beat3:
            beat4 = next_root - 1  # Chromatic from below
        else:
            beat4 = next_root + 1  # Chromatic from above
        
        bass_line.extend([beat1, beat2, beat3, beat4])
    
    return bass_line

walking_bass = generate_walking_bass(PROGRESSION, CHORDS)
print(f"Walking bass ({len(walking_bass)} notes): {walking_bass[:16]}...")
print("FRICTION: counterpoint-engine only does 1:1 species counterpoint.")
print("Jazz walking bass (4:1 ratio) had to be generated manually.")
print()

# ============================================================
# STEP 4: Apply swing feel with groove-analyzer
# ============================================================
print("=" * 60)
print("STEP 4: Applying swing feel with groove-analyzer")
print("=" * 60)

from groove_analyzer.genres import GENRE_PROFILES

jazz_profile = GENRE_PROFILES['Jazz']
print(f"Jazz profile: ε={jazz_profile.epsilon_ms}ms, swing={jazz_profile.swing_factor}, bpm={jazz_profile.bpm}")
print(f"Swing factor interpretation: downbeat-to-upbeat ratio = {jazz_profile.swing_factor}")
print(f"  At 120 BPM, 8th note = 250ms, swung triplet = {250*2/3:.0f}ms + {250/3:.0f}ms")
print()

def apply_swing(tick_positions, swing_factor=0.67, grid='16th'):
    """Apply swing to 16th-note grid positions.
    swing_factor: ratio of first note to second in a pair (0.5=straight, 0.67=triplet, 0.75=dotted)
    """
    swung = []
    for tick in tick_positions:
        # Every other 16th note gets delayed
        subdivision = tick % 4  # position within beat (0,1,2,3)
        if subdivision % 2 == 1:  # upbeat
            delay_ticks = int(tick * (swing_factor - 0.5) * 2)
            swung.append(tick + delay_ticks)
        else:
            swung.append(tick)
    return swung

print("Swing applied conceptually — groove-analyzer can ANALYZE swing but doesn't")
print("directly synthesize swing timing onto arbitrary MIDI note sequences.")
print("synthesize_groove() generates its own drum patterns, not apply-to-existing.")
print()

# ============================================================
# STEP 5: Build the full MIDI arrangement
# ============================================================
print("=" * 60)
print("STEP 5: Building full MIDI arrangement")
print("=" * 60)

BPM = 140
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
SWING_FACTOR = 0.67  # Triplet swing

midi = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
midi.tracks.append(MidiTrack())  # Track 0: Tempo/time sig

# Set tempo and time signature
midi.tracks[0].append(MetaMessage('set_tempo', tempo=bpm2tempo(BPM), time=0))
midi.tracks[0].append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))

def create_instrument_track(name, channel, program=None):
    track = MidiTrack()
    track.name = name
    if program is not None:
        track.append(Message('program_change', channel=channel, program=program, time=0))
    return track

# Track assignments
piano_track = create_instrument_track("Piano", channel=0, program=1)     # Acoustic Grand
bass_track = create_instrument_track("Bass", channel=1, program=32)      # Acoustic Bass
drums_track = create_instrument_track("Drums", channel=9)                # Channel 10
sax_track = create_instrument_track("Sax", channel=2, program=66)        # Alto Sax
trumpet_track = create_instrument_track("Trumpet", channel=3, program=56) # Trumpet

def ticks_for_bar(bar):
    return bar * BEATS_PER_BAR * TICKS_PER_BEAT

def swing_tick(tick):
    """Apply swing to a tick position."""
    beat_pos = tick % TICKS_PER_BEAT
    subdivision = beat_pos / (TICKS_PER_BEAT / 4)  # 0,1,2,3
    if int(subdivision) % 2 == 1:  # upbeat 16ths
        delay = int(TICKS_PER_BEAT / 4 * (SWING_FACTOR - 0.5) * 2)
        return tick + delay
    return tick

# --- PIANO COMPING ---
# Drop-2 voicings with typical jazz comping rhythms
comping_rhythms = [
    # Patterns of (beat_subdivision, velocity) — positions within a bar
    # These are typical Freddie Green / Red Garland style
    [(0, 0), (2.67, 0), (3.0, 0)],     # Long-short on beats 1 and 3
    [(0.5, 0), (1.0, 0), (2.67, 0)],   # Offbeat emphasis
    [(0, 0), (1.33, 0), (2.0, 0), (3.33, 0)],  # Syncopated
    [(0.67, 0), (2.0, 0), (3.0, 0)],   # Charleston rhythm
]

for bar_idx, chord_name in enumerate(PROGRESSION):
    voicing = CHORDS[chord_name]['piano']
    rhythm = comping_rhythms[bar_idx % len(comping_rhythms)]
    
    abs_bar_start = ticks_for_bar(bar_idx)
    
    for beat_offset, _ in rhythm:
        tick = abs_bar_start + int(beat_offset * TICKS_PER_BEAT)
        tick = swing_tick(tick)
        vel = np.random.randint(55, 80)
        duration = TICKS_PER_BEAT  # Hold for about a beat
        
        for note in voicing:
            piano_track.append(Message('note_on', channel=0, note=note, velocity=vel, time=0))
        
        # We'll use note_off after duration (simplified)
        for note in voicing:
            piano_track.append(Message('note_off', channel=0, note=note, velocity=0, time=duration))

# --- WALKING BASS ---
for i, pitch in enumerate(walking_bass):
    bar_idx = i // 4
    beat = i % 4
    tick = ticks_for_bar(bar_idx) + beat * TICKS_PER_BEAT
    tick = swing_tick(tick)
    
    # Slight velocity variation for feel
    vel = int(70 + 15 * math.sin(i * math.pi / 2))  # Slight crescendo/decrescendo
    vel = max(50, min(100, vel + np.random.randint(-5, 5)))
    
    bass_track.append(Message('note_on', channel=1, note=pitch, velocity=vel, time=0))
    bass_track.append(Message('note_off', channel=1, note=pitch, velocity=0, time=TICKS_PER_BEAT - 10))

# --- DRUMS (Jazz ride pattern) ---
# Ride: swing 8th pattern on ride cymbal (MIDI 51)
# Hi-hat: beats 2 and 4 (MIDI 42) with pedal
# Kick: occasional feathering on beats 1 and 3
total_bars = len(PROGRESSION)
for bar in range(total_bars):
    bar_start = ticks_for_bar(bar)
    
    # Ride cymbal: swing 8th notes (triplet feel)
    for beat in range(4):
        for sub in range(2):
            if sub == 0:
                tick = bar_start + beat * TICKS_PER_BEAT
                vel = np.random.randint(65, 85)
            else:
                # Swinged upbeat
                tick = bar_start + beat * TICKS_PER_BEAT + int(TICKS_PER_BEAT * 2/3)
                vel = np.random.randint(45, 65)
            
            drums_track.append(Message('note_on', channel=9, note=51, velocity=vel, time=0))
            drums_track.append(Message('note_off', channel=9, note=51, velocity=0, time=TICKS_PER_BEAT // 2 - 10))
    
    # Hi-hat on 2 and 4
    for beat in [1, 3]:
        tick = bar_start + beat * TICKS_PER_BEAT
        vel = np.random.randint(60, 80)
        drums_track.append(Message('note_on', channel=9, note=42, velocity=vel, time=0))
        drums_track.append(Message('note_off', channel=9, note=42, velocity=0, time=TICKS_PER_BEAT // 4))
    
    # Kick feather on 1 and 3 (very light)
    for beat in [0, 2]:
        tick = bar_start + beat * TICKS_PER_BEAT
        drums_track.append(Message('note_on', channel=9, note=36, velocity=40, time=0))
        drums_track.append(Message('note_off', channel=9, note=36, velocity=0, time=TICKS_PER_BEAT // 4))

# --- SAXOPHONE (Melody/Head) ---
# Simplified Blue Bossa melody (approximation)
# The melody is largely scale-based in C minor
melody_notes = [
    # Bars 1-4 (Cm section) — ascending scale motif
    (60, 1), (63, 0.5), (67, 0.5), (65, 1), (63, 1),  # bar 1-2
    (65, 1), (68, 0.5), (72, 0.5), (70, 1), (68, 1),   # bar 3-4
    # Bars 5-8 (ii-V-I)
    (70, 0.5), (68, 0.5), (67, 1), (65, 0.5), (63, 0.5), (62, 1),  # bar 5-6
    (60, 1.5), (63, 0.5), (67, 1), (64, 1),               # bar 7-8
    # Bars 9-12 (Am-D7-Dm-G7 section)
    (64, 1), (67, 0.5), (69, 0.5), (72, 1), (71, 1),     # bar 9-10
    (69, 1), (67, 0.5), (65, 0.5), (67, 0.5), (65, 0.5), (62, 1),  # bar 11-12
    # Bars 13-14 (resolution)
    (60, 2), (60, 2),  # Final C
]

current_tick = 0
for note, duration_beats in melody_notes:
    duration_ticks = int(duration_beats * TICKS_PER_BEAT)
    vel = int(80 + np.random.randint(-10, 10))
    vel = max(60, min(100, vel))
    
    sax_track.append(Message('note_on', channel=2, note=note, velocity=vel, time=0))
    sax_track.append(Message('note_off', channel=2, note=note, velocity=0, time=duration_ticks))
    current_tick += duration_ticks

# --- TRUMPET (Harmonized melody / fills) ---
# Simple harmonization: 3rds above sax melody
trumpet_notes = []
for note, dur in melody_notes:
    # Harmonize a 3rd or 6th above
    harmony_interval = 3 if note % 2 == 0 else 4  # Diatonic 3rds (approximation)
    trumpet_notes.append((note + harmony_interval, dur))

for note, duration_beats in trumpet_notes:
    if note > 80:  # Keep in range
        note = 80 - (note - 80)
    duration_ticks = int(duration_beats * TICKS_PER_BEAT)
    vel = int(75 + np.random.randint(-10, 10))
    vel = max(55, min(95, vel))
    
    trumpet_track.append(Message('note_on', channel=3, note=note, velocity=vel, time=0))
    trumpet_track.append(Message('note_off', channel=3, note=note, velocity=0, time=duration_ticks))

# Add all tracks to MIDI
for t in [piano_track, bass_track, drums_track, sax_track, trumpet_track]:
    midi.tracks.append(t)

output_path = "/home/phoenix/.openclaw/workspace/blue_bossa_arrangement.mid"
midi.save(output_path)
print(f"MIDI saved to {output_path}")
print(f"Tracks: {len(midi.tracks)}")
for i, track in enumerate(midi.tracks):
    print(f"  Track {i}: {track.name} ({len(track)} events)")
print()

# ============================================================
# STEP 6: Smooth dynamics with spline-midi-smooth
# ============================================================
print("=" * 60)
print("STEP 6: Smoothing dynamics with spline-midi-smooth")
print("=" * 60)

from spline_midi_smooth.interpolation import cubic_hermite, catmull_rom

# Extract velocity curves from our MIDI and smooth them
# (Can't use smooth_velocity_curve directly due to simultaneous-note bug)

# Instead, let's smooth the bass velocity curve manually
bass_velocities = [(i, 70 + 15 * math.sin(i * math.pi / 2)) for i in range(len(walking_bass))]
if len(bass_velocities) >= 4:
    spline = cubic_hermite(bass_velocities)
    smooth_times = np.linspace(0, len(walking_bass) - 1, len(walking_bass) * 10)
    smooth_vels = spline(smooth_times)
    smooth_vels = np.clip(smooth_vels, 40, 110)
    print(f"Bass velocity curve smoothed: {len(bass_velocities)} points → {len(smooth_vels)} samples")
    print(f"  Original range: {min(v for _, v in bass_velocities):.1f} - {max(v for _, v in bass_velocities):.1f}")
    print(f"  Smoothed range: {smooth_vels.min():.1f} - {smooth_vels.max():.1f}")

print()
print("FRICTION: smooth_velocity_curve() crashes on MIDI files with simultaneous notes")
print("(which is every multi-track arrangement). Had to extract and smooth manually.")
print("Also: no way to write smoothed velocities back into the MIDI tracks easily.")
print()

# ============================================================
# SUMMARY OF FRICTION POINTS
# ============================================================
print("=" * 60)
print("FRICTION POINT SUMMARY")
print("=" * 60)
frictions = [
    "1. holonomy-harmony: Roman numeral parser doesn't support jazz chord qualities (7, m7, m7b5, 7alt, maj7)",
    "2. holonomy-harmony: No built-in Blue Bossa progression (has autumn_leaves but not blue_bossa)",
    "3. counterpoint-engine: Only species counterpoint (1:1 note ratio), no walking bass (4:1 ratio)",
    "4. counterpoint-engine: No concept of chord tones, passing tones, or approach notes",
    "5. counterpoint-engine: No awareness of harmonic rhythm or chord progression context",
    "6. groove-analyzer: Can ANALYZE swing but synthesize_groove() only makes drum patterns",
    "7. groove-analyzer: No apply_swing() or apply_groove() to existing note sequences",
    "8. spline-midi-smooth: smooth_velocity_curve() crashes on simultaneous notes (common in MIDI!)",
    "9. spline-midi-smooth: No velocity shaping presets (crescendo, forte-piano, etc.)",
    "10. None of the repos: chord voicing generation, guide tone extraction, voice leading",
    "11. None of the repos: comping rhythm generation, shell voicings, rootless voicings",
    "12. None of the repos: jazz-specific scales (bebop, altered, diminished, whole-tone)",
]
for f in frictions:
    print(f"  {f}")

print()
print("DONE — arrangement written to blue_bossa_arrangement.mid")
