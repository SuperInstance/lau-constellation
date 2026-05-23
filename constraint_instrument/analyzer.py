"""
ConstraintAnalyzer — Analyze ANY external music through the constraint lens.

The diagnostic is the killer feature, but it was trapped inside.
Now users can feed their OWN music in.

Usage:
    from constraint_instrument.analyzer import ConstraintAnalyzer

    analyzer = ConstraintAnalyzer()

    # From a MIDI file
    report = analyzer.from_midi("song.mid")

    # From raw notes
    report = analyzer.from_notes(notes)

    # From an audio file
    report = analyzer.from_audio("recording.wav")

    # Detect which terrain matches best
    terrain = analyzer.detect_terrain(report)

    # Compare two performances
    diff = analyzer.compare(solo1_notes, solo2_notes)
"""

import math
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from .goodman import GoodmanEngine, DiagnosticReport, _normalize_notes
from .terrain import Terrain, TERRAINS


# ── Key Detection ────────────────────────────────────────────────────────────

# Krumhansl-Schmuckler key profiles (correlation-based key detection)
MAJOR_PROFILE = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
MINOR_PROFILE = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]


def _correlate(a: List[float], b: List[float]) -> float:
    """Pearson correlation between two vectors."""
    n = len(a)
    if n == 0:
        return 0.0
    mean_a = sum(a) / n
    mean_b = sum(b) / n
    num = sum((a[i] - mean_a) * (b[i] - mean_b) for i in range(n))
    den_a = math.sqrt(sum((a[i] - mean_a) ** 2 for i in range(n)))
    den_b = math.sqrt(sum((b[i] - mean_b) ** 2 for i in range(n)))
    if den_a == 0 or den_b == 0:
        return 0.0
    return num / (den_a * den_b)


def detect_key(notes: list) -> Tuple[int, str, float]:
    """
    Detect the most likely key using Krumhansl-Schmuckler algorithm.

    Returns:
        (key_midi: int, mode: str, confidence: float)
        mode is 'major' or 'minor'
        confidence is 0.0-1.0
    """
    notes = _normalize_notes(notes)
    if not notes:
        return 60, "major", 0.0

    # Build pitch-class distribution
    pc_counts = Counter(n["pitch"] % 12 for n in notes)
    total = sum(pc_counts.values())
    if total == 0:
        return 60, "major", 0.0

    distribution = [pc_counts.get(i, 0) / total for i in range(12)]

    best_key = 0
    best_mode = "major"
    best_corr = -999.0

    for root in range(12):
        # Rotate distribution so root is at index 0
        rotated = distribution[root:] + distribution[:root]

        major_corr = _correlate(rotated, MAJOR_PROFILE)
        minor_corr = _correlate(rotated, MINOR_PROFILE)

        if major_corr > best_corr:
            best_corr = major_corr
            best_key = root
            best_mode = "major"
        if minor_corr > best_corr:
            best_corr = minor_corr
            best_key = root
            best_mode = "minor"

    # Normalize correlation to 0-1 confidence
    confidence = max(0.0, min(1.0, (best_corr + 1) / 2))
    # MIDI note: use octave 4 (60 + root)
    key_midi = 60 + best_key
    return key_midi, best_mode, confidence


# ── Terrain Matching ─────────────────────────────────────────────────────────

def _terrain_scale_profile(terrain: Terrain) -> List[float]:
    """Build a 12-element pitch-class weight profile from a terrain's scale degrees."""
    profile = [0.0] * 12
    for sd in terrain.scale_degrees:
        profile[sd.degree % 12] = sd.weight
    return profile


def _terrain_chromatic_density(terrain: Terrain) -> float:
    return terrain.chromatic_density


def match_terrain(notes: list) -> Tuple[str, float, dict]:
    """
    Find the terrain that best matches a set of notes.

    Compares pitch-class distribution against all 17 terrains.

    Returns:
        (terrain_name: str, confidence: float, scores: dict)
        scores maps terrain_name -> correlation score
    """
    notes = _normalize_notes(notes)
    if not notes:
        return "blues", 0.0, {}

    # Build pitch-class distribution
    pc_counts = Counter(n["pitch"] % 12 for n in notes)
    total = sum(pc_counts.values())
    if total == 0:
        return "blues", 0.0, {}

    distribution = [pc_counts.get(i, 0) / total for i in range(12)]

    scores = {}
    for name, terrain in TERRAINS.items():
        profile = _terrain_scale_profile(terrain)
        # Normalize the profile
        pmax = max(profile) if profile else 1
        if pmax > 0:
            profile = [p / pmax for p in profile]
        corr = _correlate(distribution, profile)
        # Boost for chromatic density match
        pc_unique = len(set(n["pitch"] % 12 for n in notes))
        chromaticness = pc_unique / 12.0
        density_diff = abs(chromaticness - terrain.chromatic_density)
        density_bonus = (1.0 - density_diff) * 0.15
        scores[name] = corr + density_bonus

    if not scores:
        return "blues", 0.0, {}

    best = max(scores, key=scores.get)
    best_score = scores[best]

    # Confidence: how much better is the best vs the median
    sorted_scores = sorted(scores.values(), reverse=True)
    if len(sorted_scores) >= 2:
        gap = best_score - sorted_scores[1]
        confidence = min(1.0, max(0.0, 0.5 + gap * 2))
    else:
        confidence = 0.5

    return best, confidence, scores


# ── Audio Processing ─────────────────────────────────────────────────────────

def _extract_pitches_from_audio(path: str) -> list:
    """
    Extract pitch estimates from an audio file.

    Tries: basic-pitch -> aubio -> scipy spectral peaks

    Returns list of note dicts.
    """
    # Try basic-pitch first (best quality)
    try:
        import basic_pitch
        from basic_pitch.inference import predict
        from basic_pitch.note_creation import model_output_to_notes
        import numpy as np

        model_output, midi_data, _ = predict(path)
        # midi_data is a pretty_midi.PrettyMidi object
        notes = []
        for instrument in midi_data.instruments:
            for note in instrument.notes:
                notes.append({
                    "pitch": int(note.pitch),
                    "velocity": int(note.velocity * 127),
                    "start": round(note.start, 4),
                    "duration": round(note.end - note.start, 4),
                })
        if notes:
            return sorted(notes, key=lambda n: n["start"])
    except ImportError:
        pass
    except Exception:
        pass

    # Try aubio
    try:
        import aubio
        from aubio import source, pitch as aubio_pitch

        win_s = 4096
        hop_s = 512
        s = source(path, 0, hop_s)
        samplerate = s.samplerate
        pitch_o = aubio_pitch("yin", win_s, hop_s, samplerate)
        pitch_o.set_unit("midi")
        pitch_o.set_tolerance(0.8)

        notes = []
        t = 0.0
        hop_duration = hop_s / samplerate
        current_pitch = None
        current_start = 0.0

        while True:
            samples, read = s()
            freq = pitch_o(samples)[0]
            confidence = pitch_o.get_confidence()

            if confidence > 0.7 and freq > 0:
                midi_note = int(round(freq))
                if midi_note == current_pitch:
                    pass  # extend
                else:
                    if current_pitch is not None:
                        dur = t - current_start
                        if dur > 0.05:
                            notes.append({
                                "pitch": current_pitch,
                                "velocity": 80,
                                "start": round(current_start, 4),
                                "duration": round(dur, 4),
                            })
                    current_pitch = midi_note
                    current_start = t
            else:
                if current_pitch is not None:
                    dur = t - current_start
                    if dur > 0.05:
                        notes.append({
                            "pitch": current_pitch,
                            "velocity": 80,
                            "start": round(current_start, 4),
                            "duration": round(dur, 4),
                        })
                    current_pitch = None

            t += hop_duration
            if read < hop_s:
                break

        # Close last note
        if current_pitch is not None:
            dur = t - current_start
            if dur > 0.05:
                notes.append({
                    "pitch": current_pitch,
                    "velocity": 80,
                    "start": round(current_start, 4),
                    "duration": round(dur, 4),
                })

        if notes:
            return notes
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: scipy spectral peak estimation
    try:
        import numpy as np
        from scipy.io import wavfile
        from scipy.signal import find_peaks

        sr, data = wavfile.read(path)
        if len(data.shape) > 1:
            data = data[:, 0]  # mono
        data = data.astype(float)

        # Normalize
        peak_val = np.max(np.abs(data))
        if peak_val > 0:
            data = data / peak_val

        hop = 512
        frame_size = 4096
        notes = []
        t = 0.0

        for start in range(0, len(data) - frame_size, hop):
            frame = data[start:start + frame_size]
            # Apply Hann window
            window = np.hanning(len(frame))
            frame = frame * window

            # FFT
            spectrum = np.abs(np.fft.rfft(frame))
            freqs = np.fft.rfftfreq(frame_size, 1.0 / sr)

            # Find spectral peaks (frequencies)
            min_freq = 80  # Hz
            max_freq = 2000  # Hz
            min_idx = int(min_freq * frame_size / sr)
            max_idx = int(max_freq * frame_size / sr) + 1

            if max_idx > len(spectrum):
                max_idx = len(spectrum)

            segment = spectrum[min_idx:max_idx]
            if len(segment) == 0:
                continue

            peaks, properties = find_peaks(segment, height=np.max(segment) * 0.2, distance=10)
            if len(peaks) > 0:
                best_peak = peaks[np.argmax(segment[peaks])]
                freq = freqs[min_idx + best_peak]
                if freq > 0:
                    midi_note = int(round(69 + 12 * math.log2(freq / 440.0)))
                    midi_note = max(0, min(127, midi_note))
                    # Check if extending previous note
                    if notes and abs(midi_note - notes[-1]["pitch"]) <= 1:
                        notes[-1]["duration"] = round(t - notes[-1]["start"], 4)
                    else:
                        if notes:
                            notes[-1]["duration"] = max(0.05, notes[-1]["duration"])
                        notes.append({
                            "pitch": midi_note,
                            "velocity": 80,
                            "start": round(t, 4),
                            "duration": 0.05,
                        })

            t += hop / sr

        # Fix last note duration
        if notes:
            notes[-1]["duration"] = max(0.05, notes[-1]["duration"])

        return notes
    except ImportError:
        raise ImportError(
            "Audio analysis requires one of: basic-pitch, aubio, or scipy.\n"
            "Install with: pip install basic-pitch  (recommended)\n"
            "          or: pip install aubio\n"
            "          or: pip install scipy numpy"
        )
    except Exception as e:
        raise ValueError(f"Could not analyze audio file: {e}")


# ── Comparison Engine ─────────────────────────────────────────────────────────

def compare_reports(report_a: DiagnosticReport, report_b: DiagnosticReport,
                    label_a: str = "A", label_b: str = "B") -> dict:
    """
    Compare two diagnostic reports.

    Returns dict with:
        orders: dict of order -> {score_a, score_b, winner, delta}
        overall: {score_a, score_b, winner}
        verdict: human-readable comparison
    """
    orders = {}
    for oa, ob in zip(report_a.orders, report_b.orders):
        delta = oa.score - ob.score
        if abs(delta) < 0.05:
            winner = "tie"
        elif delta > 0:
            winner = label_a
        else:
            winner = label_b
        orders[oa.name] = {
            "score_a": round(oa.score, 3),
            "score_b": round(ob.score, 3),
            "delta": round(delta, 3),
            "winner": winner,
            "stars_a": oa.stars,
            "stars_b": ob.stars,
        }

    overall_delta = report_a.overall_score - report_b.overall_score
    if abs(overall_delta) < 0.03:
        overall_winner = "tie"
    elif overall_delta > 0:
        overall_winner = label_a
    else:
        overall_winner = label_b

    # Determine what each is better at
    a_strengths = [name for name, o in orders.items() if o["winner"] == label_a]
    b_strengths = [name for name, o in orders.items() if o["winner"] == label_b]

    verdict_lines = [
        f"═" * 55,
        f"  COMPARISON: {label_a} vs {label_b}",
        f"═" * 55,
    ]

    for name, o in orders.items():
        bar_a = "█" * int(o["score_a"] * 20) + "░" * (20 - int(o["score_a"] * 20))
        bar_b = "█" * int(o["score_b"] * 20) + "░" * (20 - int(o["score_b"] * 20))
        verdict_lines.append(f"\n  {name}")
        verdict_lines.append(f"    {label_a}: [{bar_a}] {o['score_a']:.0%} {o['stars_a']}")
        verdict_lines.append(f"    {label_b}: [{bar_b}] {o['score_b']:.0%} {o['stars_b']}")

    verdict_lines.append(f"\n{'─' * 55}")
    verdict_lines.append(f"  Overall: {label_a}={report_a.overall_score:.0%}  {label_b}={report_b.overall_score:.0%}")
    verdict_lines.append(f"  Winner: {overall_winner}")
    if a_strengths:
        verdict_lines.append(f"  {label_a} excels at: {', '.join(a_strengths)}")
    if b_strengths:
        verdict_lines.append(f"  {label_b} excels at: {', '.join(b_strengths)}")
    verdict_lines.append(f"═" * 55)

    verdict = "\n".join(verdict_lines)

    return {
        "orders": orders,
        "overall": {
            "score_a": round(report_a.overall_score, 3),
            "score_b": round(report_b.overall_score, 3),
            "delta": round(overall_delta, 3),
            "winner": overall_winner,
        },
        "a_strengths": a_strengths,
        "b_strengths": b_strengths,
        "verdict": verdict,
    }


# ── Main Analyzer Class ──────────────────────────────────────────────────────

class ConstraintAnalyzer:
    """
    Analyze ANY external music through the constraint lens.

    The diagnostic is the killer feature but it was trapped inside.
    This unlocks it for real users with their own music.

    Usage:
        analyzer = ConstraintAnalyzer()
        report = analyzer.from_midi("song.mid")
        print(report.summary())

        terrain = analyzer.detect_terrain(report)
        print(f"Best terrain match: {terrain}")
    """

    def from_midi(self, path: str, key: int = None, terrain_name: str = None,
                  bpm: float = None) -> DiagnosticReport:
        """
        Load a MIDI file and run full 4-order diagnostic.

        Args:
            path: Path to the MIDI file.
            key: Override key detection (MIDI note number). Auto-detected if None.
            terrain_name: Override terrain matching. Auto-detected if None.
            bpm: Override BPM detection. Auto-detected from MIDI if None.

        Returns:
            DiagnosticReport with full 4-order analysis.
        """
        # Load MIDI notes
        engine = GoodmanEngine()
        notes = engine._load_midi(path)
        if not notes:
            return engine._trivial_report(f"No notes found in {path}")

        return self.from_notes(notes, key=key, terrain=terrain_name, bpm=bpm)

    def from_notes(self, notes, key: int = None, terrain=None,
                   bpm: float = None) -> DiagnosticReport:
        """
        Analyze raw notes. Auto-detect key and best terrain match.

        Args:
            notes: List of note dicts (with pitch, velocity, start/start_time, duration).
            key: Override key detection (MIDI note number). Auto-detected if None.
            terrain: Terrain name string or None for auto-detection.
            bpm: BPM hint for timing analysis. Estimated from notes if None.

        Returns:
            DiagnosticReport with full 4-order analysis.
        """
        normalized = _normalize_notes(notes)
        if not normalized:
            engine = GoodmanEngine()
            return engine._trivial_report("No notes provided.")

        # Auto-detect key if not specified
        if key is None:
            detected_key, mode, key_confidence = detect_key(normalized)
            key = detected_key
        else:
            key_confidence = 1.0
            mode = "unknown"

        # Auto-detect BPM if not specified
        if bpm is None:
            bpm = self._estimate_bpm(normalized)

        # Resolve terrain
        from .instrument import resolve_terrain as _resolve_terrain
        from .terrain import TERRAINS

        if terrain is not None:
            if isinstance(terrain, str):
                terrain_key = _resolve_terrain(terrain)
            else:
                terrain_key = terrain
            terrain_obj = TERRAINS[terrain_key]
        else:
            # Auto-detect best terrain
            terrain_key, terrain_confidence, _ = match_terrain(normalized)
            terrain_obj = TERRAINS[terrain_key]

        # Run the diagnostic
        engine = GoodmanEngine(key=key, bpm=bpm, terrain=terrain_obj)
        report = engine.diagnose(normalized)

        # Annotate report with detected key/terrain info
        # (We add a custom attribute for display purposes)
        report._detected_key = key
        report._detected_mode = mode
        report._key_confidence = key_confidence
        report._detected_terrain = terrain_key if terrain is None else (
            terrain if isinstance(terrain, str) else terrain_key
        )

        return report

    def from_audio(self, path: str, key: int = None, terrain_name: str = None,
                   bpm: float = None) -> DiagnosticReport:
        """
        Analyze audio file (convert to pitch estimates first).

        Uses basic-pitch if available, otherwise aubio, then scipy spectral peaks.

        Args:
            path: Path to audio file (wav, mp3, etc.).
            key: Override key detection.
            terrain_name: Override terrain matching.
            bpm: BPM hint.

        Returns:
            DiagnosticReport with full 4-order analysis.
        """
        notes = _extract_pitches_from_audio(path)
        if not notes:
            engine = GoodmanEngine()
            return engine._trivial_report(f"Could not extract pitches from {path}")

        return self.from_notes(notes, key=key, terrain=terrain_name, bpm=bpm)

    def detect_terrain(self, notes_or_report) -> dict:
        """
        Which terrain best matches these notes?

        Args:
            notes_or_report: A list of notes, a DiagnosticReport, or a file path string.

        Returns:
            dict with:
                terrain: best terrain name
                confidence: 0.0-1.0
                top_3: list of (name, score) for top 3 matches
        """
        if isinstance(notes_or_report, DiagnosticReport):
            if hasattr(notes_or_report, '_source_notes'):
                notes = notes_or_report._source_notes
            else:
                return {
                    "terrain": "unknown",
                    "confidence": 0.0,
                    "top_3": [],
                    "error": "Cannot detect terrain from a report — pass notes instead."
                }
        elif isinstance(notes_or_report, str):
            # File path — load notes
            engine = GoodmanEngine()
            notes = engine._load_midi(notes_or_report)
        else:
            notes = notes_or_report

        normalized = _normalize_notes(notes)
        best, confidence, scores = match_terrain(normalized)

        # Top 3
        sorted_terrains = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_3 = [(name, round(score, 3)) for name, score in sorted_terrains[:3]]

        return {
            "terrain": best,
            "confidence": round(confidence, 3),
            "top_3": top_3,
        }

    def compare(self, notes_a, notes_b, label_a: str = "A",
                label_b: str = "B") -> dict:
        """
        Compare two performances.

        Analyzes each, then compares across all 4 orders.

        Args:
            notes_a: First performance (notes, MIDI path, or DiagnosticReport).
            notes_b: Second performance (notes, MIDI path, or DiagnosticReport).
            label_a: Label for first (default "A").
            label_b: Label for second (default "B").

        Returns:
            Comparison dict with verdict, orders, strengths.
        """
        # Resolve to DiagnosticReports
        report_a = self._resolve_report(notes_a)
        report_b = self._resolve_report(notes_b)

        result = compare_reports(report_a, report_b, label_a, label_b)

        # Add terrain matches for each
        result["terrain_a"] = self.detect_terrain(notes_a) if not isinstance(notes_a, DiagnosticReport) else None
        result["terrain_b"] = self.detect_terrain(notes_b) if not isinstance(notes_b, DiagnosticReport) else None

        return result

    def _resolve_report(self, source) -> DiagnosticReport:
        """Resolve a source (notes list, MIDI path, or report) to a DiagnosticReport."""
        if isinstance(source, DiagnosticReport):
            return source
        if isinstance(source, str):
            # Assume MIDI file path
            return self.from_midi(source)
        if isinstance(source, list):
            return self.from_notes(source)
        raise TypeError(f"Cannot analyze source of type {type(source).__name__}")

    def _estimate_bpm(self, notes: list) -> float:
        """
        Estimate BPM from note onsets using autocorrelation of inter-onset intervals.
        """
        if not notes:
            return 120.0

        normalized = _normalize_notes(notes)
        starts = sorted(set(round(n["start"], 4) for n in normalized))

        if len(starts) < 4:
            return 120.0

        # Inter-onset intervals
        iois = [starts[i + 1] - starts[i] for i in range(len(starts) - 1)]

        # Filter out very long gaps (likely phrase breaks)
        median_ioi = sorted(iois)[len(iois) // 2]
        iois = [ioi for ioi in iois if ioi < median_ioi * 4]

        if not iois:
            return 120.0

        # The most common IOI likely corresponds to a beat or sub-beat
        # Quantize to grid and find the mode
        quantized = [round(ioi * 20) / 20 for ioi in iois]  # round to 0.05
        counter = Counter(quantized)
        most_common_ioi = counter.most_common(1)[0][0]

        # Convert to BPM
        # The IOI could be a beat, half-beat, or double-beat
        bpm_from_ioi = 60.0 / most_common_ioi if most_common_ioi > 0 else 120.0

        # Normalize to reasonable BPM range (40-240)
        while bpm_from_ioi > 240:
            bpm_from_ioi /= 2
        while bpm_from_ioi < 40:
            bpm_from_ioi *= 2

        return round(bpm_from_ioi, 1)


# ── CLI Helpers ───────────────────────────────────────────────────────────────

def print_analysis_report(report: DiagnosticReport, terrain_info: dict = None,
                          key_info: dict = None) -> str:
    """Format a full analysis report with detected key and terrain."""
    lines = []

    # Header
    lines.append("═" * 60)
    lines.append("  CONSTRAINT ANALYSIS — External Music")
    lines.append("═" * 60)

    # Detected key
    if key_info:
        lines.append(f"\n  Detected Key: {key_info.get('name', '?')} "
                     f"(confidence: {key_info.get('confidence', 0):.0%})")
    elif hasattr(report, '_detected_key'):
        key_note = report._detected_key % 12
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key_name = note_names[key_note]
        mode = getattr(report, '_detected_mode', 'unknown')
        conf = getattr(report, '_key_confidence', 0)
        lines.append(f"\n  Detected Key: {key_name} {mode} "
                     f"(confidence: {conf:.0%})")

    # Detected terrain
    if terrain_info:
        lines.append(f"  Best Terrain: {terrain_info['terrain']} "
                     f"(confidence: {terrain_info['confidence']:.0%})")
        if terrain_info.get('top_3'):
            lines.append(f"  Top matches:")
            for name, score in terrain_info['top_3']:
                lines.append(f"    {name:25s} {score:.3f}")
    elif hasattr(report, '_detected_terrain'):
        lines.append(f"  Best Terrain: {report._detected_terrain}")

    # Standard diagnostic
    lines.append("")
    for o in report.orders:
        lines.append(f"  {o.name} (Order {o.order})  {o.stars}  {o.score:.0%}")
        for k, v in o.components.items():
            bar = "█" * int(v * 10) + "░" * (10 - int(v * 10))
            lines.append(f"    {k:25s} [{bar}] {v:.0%}")
        lines.append(f"    → {o.diagnosis}")

    lines.append(f"\n{'─' * 60}")
    lines.append(f"  Weakest:  {report.weakest.name} ({report.weakest.score:.0%})")
    lines.append(f"  Strongest: {report.strongest.name} ({report.strongest.score:.0%})")
    lines.append(f"\n  RECOMMENDATION: {report.recommendation}")
    lines.append("═" * 60)

    return "\n".join(lines)
