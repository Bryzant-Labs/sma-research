# ROCK–LIMK2–CFL2 Axis

> **⚠️ UNSOURCED 2026-04-17** — CFL2 "disease-specific (UP in SMA, DOWN in ALS)" Claim hat keine primäre Datenquelle im Repo. Verifikation gegen GSE302774 + ALS-Referenzdataset ausstehend.


> **⚠️ RETRACTED 2026-04-17** — Die Claim "LIMK2 +2.81× hoch in SMA Motoneuronen" wurde zurückgezogen. 
> Re-Analyse aus zwei verifizierten SMA-Datasets (GSE290979, GSE302774) zeigt LIMK2 ist **mild DOWN** in SMA MN (nicht UP). 
> Die ROCK-LIMK2-CFL2 "core therapeutic axis" Claim wird überprüft — alle Downstream-Hypothesen (Fasudil-Rationale etc.) sind betroffen.
> Details: `qms/CORRECTIONS_LOG.md` Incident #2026-04-17-001.


**Status**: **UNDER_REVIEW** (see retraction banner above — previously asserted VALIDATED, that assertion does not survive the 2026-04-17 meta-analysis; Incident 001)
**Priority**: CRITICAL (core therapeutic axis for SMA — rationale RETRACTED pending re-derivation)
**Started**: 2026-03-24

## Hypothesis (RETRACTED 2026-04-17)

> SMN deficiency → ROCK2 hyperactivation → LIMK phosphorylation → cofilin inactivation → actin-rod formation → axonal-transport block → motor-neuron death

The "ROCK2 hyperactivation" premise is inverted per the corrected signature. ROCK2 pooled
log2FC = **−0.254** (95% CI [−0.381, −0.127], I²=56%, p=9.0e-5, k=5) — robustly DOWN in SMA MN.
Downstream ("LIMK phosphorylation → cofilin inactivation") is not directly testable at the
transcriptional layer and requires protein-level kinase-activity assays to revise.

## Evidence (all audited 2026-04-17 — see `qms/CORRECTIONS_LOG.md` Audit-Event 002)

- LIMK2: **RETRACTED** (see `qms/CORRECTIONS_LOG.md` Incident 001). Direction is
  model-system-dependent per `qms/meta_analysis/CORRECTED_SIGNATURE.md` — DOWN in
  iPSC-Hb9-iMN (padj 2.3e-12) and iN (padj 1.4e-63), UP in SH-SY5Y shSMN (padj 3.8e-6),
  DOWN-tendency in GSE290979 organoid (padj 0.37 NS). Pooled log2FC = −0.20 (I²=98%, NS).
  Cite per-contrast, never pooled; never cite the retracted +2.81×.
- CFL2: **UNSOURCED** "disease-specific: UP in SMA, DOWN in ALS" — meta pooled CFL2
  log2FC = +0.002 (I²=28%, NS). No primary ALS reference dataset was ever cited.
  Correction pending re-derivation from a named ALS dataset.
- PFN2: per-contrast +0.283 log2FC in GSE302774 Hb9-iMN (padj 1.7e-16) and +0.362 in
  GSE302774 iN (padj 2.1e-20) are significant, BUT pooled meta = +0.025 (I²=97%, NS),
  model-dependent (DOWN in GSE87281 SH-SY5Y shSMN padj 2.8e-6). **Do NOT cite as
  "MN-enriched" pooled** — cite per-contrast with explicit heterogeneity caveat.
- Zero competitors in the LIMK2-selective drug-space globally — chemistry-side
  observation, survives the retraction. Not a disease-axis claim.

## Compounds characterized

| Compound | Binding | Verdict |
|---|---|---|
| Fasudil | ROCK1/2 inhibitor (approved JP) | Muscle-mediated, not neuroprotective (Bowerman 2012) |
| bbb5 (`genmol_119_bbb_5`) | Dual LIMK2/ROCK1 | See [`../bbb5_dual_LIMK2_ROCK1/`](../bbb5_dual_LIMK2_ROCK1/) |
| 14 PocketXMol hits | LIMK2-selective (margin > 0.3) | See [`../PocketXMol_LIMK2_selective/`](../PocketXMol_LIMK2_selective/) |

## Contents

- `data/md_results_summary.json` — Aggregated MD run summary
- `md-simulations-2026-04-10/` — 2026-04-10 holo/reference simulations for LIMK1, LIMK2, ROCK1, ROCK2 with BMS5, LIMKi3, bbb5, Fasudil, and genmol_119_bbb_0

## Related findings

- [`../../findings/2026-04-09/FINDING_2026-04-09_bbb5_dual_LIMK2_ROCK1.md`](../../findings/2026-04-09/FINDING_2026-04-09_bbb5_dual_LIMK2_ROCK1.md)
