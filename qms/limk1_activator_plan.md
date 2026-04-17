# LIMK1 αC-Helix Allosteric Activator Campaign — Pre-Flight Plan

**Status:** DRAFT (pre-flight — PocketXMol generation ALREADY COMPLETE from prior agent)
**Date:** 2026-04-17
**Campaign ID:** `limk1_activator_alphaC`
**Author:** Opus Master Agent (continuation of prior ssh7 agent run)
**Exploratory level:** HIGH — selectivity-control set, paralog of LIMK2.
Framing: **reference chemotype** for LIMK2 campaign, NOT a direct SMA therapy.

## Framing and purpose

LIMK1 (UniProt P53667) is the paralog of LIMK2 (Q9H3T3). Both phosphorylate
cofilin at S3. The two genes diverged ~500 Mya. The 2026-04-16 ESM-2 kinase
selectivity finding: LIMK1/LIMK2 sequence similarity = 0.990. They share
catalytic domain topology and the same LIMKi3 pan-binder.

**Why we care for the LIMK2 programme:**
- LIMK1-**selective** activator = SMA therapy? — NO, LIMK1 is cognition-linked
  (Williams syndrome deletion). Not a SMA target.
- LIMK1-**nonselective** activator = **selectivity negative control**. Any LIMK2
  activator we design must be screened against LIMK1. A compound that activates
  both is a "pan-LIMK" activator, not selective.
- LIMK1 generation set is a **reference chemotype bank** for the selectivity
  comparison.

**SMA claim surface:** none. This campaign contributes only to selectivity gating
and scaffold diversity for the LIMK2 programme.

## Target

| Parameter | Value | Source |
|---|---|---|
| Gene | LIMK1 | UniProt P53667 |
| PDB | **5L6W** — verified TITLE: "STRUCTURE OF THE LIMK1-ATPGAMMAS-CFL1 COMPLEX" | RCSB |
| Chain | L (LIM DOMAIN KINASE 1) | PDB header |
| Residue range | 328–633 | PDB |
| Co-crystal | ATP-γS (AGS) + CFL1 cofilin chain | PDB |
| State | αC-IN, ACTIVE (K368(NZ)↔E384(OE1) = 2.67 Å) | Prior derivation |
| Pocket strategy | αC-helix anchor (allosteric-stabilizing activator) | Same as LIMK2 αC |
| Pocket center | **[−24.916, 35.592, 28.584]** | CA mean of pocket residues |
| Pocket radius | 15.44 Å | PocketXMol SBDD convention |
| Pocket residues | β3-K368 + αC 378–394 + HRD-D460 + DFG 478–480 | 22 residues |
| Molecule count | 600 | Christian's dispatch |
| Batch size | 100 | A100 40 GB |

### Motif verification (done in prior derive_pocket.py, 5L6W chain L)

- β3-Lys = K368 (VMVMK motif 364–368) — confirmed K
- αC-Glu = E384 (salt bridge to K368, +16 from K, ~canonical +17) — confirmed E
- HRD catalytic D = D460 — confirmed D
- DFG motif = D478-F479-G480 — confirmed

### Salt bridge sanity

K368(NZ) ↔ E384(OE1) = **2.67 Å** = tight αC-IN active state. Activator pocket
targets the allosteric face of the αC anchor (promote/stabilize this conformation).

## Instance

| Parameter | Value |
|---|---|
| Host | `ssh7.vast.ai:17456` (root, key `~/.ssh/id_ed25519_vastai`) |
| GPU | 1× A100 SXM4 40 GB |
| PocketXMol | `/workspace/PocketXMol` (git SHA 65488cf) |
| Weights | present |
| Entry script | `scripts/sample_use.py` (NOT `_pdb` variant) |

## Workflow

**NOTE: PocketXMol generation was completed at 08:46 UTC on 2026-04-17 by prior
agent (600 attempts, 181 success, 302 incomplete, 117 bad; gen_info.csv has 600
rows). Prior agent died on Boltz-2 rate-limit. This plan resumes from filter.**

1. ✅ **Fetch 5L6W** — done by prior agent
2. ✅ **Derive αC anchor pocket** — done (pocket_derivation.py + pocket_residues.txt)
3. ✅ **Write config** (limk1_full.yml, pocket_coord + radius 15)
4. ✅ **Run PocketXMol** (600 mol, 100-batch) — outputs_limk1_full/limk1_full_pxm_20260417_084657/
5. **Extract 181 valid SMILES** → /home/bryza/fleet-results/limk1_activator_alphaC/gen_info.csv
6. **Smoke test** (only if re-run needed) — skipped because gen already complete
7. **BBB hardfilter** (TPSA<90, MW<450, 1≤logP≤4, HBD≤3) → bbb_filtered.csv
8. **Rank by cfd_pos** (PocketXMol's own pose confidence) — top 100
9. **Boltz-2 15-kinase panel** on top 100 (prefer localhost:8004 Boltz-2 Textworld)
   - LIMK1 (primary), LIMK2 (paralog, selectivity control),
   - ROCK1, ROCK2 (upstream partners),
   - JAK2, p38α, CDK5, ABL1, BRAF, SRC, MEK1, EGFR, AKT1, PKA, AURKB (off-targets)
10. **Compute z-score per row**: `z_LIMK1 = (iptm_LIMK1 − row_mean) / row_std`
11. **Top-5 by cfd_pos + BBB + z_LIMK1>0**
12. **Write DRAFT RESULTS.md** with selectivity-control framing
13. **triple_llm_verify** → upgrade DRAFT → VERIFIED if 3/3 PASS

## Quality Gates (HARD)

| Gate | Rule | Failure action |
|---|---|---|
| PDB TITLE verified | 5L6W = "LIMK1-ATPGAMMAS-CFL1 COMPLEX" | HALT if mismatch |
| Motif verified | K368+E384+D478 = K/E/D | HALT if any wrong |
| K–E salt bridge | 2.5–4 Å (active-state αC-IN) | Document if out of range |
| Smoke test | ≥3/5 valid SMILES + ≤15 s | HALT if silent-zero |
| BBB filter | Drop BBB_Martins-proxy hardfilter | (filter step) |
| Selectivity metric | **z-score per row**, NOT raw iptm margin | HARD RULE |
| Framing | RESULTS.md says "selectivity control for LIMK2" | Reject any standalone therapy claim |
| Status stays DRAFT | Until `triple_llm_verify` 3/3 PASS | No external comms |
| Not for Simon | LIMK1 activator has no SMA claim surface | NEVER send |

## Output manifest

| File | Purpose |
|---|---|
| /home/bryza/fleet-results/limk1_activator_alphaC/gen_info.csv | Raw PocketXMol 600 rows |
| /home/bryza/fleet-results/limk1_activator_alphaC/valid_smiles.csv | 181 valid SMILES |
| /home/bryza/fleet-results/limk1_activator_alphaC/bbb_filtered.csv | Post-BBB |
| /home/bryza/fleet-results/limk1_activator_alphaC/boltz2_panel.csv | 15-kinase iptm matrix |
| /home/bryza/fleet-results/limk1_activator_alphaC/top_hits.tsv | Ranked |
| /home/bryza/fleet-results/limk1_activator_alphaC/pocket_audit.json | Motif verification |
| /home/bryza/fleet-results/limk1_activator_alphaC/filter_log.jsonl | Per-gate counts |
| /home/bryza/sma-research/qms/limk1_activator_RESULTS.md | DRAFT report |

## Known risks

1. **K–E salt bridge is 2.67 Å in 5L6W** — this is αC-IN ACTIVE, which is the
   conformation we want to stabilize with an activator. Good.
2. **181/600 = 30% yield** — typical PocketXMol for non-familiar binding modes.
   Not a red flag.
3. **LIMK1 is cognition-linked (Williams syndrome)** — any cross-activity of
   LIMK2 leads at LIMK1 must be flagged as neurological risk, not a positive.
4. **ATP-γS + CFL1 both present in 5L6W** — we chose allosteric αC anchor, NOT
   the ATP site, so pocket anchor is distal from AGS. Acceptable.
5. **Previous agent killed on rate-limit** — Boltz-2 hosted NIM rate-limits
   hourly. Mitigation: prefer localhost:8004 self-host; fall back to hosted NIM
   only if self-host down.

---

**PRE-FLIGHT STATUS: PLAN WRITTEN | PocketXMol GEN: ✅ COMPLETE | FILTER + BOLTZ-2 + RESULTS: in progress**
