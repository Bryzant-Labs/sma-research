# ATLAS TOP-25 Extended — Cross-Connection Analysis
**Date**: 2026-04-17T16:33:26Z

For each fired target, biological / mechanistic connections to our existing 4-arm campaigns (LIMK2-activator, SSH1-inhibitor, PERP-binder, NMJ atomic complex) and to other atlas targets.

## EP400
- TIP60 complex ATPase — directly upstream of KAT5. Dual EP400/KAT5 targeting may synergize.
- SWI/SNF chromatin remodeler; loss-of-function in SMA likely via snRNP-chromatin coupling.

## PEAK1
- Pseudokinase; no canonical catalysis. Scaffold function for SRC/FRK. Low druggability (0.024).
- Possibly connects to ROCK/LIMK axis via pseudokinase-SRC scaffold. Speculative.

## KAT7
- HBO1/KAT7 H3K14ac at origins of replication. MN post-mitotic but may regulate SMN1/2 enhancer landscape.

## RNF213
- AAA+ ATPase E3 ubiquitin ligase. Novel target class; no direct SMA link yet but chromosomal fragility axis.

## EHMT2
- G9a inhibitors (UNC0642, BIX-01294) exist — our PXM output should match scaffold space and add MN-specific selectivity.
- Cross-link: BRD4 + G9a PPI; if KAT6B bromodomain hits also hit G9a, dual mechanism.

## KAT6A
- MYST HAT family overlap with KAT6B (atlas rank 10, fired top5). Paralog selectivity opportunity.
- KAT6A inhibition → H3K14ac loss → chromatin compaction. SMA MNs show global transcriptional dysregulation (Cajal body loss). Possible rescue axis.

## KAT5
- TIP60/KAT5 acetylates p53 K120 activating apoptosis. PERP (our arm-4 campaign) is downstream of p53. Synergy lead: KAT5 activator could amplify PERP-mediated MN rescue.
- TIP60 + TP53 + PERP = direct biological triangle. Check DiffDock vs PERP + KAT5 dual modulator.

## KMT5B
- SUV420H1 H4K20me2/3 heterochromatin. SMA MN show loss of heterochromatin integrity (our LIMK2 axis).
- A-196 (pan-SUV420) exists; our PXM output should selectivity-differentiate KMT5B vs KMT5A/C.

## EHMT1
- GLP/EHMT1 co-operates with EHMT2/G9a. If we hit EHMT1 we will likely hit EHMT2 (90% pocket identity). Cross-selectivity matters.
- H3K9me2 mark represses neurogenesis genes. SMA MN transcriptome has aberrant H3K9me2 patterns (Finkel 2020 data).

## Cross-target biological triangles
- **TIP60 axis**: EP400 (ATPase) + KAT5 (HAT) + PERP (p53 downstream) — triple dual-modulator possibility.
- **MYST paralog cluster**: KAT5 + KAT6A + KAT7 (+ KAT6B from top5) — selectivity matrix.
- **H3K9 methylation axis**: EHMT1 + EHMT2 — obligate heterodimer; single compound likely hits both.
- **SET-domain cluster**: EHMT1 + EHMT2 + KMT5B — cross-reactivity risk; selectivity critical.
