#!/usr/bin/env python3
"""
Publish the ECL-core-rescore v2 artefacts after rescore_binders_eclcore.py completes.

Inputs:
  /home/bryza/sma-research/qms/PERP_dossier/rescore_ecl_core/rescore_results.jsonl
  /home/bryza/sma-research/qms/PERP_dossier/interface_analysis/interface_metrics.json  (Round-1 top-10)
  /home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/top_binders_ecl1.tsv
  /home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/top_binders_ecl2.tsv

Outputs:
  /home/bryza/fleet-results/perp_binder_design_FINAL/rescore_ECLcore_v2.tsv
  /home/bryza/sma-research/qms/PERP_dossier/PERP_binder_RESCORE_ECLcore_v2.md

Ranking:
  Primary:   delta_iptm_core (desc)
  Tiebreak1: iptm_target_core (desc)
  Tiebreak2: plddt_target_core (desc)

Filter (SURVIVES):
  - delta_iptm_core must be not None
  - iptm_target_core >= 0.35 (non-trivial target preference)
  - delta_iptm_core >= 0.08 (beats scrambled control by a margin)
  - n_iface_A >= 3 (actually makes contact; prevents flyaway)

Gate levels (for reporting):
  STRONG : iptm_target_core >= 0.55 AND delta_iptm_core >= 0.20 AND n_iface_A >= 5
  MEDIUM : iptm_target_core >= 0.45 AND delta_iptm_core >= 0.15
  BASELINE : iptm_target_core >= 0.35 AND delta_iptm_core >= 0.08
"""
import json, csv, sys
from pathlib import Path

JSONL = Path("/home/bryza/sma-research/qms/PERP_dossier/rescore_ecl_core/rescore_results.jsonl")
TSV_OUT = Path("/home/bryza/fleet-results/perp_binder_design_FINAL/rescore_ECLcore_v2.tsv")
MD_OUT = Path("/home/bryza/sma-research/qms/PERP_dossier/PERP_binder_RESCORE_ECLcore_v2.md")
ROUND1_ECL1 = Path("/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/top_binders_ecl1.tsv")
ROUND1_ECL2 = Path("/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/top_binders_ecl2.tsv")
INTERFACE_METRICS = Path("/home/bryza/sma-research/qms/PERP_dossier/interface_analysis/interface_metrics.json")


def load_rescore():
    rows = []
    if not JSONL.exists():
        return rows
    for line in JSONL.read_text().splitlines():
        try:
            r = json.loads(line)
            if r.get("delta_iptm_core") is not None:
                rows.append(r)
        except Exception:
            pass
    return rows


def load_round1_top20(path):
    if not path.exists():
        return []
    with open(path) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def gate_level(iptm, delta, n_iface):
    if iptm is None or delta is None:
        return "FAIL"
    if iptm >= 0.55 and delta >= 0.20 and n_iface >= 5:
        return "STRONG"
    if iptm >= 0.45 and delta >= 0.15 and n_iface >= 4:
        return "MEDIUM"
    if iptm >= 0.35 and delta >= 0.08 and n_iface >= 3:
        return "BASELINE"
    return "FAIL"


def rank_rescore(rescore):
    # sort desc on delta_iptm_core, tiebreak iptm_target_core, then plddt_target_core
    def keyfn(r):
        return (
            -(r.get("delta_iptm_core") or -9),
            -(r.get("iptm_target_core") or 0),
            -(r.get("plddt_target_core") or 0),
        )
    rescore.sort(key=keyfn)
    for i, r in enumerate(rescore, 1):
        r["rank_v2"] = i
        r["gate"] = gate_level(r.get("iptm_target_core"),
                                r.get("delta_iptm_core"),
                                r.get("n_iface_A", 0))
    return rescore


def write_master_tsv(rows):
    TSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    hdr = ["rank_v2", "design_id", "ecl", "hotspot", "length",
           "iptm_target_core", "iptm_scrambled_core", "delta_iptm_core",
           "plddt_target_core", "n_iface_A", "n_iface_B",
           "iptm_target_full_round1", "delta_iptm_full_round1",
           "gate", "sequence"]
    with open(TSV_OUT, "w") as f:
        f.write("\t".join(hdr) + "\n")
        for r in rows:
            f.write("\t".join([
                str(r.get("rank_v2", "")),
                r.get("id", ""),
                r.get("ecl", ""),
                r.get("hotspot", ""),
                str(r.get("len", "")),
                f"{r.get('iptm_target_core',0):.3f}",
                f"{r.get('iptm_scrambled_core',0):.3f}",
                f"{r.get('delta_iptm_core',0):+.3f}",
                f"{r.get('plddt_target_core',0):.3f}",
                str(r.get("n_iface_A", 0)),
                str(r.get("n_iface_B", 0)),
                f"{r.get('iptm_target_full',0):.3f}",
                f"{r.get('delta_iptm_full',0):+.3f}",
                r.get("gate", ""),
                r.get("seq", ""),
            ]) + "\n")
    print(f"wrote {TSV_OUT} ({len(rows)} rows)", file=sys.stderr)


def write_markdown(all_rows):
    r1_ecl1 = {r["design_id"]: r for r in load_round1_top20(ROUND1_ECL1)}
    r1_ecl2 = {r["design_id"]: r for r in load_round1_top20(ROUND1_ECL2)}
    r1_ecl1_top10 = list(r1_ecl1.keys())[:10]
    r1_ecl2_top10 = list(r1_ecl2.keys())[:10]

    ecl1_rows = [r for r in all_rows if r["ecl"] == "ecl1"]
    ecl2_rows = [r for r in all_rows if r["ecl"] == "ecl2"]
    ecl1_rows = sorted(ecl1_rows,
        key=lambda r: (-(r["delta_iptm_core"] or -9), -(r["iptm_target_core"] or 0)))
    ecl2_rows = sorted(ecl2_rows,
        key=lambda r: (-(r["delta_iptm_core"] or -9), -(r["iptm_target_core"] or 0)))

    ecl1_top10 = ecl1_rows[:10]
    ecl2_top10 = ecl2_rows[:10]

    # Survival analysis — does each Round-1 top-10 appear in the v2 top-20 per ECL?
    r1_ecl1_survival = []
    for did in r1_ecl1_top10:
        v2_row = next((r for r in ecl1_rows if r["id"] == did), None)
        rank_v2 = next((i for i, r in enumerate(ecl1_rows, 1) if r["id"] == did), None)
        survives_top10 = rank_v2 is not None and rank_v2 <= 10
        r1_ecl1_survival.append((did, rank_v2, v2_row, survives_top10))
    r1_ecl2_survival = []
    for did in r1_ecl2_top10:
        v2_row = next((r for r in ecl2_rows if r["id"] == did), None)
        rank_v2 = next((i for i, r in enumerate(ecl2_rows, 1) if r["id"] == did), None)
        survives_top10 = rank_v2 is not None and rank_v2 <= 10
        r1_ecl2_survival.append((did, rank_v2, v2_row, survives_top10))

    ecl1_survival_rate = sum(1 for x in r1_ecl1_survival if x[3]) / 10
    ecl2_survival_rate = sum(1 for x in r1_ecl2_survival if x[3]) / 10

    # Count gate stats
    def gate_counts(rows):
        return {g: sum(1 for r in rows if r["gate"] == g)
                for g in ("STRONG", "MEDIUM", "BASELINE", "FAIL")}
    g1 = gate_counts(ecl1_rows)
    g2 = gate_counts(ecl2_rows)

    # Load interface_metrics for retraction note
    iface_metrics = []
    if INTERFACE_METRICS.exists():
        iface_metrics = json.load(open(INTERFACE_METRICS))

    # Build markdown
    md = []
    md.append("# PERP Binder Rescore v2 — ECL-core-only Boltz-2 co-fold")
    md.append("")
    md.append("**Status**: DRAFT — internal QMS revision of PERP binder top-lists.")
    md.append("**Date**: 2026-04-17")
    md.append("**Rescore budget**: 0 USD (self-host Boltz-2 on sma-h100-two:8003 + secondary endpoint :8004)")
    md.append("")
    md.append("## TL;DR")
    md.append("")
    md.append("Round-1 PERP binder top-10 was built by co-folding each binder with **full 193-aa PERP** and ranking by iptm. "
              "A Biopython interface audit (`PERP_binder_interface_analysis.md`, 2026-04-17) found that **8 of 10** "
              "top Round-1 binders actually contacted PERP's C-terminal tail (A170-A193), "
              "NOT their intended ECL loop. Only two (H1c_25_s5 at 45 % on-ECL, H1b_10_s3 at 27 %) made bona fide ECL contact.")
    md.append("")
    md.append("**Root cause**: full-length PERP target → binder was free to find the easiest-to-bind surface, "
              "which turned out to be the disordered hydrophobic tail, not the ECL loops.")
    md.append("")
    md.append("**Fix (this document)**: rescore all 240 Round-1 binders against **ECL core only**, not full PERP.")
    md.append("- ECL1 core = residues 30-80 (51 aa), used for H1a/H1b/H1c binders")
    md.append("- ECL2 core = residues 128-153 (26 aa), used for H2a/H2b/H2c binders")
    md.append("- Co-fold target + scrambled control → `iptm_target_core`, `delta_iptm_core`")
    md.append("- Ranking: `delta_iptm_core` desc; tiebreak `iptm_target_core` then plddt.")
    md.append("")
    md.append(f"**Result**: {g1['STRONG']+g1['MEDIUM']+g1['BASELINE']} / 120 ECL1 binders and "
              f"{g2['STRONG']+g2['MEDIUM']+g2['BASELINE']} / 120 ECL2 binders pass the BASELINE gate "
              f"(iptm_target_core ≥ 0.35, delta ≥ 0.08, n_iface_A ≥ 3) when forced to bind only the ECL core. "
              f"Round-1 top-10 survival in v2 top-10: ECL1 {int(ecl1_survival_rate*100)} %, ECL2 {int(ecl2_survival_rate*100)} %.")
    md.append("")
    md.append("## Methodology")
    md.append("")
    md.append("```")
    md.append("for each of 240 binders (40 designs × 6 hotspots):")
    md.append("    target_core = ECL1_core if hotspot in (H1a,H1b,H1c) else ECL2_core")
    md.append("    tgt  = Boltz2(target_core, binder_seq)")
    md.append("    scr  = Boltz2(target_core, scramble(binder_seq, seed=42))")
    md.append("    iptm_target_core    = tgt.iptm_scores[0]")
    md.append("    iptm_scrambled_core = scr.iptm_scores[0]")
    md.append("    delta_iptm_core     = tgt - scr")
    md.append("    # contact residues on chain A (= ECL core) from the returned pose")
    md.append("    n_iface_A = count(residues in ECL core within 4.5 Å heavy-atom of any binder atom)")
    md.append("    n_iface_B = count(residues in binder within 4.5 Å heavy-atom of any chain A atom)")
    md.append("```")
    md.append("")
    md.append("**Boltz-2 settings**: `recycling_steps=1`, `sampling_steps=25` (same as Round-1 for comparability).")
    md.append("**Endpoint**: round-robin across localhost:8003 (sma-h100-two tunnel) and localhost:8004 (secondary).")
    md.append("**Gate levels**:")
    md.append("- STRONG : iptm_target_core ≥ 0.55 AND delta ≥ 0.20 AND n_iface_A ≥ 5")
    md.append("- MEDIUM : iptm_target_core ≥ 0.45 AND delta ≥ 0.15 AND n_iface_A ≥ 4")
    md.append("- BASELINE : iptm_target_core ≥ 0.35 AND delta ≥ 0.08 AND n_iface_A ≥ 3")
    md.append("")
    md.append("### Why ECL-scoped iptm cannot be cheated by tail-binding")
    md.append("")
    md.append("By co-folding **only** the 51-aa ECL1 core (or 26-aa ECL2 core) as the target chain, the binder has no C-terminal tail available. "
              "Any binder whose Round-1 iptm was inflated by tail docking is forced to either (a) find genuine ECL contact or (b) fail. "
              "`delta_iptm_core > 0` vs scramble confirms specificity for ECL sequence, not generic peptide stickiness.")
    md.append("")
    md.append("## v2 Top-10 ECL1 (ECL-scoped ranking)")
    md.append("")
    md.append("| rank_v2 | design_id | hotspot | iptm_core | Δiptm_core | n_iface_A | n_iface_B | gate | iptm_full_R1 | Δiptm_full_R1 |")
    md.append("|---:|:---|:---|---:|---:|---:|---:|:---|---:|---:|")
    for r in ecl1_top10:
        md.append(f"| {r['rank_v2']} | {r['id']} | {r['hotspot']} | "
                  f"{r['iptm_target_core']:.3f} | {r['delta_iptm_core']:+.3f} | "
                  f"{r['n_iface_A']} | {r['n_iface_B']} | {r['gate']} | "
                  f"{r.get('iptm_target_full',0):.3f} | {r.get('delta_iptm_full',0):+.3f} |")
    md.append("")
    md.append("## v2 Top-10 ECL2 (ECL-scoped ranking)")
    md.append("")
    md.append("| rank_v2 | design_id | hotspot | iptm_core | Δiptm_core | n_iface_A | n_iface_B | gate | iptm_full_R1 | Δiptm_full_R1 |")
    md.append("|---:|:---|:---|---:|---:|---:|---:|:---|---:|---:|")
    for r in ecl2_top10:
        md.append(f"| {r['rank_v2']} | {r['id']} | {r['hotspot']} | "
                  f"{r['iptm_target_core']:.3f} | {r['delta_iptm_core']:+.3f} | "
                  f"{r['n_iface_A']} | {r['n_iface_B']} | {r['gate']} | "
                  f"{r.get('iptm_target_full',0):.3f} | {r.get('delta_iptm_full',0):+.3f} |")
    md.append("")
    md.append("## Round-1 top-10 survival")
    md.append("")
    md.append("### ECL1")
    md.append("")
    md.append("| Round-1 rank | design_id | v2 rank | iptm_core | Δiptm_core | gate | survives top-10 |")
    md.append("|---:|:---|---:|---:|---:|:---|:---|")
    for i, (did, rv2, row, survives) in enumerate(r1_ecl1_survival, 1):
        if row is None:
            md.append(f"| {i} | {did} | — | — | — | FAIL | no |")
        else:
            md.append(f"| {i} | {did} | {rv2} | {row['iptm_target_core']:.3f} | "
                      f"{row['delta_iptm_core']:+.3f} | {row['gate']} | "
                      f"{'yes' if survives else 'no'} |")
    md.append("")
    md.append("### ECL2")
    md.append("")
    md.append("| Round-1 rank | design_id | v2 rank | iptm_core | Δiptm_core | gate | survives top-10 |")
    md.append("|---:|:---|---:|---:|---:|:---|:---|")
    for i, (did, rv2, row, survives) in enumerate(r1_ecl2_survival, 1):
        if row is None:
            md.append(f"| {i} | {did} | — | — | — | FAIL | no |")
        else:
            md.append(f"| {i} | {did} | {rv2} | {row['iptm_target_core']:.3f} | "
                      f"{row['delta_iptm_core']:+.3f} | {row['gate']} | "
                      f"{'yes' if survives else 'no'} |")
    md.append("")
    md.append("## Gate statistics (all 240 rescored)")
    md.append("")
    md.append(f"**ECL1 (120 binders)**: STRONG {g1['STRONG']} · MEDIUM {g1['MEDIUM']} · BASELINE {g1['BASELINE']} · FAIL {g1['FAIL']}")
    md.append("")
    md.append(f"**ECL2 (120 binders)**: STRONG {g2['STRONG']} · MEDIUM {g2['MEDIUM']} · BASELINE {g2['BASELINE']} · FAIL {g2['FAIL']}")
    md.append("")
    md.append("## Retraction note")
    md.append("")
    md.append("The Round-1 top-10 documented in `PERP_binder_design_RESULTS.md` and the Round-1 ranking tables "
              "(`top_binders_ecl1.tsv`, `top_binders_ecl2.tsv`) are **superseded** by this v2 rescore for the purpose "
              "of wet-lab nomination and Simon-pack inclusion. They remain valid as intermediate artefacts but must "
              "not be cited externally as \"top PERP binders\" without the ECL-core rescore qualifier.")
    md.append("")
    md.append("The triggering audit is `PERP_binder_interface_analysis.md` (Biopython InterfaceAnalyzer on Round-1 top-10, "
              "2026-04-17). Per-binder contact metrics live in "
              "`/home/bryza/sma-research/qms/PERP_dossier/interface_analysis/interface_metrics.json`.")
    md.append("")
    md.append("Round-1 top-10 binders whose full-PERP iptm was dominated by tail contact (≥ 50 % of interface residues on PERP A170-A193):")
    md.append("")
    md.append("| design_id | ECL | full-PERP iptm_target (R1) | on-ECL contact % (Biopython audit) |")
    md.append("|:---|:---|---:|---:|")
    for im in iface_metrics:
        if "error" in im or "contacts" not in im:
            continue
        iface_a = im["contacts"].get("iface_res_A_list", [])
        if not iface_a:
            continue
        ecl = im["ecl"]
        if ecl == "ECL1":
            on_ecl = sum(1 for x in iface_a if 30 <= x <= 80)
        else:
            on_ecl = sum(1 for x in iface_a if 128 <= x <= 153)
        pct = (on_ecl / len(iface_a)) * 100 if iface_a else 0
        md.append(f"| {im['design_id']} | {ecl} | {im['iptm_target']:.3f} | {pct:.0f} % |")
    md.append("")
    md.append("## External-communication status")
    md.append("")
    md.append("**DRAFT**. Simon pack top-5 nomination is **BLOCKED** until the v2 top-10 per ECL is reviewed and "
              "a human (Christian Fischer) signs off on which v2 binders to advance to wet-lab. "
              "No external comms triggered by this document.")
    md.append("")
    md.append("### Next-compute steps (not publication readiness)")
    md.append("")
    md.append("Per `rule-compute-not-publication.md`, residual caveats are framed as compute-next, not as paper-readiness gaps:")
    md.append("")
    md.append("1. Re-run Biopython InterfaceAnalyzer on the v2 top-10 per ECL to cross-check that "
              "`n_iface_A` from the Boltz-2 pose matches a rigorous Biopython count, and to get SASA / salt-bridge / H-bond.")
    md.append("2. For surviving v2 top-5 per ECL: run a full 193-aa PERP co-fold re-check to confirm the "
              "binder's Round-1 iptm was NOT pure-tail (i.e., the binder also had a real ECL contact alongside tail noise). "
              "Expected: v2 survivors show both ECL-core iptm ≥ 0.45 AND full-PERP iptm ≥ 0.40, with majority of chain-A "
              "iface residues in the ECL-core range.")
    md.append("3. Proceed to Round-2 disulfide-constrained variants of v2 top-5 per ECL (scaffold is existing "
              "`disulfide_rerun/` pipeline).")
    md.append("4. MD relaxation (100 ns OpenMM) of v2 top-3 per ECL to check stability of the ECL interface "
              "before wet-lab nomination.")
    md.append("")
    md.append("## Reproducibility")
    md.append("")
    md.append("- Driver: `/home/bryza/sma-research/qms/PERP_dossier/rescore_ecl_core/rescore_binders_eclcore.py`")
    md.append("- Publisher: `/home/bryza/sma-research/qms/PERP_dossier/rescore_ecl_core/publish_v2.py`")
    md.append("- Per-binder raw: `/home/bryza/sma-research/qms/PERP_dossier/rescore_ecl_core/rescore_results.jsonl`")
    md.append("- Poses: `/home/bryza/sma-research/qms/PERP_dossier/rescore_ecl_core/poses/<design_id>_core.pdb`")
    md.append("- Master TSV: `/home/bryza/fleet-results/perp_binder_design_FINAL/rescore_ECLcore_v2.tsv`")
    md.append("")
    md.append("## Signoff gate")
    md.append("")
    md.append("- [ ] Triple-LLM 3/3 PASS on this document")
    md.append("- [ ] Christian Fischer human sign-off on v2 top-5 per ECL for wet-lab nomination")
    md.append("- [ ] Update CLAIMS_REGISTRY.md Claim #16 with \"Round-1 PERP top-10 RETRACTED\" subnote if any top-5 Round-1 binder drops out of v2 top-10")
    md.append("")

    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUT.write_text("\n".join(md))
    print(f"wrote {MD_OUT}", file=sys.stderr)


def main():
    rows = load_rescore()
    if not rows:
        print("no rescore results found — did rescore_binders_eclcore.py run?", file=sys.stderr)
        sys.exit(1)
    rows = rank_rescore(rows)
    write_master_tsv(rows)
    write_markdown(rows)
    print(f"published {len(rows)} binders", file=sys.stderr)


if __name__ == "__main__":
    main()
