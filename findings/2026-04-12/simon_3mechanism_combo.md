---
title: "Simon Memo — Three-Mechanism Combination Therapy for SMA"
date: 2026-04-12
author: Christian Fischer, Bryzant Labs
context: "Post-SMA Congress 2026 (Budapest, 11–14 March 2026) synthesis. Proposes a rational 3-mechanism combination that complements Fasudil rather than replacing it."
status: draft-for-review
---

# Three-Mechanism Combination Therapy for SMA

**One-line thesis:** Fasudil alone is a single-mechanism cytoskeletal rescue. The 2026 SMA Congress identified two orthogonal axes that the field has not yet integrated — NMJ-directed rescue (argenx / Sumner) and NRF2-driven redox rescue (Vrettou, Cologne). A rational three-mechanism combo (ROCK inhibitor + MuSK agonist + NRF2 activator) covers the three major failure modes of SMA motor units simultaneously and positions us as the cross-mechanism synthesis people rather than another LIMK/ROCK team.

---

## What the 2026 congress told us

1. **NMJ defects persist despite SMN-upregulating therapies.** (WS1, WS12, O27, O28 Vanhauwaert, O42 Donadio). argenx ARGX-119 — a MuSK agonist antibody — plus SMN2 splice modulator improves strength in SMA mice beyond what SMN restoration delivers alone.

2. **Metabolism and redox are the most druggable missing axes.** (Session 3; O16 Vrettou Cologne NRF2–KEAP1). Bardoxolone (CDDO-Me), omaveloxolone (RTA-408, FDA-approved 2023 for Friedreich ataxia), sulforaphane, and DMF are all validated NRF2 activators sitting idle for SMA.

3. **SMN-independent rescue is real.** (O24 Bruno CNR Trento, translation defects). The field is moving past "SMN restoration only" — multiple orthogonal mechanisms are emerging.

## The proposed 3-mechanism combo

| Mechanism | Drug | Target | Status | Evidence |
|---|---|---|---|---|
| **Cytoskeletal rescue** | Fasudil | ROCK2 → LIMK2 → Cofilin-2 | Off-patent, generic, CNS-penetrant | Bowerman 2012 SMA mouse + our ROCK2 apo 100 ns MD baseline (2026-04-12) |
| **NMJ stabilisation** | ARGX-119-like MuSK agonist *or* salbutamol as small-molecule bridge | MuSK kinase domain (agrin-LRP4-MuSK-DOK7 axis) | ARGX-119 in early clinic (argenx) | O28 Vanhauwaert 2026 congress |
| **Redox / anti-oxidant rescue** | CDDO-Me (bardoxolone) *or* omaveloxolone (Skyclarys, approved) | KEAP1 Kelch domain → NRF2 nuclear translocation | Skyclarys FDA-approved 2023 (Friedreich) | O16 Vrettou Cologne 2026 |

**Why this combination, not Fasudil alone:**

- Fasudil treats the **cytoskeletal-collapse** failure mode (actin rod accumulation via phospho-cofilin). It does not directly restore NMJ architecture and does not quench oxidative stress.
- MuSK agonism treats the **denervation** failure mode. It stabilises and re-maturates NMJs that denervate in SMA even under SMN-restored conditions.
- NRF2 activation treats the **oxidative-stress** failure mode. SMA motor neurons show elevated ROS, glutathione depletion, and mitochondrial dysfunction — all downstream of KEAP1-restrained NRF2.

Each of these compounds is either approved, in-clinic, or off-patent. None requires a new chemical matter program. The novelty is in the rational combination and in the mechanistic claim that they cover orthogonal failure modes.

## What Bryzant Labs delivers against this

1. **Docking + MD evidence for the combination on a shared LIMK2/ROCK2/MuSK/KEAP1 scaffold** (campaign launching 2026-04-12, results expected 2026-04-14).
2. **A scoring framework** that tells us which of the NRF2 activators (bardoxolone vs omaveloxolone vs sulforaphane vs DMF) is most likely to cross the BBB and not interact with Fasudil pharmacokinetically.
3. **A digital-twin** that projects what a 3-mechanism combo would do to 6MWT and MUNIX in a type-2/3 adult, using Capogrosso-lab spinal cord stimulation endpoints (O42 Donadio UPitt) as the comparator.
4. **A pre-registered hypothesis** against 3–6 month readouts in the SMAΔ7 mouse: NMJ integrity (endplate fragmentation), strength (Rotarod + grip), and survival.

## Why now

- SMA Congress 2026 just handed the field the argenx data. Anyone moving on this in the next 90 days owns the narrative.
- Skyclarys is already approved. A compassionate-use or investigator-initiated trial for SMA+Friedreich overlap patients is not a hypothetical.
- Our ROCK2 baseline MD (published 2026-04-12) is the reference that lets us interpret Fasudil-bound simulations as the first leg of this combo.

## What I need from Simon

1. **Your mechanistic red-team** on whether NMJ + NRF2 + ROCK actually cover orthogonal failure modes in SMA, or whether they collapse onto the same pathway.
2. **Your view on who in the field is closest to this combo framing** — argenx directly? Sumner lab? Is the CureSMA / FundAME portfolio already funding anything similar?
3. **Permission to fold Fasudil** into a combo narrative rather than presenting it as a standalone. This is a delta from the Feb 2026 plan.
4. **Introductions** to Vrettou (Cologne, O16) and to Vanhauwaert (argenx, O28). Both are probably one email away from you.

## What you will get back within 14 days

- Finished NMJ + NRF2 compute package (DiffDock Stage 3a + MD Stage 5 on top 10 of each)
- A written 3-mechanism combo hypothesis card linked to every piece of evidence in the platform
- A draft collaboration memo suitable for reaching out to argenx and to Vrettou

---

*Data and compute reproducibility:* Every compound in this memo is backed by a platform page on [sma-research.info](https://sma-research.info) and an open-data file on [github.com/Bryzant-Labs/sma-research](https://github.com/Bryzant-Labs/sma-research). Nothing private, nothing cherry-picked.
