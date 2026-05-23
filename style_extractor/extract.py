import mido
from collections import Counter
import math
from .tile import StyleTile


class StyleExtractor:
    def extract(self, midi_paths: list, composer: str, era: str) -> StyleTile:
        all_intervals = []
        all_durations = []  # in beats
        all_pitches = []
        all_onsets = []  # in beats

        for path in midi_paths:
            mid = mido.MidiFile(path)
            intervals, durations, pitches, onsets = self._parse_midi(mid)
            all_intervals.extend(intervals)
            all_durations.extend(durations)
            all_pitches.extend(pitches)
            all_onsets.extend(onsets)

        if not all_pitches:
            raise ValueError("No notes found in MIDI files")

        # Melodic DNA
        interval_dist = self._distribution(all_intervals)
        mean_int = sum(abs(i) for i in all_intervals) / len(all_intervals) if all_intervals else 0
        steps = sum(1 for i in all_intervals if abs(i) <= 2)
        leaps = len(all_intervals) - steps
        step_leap = steps / len(all_intervals) if all_intervals else 0

        # Rhythmic DNA
        dur_dist = self._duration_names(all_durations)
        sync = self._syncopation_rate(all_onsets)
        max_onset = max(all_onsets) if all_onsets else 1
        density = len(all_pitches) / max_onset if max_onset > 0 else 1
        entropy = self._entropy(dur_dist.values())

        # Harmonic
        CONSONANT = {0, 3, 4, 7, 8, 9, 12}
        consonant = sum(1 for i in all_intervals if abs(i) % 12 in CONSONANT)
        cons_rate = consonant / len(all_intervals) if all_intervals else 0

        # Register
        center = sum(all_pitches) / len(all_pitches)
        lo, hi = min(all_pitches), max(all_pitches)

        # Swing detection (crude: check if off-beat 8ths are consistently late)
        swing = self._detect_swing(all_onsets)

        return StyleTile(
            composer=composer, era=era,
            interval_distribution={str(k): v for k, v in interval_dist.items()},
            melodic_range_semitones=hi - lo,
            mean_interval=round(mean_int, 2),
            step_vs_leap_ratio=round(step_leap, 3),
            duration_distribution=dur_dist,
            syncopation_rate=round(sync, 3),
            mean_note_density=round(density, 2),
            rhythmic_entropy=round(entropy, 3),
            consonance_rate=round(cons_rate, 3),
            dissonance_rate=round(1 - cons_rate, 3),
            timing_precision_ms=5.0,
            swing_factor=round(swing, 3),
            pitch_center=round(center, 1),
            pitch_range=(lo, hi),
            notes_per_bar=round(density * 4, 1),
        )

    def _parse_midi(self, mid):
        """Extract features from a MIDI file."""
        pitches, onsets, durations = [], [], []
        for track in mid.tracks:
            abs_time = 0
            note_ons = {}
            for msg in track:
                abs_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_ons[msg.note] = abs_time
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in note_ons:
                        start = note_ons.pop(msg.note)
                        dur = abs_time - start
                        ticks_per_beat = mid.ticks_per_beat
                        pitches.append(msg.note)
                        onsets.append(start / ticks_per_beat)
                        durations.append(dur / ticks_per_beat)

        # Compute melodic intervals (sort by onset)
        paired = sorted(zip(onsets, pitches))
        intervals = [paired[i+1][1] - paired[i][1] for i in range(len(paired)-1)]

        return intervals, durations, pitches, onsets

    def _distribution(self, values):
        c = Counter(values)
        total = sum(c.values())
        return {k: round(v/total, 4) for k, v in c.items()}

    def _duration_names(self, durations):
        names = []
        for d in durations:
            if d >= 3.5: names.append("whole")
            elif d >= 1.5: names.append("half")
            elif d >= 0.75: names.append("quarter")
            elif d >= 0.35: names.append("eighth")
            else: names.append("sixteenth")
        c = Counter(names)
        total = len(names)
        return {k: round(v/total, 4) for k, v in c.items()}

    def _syncopation_rate(self, onsets):
        if not onsets: return 0
        on_beat = sum(1 for o in onsets if abs(o - round(o)) < 0.05)
        return 1.0 - on_beat / len(onsets)

    def _entropy(self, probs):
        probs = [p for p in probs if p > 0]
        return -sum(p * math.log2(p) for p in probs) if probs else 0

    def _detect_swing(self, onsets):
        """Crude swing detection: check if notes on off-beat 8ths are shifted."""
        if not onsets:
            return 0.0
        # Look for onset positions near half-beat boundaries
        offsets = []
        for o in onsets:
            frac = o - math.floor(o * 2) / 2  # offset from nearest half-beat
            # For notes near the "and" of a beat (0.5), check if they're shifted
            nearest_half = round(o * 2) / 2
            diff = o - nearest_half
            if abs(nearest_half - round(nearest_half) - 0.5) < 0.01:  # it's an off-beat
                offsets.append(diff)
        if not offsets:
            return 0.0
        # Average offset of off-beat notes (positive = late = swing)
        avg_offset = sum(offsets) / len(offsets)
        # Normalize: a swing ratio of 2:1 would be ~0.083 beats late
        return max(0.0, min(1.0, avg_offset / 0.083))
