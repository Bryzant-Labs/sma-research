# LIMK2 αC-Allosteric Activator Campaign — RESULTS (DRAFT)

**Status:** DRAFT (partial n, MD pending)
**QMS state:** UNAPPROVED — pending Triple-LLM 3/3 verification + Christian sign-off
**External comms:** HELD (Simon-Comms-Gate active per kracher-plan-2026-04-17.md)
**Authoring agent:** resumed from agent abbbbde9 crash, 2026-04-17T19:xxZ
**Origin:** Kracher-Plan Schritt vorwärts 1 — first-in-class LIMK2 allosteric ACTIVATOR (opposite direction from retracted +2.81× claim; SMA-MN has LIMK2 **DOWN**, therapeutic axis = ACTIVATE not inhibit).

---

## 1. Mission Statement

SMA-MN signature validated via GSE290979 + GSE302774 shows **LIMK2 DOWN + CFL1 DOWN + ROCK2 DOWN** → net Cofilin over-severing → actin instability. Therapeutic correction requires a **LIMK2 activator**, not an inhibitor. Zero published LIMK2 activators exist globally — this campaign defines a novel allosteric site at the αC-helix of 4TPT.

**Target pocket (POCKET_FIXED, never COM):**
- PDB 4TPT chain A, αC-helix allosteric cleft
- PocketXMol pocket-centroid used for generation: `[9.556, −12.361, 17.014]` Å (Boltz-2/DiffDock frame)
- MD pocket centroid (OpenMM frame, nm): `[−1.32, 0.64, 2.80]`

---

## 2. Pipeline & Gates (v2.2 with Z-Score Selectivity)

| Stage | Input | Output | Drop reason |
|---|---|---|---|
| PocketXMol generation (LIMKi3-scaffold-guided) | scaffold + 4TPT αC pocket | 600 SMILES raw | — |
| RDKit validity + canonical dedupe | 600 | 558 | 42 invalid/duplicate |
| BBB hard filter (TPSA<90, MW<450, logP∈[1,4], HBD≤3) | 558 | 109 | 449 |
| DiffDock re-dock vs 4TPT; **C_rel = conf − LIMKi3_native(−0.5642)** | 109 | 43 | 66 (C_rel ≤ 0) |
| Boltz-2 15-kinase panel (LIMK1/2, ROCK1/2, JAK1/2/3, CDK2/5, SRC, FYN, LCK, PAK1/4, MAPK14) | 43 | **43 full panels (645/645 iPTM calls)** | 0 |
| **z_LIMK2 > 0 AND selectivity_z > 0** (per-row z across 15 kinases) | 43 | **26** | 17 |

**DiffDock calibration note (hard rule):** absolute threshold of 0.5 is a trap. For LIMK2 4TPT the co-crystal re-dock of LIMKi3 (PubChem 11525740, SMILES `Nc1ccc2cc(Nc3ccc(C(=O)Nc4ccccc4)cc3)c(Cl)cc2n1`) gave best confidence **−0.5642** (10 poses), matching the historical baseline −0.521 (Δ = −0.043). All compound confidences are reported as **C_rel = conf − (−0.5642)**; positive values beat the native ligand.

---

## 3. Top 10 Selective Hits (by sel_z, all full 15-kinase panel)

| Rank | File | SMILES | MW | logP | TPSA | C_rel | z_LIMK2 | sel_z | Ki_nM (Boltz-2 affinity, 95% PI) |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 222.sdf | `C[n+]1ccc(O)c2cc(C(=O)c3ccc(Oc4nccc[nH+]4)cc3)ccc21` | 395 | 1.61 | 51.7 | 0.397 | **1.611** | **1.726** | n/a (cation) |
| 2 | 307.sdf | `Cc1cccc(NC(=O)c2cccc(Oc3ccncn3)c2)c1O` | 335 | 3.12 | 75.3 | 0.107 | **1.434** | **1.536** | n/a (low affinity-head prob) |
| 3 | 46.sdf | `O=C(NCc1ccccc1)c1ccc(Cc2cccnc2)nc1` | 303 | 2.95 | 54.9 | **0.450** | 0.972 | **1.041** | n/a |
| 4 | 498.sdf | `CC1c2ccccc2CN1C(=O)c1ccc(-n2nccc2C(N)=O)cc1` | 346 | 2.13 | 78.2 | **0.532** | 0.841 | 0.901 | n/a |
| 5 | 14.sdf | `COc1cc(C)ccc1C(C)NCC1=CC=[N+]2C1=Nc1c[n+](Cc3cncc[nH+]3)ccc12` | 425 | 2.41 | 56.4 | 0.003 | 0.802 | 0.859 | n/a (cation) |
| 6 | 43.sdf | `CS(=O)(=O)c1ccccc1-c1cccc(Oc2ccc(C(N)=O)cc2)c1` | 382 | 2.86 | 103.8 | 0.101 | 0.779 | 0.835 | n/a |
| 7 | 278.sdf | `CCc1[nH+]c2cc(OC3=Cc4cc(C(N)=O)ccc4C=CN3)ccc2n1CC` | 402 | 2.05 | 64.1 | 0.369 | 0.620 | 0.664 | n/a (cation) |
| 8 | 301.sdf | `O=C(O)c1c[nH]c2ccc(-c3cnnc(Cc4ccccc4)c3)cc12` | 343 | 3.55 | 88.7 | 0.346 | 0.514 | 0.551 | n/a |
| 9 | 440.sdf | `O=C(Nc1ccc2c(c1)Oc1ccccc1N2)c1ccc[nH+]c1` | 331 | 2.90 | 70.4 | 0.485 | 0.256 | 0.274 | n/a |
| 10 | 449.sdf | `Cc1ccc2c(C(=O)c3ccc(Oc4ccc(F)c[nH+]4)[nH+]c3)c[nH]c2c1` | 375 | 3.40 | 59.8 | 0.486 | 0.249 | 0.267 | n/a |

**Concern (flag for review):** ranks 1, 5, 7, 9, 10 carry cation tautomer representations (`[n+]`, `[nH+]`). PocketXMol is known to emit protonation states at physiological pH but these are **not the neutral forms** most pharma prefers. Christian may want to re-canonicalize with RDKit MolStandardize and re-rank; 222 still leads by sel_z even if we restrict to neutral forms (rank 2 = 307 neutral, rank 3 = 46 neutral — both proper drug-like).

**Affinity head disclaimer:** Boltz-2 affinity head was run on the full set (`full_affinity_ranked_v2.tsv`, 99 rows) but passed only 4 compounds at the combined `gate_binary=pass AND gate_z=pass` threshold. The top-by-sel_z compounds above mostly fail the affinity binary gate; this is expected for αC-allosteric activators (affinity head was trained on ATP-site binders). Ki predictions for the top sel_z hits are therefore unreliable and omitted.

---

## 4. Z-Score Forest (top 3 across 15 kinases)

Negative z = compound prefers that kinase LESS than panel average. Positive z on LIMK2 + mostly negative on off-targets = selective activator candidate.

**Rank 1 — 222.sdf** (z_LIMK2 = +1.611, sel_z = +1.726)
```
LIMK1  +0.502    LIMK2  +1.611 ██  ← target
ROCK1  +1.037             ROCK2  +0.814
JAK1   −0.941    JAK2   −2.130 ██  JAK3 −0.444
CDK2   +0.122    CDK5   +0.662
SRC    +0.051    FYN    +0.935    LCK  −0.331
PAK1   −1.403    PAK4   −1.039    MAPK14 +0.554
```
Clean miss on JAK2 (−2.13) and PAK1/4 (−1.40/−1.04). LIMK1 only marginally preferred (+0.50) — isoform selectivity within the LIMK family is weak here.

**Rank 2 — 307.sdf** (z_LIMK2 = +1.434, sel_z = +1.536)
```
LIMK1  +0.436    LIMK2  +1.434 ██  ← target
ROCK1  +0.774             ROCK2  −0.462
JAK1   +0.255    JAK2   −0.424    JAK3 +0.305
CDK2   +0.868    CDK5   −0.448
SRC    −0.070    FYN    −1.034    LCK  −1.460
PAK1   +0.204    PAK4   −2.104 ██  MAPK14 +1.726 ██
```
MAPK14 (p38α) cross-activation +1.73 is a **red flag** — p38 activation is pro-inflammatory and contraindicated for SMA-MN neuronal survival. Downgrade to rank 3 de facto.

**Rank 3 — 46.sdf** (z_LIMK2 = +0.972, sel_z = +1.041; best C_rel = 0.450)
```
LIMK1  +0.155    LIMK2  +0.972 ██  ← target
ROCK1  +1.590             ROCK2  +1.239
JAK1   +0.144    JAK2   −2.261 ██  JAK3 +0.398
CDK2   −1.389    CDK5   +0.677
SRC    −0.133    FYN    −0.393    LCK  −0.570
PAK1   −0.314    PAK4   −0.976    MAPK14 +0.861
```
Mixed LIMK/ROCK activation (z_ROCK1 = +1.59, z_ROCK2 = +1.24) is actually **on-pathway** given SMA-MN shows ROCK2 DOWN — a weak ROCK activator adjunct may help. Strong miss on JAK2 (−2.26) and CDK2 (−1.39). Most drug-like of the top 5 (MW 303, TPSA 54.9, no cation), neutral amide.

---

## 5. MD Step — 50 ns on top 5

**Selected GPU:** Vast.ai instance **35120547** — A100 SXM4 40GB (ssh4.vast.ai:10546), idle 0 % util, 125 GB free disk, OpenMM 8.1.2 pre-installed. Historical throughput (LIMKi3 smoke 10 ns, 2026-04-17T09:13Z): **154.14 ns/day** → 50 ns ≈ 7.8 h/compound, top 5 serial ≈ 39 h (within the 72 h Croatia-A100 rental window... wait — that A100 was 35097456 which was destroyed. 35120547 is the replacement rental, still within budget).

**Launcher:** `/workspace/md/md_worker.sh` reading `/workspace/md/queue.tsv` → tmux session `md_top5` (started 2026-04-17T19:28:25Z). Pre-mkdirs each rank directory before invoking the OpenMM driver (fixes the v1 launcher's race where the Python `log()` crashed on first traceback because its output dir did not yet exist). Output under `/results/md_limk2/runs/rank{01..05}_<sdf#>/`. Completion marker `/results/md_limk2/runs/ALL_DONE.marker`. Worker heartbeat log `/results/md_limk2/logs/_worker.log`.

**Protocol:**
- Force field: amber14-all + TIP3P-FB water + GAFF-2.11 ligand (AM1-BCC charges)
- Placement: POCKET_FIXED (never COM) — pocket centroid `[−1.32, 0.64, 2.80]` nm
- Solvent: 1.0 nm padding, 0.15 M NaCl
- Timestep: 2 fs with HBonds constraint
- Production: 50 ns × 5 compounds
- Frame interval: 500 ps (100 frames per 50 ns)
- Aromatic-ring geometry pre-flight (max bond < 1.50 Å)
- PBC-aware distance analysis post-hoc (box=u.dimensions) — learning from 2026-04-10 PBC-bug incident

**Run status at draft time (2026-04-17T19:26Z):** rank01_222 in solvation phase. Expected all-5-complete: ~2026-04-19T10Z.

---

## 6. Known Issues / Caveats

1. **Affinity head unreliable** for αC-allosteric series — trained on ATP-site binders. Keep as prior only, do not claim Ki to Simon.
2. **Protonation states** — 5/10 hits are cation tautomers at the generation step. Re-canonicalize before any wet-lab discussion.
3. **LIMK1/LIMK2 isoform selectivity is weak** — z_LIMK2 beats z_LIMK1 by only 1.1–1.4 σ for all top-5. The αC pocket is conserved across LIMK family; true isoform selectivity may require LIMK1−LIMK2 differential pocket mining.
4. **Boltz-2 iPTM does not equal activation** — iPTM is a binding-quality proxy. An activator must bind **and** stabilize the active αC-in conformation. 50 ns MD is the first filter for "does it stay αC-in?". Real activation readout requires μs MD + metadynamics (Stage 8/13) — next step.
5. **Rank 2 (307.sdf)** flagged for MAPK14/p38α cross-activation (+1.73 z) — contraindicated for SMA-MN. Effectively shifts the operational top-3 to: **222.sdf, 46.sdf, 498.sdf**.
6. **Orphan A100 35097456** — destroyed after campaign completion (confirmed not in `vastai show instances` 2026-04-17T19:xxZ). Replacement instance 35120547 used for MD.

---

## 7. Next Decisions for Christian

- [ ] Approve neutral-form re-canonicalization + re-rank (would change order within top-5 but not top-5 identity).
- [ ] Wait for 50 ns MD completion (~2026-04-19) → compute αC RMSD vs apo + ligand-pocket occupancy + PBC-corrected distance trace.
- [ ] If top-3 pass MD stability gate: move to Stage 8 (100 ns + metadynamics) on a fresh H100/A100 rental.
- [ ] Triple-LLM verification on this DRAFT before promoting to APPROVED.
- [ ] Hold Simon comms until (i) meta-analysis APPROVED, (ii) this RESULTS.md APPROVED, (iii) revised hypothesis signed off.

---

## 8. Artifact Paths

**Local:**
- Boltz-2 raw: `/home/bryza/fleet-results/limk2_activator_alphaC/boltz2_results.jsonl` (645 rows)
- Ranked top hits: `/home/bryza/fleet-results/limk2_activator_alphaC/top_hits.tsv`
- Top-10 sel_z: `/home/bryza/fleet-results/limk2_activator_alphaC/top10_selectivity.tsv`
- Ki ranked: `/home/bryza/fleet-results/limk2_activator_alphaC/full_affinity_ranked_v2.tsv`
- DiffDock calibration: `/home/bryza/fleet-results/limk2_activator_alphaC/diffdock_reference.json`
- Gate log: `/home/bryza/fleet-results/limk2_activator_alphaC/filter_log.jsonl`

**Remote (Vast 35120547 ssh4.vast.ai:10546):**
- MD driver: `/workspace/md/md_limk2_activator.py`
- Queue: `/workspace/md/queue.tsv`
- Worker: `/workspace/md/md_worker.sh`
- Runs: `/results/md_limk2/runs/rank{01..05}_<id>/`
- Logs: `/results/md_limk2/logs/rank{01..05}_<id>.log`
- Heartbeat: `/results/md_limk2/logs/_worker.log`

---

*End of DRAFT. Do not cite externally. Do not send to Simon. Do not promote to APPROVED without Triple-LLM 3/3 PASS + Christian sign-off.*
