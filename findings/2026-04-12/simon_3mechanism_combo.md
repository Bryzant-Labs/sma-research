---
title: "Three-Mechanism Combination Therapy Framing for SMA"
date: 2026-04-12
author: Christian Fischer, Bryzant Labs
context: "Post-SMA Congress 2026 (Budapest, 11–14 March 2026) + Cure SMA 2025 Anaheim synthesis. Proposes a rational 3-mechanism combination that complements Fasudil rather than replacing it. Public version — the private collaborator memo lives off-repo."
status: UNDER_REVIEW 2026-04-17 (Fasudil rationale affected by Incident 001 retraction)
---

# Three-Mechanism Combination Therapy Framing for SMA

> ⚠️ **UNDER_REVIEW 2026-04-17** — the "Cytoskeletal rescue — Fasudil — ROCK2 → LIMK2 → Cofilin-2"
> row in the table below asserts Fasudil operates via ROCK2-hyperactivation rescue in SMA MN.
> A 2026-04-17 3-dataset meta-analysis inverts this premise: ROCK2 is pooled log2FC **−0.254**
> (DOWN, p=9.0e-5, I²=56%, 5/5 contrasts DOWN) in SMA MN. Pan-ROCK inhibition at the
> MN-intrinsic transcriptional layer is potentially contraindicated.
>
> The MuSK-agonist track and the NRF2-KEAP1 redox track are independent of the LIMK2 retraction
> and survive. Bowerman 2012's muscle-mediated Fasudil benefit also survives (it operates at
> muscle/protein-activity layer, not MN transcription).
>
> The 3-mechanism-combo framing **needs re-derivation** before external use. See
> `qms/CORRECTIONS_LOG.md` Incident 2026-04-17-001 + Audit-Event 002,
> `qms/meta_analysis/CORRECTED_SIGNATURE.md`, `qms/GOVERNANCE_AUDIT_2026-04-17.md` §U22.

**One-line thesis:** Fasudil alone is a single-mechanism cytoskeletal rescue. The 2026 SMA Congress (Budapest) and the Cure SMA 2025 Anaheim meeting together named two orthogonal axes the field has not yet integrated — NMJ-directed rescue (first-in-class MuSK agonist Fabs, exemplified by argenx ARGX-119) and NRF2-driven redox rescue (omaveloxolone / bardoxolone / sulforaphane). A rational three-mechanism combo (ROCK inhibitor + MuSK agonist + NRF2 activator) covers the three major failure modes of SMA motor units simultaneously and positions Bryzant Labs as a cross-mechanism synthesis group.

---

## What the 2026 congress told us

1. **NMJ defects persist despite SMN-upregulating therapies.** Multiple talks (WS1, WS12, O27, O28, O42) converge on the same conclusion. First-in-class MuSK agonist Fabs (exemplified by argenx ARGX-119) plus SMN2 splice modulators improve strength in SMA mice beyond what SMN restoration delivers alone.

2. **Metabolism and redox are the most druggable missing axes.** Session 3 (O16, Cologne, NRF2–KEAP1 in SMA liver). Bardoxolone (CDDO-Me), omaveloxolone (RTA-408, Skyclarys — FDA-approved 2023 for Friedreich ataxia), sulforaphane, and DMF are all validated NRF2 activators sitting idle for SMA.

3. **SMN-independent rescue is real.** Translation-defect-rescue data from CNR Trento (O24) suggests splicing is no longer the only mechanism the field should be pursuing.

## The proposed 3-mechanism combo

| Mechanism | Drug | Target | Status | Evidence |
|---|---|---|---|---|
| **Cytoskeletal rescue** *(⚠️ UNDER_REVIEW 2026-04-17)* | Fasudil | ~~ROCK2 → LIMK2 → Cofilin-2 (MN-intrinsic rescue)~~ — **direction-inverted per 3-dataset meta**: ROCK2 is DOWN in SMA MN (pooled −0.254, p=9.0e-5). Muscle-layer mechanism (Bowerman 2012) survives as independent rationale. | Off-patent, generic, CNS-penetrant | ~~Bowerman 2012 SMA-mouse MN-rescue framing~~ — re-frame as muscle-layer only; + our ROCK2 apo 100 ns MD baseline (2026-04-12) remains valid as structural/apo reference |
| **NMJ stabilisation** | MuSK agonist Fab *or* salbutamol as small-molecule bridge | MuSK kinase domain (agrin-LRP4-MuSK-DOK7 axis) | Phase 1 complete for first-in-class Fab | Congress 2026, O28 |
| **Redox / anti-oxidant rescue** | CDDO-Me (bardoxolone) *or* omaveloxolone (Skyclarys, approved for Friedreich ataxia) | KEAP1 Kelch domain → NRF2 nuclear translocation | FDA approval for an adjacent inherited neurodegeneration | Congress 2026, O16 |

**Why this combination, not Fasudil alone:**

- Fasudil treats the **cytoskeletal-collapse** failure mode (actin rod accumulation via phospho-cofilin). It does not directly restore NMJ architecture and does not quench oxidative stress.
- MuSK agonism treats the **denervation** failure mode. It stabilises and re-maturates NMJs that denervate in SMA even under SMN-restored conditions.
- NRF2 activation treats the **oxidative-stress** failure mode. SMA motor neurons show elevated ROS, glutathione depletion, and mitochondrial dysfunction — all downstream of KEAP1-restrained NRF2.

Each of these compounds is either approved, in-clinic, or off-patent. None requires a new chemical matter program. The novelty is in the rational combination and in the mechanistic claim that they cover orthogonal failure modes.

## The hidden cross-connection: p53 cascade

An additional existing-platform finding sharpens the combo's rationale. The claim graph already contains the evidence that *axonal pathology runs through a cascade: p38 MAPK → Mdm2-mediated p53 degradation → ROCK activation* (platform claim #46341). That cascade places ROCK downstream of p53, which means Fasudil already quietly rescues p53-driven motor neuron pathology — without having been proposed for that purpose.

The 2026 cerebellar pathology data (Gerstner 2025 Brain, PMID 40585211) shows Purkinje cells die via the **same** p53-dependent mechanism. So the same three-drug cascade (Fasudil at ROCK, pifithrin-α at p53, MW150 at p38) covers cerebellar rescue by default — with zero additional compute.

## What Bryzant Labs delivers against this framing

1. **Docking + MD evidence for the combination** on a shared LIMK2 / ROCK2 / MuSK / KEAP1 scaffold (campaigns launched 2026-04-12, results expected 2026-04-14).
2. **A scoring framework** that tells us which of the NRF2 activators (bardoxolone vs omaveloxolone vs sulforaphane vs DMF) is most likely to cross the BBB and not interfere pharmacokinetically with Fasudil.
3. **A digital twin** projecting what a 3-mechanism combo would do to 6MWT and MUNIX in a type-2/3 adult, using published SMA motor endpoints as the comparator.
4. **A pre-registered hypothesis** against 3–6 month readouts in the SMN∆7 mouse: NMJ integrity (endplate fragmentation), strength (Rotarod + grip), survival, and — new as of today — cerebellar Purkinje density.
5. **A cross-connection engine run** that surfaces where the 3-mechanism combo intersects with cerebellar, translation-defect, and myostatin-adjunct data coming out of 2025–2026.

## Open scientific questions

1. Do NMJ + NRF2 + ROCK really cover orthogonal failure modes in SMA, or do they collapse onto the same pathway through p53 / oxidative stress?
2. At what dose ratios does the combo produce the strongest effect without PK interference?
3. How does the combo interact with SMN-restoring therapy (nusinersen / risdiplam / onasemnogene abeparvovec)?
4. Does the p53-cascade framing extend Fasudil's rationale to cerebellar rescue, and if so what mouse cohort answers it fastest?

---

*Data and compute reproducibility:* Every compound in this framing is backed by a platform page on [sma-research.info](https://sma-research.info) and an open-data file on [github.com/Bryzant-Labs/sma-research](https://github.com/Bryzant-Labs/sma-research). Nothing private, nothing cherry-picked.

*Note:* This document is the public-facing scientific framing. Any discussion of specific individuals, collaborators, or outreach targets lives in private notes, not in this repository.
