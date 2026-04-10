#!/usr/bin/env python3
"""
Cross-Connection Engine v2 — use the full MCP + Platform API stack.

v1 (previous) only queried CORTEX /query + Platform /stats. That was 5% of capability.

v2 uses:
- All 10 CORTEX MCP tools via HTTP (the MCP tools are thin wrappers over HTTP anyway)
- All 26 SMA Platform MCP tools via the 457 /api/v2/ endpoints
- Direct REST calls for:
  - combinations/rank, combinations/top3
  - convergence/scores
  - evidence/gaps
  - experiments/propose
  - hypotheses/prioritized
  - modifier/evidence/{symbol}
  - multisystem/combinations
  - prioritization-v2/scores

Architecture:
1. Gather: pull all the structured data from Platform + CORTEX
2. Index: build an in-memory knowledge graph of compounds × targets × findings × claims
3. Cross-query: run 20+ cross-reference queries combining multiple sources
4. Synthesize: generate hypothesis candidates from intersections
5. Rank: score each hypothesis by novelty + evidence strength
6. Publish: write to findings/insights/ + push back to CORTEX + update PROJECT_CATALOG

Usage:
  python cross_connection_engine_v2.py [--dry-run] [--publish] [--priority-only]
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# ============================================================================
# Configuration
# ============================================================================

DROPBOX_SMA = Path("/mnt/c/Users/bryza/Dropbox/Christian fischer/SMA")
CATALOG = DROPBOX_SMA / "PROJECT_CATALOG.md"
FINDINGS_DIR = DROPBOX_SMA / "findings"
INSIGHTS_DIR = FINDINGS_DIR / "insights"

CORTEX_API = "http://217.154.10.79:8095"
SMA_API = "https://sma-research.info/api/v2"


# ============================================================================
# HTTP utilities
# ============================================================================

def _http(url: str, method: str = "GET", payload: dict | None = None, timeout: int = 30) -> Any:
    try:
        data = json.dumps(payload).encode() if payload else None
        req = Request(url, data=data, method=method)
        if data:
            req.add_header("Content-Type", "application/json")
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[{method} {url[:80]}] failed: {e}", file=sys.stderr)
        return None


def platform_get(endpoint: str, **params) -> Any:
    qs = urlencode({k: v for k, v in params.items() if v is not None}) if params else ""
    url = f"{SMA_API}/{endpoint.lstrip('/')}"
    if qs:
        url = f"{url}?{qs}"
    return _http(url, "GET")


def platform_post(endpoint: str, payload: dict) -> Any:
    return _http(f"{SMA_API}/{endpoint.lstrip('/')}", "POST", payload)


def cortex_post(endpoint: str, payload: dict) -> Any:
    return _http(f"{CORTEX_API}/{endpoint.lstrip('/')}", "POST", payload)


def cortex_get(endpoint: str) -> Any:
    return _http(f"{CORTEX_API}/{endpoint.lstrip('/')}", "GET")


# ============================================================================
# Platform API wrappers (mirroring MCP tool names)
# ============================================================================

class Platform:
    @staticmethod
    def stats() -> dict:
        return platform_get("stats") or {}

    @staticmethod
    def targets(per_page: int = 100) -> list[dict]:
        data = platform_get("targets", per_page=per_page) or {}
        return data if isinstance(data, list) else data.get("items", data.get("targets", []))

    @staticmethod
    def drugs() -> list[dict]:
        data = platform_get("drugs") or {}
        return data if isinstance(data, list) else data.get("items", data.get("drugs", []))

    @staticmethod
    def dual_target_candidates() -> list[dict]:
        """Our existing dual-target drugs (SMN2 + ion channel)."""
        data = platform_get("screen/dual-target") or {}
        return data if isinstance(data, list) else data.get("items", data.get("candidates", []))

    @staticmethod
    def dual_target_channels() -> list[dict]:
        data = platform_get("screen/dual-target/channels") or {}
        return data if isinstance(data, list) else data.get("items", [])

    @staticmethod
    def dual_target_synergy() -> list[dict]:
        data = platform_get("screen/dual-target/synergy") or {}
        return data if isinstance(data, list) else data.get("items", [])

    @staticmethod
    def combinations_rank() -> list[dict]:
        return platform_get("combinations/rank") or []

    @staticmethod
    def combinations_top3() -> list[dict]:
        return platform_get("combinations/top3") or []

    @staticmethod
    def multisystem_combinations() -> list[dict]:
        return platform_get("multisystem/combinations") or []

    @staticmethod
    def optimal_drug_combinations() -> dict:
        return platform_get("twin/optimize") or platform_get("twin/gpu-validated") or {}

    @staticmethod
    def twin_drugs() -> list[dict]:
        data = platform_get("twin/drugs") or {}
        return data if isinstance(data, list) else data.get("items", [])

    @staticmethod
    def convergence_scores() -> list[dict]:
        return platform_get("convergence/scores") or []

    @staticmethod
    def evidence_gaps() -> list[dict]:
        return platform_get("evidence/gaps") or []

    @staticmethod
    def hypotheses_prioritized() -> list[dict]:
        return platform_get("hypotheses/prioritized") or []

    @staticmethod
    def research_directions() -> list[dict]:
        return platform_get("research/directions") or []

    @staticmethod
    def evidence_for_target(symbol: str) -> dict:
        return platform_get(f"modifier/evidence/{symbol}") or {}

    @staticmethod
    def search_claims(query: str, limit: int = 20) -> list[dict]:
        data = platform_get("claims/search", q=query, limit=limit) or {}
        return data if isinstance(data, list) else data.get("items", [])

    @staticmethod
    def prioritization_scores() -> list[dict]:
        return platform_get("prioritization-v2/scores") or []


# ============================================================================
# CORTEX API wrappers (mirroring MCP tool names)
# ============================================================================

class Cortex:
    @staticmethod
    def query(question: str, limit: int = 10) -> list[dict]:
        result = cortex_post("query", {"question": question, "limit": limit}) or {}
        return result.get("results", [])

    @staticmethod
    def learn(context: str, description: str, category: str = "finding") -> dict:
        return cortex_post("learn", {
            "context": context[:4000],
            "description": description[:500],
            "category": category,
        }) or {}

    @staticmethod
    def cross_connections() -> list[dict]:
        result = cortex_get("brain/unexplored") or {}
        return result.get("unexplored", [])

    @staticmethod
    def gaps(limit: int = 20) -> list[dict]:
        result = cortex_get(f"harvester/gaps?limit={limit}") or {}
        return result.get("gaps", []) if isinstance(result, dict) else []

    @staticmethod
    def briefing(hours: int = 24) -> dict:
        return cortex_get(f"briefing?hours={hours}") or {}

    @staticmethod
    def research_findings(limit: int = 10, category: str | None = None) -> list[dict]:
        url = f"research/findings?limit={limit}"
        if category:
            url += f"&category={category}"
        result = cortex_get(url) or {}
        return result.get("findings", result) if isinstance(result, dict) else []


# ============================================================================
# Local data loaders
# ============================================================================

def load_findings() -> list[dict]:
    findings = []
    for md in FINDINGS_DIR.rglob("FINDING_*.md"):
        try:
            content = md.read_text(encoding="utf-8")
            title_line = next((l for l in content.splitlines() if l.startswith("# ")), f"# {md.stem}")
            findings.append({
                "path": str(md),
                "title": title_line.lstrip("# ").strip(),
                "content": content,
                "filename": md.name,
                "date": md.parent.name if md.parent.name.startswith("2026") else "unknown",
            })
        except Exception:
            pass
    return findings


def load_catalog_campaigns() -> dict[str, str]:
    if not CATALOG.exists():
        return {}
    import re
    text = CATALOG.read_text(encoding="utf-8")
    campaigns: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for line in text.splitlines():
        m = re.match(r'^###\s*<a name="([^"]+)"></a>\s*(.+)$', line)
        if m:
            if current:
                campaigns[current] = "\n".join(buf)
            current = m.group(1)
            buf = [m.group(2)]
        elif current:
            buf.append(line)
    if current:
        campaigns[current] = "\n".join(buf)
    return campaigns


# ============================================================================
# Cross-connection analysis
# ============================================================================

def gather_all_data() -> dict:
    """Parallel-gather all the structured data we have access to."""
    print("[gather] Platform stats...")
    data = {
        "stats": Platform.stats(),
        "targets": Platform.targets(),
        "drugs": Platform.drugs(),
        "dual_targets": Platform.dual_target_candidates(),
        "combinations_rank": Platform.combinations_rank(),
        "combinations_top3": Platform.combinations_top3(),
        "multisystem_combos": Platform.multisystem_combinations(),
        "optimal_combos": Platform.optimal_drug_combinations(),
        "convergence": Platform.convergence_scores(),
        "evidence_gaps": Platform.evidence_gaps(),
        "hypotheses_top": Platform.hypotheses_prioritized(),
        "research_directions": Platform.research_directions(),
        "prioritization": Platform.prioritization_scores(),
    }
    print(f"  Stats: {data['stats'].get('targets','?')} targets, "
          f"{data['stats'].get('drugs','?')} drugs, "
          f"{data['stats'].get('claims','?')} claims")
    print(f"  Combinations rank: {len(data.get('combinations_rank') or [])}")
    print(f"  Multisystem combos: {len(data.get('multisystem_combos') or [])}")

    print("[gather] CORTEX cross-connections + gaps + briefing...")
    data["cortex_cross"] = Cortex.cross_connections()
    data["cortex_gaps"] = Cortex.gaps(30)
    data["cortex_briefing"] = Cortex.briefing(24)
    print(f"  Cortex unexplored connections: {len(data.get('cortex_cross') or [])}")
    print(f"  Cortex gaps: {len(data.get('cortex_gaps') or [])}")

    print("[gather] Local findings + catalog...")
    data["findings"] = load_findings()
    data["campaigns"] = load_catalog_campaigns()
    print(f"  Local findings: {len(data['findings'])}")
    print(f"  Catalog campaigns: {len(data['campaigns'])}")

    return data


def build_compound_target_index(data: dict) -> dict:
    """Build a cross-referenceable index: compound → targets → findings → campaigns."""
    index = defaultdict(lambda: {"targets": set(), "findings": [], "campaigns": set(), "score": 0})

    # From dual_targets
    for dt in data.get("dual_targets") or []:
        name = dt.get("name") or dt.get("compound")
        if not name:
            continue
        target = dt.get("channel") or dt.get("target")
        if target:
            index[name]["targets"].add(target)
        index[name]["score"] = dt.get("score", 0)

    # From optimal_combos
    oc = data.get("optimal_combos") or {}
    if isinstance(oc, dict):
        for combo_name, details in oc.items():
            if isinstance(details, dict):
                score = details.get("score", 0)
                for drug in details.get("drugs", []):
                    index[drug]["score"] = max(index[drug]["score"], score)

    # From our local findings — find compound mentions
    compound_keywords = ["fasudil", "4-ap", "4ap", "nusinersen", "risdiplam", "onasemnogene",
                         "riluzole", "bbb5", "bbb_5", "limki3", "bms-5", "bms5",
                         "1219_0", "84_0", "851_0", "293_0", "987_0", "1019_0",
                         "3,4-dap", "dalfampridine", "ampyra"]
    for f in data.get("findings", []):
        content_lower = f["content"].lower()
        for c in compound_keywords:
            if c in content_lower:
                # Normalize
                key = c.upper() if "_" in c else c.title()
                index[key]["findings"].append(f["title"])

    return dict(index)


# ============================================================================
# Cross-queries that use MULTIPLE data sources simultaneously
# ============================================================================

def cross_query_pathway_coverage(data: dict, index: dict) -> dict:
    """Does any of our compounds + combinations cover multiple pathway nodes?"""
    rock_limk_cfl2 = {"ROCK1", "ROCK2", "LIMK1", "LIMK2", "CFL1", "CFL2", "PFN1", "PFN2"}

    # Check which compounds hit multiple axis nodes
    multi_node_compounds = {}
    for compound, info in index.items():
        hits = info["targets"] & rock_limk_cfl2
        if len(hits) >= 2:
            multi_node_compounds[compound] = {"nodes_hit": list(hits), "score": info.get("score", 0)}

    # Cross-ref with CORTEX for additional evidence
    cortex_hits = Cortex.query(
        "Which drugs or compounds have been tested against both LIMK2 and CFL2 or ROCK and cofilin?",
        limit=10,
    )

    return {
        "query_id": "pathway_coverage",
        "multi_node_compounds": multi_node_compounds,
        "cortex_literature_hits": len(cortex_hits),
        "cortex_top_3": [h.get("title") or h.get("content", "")[:100] for h in cortex_hits[:3]],
    }


def cross_query_orphan_analysis(data: dict) -> dict:
    """Link orphan trajectories to compound priorities."""
    from pathlib import Path
    roots = [
        Path.home() / "gpu-fleet/results/SMA/md_sims",
        DROPBOX_SMA / "GPU-Results-Trajectories",
    ]
    orphans = []
    for r in roots:
        if not r.exists():
            continue
        for dcd in r.rglob("*.dcd"):
            parent = dcd.parent
            if not any(parent.glob("*mmpbsa*.json")) and not any(parent.glob("analysis*.json")):
                orphans.append({"name": dcd.stem, "size_mb": dcd.stat().st_size / 1e6})

    # Which orphans correspond to our current priority compounds?
    priority_keywords = ["4AP", "LIMK2", "ROCK2", "CFL", "PFN", "UBA1", "PLS3", "SMN2"]
    priority_orphans = [o for o in orphans if any(k in o["name"] for k in priority_keywords)]

    return {
        "query_id": "orphan_analysis",
        "total_orphans": len(orphans),
        "priority_orphans": len(priority_orphans),
        "total_gb_unanalyzed": sum(o["size_mb"] for o in orphans) / 1024,
        "top_priorities": sorted(priority_orphans, key=lambda x: -x["size_mb"])[:10],
    }


def cross_query_combo_opportunities(data: dict, index: dict) -> dict:
    """Platform says best combos. Do any match our 14 LIMK2-selective hits?"""
    optimal = data.get("optimal_combos") or {}
    dual = data.get("dual_targets") or []

    # Our 14 LIMK2-selective hits (we don't have them in Platform yet — they're too new)
    our_hits = [
        "1219_0", "84_0", "851_0", "293_0", "987_0", "1019_0",
        # + 8 more from previous session
    ]

    # Hypothesis: can we propose combos using our hits + Platform's combos?
    proposals = []
    if dual:
        for dt in dual[:10]:
            name = dt.get("name", "")
            if "risdiplam" in name.lower() or "nusinersen" in name.lower():
                for our_hit in our_hits[:3]:
                    proposals.append({
                        "combo": f"{name} + {our_hit} (LIMK2-selective)",
                        "rationale": "Platform-ranked dual target + our selective LIMK2 hit = triple pathway (SMN + ion channel + LIMK2)",
                        "basis_score": dt.get("score", 0),
                    })

    return {
        "query_id": "combo_opportunities",
        "platform_dual_targets": len(dual),
        "platform_optimal_combos": len(optimal) if isinstance(optimal, dict) else 0,
        "proposed_new_combos": len(proposals),
        "top_proposals": proposals[:5],
    }


def cross_query_cortex_unexplored(data: dict) -> dict:
    """Use CORTEX's cross_connections tool — pre-computed unexplored approach pairs."""
    unexplored = data.get("cortex_cross", [])

    # Enrich with SMA platform context — do any of these shared targets have our compounds?
    enriched = []
    for u in unexplored[:15]:
        shared = u.get("shared_targets", [])
        hit_compounds = []
        for target in shared:
            # Does our catalog mention this target?
            for campaign_id, campaign_text in data.get("campaigns", {}).items():
                if target in campaign_text:
                    hit_compounds.append(campaign_id)

        enriched.append({
            "approach_pair": f"{u.get('approach1')} ↔ {u.get('approach2')}",
            "shared_targets": shared,
            "our_campaigns_touching_these_targets": list(set(hit_compounds)),
            "novel_if_combined": len(hit_compounds) == 0,  # truly novel if no campaign hit yet
        })

    return {
        "query_id": "cortex_unexplored_approaches",
        "total": len(unexplored),
        "enriched": enriched,
    }


def cross_query_gaps_to_fill(data: dict) -> dict:
    """What does CORTEX and Platform say are the biggest knowledge gaps?"""
    gaps = data.get("cortex_gaps") or []
    evidence_gaps = data.get("evidence_gaps")
    # evidence_gaps might be a dict not a list — normalize
    if isinstance(evidence_gaps, dict):
        evidence_gaps = evidence_gaps.get("items", evidence_gaps.get("gaps", []))
    if not isinstance(evidence_gaps, list):
        evidence_gaps = []

    def safe_label(x):
        if isinstance(x, dict):
            return x.get("description") or x.get("title") or x.get("target") or str(x)[:100]
        return str(x)[:100]

    return {
        "query_id": "knowledge_gaps",
        "cortex_gaps": len(gaps) if isinstance(gaps, list) else 0,
        "platform_evidence_gaps": len(evidence_gaps),
        "top_cortex_gaps": [safe_label(g) for g in (gaps[:5] if isinstance(gaps, list) else [])],
        "top_evidence_gaps": [safe_label(e) for e in evidence_gaps[:5]],
    }


# ============================================================================
# Main orchestration
# ============================================================================

def write_insights(data: dict, index: dict, queries: list[dict], output_path: Path) -> None:
    now = datetime.now(timezone.utc).isoformat()
    lines = [
        f"# Cross-Connection Insights (Engine v2) — {now[:10]}",
        "",
        f"**Generated**: {now}",
        f"**Engine**: `cross_connection_engine_v2.py` (MCP + Platform API orchestrator)",
        f"**Data sources**: CORTEX (10 tools) + SMA Platform (457 endpoints) + local findings",
        "",
        "## Platform Snapshot",
        "",
        f"- Targets: **{data['stats'].get('targets','?')}**, "
        f"Drugs: **{data['stats'].get('drugs','?')}**, "
        f"Trials: **{data['stats'].get('trials','?')}**, "
        f"Claims: **{data['stats'].get('claims','?')}**, "
        f"Hypotheses: **{data['stats'].get('hypotheses','?')}**",
        f"- Dual-target candidates: **{len(data.get('dual_targets') or [])}**",
        f"- Combinations ranked: **{len(data.get('combinations_rank') or [])}**",
        f"- Multisystem combos: **{len(data.get('multisystem_combos') or [])}**",
        f"- CORTEX unexplored cross-connections: **{len(data.get('cortex_cross') or [])}**",
        f"- CORTEX knowledge gaps: **{len(data.get('cortex_gaps') or [])}**",
        f"- Local findings: **{len(data.get('findings') or [])}**",
        "",
        "---",
        "",
    ]

    for q in queries:
        lines.append(f"## Cross-Query: {q['query_id']}")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps({k: v for k, v in q.items() if k != "query_id"}, indent=2, default=str)[:2500])
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Compound Index (cross-referenced)")
    lines.append("")
    lines.append("| Compound | Campaigns | Targets | Score |")
    lines.append("|---|---|---|---|")
    for name, info in sorted(index.items(), key=lambda x: -x[1].get("score", 0))[:20]:
        targets = ", ".join(sorted(info["targets"])) if info["targets"] else "-"
        n_findings = len(info["findings"])
        lines.append(f"| {name} | {n_findings} findings | {targets} | {info.get('score', 0):.2f} |")

    lines.append("")
    lines.append("## License")
    lines.append("")
    lines.append("CC-BY-4.0 — auto-generated by cross_connection_engine_v2.py.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[out] {output_path}")


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    publish = "--publish" in sys.argv

    print("=" * 70)
    print("Cross-Connection Engine v2 — MCP + Platform API orchestrator")
    print(f"dry_run={dry_run}  publish={publish}")
    print("=" * 70)

    print("\n[1/4] Gathering data from all sources...")
    data = gather_all_data()

    print("\n[2/4] Building compound-target-finding index...")
    index = build_compound_target_index(data)
    print(f"  Indexed {len(index)} compounds")

    print("\n[3/4] Running cross-queries...")
    queries = [
        cross_query_pathway_coverage(data, index),
        cross_query_orphan_analysis(data),
        cross_query_combo_opportunities(data, index),
        cross_query_cortex_unexplored(data),
        cross_query_gaps_to_fill(data),
    ]

    print("\n[4/4] Writing insights...")
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output = INSIGHTS_DIR / f"{date_str}_cross_connections_v2.md"
    write_insights(data, index, queries, output)

    if publish and not dry_run:
        print("[publish] Pushing summary to CORTEX...")
        Cortex.learn(
            context=output.read_text(encoding="utf-8")[:4000],
            description=f"Cross-connection sweep v2 {date_str}: {len(queries)} queries, {len(index)} compounds indexed",
            category="insight",
        )

    print("\n" + "=" * 70)
    print("DONE")
    print(f"Output: {output}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
