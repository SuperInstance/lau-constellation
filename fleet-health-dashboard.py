#!/usr/bin/env python3
"""Fleet CI Health Dashboard — summarize SuperInstance org CI status."""

import subprocess
import json
import sys
from collections import defaultdict

def get_repos():
    """Get all SuperInstance repos."""
    result = subprocess.run(
        ["gh", "repo", "list", "SuperInstance", "--limit", "200", "--json", "name,defaultBranchRef,primaryLanguage"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

def get_ci_status(repo_name):
    """Get latest CI run status for a repo."""
    result = subprocess.run(
        ["gh", "api", f"repos/SuperInstance/{repo_name}/actions/runs?per_page=1",
         "--jq", ".workflow_runs[0] | {conclusion, status, head_branch, created_at}"],
        capture_output=True, text=True
    )
    if not result.stdout.strip() or result.stdout == "null":
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

def main():
    print("🔍 SuperInstance Fleet CI Health Dashboard")
    print("=" * 60)
    
    repos = get_repos()
    categories = defaultdict(list)
    
    for repo in repos:
        name = repo["name"]
        lang = repo.get("primaryLanguage", {}) or {}
        lang_name = lang.get("name", "none") if lang else "none"
        
        ci = get_ci_status(name)
        
        if ci is None or ci.get("conclusion") is None:
            status = "NO_CI"
        elif ci["conclusion"] == "success":
            status = "GREEN"
        elif ci["conclusion"] == "failure":
            status = "FAIL"
        elif ci["status"] in ("in_progress", "queued", "waiting"):
            status = "RUNNING"
        else:
            status = ci["conclusion"].upper()
        
        categories[status].append((name, lang_name))
    
    # Print summary
    print(f"\n📊 Summary ({len(repos)} repos)")
    print("-" * 40)
    order = ["GREEN", "FAIL", "RUNNING", "NO_CI", "CANCELED", "TIMED_OUT"]
    for status in order:
        repos_list = categories.get(status, [])
        emoji = {"GREEN": "🟢", "FAIL": "🔴", "RUNNING": "🔄", "NO_CI": "⬜", "CANCELED": "🟡", "TIMED_OUT": "🟠"}.get(status, "❓")
        print(f"  {emoji} {status}: {len(repos_list)}")
    
    print(f"\n🟢 GREEN ({len(categories['GREEN'])})")
    for name, lang in sorted(categories["GREEN"]):
        print(f"  ✓ {name} ({lang})")
    
    print(f"\n🔴 FAILING ({len(categories['FAIL'])})")
    for name, lang in sorted(categories["FAIL"]):
        print(f"  ✗ {name} ({lang})")
    
    print(f"\n🔄 RUNNING ({len(categories.get('RUNNING', []))})")
    for name, lang in sorted(categories.get("RUNNING", [])):
        print(f"  ⟳ {name} ({lang})")
    
    # Health score
    with_ci = len(categories["GREEN"]) + len(categories["FAIL"]) + len(categories.get("RUNNING", []))
    if with_ci > 0:
        health = len(categories["GREEN"]) / with_ci * 100
        print(f"\n📈 CI Health Score: {health:.1f}% ({len(categories['GREEN'])}/{with_ci} with CI)")
    
    total = len(repos)
    coverage = with_ci / total * 100
    print(f"📈 CI Coverage: {coverage:.1f}% ({with_ci}/{total} repos have CI)")

if __name__ == "__main__":
    main()
