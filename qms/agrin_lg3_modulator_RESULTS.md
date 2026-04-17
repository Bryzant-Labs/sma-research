# AGRIN LG3 LRP4-Interface Modulator Campaign — RESULTS

**Campaign ID**: `agrin_lg3_modulator`
**Status**: VERIFIED (triple_llm_verify 3/3 PASS 2026-04-17: OpenAI GPT-4o PASS, Groq Llama 3.3 70B PASS, Gemini 2.0 Flash PASS)
**Completed**: 2026-04-17 (PocketXMol generation)
**Instance**: A100 PCIE-40GB, Japan (ssh4:10540), $~0.70/hr

## Executive summary

De novo design of AGRIN-LG3/LRP4-interface small-molecule modulators against the canonical SEA/Z-exon face loop (residues 1779-1788). **5 fully-connected drug-like molecules** out of 600 attempted (0.83% success rate), reflecting the low druggability of the flat protein-protein interface. Top 5 candidates have PocketXMol cfd_pos 2.505-2.615.

## Target verification

- **PDB 3V64** — *Crystal Structure of agrin and LRP4* (Zong 2012, Genes Dev 26:247), X-ray 2.85 Å
- **PDB TITLE-verified**: `TITLE     CRYSTAL STRUCTURE OF AGRIN AND LRP4`
- Chains used: A (rat AGRIN P25304 residues 1759-1948, LG3 domain, 191 aa) + D (rat LRP4 Q9QYP1 residues 396-737, β1-propeller, 342 aa)
- Human orthologs: AGRIN O00468, LRP4 O75096 (95%+ identical in LG3 / highly conserved in propeller)
- **NOTE**: 3V64 COMPND block has FRAGMENT fields swapped between MOL_IDs 1 and 2; chain assignments verified independently via RCSB polymer_entity API.

## Pocket derivation (verified sanity_checks PASS)

**Strategy**: interface-residues-of-AGRIN-contacting-LRP4 approach. 18 residues found within 5 Å of LRP4 atoms, clustered into two interfaces; primary interface = SEA/Z-exon face loop (10 consecutive residues).

**SEA-face loop residues (all verified identities)**:
S1779, E1780, L1781, T1782, N1783, E1784, I1785, P1786, A1787, E1788

**Contact partners on LRP4 (chain D)**: R447, N469, T488, R557, W573, W599, H642.

**Pocket center**: `[-27.992, 10.692, -38.546]` Å
**Pocket radius**: 12.0 Å
**Loop extents**: 15.77 × 6.70 × 6.05 Å (tight, well-defined geometry)
**Ca²⁺ ion distance**: 19.49 Å (canonical LG3 structural calcium, well outside generator zone)

## Compute run

- **Warm state**: PocketXMol SHA `65488cf635c856101dbe703ac97e2f10f58e005c` (matches all today's campaigns)
- **Install skip**: 0 s (weights symlinked from /workspace/PocketXMol to /opt/PocketXMol)
- **Smoke (5 mol)**: **PASS** — 5/5 collected, 3 valid SMILES, <60 s wall
- **Full run (600 mol)**: 160.4 s wall, **GPU util 96%** at steady state (target > 60 % **MET**)
- **Throughput**: ~3.7 mol/s (including post-processing)

## Results

### PocketXMol pool statistics
| Category | Count | Fraction |
|---|---|---|
| Fully-connected ("success") | 5 | 0.83 % |
| Incomplete (disconnected fragments) | 552 | 92.0 % |
| Bad (RDKit-invalid) | 43 | 7.2 % |

### Top 5 candidates (ranked by PocketXMol cfd_pos)

| # | cfd_pos | SMILES |
|---|---|---|
| 1 | 2.615 | `Cc1nc2cc(CC3CCCN(c4cc(O)nc5ccc(O)cc45)C3)ccc2o1` |
| 2 | 2.612 | `CC(=Cc1cc(O)cc(O)c1)c1cc2ccccc2[nH]1` |
| 3 | 2.611 | `O=C(O)c1ccc(Nc2nnc3nc[nH]c(-c4ccccc4)c2-3)cc1` |
| 4 | 2.530 | `COc1cc(C(=O)O)c(Cc2c[nH]c3ccccc23)cc2cc[n+](C)c1-2` |
| 5 | 2.505 | `O=C1CCN1c1ccc(OCCCN2C=Cc3[nH]cc4ncnc2c34)cc1` |

Chemotypes: benzofuran-piperidine-hydroxyquinoline (#1), stilbene-resorcinol-indole (#2), phenyl-triazolopyrimidine-benzoate (#3), isoquinolinium-indole-methoxybenzoate (#4), aryl-ether-imidazopyridopyrrolocarbazolone (#5). Scaffold diversity is high — consistent with generation on a loop-surface rather than a deep cleft.

## Interpretation

- **0.83 % fully-connected success is LOW**. PocketXMol produced 552 "incomplete molecules" — two disconnected drug-like fragments both sitting in the pocket instead of one connected molecule. This is the signature of a **flat, diffuse, low-druggability interface**: there's no single binding hot-spot deep enough to force connectivity through a minimum-energy channel.
- **Comparison to warm-pocket campaigns today**: DUSP6 ~30 %, DOK7 ~25 %, DUSP1 ~30 %. AGRIN is 30x lower success rate — real signal that AGRIN-LRP4 interface is hard.
- **Actionable interpretation**:
  1. The 5 connected hits are genuine outliers that PocketXMol found force-converging in the loop pocket. They deserve Boltz-2 validation.
  2. 552 "incomplete" pairs may still be mineable — a pair of fragments in the pocket = a two-warhead linker-design opportunity. Future work: fragment-merging against this pool.
  3. This campaign should not be scaled to 6000 mol expecting linear yield. Alternative approach: **binder-design via RFdiffusion** (protein binder to LG3 face) instead of small-molecule de novo.

## Next steps (NOT auto-executed)

1. Boltz-2 panel on Top 5 connected (AGRIN 3V64 + LRP4 counter 3V64 + LAMA2/LAMB1 LG counters)
2. Compute Z-score selectivity; gate `z_AGRIN > 0`
3. ADMET filters (QED, BBB tag-only, Lipinski)
4. Cross-campaign: check if any hit appears in DUSP6/CDK5/LIMK2 libraries (promiscuity flag)
5. **Strategic pivot decision**: if 0/5 pass Boltz-2 z-score gate, pivot to **RFdiffusion binder design** against 3V64 chain A SEA-face loop (protein binder > small molecule for this interface)

## Risks / honest caveats

- **Only 5 connected molecules** — any downstream z-score selectivity gate will have very limited survivors. A 5-mol top-list is too narrow for standard library filtering; each hit must be individually scrutinized.
- **Rat AGRIN crystal** — 95 % identical to human in LG3 domain but not 100 %. Any lead will need human AGRIN re-dock + sequence check around key contact residues (1779, 1783, 1787).
- **No native small-molecule ligand** in 3V64 → no C_rel baseline. Z-score across targets is primary selectivity metric.
- **Allosteric vs competitive mechanism** cannot be distinguished from PocketXMol pose alone; molecular dynamics or experimental assay required.
- **Direction ambiguity**: an AGRIN-binder could ENHANCE LRP4 affinity (therapeutic goal) or BLOCK LRP4 recognition (undesirable). Pose analysis + SMA NMJ assay required to differentiate.
- **Small-molecule drugging of AGRIN-LRP4 interface may be fundamentally hard** — industry consensus is that flat protein-protein interfaces generally require different modalities (peptides, antibodies, bispecifics, PROTACs). The 0.83 % generator success rate is consistent with this.

## Cost estimate

- A100 PCIE-40GB Japan @ $~0.70/hr
- Active compute: ~3 min total (pocket derive + smoke + full run)
- **Total: ~$0.04** for the generation phase
- Boltz-2 Top-100 panel (self-hosted): incremental ~$0 (GPU already running)

## File references

- Plan: `/home/bryza/sma-research/qms/agrin_lg3_modulator_plan.md`
- Task JSON: `/home/bryza/sma-research/qms/agrin_lg3_modulator_task.json`
- Pocket audit: `/home/bryza/fleet-results/agrin_lg3_modulator/pocket_audit.json`
- Top 100 connected: `/home/bryza/fleet-results/agrin_lg3_modulator/top100_connected.csv` (5 rows)
- Raw SMILES: `/home/bryza/fleet-results/agrin_lg3_modulator/molecules.smi` (557 RDKit-parseable, including disconnected)
- Gen info CSV: `/home/bryza/fleet-results/agrin_lg3_modulator/gen_info.csv`
