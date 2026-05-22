"""
Metronome Viz — 9 agents with random initial phases converging to consensus.

Shows:
- Circular phase diagram (unit circle)
- Each agent as a dot on the circle
- Dots moving toward a common phase over time
- Convergence metric plotted alongside
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from constraint_theory_core import Metronome, henneberg_construct

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

N_AGENTS = 9
FRAMES = 120
FPS = 15
SEED = 42
RNG = random.Random(SEED)
TICKS_PER_FRAME = 2


def neighbors_of(edges, i):
    """Get neighbor indices for vertex i."""
    return [v if u == i else u for u, v in edges if u == i or v == i]


def circular_spread(phases):
    """0 = aligned, 1 = maximally spread."""
    sx = sum(math.cos(p) for p in phases)
    sy = sum(math.sin(p) for p in phases)
    return math.sqrt(sx * sx + sy * sy) / len(phases)


def run():
    edges = henneberg_construct(N_AGENTS)

    # Create agents with random initial phases
    agents = [
        Metronome(
            T=1.0,
            phi0=RNG.uniform(0, 2 * math.pi),
            epsilon=0.3,
            delta=0.577,
            neighbors=neighbors_of(edges, i),
            edges=edges,
            n_agents=N_AGENTS,
        )
        for i in range(N_AGENTS)
    ]

    # Pre-simulate
    history = []
    for _ in range(FRAMES):
        for _ in range(TICKS_PER_FRAME):
            for a in agents:
                a.tick()
            phases = [a.phase for a in agents]
            for a in agents:
                nbr_phases = [phases[j] for j in a.neighbors]
                a.correct(nbr_phases)
        history.append({
            "phases": [a.phase for a in agents],
            "spread": circular_spread([a.phase for a in agents]),
            "converged": sum(1 for a in agents if a.converged),
        })

    fig = plt.figure(figsize=(12, 6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1])
    ax_circle = fig.add_subplot(gs[0, 0], projection="polar")
    ax_spread = fig.add_subplot(gs[0, 1])

    # Polar plot: agents on unit circle
    dots = ax_circle.scatter([], [], c=[], cmap="cool", s=150, vmin=0, vmax=N_AGENTS - 1, zorder=5, edgecolors="k", linewidths=0.5)
    # Consensus marker
    consensus_dot = ax_circle.scatter([], [], c="red", s=300, marker="*", zorder=6, edgecolors="gold", linewidths=1)
    ax_circle.set_ylim(0, 1.2)
    ax_circle.set_yticks([])
    ax_circle.set_title("Agent Phases", pad=20)

    # Spread plot
    spread_line, = ax_spread.plot([], [], "b-", linewidth=2, label="Coherence")
    conv_line, = ax_spread.plot([], [], "g--", linewidth=1.5, label="Converged count")
    ax_spread.set_xlim(0, FRAMES)
    ax_spread.set_ylim(0, 1.1)
    ax_spread.set_xlabel("Frame")
    ax_spread.set_ylabel("Coherence (0=spread, 1=aligned)")
    ax_spread.set_title("Convergence Metrics")
    ax_spread.legend(loc="lower right")
    ax_spread.grid(True, alpha=0.3)

    title = fig.suptitle("")

    def update(frame):
        state = history[frame]
        phases = state["phases"]

        # Polar coordinates: theta = phase, r = 1.0
        thetas = np.array(phases)
        rs = np.ones(N_AGENTS)
        dots.set_offsets(np.column_stack([thetas, rs]))
        dots.set_array(np.arange(N_AGENTS))

        # Consensus target: circular mean
        sx = sum(math.cos(p) for p in phases)
        sy = sum(math.sin(p) for p in phases)
        consensus_theta = math.atan2(sy, sx)
        consensus_dot.set_offsets([[consensus_theta, 0.15]])

        # Spread plot
        frames_so_far = list(range(frame + 1))
        spreads = [history[i]["spread"] for i in frames_so_far]
        convs = [history[i]["converged"] / N_AGENTS for i in frames_so_far]
        spread_line.set_data(frames_so_far, spreads)
        conv_line.set_data(frames_so_far, convs)

        title.set_text(
            f"Metronome Consensus  |  frame {frame + 1}/{FRAMES}  |  "
            f"spread={state['spread']:.3f}  converged={state['converged']}/{N_AGENTS}"
        )
        return dots, consensus_dot, spread_line, conv_line, title

    anim = FuncAnimation(fig, update, frames=FRAMES, blit=False)

    out_dir = Path("viz_output")
    out_dir.mkdir(exist_ok=True)
    gif_path = out_dir / "metronome_consensus.gif"
    print(f"Saving GIF to {gif_path} ...")
    anim.save(str(gif_path), writer="pillow", fps=FPS)
    print(f"Saved {gif_path}")

    # Static final
    fig2, (ax_c, ax_s) = plt.subplots(1, 2, figsize=(12, 6), subplot_kw={"projection": "polar"} if False else {})
    # Re-do without polar on second for spread
    fig2.clf()
    ax_c = fig2.add_subplot(1, 2, 1, projection="polar")
    ax_s = fig2.add_subplot(1, 2, 2)

    final = history[-1]
    phases = final["phases"]
    thetas = np.array(phases)
    ax_c.scatter(thetas, np.ones(N_AGENTS), c=np.arange(N_AGENTS), cmap="cool", s=150, edgecolors="k", linewidths=0.5, zorder=5)
    sx = sum(math.cos(p) for p in phases)
    sy = sum(math.sin(p) for p in phases)
    consensus_theta = math.atan2(sy, sx)
    ax_c.scatter([consensus_theta], [0.15], c="red", s=300, marker="*", edgecolors="gold", linewidths=1, zorder=6)
    ax_c.set_ylim(0, 1.2)
    ax_c.set_yticks([])
    ax_c.set_title("Final Agent Phases")

    frames_all = list(range(FRAMES))
    spreads_all = [h["spread"] for h in history]
    convs_all = [h["converged"] / N_AGENTS for h in history]
    ax_s.plot(frames_all, spreads_all, "b-", linewidth=2, label="Coherence")
    ax_s.plot(frames_all, convs_all, "g--", linewidth=1.5, label="Converged fraction")
    ax_s.set_xlim(0, FRAMES)
    ax_s.set_ylim(0, 1.05)
    ax_s.set_xlabel("Frame")
    ax_s.set_ylabel("Value")
    ax_s.set_title("Convergence Over Time")
    ax_s.legend()
    ax_s.grid(True, alpha=0.3)

    fig2.suptitle(f"Final: spread={final['spread']:.4f}, converged={final['converged']}/{N_AGENTS}")
    fig2.tight_layout()

    static_path = out_dir / "metronome_consensus_static.png"
    fig2.savefig(str(static_path), dpi=150)
    print(f"Saved static figure to {static_path}")

    plt.close(fig)
    plt.close(fig2)


if __name__ == "__main__":
    run()
