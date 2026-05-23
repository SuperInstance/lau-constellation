"""
Terrain Morphing — crossfading between musical landscapes.

Like a DJ crossfading between genres, but at the constraint level:
the scale morphs, the gravity centers shift, the rigidity changes.
A terrain blend at t=0.3 is 30% target terrain, 70% source —
the scale degrees interpolate, the chromatic density blends,
and the rhythmic skeletons crossfade.

Usage:
    python -m constraint_instrument.terrain_morph blues bebop --steps 8
"""

import argparse
import copy
import math
import sys
from typing import Dict, List, Optional, Tuple

from .terrain import ScaleDegree, RhythmicSkeleton, Terrain
from .terrain import TERRAINS


# ── Helpers ──────────────────────────────────────────────────────────

def _load_terrain(name: str) -> Terrain:
    """Load a terrain by name from the registry."""
    if name not in TERRAINS:
        available = ", ".join(sorted(TERRAINS.keys()))
        raise ValueError(f"Unknown terrain '{name}'. Available: {available}")
    return copy.deepcopy(TERRAINS[name])


def _interpolate(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b at position t."""
    return a + (b - a) * t


def _blend_scale_degrees(
    source: List[ScaleDegree],
    target: List[ScaleDegree],
    t: float,
) -> List[ScaleDegree]:
    """Blend two scale degree lists into one unified set.
    
    Strategy:
    - Collect all unique degrees from both terrains
    - Source-only degrees fade out (weight * (1-t))
    - Target-only degrees fade in (weight * t)
    - Shared degrees interpolate linearly
    - Remove degrees below a small threshold (0.05) to keep it clean
    """
    source_map = {sd.degree: sd for sd in source}
    target_map = {sd.degree: sd for sd in target}
    
    all_degrees = sorted(set(source_map.keys()) | set(target_map.keys()))
    
    result = []
    for deg in all_degrees:
        in_source = deg in source_map
        in_target = deg in target_map
        
        if in_source and in_target:
            # Shared: interpolate weight
            weight = _interpolate(source_map[deg].weight, target_map[deg].weight, t)
            # Name: use source name if mostly source, target name if mostly target
            if t < 0.5:
                name = source_map[deg].name
            else:
                name = target_map[deg].name
            blues = source_map[deg].blues_note or target_map[deg].blues_note
        elif in_source:
            # Source-only: fade out
            weight = source_map[deg].weight * (1.0 - t)
            name = source_map[deg].name
            blues = source_map[deg].blues_note
        else:
            # Target-only: fade in
            weight = target_map[deg].weight * t
            name = target_map[deg].name
            blues = target_map[deg].blues_note
        
        # Drop negligible degrees
        if weight >= 0.05:
            result.append(ScaleDegree(
                degree=deg,
                weight=round(weight, 4),
                name=name,
                blues_note=blues,
            ))
    
    return result


def _blend_rhythmic_skeletons(
    source: List[RhythmicSkeleton],
    target: List[RhythmicSkeleton],
    t: float,
) -> List[RhythmicSkeleton]:
    """Blend rhythmic skeletons.
    
    Strategy: crossfade — source skeletons get a crossfade weight of (1-t),
    target skeletons get t. We return the source skeletons with reduced swing
    morphing toward the target's average, plus target skeletons weighted in.
    """
    skeletons = []
    
    # Source skeletons with fading swing toward target average
    if source:
        target_avg_swing = sum(s.swing for s in target) / max(len(target), 1)
        for sk in source:
            blended_swing = _interpolate(sk.swing, target_avg_swing, t)
            skeletons.append(RhythmicSkeleton(
                name=f"{sk.name}→fade",
                subdivisions=sk.subdivisions[:],
                accents=sk.accents[:],
                swing=round(blended_swing, 3),
            ))
    
    # Target skeletons with increasing presence
    if target:
        source_avg_swing = sum(s.swing for s in source) / max(len(source), 1)
        for sk in target:
            blended_swing = _interpolate(source_avg_swing, sk.swing, t)
            skeletons.append(RhythmicSkeleton(
                name=f"fade→{sk.name}",
                subdivisions=sk.subdivisions[:],
                accents=sk.accents[:],
                swing=round(blended_swing, 3),
            ))
    
    return skeletons


def _snap_note_to_terrain(note_midi: int, degrees: List[ScaleDegree], root: int = 60) -> int:
    """Snap a MIDI note to the nearest scale degree in the terrain.
    
    Finds the closest degree (by semitone distance) and returns the
    MIDI note at that degree offset from the root.
    """
    if not degrees:
        return note_midi
    
    pitch_class = note_midi % 12
    root_pc = root % 12
    
    # Find the closest degree
    best_degree = degrees[0].degree
    best_dist = abs(((pitch_class - root_pc + 6) % 12) - best_degree)
    best_dist = min(
        abs(((pitch_class - root_pc) % 12) - d.degree)
        for d in degrees
    ) if degrees else 0
    
    # Actually compute properly
    best_degree = None
    best_dist = 999
    for d in degrees:
        dist = abs(((pitch_class - root_pc) % 12) - d.degree)
        if dist < best_dist:
            best_dist = dist
            best_degree = d.degree
    
    # Place in the same octave
    octave = note_midi // 12
    snapped = octave * 12 + (root_pc + best_degree) % 12
    
    # Prefer the closest octave to original
    candidates = [snapped - 12, snapped, snapped + 12]
    return min(candidates, key=lambda n: abs(n - note_midi))


# ── Main Morpher ────────────────────────────────────────────────────

class TerrainMorpher:
    """Smoothly interpolate between two musical terrains.
    
    Like a DJ crossfading between genres, but at the constraint level —
    the scale morphs, the gravity centers shift, the rigidity changes.
    """
    
    def __init__(self, source: str, target: str):
        self.source_name = source
        self.target_name = target
        self.source = _load_terrain(source)
        self.target = _load_terrain(target)
    
    def blend(self, t: float) -> Terrain:
        """Return a blended terrain at position t (0.0=source, 1.0=target).
        
        At t=0: pure source terrain
        At t=0.5: something between source and target
        At t=1.0: pure target terrain
        
        The scale morphs by interpolating degree weights.
        The rhythmic skeletons crossfade.
        The register, chromatic density, and tempo interpolate linearly.
        """
        t = max(0.0, min(1.0, t))
        
        blended_degrees = _blend_scale_degrees(
            self.source.scale_degrees,
            self.target.scale_degrees,
            t,
        )
        
        # Blend characteristic intervals: union of both, weighted
        source_intervals = set(self.source.characteristic_intervals)
        target_intervals = set(self.target.characteristic_intervals)
        if t < 0.5:
            intervals = list(source_intervals) + [
                i for i in target_intervals if i not in source_intervals
            ]
        else:
            intervals = list(target_intervals) + [
                i for i in source_intervals if i not in target_intervals
            ]
        
        blended_skeletons = _blend_rhythmic_skeletons(
            self.source.rhythmic_skeletons,
            self.target.rhythmic_skeletons,
            t,
        )
        
        blended_register = (
            int(_interpolate(self.source.register_tendency[0], self.target.register_tendency[0], t)),
            int(_interpolate(self.source.register_tendency[1], self.target.register_tendency[1], t)),
        )
        
        blended_chromatic = round(
            _interpolate(self.source.chromatic_density, self.target.chromatic_density, t), 3
        )
        
        blended_tempo = (
            int(_interpolate(self.source.typical_tempo[0], self.target.typical_tempo[0], t)),
            int(_interpolate(self.source.typical_tempo[1], self.target.typical_tempo[1], t)),
        )
        
        name_prefix = self.source.name
        name_suffix = self.target.name
        blend_pct = int(t * 100)
        
        return Terrain(
            name=f"{name_prefix}→{name_suffix}@{blend_pct}%",
            description=(
                f"Blend {blend_pct}% from {self.source.description[:50]}… "
                f"to {self.target.description[:50]}…"
            ),
            scale_degrees=blended_degrees,
            characteristic_intervals=intervals[:8],  # cap at 8
            rhythmic_skeletons=blended_skeletons,
            register_tendency=blended_register,
            chromatic_density=blended_chromatic,
            typical_tempo=blended_tempo,
        )
    
    def morph_performance(
        self,
        notes: List[int],
        steps: int = 8,
        root: int = 60,
    ) -> List[Tuple[Terrain, List[int]]]:
        """Take a performance (list of MIDI note numbers) and morph the
        terrain underneath it.
        
        Returns a list of (terrain_state, transformed_notes) tuples,
        one per step. The notes are re-snapped to each blended terrain.
        """
        results = []
        for i in range(steps):
            t = i / max(steps - 1, 1)
            terrain = self.blend(t)
            snapped = [_snap_note_to_terrain(n, terrain.scale_degrees, root) for n in notes]
            results.append((terrain, snapped))
        return results


# ── Predefined Morph Paths ──────────────────────────────────────────

MORPH_PATHS = {
    "blues_to_bebop": ("delta_blues", "bebop_rich"),
    "classical_to_free": ("classical_counterpoint", "free_improvisation"),
    "techno_to_raga": ("electronic_techno", "indian_raga"),
    "jazz_to_silk": ("modal_jazz", "chinese_silk_bamboo"),
}


def get_morpher(path_name: str) -> TerrainMorpher:
    """Get a morpher for a predefined morph path."""
    if path_name not in MORPH_PATHS:
        available = ", ".join(sorted(MORPH_PATHS.keys()))
        raise ValueError(f"Unknown morph path '{path_name}'. Available: {available}")
    source, target = MORPH_PATHS[path_name]
    return TerrainMorpher(source, target)


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Morph between two musical terrains"
    )
    parser.add_argument("source", help="Source terrain name")
    parser.add_argument("target", help="Target terrain name")
    parser.add_argument("--steps", type=int, default=8, help="Number of morph steps")
    parser.add_argument("--path", help="Use a predefined morph path instead of source/target")
    args = parser.parse_args()
    
    if args.path:
        morpher = get_morpher(args.path)
    else:
        morpher = TerrainMorpher(args.source, args.target)
    
    print(f"╔══════════════════════════════════════════════════════════════╗")
    print(f"║  Terrain Morph: {morpher.source_name} → {morpher.target_name}")
    print(f"║  Steps: {args.steps}")
    print(f"╚══════════════════════════════════════════════════════════════╝")
    print()
    
    for i in range(args.steps):
        t = i / max(args.steps - 1, 1)
        terrain = morpher.blend(t)
        
        print(f"── Step {i+1}/{args.steps} (t={t:.2f}) ──")
        print(f"   Terrain: {terrain.name}")
        print(f"   Chromatic density: {terrain.chromatic_density:.3f}")
        print(f"   Register: {terrain.register_tendency[0]}–{terrain.register_tendency[1]}")
        print(f"   Tempo: {terrain.typical_tempo[0]}–{terrain.typical_tempo[1]} BPM")
        print(f"   Scale degrees:")
        
        for sd in terrain.scale_degrees:
            bar_len = int(sd.weight * 30)
            bar = "█" * bar_len + "░" * (30 - bar_len)
            blues_marker = " ♫" if sd.blues_note else ""
            print(f"     {sd.degree:2d} ({sd.name:20s}) {bar} {sd.weight:.3f}{blues_marker}")
        
        print()


if __name__ == "__main__":
    main()
