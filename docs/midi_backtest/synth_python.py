#!/usr/bin/env python3
"""Python synthesizer - reference implementation."""
import json, os, struct, wave
import numpy as np

SR = 44100
OUT = "output/python"
os.makedirs(OUT, exist_ok=True)

def envelope(n_samples, adsr=(0.01, 0.05, 0.7, 0.1)):
    a, d, s, r = adsr
    a_s = min(int(a*SR), n_samples)
    d_s = min(int(d*SR), n_samples - a_s)
    r_s = min(int(r*SR), n_samples - a_s - d_s)
    env = np.full(n_samples, s)
    if a_s > 0:
        env[:a_s] = np.linspace(0, 1, a_s)
    if d_s > 0:
        env[a_s:a_s+d_s] = np.linspace(1, s, d_s)
    if r_s > 0:
        env[-r_s:] = np.linspace(s, 0, r_s)
    return env

def osc_sine(freq, t):
    return np.sin(2*np.pi*freq*t)

def osc_saw(freq, t):
    """Bandlimited saw: sum of harmonics up to Nyquist."""
    result = np.zeros_like(t)
    n_harmonics = int((SR/2) / freq)
    for k in range(1, min(n_harmonics+1, 64)):
        result += ((-1)**(k+1)) * np.sin(2*np.pi*k*freq*t) / k
    return result * (2/np.pi)

def osc_square(freq, t):
    result = np.zeros_like(t)
    n_harmonics = int((SR/2) / freq)
    for k in range(1, min(n_harmonics+1, 64), 2):
        result += np.sin(2*np.pi*k*freq*t) / k
    return result * (4/np.pi)

def synth_test(name, notes):
    # Find total duration
    max_end = max(start + dur for freq, dur, vel, start in notes)
    n_samples = int(max_end * SR) + SR  # extra second
    mix = np.zeros(n_samples)
    
    for freq, dur, vel, start in notes:
        n = int(dur * SR)
        s0 = int(start * SR)
        t = np.arange(n) / SR
        amp = vel / 127.0
        sig = amp * osc_sine(freq, t) * envelope(n)
        end = min(s0 + n, n_samples)
        mix[s0:end] += sig[:end-s0]
    
    # Clip
    mix = np.clip(mix, -1.0, 1.0)
    
    # Save WAV
    path = os.path.join(OUT, f"{name}.wav")
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        data = (mix * 32767).astype(np.int16)
        wf.writeframes(data.tobytes())
    
    # Save raw float64 for analysis
    raw_path = os.path.join(OUT, f"{name}.f64")
    mix.astype(np.float64).tofile(raw_path)
    
    return path

if __name__ == "__main__":
    with open("corpus.json") as f:
        corpus = json.load(f)
    
    for name, notes in corpus.items():
        path = synth_test(name, notes)
        print(f"  Synthesized {name} -> {path}")
    print("Python synthesis complete.")
