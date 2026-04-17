# NMJ ECD De Novo Binder Design Matrix — Results (DRAFT)

**Status**: DRAFT (pending RFdiffusion → MPNN → ESMfold → Boltz-2 cascade completion + triple_llm_verify 3/3)
**Date**: 2026-04-17
**Plan**: extends PERP ECL binder cascade (see `PERP_binder_design_RESULTS.md`) to 4 NMJ receptor ECDs
**Compute**: Vast H100 SXM 80GB India, contract 35134656, SSH ssh4.vast.ai:14656, ~$1.69/hr
**Pipeline**: RFdiffusion (Complex_base, T=50 default, OMP_NUM_THREADS=4 to avoid shared-host CPU thrash) → ProteinMPNN (local, temp=0.1, 8 seq/backbone) → ESMfold (local, `facebook/esmfold_v1`, half-precision) → Boltz-2 PPI co-fold via sma-h100-two:8003 SSH tunnel, seeded scrambled negative (seed=42), delta_iptm > 0.1 gate.

## PDB verification (4 targets)

| Target | UniProt | PDB (brief) | PDB (verified/used) | TITLE result | Notes |
|---|---|---|---|---|---|
| MuSK | O15146 | 1LUF / 2IEP | **2IEP** | `CRYSTAL STRUCTURE OF IMMUNOGLOBULIN-LIKE DOMAINS 1 AND 2 OF THE RECEPTOR TYROSINE KINASE MUSK` (chains A,B, res 24-210) | 1LUF is **cytoplasmic kinase domain** (res 526-868), NOT ECD — brief's flag-to-verify was correct. 2IEP is rat (96% id human) as brief noted. |
| LRP4 | O75096 | 5K3B | **3V64** (corrected) | `CRYSTAL STRUCTURE OF AGRIN AND LRP4` (LRP4 LG3 chain A,B res 1758-1948, AGRIN β1 propeller chain C,D res 404-744) | 5K3B is **fluoroacetate dehalogenase in Rhodopseudomonas** — completely wrong protein. Used 3V64 instead (Zong 2012, *Genes Dev* 26:247, PMID 22302937) which has the direct LRP4-AGRIN interface. |
| DOK7 | Q18PE1 | 3ML4 | **3ML4** | `CRYSTAL STRUCTURE OF A COMPLEX BETWEEN DOK7 PH-PTB AND THE MUSK JUXTAMEMBRANE REGION` (chains A-D DOK7, E-H MuSK JMR 8-mer 547-555) | Verified; same PDB used in dok7_binder small-molecule plan. **Chain A has 8 missing residues (gaps at 15-17, 38, 88, 97, 149, 192)** — required gap-aware contigs. |
| CHRNA1 | P02708 | "ACh receptor ECD **VERIFY**" | **2QC1** | `CRYSTAL STRUCTURE OF THE EXTRACELLULAR DOMAIN OF THE NICOTINIC ACETYLCHOLINE RECEPTOR 1 SUBUNIT BOUND TO ALPHA-BUNGAROTOXIN AT 1.9 Å RESOLUTION` (chain A = α-BTX, chain B = CHRNA1 ECD res 0-211) | 2BG9 (4 Å full receptor) was candidate but 2QC1 is ECD-only at 1.9 Å — much better for binder design. Brief "MIR res 60-85" is not the actual α-BTX contact surface: the real iface covers **loop F (91-100) + loop A (148-150) + loop C (187-198)** — the agonist binding pocket. |

All 4 targets' sequences extracted from PDB chains and saved to `target_sequences_from_pdb.json` on H100 and dispatcher.

## Interface residues (derived from PDB, <5 Å contacts, ATOM-only)

| Target | Chain | Partner chain | Interface residues |
|---|---|---|---|
| MuSK (2IEP) | A | *none (apo crystal)* | Used Ig1 β-sheet face from mutagenesis literature: cluster M1a {47,52,55}, M1b {74,78,82}, M1c {98,102,106} |
| LRP4 (3V64) | A | AGRIN C | 1844, 1865, 1866, 1877, 1878, 1879, 1880, 1883 |
| DOK7 (3ML4) | A | MuSK JMR E | 154, 155, 156, 157, 158, 159, 160, 161, 163, 168, 174, 193, 197, 200, 201 |
| CHRNA1 (2QC1) | B | α-BTX A | 91, 93, 99, 100, 148, 149, 150, 187-195, 197, 198 |

## Hotspot triplets (3 per target)

| Target | ID | Residues | Rationale |
|---|---|---|---|
| MuSK | M1a | A47/A52/A55 | β-strand A1, N-term Ig1 |
| MuSK | M1b | A74/A78/A82 | β-turn loop center, Ig1 |
| MuSK | M1c | A98/A102/A106 | C-terminal β-strand of Ig1 |
| LRP4 | L1a | A1844/A1865/A1877 | spans the AGRIN-binding edge |
| LRP4 | L1b | A1866/A1878/A1883 | alternating on the interface |
| LRP4 | L1c | A1877/A1879/A1883 | focal on core 1877-1883 |
| DOK7 | D1a | A158/A159/A160 | canonical PTB pY-recognition triad R158/R159/Y160 |
| DOK7 | D1b | A154/A156/A160 | N-flank of triad + Y160 |
| DOK7 | D1c | A160/A174/A197 | Y160 + β-turn + 197 |
| CHRNA1 | C1a | B91/B93/B99 | loop F (main immunogenic region-adjacent) |
| CHRNA1 | C1b | B148/B150/B192 | loop A + loop C (agonist pocket span) |
| CHRNA1 | C1c | B189/B192/B195 | loop C core |

## Campaign execution

- **40 backbones per hotspot × 3 hotspots × 4 targets = 480 RFdiffusion designs**
- Per-design time measured at ~0.6 min on the H100 India shared host (with OMP_NUM_THREADS=4 cap — without this, 385-thread oversubscription deadlocked the process)
- Expected RFdiff wall clock: ~5 h
- Expected MPNN+ESMfold: ~1-2 h per target, 4-8 h total
- Expected Boltz-2 PPI (40 × 3 × 4 × 2 folds = 960 calls): ~2-3 h on sma-h100-two:8003 batched server
- **Total campaign wall clock estimate: ~11-16 h**

## Infrastructure notes

- Bootstrap on fresh pytorch:2.4.1-cuda12.4 container on ssh4:14656 required:
  - `dgl==1.1.3+cu121` from `https://data.dgl.ai/wheels/cu121/repo.html` (cu118 wheel wanted libcudart.so.11.0 which isn't present; CPU-only dgl fails with `Operator Range does not support cuda device`)
  - `se3-transformer` via `pip install --no-build-isolation git+https://github.com/NVIDIA/DeepLearningExamples.git#subdirectory=DGLPyTorch/DrugDiscovery/SE3Transformer`
  - `torchdata==0.7.1`, `pydantic`, standard scientific stack
- **Shared host issue**: the instance reports 192 CPUs but effective allocation is ~28 vCPU on a heavily loaded host (load avg 161 with default thread settings). Using `OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4` and serial (1-at-a-time) launches avoid the deadlock that happened with parallel 2-process launches.
- `diffuser.T=25` override (used in PERP campaign) **could not be applied** on this instance — it triggers an IGSO3 cache recomputation that never completed in >30 min of CPU time. Reverted to default `T=50`, accepting 2× wall-clock penalty (still within budget).

## Quality gates (pre-compute)

- [x] 4 PDB TITLEs fetched and verified via `curl -s https://files.rcsb.org/header/<PDB>.pdb | grep -E "^(TITLE|COMPND|SOURCE)"`
- [x] Brief's wrong PDB for LRP4 (5K3B) detected and replaced with correct 3V64
- [x] Chain residue ranges inspected; DOK7 chain A gap-aware contigs built
- [x] Interface residues recomputed with ATOM-only filter to exclude symmetry-mate ghost atoms
- [ ] RFdiff runs complete (in progress: fired 2026-04-17 13:44 UTC)
- [ ] ESMfold pLDDT > 0.70 gate applied per hotspot
- [ ] Scrambled-binder control computed for every Boltz-2 call (seed=42)
- [ ] delta_iptm > 0.1 gate applied
- [ ] Top 10 per target compiled into `top_binders_matrix.tsv`
- [ ] Triple-LLM verify 3/3 PASS on final RESULTS

## Caveats (to be preserved in FINAL)

- Binders designed without lipid/membrane context — MuSK and CHRNA1 ECDs sit at the synaptic membrane, and this affects the true accessible surface for a binder. DOK7 is intracellular, LRP4 LG3 is extracellular but tethered to a multi-domain LDL-R-like scaffold. **Wet-lab validation is required** before any claim.
- Disulfides in the ECDs (2IEP has Cys-Cys in Ig folds; 2QC1 has conserved C128/C142 disulfide plus cys-loop) were not explicitly restrained in RFdiff; ProteinMPNN sequence design may introduce free Cys into binders.
- 3V64 is rat LRP4; human LRP4 is ~95% identical in LG3 but this should be noted.
- CHRNA1 2QC1 chain B is bound to α-BTX (the competitive antagonist); this fixes the ECD in the agonist-OFF conformation. A designed binder might act as an inverse agonist / blocker rather than activator.
- DOK7 PTB is intracellular — "ECD" is inaccurate for DOK7; it is a cytoplasmic adapter. Reported alongside ECDs because it is part of the NMJ receptor-complex signalling axis (agrin → LRP4 → MuSK → DOK7 → AChR clustering).

## Output structure

```
/home/bryza/fleet-results/nmj_ecd_binders/
├── setup/            # PDBs, interface_residues.json, campaign_config.json, target_sequences_from_pdb.json
├── sequences/        # UniProt FASTAs and ECD-only extracts
├── logs/             # H100 bootstrap + campaign logs
├── MuSK/             # rfdiff/, mpnn/, esm/, boltz2/
├── LRP4/             # rfdiff/, mpnn/, esm/, boltz2/
├── DOK7/             # rfdiff/, mpnn/, esm/, boltz2/
├── CHRNA1/           # rfdiff/, mpnn/, esm/, boltz2/
└── top_binders_matrix.tsv  (40 rows when campaign completes: 10 per target)
```

---

*DRAFT placeholders for final numbers (to be filled when Boltz-2 completes):*

- Cascade pass rates per target — TBD
- Top 10 binders per target — TBD
- Overall winner across 40 binders — TBD
- Triple-LLM verdict — TBD
- Final wall-clock and cost — TBD
