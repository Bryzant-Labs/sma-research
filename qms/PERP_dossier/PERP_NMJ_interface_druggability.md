# PERP x NMJ Interface Druggability (fpocket)

**STATUS: DRAFT, 2026-04-17. Awaits triple_llm_verify 3/3 PASS. Not for external comms.**

---

## 1. What was run

For each locally-available PERP x partner AF2-Multimer prediction we (a) computed PERP-side interface residues within 5 A of the partner chain, (b) ran fpocket 4.0.2 on the complex, (c) identified pockets whose center lies within 8 A of an interface CA, (d) ranked those "interface pockets" by fpocket Druggability Score.

- fpocket 4.0.2 installed locally via `mamba install -n base -c bioconda fpocket -y`.
- Ranking via rank_001 per ColabFold ptm score.
- All computation on CPU, no GPU rental.

**Scope correction vs task brief.** The task brief said "12 completed PERP x NMJ multimers on TPU v6e-8 (+ 4 originals on v6e-4) = 16 total". What is actually on local disk:

| Location | Folds |
|---|---|
| `/home/bryza/gpu-fleet/results/perp_binders/perp_v6e8_multimer/` (v6e-8, synced) | 6 PERP heterodimer folds: PERP x DOK7, PERP x TP53, PERP x AGRN_LG3, PERP x RAPSN, PERP x SMN1, PERP x PERP (homodimer) |
| `/home/bryza/fleet-results/tpu_v6e4_backup/perp_multimer/` (v6e-4) | PERP monomer only, plus unrelated CHRNA1 and MUSK monomers (these are NOT PERP heterodimers) |
| `/home/bryza/fleet-results/tpu_v6e4_backup/nmj_multimer/` (v6e-4) | 4 NMJ-only monomers (AGRN_LG3, CHRNA1, MUSK_intracell, RAPSN) — no PERP present |

The remaining 12 PERP heterodimer folds listed in `gpu-fleet/campaigns/perp_interactome_v6e8/` (partners: AGRN full, CHAT, CHRND, CHRNE, CHRNG, CHRNA1_full, COLQ, DMD, LAMA4, LAMB2, LRP4_full, MUSK_full, UTRN) are either still running on the remote v6e-8 TPU tmux `perp_interactome` / `perp_full_follower` sessions or not yet rsync'd to local. **Ran fpocket on the 6 locally-available PERP heterodimer PDBs.**

---

## 2. Results table

| Partner | PERP interface residues (n) | PERP interface domains (by residue) | fpocket total pockets | Interface pockets (<8 A of iface CA) | Best interface drugg. score | Top pocket center (x,y,z) | Top pocket volume (A^3) | Recommendation |
|---|---|---|---|---|---|---|---|---|
| **PERP homodimer** (Q96FX8 x Q96FX8) | **35** | N-term(5), TM1(4), ECL1(6), ECL2(5), TM4(7), C-term(8) | 31 | **17** | **0.971** (pocket #16) | (-6.4, 12.2, -13.2) [approx, see raw JSON] | 1353 | **STRONG** small-molecule PPI-disruptor target. Interface spans the whole extracellular face + TM4 — druggability matches PF00822-clan homo-oligomer disruptors. Start here. |
| PERP x AGRN_LG3 | 18 | C-term(16), ICL(2) | 38 | 7 | **0.858** (pocket #34) | see raw JSON | 599 | **STRONG** druggable pocket, but the PERP interface is almost entirely C-terminal cytosolic tail — NOT extracellular. Pocket is between cytoplasmic faces of the two chains. LG3 is extracellular, so this iptm-low fold likely mis-orients AGRN's LG3 relative to PERP's topology. Treat as a **low-confidence positive** until re-folded with full-length AGRN and correct membrane orientation. |
| PERP x SMN1 | 15 | C-term(9), TM4(3), ECL2(1), ECL1(2) | 26 | 10 | **0.733** (pocket #22) | see raw JSON | 815 | PROMISING but biologically implausible: SMN1 is cytoplasmic, PERP is membrane — direct physical interaction is not expected. The high druggability score is likely a fold-artefact from AF2-Multimer trying to force an interface. De-prioritize unless biochemical evidence for PERP-SMN1 physical contact emerges. |
| PERP x DOK7 | 18 | C-term(14), N-term(4) | 19 | 6 | 0.273 (pocket #17) | see raw JSON | 1882 | MODERATE. Interface is all cytosolic (C-term + N-term). DOK7 is post-synaptic adapter with PH + PTB; engagement with PERP cytosolic tails is plausible. Druggability is modest (0.27). Worth orthogonal validation. |
| PERP x TP53 | 11 | C-term(11) | 35 | 7 | 0.198 (pocket #3) | see raw JSON | 807 | WEAK. Interface exclusively C-term. TP53 is transcription factor (nuclear); physical PERP-TP53 contact not expected (TP53 regulates PERP transcription, not protein). Expected negative. Druggability 0.20 is sub-threshold. |
| PERP x RAPSN | 13 | C-term(12), ICL(1) | 46 | 8 | 0.079 (pocket #6) | see raw JSON | 525 | WEAK. Almost entirely C-term interface. RAPSN is 43-kDa acetylcholine-receptor-clustering scaffold; cytoplasmic. Low druggability. Not a priority small-molecule target. |

Full machine-readable table at `/home/bryza/sma-research/qms/PERP_dossier/fpocket_out/fpocket_interface_druggability.json`. Pocket atom dumps at `fpocket_out/PERP_{partner}_out/pockets/pocket{N}_atm.pdb`.

---

## 3. Ranked druggability (interface-pocket only)

| Rank | Complex | Best interface drugg. score | Verdict |
|---|---|---|---|
| 1 | **PERP homodimer** | **0.971** | **Highest druggability. Disrupting the PERP-PERP homo-oligomer at the extracellular face is the cleanest pharmacological concept we can propose from the currently-available folds.** |
| 2 | PERP x AGRN_LG3 | 0.858 | High score but suspect fold geometry (AGRN LG3 should be extracellular, interface here is cytosolic). |
| 3 | PERP x SMN1 | 0.733 | High score but biologically implausible (SMN is cytosolic ribonucleoprotein; not a membrane-binder). |
| 4 | PERP x DOK7 | 0.273 | Modest, cytosolic interface. Plausible; orthogonal validation needed. |
| 5 | PERP x TP53 | 0.198 | Sub-threshold; expected negative. |
| 6 | PERP x RAPSN | 0.079 | Non-druggable (sub-threshold). |

**Interpretation.** The only complex with BOTH a high druggability score AND a biologically plausible interface composition (ECL1 + ECL2 + TM4, i.e. the extracellular face of PERP) is the **PERP homodimer**. This matches the published literature — PERP is known to homo-oligomerize at desmosomes (consistent with PMP-22/EMP/claudin clan members), and a pharmacological PPI-disruptor of the PERP-PERP homo-dimer is a viable concept.

**Caveat.** The PERP-homodimer ColabFold iptm at rank 1 was 0.290 (LOW-confidence). Boltz-2 re-scoring of the homodimer PERP:PERP interface (self-dock with our GenMol-seeded compounds) gave best lig_iptm 0.840 with best-seed SMILES `Cc1cccc(NC(=O)CN2C(=O)c3ccccc3C2=O)c1` — same scaffold that scored 0.944 against MUSK. This scaffold is NOT PERP-selective in our docking and would hit MUSK too. Any homodimer-disruptor program needs a selectivity panel including MUSK before wet-lab.

---

## 4. Structural/biological caveats

1. **iptm confidence.** Of the 6 heterodimers, rank-1 iptm values were in the 0.14-0.29 range (all LOW). fpocket druggability scores on low-iptm complexes should be treated as **hypothesis-generating, not hit-confirming**. The fold geometry might be wrong, and fpocket will detect pockets at any contact surface regardless of biological plausibility.

2. **C-terminal-tail dominance.** Five of six complexes have interfaces dominated by PERP's 22-aa cytosolic C-terminal tail (172-193). This is likely because the C-term is flexible/disordered (pLDDT 69) and AF2-Multimer preferentially docks partners against this flexible region. True biologically stable interfaces are more likely to involve the structured TM/ECL surface. The homodimer's C-term contribution (8/35) and the balanced domain coverage (N-term, TM1, ECL1, ECL2, TM4, C-term) is what makes it the most plausible.

3. **Membrane context missing.** None of the ColabFold multimer folds include a lipid bilayer. PERP is a 4-TM membrane protein; partners that approach from the cytosolic side (DOK7, RAPSN, SMN1, TP53) cannot in vivo touch PERP's extracellular face, and vice versa. Our interface detection script does not re-orient to a bilayer, so reported interfaces may be geometrically consistent but topologically impossible. Membrane-embedded MD would be the next correct layer of validation (deferred — requires GPU).

4. **Missing partners.** The 12 remaining PERP heterodimer folds (MUSK, LRP4, CHRNA1 full-length, CHRND, CHRNE, CHRNG, CHAT, COLQ, DMD, LAMA4, LAMB2, UTRN, AGRN full) are not yet locally available for fpocket analysis. When those complete on v6e-8 and rsync down, re-run this analysis as an addendum.

---

## 5. Recommendation summary

- **#1 priority target: PERP-PERP homodimer disruptor.** Druggability 0.971, largest interface (35 residues), balanced extracellular + TM coverage. Consistent with desmosome biology. Proceed with (a) focused GenMol seed generation at pocket #16 center coordinates, (b) Boltz-2 co-fold selectivity panel including MUSK, (c) orthogonal Boltz-2 of the homodimer interface with our existing 112 SMILES library to find selective scaffolds.
- **Watch list: DOK7.** If wet-lab IP/BioID confirms PERP-DOK7 physical interaction in SMA motor neurons, the modest-druggability cytosolic pocket (#17, drugg 0.27) is worth pursuing.
- **Skip for now**: RAPSN, TP53, SMN1, AGRN_LG3 — fold geometry either implausible or sub-threshold druggability.
- **Pending**: re-run on the 12 additional heterodimers once they rsync down from v6e-8.

---

## 6. Files produced

```
/home/bryza/sma-research/qms/PERP_dossier/fpocket_out/
  PERP_DOK7.pdb, PERP_TP53.pdb, PERP_AGRN_LG3.pdb, PERP_RAPSN.pdb,
  PERP_SMN1.pdb, PERP_homodimer.pdb          (input copies for reproducibility)
  PERP_{partner}_out/                         (fpocket workspace per complex)
    {partner}_info.txt                        (pocket-by-pocket stats)
    {partner}_out.pdb                         (complex with all pocket alpha spheres)
    pockets/pocket{N}_atm.pdb                 (atoms lining each pocket)
  PERP_{partner}.fpocket.log
  fpocket_interface_druggability.json         (unified machine-readable table)
```

---

DRAFT - update after triple_llm_verify PASS. No external comms.
