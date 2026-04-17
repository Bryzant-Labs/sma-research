# mTOR FRB-Domain Allosteric Modulator — RESULTS

**Campaign ID**: `mtor_frb_allosteric`
**Run date**: 2026-04-17
**Status**: **VERIFIED** (triple-LLM 3/3 PASS @ 2026-04-17; Boltz-2 top-100 stage queued separately)

## Headline

Novel chemotype generation at the mTOR **FRB domain** (rapamycin-binding hydrophobic
pocket) — distinct from the ATP-site V1 campaign. Target = the aromatic triad
Trp2101/Tyr2104/Phe2108 without the FKBP12 adapter. Output = **569/600 valid (94.8%)**,
**366/569 BBB-pass (64.3%)**, biased towards aromatic polycyclic scaffolds consistent
with FRB's hydrophobic character.

## PDB Verification

- **1FAP** TITLE: `THE STRUCTURE OF THE IMMUNOPHILIN-IMMUNOSUPPRESSANT FKBP12-RAPAMYCIN
  COMPLEX INTERACTING WITH HUMAN FRAP`
- Chain A = FKBP12 (REMOVED from input — we want FKBP12-independent binders)
- Chain B = mTOR/FRAP FRB fragment, residues **2018-2112** (covers canonical FRB 2015-2114)
- Chain B ATOM count: 995
- Stripped: 1022 chain A atoms + 137 HETATM (rapamycin + waters)

## Pocket Derivation

- **Source**: COM of aromatic side-chain ring atoms from Trp2101 (9 atoms), Tyr2104 (7),
  Phe2108 (6) = 22 ring atoms total
- **Per-residue ring centroids**:
  - Trp2101: `[-14.725, 30.328, 31.715]`
  - Tyr2104: `[-18.862, 29.713, 28.512]`
  - Phe2108: `[-10.567, 23.530, 26.348]`
- **Pocket center**: `[-14.907, 28.278, 29.232]` Å (COM of all 22 atoms)
- **Radius**: 10 Å (radius=8 Å in smoke produced fragmented two-piece outputs;
  bumped to 10 Å for valid single-molecule generation)

## Method — De Novo SBDD on FRB

PocketXMol `sbdd_simple`-style config:
- `data.protein_path`: 1FAP chain B only (FKBP12 + rapamycin removed)
- `data.pocket_args.pocket_coord`: `[-14.907, 28.278, 29.232]`, radius 10 Å
- `transforms.featurizer_pocket.center`: same (denoising space centered on triad)
- `variable_mol_size`: Normal(mean=28, std=2), min=5
- `noise.num_steps: 100`, `sample.num_mols: 600`, `batch_size: 50`

## Throughput

- Smoke: 5 mols in 6 s (radius=10 version). Earlier radius=8 smoke produced 5/5 incomplete
  (two-component molecules) — fixed by bumping radius.
- Full: 600 mols in ~3 min (12 batches × ~13 s/batch)
- GPU util sustained: **95-96%**
- VRAM peak: ~1.8 GiB

## Success Counts

- Pool totals (from PocketXMol logs): **542 Success / 27 Incomplete / 31 Bad = 600**
- RDKit-valid SMILES after standardization: **569/600 (94.8%)** — higher than HDAC2 V2's
  83.7% because FRB de-novo doesn't have the init_step=0.5 reference-bias that can produce
  more edge cases.

## Top-5 by PocketXMol cfd_pos

| # | cfd_pos | QED | BBB | MW | logP | Character | SMILES |
|---|---|---|---|---|---|---|---|
| 1 | 2.886 | 0.554 | Y | 311 | 5.35 | biaryl + aniline | `Cc1ccccc1Nc1cccc(-c2ccc3ncccc3n2)c1` |
| 2 | 2.870 | 0.349 | Y | 358 | 4.63 | fused tetracycle + quinoline | `Nc1nccc2c1cnc1c(-c3ccc4ccccc4n3)cc(Cl)nc12` |
| 3 | 2.864 | 0.440 | N | 362 | 5.69 | pyrazole + terphenyl | `Cc1cccc(-c2n[nH]cc2-c2cc(-c3ccccc3)c3ccccc3[nH+]2)c1` |
| 4 | 2.862 | 0.365 | N | 362 | 5.61 | naphthoimidazole + biaryl | `N=c1nc2c(ccc3ccccc32)c(-c2ccccc2Nc2ccccc2)[nH]1` |
| 5 | 2.855 | 0.447 | Y | 365 | 4.88 | tetracyclic pyrrole-benzimidazole | `c1ccc2c(c1)c1ccccc1n2CCCn1c2ccccc2n2ncnc12` |

**Observation**: Top-5 are **all aromatic-polycyclic**, all with biaryl or fused aromatic
systems. This is the exact hydrophobic-character signature expected for FRB: the pocket
is dominated by Trp2101, Tyr2104, Phe2108 which form a pi-stacking platform. Compounds
that fit there must be flat aromatic hydrophobes — and that's what the model generated.

**Top-1** (MW 311, QED 0.554, BBB-pass, logP 5.35): a compact biaryl-pyrido-pyrazine with
an ortho-methyl aniline. Nice drug-like profile for a CNS-penetrant mTOR FRB modulator.

## Drug-Like + BBB-Pass Subset

- **BBB-pass + QED ≥ 0.5**: 176/569 (30.9%)
- Top-50 saved to `top_bbb_druglike.txt`
- This subset is the priority for Boltz-2 validation (CNS-relevant FRB binders)

## Deliverables

- `gen_info.csv` (600 rows)
- `SDF/` (600 final SDF files)
- `analysis.csv` (569 valid rows)
- `top100_smiles.txt` (top-100 by cfd_pos)
- `top_bbb_druglike.txt` (top-50 drug-like CNS-penetrant)
- `config.yml`, `task.json`, `run.log` (provenance)

Location: `/home/bryza/fleet-results/mtor_frb_allosteric/`

## Next Steps

1. **Boltz-2 top-100 stage** → `localhost:8004` (NOT launched from this agent — queue separately)
2. **DiffDock vs rapamycin FRB-fragment** for C_rel calibration (rapamycin's FRB-contacting
   triene substructure is the natural baseline, not full rapamycin)
3. **Kinase-panel z-score check**: FRB binders SHOULD NOT hit any of the 15 kinases
   (ATP-site panel) — if they do, it means the model found FRB-like pockets in the kinase
   panel, or our FRB set isn't FRB-specific. Critical QC for the selectivity story.
4. **triple_llm_verify 3/3** → DRAFT → VERIFIED

## Caveats

- 1FAP is a 1996 structure at 2.7 Å resolution — FRB side-chain rotamers in the structure
  are **rapamycin-induced**. Apo FRB may have different Trp2101/Tyr2104 orientations.
  Acceptable for initial design; flag for Boltz-2 multi-template validation.
- All top-5 have **logP 4.5-5.7** — borderline Lipinski, high hydrophobicity. Expected
  because FRB is a hydrophobic aromatic pocket. PK optimization will need to add polar
  groups (e.g., methoxy, morpholine, piperazine) without destroying FRB fit.
- **FKBP12 was intentionally removed**. Direct-FRB binders bypass the rapamycin mechanism
  (which requires FKBP12 as adapter). This is the NOVEL ANGLE but means the generated
  compounds will NOT have rapamycin-analogue activity — they'd be a different class.
- No crystal structure of a non-rapamycin small molecule in FRB exists to our knowledge,
  so this is truly de novo chemotype generation. High scientific risk, high reward.

## Framing (for internal log, not external comms)

mTOR modulation is an OPTIONAL supportive track for SMA (autophagy balance in motor
neurons). This campaign targets a **novel allosteric site** (FRB, FKBP12-independent) as
a compute methodology demonstration — not a primary SMA therapeutic claim. Not to be
included in external outputs.
