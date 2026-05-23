"""
Constraint MCP Server — exposes the constraint-theory ecosystem as MCP tools
for Copilot for Eclipse.

Tools provided:
  - constraint_snap:      snap a pitch to the nearest Eisenstein lattice point
  - constraint_funnel:    apply gravitational pull toward a target pitch
  - constraint_diagnose:  run 4-order Goodman diagnostic on a sequence of notes
  - constraint_generate:  generate music in a given mode + terrain
  - constraint_render:    render notes to WAV audio bytes
  - constraint_terrain_list: list available musical terrains
"""

import json
import sys
import traceback
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

# ── Lazy imports for the constraint ecosystem ─────────────────────────────

_substrate = None
_instrument = None
_synth = None


def _get_substrate():
    global _substrate
    if _substrate is None:
        # Add parent directories so we can find constraint-substrate and constraint_instrument
        from pathlib import Path
        workspace = Path(__file__).resolve().parent.parent.parent
        sub_py = workspace / "constraint-substrate" / "python"
        if sub_py.exists():
            sys.path.insert(0, str(sub_py))
        import constraint_substrate as cs
        _substrate = cs
    return _substrate


def _get_instrument():
    global _instrument
    if _instrument is None:
        from pathlib import Path
        workspace = Path(__file__).resolve().parent.parent.parent
        inst_py = workspace / "constraint_instrument"
        if inst_py.exists():
            sys.path.insert(0, str(inst_py))
        import constraint_instrument as ci
        _instrument = ci
    return _instrument


def _get_synth():
    global _synth
    if _synth is None:
        from pathlib import Path
        workspace = Path(__file__).resolve().parent.parent.parent
        synth_py = workspace / "constraint-synth"
        if synth_py.exists():
            sys.path.insert(0, str(synth_py))
        import constraint_synth
        _synth = constraint_synth
    return _synth


# ── MCP Server ────────────────────────────────────────────────────────────

app = Server("constraint-ecosystem")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="constraint_snap",
            description=(
                "Snap a MIDI pitch to the nearest Eisenstein lattice point. "
                "Returns the snapped pitch and the lattice coordinates (a, b) "
                "where the Eisenstein integer is a + b·ω, ω = e^{2πi/3}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "pitch": {
                        "type": "integer",
                        "description": "MIDI pitch number (0-127, 60 = middle C)",
                    },
                    "key_root": {
                        "type": "integer",
                        "description": "Root pitch of the key (default: 0 = C). Used for relative lattice positioning.",
                        "default": 0,
                    },
                },
                "required": ["pitch"],
            },
        ),
        Tool(
            name="constraint_funnel",
            description=(
                "Apply gravitational funnel pull toward a target pitch. "
                "Returns the new pitch after one step of the funnel attractor, "
                "blending direction toward target with current position."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "current_pitch": {
                        "type": "integer",
                        "description": "Current MIDI pitch",
                    },
                    "target_pitch": {
                        "type": "integer",
                        "description": "Target MIDI pitch to gravitate toward",
                    },
                    "strength": {
                        "type": "number",
                        "description": "Funnel strength 0.0-1.0 (default: 0.5). Higher = stronger pull.",
                        "default": 0.5,
                    },
                },
                "required": ["current_pitch", "target_pitch"],
            },
        ),
        Tool(
            name="constraint_diagnose",
            description=(
                "Run a 4-order Goodman diagnostic on a sequence of musical notes. "
                "Evaluates: 0th (position/scale), 1st (direction/voice-leading), "
                "2nd (curvature/rhythm/dynamics), 3rd (structure/form). "
                "Returns per-order scores (0-5 stars) and actionable diagnoses."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "notes": {
                        "type": "array",
                        "description": "Sequence of note objects",
                        "items": {
                            "type": "object",
                            "properties": {
                                "pitch": {"type": "integer", "description": "MIDI pitch"},
                                "velocity": {"type": "integer", "description": "Velocity 0-127"},
                                "start": {"type": "number", "description": "Start time in beats"},
                                "duration": {"type": "number", "description": "Duration in beats"},
                            },
                            "required": ["pitch"],
                        },
                    },
                    "terrain_name": {
                        "type": "string",
                        "description": "Terrain to diagnose against (e.g. 'bebop', 'delta_blues'). Default: 'bebop'.",
                        "default": "bebop",
                    },
                },
                "required": ["notes"],
            },
        ),
        Tool(
            name="constraint_generate",
            description=(
                "Generate a musical phrase in a given mode and terrain. "
                "Uses the constraint instrument system (Parker/Miles/Ellington/etc. modes) "
                "to produce note sequences that satisfy lattice, funnel, and terrain constraints."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Instrument mode: parker, miles, ellington, basie, goodman, armstrong, ella",
                        "enum": [
                            "parker", "miles", "ellington", "basie",
                            "goodman", "armstrong", "ella",
                        ],
                    },
                    "terrain": {
                        "type": "string",
                        "description": "Musical terrain name (use constraint_terrain_list to see options)",
                    },
                    "bars": {
                        "type": "integer",
                        "description": "Number of bars to generate (default: 4)",
                        "default": 4,
                    },
                    "key_root": {
                        "type": "integer",
                        "description": "Root pitch in MIDI (default: 60 = C4)",
                        "default": 60,
                    },
                },
                "required": ["mode", "terrain"],
            },
        ),
        Tool(
            name="constraint_render",
            description=(
                "Render a sequence of notes to WAV audio. "
                "Returns base64-encoded WAV data that can be played or saved."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "notes": {
                        "type": "array",
                        "description": "Notes to render",
                        "items": {
                            "type": "object",
                            "properties": {
                                "pitch": {"type": "integer"},
                                "velocity": {"type": "integer", "default": 80},
                                "start": {"type": "number"},
                                "duration": {"type": "number", "default": 0.5},
                            },
                            "required": ["pitch", "start"],
                        },
                    },
                    "preset": {
                        "type": "string",
                        "description": "Synth preset: piano, saxophone, guitar, bass, drums",
                        "default": "piano",
                    },
                    "bpm": {
                        "type": "integer",
                        "description": "Tempo in BPM (default: 120)",
                        "default": 120,
                    },
                    "sample_rate": {
                        "type": "integer",
                        "description": "Sample rate (default: 44100)",
                        "default": 44100,
                    },
                },
                "required": ["notes"],
            },
        ),
        Tool(
            name="constraint_terrain_list",
            description=(
                "List all available musical terrains (bathymetric maps of constraint space). "
                "Each terrain defines scale degrees, rhythmic skeletons, register tendencies, "
                "and chromatic density for a specific musical tradition."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        if name == "constraint_snap":
            return await _handle_snap(arguments)
        elif name == "constraint_funnel":
            return await _handle_funnel(arguments)
        elif name == "constraint_diagnose":
            return await _handle_diagnose(arguments)
        elif name == "constraint_generate":
            return await _handle_generate(arguments)
        elif name == "constraint_render":
            return await _handle_render(arguments)
        elif name == "constraint_terrain_list":
            return await _handle_terrain_list(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        tb = traceback.format_exc()
        return [TextContent(type="text", text=f"Error: {e}\n\nTraceback:\n{tb}")]


# ── Tool handlers ─────────────────────────────────────────────────────────

async def _handle_snap(args: dict) -> list[TextContent]:
    cs = _get_substrate()
    pitch = args["pitch"]
    key_root = args.get("key_root", 0)

    snapped = cs.snap(pitch, key_root)
    # snap returns (pitch, (a, b)) or just pitch depending on API
    if isinstance(snapped, tuple):
        snapped_pitch, coords = snapped
    else:
        snapped_pitch = snapped
        coords = None

    result = {
        "input_pitch": pitch,
        "key_root": key_root,
        "snapped_pitch": snapped_pitch,
        "offset": snapped_pitch - pitch,
    }
    if coords:
        result["lattice_coords"] = {"a": coords[0], "b": coords[1]}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def _handle_funnel(args: dict) -> list[TextContent]:
    cs = _get_substrate()
    current = args["current_pitch"]
    target = args["target_pitch"]
    strength = args.get("strength", 0.5)

    # funnel_step(current_state, target, strength) -> new_state
    # The substrate funnel works on generalized state; for MIDI we use it directly
    new_pitch = cs.funnel_step(current, target, strength)

    result = {
        "current_pitch": current,
        "target_pitch": target,
        "strength": strength,
        "result_pitch": new_pitch if isinstance(new_pitch, (int, float)) else current,
        "distance_to_target": abs(target - (new_pitch if isinstance(new_pitch, (int, float)) else current)),
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def _handle_diagnose(args: dict) -> list[TextContent]:
    from constraint_instrument.goodman import Goodman
    notes = args["notes"]
    terrain_name = args.get("terrain_name", "bebop")

    goodman = Goodman()
    # Normalize notes
    normalized = []
    for n in notes:
        normalized.append({
            "pitch": n["pitch"],
            "velocity": n.get("velocity", 80),
            "start": n.get("start", 0.0),
            "duration": n.get("duration", 0.5),
        })

    report = goodman.diagnose(normalized, terrain=terrain_name)

    # Serialize the diagnostic report
    orders = []
    for os_ in report.orders:
        orders.append({
            "order": os_.order,
            "name": os_.name,
            "score": round(os_.score, 3),
            "stars": os_.stars,
            "components": {k: round(v, 3) for k, v in os_.components.items()},
            "diagnosis": os_.diagnosis,
        })

    result = {
        "terrain": terrain_name,
        "note_count": len(normalized),
        "overall_score": round(report.overall_score, 3),
        "overall_stars": report.overall_stars,
        "orders": orders,
        "summary": report.summary,
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def _handle_generate(args: dict) -> list[TextContent]:
    ci = _get_instrument()
    mode = args["mode"]
    terrain_name = args["terrain"]
    bars = args.get("bars", 4)
    key_root = args.get("key_root", 60)

    inst = ci.Instrument(mode=mode, terrain=terrain_name, key_root=key_root)
    phrase = inst.generate(bars=bars)

    # phrase is a list of note dicts
    notes_out = []
    for n in phrase:
        notes_out.append({
            "pitch": n["pitch"] if isinstance(n, dict) else n,
            "velocity": n.get("velocity", 80) if isinstance(n, dict) else 80,
            "start": n.get("start", 0.0) if isinstance(n, dict) else 0.0,
            "duration": n.get("duration", 0.5) if isinstance(n, dict) else 0.5,
        })

    result = {
        "mode": mode,
        "terrain": terrain_name,
        "bars": bars,
        "key_root": key_root,
        "notes": notes_out,
        "note_count": len(notes_out),
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def _handle_render(args: dict) -> list[TextContent]:
    import base64
    import io
    import struct
    import math

    notes = args["notes"]
    preset = args.get("preset", "piano")
    bpm = args.get("bpm", 120)
    sample_rate = args.get("sample_rate", 44100)

    # Simple WAV renderer — generates sine-wave based audio
    # In production, this would use constraint_synth
    beat_duration = 60.0 / bpm  # seconds per beat
    total_beats = max(n["start"] + n.get("duration", 0.5) for n in notes) if notes else 4.0
    total_samples = int(total_beats * beat_duration * sample_rate) + sample_rate  # 1 sec padding

    # Mix all notes
    audio = [0.0] * total_samples
    freq_map = {
        "piano": 1.0, "saxophone": 0.8, "guitar": 0.9,
        "bass": 1.2, "drums": 0.5,
    }
    harmonic = freq_map.get(preset, 1.0)

    for note in notes:
        freq = 440.0 * (2.0 ** ((note["pitch"] - 69) / 12.0))
        vel = note.get("velocity", 80) / 127.0
        start_sample = int(note["start"] * beat_duration * sample_rate)
        duration_samples = int(note.get("duration", 0.5) * beat_duration * sample_rate)

        for i in range(min(duration_samples, total_samples - start_sample)):
            t = i / sample_rate
            env = min(1.0, i / (0.01 * sample_rate)) * min(1.0, (duration_samples - i) / (0.05 * sample_rate))
            # Simple additive synthesis
            sample = vel * env * (
                math.sin(2 * math.pi * freq * t) * 0.6 +
                math.sin(2 * math.pi * freq * 2 * t) * 0.2 * harmonic +
                math.sin(2 * math.pi * freq * 3 * t) * 0.1 * harmonic
            )
            audio[start_sample + i] += sample

    # Normalize
    peak = max(abs(s) for s in audio) if audio else 1.0
    if peak > 0:
        audio = [s / peak * 0.8 for s in audio]

    # Encode as WAV
    buf = io.BytesIO()
    num_samples = len(audio)
    data_size = num_samples * 2  # 16-bit

    buf.write(b'RIFF')
    buf.write(struct.pack('<I', 36 + data_size))
    buf.write(b'WAVE')
    buf.write(b'fmt ')
    buf.write(struct.pack('<IHHIIHH', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
    buf.write(b'data')
    buf.write(struct.pack('<I', data_size))
    for s in audio:
        buf.write(struct.pack('<h', int(s * 32767)))

    wav_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    result = {
        "preset": preset,
        "bpm": bpm,
        "sample_rate": sample_rate,
        "duration_seconds": round(total_beats * beat_duration, 2),
        "note_count": len(notes),
        "wav_base64_length": len(wav_b64),
        "wav_base64": wav_b64,
    }
    return [TextContent(type="text", text=json.dumps(result))]


async def _handle_terrain_list(args: dict) -> list[TextContent]:
    ci = _get_instrument()
    terrains = []
    for name, terrain in ci.TERRAINS.items():
        terrains.append({
            "name": name,
            "display_name": getattr(terrain, "display_name", name),
            "description": getattr(terrain, "description", ""),
            "scale_degrees": len(getattr(terrain, "scale_degrees", [])),
        })

    result = {
        "terrain_count": len(terrains),
        "terrains": terrains,
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


# ── Entry point ───────────────────────────────────────────────────────────

async def _run():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    import asyncio
    asyncio.run(_run())


if __name__ == "__main__":
    main()
