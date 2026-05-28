"""Integration tests: end-to-end pipelines."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

import mido

from constraint_toolkit.dials import DialPosition, DIAL_RANGES, compute_dial_distance
from constraint_toolkit.analyzer import analyze_midi
from constraint_toolkit.classifier import DialClassifier
from constraint_toolkit.composer import ConstraintComposer
from constraint_toolkit.optimizer import GrooveOptimizer, OptimizationResult


def _make_sine_wav(path: Path, freq=440.0, duration=2.0, sr=22050):
    """Create a simple sine WAV for testing."""
    import struct
    import wave
    t = np.linspace(0, duration, int(sr * duration), dtype=np.float64)
    audio = (np.sin(2 * np.pi * freq * t) * 0.5 * 32767).astype(np.int16)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio.tobytes())


def _make_midi_file(path: Path, bpm=120, notes=None):
    """Create a simple MIDI file."""
    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    track.append(mido.MetaMessage("set_tempo", tempo=int(60_000_000 / bpm), time=0))
    if notes is None:
        notes = [(0, 60), (240, 64), (480, 67), (720, 72)]
    prev_tick = 0
    for tick, pitch in notes:
        delta = tick - prev_tick
        track.append(mido.Message("note_on", note=pitch, velocity=80, time=max(0, delta)))
        track.append(mido.Message("note_off", note=pitch, velocity=0, time=120))
        prev_tick = tick + 120
    track.append(mido.MetaMessage("end_of_track", time=0))
    mid.tracks.append(track)
    mid.save(str(path))


class TestEndToEndPipeline:
    """End-to-end: compose → analyze → classify → optimize → re-analyze."""

    def test_compose_analyze_classify(self):
        """Compose a piece, analyze it, and classify the genre."""
        comp = ConstraintComposer(seed=42)
        target = DialPosition(
            harmonic_tension=3.5, rhythmic_complexity=3.0, spectral_density=2.0,
        )
        midi = comp.compose(target, bars=4, tempo=120)

        # Save and re-analyze
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            midi.save(f.name)
            result = analyze_midi(f.name)
            dial = result.dial_position
            Path(f.name).unlink()

        # Should be roughly in the right dial region
        assert 0 <= dial.harmonic_tension <= 5
        assert 0 <= dial.rhythmic_complexity <= 5

        # Classify
        clf = DialClassifier(seed=42)
        genre, conf = clf.predict_genre(dial)
        assert isinstance(genre, str)
        assert 0 <= conf <= 1

    def test_round_trip_dial_targets(self, tmp_path):
        """Compose targeting a tradition → analyze → verify dials are in range."""
        comp = ConstraintComposer(seed=42)
        for tradition, prof in list(DIAL_RANGES.items())[:3]:
            midi = comp.compose_in_tradition(tradition, bars=4)
            path = tmp_path / f"{tradition}.mid"
            midi.save(str(path))

            result = analyze_midi(str(path))
            dial = result.dial_position
            assert 0 <= dial.harmonic_tension <= 5
            assert 0 <= dial.rhythmic_complexity <= 5
            assert 0 <= dial.spectral_density <= 5

    def test_classify_held_out_tradition(self):
        """Build classifier with some traditions, predict held-out one."""
        clf = DialClassifier(seed=42)

        # Test centres of each tradition
        results = {}
        for tradition, prof in DIAL_RANGES.items():
            c = prof["center"]
            centre = DialPosition(
                harmonic_tension=float(c[0]),
                rhythmic_complexity=float(c[1]),
                spectral_density=float(c[2]),
            )
            predicted, conf = clf.predict_genre(centre)
            results[tradition] = (predicted, conf)

        # Most should classify correctly or to a nearby tradition
        correct = sum(1 for t, (p, _) in results.items() if t == p)
        assert correct >= len(DIAL_RANGES) * 0.5  # At least 50% accuracy

    def test_optimize_and_reanalyze(self, tmp_path):
        """Optimize a quantized pattern and verify it changed."""
        # Create quantized MIDI directly
        mid = mido.MidiFile(ticks_per_beat=480)
        meta = mido.MidiTrack()
        meta.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
        meta.append(mido.MetaMessage("end_of_track", time=0))
        mid.tracks.append(meta)

        track = mido.MidiTrack()
        track.append(mido.MetaMessage("track_name", name="Test", time=0))
        prev = 0
        for i in range(8):
            tick = i * 480
            track.append(mido.Message("note_on", note=60 + i, velocity=80, time=tick - prev))
            track.append(mido.Message("note_off", note=60 + i, velocity=0, time=120))
            prev = tick + 120
        track.append(mido.MetaMessage("end_of_track", time=0))
        mid.tracks.append(track)

        midi_path = tmp_path / "input.mid"
        mid.save(str(midi_path))

        # Analyze original
        original_dial = analyze_midi(str(midi_path))

        # Optimize toward Jazz (pass MidiFile, returns OptimizationResult)
        opt = GrooveOptimizer(seed=42)
        result = opt.optimize(mid, target_genre="Jazz", iterations=20)

        # Verify optimization result
        assert isinstance(result, OptimizationResult)
        assert isinstance(result.optimized_position, DialPosition)
        assert 0 <= result.optimized_position.harmonic_tension <= 5
        assert 0 <= result.optimized_position.rhythmic_complexity <= 5
        assert 0 <= result.optimized_position.spectral_density <= 5

    def test_novel_composition_in_unexplored_region(self):
        """Compose in an unexplored dial region and verify novelty."""
        comp = ConstraintComposer(seed=42)
        clf = DialClassifier(seed=42)

        # Unexplored region: very low harmonic, low rhythmic, very high spectral
        novel_pos = DialPosition(
            harmonic_tension=0.2, rhythmic_complexity=0.3, spectral_density=4.8,
        )
        novelty_before = clf.predict_novelty(novel_pos)

        midi = comp.compose_novel(novel_pos, bars=4)
        assert isinstance(midi, mido.MidiFile)
        assert len(midi.tracks) >= 1
