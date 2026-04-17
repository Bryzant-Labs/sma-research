# PERP — Relevance to the Neuromuscular Junction

**STATUS: INTERNAL draft, 2026-04-17. All numeric values traceable to `/home/bryza/fleet-results/perp_multimer/` (v6e-4) and `/home/bryza/gpu-fleet/results/perp_binders/perp_v6e8_multimer/` (v6e-8).**

---

## 1. The gap in the public literature

PubMed counts (2026-04-17):

| Query | # hits |
|---|---|
| `PERP AND motor neuron` | 2 |
| `PERP AND neuromuscular` | 0 |
| `PERP AND "spinal muscular atrophy"` | 1 |
| `PERP AND "neuromuscular junction"` | 0 |
| `PERP AND muscle` | 26 (mostly skeletal-muscle oxidative-stress, not NMJ) |

**Published NMJ-specific PERP biology = zero papers.** The single PERP / SMA paper is Simon 2022 (PMID 36419936), which motivates but does not quantify the PERP-at-NMJ hypothesis. Simon's unpublished observation is therefore literally novel.

---

## 2. NMJ proteins we have folded with PERP (v6e-8 multimer campaign)

Folder: `/home/bryza/gpu-fleet/results/perp_binders/perp_v6e8_multimer/`
Method: ColabFold / AF2-Multimer v3 on TPU v6e-8, 3 ranks per complex.

**Completed PERP-heteromer folds (rank_001 scores):**

| Complex | iptm | ptm | Mean pLDDT | Interpretation |
|---|---|---|---|---|
| PERP : PERP (homodimer) | 0.290 | 0.560 | 74.0 | Low-confidence interface; PERP homodimer is reported in desmosomes but our AF2 run does not confidently recover it. Try longer seeds or Boltz-2 multimer. |
| PERP : RAPSN | 0.240 | 0.700 | 85.7 | Low iptm but RAPSN monomer pLDDT is high — interface is not confidently modelled. RAPSN is the AChR-clustering scaffold at the post-synapse — highest-priority NMJ partner. |
| PERP : DOK7 | 0.210 | 0.380 | 57.2 | Low pLDDT for the complex — DOK7 monomer may be partially disordered. Re-run with DOK7 constructs restricted to the PH-PTB tandem. |
| PERP : AGRN (LG3 domain) | 0.150 | 0.460 | 70.6 | Low iptm. LG3 is the LRP4-binding fragment; PERP may not directly interact with AGRN. Keep as negative control for comparison. |
| PERP : TP53 | 0.170 | 0.410 | 66.2 | Low iptm but unsurprising — PERP is downstream of TP53 transcriptionally, direct physical interaction is not expected. Good negative control. |
| PERP : SMN1 | 0.140 | 0.380 | 54.0 | Low iptm; SMN1 is in the cytoplasm / Cajal bodies, PERP is membrane. Negative control consistent with biology. |

All six folds: **iptm < 0.3 = LOW confidence for a binding interface**. This is not a failure of the pipeline — it is a useful negative result:
- No confident heteromeric interface is predicted between PERP and any of the NMJ scaffolding proteins tested.
- The most interesting residual signal is **PERP : RAPSN ptm 0.70 + pLDDT 86** — high monomer confidence but no firm interface. This is the partner we would prioritize for longer-seed AF2 and Boltz-2 follow-up, because RAPSN sits at the post-synaptic AChR cluster, and Simon's unpublished NMJ PERP observation is most-plausibly a post-synaptic phenomenon.

**Why the campaign continues to be valuable even with low iptm.** AF2-Multimer iptm is notoriously biased against transmembrane-protein complexes (MSA pairing is poor, lipid context missing). A low iptm does NOT exclude interaction; it says "not confidently predicted". The complementary strategy is Boltz-2 multimer (better at membrane proteins) and IP / co-IP wet-lab validation — both currently queued.

---

## 3. Pending v6e-8 partners (14 total NMJ partners in campaign)

Source: `/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/fetch_and_queue.sh`
Total partner list (with UniProt accessions hard-coded in the shell script):

| # | Partner | UniProt | NMJ role | Status |
|---|---|---|---|---|
| 1 | DOK7 | Q18PE1 | MuSK activator | DONE (iptm 0.21) |
| 2 | RAPSN | Q13702 | AChR clustering | DONE (iptm 0.24) |
| 3 | AGRN | O00468 | pre-synaptic organiser, binds LRP4 | DONE (iptm 0.15, LG3 only) |
| 4 | TP53 | P04637 | transcriptional regulator (negative control) | DONE (iptm 0.17) |
| 5 | SMN1 | Q16637 | SMA gene (negative control) | DONE (iptm 0.14) |
| 6 | homodimer | Q96FX8 (x2) | desmosome oligomer | DONE (iptm 0.29) |
| 7 | UTRN | P46939 | dystrophin homolog, post-synaptic | PENDING |
| 8 | DMD | P11532 | dystrophin, post-synaptic | PENDING |
| 9 | CHRNG | P07510 | fetal AChR γ-subunit | PENDING |
| 10 | CHRND | Q07001 | AChR δ-subunit | PENDING |
| 11 | CHRNE | Q04844 | adult AChR ε-subunit | PENDING |
| 12 | CHAT | P28329 | choline acetyltransferase, pre-synaptic | PENDING |
| 13 | COLQ | Q9Y215 | AChE scaffold at the synaptic cleft | PENDING |
| 14 | LAMA4 | Q16363 | basal-lamina, synaptic cleft | PENDING |
| 15 | LAMB2 | P55268 | basal-lamina, synaptic cleft | PENDING |

**Prioritization rationale.**
- **Post-synaptic AChR cluster (RAPSN, DOK7, MUSK, LRP4)** — Simon's NMJ-PERP observation is most-plausibly a post-synaptic phenomenon; these are the highest-priority targets.
- **CHRNG / CHRND / CHRNE** — if PERP interacts with one specific AChR subunit, that is a tractable structural hypothesis.
- **CHAT + COLQ** — pre-synaptic and cleft proteins, useful negative controls.
- **UTRN / DMD / LAMA4 / LAMB2** — dystrophin-glycoprotein complex + basal lamina; if PERP interacts here, the story shifts from "apoptosis effector at the NMJ" to "structural stabilizer at the post-synaptic membrane".

v6e-8 fold speed is ~10–15 min / complex. Full 14-partner panel expected ≤ 4 hours once the slice is freed.

**Missing from the list** (task mentioned but not yet queued): MUSK, LRP4, CHRNA1. Note however that Boltz-2 multimer has been run for PERP × MUSK, PERP × LRP4, PERP × CHRNA1, PERP × PERP (see `PERP_compute_status.md` §3). Those are the 40 Boltz-2 entries in `fleet-results/boltz2_perp_*`. **Recommendation: add MUSK + LRP4 + CHRNA1 to the v6e-8 AF2 queue for completeness.**

---

## 4. Open questions Simon might want us to answer

These are framed as compute-answerable research questions, ordered by decreasing priority.

### Q1. Does PERP physically interact with RAPSN, DOK7, MUSK, LRP4, or any AChR subunit?

Method on hand: AF2-Multimer (v6e-8) + Boltz-2 multimer. Expected turnaround: hours-to-days.
Evidence needed for a confident "yes": iptm > 0.6 (at least two seeds), plus a plausible interface made by Loop 1 / Loop 3 of PERP (the two extracellular loops).
Current status: no interaction in the first 6 folds above. 14 more partners pending.

### Q2. Is PERP-DOWN in SMA iPSC-MN (our meta-analysis: log2FC −0.41 Hb9-iMN, −0.74 iN) consistent with PERP-DOWN at the NMJ in Simon's system?

Method: cross-check Simon's unpublished PERP IHC / western signal against our meta log2FC. If both show DOWN, that is a convergent transcriptomic-to-proteomic result.
Compute we can do: none beyond the meta-analysis above. **This is a Simon-side question.**

### Q3. Would a PERP-stabilizing small molecule (molecular glue, DUBTAC) rescue NMJ function?

Rationale: PERP is ubiquitinated by CRL4-DCAF13 (PMID 35178836) and degraded; if SMA MN has low PERP, a molecule that blocks the E3-PERP interaction or recruits a DUB to PERP could rescue PERP protein level.
Compute we can do: DUBTAC / molecular-glue design from the AF2 PERP model + CRL4 / DCAF13 structures.
Status: **not started**. Would require a dedicated campaign.

### Q4. Can we design a PERP-selective small-molecule binder targeting Loop 1 of the monomer?

Method: RFdiffusion binder design on AF2 PERP model, filter to Loop 1 binding, then ProteinMPNN sequence-recovery, then Boltz-2 affinity.
Compute we can do: already have 112 tetrahydropyran + sulfonamide seeds queued (`/home/bryza/gpu-fleet/results/perp_binders/perp_binder_seeds.jsonl`); 39 Boltz-2 runs executed (see `PERP_compute_status.md` for affinity summary).
Status: **in progress**. This is our most developed compute track.

### Q5. Does Loop 1 sequence conservation across species predict NMJ-specific role?

Method: align PERP orthologs across vertebrates (human / mouse / rat / zebrafish / frog). Loop 1 conservation would tell us whether the predicted drug-target surface is species-specific or deeply conserved.
Compute we can do: multiple-sequence alignment + conservation score. Easy, ~1 hour.
Status: **not started**.

### Q6. Does PERP function at the NMJ involve desmosome-like junctional structures?

Context: PERP's known biology is desmosome / epithelial adhesion. NMJ has cell-cell contacts between motor nerve terminal and muscle endplate via a basal-lamina bridge — not a classical desmosome. Could PERP have re-purposed the desmosome-scaffolding role to stabilize the post-synaptic membrane?
Compute we can do: search for desmoplakin / desmocollin-like scaffolding partners in Simon's lab's RNA-seq (if available).
Status: **depends on Simon's system**.

---

## 5. Summary

- No published NMJ-specific PERP biology exists — our computational work is genuinely first-in-class in this space.
- Our AF2-Multimer v6e-8 campaign has folded 6 PERP-heteromers so far; all show low iptm (< 0.3). No confident NMJ interaction predicted yet. 14-partner panel is in progress.
- PERP transcript is DOWN in the two best-powered human iPSC-MN SMA contrasts (GSE302774 Hb9-iMN padj 3.5e-3, iN padj 6.5e-19), consistent with a potential NMJ-PERP loss-of-function.
- Therapeutic angle: PERP **stabilization** (molecular glue / DUBTAC targeting DCAF13-PERP) could rescue PERP protein level if Simon's IHC / western confirms the DOWN direction at the protein level at the NMJ.
- We need Simon's per-cell-type, per-time-point PERP protein data to resolve whether our transcriptomic signal translates; that is the wet-lab side of the question.

*End of NMJ-relevance section. All scores traceable to `raw/` PDB + JSON files and to `/home/bryza/gpu-fleet/results/perp_binders/perp_v6e8_multimer/`.*
