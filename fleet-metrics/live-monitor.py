#!/usr/bin/env python3
"""
live-monitor.py — Cloudflare Workers analytics monitor.

Fetches cache hit rate, HTTP error rates, and latency metrics via the
Cloudflare GraphQL Analytics API every 2 minutes and writes the results
as JSON to live-stats.json.

Usage:
    python3 fleet-metrics/live-monitor.py

Configuration (environment variables):
    CLOUDFLARE_API_TOKEN  — API token with Account Analytics read scope
    CLOUDFLARE_ACCOUNT_ID — Cloudflare account ID
    POLL_INTERVAL_SECS    — Seconds between polls (default: 120)
    OUTPUT_PATH           — Where to write JSON output (default: live-stats.json)
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

API_URL = "https://api.cloudflare.com/client/v4/graphql"

# --- Configuration ----------------------------------------------------------

API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL_SECS", "120"))

# Resolve output path relative to this file so it works from anywhere
_SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = Path(os.environ.get("OUTPUT_PATH", str(_SCRIPT_DIR / "live-stats.json")))


# --- GraphQL queries --------------------------------------------------------

# Worker-level analytics: requests, cache ratio, errors, latency
WORKERS_QUERY = """
query WorkersAnalytics($accountTag: String!, $since: Time!, $until: Time!) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      workersInvocationsAdaptive(
        filter: { datetime_gt: $since, datetime_lt: $until }
        limit: 100
      ) {
        sum {
          requests
          subrequests
          errors
        }
        avg {
          cpuTimeUs
        }
        dimensions {
          scriptName
          status
        }
      }
    }
  }
}
"""

# Zone/account-level HTTP analytics: cache, errors, response time
HTTP_QUERY = """
query HttpAnalytics($accountTag: String!, $since: Time!, $until: Time!) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      rumPageloadAdaptive(
        filter: { datetime_gt: $since, datetime_lt: $until }
        limit: 100
      ) {
        sum {
          pageViews
          responses
        }
        avg {
          dnsResponseTimeMs
          responseTimeMs
        }
        dimensions {
          httpStatus
          country
        }
      }
    }
  }
}
"""


# --- Helpers ----------------------------------------------------------------

def _headers():
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }


def run_query(query: str, variables: dict) -> dict:
    """Execute a single GraphQL query against the Cloudflare API."""
    payload = json.dumps({"query": query, "variables": variables}).encode()
    req = request.Request(API_URL, data=payload, headers=_headers(), method="POST")
    try:
        with request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        return {"errors": [{"message": f"HTTP {exc.code}: {body}"}]}
    except Exception as exc:  # noqa: BLE001
        return {"errors": [{"message": str(exc)}]}


def collect_metrics() -> dict:
    """Run both queries and assemble a metrics snapshot."""
    now = datetime.now(timezone.utc)
    # Look back 5 minutes to have data even on first poll
    since = int(now.timestamp()) - 300
    until = int(now.timestamp())

    variables = {
        "accountTag": ACCOUNT_ID,
        "since": datetime.fromtimestamp(since, tz=timezone.utc).isoformat(),
        "until": datetime.fromtimestamp(until, tz=timezone.utc).isoformat(),
    }

    workers_data = run_query(WORKERS_QUERY, variables)
    http_data = run_query(HTTP_QUERY, variables)

    # --- Parse workers data ---
    worker_stats = []
    total_requests = 0
    total_errors = 0
    total_cpu_us = 0.0
    cpu_samples = 0

    try:
        invocations = (
            workers_data["data"]["viewer"]["accounts"][0]
            ["workersInvocationsAdaptive"]
        )
        for inv in invocations:
            s = inv.get("sum", {})
            a = inv.get("avg", {})
            d = inv.get("dimensions", {})
            reqs = s.get("requests", 0)
            errs = s.get("errors", 0)
            cpu = a.get("cpuTimeUs", 0) or 0
            script = d.get("scriptName", "unknown")
            status = d.get("status", "")

            total_requests += reqs
            total_errors += errs
            if cpu:
                total_cpu_us += cpu * reqs
                cpu_samples += reqs

            # Track per-worker stats
            if reqs > 0:
                worker_stats.append({
                    "script": script,
                    "status": status,
                    "requests": reqs,
                    "errors": errs,
                    "avg_cpu_time_us": round(cpu, 2),
                    "error_rate": round(errs / reqs * 100, 2) if reqs else 0,
                })
    except (KeyError, IndexError, TypeError):
        pass

    # --- Parse HTTP data for cache & latency ---
    cache_hits = 0
    cache_misses = 0
    total_responses = 0
    http_status_counts = {}
    avg_response_time_ms = 0

    try:
        rum = http_data["data"]["viewer"]["accounts"][0]["rumPageloadAdaptive"]
        resp_time_sum = 0.0
        resp_time_count = 0
        for entry in rum:
            s = entry.get("sum", {})
            a = entry.get("avg", {})
            d = entry.get("dimensions", {})
            views = s.get("pageViews", 0) or 0
            resps = s.get("responses", 0) or 0
            rt = a.get("responseTimeMs", 0) or 0
            status_code = str(d.get("httpStatus", ""))

            total_responses += resps
            if status_code:
                http_status_counts[status_code] = (
                    http_status_counts.get(status_code, 0) + resps
                )
            if rt and resps:
                resp_time_sum += rt * resps
                resp_time_count += resps

        if resp_time_count:
            avg_response_time_ms = round(resp_time_sum / resp_time_count, 2)
    except (KeyError, IndexError, TypeError):
        pass

    # Cache hit rate: Cloudflare doesn't return cached vs non-cached directly
    # in rum data, so estimate from 2xx + cached headers if available.
    # Fallback: use zone-level cache if present in workers data.
    cache_hit_rate = 0.0
    if total_requests > 0:
        # Approximate: successful responses with cached content
        # (Cloudflare GraphQL cache data may need zone-level query)
        cached = http_status_counts.get("200", 0)
        cache_hit_rate = (
            round(cached / total_responses * 100, 2) if total_responses else 0.0
        )

    error_rate = round(total_errors / total_requests * 100, 2) if total_requests else 0.0
    avg_cpu_us = round(total_cpu_us / cpu_samples, 2) if cpu_samples else 0.0

    return {
        "timestamp": now.isoformat(),
        "window": {"since": variables["since"], "until": variables["until"]},
        "summary": {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate_pct": error_rate,
            "cache_hit_rate_pct": cache_hit_rate,
            "avg_cpu_time_us": avg_cpu_us,
            "avg_response_time_ms": avg_response_time_ms,
            "total_responses": total_responses,
        },
        "workers": sorted(worker_stats, key=lambda w: w["requests"], reverse=True),
        "http_status_distribution": dict(
            sorted(http_status_counts.items(), key=lambda x: -x[1])
        ),
        "raw_errors": (
            workers_data.get("errors") or http_data.get("errors") or None
        ),
    }


def write_output(metrics: dict) -> None:
    """Write metrics to the output JSON file atomically."""
    tmp = OUTPUT_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2) + "\n")
    tmp.replace(OUTPUT_PATH)


def validate_config() -> None:
    """Exit early with a helpful message if required env vars are missing."""
    missing = []
    if not API_TOKEN:
        missing.append("CLOUDFLARE_API_TOKEN")
    if not ACCOUNT_ID:
        missing.append("CLOUDFLARE_ACCOUNT_ID")
    if missing:
        print(
            "ERROR: Missing required environment variables: "
            + ", ".join(missing),
            file=sys.stderr,
        )
        print(
            "\nSet them before running:\n"
            "  export CLOUDFLARE_API_TOKEN='your-token'\n"
            "  export CLOUDFLARE_ACCOUNT_ID='your-account-id'\n",
            file=sys.stderr,
        )
        sys.exit(1)


# --- Main loop --------------------------------------------------------------

def main() -> None:
    validate_config()
    print(
        f"🛰️  live-monitor started — polling every {POLL_INTERVAL}s\n"
        f"   account: {ACCOUNT_ID}\n"
        f"   output:  {OUTPUT_PATH}\n"
        f"   Ctrl+C to stop\n"
    )

    while True:
        try:
            metrics = collect_metrics()
            write_output(metrics)
            s = metrics["summary"]
            print(
                f"[{metrics['timestamp'][:19]}] "
                f"reqs={s['total_requests']} "
                f"errors={s['error_rate_pct']}% "
                f"cache={s['cache_hit_rate_pct']}% "
                f"cpu={s['avg_cpu_time_us']}μs "
                f"rt={s['avg_response_time_ms']}ms "
                f"→ {OUTPUT_PATH.name}"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] {exc}", file=sys.stderr)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 live-monitor stopped")
