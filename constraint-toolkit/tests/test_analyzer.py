"""Tests for audio/MIDI analysis."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from constraint_toolkit.analyzer import analyze_wav, analyze_midi, batch_analyze
from constraint_toolkit.dials import DialPosition


def _make_sine_wav(path: Path, freq=440.0, duration=2.0, sr=22050):
    """Create a simple sine WAV file for testing."""
    import wave

    t = np.linspace(0, duration, int(sr * duration), dtype=np.float64)
    audio = (np.sin(2 * np.pi * freq * t) * 0.5 * 32767).astype(np.int16)

    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio.tobytes())


def _make_midi_file(path: Path, bpm=120, notes=None):
    """Create a simple MIDI file for testing."""
    import mido

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


class TestAnalyzeWav:
    """Tests for analyze_wav."""

    def test_returns_analysis_result(self, tmp_path):
        wav_path = tmp_path / "test.wav"
        _make_sine_wav(wav_path)
        result = analyze_wav(wav_path)
        assert hasattr(result, "dial_position")
        assert isinstance(result.dial_position, DialPosition)

    def test_values_in_range(self, tmp_path):
        wav_path = tmp_path / "test.wav"
        _make_sine_wav(wav_path)
        result = analyze_wav(wav_path)
        dp = result.dial_position
        assert 0 <= dp.harmonic_tension <= 5
        assert 0 <= dp.rhythmic_complexity <= 5
        assert 0 <= dp.spectral_density <= 5

    def test_sine_wave_low_complexity(self, tmp_path):
        # Pure sine should have low spectral density
        wav_path = tmp_path / "test.wav"
        _make_sine_wav(wav_path, freq=440, duration=2.0)
        result = analyze_wav(wav_path)
        # Pure sine is harmonically simple
        assert result.dial_position.harmonic_tension < 3.0

    def test_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            analyze_wav("/nonexistent/file.wav")

    def test_consistency(self, tmp_path):
        wav_path = tmp_path / "test.wav"
        _make_sine_wav(wav_path)
        r1 = analyze_wav(wav_path)
        r2 = analyze_wav(wav_path)
        assert r1.dial_position.harmonic_tension == r2.dial_position.harmonic_tension
        assert r1.dial_position.rhythmic_complexity == r2.dial_position.rhythmic_complexity
        assert r1.dial_position.spectral_density == r2.dial_position.spectral_density


class TestAnalyzeMidi:
    """Tests for analyze_midi."""

    def test_returns_analysis_result(self, tmp_path):
        midi_path = tmp_path / "test.mid"
        _make_midi_file(midi_path)
        result = analyze_midi(midi_path)
        assert hasattr(result, "dial_position")
        assert isinstance(result.dial_position, DialPosition)

    def test_values_in_range(self, tmp_path):
        midi_path = tmp_path / "test.mid"
        _make_midi_file(midi_path)
        result = analyze_midi(midi_path)
        dp = result.dial_position
        assert 0 <= dp.harmonic_tension <= 5
        assert 0 <= dp.rhythmic_complexity <= 5
        assert 0 <= dp.spectral_density <= 5

    def test_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            analyze_midi("/nonexistent/file.mid")


class TestBatchAnalyze:
    """Tests for batch_analyze."""

    def test_batch_multiple_files(self, tmp_path):
        for i in range(3):
            _make_sine_wav(tmp_path / f"test_{i}.wav", freq=440 + i * 100)

        results = batch_analyze(tmp_path, pattern="*.wav")
        assert len(results) == 3
        for name, result in results.items():
            assert hasattr(result, "dial_position")

    def test_batch_empty_dir(self, tmp_path):
        results = batch_analyze(tmp_path, pattern="*.wav")
        assert len(results) == 0

    def test_batch_handles_errors(self, tmp_path):
        # One valid, one invalid
        _make_sine_wav(tmp_path / "good.wav")
        bad = tmp_path / "bad.wav"
        bad.write_bytes(b"not a wav file")

        results = batch_analyze(tmp_path, pattern="*.wav")
        # Should return results for both (bad gets error result)
        # Keys may be full paths or just filenames
        found_good = any("good.wav" in k for k in results)
        assert found_good
