"""ConstraintOscilloscope — visualize the same constraint structure at 4 scales.

1. Sample level  — rendered audio waveform (lattice snap geometry)
2. Note level    — piano roll (pitch lattice & timing grid)
3. Phrase level  — holonomy trajectory (key drift)
4. Piece level   — note density / structural arc
"""

import os
import sys
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


class ConstraintOscilloscope:
    """Multi-scale constraint visualizer."""

    def visualize_midi(
        self,
        midi_path: str,
        output_path: str = "constraint_scope.png",
        title: str | None = None,
    ):
        """Full 4-panel visualization of a MIDI file."""
        import mido

        mid = mido.MidiFile(midi_path)

        fig = plt.figure(figsize=(20, 16))
        base = os.path.basename(midi_path)
        fig.suptitle(
            title or f"Constraint Oscilloscope — {base}",
            fontsize=16,
            fontweight="bold",
        )
        gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.30)

        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_waveform(ax1, mid)

        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_piano_roll(ax2, mid)

        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_holonomy(ax3, mid)

        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_density(ax4, mid)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return output_path

    # ------------------------------------------------------------------
    # Panel helpers
    # ------------------------------------------------------------------

    def _plot_waveform(self, ax, mid):
        """Panel 1: Rendered audio waveform showing lattice snap geometry."""
        # Lazy import so the module works even without constraint-synth installed
        try:
            cs_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "constraint-synth"
            )
            cs_path = os.path.abspath(cs_path)
            if cs_path not in sys.path:
                sys.path.insert(0, cs_path)
            from constraint_synth.synth import ConstraintSynth
            from constraint_synth.oscillator import LatticeOscillator

            synth = ConstraintSynth(oscillator=LatticeOscillator(lattice_shape="triangle"))
            notes = self._extract_notes(mid)[:4]
            if notes:
                segments = []
                for pitch, velocity, duration, _start in notes:
                    dur = max(duration, 0.01)
                    segments.append(synth.play_note(pitch, velocity, dur))
                signal = np.concatenate(segments)
                samples = min(4000, len(signal))
                t = np.arange(samples) / 44100 * 1000  # ms
                ax.plot(t, signal[:samples], linewidth=0.5, color="#2196F3")
                ax.set_title("Sample Level — Lattice Snap Geometry", fontsize=12)
                ax.set_xlabel("Time (ms)")
                ax.set_ylabel("Amplitude")
                ax.axhline(y=0, color="gray", linewidth=0.3)
                ax.set_ylim(-1.2, 1.2)
                return
        except Exception as exc:
            pass  # fall through to fallback

        # Fallback: synthetic waveform from note data
        notes = self._extract_notes(mid)[:8]
        if not notes:
            ax.text(0.5, 0.5, "No notes found", ha="center", va="center",
                    transform=ax.transAxes)
            ax.set_title("Sample Level — Lattice Snap Geometry", fontsize=12)
            return

        sr = 44100
        max_dur = sum(max(n[2], 0.01) for n in notes)
        total_samples = int(sr * max_dur)
        signal = np.zeros(total_samples)
        pos = 0
        for pitch, vel, dur, _ in notes:
            dur = max(dur, 0.01)
            freq = 440.0 * (2 ** ((pitch - 69) / 12.0))
            n = int(sr * dur)
            t = np.arange(n) / sr
            tone = np.sin(2 * np.pi * freq * t) * (vel / 127.0)
            end = min(pos + n, total_samples)
            signal[pos:end] += tone[: end - pos]
            pos = end

        samples = min(4000, len(signal))
        t_ms = np.arange(samples) / sr * 1000
        ax.plot(t_ms, signal[:samples], linewidth=0.5, color="#2196F3")
        ax.set_title("Sample Level — Waveform (synthetic fallback)", fontsize=12)
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Amplitude")
        ax.axhline(y=0, color="gray", linewidth=0.3)

    def _plot_piano_roll(self, ax, mid):
        """Panel 2: Piano roll showing note-level constraint (pitch quantization)."""
        notes = self._extract_notes(mid)
        if not notes:
            ax.text(0.5, 0.5, "No notes found", ha="center", va="center",
                    transform=ax.transAxes)
            ax.set_title("Note Level — Pitch Lattice & Timing Grid", fontsize=12)
            return

        for pitch, velocity, duration, start in notes:
            color = plt.cm.viridis(velocity / 127)
            ax.barh(
                pitch,
                duration * 1000,
                left=start * 1000,
                height=0.8,
                color=color,
                edgecolor="none",
                alpha=0.8,
            )

        ax.set_title("Note Level — Pitch Lattice & Timing Grid", fontsize=12)
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("MIDI Pitch")

        pitches = [n[0] for n in notes]
        ax.set_ylim(min(pitches) - 2, max(pitches) + 2)

        # C-major scale degree grid lines
        for note in range(min(pitches) - 2, max(pitches) + 3):
            pc = note % 12
            if pc in (0, 2, 4, 5, 7, 9, 11):
                ax.axhline(y=note, color="red", linewidth=0.3, alpha=0.4)

    def _plot_holonomy(self, ax, mid):
        """Panel 3: Holonomy trajectory showing phrase-level key drift."""
        notes = self._extract_notes(mid)
        if not notes:
            ax.text(0.5, 0.5, "No notes found", ha="center", va="center",
                    transform=ax.transAxes)
            ax.set_title("Phrase Level — Holonomy (Key Drift)", fontsize=12)
            return

        # Pitch-class distance from C (0) — cumulative drift
        key_center_pc = 0  # C
        drifts = [(n[0] % 12 - key_center_pc) for n in notes]
        cumulative = np.cumsum(drifts).astype(float)
        # Detrend so we see winding, not linear growth
        x = np.arange(len(cumulative))
        if len(x) > 1:
            slope = cumulative[-1] / (len(cumulative) - 1)
            cumulative -= x * slope

        times_ms = [n[3] * 1000 for n in notes]

        ax.plot(times_ms, cumulative, linewidth=1.5, color="#FF5722")
        ax.fill_between(times_ms, 0, cumulative, alpha=0.2, color="#FF5722")
        ax.axhline(y=0, color="gray", linewidth=0.5)
        ax.set_title("Phrase Level — Holonomy (Key Drift)", fontsize=12)
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Cumulative Drift (semitones)")

    def _plot_density(self, ax, mid):
        """Panel 4: Note density over time showing structural arc."""
        notes = self._extract_notes(mid)
        if not notes:
            ax.text(0.5, 0.5, "No notes found", ha="center", va="center",
                    transform=ax.transAxes)
            ax.set_title("Piece Level — Constraint Density (Structural Arc)", fontsize=12)
            return

        max_time = max(n[3] + n[2] for n in notes)
        n_bins = max(20, int(max_time / 0.2))  # ~200ms windows minimum
        n_bins = min(n_bins, 100)
        window = max_time / n_bins
        bins = np.linspace(0, max_time, n_bins + 1)

        note_counts = np.zeros(n_bins)
        velocities = np.zeros(n_bins)
        for pitch, vel, dur, start in notes:
            idx = min(int(start / window), n_bins - 1)
            note_counts[idx] += 1
            velocities[idx] += vel

        centers = (bins[:-1] + bins[1:]) / 2 * 1000  # ms
        ax.bar(centers, note_counts, width=window * 1000 * 0.8,
               color="#4CAF50", alpha=0.7, label="note count")

        # Overlay average velocity as line
        with np.errstate(invalid="ignore", divide="ignore"):
            avg_vel = np.where(note_counts > 0, velocities / note_counts, 0)
        ax2 = ax.twinx()
        ax2.plot(centers, avg_vel, color="#FF9800", linewidth=1.5, alpha=0.8,
                 label="avg velocity")
        ax2.set_ylabel("Avg Velocity", color="#FF9800")
        ax2.tick_params(axis="y", labelcolor="#FF9800")

        ax.set_title("Piece Level — Constraint Density (Structural Arc)", fontsize=12)
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Notes per window")

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_notes(mid):
        """Extract (pitch, velocity, duration_sec, start_sec) from a MIDI file."""
        ticks_per_beat = mid.ticks_per_beat
        tempo = 500000  # default 120 BPM
        for track in mid.tracks:
            for msg in track:
                if msg.type == "set_tempo":
                    tempo = msg.tempo
                    break

        sec_per_tick = tempo / (ticks_per_beat * 1_000_000)
        notes = []

        for track in mid.tracks:
            abs_tick = 0
            note_ons = {}
            for msg in track:
                abs_tick += msg.time
                if msg.type == "note_on" and msg.velocity > 0:
                    note_ons[msg.note] = (abs_tick, msg.velocity)
                elif msg.type == "note_off" or (
                    msg.type == "note_on" and msg.velocity == 0
                ):
                    if msg.note in note_ons:
                        start_tick, vel = note_ons.pop(msg.note)
                        start_sec = start_tick * sec_per_tick
                        dur_sec = (abs_tick - start_tick) * sec_per_tick
                        notes.append((msg.note, vel, dur_sec, start_sec))

        return sorted(notes, key=lambda n: n[3])
