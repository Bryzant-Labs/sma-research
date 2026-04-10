# 4-AP Compute Plan — What To Do Before Simon Handoff

**Date**: 2026-04-10
**Context**: 4-AP is a Track B (Universal Recovery Platform) candidate for SMA. Before handing Simon a wet-lab package, we should complete the computational evidence. This is a gap analysis + action plan.

## What We Already Have (audit 2026-04-10)

| Asset | Status | Files |
|---|---|---|
| 4-AP Kv1.2 holo MD | PARTIAL 12.3/20 ns (62.5%) | `md_sims/4AP_Kv12_holo/` |
| 4-AP SMN2 holo MD | COMPLETE 18.6/20 ns (neg result) | `md_sims/4AP_SMN2_holo/` |
| SMN2 vs Kv1.2 4-AP selectivity MD | COMPLETE 10 ns | `md_sims/SMN2_vs_Kv12_4AP_selectivity/` |
| 4-AP SMN2 MMPBSA trajectory | Trajectory only, no ΔG | `md_sims/SMN2_4AP_MMPBSA/` |
| 4-AP DiffDock selectivity | COMPLETE 5 targets (Kv1.2, Kv3.1, Kv7.1, SARM1, RIPK1) | `drug_discovery/diffdock/batch_4ap/` |
| 4-AP MMPBSA (Kv1.2) | NOT DONE | — |
| 4-AP ADMET profile | NOT DONE (but FDA-approved so known) | — |
| 4-AP contact map analysis | NOT DONE | — |
| 4-AP vs regeneration targets | NOT DONE | — |

## What 4-AP Could Additionally Do (mechanisms to test)

### Primary: Kv1 family blockade (validated)
- **Kv1.1** (axon initial segment, critical for AP firing)
- **Kv1.2** (juxtaparanode, remyelination) — we have MD
- **Kv1.3** (T-cell, immune modulation — could reduce SMA neuroinflammation)
- **Kv1.4, Kv1.5, Kv1.6** (tissue-specific)

### Secondary: Kv3 family (weaker blockade at higher doses)
- **Kv3.1** — fast-spiking interneurons — we have DiffDock
- **Kv3.2, Kv3.3, Kv3.4** — motor neuron populations

### Regeneration pathway (Simon's hypothesis)
- **BDNF/TrkB signaling** — growth factor cascade
- **STAT3** — master axon regeneration transcription factor
- **mTOR** — cell growth, protein synthesis
- **PTEN** — tumor suppressor, INHIBITS axon regeneration (opposing)
- **GAP43** (neuromodulin) — growth cone marker
- **STMN2** (stathmin-2) — axonal microtubule dynamics, already in our SMA targets
- **Sox11, ATF3** — regeneration transcription factors

### Remyelination targets (4-AP in MS literature)
- **Kir4.1** (inward rectifier) — oligodendrocyte function
- **NKCC1** (Na-K-Cl cotransporter) — Schwann cell osmoregulation
- **MBP interactions** — myelin compaction
- **OPC (oligodendrocyte precursor) differentiation markers**

### NMJ-specific (presynaptic boost)
- **CaV2.1 (P/Q-type Ca²⁺ channel)** — presynaptic Ca²⁺ influx, neurotransmitter release
- **SNARE complex proteins** — vesicle fusion
- **Nicotinic AChR α1** — postsynaptic receptor clustering

## Compute Experiments — Prioritized

### 🟢 QUICK WINS (today, <2h, cheap)

#### 1. **MMPBSA on 4-AP Kv1.2 trajectory** (⭐ highest value)
- Input: `md_sims/4AP_Kv12_holo/trajectory.dcd` (12.3 ns)
- Method: AmberTools MMPBSA.py (installed locally in ~/miniforge3/envs/ambertools)
- Output: ΔG_bind (kcal/mol) for 4-AP on Kv1.2
- Compare to: Published Kv1.2 + 4-AP affinity (~100 μM = ~-5 kcal/mol)
- **Why critical**: Quantifies the binding. Without this, we have "it's stable in MD" but no number.
- **Compute**: ~1h on local CPU (AmberTools)
- **Deliverable**: `drug_discovery/mmpbsa/4AP_Kv12_holo/mmpbsa_result.json`

#### 2. **Contact persistence map** (Kv1.2 residues touched by 4-AP)
- Input: Same trajectory
- Method: MDAnalysis contact analysis — count frames where each Kv1.2 residue is within 4 Å of 4-AP
- Output: Table of residues + contact frequency + comparison to literature (known Kv1.2 inner gate residues V381, I385, etc.)
- **Why**: Validates that 4-AP binds the expected site (S6 inner gate), not a random pocket
- **Compute**: ~10 min Python on local CPU
- **Deliverable**: `drug_discovery/contact_maps/4AP_Kv12_contacts.csv` + heatmap PNG

#### 3. **ADMET confirmation via ADMET-AI**
- Input: 4-AP SMILES `Nc1ccncc1`
- Method: ADMET-AI GNN prediction on all 41 TDC endpoints
- Output: BBB, hERG, DILI, CYP3A4, Ames, etc.
- **Why**: Confirms clinical safety profile computationally (it's already FDA-approved, so this is validation not discovery)
- **Compute**: <1 min CPU
- **Deliverable**: `drug_discovery/admet_v2/4AP_admet_ai.json`

#### 4. **Docking against regeneration targets** (DiffDock batch)
Targets to add to existing DiffDock run:
- BDNF receptor TrkB (PDB: 1HCF or AlphaFold)
- STAT3 SH2 domain (PDB: 1BG1)
- PTEN (PDB: 1D5R)
- GAP43 (AlphaFold)
- STMN2 (AlphaFold)
- mTOR FRB domain (PDB: 4DRI)
- **Why**: DIRECTLY tests Simon's regeneration hypothesis computationally
- **Compute**: ~30 min per target on A100, can run after current RFdiffusion finishes
- **Deliverable**: `drug_discovery/diffdock/batch_4ap_regeneration/`

### 🟡 MEDIUM PRIORITY (1-2 days compute)

#### 5. **Complete 4-AP Kv1.2 20 ns MD** (finish partial)
- Script already debugged: `~/gpu-fleet/scripts/deploy_4ap_kv12_md.sh` (has setuptools<81 + conda TOS fixes)
- Rent RTX 3090 ($0.15/hr), run remaining 7.7 ns from saved checkpoint (~20 hours)
- **Why**: Get the full 20 ns publication-quality trajectory
- **Cost**: ~$3
- **Deliverable**: Full `md_sims/4AP_Kv12_holo_20ns/`

#### 6. **Kv1 family selectivity MD panel**
- Targets: **Kv1.1** (2R9R analog for SMA), **Kv1.3** (3OC3), **Kv1.5** (not SMA-relevant but validation)
- 10 ns each, holo with 4-AP pre-docked
- **Why**: Shows which Kv1 isoforms 4-AP prefers (relevant for side effects)
- **Compute**: 3 × ~10 hours on RTX 3090 each = ~30 GPU hours = ~$6
- **Deliverable**: `md_sims/4AP_Kv1X_panel/`

#### 7. **4-AP vs 3,4-DAP (Firdapse) comparative docking**
- 3,4-Diaminopyridine is more potent (approved for LEMS, 4x stronger at Kv1)
- DiffDock both on same 5 targets
- **Why**: If we propose 4-AP for SMA, 3,4-DAP is a smarter alternative — both approved, 3,4-DAP more potent
- **Compute**: ~30 min DiffDock
- **Deliverable**: `drug_discovery/diffdock/batch_34DAP/` + comparison report

#### 8. **Network analysis on SMA platform**
- Use CORTEX + SMA platform API to find all known interactions 4-AP → SMA-relevant targets
- Query published databases (DrugBank, ChEMBL, STITCH) for 4-AP targets
- **Why**: Find NEW mechanisms we haven't considered
- **Compute**: ~15 min API queries + CORTEX reasoning
- **Deliverable**: `findings/FINDING_4AP_network_analysis.md`

### 🔴 BIG COMPUTE (speculative, 1 week+)

#### 9. **Full Kv1.2 tetramer with explicit membrane bilayer MD**
- Current MD likely uses monomer/truncated — not physiological
- Build with CHARMM-GUI: full tetramer + POPC bilayer + TIP3P + ions
- 100 ns production MD
- **Why**: True functional state of channel for drug-binding analysis
- **Compute**: ~5 days on A100 = ~$60-100
- **Risk**: May reveal the current MD was inadequate

#### 10. **Metadynamics binding/unbinding 4-AP + Kv1.2**
- Enhanced sampling to compute Kd from free energy surface
- Requires PLUMED + OpenMM
- **Why**: Quantify 4-AP affinity independently of classical MMPBSA
- **Compute**: ~1 week on A100 = ~$100-150
- **Risk**: Expensive, may not converge

## Recommended Execution Order (to finish THIS week)

### Phase 1: Today/Tonight (3 hours of work, $0 cost)
```
[1] MMPBSA on existing 4AP_Kv12_holo trajectory     — 1h on local CPU
[2] Contact map analysis                              — 10 min Python
[3] ADMET-AI for 4-AP SMILES                          — 1 min
[4] CORTEX network query for 4-AP SMA links           — 15 min
```
**→ Gives us: ΔG, binding residues, safety profile, literature context**

### Phase 2: Tomorrow (on A100 or RTX 3090, ~$8)
```
[5] DiffDock 4-AP vs regeneration targets (6 targets) — 3h on A100
[6] DiffDock 3,4-DAP vs same 6 targets                — 3h on A100
[7] Complete 20 ns Kv1.2 holo MD                       — 20h on RTX 3090 (background)
```
**→ Gives us: Regeneration hypothesis tested, better drug comparison, full MD**

### Phase 3: Later this week (if time permits, ~$15)
```
[8] Kv1 family panel (Kv1.1, Kv1.3) MDs                — 30 GPU hours
[9] Fasudil + 4-AP synergy MD (combo docked to ROCK2) — 15 GPU hours
```
**→ Gives us: Side effect profile, combination therapy data**

### Phase 4: Simon Package Assembly
After Phase 1+2:
- Compile findings into single PDF brief
- Quantitative results: ΔG, contact residues, regeneration docking scores
- Decision: is 4-AP worth wet-lab follow-up in SMA models?
- Proposed protocol: 4-AP + nusinersen in delta7-SMA mice

## Cost Summary

| Phase | Time | Compute Cost | Scientific Value |
|---|---|---|---|
| Phase 1 | 3h | $0 | ⭐⭐⭐⭐⭐ Foundation |
| Phase 2 | 1 day | ~$8 | ⭐⭐⭐⭐ Regeneration hypothesis tested |
| Phase 3 | 3 days | ~$15 | ⭐⭐⭐ Additional depth |
| Phase 4 | 2h | $0 | ⭐⭐⭐⭐⭐ Package |
| **Total** | **4-5 days** | **~$23** | **Publishable, Simon-ready** |

## What We Should NOT Do (yet)

- ❌ Full tetramer membrane MD ($60-100) — too expensive for incremental value
- ❌ Metadynamics ($100-150) — exotic, may not converge
- ❌ Synthesize 4-AP analogs — it's already approved, no point
- ❌ Run 4-AP on SMN2 again — already showed negative result

## Key Questions for Simon

Before committing to wet lab, we should ask Simon:
1. Does he have access to delta7-SMA mice or SMA patient iPSC-MNs?
2. Has he seen any 4-AP effect in SMA context (published or anecdotal)?
3. Would he prefer 4-AP or 3,4-DAP (Firdapse) for testing? Firdapse is 4× more potent.
4. Is there an existing MS or SCI collaborator who has 4-AP tissue data?
5. Would a simple axonal crush model with 4-AP ± SMN rescue be feasible?

## License

CC-BY-4.0 — open planning document. Part of `Bryzant-Labs/sma-research`.
