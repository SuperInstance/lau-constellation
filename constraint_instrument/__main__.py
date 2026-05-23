"""
CLI entry point: python -m constraint_instrument

Commands:
  generate   — mode + terrain → notes → WAV
  render     — (re-render last performance — not yet wired)
  diagnose   — generate + run Goodman diagnostic
  terrains   — list all available terrains
"""

import argparse
import sys

from . import Instrument, TERRAINS


def cmd_terrains(_args):
    """List all available terrains."""
    print(f"Available terrains ({len(TERRAINS)}):\n")
    for name, t in TERRAINS.items():
        print(f"  {name:25s} {t.description}")
    print()


def cmd_generate(args):
    """Generate a performance and render to WAV."""
    inst = Instrument(mode=args.mode, terrain=args.terrain, key=args.key)
    result = inst.perform(bars=args.bars)
    output = args.output or f"{args.mode}_{args.terrain}.wav"
    path = inst.render(output, bpm=args.bpm)
    n_notes = len(result.get("notes", []))
    print(f"✓ Generated {n_notes} notes → {path}")


def cmd_diagnose(args):
    """Generate a performance and diagnose it."""
    inst = Instrument(mode="goodman", terrain=args.terrain, key=args.key)
    # First generate with a performer mode
    performer = Instrument(mode=args.mode, terrain=args.terrain, key=args.key)
    result = performer.perform(bars=args.bars)
    notes = result.get("notes", [])
    report = inst.diagnose(notes)
    print(report)


def main():
    parser = argparse.ArgumentParser(
        prog="constraint_instrument",
        description="Constraint-music instrument — seven modes, seventeen terrains.",
    )
    sub = parser.add_subparsers(dest="command")

    # terrains
    sub.add_parser("terrains", help="List all available terrains")

    # generate
    gen = sub.add_parser("generate", help="Generate a performance and render to WAV")
    gen.add_argument("--mode", required=True, choices=Instrument.MODES, help="Performance mode")
    gen.add_argument("--terrain", required=True, choices=list(TERRAINS.keys()), help="Terrain map")
    gen.add_argument("--bars", type=int, default=8, help="Number of bars (default: 8)")
    gen.add_argument("--key", type=int, default=60, help="MIDI key center (default: 60 = C4)")
    gen.add_argument("--bpm", type=int, default=120, help="Tempo in BPM (default: 120)")
    gen.add_argument("--output", "-o", default=None, help="Output WAV path")

    # diagnose
    diag = sub.add_parser("diagnose", help="Generate + diagnose a performance")
    diag.add_argument("--mode", required=True, choices=Instrument.MODES, help="Performance mode")
    diag.add_argument("--terrain", required=True, choices=list(TERRAINS.keys()), help="Terrain map")
    diag.add_argument("--bars", type=int, default=8, help="Number of bars (default: 8)")
    diag.add_argument("--key", type=int, default=60, help="MIDI key center (default: 60 = C4)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    commands = {
        "terrains": cmd_terrains,
        "generate": cmd_generate,
        "diagnose": cmd_diagnose,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
