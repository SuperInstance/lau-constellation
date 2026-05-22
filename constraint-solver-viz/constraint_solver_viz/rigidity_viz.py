"""
Rigidity Viz — build a Laman graph via Henneberg construction step-by-step.

Shows:
- Graph vertices and edges appearing one by one
- Rigidity matrix filling in
- Final algebraic connectivity result
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyBboxPatch

from constraint_theory_core.rigidity import henneberg_construct, algebraic_connectivity

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

N_VERTICES = 9
SEED = 42
FRAMES = 120
FPS = 15


def layout_vertices(n: int, seed: int = 42) -> np.ndarray:
    """Place vertices on a circle for clean visualisation."""
    rng = np.random.default_rng(seed)
    angles = np.sort(rng.uniform(0, 2 * math.pi, n))
    radius = 2.0
    return np.column_stack([radius * np.cos(angles), radius * np.sin(angles)])


def build_step_edges(edges: list[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    """Group edges by the maximum vertex index they involve."""
    # Frame 0: just vertex 0
    # Then add vertex 1 with edge (0,1)
    # Then add vertex 2 with edges connecting to it
    steps: list[list[tuple[int, int]]] = [[]]
    current: list[tuple[int, int]] = []
    max_v = 0
    for e in edges:
        u, v = e
        new_max = max(u, v)
        if new_max > max_v:
            # New vertex step
            current = current.copy()
            current.append(e)
            steps.append(current)
            max_v = new_max
        else:
            # Edge within existing vertices
            current = current.copy()
            current.append(e)
            steps[-1] = current
    return steps


def rigidity_matrix(edges: list[tuple[int, int]], pos: np.ndarray) -> np.ndarray:
    """Build the rigidity matrix R (|E| × 2|V|)."""
    m = len(edges)
    n = len(pos)
    R = np.zeros((m, 2 * n))
    for row, (u, v) in enumerate(edges):
        dx = pos[v, 0] - pos[u, 0]
        dy = pos[v, 1] - pos[u, 1]
        dist = math.hypot(dx, dy) + 1e-9
        # Row for edge (u,v): direction cosines
        R[row, 2 * u] = -dx / dist
        R[row, 2 * u + 1] = -dy / dist
        R[row, 2 * v] = dx / dist
        R[row, 2 * v + 1] = dy / dist
    return R


def run():
    edges = henneberg_construct(N_VERTICES, seed=SEED)
    pos = layout_vertices(N_VERTICES, seed=SEED)
    step_edges = build_step_edges(edges)
    n_steps = len(step_edges)

    # Pre-compute frames: each step gets a few frames for smoothness
    frames_per_step = max(1, FRAMES // n_steps)
    frame_map = []
    for step_idx in range(n_steps):
        frame_map.extend([step_idx] * frames_per_step)
    # Ensure exact frame count
    while len(frame_map) < FRAMES:
        frame_map.append(n_steps - 1)
    frame_map = frame_map[:FRAMES]

    fig = plt.figure(figsize=(14, 6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.2])
    ax_graph = fig.add_subplot(gs[0, 0])
    ax_matrix = fig.add_subplot(gs[0, 1])

    # Graph elements
    vertex_scatter = ax_graph.scatter([], [], c="steelblue", s=300, zorder=5, edgecolors="k", linewidths=1)
    labels = []
    edge_lines = []

    ax_graph.set_xlim(-3, 3)
    ax_graph.set_ylim(-3, 3)
    ax_graph.set_aspect("equal")
    ax_graph.set_title("Laman Graph (Henneberg I)")
    ax_graph.axis("off")

    # Matrix image
    matrix_im = ax_matrix.imshow(np.zeros((1, 1)), cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax_matrix.set_title("Rigidity Matrix")
    ax_matrix.set_xlabel("Coordinate index (2×vertex)")
    ax_matrix.set_ylabel("Edge index")

    # Final-result text box (shown at end)
    result_box = ax_graph.text(
        0.5, 0.02, "", transform=ax_graph.transAxes,
        fontsize=11, ha="center", va="bottom",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", edgecolor="gray")
    )

    title = fig.suptitle("")

    def update(frame):
        step_idx = frame_map[frame]
        current_edges = step_edges[step_idx]

        # Determine visible vertices
        visible = set()
        for u, v in current_edges:
            visible.add(u)
            visible.add(v)
        if not visible:
            visible = {0}
        visible = sorted(visible)

        # Update vertices
        vpos = pos[visible]
        vertex_scatter.set_offsets(vpos)

        # Update labels
        for txt in labels:
            txt.remove()
        labels.clear()
        for i, v in enumerate(visible):
            txt = ax_graph.text(vpos[i, 0], vpos[i, 1], str(v), ha="center", va="center", fontsize=10, fontweight="bold", zorder=6)
            labels.append(txt)

        # Update edges
        for ln in edge_lines:
            ln.remove()
        edge_lines.clear()
        for u, v in current_edges:
            ln = ax_graph.plot([pos[u, 0], pos[v, 0]], [pos[u, 1], pos[v, 1]], "k-", linewidth=1.5, zorder=3)[0]
            edge_lines.append(ln)

        # Update rigidity matrix
        if current_edges:
            R = rigidity_matrix(current_edges, pos)
            # Only show columns for visible vertices
            cols = []
            for v in range(N_VERTICES):
                cols.extend([2 * v, 2 * v + 1])
            R_disp = R[:, cols]
        else:
            R_disp = np.zeros((1, 1))

        matrix_im.set_array(R_disp)
        matrix_im.set_extent([-0.5, R_disp.shape[1] - 0.5, R_disp.shape[0] - 0.5, -0.5])
        ax_matrix.set_xlim(-0.5, max(R_disp.shape[1] - 0.5, 0.5))
        ax_matrix.set_ylim(max(R_disp.shape[0] - 0.5, 0.5), -0.5)

        # Stats
        n_v = len(visible)
        n_e = len(current_edges)
        expected = 2 * n_v - 3 if n_v >= 2 else 0

        if frame == FRAMES - 1:
            lam2 = algebraic_connectivity(edges, N_VERTICES)
            result_box.set_text(
                f"Vertices: {N_VERTICES}  |  Edges: {len(edges)}  |  Expected: {2 * N_VERTICES - 3}\n"
                f"Algebraic connectivity λ₂ = {lam2:.4f}"
            )
        else:
            result_box.set_text(f"Vertices: {n_v}  |  Edges: {n_e}  |  Expected: {expected}")

        title.set_text(f"Laman Rigidity Construction  —  step {step_idx + 1}/{n_steps}")
        fig.canvas.draw_idle()
        return vertex_scatter, matrix_im, result_box, title

    anim = FuncAnimation(fig, update, frames=FRAMES, blit=False)

    out_dir = Path("viz_output")
    out_dir.mkdir(exist_ok=True)
    gif_path = out_dir / "rigidity_construction.gif"
    print(f"Saving GIF to {gif_path} ...")
    anim.save(str(gif_path), writer="pillow", fps=FPS)
    print(f"Saved {gif_path}")

    # Static final frame
    fig2, (ax_g, ax_m) = plt.subplots(1, 2, figsize=(14, 6))
    ax_g.scatter(pos[:, 0], pos[:, 1], c="steelblue", s=300, zorder=5, edgecolors="k", linewidths=1)
    for i, p in enumerate(pos):
        ax_g.text(p[0], p[1], str(i), ha="center", va="center", fontsize=10, fontweight="bold", zorder=6)
    for u, v in edges:
        ax_g.plot([pos[u, 0], pos[v, 0]], [pos[v, 1], pos[u, 1]], "k-", linewidth=1.5, zorder=3)
    ax_g.set_xlim(-3, 3)
    ax_g.set_ylim(-3, 3)
    ax_g.set_aspect("equal")
    ax_g.set_title("Final Laman Graph")
    ax_g.axis("off")

    R = rigidity_matrix(edges, pos)
    im = ax_m.imshow(R, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax_m.set_title("Final Rigidity Matrix")
    ax_m.set_xlabel("Coordinate index (2×vertex)")
    ax_m.set_ylabel("Edge index")
    plt.colorbar(im, ax=ax_m)

    lam2 = algebraic_connectivity(edges, N_VERTICES)
    fig2.suptitle(f"λ₂ = {lam2:.4f}  |  |E| = {len(edges)} = 2×{N_VERTICES}−3 = {2*N_VERTICES-3}")
    fig2.tight_layout()

    static_path = out_dir / "rigidity_construction_static.png"
    fig2.savefig(str(static_path), dpi=150)
    print(f"Saved static figure to {static_path}")

    plt.close(fig)
    plt.close(fig2)


if __name__ == "__main__":
    run()
