"""
Conservation law metrics for SuperInstance fleet.

CLT second-order correction:
    delta(n) = (1/sqrt(n)) * (1 - 3/(2n))

- Leading 1/sqrt(n): CLT convergence rate
- Correction -3/(2n): skewness term; valid domain is n >= 3
- Coupling cancellation rate: fraction of inter-agent coupling interference
  that is cancelled by the symmetric fleet structure at scale n.
"""

import json
import math
import os


def delta(n: int) -> float:
    """CLT coupling correction term for n agents."""
    return (1.0 / math.sqrt(n)) * (1.0 - 3.0 / (2.0 * n))


def coupling_cancellation_rate(n: int) -> float:
    """
    Fraction of coupling cancelled at agent count n.
    Raw formula; may exceed [0,1] for very small n (formula artifact).
    Target: ~0.864 at n=50.
    """
    return 1.0 - delta(n)


def generate_theoretical_metrics() -> dict:
    """Generate n=1..100 theoretical dataset using CLT delta formula."""
    agents = []
    for n in range(1, 101):
        d = delta(n)
        ccr = coupling_cancellation_rate(n)
        agents.append({
            "n": n,
            "delta": round(d, 8),
            "coupling_cancellation_rate": round(ccr, 8),
        })
    return {
        "source": "theoretical",
        "formula": "delta(n) = (1/sqrt(n)) * (1 - 3/(2n))",
        "agents": agents,
    }


def load_or_generate_metrics(data_path: str = "fleet-metrics/data/metrics.json") -> dict:
    """
    Approach C hybrid: read real fleet data if metrics.json exists,
    otherwise generate theoretical dataset.
    """
    if os.path.exists(data_path):
        with open(data_path) as f:
            data = json.load(f)
        # Ensure required fields are present; backfill delta/CCR if absent.
        for entry in data.get("agents", []):
            n = entry["n"]
            if "delta" not in entry:
                entry["delta"] = round(delta(n), 8)
            if "coupling_cancellation_rate" not in entry:
                entry["coupling_cancellation_rate"] = round(coupling_cancellation_rate(n), 8)
        return data

    return generate_theoretical_metrics()
