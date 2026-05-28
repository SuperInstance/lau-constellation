"""CLI for constraint-toolkit."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

# ANSI color helpers
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
RESET = "\033[0m"


def _color(text: str, *codes: str) -> str:
    return "".join(codes) + text + RESET


def _table(headers: list[str], rows: list[list[str]], widths: Optional[list[int]] = None) -> str:
    """Format a simple ASCII table."""
    if widths is None:
        widths = [max(len(h), *(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]

    def row(cells: list[str]) -> str:
        parts = []
        for i, (c, w) in enumerate(zip(cells, widths)):
            parts.append(str(c).ljust(w))
        return "  ".join(parts)

    lines = [
        _color(row(headers), BOLD),
        _color("  ".join("─" * w for w in widths), DIM),
    ]
    for r in rows:
        lines.append(row(r))
    return "\n".join(lines)


# ── Commands ──────────────────────────────────────────────────────────

def cmd_analyze(args: argparse.Namespace) -> int:
    from .analyzer import analyze_wav, analyze_midi
    from .dials import DIAL_RANGES

    path = Path(args.path)
    if not path.exists():
        print(_color(f"Error: file not found: {path}", RED, BOLD))
        return 1

    ext = path.suffix.lower()
    try:
        if ext in (".wav", ".mp3", ".flac", ".ogg", ".aiff"):
            result = analyze_wav(str(path))
        elif ext in (".mid", ".midi"):
            result = analyze_midi(str(path))
        else:
            print(_color(f"Error: unsupported file type: {ext}", RED, BOLD))
            return 1
    except Exception as e:
        print(_color(f"Error analyzing file: {e}", RED, BOLD))
        return 1

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, default=str))
        return 0

    # Pretty output
    print(_color(f"\n  Analysis: {path.name}", BOLD, CYAN))
    print(_color(f"  {'─' * 40}", DIM))

    dp = result.dial_position
    headers = ["Dial", "Value"]
    rows = [
        ["Harmonic Tension", f"{dp.harmonic_tension:.2f}"],
        ["Rhythmic Complexity", f"{dp.rhythmic_complexity:.2f}"],
        ["Spectral Density", f"{dp.spectral_density:.2f}"],
    ]
    print()
    print(_table(headers, rows, widths=[22, 10]))

    if args.verbose and result.features:
        print()
        print(_color("  Features:", BOLD))
        for k, v in result.features.items() if isinstance(result.features, dict) else []:
            print(f"    {k}: {v}")

    if result.suggested_tradition:
        print(f"\n  Suggested tradition: {_color(result.suggested_tradition, GREEN, BOLD)}")

    print()
    return 0


def cmd_classify(args: argparse.Namespace) -> int:
    from .analyzer import analyze_wav, analyze_midi
    from .classifier import DialClassifier

    path = Path(args.path)
    if not path.exists():
        print(_color(f"Error: file not found: {path}", RED, BOLD))
        return 1

    ext = path.suffix.lower()
    try:
        if ext in (".wav", ".mp3", ".flac", ".ogg", ".aiff"):
            result = analyze_wav(str(path))
        else:
            result = analyze_midi(str(path))
    except Exception as e:
        print(_color(f"Error analyzing file: {e}", RED, BOLD))
        return 1

    clf = DialClassifier()
    clf.fit_defaults()
    pred = clf.predict_result(result.dial_position)

    print(_color(f"\n  Classification: {path.name}", BOLD, CYAN))
    print(_color(f"  {'─' * 40}", DIM))
    print(f"  Genre:  {_color(pred.genre, GREEN, BOLD)}")
    print(f"  Confidence: {pred.confidence:.1%}")
    if pred.novelty is not None:
        print(f"  Novelty: {pred.novelty:.2f}")
    print()
    return 0


def cmd_compose(args: argparse.Namespace) -> int:
    from .composer import ConstraintComposer

    composer = ConstraintComposer()

    kwargs = {}
    if args.tradition:
        kwargs["tradition"] = args.tradition
    if args.harmonic is not None:
        kwargs["harmonic_tension"] = args.harmonic
    if args.rhythmic is not None:
        kwargs["rhythmic_complexity"] = args.rhythmic
    if args.spectral is not None:
        kwargs["spectral_density"] = args.spectral

    print(_color("\n  Composing...", BOLD, CYAN))

    try:
        midi = composer.compose(
            bars=args.bars,
            tempo=args.tempo,
            **kwargs,
        )
    except Exception as e:
        print(_color(f"Error composing: {e}", RED, BOLD))
        return 1

    output = args.output or "output.mid"

    if output.endswith(".wav"):
        from .synthesizer import ConstraintSynth
        from .dials import DialPosition

        synth = ConstraintSynth()
        dial = None
        if args.harmonic is not None or args.rhythmic is not None or args.spectral is not None:
            dial = DialPosition(
                harmonic_tension=args.harmonic or 2.5,
                rhythmic_complexity=args.rhythmic or 2.5,
                spectral_density=args.spectral or 2.5,
            )
        audio = synth.render_midi(midi, dial_target=dial, bpm=args.tempo)
        synth.save_wav(audio, output)
        print(_color(f"  ✓ Saved WAV: {output}", GREEN))
    else:
        midi.save(output)
        print(_color(f"  ✓ Saved MIDI: {output}", GREEN))

    print()
    return 0


def cmd_transfer(args: argparse.Namespace) -> int:
    from .style_transfer import StyleTransfer

    st = StyleTransfer()
    print(_color(f"\n  Transferring style → {args.target}...", BOLD, CYAN))

    try:
        result = st.transfer(args.input, target_tradition=args.target)
    except Exception as e:
        print(_color(f"Error: {e}", RED, BOLD))
        return 1

    result.save(args.output)
    print(_color(f"  ✓ Saved: {args.output}", GREEN))
    print()
    return 0


def cmd_optimize(args: argparse.Namespace) -> int:
    from mido import MidiFile
    from .optimizer import GrooveOptimizer

    if not Path(args.input).exists():
        print(_color(f"Error: file not found: {args.input}", RED, BOLD))
        return 1

    mid = MidiFile(args.input)
    opt = GrooveOptimizer()

    print(_color(f"\n  Optimizing groove for {args.target}...", BOLD, CYAN))
    print(f"  Iterations: {args.iterations}")

    try:
        result = opt.optimize(mid, genre=args.target, iterations=args.iterations)
    except Exception as e:
        print(_color(f"Error: {e}", RED, BOLD))
        return 1

    print(_color(f"\n  Result:", BOLD))
    print(f"  Fitness: {result.fitness:.4f}")
    print(f"  Generations: {result.generations}")
    print()

    result.midi.save(args.output)
    print(_color(f"  ✓ Saved: {args.output}", GREEN))
    print()
    return 0


def cmd_stress_test(args: argparse.Namespace) -> int:
    from .conservation import stress_test

    print(_color(f"\n  Running conservation stress test (n={args.n})...", BOLD, CYAN))

    results = stress_test(n_sequences=args.n)

    headers = ["Metric", "Value"]
    rows = [
        ["Sequences", str(results.get("n_sequences", args.n))],
        ["Mean Sum (I_v+I_h)", f"{results.get('mean_sum', 0):.4f}"],
        ["Std Sum", f"{results.get('std_sum', 0):.4f}"],
        ["CV", f"{results.get('cv', 0):.4f}"],
        ["Correlation (v↔h)", f"{results.get('correlation', 0):.4f}"],
        ["ET Mean", f"{results.get('et_mean', 0):.4f}"],
        ["Meantone Mean", f"{results.get('meantone_mean', 0):.4f}"],
    ]
    print()
    print(_table(headers, rows, widths=[20, 16]))
    print()
    return 0


def cmd_dial_map(args: argparse.Namespace) -> int:
    from .dials import DIAL_RANGES

    print(_color("\n  Dial Space Map", BOLD, CYAN))
    print(_color(f"  {'─' * 60}", DIM))
    print()

    headers = ["Tradition", "H.Tension", "R.Complex", "S.Density"]
    rows = []
    for name, data in DIAL_RANGES.items():
        center = data["center"]
        rows.append([
            name,
            f"{center[0]:.2f}",
            f"{center[1]:.2f}",
            f"{center[2]:.2f}",
        ])
    print(_table(headers, rows))
    print()
    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    from .benchmarks import BenchmarkSuite

    print(_color("\n  Running benchmarks...", BOLD, CYAN))
    suite = BenchmarkSuite()
    report = suite.run_all()

    print(report.format_report())
    return 0


def cmd_recommend(args: argparse.Namespace) -> int:
    from .recommender import Recommender
    from .analyzer import analyze_wav, analyze_midi

    path = Path(args.path)
    if not path.exists():
        print(_color(f"Error: file not found: {path}", RED, BOLD))
        return 1

    ext = path.suffix.lower()
    try:
        if ext in (".wav", ".mp3", ".flac", ".ogg", ".aiff"):
            analysis = analyze_wav(str(path))
        else:
            analysis = analyze_midi(str(path))
    except Exception as e:
        print(_color(f"Error analyzing file: {e}", RED, BOLD))
        return 1

    rec = Recommender()
    recommendations = rec.recommend(str(path), n=args.n)

    print(_color(f"\n  Recommendations for {path.name}", BOLD, CYAN))
    print(_color(f"  {'─' * 50}", DIM))
    print()

    headers = ["#", "Tradition", "Distance", "Adventure", "Fusion"]
    rows = []
    for i, r in enumerate(recommendations[: args.n], 1):
        rows.append([
            str(i),
            r.tradition_name,
            f"{r.distance:.3f}",
            f"{r.adventure_factor:.2f}",
            f"{r.fusion_viability:.2f}",
        ])
    print(_table(headers, rows))
    print()
    return 0


# ── Main ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="constraint-toolkit",
        description="Music analysis toolkit based on Dials Not Laws theory",
    )
    parser.add_argument("--version", "-V", action="version", version="%(prog)s 0.1.0")
    subparsers = parser.add_subparsers(dest="command")

    # analyze
    p_analyze = subparsers.add_parser("analyze", help="Analyze a WAV or MIDI file")
    p_analyze.add_argument("path", help="Path to file")
    p_analyze.add_argument("--verbose", "-v", action="store_true")
    p_analyze.add_argument("--json", action="store_true", help="Output as JSON")

    # classify
    p_classify = subparsers.add_parser("classify", help="Classify genre of a file")
    p_classify.add_argument("path")

    # compose
    p_compose = subparsers.add_parser("compose", help="Compose music")
    p_compose.add_argument("--tradition", "-t", help="Tradition to compose in")
    p_compose.add_argument("--harmonic", "-H", type=float, help="Target harmonic tension 0-5")
    p_compose.add_argument("--rhythmic", "-R", type=float, help="Target rhythmic complexity 0-5")
    p_compose.add_argument("--spectral", "-S", type=float, help="Target spectral density 0-5")
    p_compose.add_argument("--bars", type=int, default=8)
    p_compose.add_argument("--tempo", type=int, default=120)
    p_compose.add_argument("--output", "-o", help="Output path (.mid or .wav)")

    # transfer
    p_transfer = subparsers.add_parser("transfer", help="Style transfer")
    p_transfer.add_argument("input", help="Input file")
    p_transfer.add_argument("--target", "-t", required=True, help="Target tradition")
    p_transfer.add_argument("--output", "-o", required=True)

    # optimize
    p_optimize = subparsers.add_parser("optimize", help="Optimize groove")
    p_optimize.add_argument("input", help="Input MIDI file")
    p_optimize.add_argument("--target", "-t", required=True, help="Target tradition")
    p_optimize.add_argument("--output", "-o", required=True)
    p_optimize.add_argument("--iterations", type=int, default=100)

    # stress-test
    p_stress = subparsers.add_parser("stress-test", help="Conservation stress test")
    p_stress.add_argument("--n", type=int, default=10000)

    # dial-map
    p_dial = subparsers.add_parser("dial-map", help="Show dial space map")

    # benchmark
    p_bench = subparsers.add_parser("benchmark", help="Run benchmarks")

    # recommend
    p_rec = subparsers.add_parser("recommend", help="Recommend similar traditions")
    p_rec.add_argument("path", help="Query file")
    p_rec.add_argument("--n", type=int, default=5)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "analyze": cmd_analyze,
        "classify": cmd_classify,
        "compose": cmd_compose,
        "transfer": cmd_transfer,
        "optimize": cmd_optimize,
        "stress-test": cmd_stress_test,
        "dial-map": cmd_dial_map,
        "benchmark": cmd_benchmark,
        "recommend": cmd_recommend,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        print(_color(f"Unknown command: {args.command}", RED, BOLD))
        sys.exit(1)

    rc = handler(args)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
