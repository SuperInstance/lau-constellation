"""
Holonomy Viz — walk around the circle of fifths and show cumulative holonomy.

Shows:
- Musical notes arranged as a circle (circle of fifths)
- Step-by-step traversal
- Cumulative holonomy at each step
- Green = zero holonomy, red = non-zero
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyArrowPatch

from constraint_theory_core.holonomy import cycle_holonomy

# ---------------------------------------------------------------------------
# Circle of fifths data
# ---------------------------------------------------------------------------

NOTES = ["C", "G", "D", "A", "E", "B", "F♯", "D♭", "A♭", "E♭", "B♭", "F"]
# Each step around the circle of fifths is +7 semitones, which is 7×30° = 210° in our 48-dir space,
# but for visualisation we use 12 equal angular steps.
N_NOTES = len(NOTES)

# Construct a cycle: C → G → D → A → E → B → F♯ → D♭ → A♭ → E♭ → B♭ → F → C
CYCLE_EDGES = [(i, (i + 1) % N_NOTES) for i in range(N_NOTES)]

# Direction indices for each step (7 semitones = 4 steps of 48-dir = 4×7.5° = 30° ... not exact)
# In 48-dir space, 360°/48 = 7.5° per step.  7 semitones = 210° = 28 steps.
# So each edge in the circle of fifths gets direction 28.
STEP_DIRECTION = 28  # 210° / 7.5° = 28

# A consistent cycle would sum to 0 mod 48: 12 × 28 = 336 ≡ 336 mod 48 = 336 - 6×48 = 336 - 288 = 48 ≡ 0
# So the circle of fifths is actually consistent! Let's also show a broken version.
DIRECTIONS_CONSISTENT = [STEP_DIRECTION] * N_NOTES

# For contrast, create an inconsistent walk where one step is wrong
DIRECTIONS_BROKEN = [STEP_DIRECTION] * N_NOTES
DIRECTIONS_BROKEN[5] = STEP_DIRECTION + 3  # one bad step


def note_positions(radius: float = 2.0) -> np.ndarray:
    """Return (x, y) for each note on a circle."""
    angles = np.linspace(0, 2 * math.pi, N_NOTES, endpoint=False) + math.pi / 2
    return np.column_stack([radius * np.cos(angles), radius * np.sin(angles)])


def run():
    pos = note_positions(radius=2.0)

    # We will animate two scenarios side-by-side
    FRAMES = 80
    FPS = 12

    fig, (ax_good, ax_bad) = plt.subplots(1, 2, figsize=(14, 7))

    def setup_ax(ax, title):
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=14, fontweight="bold")
        # Draw note labels
        for i, (x, y) in enumerate(pos):
            ax.text(x * 1.15, y * 1.15, NOTES[i], ha="center", va="center", fontsize=12, fontweight="bold")
        # Draw faint circle
        circle = plt.Circle((0, 0), 2.0, color="gray", fill=False, linestyle="--", alpha=0.3)
        ax.add_patch(circle)

    setup_ax(ax_good, "Consistent Cycle")
    setup_ax(ax_bad, "Inconsistent Cycle (fault at B)")

    # Arrow collections
    good_arrows = []
    bad_arrows = []
    good_labels = []
    bad_labels = []

    def clear_arrows(ax, arrows, labels):
        for a in arrows:
            a.remove()
        arrows.clear()
        for t in labels:
            t.remove()
        labels.clear()

    def add_arrow(ax, start, end, color, arrows):
        arrow = FancyArrowPatch(
            start, end,
            arrowstyle="->", mutation_scale=15,
            color=color, linewidth=2, zorder=4
        )
        ax.add_patch(arrow)
        arrows.append(arrow)

    def update(frame):
        # Number of steps revealed grows with frame
        max_step = min(N_NOTES, (frame * N_NOTES) // (FRAMES - 20) + 1)

        # --- Consistent cycle ---
        clear_arrows(ax_good, good_arrows, good_labels)
        cumulative = 0
        for step in range(max_step):
            u = step % N_NOTES
            v = (step + 1) % N_NOTES
            cumulative = (cumulative + DIRECTIONS_CONSISTENT[step]) % 48
            color = "green" if cumulative == 0 else "red"
            add_arrow(ax_good, pos[u], pos[v], color, good_arrows)
            # Cumulative label near midpoint
            mid = (pos[u] + pos[v]) / 2 * 0.85
            txt = ax_good.text(mid[0], mid[1], str(cumulative), fontsize=8, color=color, ha="center", va="center")
            good_labels.append(txt)

        # Show total holonomy
        total = cycle_holonomy(CYCLE_EDGES[:max_step], DIRECTIONS_CONSISTENT[:max_step]) if max_step > 0 else 0
        status = "✓ Consistent" if total == 0 else f"✗ Holonomy = {total}"
        txt = ax_good.text(0, -2.6, status, ha="center", va="top", fontsize=11, fontweight="bold",
                           color="green" if total == 0 else "red",
                           bbox=dict(boxstyle="round", facecolor="white", edgecolor="gray", alpha=0.8))
        good_labels.append(txt)

        # --- Broken cycle ---
        clear_arrows(ax_bad, bad_arrows, bad_labels)
        cumulative = 0
        for step in range(max_step):
            u = step % N_NOTES
            v = (step + 1) % N_NOTES
            cumulative = (cumulative + DIRECTIONS_BROKEN[step]) % 48
            color = "green" if cumulative == 0 else "red"
            add_arrow(ax_bad, pos[u], pos[v], color, bad_arrows)
            mid = (pos[u] + pos[v]) / 2 * 0.85
            txt = ax_bad.text(mid[0], mid[1], str(cumulative), fontsize=8, color=color, ha="center", va="center")
            bad_labels.append(txt)

        total_bad = cycle_holonomy(CYCLE_EDGES[:max_step], DIRECTIONS_BROKEN[:max_step]) if max_step > 0 else 0
        status_bad = "✓ Consistent" if total_bad == 0 else f"✗ Holonomy = {total_bad}"
        txt = ax_bad.text(0, -2.6, status_bad, ha="center", va="top", fontsize=11, fontweight="bold",
                          color="green" if total_bad == 0 else "red",
                          bbox=dict(boxstyle="round", facecolor="white", edgecolor="gray", alpha=0.8))
        bad_labels.append(txt)

        fig.suptitle(f"Holonomy Walk  —  step {max_step}/{N_NOTES}", fontsize=16, fontweight="bold")
        return good_arrows + bad_arrows + good_labels + bad_labels

    anim = FuncAnimation(fig, update, frames=FRAMES, blit=False)

    out_dir = Path("viz_output")
    out_dir.mkdir(exist_ok=True)
    gif_path = out_dir / "holonomy_walk.gif"
    print(f"Saving GIF to {gif_path} ...")
    anim.save(str(gif_path), writer="pillow", fps=FPS)
    print(f"Saved {gif_path}")

    # Static comparison
    fig2, (ax_g, ax_b) = plt.subplots(1, 2, figsize=(14, 7))
    setup_ax(ax_g, "Consistent Cycle (holonomy = 0)")
    setup_ax(ax_b, "Inconsistent Cycle (holonomy ≠ 0)")

    for ax, dirs, label in [(ax_g, DIRECTIONS_CONSISTENT, "good"), (ax_b, DIRECTIONS_BROKEN, "bad")]:
        cumulative = 0
        for step in range(N_NOTES):
            u = step % N_NOTES
            v = (step + 1) % N_NOTES
            cumulative = (cumulative + dirs[step]) % 48
            color = "green" if cumulative == 0 else "red"
            add_arrow(ax, pos[u], pos[v], color, [])
            mid = (pos[u] + pos[v]) / 2 * 0.85
            ax.text(mid[0], mid[1], str(cumulative), fontsize=8, color=color, ha="center", va="center")
        total = cycle_holonomy(CYCLE_EDGES, dirs)
        status = "✓ Consistent" if total == 0 else f"✗ Holonomy = {total}"
        ax.text(0, -2.6, status, ha="center", va="top", fontsize=12, fontweight="bold",
                color="green" if total == 0 else "red",
                bbox=dict(boxstyle="round", facecolor="white", edgecolor="gray", alpha=0.8))

    fig2.suptitle("Holonomy Comparison — Circle of Fifths", fontsize=16, fontweight="bold")
    static_path = out_dir / "holonomy_walk_static.png"
    fig2.savefig(str(static_path), dpi=150)
    print(f"Saved static figure to {static_path}")

    plt.close(fig)
    plt.close(fig2)


if __name__ == "__main__":
    run()
