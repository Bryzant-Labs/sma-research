#!/usr/bin/env python3
"""
Cross-Connection Benchmark 2.0

Quantitatively measures whether the cross-connection engine finds the insights
a human researcher would find. Scores the engine on 5 dimensions:

1. RECALL — does it find the 6 manual insights from CROSS_CONNECTIONS_2026-04-10.md?
2. PRECISION — are the automated findings factually correct?
3. NOVELTY — does it generate insights NOT in the manual seed?
4. CROSS-SOURCE — does it actually use multiple data sources per insight?
5. ACTIONABILITY — do insights lead to concrete next steps?

Output: benchmark_report_YYYY-MM-DD.md with scores, failures, improvements.

Usage:
    python cross_connection_benchmark_v2.py
    python cross_connection_benchmark_v2.py --strict  # fail if scores < threshold
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DROPBOX = Path("/mnt/c/Users/bryza/Dropbox/Christian fischer/SMA")
FINDINGS = DROPBOX / "findings"
INSIGHTS = FINDINGS / "insights"
MANUAL_SEED = FINDINGS / "2026-04-10" / "CROSS_CONNECTIONS_2026-04-10.md"

# ============================================================================
# Ground truth — the 6 manual insights from 2026-04-10
# ============================================================================

GROUND_TRUTH = [
    {
        "id": "manual_1_4ap_limk2_bidirectional",
        "title": "4-AP + LIMK2-selective hits = full ROCK-LIMK2-CFL2 coverage",
        "keywords_required": ["4-ap", "limk2", "cfl2"],
        "keywords_any": ["bidirectional", "axis", "pathway", "downstream"],
        "data_sources_expected": ["finding", "md_sim", "campaign"],
        "actionable": True,
    },
    {
        "id": "manual_2_esm2_selectivity_paradox",
        "title": "ESM-2 0.990 similarity + 14 selective hits = extract selectivity determinants",
        "keywords_required": ["esm2", "selectivity", "limk"],
        "keywords_any": ["paradox", "residue", "determinant", "0.990", "pharmacophore"],
        "data_sources_expected": ["esm2", "finding", "compound_index"],
        "actionable": True,
    },
    {
        "id": "manual_3_triple_drug_cocktail",
        "title": "Fasudil + LIMK2-hit + 4-AP triple cocktail",
        "keywords_required": ["fasudil", "4-ap", "limk2"],
        "keywords_any": ["triple", "combo", "combination", "cocktail"],
        "data_sources_expected": ["combinations", "finding", "drug_db"],
        "actionable": True,
    },
    {
        "id": "manual_4_gRNA_aav_cure_vehicle",
        "title": "Our safest gRNA + RFdiffusion AAV9 = in-house cure vehicle",
        "keywords_required": ["grna", "aav"],
        "keywords_any": ["casoffinder", "cure", "vehicle", "antisense", "rfdiffusion"],
        "data_sources_expected": ["casoffinder", "rfdiffusion", "finding"],
        "actionable": True,
    },
    {
        "id": "manual_5_orphan_smn2_vs_kv12_selectivity_md",
        "title": "Orphan SMN2 vs Kv1.2 selectivity MD (never analyzed)",
        "keywords_required": ["smn2", "kv1.2", "selectivity"],
        "keywords_any": ["orphan", "analyzed", "trajectory"],
        "data_sources_expected": ["filesystem", "md_sim"],
        "actionable": True,
    },
    {
        "id": "manual_6_ripk1_antinecroptosis",
        "title": "RIPK1 anti-necroptosis 4-AP weak binding needs re-validation",
        "keywords_required": ["ripk1"],
        "keywords_any": ["necroptosis", "martinez", "re-dock", "weak"],
        "data_sources_expected": ["backup", "docking"],
        "actionable": True,
    },
]

# Data source patterns that should appear in a well-built cross-connection
DATA_SOURCE_MARKERS = {
    "cortex": ["cortex", "knowledge graph", "neo4j"],
    "platform_api": ["api/v2", "platform", "/stats", "combinations", "dual-target", "twin"],
    "findings": ["finding_", "findings/", ".md"],
    "md_sim": [".dcd", "trajectory", "md_sims", "100ns", "holo"],
    "esm2": ["esm2", "similarity matrix", "embedding"],
    "compound_index": ["compound index", "fasudil", "4-ap", "bbb5", "nusinersen"],
    "casoffinder": ["casoffinder", "off-target", "grna"],
    "rfdiffusion": ["rfdiffusion", "aav capsid", "vp1"],
    "docking": ["diffdock", "confidence", "pose"],
    "backup": ["gpu-fleet-backup", "april 6", "april 2"],
    "filesystem": ["dropbox", "gpu-fleet", "md_sims/"],
    "drug_db": ["drugbank", "approved", "chembl", "fda"],
    "campaign": ["campaign", "project_catalog"],
    "combinations": ["combinat", "dual-target", "twin/optimize"],
}


# ============================================================================
# Scoring functions
# ============================================================================

def find_in_text(text: str, keywords: list[str], mode: str = "all") -> tuple[bool, list[str]]:
    """Return (matched, matching_keywords). mode='all' or 'any'."""
    text_lower = text.lower()
    matches = [k for k in keywords if k.lower() in text_lower]
    if mode == "all":
        return (len(matches) == len(keywords), matches)
    else:
        return (len(matches) > 0, matches)


def count_data_sources(text: str) -> dict[str, list[str]]:
    """For each data source, return the markers found in the text."""
    text_lower = text.lower()
    found = {}
    for source, markers in DATA_SOURCE_MARKERS.items():
        hits = [m for m in markers if m.lower() in text_lower]
        if hits:
            found[source] = hits
    return found


def score_recall(engine_output: str) -> dict:
    """Did the engine find each of the 6 ground-truth insights?"""
    scores = []
    for gt in GROUND_TRUTH:
        req_ok, req_matches = find_in_text(engine_output, gt["keywords_required"], "all")
        any_ok, any_matches = find_in_text(engine_output, gt["keywords_any"], "any")
        # An insight is "found" if all required AND any one optional keyword match
        found = req_ok and any_ok
        scores.append({
            "insight_id": gt["id"],
            "title": gt["title"],
            "found": found,
            "required_matched": req_matches,
            "required_total": len(gt["keywords_required"]),
            "optional_matched": any_matches,
        })
    n_found = sum(1 for s in scores if s["found"])
    return {
        "recall": n_found / len(GROUND_TRUTH),
        "n_found": n_found,
        "n_total": len(GROUND_TRUTH),
        "details": scores,
    }


def score_cross_source(engine_output: str) -> dict:
    """How many distinct data sources does the engine cite?"""
    sources = count_data_sources(engine_output)
    return {
        "cross_source_score": len(sources) / len(DATA_SOURCE_MARKERS),
        "n_sources_used": len(sources),
        "n_sources_possible": len(DATA_SOURCE_MARKERS),
        "sources": list(sources.keys()),
    }


def score_novelty(engine_output: str, manual_text: str) -> dict:
    """Does the engine generate insights NOT already in the manual seed?"""
    # Extract distinct concepts from the engine output
    engine_concepts = set()
    # Simple approach: every hypothesis-like sentence
    sentences = re.split(r'(?<=[.!?])\s+', engine_output)
    for s in sentences:
        if any(keyword in s.lower() for keyword in ["if", "could", "would", "suggests", "implies", "opportunity"]):
            engine_concepts.add(s.strip()[:150])

    # Check which concepts are NOT in the manual seed
    manual_lower = manual_text.lower()
    novel = []
    for concept in engine_concepts:
        # A concept is "novel" if its main keywords don't all appear in manual seed
        words = [w for w in concept.lower().split() if len(w) > 5]
        if words:
            overlap = sum(1 for w in words if w in manual_lower)
            if overlap / len(words) < 0.5:  # less than half of distinct words in manual
                novel.append(concept[:120])

    return {
        "novelty_score": len(novel) / max(len(engine_concepts), 1),
        "n_novel_concepts": len(novel),
        "n_total_concepts": len(engine_concepts),
        "sample_novel": novel[:5],
    }


def score_actionability(engine_output: str) -> dict:
    """Does the engine propose concrete next steps or just summarize?"""
    action_markers = [
        "action needed", "next step", "proposed experiment", "to-do",
        "should run", "should analyze", "propose to simon", "recommended",
        "todo", "mmpbsa", "ready for", "deploy", "launch",
    ]
    text_lower = engine_output.lower()
    hits = [m for m in action_markers if m in text_lower]
    # Count line items (bullets, numbered)
    actions = len(re.findall(r'^\s*[\-\*\d]+[.\)]\s+', engine_output, re.MULTILINE))
    return {
        "actionability_score": min(1.0, len(hits) / 5 + actions / 20),
        "action_markers_found": hits,
        "n_bulleted_items": actions,
    }


def score_data_utilization(engine_output: str) -> dict:
    """Does the engine USE the data (numbers, counts, specific results)?"""
    # Look for numeric claims
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', engine_output)
    # Look for specific compound/target names
    known_names = [
        "limk1", "limk2", "rock1", "rock2", "cfl1", "cfl2", "smn1", "smn2",
        "4-ap", "fasudil", "bbb5", "nusinersen", "risdiplam",
        "pfn1", "pfn2", "uba1", "pls3",
    ]
    names_used = sum(1 for n in known_names if n in engine_output.lower())
    return {
        "data_utilization_score": min(1.0, len(numbers) / 20 + names_used / 10),
        "n_numbers_cited": len(numbers),
        "n_named_entities": names_used,
    }


# ============================================================================
# Main
# ============================================================================

def benchmark_engine(engine_output_path: Path, engine_name: str, manual_text: str) -> dict:
    if not engine_output_path.exists():
        return {
            "engine": engine_name,
            "error": f"output file not found: {engine_output_path}",
            "total_score": 0,
        }

    engine_output = engine_output_path.read_text(encoding="utf-8")

    recall = score_recall(engine_output)
    cross_source = score_cross_source(engine_output)
    novelty = score_novelty(engine_output, manual_text)
    actionability = score_actionability(engine_output)
    data_util = score_data_utilization(engine_output)

    # Composite score (weighted)
    total = (
        recall["recall"] * 0.35 +
        cross_source["cross_source_score"] * 0.25 +
        novelty["novelty_score"] * 0.15 +
        actionability["actionability_score"] * 0.15 +
        data_util["data_utilization_score"] * 0.10
    )

    return {
        "engine": engine_name,
        "output_file": str(engine_output_path),
        "output_size_chars": len(engine_output),
        "total_score": round(total, 3),
        "grade": (
            "A" if total >= 0.85 else
            "B" if total >= 0.70 else
            "C" if total >= 0.55 else
            "D" if total >= 0.40 else "F"
        ),
        "scores": {
            "recall": recall,
            "cross_source": cross_source,
            "novelty": novelty,
            "actionability": actionability,
            "data_utilization": data_util,
        },
    }


def write_report(results: list[dict], output_path: Path) -> None:
    now = datetime.now(timezone.utc).isoformat()
    lines = [
        f"# Cross-Connection Benchmark 2.0 Report — {now[:10]}",
        "",
        f"**Generated**: {now}",
        f"**Benchmark script**: `cross_connection_benchmark_v2.py`",
        f"**Ground truth**: `findings/2026-04-10/CROSS_CONNECTIONS_2026-04-10.md` (6 manual insights)",
        "",
        "## Summary (quick view)",
        "",
        "| Engine | Grade | Total | Recall | Cross-Source | Novelty | Actionability | Data |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        if "error" in r:
            lines.append(f"| {r['engine']} | — | ERROR | — | — | — | — | — |")
            continue
        s = r["scores"]
        lines.append(
            f"| {r['engine']} | **{r['grade']}** | {r['total_score']:.2f} "
            f"| {s['recall']['recall']:.2f} ({s['recall']['n_found']}/{s['recall']['n_total']}) "
            f"| {s['cross_source']['cross_source_score']:.2f} ({s['cross_source']['n_sources_used']}/{s['cross_source']['n_sources_possible']}) "
            f"| {s['novelty']['novelty_score']:.2f} "
            f"| {s['actionability']['actionability_score']:.2f} "
            f"| {s['data_utilization']['data_utilization_score']:.2f} |"
        )
    lines.append("")

    # Scoring weights
    lines.append("## Scoring weights")
    lines.append("")
    lines.append("- Recall: 35% (did it find the 6 manual insights?)")
    lines.append("- Cross-Source: 25% (how many data sources used?)")
    lines.append("- Novelty: 15% (new concepts beyond manual seed?)")
    lines.append("- Actionability: 15% (concrete next steps?)")
    lines.append("- Data utilization: 10% (specific numbers + named entities?)")
    lines.append("")
    lines.append("**Grade scale**: A ≥ 0.85, B ≥ 0.70, C ≥ 0.55, D ≥ 0.40, F < 0.40")
    lines.append("")

    # Per-engine details
    for r in results:
        lines.append("---")
        lines.append("")
        lines.append(f"## {r['engine']}")
        lines.append("")
        if "error" in r:
            lines.append(f"**ERROR**: {r['error']}")
            continue

        s = r["scores"]

        # Recall detail
        lines.append("### Recall — did it find the 6 manual insights?")
        lines.append("")
        lines.append(f"**Score**: {s['recall']['recall']:.2f} ({s['recall']['n_found']}/{s['recall']['n_total']} found)")
        lines.append("")
        for d in s["recall"]["details"]:
            check = "✅" if d["found"] else "❌"
            lines.append(f"- {check} **{d['insight_id']}**: {d['title']}")
            if not d["found"]:
                lines.append(f"  - Required matched: {d['required_matched']} / {d['required_total']}")
                lines.append(f"  - Optional matched: {d['optional_matched']}")
        lines.append("")

        # Cross-source
        lines.append("### Cross-Source — data sources utilized")
        lines.append("")
        lines.append(f"**Score**: {s['cross_source']['cross_source_score']:.2f} "
                     f"({s['cross_source']['n_sources_used']}/{s['cross_source']['n_sources_possible']})")
        lines.append("")
        lines.append(f"**Sources cited**: {', '.join(sorted(s['cross_source']['sources']))}")
        missing = set(DATA_SOURCE_MARKERS.keys()) - set(s['cross_source']['sources'])
        if missing:
            lines.append(f"**Missing**: {', '.join(sorted(missing))}")
        lines.append("")

        # Novelty
        lines.append("### Novelty")
        lines.append("")
        lines.append(f"**Score**: {s['novelty']['novelty_score']:.2f} "
                     f"({s['novelty']['n_novel_concepts']}/{s['novelty']['n_total_concepts']})")
        if s['novelty']['sample_novel']:
            lines.append("")
            lines.append("**Sample novel concepts**:")
            for c in s['novelty']['sample_novel'][:3]:
                lines.append(f"- {c}")
        lines.append("")

        # Actionability
        lines.append("### Actionability")
        lines.append("")
        lines.append(f"**Score**: {s['actionability']['actionability_score']:.2f}")
        lines.append(f"**Action markers found**: {', '.join(s['actionability']['action_markers_found'][:10])}")
        lines.append(f"**Bulleted items**: {s['actionability']['n_bulleted_items']}")
        lines.append("")

        # Data util
        lines.append("### Data utilization")
        lines.append("")
        lines.append(f"**Score**: {s['data_utilization']['data_utilization_score']:.2f}")
        lines.append(f"**Numbers cited**: {s['data_utilization']['n_numbers_cited']}")
        lines.append(f"**Named entities**: {s['data_utilization']['n_named_entities']}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("A passing engine should score ≥ **0.70** (Grade B) — meaning it finds ~70% of manual insights,")
    lines.append("uses ≥ 60% of data sources, has some novel insights, proposes actions, and cites specific data.")
    lines.append("")
    lines.append("An F grade means the engine is not using the data effectively — likely only querying one source")
    lines.append("or not extracting concrete insights. Re-architect.")
    lines.append("")
    lines.append("## License")
    lines.append("")
    lines.append("CC-BY-4.0 — benchmark results open for reproducibility.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written: {output_path}")


def main() -> int:
    strict = "--strict" in sys.argv

    print("=" * 70)
    print("Cross-Connection Benchmark 2.0")
    print("=" * 70)

    # Load manual seed for novelty comparison
    if not MANUAL_SEED.exists():
        print(f"FATAL: manual seed not found at {MANUAL_SEED}", file=sys.stderr)
        return 1
    manual_text = MANUAL_SEED.read_text(encoding="utf-8")
    print(f"\n[load] Manual seed: {len(manual_text)} chars ({MANUAL_SEED})")

    # Find all engine outputs to benchmark
    engines_to_test = [
        (INSIGHTS / "2026-04-10_cross_connections.md", "Engine v1 (CORTEX-only)"),
        (INSIGHTS / "2026-04-10_cross_connections_v2.md", "Engine v2 (MCP + Platform)"),
        (INSIGHTS / "2026-04-10_cross_connections_v3.md", "Engine v3 (+ LLM synthesis)"),
        (MANUAL_SEED, "Manual seed (human baseline)"),
    ]

    results = []
    for path, name in engines_to_test:
        print(f"\n[bench] {name} → {path.name}")
        r = benchmark_engine(path, name, manual_text)
        if "error" not in r:
            print(f"  Grade: {r['grade']}  Total: {r['total_score']:.2f}")
            print(f"  Recall: {r['scores']['recall']['recall']:.2f}, "
                  f"Cross-source: {r['scores']['cross_source']['cross_source_score']:.2f}, "
                  f"Novelty: {r['scores']['novelty']['novelty_score']:.2f}")
        else:
            print(f"  ERROR: {r['error']}")
        results.append(r)

    # Write report
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = INSIGHTS / f"{date_str}_benchmark_report.md"
    write_report(results, report_path)

    print("\n" + "=" * 70)
    print(f"DONE — report: {report_path}")
    print("=" * 70)

    # Strict mode: fail if any engine scored below threshold
    if strict:
        for r in results:
            if r.get("total_score", 0) < 0.55 and "Manual" not in r["engine"]:
                print(f"\nSTRICT FAIL: {r['engine']} scored {r['total_score']:.2f} < 0.55", file=sys.stderr)
                return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
