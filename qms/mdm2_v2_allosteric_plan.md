# MDM2 V2 — Allosteric Activator Campaign — Plan

**Campaign ID**: `mdm2_activator_v2_allosteric`
**Instance**: A100 SXM4-40GB, Slovenia, ssh3:14116 (Vast 35124116 replacement)
**Launched**: 2026-04-17
**Status**: DRAFT (pending triple_llm_verify 3/3 PASS)

## Critical framing: V2 addresses V1 mechanistic paradox

- **V1 campaign (agent a0f84257, 2026-04-17 earlier)** targeted the Nutlin-3a orthosteric cleft on MDM2 (pocket center **[-23.835, 7.530, -14.053]**). Compounds binding that site act as **INHIBITORS** (competitive with p53 → stabilize p53 → WRONG direction for SMA where p53 is already UP +0.260, p=0.030).
- **V2 targets a DISTINCT allosteric site** that is hypothesized to ENHANCE MDM2-p53 ubiquitination turnover (reducing p53 apoptotic pressure in SMA MN).
- **Only wet-lab can distinguish** V1 orthosteric (likely inhibitors) vs V2 allosteric (potential activators). Both campaigns are archived; post-hoc triage = mandatory.

## Target

- **Protein**: MDM2 (E3 ubiquitin-protein ligase Mdm2, HDM2)
- **UniProt**: Q00987 (Homo sapiens, 491 aa full-length)
- **PDB**: **4HG7** — *"Crystal structure of an MDM2/Nutlin-3a complex"* (ALREADY TITLE-verified in V1)
- **Chain A**: MDM2 p53-binding domain, residues 17-125 (N-terminal domain only — C-terminal RING/acidic domain NOT in 4HG7)
- **Structural caveat**: 4HG7 only covers aa 17-125. MDM2's Lid domain (1-24) is partially present (aa 17-24 only); aa 1-16 and RING-domain 430-491 are absent. V2 uses the MOST ACCESSIBLE non-orthosteric region within the 17-125 envelope.

## Pocket derivation strategy (V2 — allosteric)

**V1 pocket center** (orthosteric Nutlin cleft): **[-23.835, 7.530, -14.053]** (mean of 40 NUT heavy-atom coords)

**V2 strategy**: identify an allosteric pocket ≥ 15 Å from V1 center, on the opposite face of the MDM2 N-terminal domain, with residue contacts that include Lid-adjacent residues (17-24) and/or the back-face β-sheet. Three candidate anchors considered:

1. **Lid-adjacent N-terminal face (aa 17-30)** — the visible Lid residues (17-24) plus the adjacent β-strand (25-30). This face is solvent-exposed in Nutlin-bound structures and has been proposed as an allosteric regulator of the p53-binding conformation (Bueren-Calabuig & Michel 2016; Showalter et al. 2008 NMR).
2. **Back-face opposite Nutlin cleft** — mirror-reflection of pocket center through MDM2 centroid. Purely geometric candidate.
3. **β2-β3 loop (residues 60-70)** — peripheral to the hydrophobic cleft but on a face distinct from F19/W23/L26 mimic subpockets.

**Decision**: COMBINE (1) + (3) — compute V2 pocket center as **mean CA of residues {20, 21, 22, 23, 24, 25, 28, 30, 62, 65, 68}** = Lid-anchor + β2-β3 loop convergence, on the back-face of the N-terminal domain. This is geometrically distant from V1 (expected > 15 Å) and overlaps no Nutlin-hotspot residue (F19/W23/L26 are the subpocket-defining sidechains of the Nutlin cleft — we deliberately exclude them).

**Verification on-instance (MANDATORY before launch)**:
- Compute V2 pocket center from chosen residue CAs
- Compute `distance(V1_center, V2_center)` — **MUST be > 15 Å**
- Identify closest anchor residues to V2 center (5 Å sphere)
- Confirm F19, W23, L26 CA are each > 10 Å from V2 center (Nutlin-hotspot exclusion)

## Rationale (SMA)

1. **Meta-analysis finding** (2026-04-17): TP53 pooled expression = +0.260, p = 0.030 across 3 SMA MN datasets. p53-downstream apoptosis markers (PERP, PUMA, NOXA) elevated.
2. **Therapeutic direction**: REDUCE p53 apoptotic pressure on MN → **MDM2 ACTIVATOR** (increase p53 ubiquitination + proteasomal turnover).
3. **Why allosteric, not orthosteric**: Nutlin-cleft binders **block** p53-MDM2 binding → p53 stabilized → opposite of what SMA MN needs. Allosteric site binders can **stabilize** the p53-bound productive conformation (enhance turnover) without blocking p53 access.
4. **First-in-class (again)**: NO clinical-stage MDM2 activator, allosteric or orthosteric. Both V1 and V2 are exploratory chemotype-generation for a novel therapeutic direction.
5. **Lid domain biology**: MDM2 Lid (1-24) regulates p53-binding affinity via autoinhibition. Ligands that stabilize the "Lid-open for p53" conformation theoretically enhance MDM2 processivity.

## Compute

- **Instance**: ssh3:14116 (A100 SXM4 40GB, Slovenia, Vast 35124116 — replacement; same warm state as V1 earlier today)
- **Warm state**: PocketXMol at `/opt/PocketXMol` (SHA `65488cf635c856101dbe703ac97e2f10f58e005c`), conda env `pxm_cu128` active, weights cached, 4HG7 already fetched to `/root/mdm2_work/`
- **n_molecules**: 600
- **batch_size**: 50
- **Smoke**: 5-mol first
- **tmux session**: `pxm_mdm2_v2`
- **GPU util target**: > 60%
- **Pocket radius**: 10.0 Å (match V1 for direct comparison)

## Post-generation pipeline

1. RDKit sanity + QED/Lipinski filter
2. **BBB hardfilter** (< 0.5 drop) — SMA MN target requires CNS penetration
3. Top 100 → STAGE Boltz-2 queue (`boltz2_queue.jsonl`, do NOT launch from agent):
   - **Primary**: MDM2 (Q00987) 4HG7 chain A
   - **Mechanism probe**: co-screen vs MDM2-p53 peptide complex (PDB 1YCR) — compounds that DO NOT displace p53 (high ipTM with p53 bound) = allosteric candidates; compounds that displace p53 = acting like V1 (orthosteric inhibitors)
   - **Off-target panel**: MDMX/MDM4 (O15151) — MDM2 paralog, want MDM2-selective
   - **Negative controls**: unrelated E3 ligases (MDM4, BIRC3, TRIM28)
4. Z-score selectivity: `z_MDM2 > 0` AND `z_MDM2 > z_MDM4` (paralog-selective)
5. DRAFT stays DRAFT until triple_llm_verify 3/3 PASS

## V2 vs V1: pocket location, expected mechanism, validation path

| Dimension | V1 (orthosteric) | V2 (allosteric) |
|---|---|---|
| Campaign ID | `mdm2_activator` | `mdm2_activator_v2_allosteric` |
| Pocket anchor | Mean of 40 NUT heavy atoms | Mean CA of Lid-anchor + β2-β3 loop residues |
| Pocket center | [-23.835, 7.530, -14.053] | TBD (on-instance) |
| Distance V1↔V2 | 0 Å | MUST be > 15 Å (HARD gate) |
| Hotspot residues | F19, W23, L26 (Nutlin mimic) | 20-30 Lid + 62-68 β-loop; F19/W23/L26 excluded |
| Expected mechanism | p53-MDM2 **competitive inhibition** | **Allosteric modulation** of Lid / conformational stabilizer |
| Direction for SMA | WRONG (stabilizes p53, we want less p53) | HYPOTHESIZED RIGHT (enhances MDM2 turnover) |
| Clinical precedent | Extensive (Nutlin, idasanutlin, HDM201, RG7112) | ZERO — first-in-class |
| Validation required | Biochemical p53-MDM2 displacement (likely PASS = INHIBITOR) | In-cell p53 half-life + K48-Ub-p53 ELISA (ONLY way to confirm activator direction) |

**OPEN QUESTION (documented as such)**: which arm (V1 orthosteric vs V2 allosteric) gives real MDM2-activator activity — not determinable from compute alone. Both arms must be wet-lab triaged for mechanism (p53 half-life reduction = activator; p53 stabilization = inhibitor) before any external comms.

## Risks / honest caveats

- **4HG7 is only aa 17-125**: true full-length MDM2 allosteric sites (C-terminal acidic 230-300, RING 430-491) are NOT in 4HG7. V2 is restricted to the N-terminal domain allosteric space. A follow-up campaign on MDM2 full-length AlphaFold model would cover C-terminal allostery.
- **V2 pocket is smaller / shallower**: Lid+β-loop surface is more exposed than Nutlin cleft. Expected lower hit rate.
- **Hypothesis-driven, not validated**: "Lid stabilization = activator" is plausible biochemistry but NOT established in clinical or wet-lab drug-discovery literature. The "allosteric activator" direction is inferred, not proven.
- **Mechanism-inversion risk**: an allosteric pocket binder could STILL act as a non-competitive p53-MDM2 inhibitor (reduce MDM2 conformational dynamics → reduce substrate processivity). Mechanistic triage is essential.
- **Distance > 15 Å is geometric only**: geometric distance does not guarantee functional distinction. Allostery is defined by functional coupling, not spatial separation.
- **EXPLORATORY ONLY**: no external comms about MDM2 activators until wet-lab mechanism confirmation.

## File layout

- Plan: `/home/bryza/sma-research/qms/mdm2_v2_allosteric_plan.md` (this file)
- V1 plan: `/home/bryza/sma-research/qms/mdm2_activator_plan.md`
- V1 RESULTS: `/home/bryza/sma-research/qms/mdm2_activator_RESULTS.md`
- Task JSON: `/home/bryza/sma-research/qms/mdm2_v2_allosteric_task.json`
- Pocket script (on instance): `/root/mdm2_v2_work/pocket_v2_derive.py`
- PocketXMol outputs (on instance): `/results/pocketxmol/mdm2_activator_v2_allosteric/`
- Local mirror: `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/`
- RESULTS doc: `/home/bryza/sma-research/qms/mdm2_v2_allosteric_RESULTS.md` (DRAFT)
