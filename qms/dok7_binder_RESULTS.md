# DOK7 PTB MuSK-Dimer-Stabilizer Campaign — RESULTS

**Campaign ID**: `dok7_binder`
**Status**: VERIFIED (triple_llm_verify 3/3 PASS 2026-04-17: OpenAI GPT-4o PASS, Groq Llama 3.3 70B PASS, Gemini 2.0 Flash PASS)
**Completed**: 2026-04-17 (PocketXMol generation)
**Instance**: A100 SXM4-40GB, Slovenia (ssh2:10542, contract 35120543), $0.6944/hr

## Executive summary

De novo design of DOK7 PTB small-molecule stabilizers targeting the canonical phospho-tyrosine recognition groove (R158/R159/Y160 triad + flanking 154-168). **149 fully-connected drug-like molecules** out of 600 attempted (24.8% success rate), reflecting the well-defined PTB groove geometry. Top 5 candidates have PocketXMol cfd_pos 2.777-2.818.

## Target verification

- **PDB 3ML4** — *Crystal structure of a complex between Dok7 PH-PTB and the MuSK juxtamembrane region* (Bergamin 2010, Mol Cell 39:100), X-ray 2.6 Å
- **PDB TITLE-verified**: `TITLE     CRYSTAL STRUCTURE OF A COMPLEX BETWEEN DOK7 PH-PTB AND THE MUSK`  `TITLE    2 JUXTAMEMBRANE REGION`
- Chains used: A (HUMAN DOK-7 Q18PE1 PH-PTB tandem, residues 1-220) + E (HUMAN MUSK O15146 JMR residues 544-556, 13-aa peptide)
- **3ML4 is the ONLY DOK7 crystal structure in PDB** — no alternative template available.

## Pocket derivation (verified sanity_checks PASS)

**Strategy**: canonical PTB phospho-tyrosine recognition groove. 15 DOK7 residues found within 5 Å of MuSK JMR peptide; focal core targets the R158/R159/Y160 triad plus flanking 154-168.

**Core PTB-groove residues (all verified identities)**:
L154, S155, D156, L157, **R158**, **R159**, **Y160**, G161, V163
(R158/R159 = arg-arg dyad that coordinates the pY553 phosphate; Y160 = stacking tyrosine)

**Triad geometry verified**:
- R158-R159 CA-CA = 3.79 Å (perfect trans-peptide)
- R159-Y160 CA-CA = 3.79 Å (perfect trans-peptide)

**Pocket center**: `[-80.758, -17.716, -27.745]` Å
**Pocket radius**: 10.0 Å
**Core extents**: 7.80 × 18.55 × 12.76 Å

Note: MuSK Y553 itself is disordered in the crystal (residues 553, 556 absent); only 8 JMR residues (547-552, 554-555) are resolved in chain E. The pocket is defined by DOK7 side of the interface, not the peptide.

## Compute run

- **Warm state**: PocketXMol SHA `65488cf635c856101dbe703ac97e2f10f58e005c`, conda env `pxm_cu128`, weights cached at `/opt/PocketXMol/data/trained_models`
- **Install skip**: 0 s (fully warm)
- **Smoke (5 mol)**: **PASS** — 5/5 collected, 4 valid SMILES, ~15 s wall
- **Full run (600 mol)**: 153.8 s wall, **GPU util 95-96%** at steady state (target > 60 % **MET**)
- **Throughput**: ~3.9 mol/s (including post-processing)

## Results

### PocketXMol pool statistics
| Category | Count | Fraction |
|---|---|---|
| Fully-connected ("success") | 149 | 24.8 % |
| Incomplete (disconnected fragments) | 366 | 61.0 % |
| Bad (RDKit-invalid) | 85 | 14.2 % |

### Top 5 candidates (ranked by PocketXMol cfd_pos)

| # | cfd_pos | SMILES |
|---|---|---|
| 1 | 2.818 | `Nc1ccc2nc(-c3ccc4[nH]c5ccc(-c6cc[nH+]cc6)cc5c4c3)[nH]c2c1` |
| 2 | 2.801 | `COc1ccccc1-c1cccc(-c2nc(Cc3ccc[nH+]c3)n[nH]2)c1` |
| 3 | 2.801 | `CC(=O)Nc1ccc2c(c1)ncc1c(-c3cccc(-c4cccc(C)c4C)c3)ccnc12` |
| 4 | 2.799 | `NC(=O)c1ccc(-c2csc(Cc3ccc(-c4ccccc4)cc3)n2)cc1` |
| 5 | 2.777 | `O=C(NCCc1ccccc1F)Nc1ccc(-c2ccccc2)cc1` |

Chemotypes: aminobenzimidazole-biarylpyridyl (#1), methoxyphenyl-triazole (#2), acetamide-naphthyridine-biaryltoluene (#3), carbamoyl-thiazole-biphenyl (#4), fluorophenyl-urea-biphenyl (#5). The top set is biaryl / heteroaryl-rich — consistent with targeting an arg-arg dyad that prefers π-stacking and aromatic hydrogen-bond acceptors to mimic the phosphate.

## Interpretation

- **24.8 % fully-connected success is STRONG** — typical for a well-defined groove campaign (cf. DUSP6 ~30 %, DUSP1 ~30 %, CDK5 ~25 %).
- **Top hits dominated by aromatic / heteroaryl scaffolds with H-bond acceptors** that can substitute for the phosphate oxygens of pY. This is the expected chemistry for a PTB-groove binder.
- **Positive ionizable groups** ([nH+]) in Top 1, 2 — these would be protonated at physiological pH and could mimic the phosphate negative charge reciprocally interacting with R158/R159. Pose-level analysis in Boltz-2 will confirm.
- **pY-mimetic warning**: PTB domains are notoriously hard to drug with non-phosphate small molecules. Prior PTB-directed campaigns (SHP2, IRS1) have required covalent or peptide strategies. Our top hits avoid phosphate groups entirely — a pragmatic design choice but may limit ceiling affinity.
- **Selectivity risk**: R158/R159/Y160 triad is NOT unique to DOK7 — many PTB domains (IRS1, SHC1) share related motifs. Top hits will likely cross-react; counter-screen critical.

## Next steps (NOT auto-executed)

1. Boltz-2 panel on Top 100 connected (DOK7 3ML4 + MuSK counter + IRS1 PTB + SHC1 PTB)
2. Compute Z-score selectivity; gate `z_DOK7 > 0` + `selectivity_z > 0` vs IRS1/SHC1
3. ADMET filters (QED, BBB tag-only, Lipinski)
4. Cross-campaign: check if any hit appears in DUSP6/CDK5/LIMK2 libraries (promiscuity flag)
5. Strategic: run **secondary DOK7 campaign** targeting the dimer interface (separate PDB region), not the pY-groove — complementary mechanism, potentially cleaner selectivity

## Risks / honest caveats

- **Single PDB template** (3ML4) — no conformational ensemble; hits may be brittle to DOK7 dynamics. Consider running a short MD on chain A + Boltz-2 rescore on multiple snapshots.
- **No native small-molecule ligand** in 3ML4 → no C_rel baseline. Z-score is primary selectivity metric.
- **PTB-family cross-reactivity**: R158/R159/Y160-like motifs exist in many PTBs. Expect promiscuity. Counter-screen essential.
- **Direction ambiguity**: a PTB-groove binder could STABILIZE DOK7-MuSK complex (therapeutic goal) or COMPETE with MuSK-pY553 (undesirable for SMA NMJ). Pose-level analysis + cell-based NMJ clustering assay required to differentiate.
- **Allosteric stabilizer mode preferred but not targetable computationally** — the 3ML4 crystal only shows the pY-groove binding mode; an allosteric pocket would need separate identification (e.g., FPocket, DoGSiteScorer on full 3ML4 tetrameric assembly).

## Cost estimate

- A100 SXM4 40GB Slovenia @ $0.6944/hr
- Active compute: ~3 min total (pocket derive + smoke + full run)
- **Total: ~$0.04** for the generation phase
- Boltz-2 Top-100 panel (self-hosted): incremental ~$0 (GPU already running)

## File references

- Plan: `/home/bryza/sma-research/qms/dok7_binder_plan.md`
- Task JSON: `/home/bryza/sma-research/qms/dok7_binder_task.json`
- Pocket audit: `/home/bryza/fleet-results/dok7_binder/pocket_audit.json`
- Top 100 connected: `/home/bryza/fleet-results/dok7_binder/top100_connected.csv` (100 of 149 fully-connected)
- Raw SMILES: `/home/bryza/fleet-results/dok7_binder/molecules.smi` (515 RDKit-parseable, including disconnected)
- Gen info CSV: `/home/bryza/fleet-results/dok7_binder/gen_info.csv`
