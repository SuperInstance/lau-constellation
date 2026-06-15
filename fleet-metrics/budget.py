"""
Fleet budget conservation model: gamma + eta = C

  gamma  — productive spend (work output reaching end goal)
  eta    — overhead spend (inter-agent coordination, coupling cost)
  C      — total budget envelope (fixed per time unit)

Overhead fraction is the uncancelled coupling: max(0, delta(n)).
Clipping at 0 handles the n=1 formula artifact where delta goes negative
(a single agent has no inter-agent coordination cost by definition).
"""

from conservation_law import delta


def compute_budget_split(n: int, C: float = 1.0) -> tuple:
    """Return (gamma, eta) for n agents with total budget C."""
    uncancelled = max(0.0, delta(n))
    eta = uncancelled * C
    gamma = C - eta
    return gamma, eta


def budget_summary(metrics: dict, C: float = 1.0) -> list:
    """Compute budget splits for every agent count in metrics."""
    rows = []
    for entry in metrics["agents"]:
        n = entry["n"]
        gamma, eta = compute_budget_split(n, C)
        rows.append({
            "n": n,
            "C": round(C, 6),
            "gamma": round(gamma, 6),
            "eta": round(eta, 6),
            "productive_pct": round(gamma / C * 100.0, 4),
            "overhead_pct": round(eta / C * 100.0, 4),
            "per_agent_overhead": round(eta / n, 8),
        })
    return rows


def peak_overhead_row(budget_rows: list) -> dict:
    """Return the row with the highest overhead (worst coupling scenario)."""
    return max(budget_rows, key=lambda r: r["overhead_pct"])


def cost_savings_analysis(budget_rows: list, target_n: int = 50) -> dict:
    """
    Compute savings when scaling to target_n agents vs peak-overhead scenario.

    Key insight: overhead first rises (coordination cost grows faster than
    cancellation kicks in), peaks around n=4-5, then falls as fleet
    cancellation dominates.  Scaling to n=50 recovers most of that overhead.
    """
    peak = peak_overhead_row(budget_rows)
    target_row = next(r for r in budget_rows if r["n"] == target_n)

    overhead_reduction_pct_points = round(
        peak["overhead_pct"] - target_row["overhead_pct"], 4
    )
    per_agent_reduction_factor = round(
        peak["per_agent_overhead"] / max(target_row["per_agent_overhead"], 1e-12), 2
    )

    return {
        "peak_overhead": {
            "n": peak["n"],
            "overhead_pct": peak["overhead_pct"],
            "per_agent_overhead": peak["per_agent_overhead"],
        },
        "target_fleet": {
            "n": target_row["n"],
            "overhead_pct": target_row["overhead_pct"],
            "per_agent_overhead": target_row["per_agent_overhead"],
        },
        "overhead_reduction_pct_points": overhead_reduction_pct_points,
        "per_agent_overhead_reduction_factor": per_agent_reduction_factor,
        "description": (
            f"Scaling from {peak['n']} to {target_n} agents reduces overhead by "
            f"{overhead_reduction_pct_points:.2f} percentage points "
            f"and cuts per-agent coordination cost by {per_agent_reduction_factor}x."
        ),
    }
