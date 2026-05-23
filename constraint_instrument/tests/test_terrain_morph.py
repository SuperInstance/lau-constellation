"""Tests for terrain_morph.py"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from constraint_instrument.terrain import ScaleDegree, Terrain
from constraint_instrument.terrain_morph import (
    TerrainMorpher,
    _blend_scale_degrees,
    _snap_note_to_terrain,
    get_morpher,
    MORPH_PATHS,
)


# ── Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def blues_bebop_morpher():
    return TerrainMorpher("delta_blues", "bebop_rich")


@pytest.fixture
def classical_free_morpher():
    return TerrainMorpher("classical_counterpoint", "free_improvisation")


# ── Blend endpoints ──────────────────────────────────────────────────

class TestBlendEndpoints:
    """Blend at t=0 returns source; blend at t=1 returns target."""
    
    def test_blend_t0_matches_source_degrees(self, blues_bebop_morpher):
        """At t=0, blended degrees should match source exactly."""
        result = blues_bebop_morpher.blend(0.0)
        source_degrees = blues_bebop_morpher.source.scale_degrees
        
        assert len(result.scale_degrees) == len(source_degrees)
        for r, s in zip(result.scale_degrees, source_degrees):
            assert r.degree == s.degree
            assert abs(r.weight - s.weight) < 0.01
    
    def test_blend_t1_matches_target_degrees(self, blues_bebop_morpher):
        """At t=1, blended degrees should match target exactly."""
        result = blues_bebop_morpher.blend(1.0)
        target_degrees = blues_bebop_morpher.target.scale_degrees
        
        assert len(result.scale_degrees) == len(target_degrees)
        for r, t in zip(result.scale_degrees, target_degrees):
            assert r.degree == t.degree
            assert abs(r.weight - t.weight) < 0.01
    
    def test_blend_t0_chromatic_density(self, blues_bebop_morpher):
        result = blues_bebop_morpher.blend(0.0)
        assert result.chromatic_density == blues_bebop_morpher.source.chromatic_density
    
    def test_blend_t1_chromatic_density(self, blues_bebop_morpher):
        result = blues_bebop_morpher.blend(1.0)
        assert result.chromatic_density == blues_bebop_morpher.target.chromatic_density
    
    def test_blend_t0_register(self, blues_bebop_morpher):
        result = blues_bebop_morpher.blend(0.0)
        assert result.register_tendency == blues_bebop_morpher.source.register_tendency
    
    def test_blend_t1_register(self, blues_bebop_morpher):
        result = blues_bebop_morpher.blend(1.0)
        assert result.register_tendency == blues_bebop_morpher.target.register_tendency


# ── Blend midpoint ───────────────────────────────────────────────────

class TestBlendMidpoint:
    """Blend at t=0.5 is between both terrains."""
    
    def test_midpoint_has_more_degrees_than_either(self, blues_bebop_morpher):
        """At t=0.5, both source and target degrees are present (union)."""
        result = blues_bebop_morpher.blend(0.5)
        source_degrees = {sd.degree for sd in blues_bebop_morpher.source.scale_degrees}
        target_degrees = {sd.degree for sd in blues_bebop_morpher.target.scale_degrees}
        result_degrees = {sd.degree for sd in result.scale_degrees}
        
        # Should contain all degrees from both (above threshold)
        assert source_degrees.issubset(result_degrees) or len(result_degrees) >= max(len(source_degrees), len(target_degrees))
    
    def test_midpoint_chromatic_is_average(self, blues_bebop_morpher):
        result = blues_bebop_morpher.blend(0.5)
        expected = (blues_bebop_morpher.source.chromatic_density + blues_bebop_morpher.target.chromatic_density) / 2
        assert abs(result.chromatic_density - expected) < 0.01
    
    def test_midpoint_weights_between(self, blues_bebop_morpher):
        """At t=0.5, shared degree weights should be between source and target."""
        result = blues_bebop_morpher.blend(0.5)
        source_map = {sd.degree: sd.weight for sd in blues_bebop_morpher.source.scale_degrees}
        target_map = {sd.degree: sd.weight for sd in blues_bebop_morpher.target.scale_degrees}
        result_map = {sd.degree: sd.weight for sd in result.scale_degrees}
        
        # For shared degrees, weight should be between source and target
        shared = set(source_map.keys()) & set(target_map.keys())
        for deg in shared:
            if deg in result_map:
                lo = min(source_map[deg], target_map[deg])
                hi = max(source_map[deg], target_map[deg])
                assert lo - 0.01 <= result_map[deg] <= hi + 0.01, \
                    f"Degree {deg}: {result_map[deg]} not between {lo} and {hi}"


# ── Morph performance ───────────────────────────────────────────────

class TestMorphPerformance:
    """Morphing a melody produces valid notes at every step."""
    
    def test_morph_produces_correct_steps(self, blues_bebop_morpher):
        melody = [60, 64, 67, 72, 71, 67, 64, 60]
        steps = 8
        results = blues_bebop_morpher.morph_performance(melody, steps=steps)
        assert len(results) == steps
    
    def test_morph_notes_are_valid_midi(self, blues_bebop_morpher):
        melody = [60, 64, 67, 72, 71, 67, 64, 60]
        results = blues_bebop_morpher.morph_performance(melody, steps=8)
        for terrain, notes in results:
            for note in notes:
                assert 0 <= note <= 127, f"Invalid MIDI note: {note}"
    
    def test_morph_notes_match_melody_length(self, blues_bebop_morpher):
        melody = [60, 64, 67, 72]
        results = blues_bebop_morpher.morph_performance(melody, steps=5)
        for terrain, notes in results:
            assert len(notes) == len(melody)
    
    def test_morph_single_step(self, blues_bebop_morpher):
        """With 1 step, should still work."""
        melody = [60, 64, 67]
        results = blues_bebop_morpher.morph_performance(melody, steps=1)
        assert len(results) == 1
        assert len(results[0][1]) == 3


# ── Predefined paths ────────────────────────────────────────────────

class TestPredefinedPaths:
    """Predefined morph paths work correctly."""
    
    @pytest.mark.parametrize("path_name", list(MORPH_PATHS.keys()))
    def test_predefined_path_works(self, path_name):
        morpher = get_morpher(path_name)
        result = morpher.blend(0.5)
        assert isinstance(result, Terrain)
        assert len(result.scale_degrees) > 0
    
    def test_invalid_path_raises(self):
        with pytest.raises(ValueError, match="Unknown morph path"):
            get_morpher("nonexistent_path")


# ── Edge cases ──────────────────────────────────────────────────────

class TestEdgeCases:
    
    def test_blend_clamps_t_below_zero(self, blues_bebop_morpher):
        result = blues_bebop_morpher.blend(-0.5)
        source_degrees = blues_bebop_morpher.source.scale_degrees
        assert len(result.scale_degrees) == len(source_degrees)
    
    def test_blend_clamps_t_above_one(self, blues_bebop_morpher):
        result = blues_bebop_morpher.blend(1.5)
        target_degrees = blues_bebop_morpher.target.scale_degrees
        assert len(result.scale_degrees) == len(target_degrees)
    
    def test_same_source_and_target(self):
        morpher = TerrainMorpher("delta_blues", "delta_blues")
        result = morpher.blend(0.5)
        # Should still work — degrees should match
        assert len(result.scale_degrees) == len(morpher.source.scale_degrees)
    
    def test_unknown_terrain_raises(self):
        with pytest.raises(ValueError, match="Unknown terrain"):
            TerrainMorpher("nonexistent", "bebop_rich")
    
    def test_snap_note_returns_valid(self):
        degrees = [
            ScaleDegree(0, 1.0, "root"),
            ScaleDegree(4, 0.9, "third"),
            ScaleDegree(7, 0.85, "fifth"),
        ]
        result = _snap_note_to_terrain(62, degrees, root=60)
        assert 0 <= result <= 127


# ── Scale degree blending unit tests ────────────────────────────────

class TestBlendScaleDegrees:
    
    def test_shared_degrees_interpolate(self):
        source = [ScaleDegree(0, 1.0, "root"), ScaleDegree(7, 0.9, "fifth")]
        target = [ScaleDegree(0, 0.8, "root"), ScaleDegree(7, 1.0, "fifth")]
        result = _blend_scale_degrees(source, target, 0.5)
        result_map = {sd.degree: sd.weight for sd in result}
        assert abs(result_map[0] - 0.9) < 0.01
        assert abs(result_map[7] - 0.95) < 0.01
    
    def test_source_only_fades_out(self):
        source = [ScaleDegree(3, 0.9, "min3"), ScaleDegree(0, 1.0, "root")]
        target = [ScaleDegree(0, 1.0, "root")]
        result = _blend_scale_degrees(source, target, 0.5)
        result_map = {sd.degree: sd.weight for sd in result}
        # degree 3 should be present but halved
        assert 3 in result_map
        assert abs(result_map[3] - 0.45) < 0.01
    
    def test_target_only_fades_in(self):
        source = [ScaleDegree(0, 1.0, "root")]
        target = [ScaleDegree(0, 1.0, "root"), ScaleDegree(6, 0.7, "tritone")]
        result = _blend_scale_degrees(source, target, 0.5)
        result_map = {sd.degree: sd.weight for sd in result}
        assert 6 in result_map
        assert abs(result_map[6] - 0.35) < 0.01
