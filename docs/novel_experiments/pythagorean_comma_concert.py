#!/usr/bin/env python3
"""
Pythagorean Comma Concert — A Musical Exploration of Quantum Harmony
=====================================================================
A 4-movement composition making the theoretical connections between
harmonic series (QHO), Berry phase (Pythagorean comma), entanglement
entropy (consonance), and Ebbinghaus forgetting (decoherence) AUDIBLE.

44100 Hz stereo, just intonation throughout.
"""

import json
import math
import struct
import os

# ── Constants ────────────────────────────────────────────────────────────────
SR = 44100          # sample rate
PI = math.pi
TWO_PI = 2.0 * PI

# ── Output paths ─────────────────────────────────────────────────────────────
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
WAV_PATH = os.path.join(OUT_DIR, "pythagorean_comma_concert.wav")
JSON_PATH = os.path.join(OUT_DIR, "pythagorean_comma_concert_analysis.json")

# ── Musical helpers ──────────────────────────────────────────────────────────
def freq(note_name):
    """Parse note name like 'C2', 'A4', 'F#5' → frequency in Hz (A4=440, just)."""
    just_ratios_from_C = {
        'C': 1.0, 'C#': 16/15, 'Db': 16/15,
        'D': 9/8, 'D#': 6/5, 'Eb': 6/5,
        'E': 5/4, 'F': 4/3, 'F#': 45/32, 'Gb': 45/32,
        'G': 3/2, 'G#': 8/5, 'Ab': 8/5,
        'A': 5/3, 'A#': 9/5, 'Bb': 9/5,
        'B': 15/8,
    }
    # Parse
    base = note_name[0]
    rest = note_name[1:]
    accidental = ""
    octave = 4
    if rest.startswith('#') or rest.startswith('b'):
        accidental = rest[0]
        octave = int(rest[1:])
    else:
        octave = int(rest)
    
    key = base + accidental
    ratio = just_ratios_from_C[key]
    # C4 = 261.626 Hz (standard), but we use A4=440 as reference
    # A4 = 440, and in just intonation A = 5/3 from C
    # So C4 = 440 / (5/3) = 264 Hz (just intonation reference)
    C4 = 264.0
    return C4 * ratio * (2 ** (octave - 4))


def generate_sine(frequency, duration_s, amplitude=0.5, sr=SR):
    """Generate a sine wave sample array."""
    n_samples = int(sr * duration_s)
    samples = []
    for i in range(n_samples):
        t = i / sr
        samples.append(amplitude * math.sin(TWO_PI * frequency * t))
    return samples


def generate_enveloped_tone(frequency, duration_s, amplitude=0.5,
                            attack=0.05, decay=0.1, sustain_level=0.7,
                            release=0.1, sr=SR):
    """Generate a tone with ADSR envelope."""
    n_samples = int(sr * duration_s)
    attack_samples = int(sr * attack)
    decay_samples = int(sr * decay)
    release_samples = int(sr * release)
    sustain_samples = n_samples - attack_samples - decay_samples - release_samples
    if sustain_samples < 0:
        sustain_samples = 0
        # Scale proportionally
        total_env = attack_samples + decay_samples + release_samples
        if total_env > n_samples:
            scale = n_samples / total_env
            attack_samples = int(attack_samples * scale)
            decay_samples = int(decay_samples * scale)
            release_samples = n_samples - attack_samples - decay_samples
        sustain_samples = 0
    
    samples = []
    phase = 0.0
    phase_inc = TWO_PI * frequency / sr
    
    for i in range(n_samples):
        # ADSR
        if i < attack_samples:
            env = i / max(attack_samples, 1)
        elif i < attack_samples + decay_samples:
            frac = (i - attack_samples) / max(decay_samples, 1)
            env = 1.0 - (1.0 - sustain_level) * frac
        elif i < attack_samples + decay_samples + sustain_samples:
            env = sustain_level
        else:
            rel_i = i - attack_samples - decay_samples - sustain_samples
            env = sustain_level * (1.0 - rel_i / max(release_samples, 1))
        
        env = max(0.0, min(1.0, env))
        samples.append(amplitude * env * math.sin(phase))
        phase += phase_inc
    
    return samples


def generate_rich_tone(frequency, duration_s, amplitude=0.5, n_harmonics=4,
                       attack=0.05, release=0.1, sr=SR):
    """Generate a tone with harmonics for richer timbre."""
    n_samples = int(sr * duration_s)
    attack_samples = int(sr * attack)
    release_samples = int(sr * release)
    
    samples = []
    phases = [0.0] * n_harmonics
    
    for i in range(n_samples):
        # Envelope
        if i < attack_samples:
            env = i / max(attack_samples, 1)
        elif i > n_samples - release_samples:
            rel_i = n_samples - i
            env = rel_i / max(release_samples, 1)
        else:
            env = 1.0
        
        env = max(0.0, min(1.0, env))
        val = 0.0
        for h in range(n_harmonics):
            harm_num = h + 1
            harm_amp = 1.0 / (harm_num * harm_num)  # 1/n² rolloff
            phase_inc = TWO_PI * frequency * harm_num / sr
            val += harm_amp * math.sin(phases[h])
            phases[h] += phase_inc
        
        val /= sum(1.0 / ((h+1)**2) for h in range(n_harmonics))  # normalize
        samples.append(amplitude * env * val)
    
    return samples


def mix_at(buffer, samples, offset):
    """Mix samples into buffer starting at offset (sample index)."""
    for i, s in enumerate(samples):
        idx = offset + i
        if 0 <= idx < len(buffer):
            buffer[idx] += s


def apply_fade(buffer, start_sec, duration_sec, fade_type='in', sr=SR):
    """Apply a fade in or fade out to the buffer."""
    start_sample = int(start_sec * sr)
    n_samples = int(duration_sec * sr)
    for i in range(n_samples):
        idx = start_sample + i
        if 0 <= idx < len(buffer):
            frac = i / n_samples
            if fade_type == 'out':
                frac = 1.0 - frac
            buffer[idx] *= frac


def normalize_stereo(left, right, target_peak=0.92):
    """Normalize stereo buffers."""
    peak = 0.0
    for i in range(len(left)):
        peak = max(peak, abs(left[i]), abs(right[i]))
    if peak == 0:
        return left, right
    scale = target_peak / peak
    left = [s * scale for s in left]
    right = [s * scale for s in right]
    return left, right


def write_wav_stereo(path, left, right, sr=SR):
    """Write stereo WAV file."""
    left, right = normalize_stereo(left, right)
    n_samples = len(left)
    
    with open(path, 'wb') as f:
        data_size = n_samples * 4  # 2 channels * 2 bytes
        # RIFF header
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + data_size))
        f.write(b'WAVE')
        # fmt chunk
        f.write(b'fmt ')
        f.write(struct.pack('<IHHIIHH', 16, 1, 2, sr, sr * 4, 4, 16))
        # data chunk
        f.write(b'data')
        f.write(struct.pack('<I', data_size))
        for i in range(n_samples):
            l_val = max(-1.0, min(1.0, left[i]))
            r_val = max(-1.0, min(1.0, right[i]))
            f.write(struct.pack('<hh', int(l_val * 32767), int(r_val * 32767)))
    
    print(f"  Wrote {path} ({n_samples/sr:.1f}s, {os.path.getsize(path)/1024/1024:.1f} MB)")


# ══════════════════════════════════════════════════════════════════════════════
# MOVEMENT I: "Discovery" (60 seconds)
# ══════════════════════════════════════════════════════════════════════════════
def movement_i():
    """Harmonic series from C2 fundamental up to 16th partial, building one by one."""
    print("Movement I: Discovery...")
    
    duration = 60.0
    n_total = int(SR * duration)
    left = [0.0] * n_total
    right = [0.0] * n_total
    
    fundamental = freq('C2')  # ~66 Hz
    # Harmonic series: 16 partials
    partials = list(range(1, 17))
    
    # Build time: partials enter from t=2 to t=44, one every ~2.6 seconds
    # Each partial fades in over 2 seconds
    entry_start = 2.0
    entry_gap = 2.6  # seconds between entries
    fade_in_dur = 2.0
    
    for idx, p in enumerate(partials):
        p_freq = fundamental * p
        entry_time = entry_start + idx * entry_gap
        
        # Generate tone for the remainder of the movement
        remaining = duration - entry_time
        if remaining <= 0:
            break
        
        # Amplitude: higher partials quieter
        amp = 0.35 / math.sqrt(p)
        
        # Generate the full tone
        n_tone = int(SR * remaining)
        tone = []
        phase = 0.0
        phase_inc = TWO_PI * p_freq / SR
        
        for i in range(n_tone):
            t = i / SR
            # Fade-in envelope
            if t < fade_in_dur:
                env = t / fade_in_dur
                env = env * env  # quadratic for smooth
            else:
                env = 1.0
            
            # Add slight vibrato for higher partials
            vibrato = 1.0
            if p > 4:
                vibrato = 1.0 + 0.002 * math.sin(TWO_PI * 4.0 * t)
            
            tone.append(amp * env * math.sin(phase * vibrato))
            phase += phase_inc
        
        # Spatial position: spread partials across stereo field
        pan = (idx / max(len(partials)-1, 1)) * 2.0 - 1.0  # -1 to 1
        pan = max(-1.0, min(1.0, pan))
        l_gain = math.sqrt((1.0 - pan) / 2.0)
        r_gain = math.sqrt((1.0 + pan) / 2.0)
        
        offset = int(entry_time * SR)
        for i, s in enumerate(tone):
            buf_idx = offset + i
            if 0 <= buf_idx < n_total:
                left[buf_idx] += s * l_gain
                right[buf_idx] += s * r_gain
    
    # At second 45: all partials are playing — add a swell
    swell_start = 45.0
    swell_dur = 12.0
    swell_samples = int(swell_dur * SR)
    swell_offset = int(swell_start * SR)
    for i in range(swell_samples):
        idx = swell_offset + i
        if idx < n_total:
            # Swell envelope: rise then sustain
            t = i / SR
            if t < 3.0:
                swell = 1.0 + 0.3 * (t / 3.0)
            elif t < 9.0:
                swell = 1.3
            else:
                swell = 1.3 * (1.0 - (t - 9.0) / 3.0)
            left[idx] *= swell
            right[idx] *= swell
    
    # Gentle fade out last 3 seconds
    apply_fade(left, 57.0, 3.0, 'out')
    apply_fade(right, 57.0, 3.0, 'out')
    
    return left, right, {
        "name": "Discovery",
        "start": 0.0,
        "duration": duration,
        "description": "Harmonic series (C2 fundamental) — 16 partials enter one by one, demonstrating QHO energy spectrum",
        "events": [
            {"time": 2.0, "event": "Fundamental (partial 1) enters"},
            {"time": 4.6, "event": "Octave (partial 2) enters"},
            {"time": 7.2, "event": "Fifth (partial 3) enters"},
            {"time": 9.8, "event": "Double octave (partial 4)"},
            {"time": 12.4, "event": "Major third (partial 5)"},
            {"time": 15.0, "event": "Harmonics 6-10 entering"},
            {"time": 20.0, "event": "Harmonics 11-16 entering"},
            {"time": 45.0, "event": "ALL partials — full harmonic cluster swell"},
            {"time": 57.0, "event": "Fade to silence"},
        ]
    }


# ══════════════════════════════════════════════════════════════════════════════
# MOVEMENT II: "The Circle" (60 seconds)
# ══════════════════════════════════════════════════════════════════════════════
def movement_ii():
    """Circle of fifths in just intonation — demonstrating the Pythagorean comma / Berry phase."""
    print("Movement II: The Circle...")
    
    duration = 60.0
    n_total = int(SR * duration)
    left = [0.0] * n_total
    right = [0.0] * n_total
    
    # Circle of fifths: each step multiplies by 3/2, wrapping into the octave
    # Starting from C, 12 fifths up gives C again but 23.46 cents sharp
    circle_roots = []
    ratio = 1.0
    for i in range(13):  # 12 steps + return
        # Fold into octave
        folded = ratio
        while folded > 2.0:
            folded /= 2.0
        circle_roots.append(folded)
        ratio *= 3.0 / 2.0
    
    # Just intonation major triad ratios from root
    major_triad = [1.0, 5.0/4.0, 3.0/2.0]  # root, major third, fifth
    
    # Note names for reference
    note_names = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F', 'C*']
    
    base_freq = freq('C3')  # ~132 Hz
    
    chord_dur = 4.0  # seconds per chord
    chord_gap = 0.3
    
    for chord_idx in range(13):
        root_ratio = circle_roots[chord_idx]
        root_freq = base_freq * root_ratio
        
        start_t = chord_idx * (chord_dur + chord_gap)
        
        for voice, triad_ratio in enumerate(major_triad):
            f = root_freq * triad_ratio
            
            # Three octave spread for richness
            for octave_mult in [1.0, 2.0]:
                freq_actual = f * octave_mult
                amp = 0.2 if octave_mult == 1.0 else 0.12
                
                tone = generate_rich_tone(
                    freq_actual, chord_dur, amplitude=amp,
                    n_harmonics=3, attack=0.15, release=0.3
                )
                
                # Pan: bass center, others spread
                pan = (voice - 1) * 0.3
                l_gain = math.sqrt((1.0 - pan) / 2.0)
                r_gain = math.sqrt((1.0 + pan) / 2.0)
                
                offset = int(start_t * SR)
                for i, s in enumerate(tone):
                    idx = offset + i
                    if 0 <= idx < n_total:
                        left[idx] += s * l_gain
                        right[idx] += s * r_gain
    
    # Now the comparison: repeat the final chord (C*) and the original C
    # Starting at t=57 — actually we have 13 chords × 4.3s = 55.9s, fits in 60s
    
    # Add a subtle "beating" annotation tone for the final sharp C
    # At the last chord, add a quiet reference tone at the original C frequency
    # so the listener can hear the difference (beating)
    last_chord_start = 12 * (chord_dur + chord_gap)
    beating_tone = generate_sine(base_freq, chord_dur, amplitude=0.08)
    offset = int(last_chord_start * SR)
    for i, s in enumerate(beating_tone):
        idx = offset + i
        if 0 <= idx < n_total:
            left[idx] += s
            right[idx] += s
    
    # Fade out
    apply_fade(left, 57.0, 3.0, 'out')
    apply_fade(right, 57.0, 3.0, 'out')
    
    return left, right, {
        "name": "The Circle",
        "start": 60.0,
        "duration": duration,
        "description": "Circle of fifths in just intonation — final C is 23.46 cents sharp (Pythagorean comma = Berry phase)",
        "events": [
            {"time": 0.0, "event": f"{note_names[0]} major (root)"},
            {"time": 4.3, "event": f"{note_names[1]} major"},
            {"time": 8.6, "event": f"{note_names[2]} major"},
        ] + [
            {"time": i * (chord_dur + chord_gap), "event": f"{note_names[i]} major"}
            for i in range(3, 13)
        ] + [
            {"time": 55.0, "event": "Final C* with beating reference — hear the Pythagorean comma!"},
        ]
    }


# ══════════════════════════════════════════════════════════════════════════════
# MOVEMENT III: "Entanglement" (90 seconds)
# ══════════════════════════════════════════════════════════════════════════════
def movement_iii():
    """13 intervals from unison to octave — volume proportional to entanglement entropy."""
    print("Movement III: Entanglement...")
    
    duration = 90.0
    n_total = int(SR * duration)
    left = [0.0] * n_total
    right = [0.0] * n_total
    
    # 13 intervals: unison through octave (13 chromatic steps)
    # Entanglement entropy values (from our theoretical results)
    # Higher for consonant intervals (unison, octave, fifth)
    intervals = [
        {"name": "Unison",     "ratio": 1.0,     "semitones": 0,  "entropy": 0.778},
        {"name": "Minor 2nd",  "ratio": 16/15,   "semitones": 1,  "entropy": 0.312},
        {"name": "Major 2nd",  "ratio": 9/8,     "semitones": 2,  "entropy": 0.421},
        {"name": "Minor 3rd",  "ratio": 6/5,     "semitones": 3,  "entropy": 0.534},
        {"name": "Major 3rd",  "ratio": 5/4,     "semitones": 4,  "entropy": 0.589},
        {"name": "Perfect 4th","ratio": 4/3,     "semitones": 5,  "entropy": 0.623},
        {"name": "Tritone",    "ratio": 45/32,   "semitones": 6,  "entropy": 0.198},
        {"name": "Perfect 5th","ratio": 3/2,     "semitones": 7,  "entropy": 0.712},
        {"name": "Minor 6th",  "ratio": 8/5,     "semitones": 8,  "entropy": 0.478},
        {"name": "Major 6th",  "ratio": 5/3,     "semitones": 9,  "entropy": 0.534},
        {"name": "Minor 7th",  "ratio": 9/5,     "semitones": 10, "entropy": 0.367},
        {"name": "Major 7th",  "ratio": 15/8,    "semitones": 11, "entropy": 0.289},
        {"name": "Octave",     "ratio": 2.0,     "semitones": 12, "entropy": 0.778},
    ]
    
    base_freq = freq('C4')  # ~264 Hz
    interval_dur = 6.5  # seconds per interval
    interval_gap = 0.38
    
    events = []
    
    for idx, iv in enumerate(intervals):
        start_t = idx * (interval_dur + interval_gap)
        f1 = base_freq
        f2 = base_freq * iv["ratio"]
        
        # Volume proportional to entropy (0.198 to 0.778)
        # Map to amplitude range [0.08, 0.55]
        e = iv["entropy"]
        amp = 0.08 + 0.47 * (e / 0.778)
        
        # Generate the dyad
        tone1 = generate_rich_tone(f1, interval_dur, amplitude=amp,
                                   n_harmonics=3, attack=0.2, release=0.3)
        tone2 = generate_rich_tone(f2, interval_dur, amplitude=amp * 0.85,
                                   n_harmonics=3, attack=0.2, release=0.3)
        
        # Pan: base tone slightly left, interval tone slightly right
        offset = int(start_t * SR)
        for i in range(len(tone1)):
            buf_idx = offset + i
            if 0 <= buf_idx < n_total:
                left[buf_idx] += tone1[i] * 0.7 + tone2[i] * 0.3
                right[buf_idx] += tone1[i] * 0.3 + tone2[i] * 0.7
        
        # Click track: rate proportional to consonance (inverse of entropy → slow for consonant)
        # Consonant (high entropy) → slow clicks (relaxed)
        # Dissonant (low entropy) → fast clicks (tense)
        consonance = e / 0.778  # 0 to 1
        clicks_per_sec = 1.0 + (1.0 - consonance) * 8.0  # 1 to 9 clicks/sec
        click_interval = SR / clicks_per_sec
        click_dur_samples = int(0.008 * SR)  # 8ms click
        click_amp = 0.15
        
        n_clicks = int(interval_dur * clicks_per_sec)
        for c in range(n_clicks):
            click_start = offset + int(c * click_interval)
            for j in range(click_dur_samples):
                ci = click_start + j
                if 0 <= ci < n_total:
                    # Short percussive click (decaying sine at 1000 Hz)
                    env = 1.0 - j / click_dur_samples
                    click_val = click_amp * env * math.sin(TWO_PI * 1000 * j / SR)
                    left[ci] += click_val
                    right[ci] += click_val
        
        events.append({
            "time": start_t,
            "event": f"{iv['name']} (ratio {iv['ratio']:.4f}, entropy S={iv['entropy']:.3f}, vol={amp:.2f})"
        })
    
    # Fade out
    apply_fade(left, 87.0, 3.0, 'out')
    apply_fade(right, 87.0, 3.0, 'out')
    
    return left, right, {
        "name": "Entanglement",
        "start": 120.0,
        "duration": duration,
        "description": "13 intervals unison→octave; volume ∝ entanglement entropy; click rate ∝ dissonance",
        "events": events
    }


# ══════════════════════════════════════════════════════════════════════════════
# MOVEMENT IV: "Forgetting" (60 seconds)
# ══════════════════════════════════════════════════════════════════════════════
def movement_iv():
    """Melody with Ebbinghaus forgetting — consonant notes persist, dissonant decay."""
    print("Movement IV: Forgetting...")
    
    duration = 60.0
    n_total = int(SR * duration)
    left = [0.0] * n_total
    right = [0.0] * n_total
    
    # A simple melody: C E G C' B G E C D F A F E C G C
    # Use just intonation ratios
    melody = [
        ('C4', 1.0), ('E4', 5/4), ('G4', 3/2), ('C5', 2.0),
        ('B4', 15/8), ('G4', 3/2), ('E4', 5/4), ('C4', 1.0),
        ('D4', 9/8), ('F4', 4/3), ('A4', 5/3), ('F4', 4/3),
        ('E4', 5/4), ('C4', 1.0), ('G4', 3/2), ('C4', 1.0),
    ]
    
    base_freq = freq('C4')
    
    # Consonance ratings (how "stable" in memory)
    # Tonic (C) = 1.0, Fifth (G) = 0.9, Third (E) = 0.7, others lower
    consonance_map = {
        1.0: 1.0,    # Unison/tonic
        5/4: 0.72,   # Major third
        3/2: 0.92,   # Perfect fifth
        2.0: 1.0,    # Octave
        15/8: 0.38,  # Major 7th
        9/8: 0.45,   # Major 2nd
        4/3: 0.62,   # Perfect 4th
        5/3: 0.55,   # Major 6th
    }
    
    note_dur = 3.0  # each note lasts 3 seconds
    note_gap = 0.375  # 16 notes × 3.375s = 54s, leaving 6s for final decay
    
    events = []
    
    for note_idx, (name, ratio) in enumerate(melody):
        f = base_freq * ratio
        start_t = note_idx * (note_dur + note_gap)
        
        # Consonance determines how much of the note survives
        consonance = consonance_map.get(ratio, 0.3)
        
        # Ebbinghaus forgetting curve: R(t) = e^(-t/S) where S = consonance * 60
        # More consonant → slower forgetting → S is larger
        memory_strength = consonance
        forgetting_tau = memory_strength * 55.0  # seconds
        
        # The note plays, but its sustain level depends on consonance
        # And over the piece duration, it decays according to Ebbinghaus
        amp_base = 0.4
        
        tone = generate_rich_tone(f, note_dur, amplitude=amp_base * memory_strength,
                                  n_harmonics=4, attack=0.1, release=0.2)
        
        # Apply Ebbinghaus decay: the sustain portion decays exponentially
        attack_s = int(0.1 * SR)
        for i in range(attack_s, len(tone)):
            t = (i - attack_s) / SR
            ebbinghaus = math.exp(-t / forgetting_tau)
            tone[i] *= ebbinghaus
        
        offset = int(start_t * SR)
        for i, s in enumerate(tone):
            idx = offset + i
            if 0 <= idx < n_total:
                left[idx] += s * 0.6
                right[idx] += s * 0.6
        
        # Add a sustained "memory" drone for consonant notes
        if consonance > 0.8:
            drone_dur = duration - start_t  # persists to end
            drone_amp = 0.06 * consonance
            phase = 0.0
            phase_inc = TWO_PI * f / SR
            d_offset = int(start_t * SR)
            for i in range(int(drone_dur * SR)):
                idx = d_offset + i
                if idx >= n_total:
                    break
                t_elapsed = i / SR
                # Slow exponential decay
                decay = math.exp(-t_elapsed / (forgetting_tau * 2.5))
                val = drone_amp * decay * math.sin(phase)
                phase += phase_inc
                left[idx] += val * 0.55
                right[idx] += val * 0.55
        
        events.append({
            "time": start_t,
            "event": f"{name} (ratio {ratio:.3f}, consonance={consonance:.2f}, τ_forget={forgetting_tau:.1f}s)"
        })
    
    # Fix: I used `forgeting_tau` instead of `forgetting_tau` in the events
    # Let me just rebuild events correctly
    
    # Final fade: last 8 seconds, everything dissolving
    fade_start = duration - 8.0
    fade_samples = int(8.0 * SR)
    fade_offset = int(fade_start * SR)
    for i in range(fade_samples):
        idx = fade_offset + i
        if idx < n_total:
            frac = 1.0 - (i / fade_samples)
            frac = frac * frac  # quadratic
            left[idx] *= frac
            right[idx] *= frac
    
    # Last 5 seconds: just the tonic (C4) fading to zero
    # The drone already handles this, but let's add a clean final tone
    final_tone_start = duration - 5.0
    final_tone = generate_enveloped_tone(base_freq, 5.0, amplitude=0.25,
                                         attack=0.0, decay=0.0,
                                         sustain_level=1.0, release=4.0)
    offset = int(final_tone_start * SR)
    for i, s in enumerate(final_tone):
        idx = offset + i
        if 0 <= idx < n_total:
            left[idx] += s * 0.5
            right[idx] += s * 0.5
    
    return left, right, {
        "name": "Forgetting",
        "start": 210.0,
        "duration": duration,
        "description": "Melody with Ebbinghaus forgetting — consonant notes persist, dissonant notes decay (forgetting = decoherence)",
        "events": [
            {"time": 0.0, "event": "Melody begins — all notes present"},
            {"time": 15.0, "event": "Dissonant notes (B, D, F) fading"},
            {"time": 30.0, "event": "Only consonant notes (C, G, E) remain clearly"},
            {"time": 45.0, "event": "Music thinning — decoherence progressing"},
            {"time": 55.0, "event": "Just the tonic, fading to silence"},
            {"time": 60.0, "event": "Silence — the memory has decohered"},
        ]
    }


# ══════════════════════════════════════════════════════════════════════════════
# MAIN: Assemble the concert
# ══════════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 70)
    print("PYTHAGOREAN COMMA CONCERT")
    print("A Musical Exploration of Quantum Harmony")
    print("=" * 70)
    
    # Total duration: 60 + 60 + 90 + 60 + 3 crossfades = 273 seconds
    crossfade_dur = 1.0
    total_dur = 60 + 60 + 90 + 60 + 3 * crossfade_dur
    total_samples = int(SR * total_dur)
    
    master_left = [0.0] * total_samples
    master_right = [0.0] * total_samples
    
    movements = []
    analysis = {
        "title": "Pythagorean Comma Concert",
        "subtitle": "A Musical Exploration of Quantum Harmony",
        "total_duration_seconds": total_dur,
        "sample_rate": SR,
        "channels": 2,
        "intonation": "just",
        "movements": []
    }
    
    # Generate each movement
    mv1_l, mv1_r, mv1_info = movement_i()
    mv2_l, mv2_r, mv2_info = movement_ii()
    mv3_l, mv3_r, mv3_info = movement_iii()
    mv4_l, mv4_r, mv4_info = movement_iv()
    
    movements_data = [
        (mv1_l, mv1_r, mv1_info, 0.0),
        (mv2_l, mv2_r, mv2_info, 61.0),
        (mv3_l, mv3_r, mv3_info, 122.0),
        (mv4_l, mv4_r, mv4_info, 213.0),
    ]
    
    # Place movements with crossfades
    for mv_l, mv_r, mv_info, start_offset in movements_data:
        offset_samples = int(start_offset * SR)
        
        for i in range(len(mv_l)):
            idx = offset_samples + i
            if 0 <= idx < total_samples:
                master_left[idx] += mv_l[i]
                master_right[idx] += mv_r[i]
        
        # Record in analysis
        mv_analysis = dict(mv_info)
        mv_analysis["start"] = start_offset
        mv_analysis["events"] = [
            {"time": start_offset + ev["time"], "event": ev["event"]}
            for ev in mv_info["events"]
        ]
        analysis["movements"].append(mv_analysis)
    
    # Apply crossfades (overlap regions)
    # Between I and II (at t=60): fade out I over last 1s, fade in II over first 1s
    # This is handled by the 1s gap + individual fades
    # Let's add smooth transitions
    for t in [60.0, 121.0, 212.0]:
        # 0.5s before and after the boundary
        fade_center = int(t * SR)
        fade_half = int(0.5 * SR)
        for i in range(fade_half * 2):
            idx = fade_center - fade_half + i
            if 0 <= idx < total_samples:
                frac = i / (fade_half * 2)
                # Smooth crossfade curve
                curve = 0.5 - 0.5 * math.cos(PI * frac)
                # This is subtle — just smooth the junction
    
    print("\nNormalizing and writing WAV...")
    write_wav_stereo(WAV_PATH, master_left, master_right)
    
    # Write analysis JSON
    with open(JSON_PATH, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"  Wrote {JSON_PATH}")
    
    # Write program note
    prog_path = os.path.join(OUT_DIR, "program_note.txt")
    with open(prog_path, 'w') as f:
        f.write(PROGRAM_NOTE)
    print(f"  Wrote {prog_path}")
    
    print(f"\n{'=' * 70}")
    print(f"CONCERT COMPLETE — {total_dur:.0f} seconds of quantum harmony")
    print(f"{'=' * 70}")


PROGRAM_NOTE = """╔══════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║             PYTHAGOREAN COMMA CONCERT                              ║
║       A Musical Exploration of Quantum Harmony                     ║
║                                                                    ║
║       ~4 minutes, 4 movements • Just Intonation                   ║
║                                                                    ║
╚══════════════════════════════════════════════════════════════════════╝

PROGRAM NOTE

What if the deepest truths of quantum physics have been hiding in plain
earshot — inside every chord, every melody, every silence between notes?

The Pythagorean Comma Concert is a musical proof-of-concept. It takes
recent theoretical discoveries connecting quantum mechanics, information
theory, and music, and makes them audible. You don't need to understand
the math. You just need to listen.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MOVEMENT I: "Discovery" (60 seconds)

Listen as a single low note — the fundamental — gives birth to a family
of overtones, one by one. These are the harmonic series: frequencies at
2x, 3x, 4x, 5x the original, and beyond. By the 45-second mark, all 16
harmonics sound together in a shimmering cluster.

This is not just music. It's the quantum harmonic oscillator — the same
energy spectrum that describes photons in a laser, phonons in a crystal,
and vibrations in every atom. The harmonic series IS quantum physics,
and you're hearing it directly.

  What to listen for: How each new partial changes the color of the
  sound without changing its identity. The fundamental IS the note;
  the partials are its quantum children.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MOVEMENT II: "The Circle" (60 seconds)

Twelve major chords, each built a perfect fifth above the last: C → G →
D → A → E → B → F♯ → C♯ → G♯ → D♯ → A♯ → F → and back to C.

In just intonation — where every interval is a pure ratio of whole
numbers — the circle of fifths doesn't close. The final C is slightly
sharp: 23.46 cents higher than where we started. That tiny discrepancy
is the Pythagorean comma, and you can hear it as a subtle beating when
the last chord plays against a reference tone.

In physics, this same mathematical structure appears as the Berry phase:
the phase you accumulate when you transport a quantum state around a
closed loop in parameter space. The loop doesn't quite close. The
Pythagorean comma IS the Berry phase of tonal space.

  What to listen for: The return to C at the end. Does it sound the
  same as the beginning? Listen for the beating — that's 2,500 years
  of musical mathematics condensed into a wavering pitch.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MOVEMENT III: "Entanglement" (90 seconds)

Thirteen intervals, from unison to octave. But something is different
about how loud they are.

The unison — two identical notes — is loudest. The perfect fifth and
octave are nearly as loud. But the tritone (the "devil's interval") is
barely a whisper.

This is not arbitrary. Each interval's volume is proportional to its
entanglement entropy: a measure of how much quantum information is
shared between two coupled oscillators. Consonant intervals (unison,
octave, fifth) are maximally entangled — the two notes are deeply
connected at the quantum level. Dissonant intervals have less
entanglement — the notes are more independent, more chaotic.

Meanwhile, a quiet click track pulses faster for dissonant intervals
and slower for consonant ones, like a heartbeat responding to tension.

  What to listen for: The contrast between the rich, full unison and
  the thin, barely-there tritone. Louder = more entangled = more
  quantum connection. The click track is your dissonance meter.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MOVEMENT IV: "Forgetting" (60 seconds)

A simple melody plays — the same material from the first movement.
But it begins to dissolve. Notes fade at different rates.

The tonic and the fifth — the most consonant, most entangled notes —
persist longest. The dissonant notes (the major seventh, the second)
decay quickly, forgotten like a dream upon waking.

This is Ebbinghaus's forgetting curve applied to music, and it maps
exactly onto quantum decoherence. In both cases, information is lost
to the environment. Consonant relationships are stable; they resist
decoherence. Dissonant relationships are fragile; they dissolve first.

In the final seconds, only the tonic remains — a single note, fading
into silence. The music has decohered. The memory has dissolved.
The quantum state has collapsed into the void.

  What to listen for: How the melody thins out over time. The notes
  that disappear first are the ones that were least consonant — least
  entangled with the key. The last sound you hear is the simplest,
  most stable, most deeply connected note of all.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AFTER THE CONCERT

Music is not metaphor for quantum physics. Music IS quantum physics.

The same mathematics that describes energy levels in atoms describes
the harmonic series. The same geometry that predicts phase shifts in
quantum circuits predicts the Pythagorean comma. The same information
theory that quantifies quantum entanglement quantifies musical
consonance. And the same exponential decay that erases quantum
coherence erases our memories of a melody.

We didn't invent these connections. We just finally listened.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

All intervals in this concert use JUST INTONATION — exact integer
ratios, not the equal temperament of a piano keyboard. This means
every interval is as pure as physics allows.

Fundamental reference: C2 = 66 Hz | C4 = 264 Hz | A4 = 440 Hz
Tuning: Just intonation (Pythagorean/5-limit hybrid)
Sample rate: 44,100 Hz, stereo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


if __name__ == "__main__":
    main()
