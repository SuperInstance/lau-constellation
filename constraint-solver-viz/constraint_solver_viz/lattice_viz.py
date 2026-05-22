"""
Lattice Viz — animate points snapping to the Eisenstein A₂ lattice.

Shows:
- Random points drifting toward their snapped lattice positions
- Voronoi cell colouring
- Quantization error as point size
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from scipy.spatial import Voronoi, voronoi_plot_2d

from constraint_theory_core.lattice import snap, A2Point, covering_radius, OMEGA_RE, OMEGA_IM

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

N_POINTS = 30
FRAMES = 120
FPS = 20
SEED = 42
RNG = random.Random(SEED)

# Lattice display range
A_RANGE = range(-4, 5)
B_RANGE = range(-4, 5)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def lattice_points():
    """Return all A₂ lattice points in the display range as (x, y)."""
    pts = []
    for a in A_RANGE:
        for b in B_RANGE:
            p = A2Point(a, b)
            pts.append(p.to_complex())
    return pts


def generate_random_points(n: int):
    """Generate n random points and their snap targets."""
    points = []
    targets = []
    for _ in range(n):
        a = RNG.uniform(-3.5, 3.5)
        b = RNG.uniform(-3.5, 3.5)
        x = a + b * OMEGA_RE
        y = b * OMEGA_IM
        pt, err = snap(x, y)
        tx, ty = pt.to_complex()
        points.append([x, y])
        targets.append([tx, ty, err])
    return np.array(points), np.array(targets)


def make_voronoi():
    """Build Voronoi diagram for the lattice points."""
    pts = lattice_points()
    # Add bounding box points to close infinite regions
    margin = 5.0
    bbox = [
        [-margin, -margin],
        [margin, -margin],
        [margin, margin],
        [-margin, margin],
    ]
    all_pts = np.vstack([pts, bbox])
    return Voronoi(all_pts)


# ---------------------------------------------------------------------------
# Animation
# ---------------------------------------------------------------------------

def animate():
    rng = RNG
    points, targets = generate_random_points(N_POINTS)
    target_xy = targets[:, :2]
    errors = targets[:, 2]

    # Interpolation: ease-out cubic
    def ease(t):
        return 1 - (1 - t) ** 3

    fig, ax = plt.subplots(figsize=(8, 8))

    # Draw Voronoi cells (static background)
    vor = make_voronoi()
    voronoi_plot_2d(
        vor,
        ax=ax,
        show_vertices=False,
        line_colors="gray",
        line_alpha=0.3,
        line_width=0.5,
        point_size=0,
    )

    # Colour Voronoi regions by distance from origin
    for region_idx, region in enumerate(vor.regions):
        if not region or -1 in region:
            continue
        polygon = [vor.vertices[i] for i in region]
        centroid = np.mean(polygon, axis=0)
        dist = math.sqrt(centroid[0] ** 2 + centroid[1] ** 2)
        color = plt.cm.viridis(min(dist / 4.0, 1.0))
        ax.fill(*zip(*polygon), color=color, alpha=0.15)

    # Draw lattice points
    lattice_xy = np.array(lattice_points())
    ax.scatter(
        lattice_xy[:, 0],
        lattice_xy[:, 1],
        c="black",
        s=20,
        zorder=3,
        marker="+",
        label="Lattice points",
    )

    # Draw covering-radius circles around lattice points
    rho = covering_radius()
    for x, y in lattice_xy:
        circle = plt.Circle((x, y), rho, color="blue", fill=False, alpha=0.15, linewidth=0.5)
        ax.add_patch(circle)

    # Animated scatter
    scatter = ax.scatter([], [], c=[], s=[], cmap="coolwarm", vmin=0, vmax=0.6, zorder=4)

    # Title and annotations
    title = ax.set_title("")
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_aspect("equal")
    ax.set_xlabel("Re")
    ax.set_ylabel("Im")
    ax.legend(loc="upper right", fontsize=8)

    # Snap lines (will be updated each frame)
    lines = []

    def init():
        scatter.set_offsets(np.empty((0, 2)))
        scatter.set_sizes([])
        scatter.set_array(np.array([]))
        for ln in lines:
            ln.remove()
        lines.clear()
        title.set_text("")
        return scatter, title

    def update(frame):
        t = frame / (FRAMES - 1)
        alpha = ease(t)

        # Interpolate positions
        curr = points * (1 - alpha) + target_xy * alpha

        # Point size proportional to remaining error
        remaining_err = errors * (1 - alpha)
        sizes = 50 + 300 * remaining_err

        # Colour by remaining error
        scatter.set_offsets(curr)
        scatter.set_sizes(sizes)
        scatter.set_array(remaining_err)

        # Snap lines (fading out)
        for ln in lines:
            ln.remove()
        lines.clear()
        if t < 0.9:
            for i in range(N_POINTS):
                if remaining_err[i] > 0.02:
                    ln = ax.plot(
                        [points[i, 0], curr[i, 0]],
                        [points[i, 1], curr[i, 1]],
                        "k-",
                        alpha=0.1 * (1 - alpha),
                        linewidth=0.3,
                    )[0]
                    lines.append(ln)

        title.set_text(
            f"A₂ Lattice Snap  |  frame {frame + 1}/{FRAMES}  |  "
            f"ρ = {rho:.3f}  |  avg err = {np.mean(remaining_err):.4f}"
        )
        return scatter, title, *lines

    anim = FuncAnimation(fig, update, frames=FRAMES, init_func=init, blit=False)

    out_dir = Path("viz_output")
    out_dir.mkdir(exist_ok=True)
    gif_path = out_dir / "lattice_snap.gif"
    mp4_path = out_dir / "lattice_snap.mp4"

    print(f"Saving GIF to {gif_path} ...")
    anim.save(str(gif_path), writer="pillow", fps=FPS)
    print(f"Saved {gif_path}")

    # Try MP4 (requires ffmpeg)
    try:
        print(f"Saving MP4 to {mp4_path} ...")
        anim.save(str(mp4_path), writer="ffmpeg", fps=FPS)
        print(f"Saved {mp4_path}")
    except Exception as exc:
        print(f"MP4 skipped ({exc})")

    plt.close(fig)


# ---------------------------------------------------------------------------
# Static figure fallback
# ---------------------------------------------------------------------------

def static_figure():
    """Produce a static summary figure."""
    points, targets = generate_random_points(N_POINTS)
    target_xy = targets[:, :2]
    errors = targets[:, 2]

    fig, ax = plt.subplots(figsize=(8, 8))

    vor = make_voronoi()
    voronoi_plot_2d(vor, ax=ax, show_vertices=False, line_colors="gray", line_alpha=0.3, line_width=0.5, point_size=0)

    for region_idx, region in enumerate(vor.regions):
        if not region or -1 in region:
            continue
        polygon = [vor.vertices[i] for i in region]
        centroid = np.mean(polygon, axis=0)
        dist = math.sqrt(centroid[0] ** 2 + centroid[1] ** 2)
        color = plt.cm.viridis(min(dist / 4.0, 1.0))
        ax.fill(*zip(*polygon), color=color, alpha=0.15)

    lattice_xy = np.array(lattice_points())
    ax.scatter(lattice_xy[:, 0], lattice_xy[:, 1], c="black", s=20, zorder=3, marker="+")

    rho = covering_radius()
    for x, y in lattice_xy:
        ax.add_patch(plt.Circle((x, y), rho, color="blue", fill=False, alpha=0.15, linewidth=0.5))

    # Final snapped positions
    sc = ax.scatter(target_xy[:, 0], target_xy[:, 1], c=errors, s=50 + 300 * errors, cmap="coolwarm", vmin=0, vmax=0.6, zorder=4, edgecolors="k", linewidths=0.3)
    plt.colorbar(sc, ax=ax, label="Quantization error")

    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_aspect("equal")
    ax.set_title("Eisenstein A₂ Lattice Snap (final state)")
    ax.set_xlabel("Re")
    ax.set_ylabel("Im")

    out_path = Path("viz_output") / "lattice_snap_static.png"
    fig.savefig(str(out_path), dpi=150)
    print(f"Saved static figure to {out_path}")
    plt.close(fig)


if __name__ == "__main__":
    animate()
    static_figure()
