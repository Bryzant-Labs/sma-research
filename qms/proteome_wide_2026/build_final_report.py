#!/usr/bin/env python3
"""Build the ATLAS_TOP25_CASCADE_RESULTS.md report after PXM + Boltz-2 complete.

Reads:
  - top100_<TARGET>.tsv  (Phase-4 filter cascade)
  - zscore_matrix_<TARGET>.csv   (Phase-5 Boltz-2 panel)
  - cross_target_top_hits.csv
  - cascade_summary.tsv
  - TITLE_AUDIT_extended.md (context)

Writes:
  - /home/bryza/sma-research/qms/ATLAS_TOP25_CASCADE_RESULTS.md
  - /home/bryza/sma-research/qms/ATLAS_TOP25_top3_per_target.tsv
  - /home/bryza/sma-research/qms/ATLAS_TOP25_cross_connections.md
"""
import csv
import json
from pathlib import Path
from datetime import datetime

QMS = Path("/home/bryza/sma-research/qms")
CASCADE = Path("/home/bryza/sma-research/qms/proteome_wide_2026/cascade_extended_output")
TITLE_AUDIT = Path("/home/bryza/sma-research/qms/proteome_wide_2026/TITLE_AUDIT_extended.md")

TARGETS = ["EP400", "PEAK1", "KAT7", "RNF213", "EHMT2", "KAT6A", "KAT5", "KMT5B", "EHMT1"]

# Cross-connection hints to existing 4-arm campaigns
CROSS_CONNECTIONS = {
    "KAT6A": [
        "MYST HAT family overlap with KAT6B (atlas rank 10, fired top5). Paralog selectivity opportunity.",
        "KAT6A inhibition → H3K14ac loss → chromatin compaction. SMA MNs show global transcriptional dysregulation (Cajal body loss). Possible rescue axis.",
    ],
    "KAT5": [
        "TIP60/KAT5 acetylates p53 K120 activating apoptosis. PERP (our arm-4 campaign) is downstream of p53. Synergy lead: KAT5 activator could amplify PERP-mediated MN rescue.",
        "TIP60 + TP53 + PERP = direct biological triangle. Check DiffDock vs PERP + KAT5 dual modulator.",
    ],
    "KAT7": [
        "HBO1/KAT7 H3K14ac at origins of replication. MN post-mitotic but may regulate SMN1/2 enhancer landscape.",
    ],
    "EHMT1": [
        "GLP/EHMT1 co-operates with EHMT2/G9a. If we hit EHMT1 we will likely hit EHMT2 (90% pocket identity). Cross-selectivity matters.",
        "H3K9me2 mark represses neurogenesis genes. SMA MN transcriptome has aberrant H3K9me2 patterns (Finkel 2020 data).",
    ],
    "EHMT2": [
        "G9a inhibitors (UNC0642, BIX-01294) exist — our PXM output should match scaffold space and add MN-specific selectivity.",
        "Cross-link: BRD4 + G9a PPI; if KAT6B bromodomain hits also hit G9a, dual mechanism.",
    ],
    "KMT5B": [
        "SUV420H1 H4K20me2/3 heterochromatin. SMA MN show loss of heterochromatin integrity (our LIMK2 axis).",
        "A-196 (pan-SUV420) exists; our PXM output should selectivity-differentiate KMT5B vs KMT5A/C.",
    ],
    "EP400": [
        "TIP60 complex ATPase — directly upstream of KAT5. Dual EP400/KAT5 targeting may synergize.",
        "SWI/SNF chromatin remodeler; loss-of-function in SMA likely via snRNP-chromatin coupling.",
    ],
    "RNF213": [
        "AAA+ ATPase E3 ubiquitin ligase. Novel target class; no direct SMA link yet but chromosomal fragility axis.",
    ],
    "PEAK1": [
        "Pseudokinase; no canonical catalysis. Scaffold function for SRC/FRK. Low druggability (0.024).",
        "Possibly connects to ROCK/LIMK axis via pseudokinase-SRC scaffold. Speculative.",
    ],
}


def load_title_audit_table():
    if not TITLE_AUDIT.exists():
        return ""
    return TITLE_AUDIT.read_text()


def load_top_compounds(target, n=3):
    """Get top-N compounds from top100 + their Boltz-2 Z-scores if available."""
    top_tsv = CASCADE / f"top100_{target}.tsv"
    if not top_tsv.exists():
        return []
    rows = []
    with open(top_tsv) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for i, row in enumerate(reader, 1):
            if i > n:
                break
            rows.append({"rank": i, **row})

    # Join with Boltz-2 matrix
    zscore_csv = CASCADE / f"zscore_matrix_{target}.csv"
    if zscore_csv.exists():
        zmap = {}
        with open(zscore_csv) as f:
            reader = csv.DictReader(f)
            for row in reader:
                zmap[row["compound_id"]] = row
        for r in rows:
            cid = f"{target}_cpd_{r['rank']}"
            if cid in zmap:
                zr = zmap[cid]
                r["z_primary"] = zr.get("z_primary", "") or ""
                r["sel_z"] = zr.get("selectivity_z", "") or ""
                r["iptm_primary"] = zr.get(f"iptm_{target}", "") or ""
    return rows


def build_cascade_summary():
    summ = CASCADE / "cascade_summary.tsv"
    if not summ.exists():
        return []
    rows = []
    with open(summ) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)
    return rows


def build_cross_target_hits():
    cth = CASCADE / "cross_target_top_hits.csv"
    if not cth.exists():
        return []
    rows = []
    with open(cth) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows[:20]


def main():
    out_md = QMS / "ATLAS_TOP25_CASCADE_RESULTS.md"
    top3_tsv = QMS / "ATLAS_TOP25_top3_per_target.tsv"
    cross_md = QMS / "ATLAS_TOP25_cross_connections.md"

    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # ---- build top3 TSV ----
    top3_rows = []
    for tgt in TARGETS:
        rows = load_top_compounds(tgt, n=3)
        for r in rows:
            top3_rows.append({
                "target": tgt,
                "rank": r["rank"],
                "smiles": r.get("smiles", ""),
                "cfd_pos": r.get("cfd_pos", ""),
                "qed": r.get("qed", ""),
                "mw": r.get("mw", ""),
                "logp": r.get("logp", ""),
                "tpsa": r.get("tpsa", ""),
                "bbb_score": r.get("bbb_score", ""),
                "iptm_primary": r.get("iptm_primary", ""),
                "z_primary": r.get("z_primary", ""),
                "selectivity_z": r.get("sel_z", ""),
            })
    if top3_rows:
        with open(top3_tsv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(top3_rows[0].keys()), delimiter="\t")
            w.writeheader()
            for row in top3_rows:
                w.writerow(row)

    # ---- build cross_connections ----
    with open(cross_md, "w") as f:
        f.write(f"# ATLAS TOP-25 Extended — Cross-Connection Analysis\n")
        f.write(f"**Date**: {now}\n\n")
        f.write("For each fired target, biological / mechanistic connections to our existing 4-arm "
                "campaigns (LIMK2-activator, SSH1-inhibitor, PERP-binder, NMJ atomic complex) "
                "and to other atlas targets.\n\n")
        for tgt in TARGETS:
            conns = CROSS_CONNECTIONS.get(tgt, ["(no cross-connection hints yet)"])
            f.write(f"## {tgt}\n")
            for c in conns:
                f.write(f"- {c}\n")
            f.write("\n")
        # Triangles
        f.write("## Cross-target biological triangles\n")
        f.write("- **TIP60 axis**: EP400 (ATPase) + KAT5 (HAT) + PERP (p53 downstream) — triple dual-modulator possibility.\n")
        f.write("- **MYST paralog cluster**: KAT5 + KAT6A + KAT7 (+ KAT6B from top5) — selectivity matrix.\n")
        f.write("- **H3K9 methylation axis**: EHMT1 + EHMT2 — obligate heterodimer; single compound likely hits both.\n")
        f.write("- **SET-domain cluster**: EHMT1 + EHMT2 + KMT5B — cross-reactivity risk; selectivity critical.\n")

    # ---- build main results MD ----
    summary_rows = build_cascade_summary()
    cth = build_cross_target_hits()

    with open(out_md, "w") as f:
        f.write(f"# SMA Novel Target Atlas — Extended (ranks 6-25) Cascade Results\n\n")
        f.write(f"**Date**: {now}\n")
        f.write(f"**Parent atlas**: `/home/bryza/sma-research/qms/SMA_NOVEL_TARGET_ATLAS_2026.md`\n")
        f.write(f"**TITLE audit**: `/home/bryza/sma-research/qms/proteome_wide_2026/TITLE_AUDIT_extended.md`\n")
        f.write(f"**Top-5 sibling campaign**: `/home/bryza/sma-research/qms/SMA_NOVEL_TARGET_ATLAS_TOP5_PXM_RESULTS.md`\n")
        f.write(f"**Cross-connections**: `/home/bryza/sma-research/qms/ATLAS_TOP25_cross_connections.md`\n")
        f.write(f"**Top-3 per target**: `/home/bryza/sma-research/qms/ATLAS_TOP25_top3_per_target.tsv`\n\n")
        f.write(f"**Status**: DRAFT — INTERNAL ONLY. Simon-Comms-Gate HELD.\n\n")

        f.write(f"## Target selection (20 → 9 fired)\n\n")
        f.write(f"Atlas ranks 6-25 (skipping top5 = PCIF1, BPTF, LARP1, SH3BP5, KAT6B already fired)\n")
        f.write(f"→ 20 candidates passing druggable_bucket ≥ 4, pubmed ≤ 10, mean_cosine ≥ 0.55\n")
        f.write(f"→ 11 skipped (no suitable PDB ≤ 2.5 Å OR fpocket druggability < 0.1):\n")
        f.write(f"  TEF, PI4KA, EIF4G1, MRPS31, RANBP2, USP34, BTF3, TIAM1, MYCBP2, OPTN, PIK3C2A\n")
        f.write(f"→ **9 targets fired**: EP400, PEAK1, KAT7, RNF213, EHMT2, KAT6A, KAT5, KMT5B, EHMT1\n\n")
        f.write(f"See TITLE_AUDIT_extended.md for per-target rationale.\n\n")

        f.write(f"## Per-target cascade statistics\n\n")
        f.write(f"| Target | PDB | total gen | valid | passed filters | top100 | top cfd_pos |\n")
        f.write(f"|--------|-----|-----------|-------|----------------|--------|-------------|\n")
        for tgt in TARGETS:
            r = next((r for r in summary_rows if r["target"] == tgt), None)
            if r:
                f.write(f"| {tgt} | {_pdb(tgt)} | {r.get('n_total', '?')} | "
                        f"{r.get('n_valid', '?')} | {r.get('n_filtered', '?')} | "
                        f"{r.get('n_top100', '?')} | {r.get('top_cfd_pos', '?')} |\n")
            else:
                f.write(f"| {tgt} | {_pdb(tgt)} | — | — | — | — | — |\n")
        f.write("\n")

        f.write(f"## Top-3 per target (Z-scored Boltz-2 selectivity)\n\n")
        f.write(f"Columns: target, rank, SMILES (truncated), QED, BBB, z_primary, selectivity_z\n\n")
        for tgt in TARGETS:
            f.write(f"### {tgt}\n\n")
            rows = load_top_compounds(tgt, n=3)
            if not rows:
                f.write("_No results (PXM not yet complete or filter cascade pending)._\n\n")
                continue
            f.write(f"| # | SMILES | QED | BBB | iptm_primary | z_primary | sel_z |\n")
            f.write(f"|---|--------|-----|-----|--------------|-----------|-------|\n")
            for r in rows:
                smi = r.get("smiles", "")
                if len(smi) > 55:
                    smi = smi[:52] + "..."
                f.write(f"| {r['rank']} | `{smi}` | "
                        f"{_fmt(r.get('qed', ''))} | {_fmt(r.get('bbb_score', ''))} | "
                        f"{_fmt(r.get('iptm_primary', ''))} | {_fmt(r.get('z_primary', ''))} | "
                        f"{_fmt(r.get('sel_z', ''))} |\n")
            f.write("\n")

        f.write(f"## Cross-target top hits (passing z_primary > 0 AND sel_z > 0)\n\n")
        if cth:
            f.write(f"| compound_id | primary | iptm_prim | z_prim | sel_z |\n")
            f.write(f"|-------------|---------|-----------|--------|-------|\n")
            for r in cth[:15]:
                pt = r.get("primary_target", "")
                f.write(f"| {r['compound_id']} | {pt} | "
                        f"{_fmt(r.get(f'iptm_{pt}', ''))} | "
                        f"{_fmt(r.get('z_primary', ''))} | "
                        f"{_fmt(r.get('selectivity_z', ''))} |\n")
        else:
            f.write("_Pending Boltz-2 panel completion._\n\n")

        f.write(f"\n## Triple-LLM gate\n\n")
        f.write(f"This report MUST be triple-LLM-verified before any non-internal use.\n")
        f.write(f"Verification file: `ATLAS_TOP25_CASCADE_RESULTS_triple_llm.json` (pending).\n\n")

        f.write(f"## Next compute steps\n\n")
        f.write(f"1. **MD (25 ns)** for top-3 overall cross-target hits → stage on any idle A100.\n")
        f.write(f"2. **Cross-paralog selectivity** (KAT5/6A/7 vs KAT6B; EHMT1 vs EHMT2; KMT5B vs KMT5A/C).\n")
        f.write(f"3. **Chai-1 or OpenFold2 multi-seed rescore** for the top-3 to remove Boltz-2 single-pose bias.\n")
        f.write(f"4. **Known-inhibitor comparison**: for each target where a reference inhibitor exists "
                f"(UNC0642/G9a, A-196/SUV420, PF-9363/KAT6, NU9056/KAT5), re-dock via Boltz-2 as sanity check.\n")
        f.write(f"5. **Fleet cross-connection cron**: after merge, `cross_connection_engine.py` "
                f"should auto-detect triangles (KAT5+TP53+PERP, TIP60-EP400, EHMT1+EHMT2).\n\n")

        f.write(f"## Rules of use\n\n")
        f.write(f"- DRAFT. Simon-Comms-Gate HELD until triple-LLM 3/3 PASS + Christian SEND trigger.\n")
        f.write(f"- No external (Simon, Torsten) communication.\n")
        f.write(f"- Internal worktree review only.\n")


def _fmt(v):
    if v is None or v == "":
        return "—"
    try:
        x = float(v)
        return f"{x:.3f}"
    except Exception:
        return str(v)


PDB_MAP = {
    "EP400": "9C57",    "PEAK1": "6BHC",  "KAT7": "7D0P",
    "RNF213": "8S24",   "EHMT2": "5VSC",  "KAT6A": "9DZN",
    "KAT5": "2OU2",     "KMT5B": "3S8P",  "EHMT1": "3HNA",
}
def _pdb(t): return PDB_MAP.get(t, "")


if __name__ == "__main__":
    main()
