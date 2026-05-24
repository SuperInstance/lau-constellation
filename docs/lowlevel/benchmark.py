#!/usr/bin/env python3
"""
benchmark.py — Compare WASM vs Native vs Python lattice oscillator performance

Compiles the C lattice oscillator to native (gcc) and WASM (emcc),
then benchmarks all three implementations against a Python/numpy reference.

Usage:
    python3 benchmark.py [--samples 44100] [--voices 4] [--partials 8]

Output:
    Comparison table: wall time, memory, voices/sec, throughput ratio
"""

import time
import sys
import os
import subprocess
import struct
import ctypes
import argparse
import tempfile
import statistics

# ============================================================================
# Configuration
# ============================================================================

SAMPLE_RATE = 44100
DEFAULT_SAMPLES = 44100  # 1 second
DEFAULT_VOICES = 4
DEFAULT_PARTIALS = 8
WARMUP_RUNS = 3
BENCH_RUNS = 10

# Paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LATTICE_C = os.path.join(SCRIPT_DIR, "wasm_lattice", "lattice.c")
WASM_DIR = os.path.join(SCRIPT_DIR, "wasm_lattice")

# ============================================================================
# Python implementation (reference)
# ============================================================================

import math

def python_lattice(frequency, num_samples, sample_rate, num_voices, num_partials):
    """Pure Python lattice oscillator — the baseline."""
    # Lattice ratios
    RATIOS = [1.0, 1.5, 1.25, 1.875, 2.0, 2.25, 2.5, 3.125,
              1.333, 1.2, 1.6, 1.125, 2.667, 3.0, 3.125, 3.75]
    AMPS = [1.0, 0.6, 0.45, 0.3, 0.25, 0.15, 0.1, 0.05,
            0.4, 0.35, 0.3, 0.2, 0.18, 0.28, 0.15, 0.1]

    two_pi = 2.0 * math.pi
    output = [0.0] * num_samples

    for voice in range(num_voices):
        freq = frequency * (1 + voice * 0.01)  # Slight detune for realism
        for n in range(num_samples):
            t = n / sample_rate
            sample = 0.0
            for p in range(num_partials):
                angle = two_pi * freq * RATIOS[p] * t
                sample += AMPS[p] * math.sin(angle)
            output[n] += sample / (num_voices * num_partials)

    return output

def python_lattice_numpy(frequency, num_samples, sample_rate, num_voices, num_partials):
    """NumPy-optimized lattice oscillator."""
    try:
        import numpy as np
    except ImportError:
        return None

    RATIOS = np.array([1.0, 1.5, 1.25, 1.875, 2.0, 2.25, 2.5, 3.125,
                       1.333, 1.2, 1.6, 1.125, 2.667, 3.0, 3.125, 3.75],
                      dtype=np.float32)
    AMPS = np.array([1.0, 0.6, 0.45, 0.3, 0.25, 0.15, 0.1, 0.05,
                     0.4, 0.35, 0.3, 0.2, 0.18, 0.28, 0.15, 0.1],
                    dtype=np.float32)

    output = np.zeros(num_samples, dtype=np.float32)
    t = np.arange(num_samples, dtype=np.float32) / sample_rate

    for voice in range(num_voices):
        freq = frequency * (1 + voice * 0.01)
        for p in range(num_partials):
            angles = 2.0 * np.pi * freq * RATIOS[p] * t
            output += AMPS[p] * np.sin(angles)

    output /= (num_voices * num_partials)
    return output

# ============================================================================
# Native C benchmark (via ctypes)
# ============================================================================

def build_native_lib():
    """Compile lattice.c to a shared library."""
    lib_path = os.path.join(WASM_DIR, "lattice_bench.so")
    if os.path.exists(lib_path):
        # Check if source is newer
        if os.path.getmtime(lib_path) > os.path.getmtime(LATTICE_C):
            return lib_path

    # Build a standalone benchmark wrapper
    wrapper_c = os.path.join(WASM_DIR, "bench_wrapper.c")
    with open(wrapper_c, 'w') as f:
        f.write("""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Include the lattice oscillator */
#include "lattice.c"

/* Benchmark entry point */
void bench_lattice(float *output, int num_samples, int num_voices, int num_partials,
                   float frequency, int sample_rate) {
    lattice_init(num_voices, num_partials);

    /* Start all voices */
    for (int v = 0; v < num_voices; v++) {
        lattice_note_on(frequency * (1.0f + v * 0.01f));
    }

    lattice_process(output, num_samples);
}
""")

    cmd = [
        "gcc", "-O3", "-shared", "-fPIC",
        "-o", lib_path,
        wrapper_c, "-lm"
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=WASM_DIR)
        os.unlink(wrapper_c)
        return lib_path
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Warning: Could not build native library: {e}")
        return None

def benchmark_native(num_samples, num_voices, num_partials, frequency):
    """Benchmark native C via ctypes."""
    lib_path = build_native_lib()
    if lib_path is None:
        return None

    try:
        lib = ctypes.CDLL(lib_path)
    except OSError:
        return None

    lib.bench_lattice.restype = None
    lib.bench_lattice.argtypes = [
        ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_float, ctypes.c_int
    ]

    # Allocate output buffer
    buf = (ctypes.c_float * num_samples)()

    # Warmup
    for _ in range(WARMUP_RUNS):
        lib.bench_lattice(buf, num_samples, num_voices, num_partials,
                         ctypes.c_float(frequency), SAMPLE_RATE)

    # Benchmark
    times = []
    for _ in range(BENCH_RUNS):
        t0 = time.perf_counter()
        lib.bench_lattice(buf, num_samples, num_voices, num_partials,
                         ctypes.c_float(frequency), SAMPLE_RATE)
        t1 = time.perf_counter()
        times.append(t1 - t0)

    return {
        'times': times,
        'mean': statistics.mean(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'label': 'Native C (gcc -O3)'
    }

# ============================================================================
# WASM benchmark (via wasmtime)
# ============================================================================

def build_wasm():
    """Compile lattice.c to WASM."""
    wasm_path = os.path.join(WASM_DIR, "lattice_bench.wasm")
    if os.path.exists(wasm_path):
        if os.path.getmtime(wasm_path) > os.path.getmtime(LATTICE_C):
            return wasm_path

    cmd = [
        "emcc", "-O3", "-s", "STANDALONE_WASM",
        "-s", "WASM=1",
        "-s", f"EXPORTED_FUNCTIONS=['_lattice_init','_lattice_process','_lattice_note_on','_lattice_note_off','_lattice_set_dial']",
        "--no-entry",
        "-o", wasm_path,
        LATTICE_C
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return wasm_path
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Warning: Could not build WASM: {e}")
        return None

def benchmark_wasm(num_samples, num_voices, num_partials, frequency):
    """Benchmark WASM via wasmtime Python bindings."""
    try:
        import wasmtime
    except ImportError:
        print("Warning: wasmtime not installed (pip install wasmtime)")
        return None

    wasm_path = build_wasm()
    if wasm_path is None:
        return None

    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)
    module = wasmtime.Module.from_file(engine, wasm_path)

    # Create imports (stubs for math functions)
    memory = wasmtime.Memory(store, wasmtime.MemoryType(wasmtime.Limits(256, None)))

    def make_f32_func(fn):
        ty = wasmtime.FuncType([wasmtime.ValType.f32()], [wasmtime.ValType.f32])
        return wasmtime.Func(store, ty, fn)

    imports = [
        memory,
        make_f32_func(lambda x: math.exp(x)),   # expf
        make_f32_func(lambda x: math.sin(x)),   # sinf
        make_f32_func(lambda x: math.cos(x)),   # cosf
        make_f32_func(lambda x: math.log2(x)),  # log2f
    ]

    instance = wasmtime.Instance(store, module, imports)

    # Get exported functions
    init = instance.exports(store)["lattice_init"]
    process = instance.exports(store)["lattice_process"]
    note_on = instance.exports(store)["lattice_note_on"]

    # Allocate memory for output
    mem = instance.exports(store)["memory"]
    ptr = 1024  # Use offset past stack/data

    # Initialize
    init(store, num_voices, num_partials)

    # Start voices
    for v in range(num_voices):
        note_on(store, frequency * (1.0 + v * 0.01))

    # Warmup
    for _ in range(WARMUP_RUNS):
        process(store, ptr, num_samples)

    # Benchmark
    times = []
    for _ in range(BENCH_RUNS):
        t0 = time.perf_counter()
        process(store, ptr, num_samples)
        t1 = time.perf_counter()
        times.append(t1 - t0)

    return {
        'times': times,
        'mean': statistics.mean(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'label': 'WASM (wasmtime)'
    }

# ============================================================================
# Python benchmark
# ============================================================================

def benchmark_python(num_samples, num_voices, num_partials, frequency):
    """Benchmark pure Python implementation."""
    # Warmup
    for _ in range(WARMUP_RUNS):
        python_lattice(frequency, min(num_samples, 1000), SAMPLE_RATE,
                      num_voices, num_partials)

    # Benchmark
    times = []
    for _ in range(BENCH_RUNS):
        t0 = time.perf_counter()
        python_lattice(frequency, num_samples, SAMPLE_RATE,
                      num_voices, num_partials)
        t1 = time.perf_counter()
        times.append(t1 - t0)

    return {
        'times': times,
        'mean': statistics.mean(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'label': 'Python (pure)'
    }

def benchmark_numpy(num_samples, num_voices, num_partials, frequency):
    """Benchmark NumPy implementation."""
    # Warmup
    for _ in range(WARMUP_RUNS):
        python_lattice_numpy(frequency, min(num_samples, 1000), SAMPLE_RATE,
                            num_voices, num_partials)

    times = []
    for _ in range(BENCH_RUNS):
        t0 = time.perf_counter()
        python_lattice_numpy(frequency, num_samples, SAMPLE_RATE,
                            num_voices, num_partials)
        t1 = time.perf_counter()
        times.append(t1 - t0)

    return {
        'times': times,
        'mean': statistics.mean(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'label': 'Python (NumPy)'
    }

# ============================================================================
# Results formatting
# ============================================================================

def format_results(results, num_samples):
    """Print a comparison table."""
    print("\n" + "=" * 78)
    print(f"  LATTICE OSCILLATOR BENCHMARK — {num_samples} samples "
          f"({num_samples/SAMPLE_RATE:.2f}s @ {SAMPLE_RATE}Hz)")
    print("=" * 78)

    print(f"  {'Implementation':<22} {'Time (ms)':<12} {'± (ms)':<10} "
          f"{'Voices/s':<12} {'vs Native':<10}")
    print("  " + "-" * 66)

    # Find native baseline
    native_mean = None
    for r in results:
        if 'Native' in r['label'] and r is not None:
            native_mean = r['mean']
            break

    for r in results:
        if r is None:
            continue

        ms = r['mean'] * 1000
        sd = r['stdev'] * 1000
        voices_per_sec = num_samples / r['mean'] / SAMPLE_RATE if r['mean'] > 0 else 0

        if native_mean and native_mean > 0:
            ratio = r['mean'] / native_mean
            ratio_str = f"{ratio:.2f}×"
        else:
            ratio_str = "baseline"

        print(f"  {r['label']:<22} {ms:<12.3f} {sd:<10.3f} "
              f"{voices_per_sec:<12.1f} {ratio_str:<10}")

    print("=" * 78)

    # Summary
    native_result = next((r for r in results if r and 'Native' in r['label']), None)
    wasm_result = next((r for r in results if r and 'WASM' in r['label']), None)
    python_result = next((r for r in results if r and 'Python (pure)' in r['label']), None)

    print("\n  Summary:")
    if native_result:
        print(f"    Native C:  {native_result['mean']*1000:.3f}ms "
              f"({num_samples/native_result['mean']:.0f} samples/sec)")
    if wasm_result and native_result:
        overhead = (wasm_result['mean'] / native_result['mean'] - 1) * 100
        print(f"    WASM:      {wasm_result['mean']*1000:.3f}ms "
              f"({overhead:+.1f}% vs native)")
    if python_result and native_result:
        slowdown = python_result['mean'] / native_result['mean']
        print(f"    Python:    {python_result['mean']*1000:.3f}ms "
              f"({slowdown:.1f}× slower than native)")
    print()

# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Lattice Oscillator Benchmark')
    parser.add_argument('--samples', type=int, default=DEFAULT_SAMPLES,
                       help=f'Number of samples to generate (default: {DEFAULT_SAMPLES})')
    parser.add_argument('--voices', type=int, default=DEFAULT_VOICES,
                       help=f'Number of voices (default: {DEFAULT_VOICES})')
    parser.add_argument('--partials', type=int, default=DEFAULT_PARTIALS,
                       help=f'Number of partials (default: {DEFAULT_PARTIALS})')
    parser.add_argument('--frequency', type=float, default=440.0,
                       help='Base frequency in Hz (default: 440)')
    parser.add_argument('--runs', type=int, default=BENCH_RUNS,
                       help=f'Benchmark runs (default: {BENCH_RUNS})')
    args = parser.parse_args()

    global BENCH_RUNS
    BENCH_RUNS = args.runs

    print(f"\n  Lattice Oscillator Benchmark")
    print(f"  {'='*40}")
    print(f"  Samples:  {args.samples} ({args.samples/SAMPLE_RATE:.2f}s)")
    print(f"  Voices:   {args.voices}")
    print(f"  Partials: {args.partials}")
    print(f"  Base freq: {args.frequency} Hz")
    print(f"  Runs:     {args.runs} (+ {WARMUP_RUNS} warmup)")
    print()

    results = []

    # Run benchmarks
    print("  [1/4] Benchmarking Native C...")
    r = benchmark_native(args.samples, args.voices, args.partials, args.frequency)
    results.append(r)
    if r: print(f"        → {r['mean']*1000:.3f}ms")
    else: print("        → SKIPPED (build failed)")

    print("  [2/4] Benchmarking WASM...")
    r = benchmark_wasm(args.samples, args.voices, args.partials, args.frequency)
    results.append(r)
    if r: print(f"        → {r['mean']*1000:.3f}ms")
    else: print("        → SKIPPED (emscripten/wasmtime not available)")

    print("  [3/4] Benchmarking Python (pure)...")
    r = benchmark_python(args.samples, args.voices, args.partials, args.frequency)
    results.append(r)
    print(f"        → {r['mean']*1000:.3f}ms")

    print("  [4/4] Benchmarking Python (NumPy)...")
    r = benchmark_numpy(args.samples, args.voices, args.partials, args.frequency)
    results.append(r)
    if r: print(f"        → {r['mean']*1000:.3f}ms")
    else: print("        → SKIPPED (numpy not available)")

    # Print results
    format_results([r for r in results if r is not None], args.samples)

if __name__ == "__main__":
    main()
