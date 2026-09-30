# Corrections and negative results (DRAFT for sma-research.info)

> Draft text for a public page, e.g. `/corrections/` and a link from About.
> Every line is taken from `README.md` or `qms/CLAIMS_REGISTRY.md` / `qms/CORRECTIONS_LOG.md`.
> Christian to check wording and dates before publishing.

All results on this platform are computational predictions or hypotheses. We publish corrections with the same prominence as findings and never edit them silently.

## Retracted claims

| Date | Claim | What the data showed |
|---|---|---|
| 2026-04-17 | LIMK2 is up-regulated 2.81-fold in SMA motor neurons | Meta-analysis of GSE290979, GSE302774 and GSE87281 shows LIMK2 slightly down or model-dependent, not up. The original source was a placeholder. |
| 2026-04-17 | CFL2 is disease-specific (up in SMA, down in ALS) | SMA side pooled log2FC +0.002 (p = 0.96), direction mixed across datasets. |
| 2026-04-17 | CORO1C is down 1.77-fold | Re-derivation gives pooled log2FC -0.025 (p = 0.75), not significant. |
| 2026-04-17 | The ROCK-LIMK2-CFL2 axis is hyperactive in SMA motor neurons | LIMK2, ROCK2 and CFL1 are not up in the same datasets. Expression is not activity, so the axis stays a hypothesis. |
| 2026-04-17 | MDM2 "RING allosteric activator" compounds (Arm 4) | 0 of 20 compounds passed the pre-registered docking gates, and a generic non-binder scored higher than every candidate. |
| 2026-04-17 | LIMK2 alpha-C compound library | Retracted after an affinity audit; see the corrections log. |

## Negative and reclassified results

- Fasudil scaffold hop: 0 of 20 variants were LIMK2-selective.
- 4-aminopyridine does not bind CORO1C therapeutically; it is reclassified as a Kv-channel compensator.
- AF3 high-confidence kinase pairs may model kinase-substrate encounter complexes rather than stable protein-protein interactions.
- 0 % of the molecular dynamics runs show ligand residence time.

## How to read scores on this site

- **ipTM is a structure-confidence score, not an affinity.** Against ChEMBL Ki data for four kinases, Boltz-2 ipTM explains little of the variance (R-squared 0.007 to 0.307, 20 compounds per kinase). ipTM saturates between about 0.88 and 0.99 for kinase pockets.
- **A high score from one method is a hypothesis.** Hits need an independent second method before they are discussed as leads.
- **Confidence values on automatically extracted claims are not calibrated probabilities.**
- **"Validated" on this platform never means experimentally validated** unless a wet-lab measurement is cited.
