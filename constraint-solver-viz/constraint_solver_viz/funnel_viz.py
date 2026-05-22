"""
Funnel Viz — animate the deadband funnel narrowing over time.

Shows:
- Multiple agents (dots) moving toward the centre
- Funnel boundary shrinking exponentially
- Anomaly detection: escaping dots turn red
- Uses actual TemporalAgent API
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from constraint_theory_core.temporal import TemporalAgent, FunnelPhase
from constraint_theory_core.lattice import covering_radius

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

N_AGENTS = 12
FRAMES = 150
FPS = 20
SEED = 42
RNG = random.Random(SEED)

# Time settings
T_START = 0.0
T_END = 15.0
DT = (T_END - T_START) / FRAMES

# Agent motion: drift toward centre with noise
NOISE_AMP = 0.15


def run():
    # -----------------------------------------------------------------------
    # Setup agents
    # -----------------------------------------------------------------------
    decay_rate = 0.25
    epsilon_0 = covering_radius()
    delta = covering_radius()

    agents: list[TemporalAgent] = [
        TemporalAgent(decay_rate=decay_rate, epsilon_0=epsilon_0, delta=delta)
        for _ in range(N_AGENTS)
    ]

    # Each agent has a 2-D position that we simulate
    positions = np.array([
        [RNG.uniform(-2.0, 2.0), RNG.uniform(-2.0, 2.0)]
        for _ in range(N_AGENTS)
    ])

    # Pre-compute trajectories and funnel states
    history: list[dict] = []
    t = T_START

    for frame in range(FRAMES):
        t += DT
        # Drift toward origin with noise
        drift = -0.08 * positions + NOISE_AMP * np.array([
            [RNG.gauss(0, 1), RNG.gauss(0, 1)] for _ in range(N_AGENTS)
        ])
        positions = positions + drift * DT

        results = []
        for i, agent in enumerate(agents):
            result = agent.observe(positions[i, 0], positions[i, 1], t=t)
            results.append(result)

        history.append({
            "t": t,
            "positions": positions.copy(),
            "results": results,
            "epsilon": agents[0].epsilon,
            "delta": delta,
        })

    # -----------------------------------------------------------------------
    # Build figure
    # -----------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 8))

    # Funnel boundary lines (updated each frame)
    epsilon_line_pos, = ax.plot([], [], "g--", linewidth=1.5, label="Deadband ε")
    epsilon_line_neg, = ax.plot([], [], "g--", linewidth=1.5)
    delta_line_pos, = ax.plot([], [], "r--", linewidth=1.0, alpha=0.5, label="Anomaly δ")
    delta_line_neg, = ax.plot([], [], "r--", linewidth=1.0, alpha=0.5)

    # Shaded funnel region
    funnel_fill = ax.fill_between([], [], [], color="green", alpha=0.1)
    approach_fill_top = ax.fill_between([], [], [], color="orange", alpha=0.08)
    approach_fill_bot = ax.fill_between([], [], [], color="orange", alpha=0.08)

    # Agent scatter
    scatter = ax.scatter([], [], c=[], s=80, cmap="RdYlGn_r", vmin=0, vmax=1, zorder=5, edgecolors="k", linewidths=0.5)

    # Centre cross
    ax.axhline(0, color="black", linewidth=0.5, alpha=0.3)
    ax.axvline(0, color="black", linewidth=0.5, alpha=0.3)

    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(loc="upper right", fontsize=9)

    title = ax.set_title("")

    # We need to manage fill_between artists manually
    fill_collections = []

    def update(frame):
        state = history[frame]
        pos = state["positions"]
        eps = state["epsilon"]
        delta = state["delta"]

        # Build funnel envelope curves as circular rings in 2-D
        # For 2-D visualisation we draw a circle of radius ε and δ
        theta = np.linspace(0, 2 * math.pi, 200)
        eps_x = eps * np.cos(theta)
        eps_y = eps * np.sin(theta)
        delta_x = delta * np.cos(theta)
        delta_y = delta * np.sin(theta)

        epsilon_line_pos.set_data(eps_x, eps_y)
        epsilon_line_neg.set_data([], [])
        delta_line_pos.set_data(delta_x, delta_y)
        delta_line_neg.set_data([], [])

        # Remove old fills
        nonlocal fill_collections
        for coll in fill_collections:
            coll.remove()
        fill_collections = []

        # Green fill: inside deadband
        fill_collections.append(ax.fill_between(eps_x, eps_y, -eps_y, color="green", alpha=0.08))
        # Actually fill_between needs 1-D x and y bounds; for a circle we'll use a polygon patch
        # Replace with Circle patches for cleaner look
        from matplotlib.patches import Circle

        # Remove old patches too
        for patch in getattr(ax, "_funnel_patches", []):
            patch.remove()
        ax._funnel_patches = []

        c1 = Circle((0, 0), eps, color="green", alpha=0.08, zorder=1)
        c2 = Circle((0, 0), delta, color="orange", alpha=0.06, zorder=1)
        ax.add_patch(c1)
        ax.add_patch(c2)
        ax._funnel_patches = [c1, c2]

        # Agent colours based on phase
        # 0 = green (narrowing), 0.5 = yellow (approach), 1 = red (anomaly)
        colours = []
        for r in state["results"]:
            if r.phase == FunnelPhase.ANOMALY:
                colours.append(1.0)
            elif r.phase == FunnelPhase.APPROACH:
                colours.append(0.5)
            else:
                colours.append(0.0)

        scatter.set_offsets(pos)
        scatter.set_array(np.array(colours))

        conv = sum(1 for r in state["results"] if r.phase == FunnelPhase.NARROWING)
        anom = sum(1 for r in state["results"] if r.phase == FunnelPhase.ANOMALY)
        title.set_text(
            f"Deadband Funnel  |  t={state['t']:.2f}s  |  "
            f"ε={eps:.4f}  |  narrowing={conv}/{N_AGENTS}  anomalies={anom}"
        )
        return scatter, epsilon_line_pos, delta_line_pos, title

    anim = FuncAnimation(fig, update, frames=FRAMES, blit=False)

    out_dir = Path("viz_output")
    out_dir.mkdir(exist_ok=True)
    gif_path = out_dir / "deadband_funnel.gif"
    print(f"Saving GIF to {gif_path} ...")
    anim.save(str(gif_path), writer="pillow", fps=FPS)
    print(f"Saved {gif_path}")

    # Static summary
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    final = history[-1]
    pos = final["positions"]
    colours = []
    for r in final["results"]:
        if r.phase == FunnelPhase.ANOMALY:
            colours.append("red")
        elif r.phase == FunnelPhase.APPROACH:
            colours.append("orange")
        else:
            colours.append("green")

    ax2.scatter(pos[:, 0], pos[:, 1], c=colours, s=80, edgecolors="k", linewidths=0.5, zorder=5)
    ax2.add_patch(plt.Circle((0, 0), final["epsilon"], color="green", fill=False, linestyle="--", linewidth=1.5))
    ax2.add_patch(plt.Circle((0, 0), final["delta"], color="red", fill=False, linestyle="--", linewidth=1.0, alpha=0.5))
    ax2.axhline(0, color="black", linewidth=0.5, alpha=0.3)
    ax2.axvline(0, color="black", linewidth=0.5, alpha=0.3)
    ax2.set_xlim(-3, 3)
    ax2.set_ylim(-3, 3)
    ax2.set_aspect("equal")
    ax2.set_title("Deadband Funnel — Final State")
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")

    static_path = out_dir / "deadband_funnel_static.png"
    fig2.savefig(str(static_path), dpi=150)
    print(f"Saved static figure to {static_path}")

    plt.close(fig)
    plt.close(fig2)


if __name__ == "__main__":
    run()
