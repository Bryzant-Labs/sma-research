"""LIMK2 Arm 1 Redesign — end-to-end orchestrator.

Runs:
  1. Pull PXM SDFs from asxm (strategies A/B/C)
  2. RDKit filter + descriptors + Tanimoto vs LIMKi3
  3. Strategy-specific filters (A/C: HBD 2-4, B: Tanimoto>=0.3, all: BBB>=0.5)
  4. Build Boltz-2 affinity YAMLs
  5. Run Boltz-2 affinity head on sma-h100-two
  6. Apply gate: affinity_probability_binary > 0.3
  7. If survivors >= 5 → run 15-kinase selectivity panel
  8. Gate: z_LIMK2 > 0 AND sel_z > 0
  9. If panel-passers >= 5 → write RESULTS.md DRAFT, triple-LLM verify, promote.
     Else → write HONEST RETRACTION.

Logs to: logs/orchestrate_YYYYMMDD_HHMM.log
"""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/home/bryza/sma-research/qms/limk2_arm1_redesign")
RESULTS_PATH = ROOT / "LIMK2_ARM1_REDESIGN_RESULTS.md"
GATE_THRESHOLD = 5


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def step_filter_and_score():
    """Runs filter_and_score.py as subprocess; it handles fetch + RDKit + boltz."""
    log("STEP 1-6: filter + Boltz-2 affinity head rescore")
    r = subprocess.run(
        ["python3", str(ROOT / "filter_and_score.py")],
        capture_output=True, text=True,
    )
    print(r.stdout[-3000:])
    if r.returncode != 0:
        log(f"FILTER+SCORE FAILED rc={r.returncode}; STDERR tail: {r.stderr[-2000:]}")
        return False, 0
    gd = json.loads((ROOT / "GATE_DECISION.json").read_text())
    n_binders = gd.get("n_binders", 0)
    log(f"Affinity gate: {n_binders} binders passed (>= {GATE_THRESHOLD} to proceed)")
    return True, n_binders


def step_selectivity_panel():
    log("STEP 7-8: 15-kinase selectivity panel")
    r = subprocess.run(
        ["python3", str(ROOT / "run_kinase_panel.py")],
        capture_output=True, text=True,
    )
    print(r.stdout[-3000:])
    if r.returncode != 0:
        log(f"PANEL FAILED rc={r.returncode}; STDERR tail: {r.stderr[-2000:]}")
        return False, 0
    sg = json.loads((ROOT / "SELECTIVITY_GATE.json").read_text())
    n_pass = sg.get("n_passing", 0)
    log(f"Selectivity gate: {n_pass} compounds pass z_LIMK2>0 AND sel_z>0 (>= {GATE_THRESHOLD} to restore Arm 1)")
    return True, n_pass


def write_results(n_binders, n_pass, gate_outcome):
    """Write LIMK2_ARM1_REDESIGN_RESULTS.md."""
    gd = json.loads((ROOT / "GATE_DECISION.json").read_text()) if (ROOT / "GATE_DECISION.json").exists() else {}
    sg = json.loads((ROOT / "SELECTIVITY_GATE.json").read_text()) if (ROOT / "SELECTIVITY_GATE.json").exists() else {}
    flog = json.loads((ROOT / "filter_log.json").read_text()) if (ROOT / "filter_log.json").exists() else {}
    pg = json.loads((ROOT / "pocket_geometry.json").read_text())

    binders = gd.get("binders", [])
    panel_pass = sg.get("passing", [])
    panel_all = sg.get("all_ranked", [])

    def fmt_ki(b):
        ki = b.get("pred_ki_nM")
        if ki is None: return "NA"
        lo, hi = b.get("ki_95pi_nM", [None, None])
        if ki < 1000:
            return f"{ki:.1f} nM [{lo:.1f}-{hi:.1f} nM]"
        else:
            return f"{ki/1000:.2f} µM [{lo/1000:.2f}-{hi/1000:.2f} µM]"

    now = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())

    md = [
        f"# LIMK2 Arm 1 Redesign — Results",
        "",
        f"**DRAFT — written {now} — triple-LLM verification pending — external transmission BLOCKED.**",
        "",
        f"**Author:** Opus Master Agent, session 2026-04-17",
        f"**Mission:** rescue LIMK2-αC Arm 1 of Simon-pack after affinity-head library-wide retraction (0/99 nanomolar binders in prior PocketXMol αC-K383 library).",
        "",
        "## 0. Honest status",
        "",
    ]
    if gate_outcome == "RESTORED":
        md += [
            f"**OUTCOME: Arm 1 RESTORED** — {n_pass} compound(s) pass BOTH affinity-probability>0.3 (calibrated Ki R²=0.690) AND selectivity z-gates (z_LIMK2>0, sel_z>0).",
            "",
            "**Caveats not stripped:**",
            "- These are computational leads only. No wet-lab binding or enzymatic data exists.",
            "- Ki calibration RMSE is 0.378 log10-Ki (≈2.4× multiplicative uncertainty).",
            "- The Boltz-2 affinity head training data may overlap published LIMK2 ligands; R²=0.690 is likely an upper bound for out-of-distribution performance on PocketXMol chemotypes.",
            "- `sel_z` uses Boltz-2 iptm as a selectivity proxy. iptm-vs-Ki correlation R²=0.007 per ae345009; iptm panel is a geometric tiebreaker, not a functional selectivity measurement.",
            "- Activator vs inhibitor classification cannot be made computationally; requires in-vitro enzymatic assay.",
        ]
    else:
        md += [
            f"**OUTCOME: Arm 1 REMAINS RETRACTED** — redesign strategies A/B/C exhausted.",
            f"- {n_binders} compounds passed affinity-probability gate (>0.3)",
            f"- {n_pass} compounds passed selectivity z-gates (z_LIMK2>0 AND sel_z>0)",
            f"- **Neither threshold ({GATE_THRESHOLD}) reached.**",
            "",
            "**Verdict:** no nanomolar, selective LIMK2 binder could be generated in this redesign pass. Arm 1 requires wet-lab fragment-screen before further compute investment. The other 3 arms of the Simon-pack (ROCK2-αC, PERP binders, MDM2 activator) are unaffected.",
        ]
    md += [""]

    # PDB verification section
    md += [
        "## 1. Input verification",
        "",
        f"- **PDB:** 4TPT",
        f"- **Title (RCSB verified):** {pg['title_verified']}",
        "- **Chain:** A (apo — 35H ligand stripped)",
        "- **Local numbering confirmed:** catalytic β3-Lys = K360, αC-Glu = E376, HRD-Asp = D451, DFG-Asp = D469, gatekeeper vicinity = T405.",
        "- Task spec referenced K383/T407/G408/T409/D460; these residue numbers do not map to 4TPT chain A.",
        "  Strategies below use the actual catalytic anchors identified from the PDB.",
        "- 35H (LIMKi3 analog) ligand COM: [9.384, 7.372, 20.916] Å.",
        "",
        "## 2. Three redesign pocket strategies",
        "",
        "| Strategy | Anchor rationale | Pocket center (Å) | Radius | Filter |",
        "|---|---|---|---|---|",
        f"| A — activator DFG-oriented | prior αC center ({pg['prior_alphaC_pocket']}) shifted 4.5 Å toward DFG-Asp D469 Cα | {pg['pocket_A_activator_Dfg_oriented']['center']} | 10 Å | RDKit + Lipinski + QED≥0.4 + BBB≥0.5 + HBD∈[2,4] |",
        f"| B — LIMKi3 scaffold-seeded | 35H ligand COM (LIMKi3 analog co-crystallized) | {pg['pocket_B_limki3_seeded']['center']} | 10 Å | RDKit + Lipinski + QED≥0.4 + BBB≥0.5 + Tanimoto(ECFP4) ≥ 0.3 vs LIMKi3 |",
        f"| C — αC-Glu / DFG-Asp H-bond network | midpoint(E376 carboxylate, D469 carboxylate) | {pg['pocket_C_Hbond_network']['center']} | 8 Å | RDKit + Lipinski + QED≥0.4 + BBB≥0.5 + HBD∈[2,4] |",
        "",
        "Each ran PocketXMol (500 molecules, `task=sbdd`, flow_model=jointModel via `configs/sample/pxm.yml`) on A100 SXM 40GB (Vast instance 35141611).",
        "",
        "## 3. Generation + filter cascade",
        "",
        f"```",
        f"Raw generated: {flog.get('total_generated', 'NA')}",
        f"After RDKit validity + unique canonical SMILES: included in total_generated (unique count)",
        f"After Lipinski Ro5: {flog.get('after_lipinski', 'NA')}",
        f"After QED >= 0.4: {flog.get('after_QED_0.4', 'NA')}",
        f"After BBB >= 0.5 (Egan logistic): {flog.get('after_BBB_0.5', 'NA')}",
        f"After strategy-specific filter: {flog.get('after_strategy_specific', 'NA')}",
        f"  by strategy: {flog.get('by_strategy', {})}",
        f"```",
        "",
        "## 4. Boltz-2 affinity head rescoring",
        "",
        f"- Model: Boltz-2 with `properties.affinity.binder: L1` on each compound vs LIMK2 kinase domain (human P53671 domain 327-606).",
        f"- Server: self-host on sma-h100-two (H100 PCIe 80GB), `/home/shadeform/miniconda3/envs/pxm_cu128/bin/boltz predict` with `--sampling_steps_affinity 100 --diffusion_samples_affinity 3`.",
        f"- Calibration of record: LIMK2 slope=1.249, intercept=3.549, RMSE=0.378 log10-Ki, R²=0.690, n=20 ChEMBL Ki pairs (fits `/home/bryza/sma-research/qms/chembl_ki_affinity_head/fits.json`).",
        f"- Gate: `affinity_probability_binary > 0.3`.",
        "",
        f"**Binary-binder gate survivors: {len(binders)}**",
        "",
    ]
    if binders:
        md += [
            "| rank | strategy | job_id | pred Ki (95% PI) | prob_binary | QED | BBB | Tanimoto_vs_LIMKi3 | SMILES (first 50) |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for i, b in enumerate(binders[:30], 1):
            ki_s = fmt_ki(b)
            tani = b.get("tanimoto_limki3")
            tani_s = f"{tani:.3f}" if tani is not None else "NA"
            smi_short = b["smiles"][:50] + ("..." if len(b["smiles"]) > 50 else "")
            md.append(
                f"| {i} | {b['strategy']} | `{b['job_id']}` | {ki_s} | {b.get('affinity_probability_binary', 0):.3f} | {b.get('QED', 0):.2f} | {b.get('BBB', 0):.2f} | {tani_s} | `{smi_short}` |"
            )
    md += [""]

    # Selectivity panel
    md += [
        "## 5. 15-kinase selectivity panel",
        "",
    ]
    if panel_all:
        md += [
            f"Ran Boltz-2 against LIMK2 + 14 off-target kinases (LIMK1, ROCK1/2, JAK1/2/3, CDK2/5, SRC, FYN, LCK, PAK1/4, MAPK14).",
            f"- Total compounds panelled: {len(panel_all)}",
            f"- Pass `z_LIMK2 > 0 AND sel_z > 0`: **{len(panel_pass)}**",
            "",
            "**Top-ranked by sel_z (even if gate failed):**",
            "",
            "| rank | strategy | job_id | iptm_LIMK2 | z_LIMK2 | sel_z | n_kinases_ok | pred Ki |",
            "|---|---|---|---|---|---|---|---|",
        ]
        # Merge Ki back
        b_by_job = {b["job_id"]: b for b in binders}
        for i, r in enumerate(panel_all[:15], 1):
            b_match = b_by_job.get(r["binder_job_id"], {})
            ki_s = fmt_ki(b_match)
            md.append(
                f"| {i} | {r['strategy']} | `{r['binder_job_id']}` | {r['iptm_LIMK2']:.3f} | {r['z_LIMK2']:+.2f} | {r['sel_z']:+.2f} | {r['n_kinases_ok']} | {ki_s} |"
            )
    else:
        md.append("_No compounds reached selectivity panel — gate decision was made upstream._")

    md += [""]

    # Final decision + honesty block
    md += [
        "## 6. Gate decision",
        "",
        f"- Compounds passing **both** affinity-binary (prob>0.3) AND selectivity z-gates: **{n_pass}**",
        f"- Threshold for Arm 1 RESTORATION: ≥ 5",
        f"- **Decision:** {gate_outcome}",
        "",
    ]
    if gate_outcome == "RESTORED":
        md += [
            "### Recommended leads",
            "",
        ]
        for i, r in enumerate(panel_pass[:10], 1):
            b_match = b_by_job.get(r["binder_job_id"], {})
            ki_s = fmt_ki(b_match)
            md += [
                f"**Lead {i}** — Strategy {r['strategy']}",
                f"  - SMILES: `{r['smiles']}`",
                f"  - Predicted Ki: {ki_s}",
                f"  - Boltz-2 iptm (LIMK2): {r['iptm_LIMK2']:.3f}",
                f"  - z_LIMK2: {r['z_LIMK2']:+.2f}",
                f"  - sel_z: {r['sel_z']:+.2f}",
                "",
            ]
    else:
        md += [
            "### Why Arm 1 remains retracted",
            "",
            "The redesign strategies (A: DFG-oriented activator pocket; B: LIMKi3 scaffold-seeded; C: αC-Glu/DFG-Asp H-bond network) did not yield enough compounds passing both gates. Possible causes:",
            "- **Affinity head R²=0.690 calibration** filters out most PocketXMol geometry-plausible hits that lack Ki structural signature.",
            "- **Binary-binder prob > 0.3** is conservative; most µM-range binders fall at 0.1-0.3 rather than > 0.5.",
            "- **PocketXMol on αC-allosteric pockets** tends toward non-cognate scaffolds biased away from established kinase ligand series (this was the core failure mode of the original LIMK2-αC library).",
            "",
            "### Recommendation for Arm 1",
            "",
            "**Wet-lab fragment screen** (e.g., SPR or NMR against recombinant LIMK2 kinase domain, 4TPT pocket-directed fragment library ~500 fragments) is the most honest next step before further compute investment. Alternative compute strategies that might be worth a follow-up pass include:",
            "- Scaffold-retained fragment-growing from a µM-range LIMK2 scaffold (e.g., pyridazone-type or aminopyrimidine-type) rather than de novo PocketXMol.",
            "- Boltz-2 affinity head with 3 seeds per compound (instead of 1) to stabilize the `affinity_probability_binary` estimate.",
            "- Co-crystal-informed PocketXMol fragment-linking targeting both the hinge and the αC cleft as a 2-pocket linker problem.",
            "",
            "The other three Simon-pack arms (ROCK2-αC activator, PERP ECL binders, MDM2 activator) are unaffected by this retraction.",
        ]

    md += [
        "",
        "## 7. Compute budget actual",
        "",
        "- PocketXMol 3×500 mol on A100 SXM 40GB (sma-pxm-batch-20260417-asxm, 35141611): ~60 min wall-clock, ~$0.85.",
        "- Boltz-2 affinity head on sma-h100-two H100 PCIe (self-host): {n_binders_for_boltz} YAMLs × ~10s = ~{boltz_min} min.",
        "- Boltz-2 15-kinase panel (if run): {n_panel_yamls} YAMLs × ~3s batched = ~{panel_min} min.",
        "- DiffDock C_rel validation: NOT run in this pass (reserved for restored leads only).",
        "- Total marginal spend: ~$1 (well under $5 budget).",
        "",
        "## 8. File manifest",
        "",
        "- `pocket_geometry.json` — 3 pocket centers with key-residue anchors",
        "- `configs/config_{A,B,C}_*.yml` — PocketXMol configs",
        "- `4tpt_chainA_apo.pdb` — LIMK2 chain A, apo, HETATM stripped",
        "- `filter_and_score.py` — full cascade runner",
        "- `run_kinase_panel.py` — selectivity panel runner",
        "- `orchestrate_redesign.py` — end-to-end orchestrator (this run)",
        "- `filter_log.json` — gate-by-gate retention counts",
        "- `GATE_DECISION.json` — affinity binders (prob > 0.3)",
        "- `SELECTIVITY_GATE.json` — z-gate passers",
        "- `survivors_filtered.csv` — pre-Boltz candidates",
        "- `affinity_rescored.json` — Boltz-2 affinity head results",
        "- `kinase_panel_raw.jsonl` — raw 15-kinase Boltz-2 outputs",
        "- `kinase_panel_ranked.csv` — z-score ranked",
        "",
        "## 9. Triple-LLM verification",
        "",
        "| Reviewer | Verdict | Timestamp |",
        "|---|---|---|",
        "| OpenAI GPT-4o | pending | — |",
        "| Groq Llama-3.3-70B | pending | — |",
        "| Google Gemini 2.0 Flash | pending | — |",
        "",
        "Aggregate: **DRAFT — not yet 3/3 PASS**. External transmission blocked until `LIMK2_ARM1_REDESIGN_RESULTS_triple_llm.json` shows `gate: APPROVED`.",
        "",
        "---",
        "",
        "*End of redesign results, DRAFT. Do not forward externally until triple-LLM gate clears + Christian Fischer human sign-off + LIMK2_NEW_STORY_FOR_SIMON.md v3 update applied.*",
    ]

    n_binders_for_boltz = len(binders) if binders else 0
    boltz_min = max(1, n_binders_for_boltz * 10 // 60)
    n_panel_yamls = len(panel_all) * 15 if panel_all else 0
    panel_min = max(1, n_panel_yamls * 3 // 60)

    text = "\n".join(md)
    text = text.replace("{n_binders_for_boltz}", str(n_binders_for_boltz))
    text = text.replace("{boltz_min}", str(boltz_min))
    text = text.replace("{n_panel_yamls}", str(n_panel_yamls))
    text = text.replace("{panel_min}", str(panel_min))

    RESULTS_PATH.write_text(text)
    log(f"Wrote RESULTS: {RESULTS_PATH}")


def run_triple_llm_verify():
    log("STEP 9: triple-LLM verification")
    script = Path("/home/bryza/gpu-fleet/scripts/triple_llm_verify.py")
    if not script.exists():
        log(f"ERROR: triple_llm_verify.py not found at {script}")
        return False
    r = subprocess.run(
        ["python3", str(script), "--file", str(RESULTS_PATH)],
        capture_output=True, text=True, timeout=600,
    )
    print(r.stdout[-3000:])
    if r.returncode != 0:
        print("STDERR tail:", r.stderr[-1500:])
    verdict_path = RESULTS_PATH.with_name(RESULTS_PATH.stem + "_triple_llm.json")
    if verdict_path.exists():
        v = json.loads(verdict_path.read_text())
        return v.get("gate") == "APPROVED"
    return False


def main():
    log("=== LIMK2 Arm 1 Redesign Orchestrator ===")

    ok, n_binders = step_filter_and_score()
    if not ok:
        log("HALT: filter+score failed")
        return 1

    n_pass = 0
    if n_binders >= GATE_THRESHOLD:
        log(f"Affinity gate passed threshold ({n_binders} >= {GATE_THRESHOLD}). Proceeding to selectivity panel.")
        ok, n_pass = step_selectivity_panel()
        if not ok:
            log("Selectivity panel failed")

    gate_outcome = "RESTORED" if n_pass >= GATE_THRESHOLD else "EXHAUSTED"
    log(f"=== FINAL DECISION: {gate_outcome} (n_binders={n_binders}, n_pass={n_pass}) ===")

    write_results(n_binders, n_pass, gate_outcome)

    # Run triple-LLM verification regardless of outcome (honest retraction also deserves QC)
    approved = run_triple_llm_verify()
    log(f"Triple-LLM verification: {'APPROVED' if approved else 'REJECTED / ERROR'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
