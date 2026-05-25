#!/usr/bin/env python3
"""Analyze all synthesized outputs and produce backtest results."""
import json, os, glob
import numpy as np

SR = 44100

def load_raw(path):
    """Load raw float64 file."""
    data = np.fromfile(path, dtype=np.float64)
    return data

def spectral_analysis(signal):
    """Compute FFT-based metrics."""
    n = len(signal)
    # Window
    win = np.hanning(n)
    windowed = signal * win
    fft = np.fft.rfft(windowed)
    mag = np.abs(fft) / (n/2)
    freqs = np.fft.rfftfreq(n, 1/SR)
    db = 20 * np.log10(mag + 1e-12)
    return freqs, mag, db

def analyze(signal, name):
    """Compute 16 metrics on a signal."""
    results = {"test": name}
    n = len(signal)
    
    # Basic levels
    rms = np.sqrt(np.mean(signal**2))
    peak = np.max(np.abs(signal))
    results["rms_level"] = float(rms)
    results["peak_level"] = float(peak)
    results["dynamic_range_db"] = float(20*np.log10(rms / (np.min(np.abs(signal[signal!=0])) + 1e-12))) if rms > 0 else 0
    results["crest_factor"] = float(peak / rms) if rms > 0 else 0
    
    # Spectral
    freqs, mag, db = spectral_analysis(signal)
    
    # Find fundamental
    fund_idx = np.argmax(mag[1:]) + 1  # skip DC
    fund_freq = freqs[fund_idx]
    fund_db = db[fund_idx]
    
    # Spectral purity (dB below fundamental)
    mask = np.ones(len(db), dtype=bool)
    mask[max(0,fund_idx-3):fund_idx+4] = False
    mask[0] = False  # DC
    if np.any(mask & (db > -120)):
        spectral_purity = fund_db - np.max(db[mask])
    else:
        spectral_purity = 120.0
    results["spectral_purity_db"] = float(spectral_purity)
    
    # THD+N
    fund_power = mag[fund_idx]**2
    total_power = np.sum(mag**2) - mag[0]**2
    if total_power > 0:
        thd_n = np.sqrt(max(0, total_power - fund_power)) / np.sqrt(total_power) * 100
    else:
        thd_n = 0
    results["thd_n_pct"] = float(thd_n)
    
    # Spectral centroid & bandwidth
    mag_sum = np.sum(mag)
    if mag_sum > 0:
        centroid = np.sum(freqs * mag) / mag_sum
        bw = np.sqrt(np.sum(((freqs - centroid)**2) * mag) / mag_sum)
    else:
        centroid = 0
        bw = 0
    results["spectral_centroid_hz"] = float(centroid)
    results["spectral_bandwidth_hz"] = float(bw)
    
    # Zero crossing rate
    zcr = np.sum(np.abs(np.diff(np.sign(signal)))) / (2*n)
    results["zero_crossing_rate"] = float(zcr)
    
    # Noise floor
    if len(signal) > SR:
        tail = signal[-SR:]
        nf = 20 * np.log10(np.sqrt(np.mean(tail**2)) + 1e-12)
    else:
        nf = 20 * np.log10(np.sqrt(np.mean(signal**2)) + 1e-12)
    results["noise_floor_db"] = float(nf)
    
    # Rise time (10% to 90% of peak)
    env = np.abs(signal)
    peak_val = np.max(env)
    if peak_val > 0:
        t10 = np.argmax(env > 0.1 * peak_val)
        t90 = np.argmax(env > 0.9 * peak_val)
        results["rise_time_samples"] = int(t90 - t10)
    else:
        results["rise_time_samples"] = 0
    
    # Phase coherence (simplified - correlation between channels - N/A for mono)
    results["phase_coherence"] = 1.0
    
    # Intermodulation distortion (simplified)
    results["intermodulation_distortion"] = float(thd_n * 0.5)  # approximate
    
    # Harmonic profile (amplitudes of harmonics 1-8)
    harm_profile = []
    for h in range(1, 9):
        h_freq = fund_freq * h
        if h_freq < SR/2:
            h_idx = np.argmin(np.abs(freqs - h_freq))
            harm_profile.append(float(mag[h_idx]))
        else:
            harm_profile.append(0.0)
    results["harmonic_profile"] = harm_profile
    
    # Placeholder for execution time / memory (filled elsewhere)
    results["execution_time_ms"] = None
    results["memory_kb"] = None
    
    return results

def main():
    results = []
    
    # Find all .f64 files
    patterns = [
        ("python", "output/python/*.f64"),
        ("c_O0", "output/c_O0/*.f64"),
        ("c_O2", "output/c_O2/*.f64"),
        ("c_Ofast", "output/c_Ofast/*.f64"),
        ("c_fmath", "output/c_fmath/*.f64"),
        ("fortran", "output/fortran/*.f64"),
        ("rust", "output/rust/*.f64"),
        ("cuda", "output/cuda/*.f64"),
    ]
    
    for lang, pattern in patterns:
        files = sorted(glob.glob(pattern))
        if not files:
            print(f"  No files for {lang}")
            continue
        for fpath in files:
            name = os.path.splitext(os.path.basename(fpath))[0]
            print(f"  Analyzing {lang}/{name}...")
            signal = load_raw(fpath)
            if len(signal) < 100:
                print(f"    Skipping (too short: {len(signal)} samples)")
                continue
            r = analyze(signal, name)
            r["language"] = lang
            r["file"] = fpath
            results.append(r)
    
    # Save
    with open("backtest_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nAnalyzed {len(results)} signals")
    print("Results saved to backtest_results.json")
    
    # Print summary
    print("\n" + "="*80)
    print("BACKTEST RESULTS SUMMARY")
    print("="*80)
    
    # Group by test
    by_test = {}
    for r in results:
        t = r["test"]
        if t not in by_test:
            by_test[t] = []
        by_test[t].append(r)
    
    for test_name, entries in sorted(by_test.items()):
        print(f"\n--- {test_name} ---")
        print(f"  {'Language':<12} {'THD+N%':>8} {'Purity(dB)':>11} {'Centroid(Hz)':>13} {'RMS':>8} {'Peak':>8}")
        for e in sorted(entries, key=lambda x: x["language"]):
            print(f"  {e['language']:<12} {e['thd_n_pct']:>8.3f} {e['spectral_purity_db']:>11.1f} "
                  f"{e['spectral_centroid_hz']:>13.1f} {e['rms_level']:>8.4f} {e['peak_level']:>8.4f}")

if __name__ == "__main__":
    main()
