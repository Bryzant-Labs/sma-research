# ROCK1 ATP-Site Inhibitor Campaign — Pre-Flight Plan

**Status:** DRAFT (pre-flight)
**Date:** 2026-04-17
**Campaign ID:** `rock1_inhibitor_atp`
**Author:** Opus Master Agent
**Exploratory level:** LOW — ROCK1 inhibitors are well-characterized
(fasudil, ripasudil, Y-27632). This campaign is a **selectivity-control set**
for the ROCK2 programme, NOT a direct SMA therapy.
Framing: **reference chemotype bank** for LIMK2/ROCK2 selectivity gating.

## Framing and purpose

ROCK1 (UniProt Q13464) is the paralog of ROCK2 (O75116). Both phosphorylate
LIMK1/2 at Thr508/Thr505 to activate them. ~~The ROCK-LIMK2-CFL2 axis is the
therapeutic axis for SMA (3 datasets, memory).~~ **RETRACTED 2026-04-17**: per
the 3-dataset meta-analysis (`qms/meta_analysis/CORRECTED_SIGNATURE.md`), ROCK2
is pooled log2FC **−0.254** (DOWN, p=9.0e-5, I²=56%) in SMA MN, and ROCK1 is
pooled **−0.071** (I²=71%, NS). **ROCK1 inhibition has NO transcriptomic
rationale for SMA MN.** This campaign's SMA claim surface is explicitly empty
(see "Framing and purpose" below); it exists ONLY as a selectivity-control
reference chemotype bank for the LIMK2/ROCK2 programme, and that utility is
unaffected by the disease-direction retraction. See `qms/CORRECTIONS_LOG.md`
Incident 2026-04-17-001 + Audit-Event 002.

**Why we care for the LIMK2/ROCK2 programme:**
- Fasudil (ROCK inhibitor) is the existing SMA-relevance "tool compound"
  (Bowerman 2012 re-interpreted as muscle-mediated, not neuroprotective).
- ROCK1-**selective** inhibitor = **NOT** an SMA therapy. ROCK1 is tissue-wide
  (lung, vasculature, cardiomyocyte); selective inhibition has cardiovascular
  risk (hypotension, reflex tachycardia).
- The goal of a ROCK2-selective SMA programme requires discriminating against
  ROCK1. This campaign produces the ROCK1 reference chemotype bank.

**SMA claim surface:** none. This campaign contributes to selectivity gating
and scaffold diversity for the ROCK2 / LIMK2 programme. NOT a therapy claim.

## Target

| Parameter | Value | Source |
|---|---|---|
| Gene | ROCK1 | UniProt Q13464 |
| PDB | **2ESM** — verified TITLE: "CRYSTAL STRUCTURE OF ROCK 1 BOUND TO FASUDIL" | RCSB |
| Reference | Jacobs et al. J Biol Chem 2006 | PubMed 16556902 |
| Chain | A | PDB header (chains A, B present; A used) |
| Residue range | 6–405 (kinase domain) | PDB |
| Co-crystal ligand | M77 = fasudil (HA-1077) | HETATM |
| State | DFG-in (typical for fasudil) | Jacobs 2006 |
| Pocket strategy | **ATP site (orthosteric inhibitor)** | fasudil HETATM mean |
| Pocket center | **computed on-instance** = mean(M77 HETATM coords) | TBD |
| Pocket radius | 15 Å (reproducible with LIMK1 campaign) | PocketXMol SBDD convention |
| Molecule count | 600 | Christian's dispatch |
| Batch size | 100 | A100 40 GB (match LIMK1 run) |

### Motif sanity (post-hoc verification after pocket derivation)

- β3-Lys candidate: K105 (canonical kinase β3; verified on-instance)
- αC-Glu candidate: E124 (+19 from K105, verified on-instance)
- DFG-Asp candidate: D216 (HRD 198–200, DFG 216–218; verified on-instance)
- Expected K–E distance: 2.5–4 Å (DFG-in active site)
- Pocket center must be within 12 Å of all three CA (ATP site is between β3-K,
  αC-E, and DFG).

## Instance

| Parameter | Value |
|---|---|
| Host | `ssh7.vast.ai:17456` (root, key `~/.ssh/id_ed25519_vastai`) |
| GPU | 1× A100 SXM4 40 GB |
| PocketXMol | `/workspace/PocketXMol` (git SHA 65488cf) |
| Receptor PDB | `data/examples/smallmol/rock1_receptor.pdb` (already = 2ESM chain A) |
| Entry script | `scripts/sample_use.py` (NOT `_pdb` variant) |

## Workflow

1. **Probe GPU** — nvidia-smi (must be 0% util before burn)
2. **Fetch 2ESM** — /tmp/2ESM.pdb from RCSB to extract M77 HETATM coords
3. **Derive pocket center** = mean of M77 atom coords (fasudil center of mass)
4. **Sanity check**: center within 12 Å of K105-CA, E124-CA, D216-CA
5. **Write config** (rock1_atp.yml) with pocket_coord + radius 15
6. **Smoke test** (n=5, batch=5, expected 6–15 s) — verify non-zero output
7. **Full burn** (n=600, batch=100, expected 2–4 min) in tmux `pxm_rock1`
8. **Monitor GPU util > 60%** within 60 s
9. **Extract valid SMILES** → /home/bryza/fleet-results/rock1_inhibitor_atp/gen_info.csv
10. **BBB hardfilter** (TPSA<90, MW<450, 1≤logP≤4, HBD≤3) → bbb_filtered.csv
11. **Rank by cfd_pos** — top 100
12. **Boltz-2 15-kinase panel** on top 100
    - ROCK1 (primary), ROCK2 (paralog selectivity control)
    - LIMK1, LIMK2 (downstream partners)
    - JAK2, p38α, CDK5, ABL1, BRAF, SRC, MEK1, EGFR, AKT1, PKA, AURKB
13. **z-score per row**: `z_ROCK1 = (iptm_ROCK1 − row_mean) / row_std`
14. **Top-5 by cfd_pos + BBB + z_ROCK1 > 0**
15. **Compare to fasudil reference**: fasudil expected iptm on ROCK1 ≈ 0.85–0.92;
    any hit with iptm > 0.90 on ROCK1 is plausible in-pocket
16. **Write DRAFT RESULTS.md** with selectivity-control framing
17. **triple_llm_verify** → upgrade DRAFT → VERIFIED if 3/3 PASS

## Quality Gates (HARD)

| Gate | Rule | Failure action |
|---|---|---|
| PDB TITLE verified | 2ESM = "ROCK 1 BOUND TO FASUDIL" | HALT if mismatch |
| Motif verified | K105+E124+D216 = K/E/D | HALT if any wrong |
| Pocket center | within 12 Å of each of K105-CA, E124-CA, D216-CA | HALT if > 12 Å |
| Smoke test | ≥3/5 valid SMILES + ≤15 s | HALT; do not burn full |
| Full run | ≥100 valid SMILES | Investigate if < 100 |
| GPU util | >60% sustained after 60 s | Debug batch_size |
| BBB filter | Drop BBB_Martins-proxy hardfilter | (filter step) |
| Selectivity metric | **z-score per row**, NOT raw iptm margin | HARD RULE |
| ROCK2 selectivity gate | z_ROCK1 vs z_ROCK2 documented | (document direction) |
| Framing | RESULTS.md says "selectivity control for ROCK2/LIMK2" | Reject any standalone therapy claim |
| Status stays DRAFT | Until `triple_llm_verify` 3/3 PASS | No external comms |
| Not for Simon | ROCK1-selective has no SMA claim surface | NEVER send |

## Output manifest

| File | Purpose |
|---|---|
| /home/bryza/fleet-results/rock1_inhibitor_atp/gen_info.csv | Raw PocketXMol 600 rows |
| /home/bryza/fleet-results/rock1_inhibitor_atp/valid_smiles.csv | Valid SMILES only |
| /home/bryza/fleet-results/rock1_inhibitor_atp/bbb_filtered.csv | Post-BBB |
| /home/bryza/fleet-results/rock1_inhibitor_atp/boltz2_panel.csv | 15-kinase iptm matrix |
| /home/bryza/fleet-results/rock1_inhibitor_atp/top_hits.tsv | Ranked |
| /home/bryza/fleet-results/rock1_inhibitor_atp/pocket_audit.json | Motif verification + M77 center |
| /home/bryza/fleet-results/rock1_inhibitor_atp/filter_log.jsonl | Per-gate counts |
| /home/bryza/sma-research/qms/rock1_inhibitor_RESULTS.md | DRAFT report |

## Known risks

1. **Fasudil pocket is well-known** — we should rediscover fasudil-like
   chemotypes (isoquinoline-5-sulfonamide pattern). Absence of any isoquinoline
   in top-100 would be a red flag for PocketXMol.
2. **ROCK1 and ROCK2 are 92% identical in kinase domain** — sel_z for ROCK1 vs
   ROCK2 will likely be small for ATP-site inhibitors. This is expected and
   confirms the selectivity-control framing.
3. **Cardiac liability** — ROCK1 inhibition has known hypotension risk. No
   clinical relevance for this campaign, but documented for completeness.
4. **Previous agent killed on rate-limit + wrong script** — prior rock1 smoke
   used sample_pdb.py (which requires pandas and is NOT the task-briefed entry).
   Fix: use sample_use.py per brief.

---

**PRE-FLIGHT STATUS: PLAN WRITTEN | PocketXMol GEN: not started | SMOKE TEST: not started**
