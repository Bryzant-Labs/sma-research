# SSH1 Phosphatase Inhibitor Virtual Screen — RESULTS (DRAFT)

**Campaign:** Kracher plan "Schritt vorwärts 2" — SSH1 inhibition raises p-cofilin, rescues LIMK2-loss-of-function cytoskeletal arm
**Status:** DRAFT — Phase 1 and Phase 2 complete; Phase 3 (Boltz-2 cross-phosphatase rescore) enqueued
**Agent-of-record:** successor to a5010743 (resumed 2026-04-17 after crash/GPU-reprovision)
**Simon-Comms-Gate:** HELD — DRAFT status, not for external share
**Triple-LLM gate:** pending (run after Phase 3 Boltz panel lands)

---

## 1. Mission recap

Hypothesis: in SMA motor neurons, LIMK2 is DOWN (meta-analysis, see `/home/bryza/sma-research/qms/meta_analysis/CORRECTED_SIGNATURE.md` — NOT the retracted UP direction).
- LIMK2 ↓ → p-Ser3-cofilin ↓ → F-actin severing ↑ → cytoskeletal dysfunction.
- **Orthogonal rescue:** inhibit the opposite reaction — the cofilin phosphatase **SSH1** (Slingshot-1) — to restore p-cofilin. This is a compensatory-axis strategy, not substrate replacement.

Caveat (explicit): the SMA-MN LIMK2 direction is under re-audit in the broader meta-analysis. If the direction inverts again, SSH1-inhibition rationale inverts too. This result stays DRAFT until the cofilin-axis direction is triple-verified.

No published SSH1-focused SMA program exists. Structure-based virtual screen, ChEMBL library.

---

## 2. Target set and calibration

| Target | UniProt | Domain used | Residues | Rationale |
|--------|---------|-------------|----------|-----------|
| **SSH1 (primary)** | Q8WYL5 | phosphatase | 214–459 (AF-Q8WYL5-F1) | cofilin phosphatase |
| SSH2 (off) | Q76I76 | phosphatase (auto-detected CX5R) | ~765–1014 | paralog |
| SSH3 (off) | Q8TE77 | phosphatase (auto-detected CX5R) | ~288–537 | paralog |
| DUSP6 (off) | Q16828 | DSP fold | ~168–381 | related DSP-fold control |

**Catalytic pocket (SSH1):** Cys393 SG / Arg399 CZ midpoint at `(-5.872, 1.155, 9.541)` Å, distance 4.87 Å, seq_gap +6 — matches the DSP-fold CX5R motif exactly. fpocket was unavailable on the runtime image; 3D-adjacency detection is authoritative here because the DSP fold has a single canonical catalytic Cys-Arg pair.

**Reference C_rel calibration (DiffDock):**

| Ref compound | Role | top_conf |
|--------------|------|----------|
| sanguinarine | natural SSH1 activator (weak binder, pocket-geometry probe) | −1.291 |
| SP-2509 | LSD1 inhibitor, off-pocket negative | −1.453 |
| BCI | DUSP6 inhibitor, on-family positive | −1.715 |
| **median** | **C_rel baseline** | **−1.453** |

Calibration note / known weakness: there is no published tight SSH1 ligand to use as a native co-crystal re-dock reference (compare the LIMK2 4TPT / LIMKi3 native re-dock we use elsewhere at C_rel = −0.521). The three references above form a weak, off-pocket-heavy baseline, making C_rel > 0 **permissive**. We flag this explicitly and compensate with the post-DiffDock PAINS + drug-likeness filter below plus the Phase 3 Boltz-2 cross-phosphatase z-panel.

---

## 3. Library and DiffDock screen (Phase 2, complete)

ChEMBL phosphatase-bioactive query, paginated (URL-doubling bug in `fleet_manager.chembl_fetch` fixed this session):

| Stage | n |
|-------|---|
| Raw ChEMBL fetch | 6 720 |
| RDKit + Lipinski + QED ≥ 0.5 | 6 298 |
| BBB pass (tPSA ≤ 90 Å², logP 1–4, HBD ≤ 3) | 3 568 |
| DiffDock-NIM input | 3 568 |
| DiffDock returned a top_conf | **414** |
| C_rel > 0 (vs median ref baseline) | 192 |
| C_rel > 0.5 | 90 |
| C_rel > 1.0 | 13 |

Errors in the DiffDock loop (reported as `errors=N` accumulator) are RDKit / conformer-gen rejections, not NIM crashes. Final-pass rate: 414 / 3568 = 11.6 %. `diffdock_ssh1_ranked.tsv` is the primary artifact.

### 3.1 Raw top-30 reality check → PAINS + drug-likeness filter applied

The raw top-30 by C_rel contains obvious calibration artifacts:

- CHEMBL660 (**adamantane-amine**, MW 151, no aromatic ring, no polar H-bond donor/acceptor for Cys393/Arg399) ranked #1
- CHEMBL9324 (**tetraethylammonium**, quaternary cation, no phosphatase pharmacophore) at +0.92
- Multiple naphthoquinones / 1,3-indandiones (CHEMBL590 = menadione / Vit K3, CHEMBL711, CHEMBL295316, CHEMBL15192) — PAINS redox cyclers
- Several repurposing hits with no mechanistic basis for SSH1 (CHEMBL42 = clozapine, CHEMBL31 / CHEMBL278255 / CHEMBL416755 = fluoroquinolone cluster, CHEMBL710 = finasteride)

These survive the raw DiffDock C_rel because our three reference compounds are not tight SSH1 binders, so the bar is low. We applied an RDKit post-filter (PAINS A+B+C + QED ≥ 0.40 + MW 200–500 + ≥ 1 aromatic ring + ≥ 12 heavy atoms + |formal charge| ≤ 2) to the 192 C_rel > 0 compounds.

| Filter stage | n |
|--------------|---|
| C_rel > 0 | 192 |
| PAINS hit | −10 |
| MW out of range 200–500 | −33 |
| < 1 aromatic ring | −6 |
| **Post-filter drug-like** | **143** |
| **top-100 → Phase 3** | **100** |

Artifacts at file:
- `/home/bryza/sma-research/qms/ssh1_vscreen/diffdock_ssh1_ranked.tsv` — raw 414 DiffDock
- `/home/bryza/sma-research/qms/ssh1_vscreen/diffdock_ssh1_filtered.tsv` — 143 post-filter
- `/home/bryza/sma-research/qms/ssh1_vscreen/top100_druglike.tsv` — Phase 3 input

### 3.2 Top 10 drug-like SSH1 hits (post-PAINS, pre-Boltz)

| Rank | ChEMBL | C_rel | QED | MW | SMILES | Note |
|------|--------|-------|-----|----|--------|------|
| 1 | CHEMBL279085 | +1.333 | 0.747 | 209 | `C=CCN1CCc2nc(N)sc2CC1` | allyl-amino-thiazole-piperidine |
| 2 | CHEMBL278488 | +1.252 | 0.816 | 218 | `CC1(c2ccccc2)OC(C(=O)O)=CC1=O` | α,β-unsat lactone (watch Michael) |
| 3 | CHEMBL7257 | +1.152 | 0.852 | 218 | `COc1ccc2[nH]cc(CCN(C)C)c2c1` | 5-methoxy-tryptamine-class |
| 4 | CHEMBL13852 | +1.132 | 0.834 | 216 | `c1ccc(C2CC2)c(OCC2=NCCN2)c1` | imidazoline-phenyl-cyclopropane |
| 5 | CHEMBL451 | +1.113 | 0.650 | 300 | `CNC1=Nc2ccc(Cl)cc2C(c2ccccc2)=[N+]([O-])C1` | chlordiazepoxide (benzodiazepine N-oxide) |
| 6 | CHEMBL269455 | +1.077 | 0.728 | 286 | `O=C1NC(=O)C2(N1)c1cc(F)ccc1-c1ccc(F)cc12` | fluorene-hydantoin, rigid |
| 7 | CHEMBL416755 | +1.051 | 0.885 | 261 | `CCn1cc(C(=O)O)c(=O)c2cc3c(cc21)OCO3` | oxolinic-acid (fluoroquinolone) |
| 8 | CHEMBL277775 | +0.999 | 0.696 | 204 | `c1ccc(C2CN3CCSC3=N2)cc1` | thiazoline-phenyl |
| 9 | CHEMBL280164 | +0.995 | 0.604 | 456 | `Cc1nnc2n1-c1sc(CCC(=O)N3CCOCC3)cc1C(c1ccccc1Cl)=NC2` | triazolo-thienodiazepine (olanzapine family) |
| 10 | CHEMBL18116 | +0.953 | 0.795 | 207 | `Cc1cccc(N2CC(CO)OC2=O)c1` | aryl-oxazolidinone |

Caveats:
- Rank 2 (CHEMBL278488) has a cross-conjugated enone; we will eye-ball it as covalent-warhead-adjacent and deprioritise unless Boltz rescore is strong.
- Rank 7 (CHEMBL416755 / oxolinic acid) is a fluoroquinolone; the C=O / β-keto-acid likely chelates the active-site divalent cation. We will watch the cross-phosphatase z-panel — if it hits all 4, it's a pan-DSP-fold chelator, not a selective SSH1 hit.
- Rank 9 (CHEMBL280164) is olanzapine-class benzodiazepine — likely a ligand-efficiency inflation artifact; MW 456 is at the drug-like boundary.
- Rank 5 (CHEMBL451) is chlordiazepoxide — repurposing possible but mechanism uncertain.

---

## 4. Phase 3 — Boltz-2 cross-phosphatase z-panel (queued, not yet run)

**Input:** 100 drug-like compounds × 4 targets (SSH1 catalytic, SSH2 cat, SSH3 cat, DUSP6) = 400 predictions.
**Batching:** 10 compounds per task → 40 `boltz2_affinity` fleet tasks (run_tag `ssh1vscreen_phase3_19850c`), priority 40, queued `2026-04-17 ~21:30Z`.
**Router:** `ROUTING["boltz2_affinity"] = ["HostedNIMWorker"]` (hosted NVIDIA Boltz-2 NIM). No Vast GPU burn for Phase 3.
**Metric (per Rule `rule-zscore-is-the-selectivity-metric.md`):**
- for each compound: compute `iptm_i` against each of the 4 targets, standardise across the 100-compound pool per target → `z_i = (iptm_i − mean_col) / std_col`
- `z_SSH1 > 0` = prefers SSH1
- `selectivity_z = z_SSH1 − mean(z_SSH2, z_SSH3, z_DUSP6) > 0` = net selective for SSH1
- Kracher target: `selectivity_z > 0.5` (margin 0.5 on the z-scale) for any hit to be called "SSH1-selective"

Phase-3 table will be filled in here when the 40 tasks complete. Monitor:

```bash
sqlite3 ~/fleet-dispatcher/queue.db "SELECT status, COUNT(*) FROM tasks WHERE id LIKE '%ssh1vscreen_phase3_19850c%' GROUP BY status"
```

---

## 5. State of the two GPU instances (2026-04-17 21:30Z)

### Instance 35137507 — H100 SXM France `sma-ssh1-rerun-fr`, ssh9:17506
- Primary SSH1 vscreen host. **Phase 1 + Phase 2 complete.** All artifacts rsync'd to `/home/bryza/sma-research/qms/ssh1_vscreen/`.
- Currently idle (GPU 0 %, 0 MiB). Decision: **leave idle** until Phase 3 NIM-side results are in. The next step that could use its compute is a MD refinement of the top-5 post-Boltz hits; firing a new fresh 5–10 k DiffDock screen right now would be premature because the c_rel baseline weakness (Section 2) would carry into the next pass.
- Follow-up (if Boltz-2 z-panel gives ≥ 3 selective hits): use this instance for 100 ns MD on SSH1 + top-3 leads.

### Instance 35097680 — H100 NVL Bulgaria `ssh1-vscreen-v2-20260416`, ssh8:17680
- **Label is misleading** — the SSH1 vscreen scaffold was prepped here 2026-04-16 21:45Z (`DEPLOY_READY` marker, 4 target PDBs, `chembl_phosphatase_docs.json`) but **no compounds were ever screened** (`screen_smiles.smi` = 0 bytes). The instance was then repurposed to PERP binder work (round-2 and round-3 pipeline now active: RFdiffusion + ProteinMPNN + batched Boltz-2 server on :8003, GPU 40 % util, tmux sessions `boltz2` + `perp_r3`).
- Verdict: **NOT redundant with France** — it's a different campaign. Do NOT destroy. Do NOT re-task.
- Optional follow-up: retro-rename the Vast label to `sma-perp-binder-rounds-bg` to remove confusion. (Not done — out of scope.)

---

## 6. Blockers / unknowns for Christian

1. **C_rel calibration gap.** No published SSH1 tight-binder for a native co-crystal re-dock. Our three-ref baseline is weak, which inflates the raw C_rel > 0 pool with PAINS / fragment artifacts (documented, filtered). If a ligand-bound SSH1 structure surfaces (PDB or in-house), we should re-run the 143-compound filtered pool with the corrected baseline.
2. **SMA-MN LIMK2 direction re-audit.** The whole rescue rationale depends on LIMK2 being DOWN (not UP) in SMA motor neurons. The meta-analysis audit is still active (see `/home/bryza/sma-research/qms/meta_analysis/`). If the direction flips back, this campaign inverts (we would screen for SSH1 *activators*, not inhibitors).
3. **Fluoroquinolone cluster (ranks 7, ~25, ~26).** Likely Mg²⁺-chelation artifact common to any phosphatase active site — we expect these to hit all 4 z-panel targets, confirming non-selectivity. If they *don't*, we need to look at the pocket geometry more carefully before believing it.
4. **Bulgaria label pollution.** The misleading `ssh1-vscreen-v2-20260416` label on 35097680 nearly caused a double-burn (resumed agent assumed a second independent SSH1 screen was running). Suggest adding a label-on-repurpose step to the fleet.

---

## 7. Next actions (autonomous, no further permission needed)

- [x] Phase 1 complete: structures, library, pocket, ref calibration
- [x] Phase 2 complete: 3 568 → 414 DiffDock, 192 C_rel > 0, 143 PAINS-clean
- [x] Phase 3 enqueued: 40 boltz2_affinity tasks (100 cpd × 4 tgt, batch 10) → HostedNIMWorker
- [ ] Phase 3 fill-in: top-10 post-Boltz selectivity table (auto-populate when tasks complete)
- [ ] Triple-LLM verify on this file once Phase 3 lands
- [ ] Flip DRAFT → APPROVED only after triple_llm 3/3 PASS
- [ ] **Simon-Comms-Gate stays HELD** regardless of result — per Kracher plan, only send when ≥ 1 compute track returns with a signal.
