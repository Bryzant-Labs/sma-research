#!/usr/bin/env python3
"""
Cross-Connection Engine — find insights that span multiple SMA campaigns.

The 1.0 goal: don't forget projects.
The 2.0 goal (this script): find connections between projects that nobody else can see.

Run: python cross_connection_engine.py [--dry-run] [--publish]

What it does:
1. Loads PROJECT_CATALOG.md to understand all campaigns
2. Ingests every finding markdown into CORTEX (if not already there)
3. Runs a sweep of cross-campaign queries
4. Generates insight markdown in findings/insights/YYYY-MM-DD.md
5. Optionally publishes to CORTEX + Dropbox + GitHub
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

# ============================================================================
# Configuration
# ============================================================================

DROPBOX_SMA = Path("/mnt/c/Users/bryza/Dropbox/Christian fischer/SMA")
CATALOG = DROPBOX_SMA / "PROJECT_CATALOG.md"
FINDINGS_DIR = DROPBOX_SMA / "findings"
INSIGHTS_DIR = FINDINGS_DIR / "insights"
PLATFORM_RESULTS = Path.home() / "gpu-fleet" / "results" / "SMA"

CORTEX_API = "http://217.154.10.79:8095"
SMA_PLATFORM_API = "https://sma-research.info/api/v2"

# Cross-queries designed to surface non-obvious connections
CROSS_QUERIES = [
    {
        "id": "pathway_coverage",
        "question": "Which compounds have been tested against multiple nodes of the ROCK-LIMK2-CFL2 axis? "
                    "Can we construct a combination therapy covering the full pathway?",
        "tags": ["pathway", "combo", "rock-limk-cfl2"],
    },
    {
        "id": "orphan_trajectories",
        "question": "Which molecular dynamics trajectories exist in our data but have never been analyzed "
                    "with MMPBSA, contact maps, or RMSD analysis?",
        "tags": ["md", "orphan-data", "analysis-gap"],
    },
    {
        "id": "selectivity_determinants",
        "question": "For our 14 LIMK2-selective compounds, what structural features distinguish them from "
                    "non-selective molecules? What residues on LIMK2 do they contact that LIMK1 lacks?",
        "tags": ["selectivity", "structure", "pharmacophore"],
    },
    {
        "id": "approved_drug_combos",
        "question": "Which FDA-approved drugs could be repurposed and combined for SMA based on our "
                    "computational screens? Are there synergies between approved compounds?",
        "tags": ["repurposing", "combo", "approved"],
    },
    {
        "id": "contradictions",
        "question": "Are there any contradictions between our campaigns — findings that suggest opposite "
                    "conclusions or compounds where one analysis says yes and another says no?",
        "tags": ["contradiction", "qa"],
    },
    {
        "id": "simon_ready",
        "question": "Which findings are ready to hand to Simon for wet-lab validation, and which still "
                    "need additional computational work to be considered complete?",
        "tags": ["simon", "wet-lab", "handoff"],
    },
    {
        "id": "published_connections",
        "question": "For each of our computational hits, what published SMA literature supports or "
                    "contradicts the hypothesis? Which hits have zero literature backing (novel) vs "
                    "strong backing (validated)?",
        "tags": ["literature", "novelty"],
    },
    {
        "id": "cross_campaign_compounds",
        "question": "Which compounds appear in multiple campaigns — either as primary candidates or as "
                    "controls — and what did each campaign say about them?",
        "tags": ["cross-ref", "compounds"],
    },
]

# ============================================================================
# HTTP helpers
# ============================================================================

def _post(url: str, payload: dict, timeout: int = 30) -> dict | None:
    try:
        req = Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[POST {url}] failed: {e}", file=sys.stderr)
        return None


def _get(url: str, timeout: int = 30) -> dict | None:
    try:
        req = Request(url, method="GET")
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[GET {url}] failed: {e}", file=sys.stderr)
        return None


def cortex_query(question: str, limit: int = 10) -> list[dict]:
    result = _post(f"{CORTEX_API}/query", {"question": question, "limit": limit}) or {}
    return result.get("results", [])


def cortex_learn(context: str, description: str, category: str = "finding") -> dict | None:
    return _post(
        f"{CORTEX_API}/learn",
        {
            "context": context[:4000],
            "description": description[:500],
            "category": category,
        },
    )


# ============================================================================
# Data loaders
# ============================================================================

def load_catalog_sections() -> dict[str, str]:
    """Parse PROJECT_CATALOG.md into sections keyed by campaign name."""
    if not CATALOG.exists():
        print(f"FATAL: catalog not found at {CATALOG}", file=sys.stderr)
        sys.exit(1)

    text = CATALOG.read_text(encoding="utf-8")
    sections: dict[str, str] = {}
    current_key = None
    current_buf: list[str] = []

    for line in text.splitlines():
        m = re.match(r"^###\s*<a name=\"([^\"]+)\"></a>\s*(.+)$", line)
        if m:
            if current_key:
                sections[current_key] = "\n".join(current_buf).strip()
            current_key = m.group(1)
            current_buf = [f"# {m.group(2)}"]
        elif current_key:
            current_buf.append(line)

    if current_key:
        sections[current_key] = "\n".join(current_buf).strip()

    return sections


def load_all_findings() -> list[dict]:
    """Load every FINDING_*.md from findings/ recursively."""
    findings: list[dict] = []
    for md_path in FINDINGS_DIR.rglob("FINDING_*.md"):
        try:
            content = md_path.read_text(encoding="utf-8")
            # First heading = title
            title_m = re.search(r"^#\s*(.+)$", content, re.MULTILINE)
            title = title_m.group(1).strip() if title_m else md_path.stem
            # Date from path or filename
            date_m = re.search(r"(\d{4}-\d{2}-\d{2})", md_path.name)
            date = date_m.group(1) if date_m else "unknown"
            findings.append({
                "path": str(md_path),
                "title": title,
                "date": date,
                "content": content,
                "filename": md_path.name,
            })
        except Exception as e:
            print(f"Failed to load {md_path}: {e}", file=sys.stderr)

    return findings


def load_platform_stats() -> dict:
    """Get current SMA platform stats (targets, drugs, trials, claims)."""
    return _get(f"{SMA_PLATFORM_API}/stats") or {}


def load_platform_targets(limit: int = 20) -> list[dict]:
    data = _get(f"{SMA_PLATFORM_API}/targets?per_page={limit}") or {}
    return data.get("items", data.get("targets", [])) if isinstance(data, dict) else []


def find_orphan_trajectories() -> list[dict]:
    """Scan for .dcd files without a matching analysis output."""
    orphans: list[dict] = []
    md_roots = [
        PLATFORM_RESULTS / "md_sims",
        DROPBOX_SMA / "GPU-Results-Trajectories",
        DROPBOX_SMA / "GPU-Results" / "md_simulations",
    ]
    for root in md_roots:
        if not root.exists():
            continue
        for dcd in root.rglob("*.dcd"):
            parent = dcd.parent
            has_mmpbsa = any(parent.glob("*mmpbsa*.json"))
            has_analysis = any(parent.glob("analysis*.json")) or any(parent.glob("contacts*.csv"))
            if not (has_mmpbsa or has_analysis):
                orphans.append({
                    "path": str(dcd),
                    "size_mb": dcd.stat().st_size / (1024 * 1024),
                    "parent": parent.name,
                })
    return orphans


# ============================================================================
# Insight generation
# ============================================================================

def ingest_findings_to_cortex(findings: list[dict], dry_run: bool = False) -> int:
    """Push each finding into CORTEX so cross-queries can find it."""
    count = 0
    for f in findings:
        desc = f"Finding {f['date']}: {f['title']}"
        if dry_run:
            print(f"  [DRY] would ingest: {desc}")
            count += 1
            continue
        result = cortex_learn(
            context=f["content"][:4000],
            description=desc[:500],
            category="finding",
        )
        if result and result.get("stored"):
            count += 1
    return count


def run_cross_queries() -> list[dict]:
    """Run the cross-campaign query sweep, return insights."""
    insights = []
    for q in CROSS_QUERIES:
        print(f"  Querying: {q['id']}")
        results = cortex_query(q["question"], limit=15)
        if not results:
            print(f"    (no results)")
            continue
        # Extract titles and content snippets for the insight
        hits = []
        for r in results[:10]:
            title = r.get("title") or r.get("content", "")[:120]
            hits.append({
                "title": title.strip().replace("\n", " ")[:200],
                "node_type": r.get("node_type", "?"),
                "score": r.get("score", 0),
            })
        insights.append({
            "query_id": q["id"],
            "question": q["question"],
            "tags": q["tags"],
            "hits": hits,
            "hit_count": len(results),
        })
    return insights


def write_insights_markdown(
    insights: list[dict],
    orphans: list[dict],
    stats: dict,
    output_path: Path,
) -> None:
    """Write the insights to a timestamped markdown file."""
    now = datetime.now(timezone.utc).isoformat()
    lines = [
        f"# SMA Cross-Connection Insights — {now[:10]}",
        "",
        f"**Generated**: {now}",
        f"**Engine**: `cross_connection_engine.py`",
        f"**Platform stats**: {stats.get('targets', '?')} targets, "
        f"{stats.get('drugs', '?')} drugs, {stats.get('trials', '?')} trials, "
        f"{stats.get('claims', '?')} claims",
        "",
        "## What this is",
        "",
        "Automated cross-campaign analysis that surfaces connections between findings, "
        "compounds, and hypotheses across our 9 SMA research campaigns. Goal: find "
        "publishable hypotheses that exist in our data but have never been explicitly stated.",
        "",
        "---",
        "",
    ]

    # Cross-query insights
    for ins in insights:
        lines.append(f"## Query: {ins['query_id']}")
        lines.append("")
        lines.append(f"**Question**: {ins['question']}")
        lines.append("")
        lines.append(f"**Tags**: {', '.join(ins['tags'])}")
        lines.append(f"**Hits**: {ins['hit_count']}")
        lines.append("")
        if ins["hits"]:
            lines.append("**Top results:**")
            lines.append("")
            for i, h in enumerate(ins["hits"], 1):
                lines.append(f"{i}. [{h['node_type']}] {h['title']}")
            lines.append("")
        lines.append("---")
        lines.append("")

    # Orphan trajectories section
    lines.append("## Orphan MD Trajectories (analysis gap)")
    lines.append("")
    if orphans:
        lines.append("The following MD trajectories exist but have no associated MMPBSA, "
                     "contact map, or other analysis file. These represent **free science** — "
                     "compute already paid for, insights not yet extracted.")
        lines.append("")
        lines.append("| Trajectory | Parent | Size (MB) |")
        lines.append("|---|---|---|")
        for o in orphans[:20]:
            name = Path(o["path"]).name
            lines.append(f"| {name} | {o['parent']} | {o['size_mb']:.1f} |")
    else:
        lines.append("_No orphan trajectories found — every .dcd has analysis output._")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Next steps
    lines.append("## Suggested Next Steps")
    lines.append("")
    lines.append("1. **Review top hit per query** — does it suggest a novel combination or experiment?")
    lines.append("2. **Analyze orphan trajectories** — cheap wins, just run MMPBSA + contact maps locally.")
    lines.append("3. **Update PROJECT_CATALOG.md** — add any new cross-references to the relevant "
                 "campaign sections.")
    lines.append("4. **Propose wet-lab experiments** — if a query surfaces a novel hypothesis, "
                 "draft a protocol for Simon.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## License")
    lines.append("")
    lines.append("CC-BY-4.0 — open analysis. Auto-generated by cross_connection_engine.py.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote insights to {output_path}")


# ============================================================================
# Main
# ============================================================================

def main() -> int:
    dry_run = "--dry-run" in sys.argv
    publish = "--publish" in sys.argv

    print("=" * 60)
    print("SMA Cross-Connection Engine")
    print(f"Dry run: {dry_run}, Publish: {publish}")
    print("=" * 60)

    print("\n[1/5] Loading PROJECT_CATALOG.md sections...")
    sections = load_catalog_sections()
    print(f"  Loaded {len(sections)} campaign sections: {list(sections.keys())}")

    print("\n[2/5] Loading all findings...")
    findings = load_all_findings()
    print(f"  Loaded {len(findings)} findings from {FINDINGS_DIR}")

    print("\n[3/5] Ingesting findings into CORTEX...")
    ingested = ingest_findings_to_cortex(findings, dry_run=dry_run)
    print(f"  Ingested {ingested} findings")

    print("\n[4/5] Running cross-campaign queries...")
    insights = run_cross_queries()
    print(f"  Got {len(insights)} insight query results")

    print("\n  Scanning for orphan trajectories...")
    orphans = find_orphan_trajectories()
    print(f"  Found {len(orphans)} orphan .dcd files")

    print("\n[5/5] Loading platform stats and writing output...")
    stats = load_platform_stats()

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_path = INSIGHTS_DIR / f"{date_str}_cross_connections.md"
    write_insights_markdown(insights, orphans, stats, output_path)

    if publish and not dry_run:
        print("\n  Publishing insight summary to CORTEX...")
        summary = f"Cross-connection sweep {date_str}: {len(insights)} queries, {len(orphans)} orphan trajectories"
        cortex_learn(
            context=output_path.read_text(encoding="utf-8")[:4000],
            description=summary,
            category="insight",
        )

    print("\n" + "=" * 60)
    print("DONE")
    print(f"Insights: {output_path}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
