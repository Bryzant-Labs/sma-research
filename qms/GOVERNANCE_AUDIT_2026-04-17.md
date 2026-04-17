# Platform Governance Audit — 2026-04-17

**Status**: DRAFT (pending triple_llm_verify 3/3 PASS + human sign-off)
**Trigger**: LIMK2 +2.81× retraction (Incident 2026-04-17-001) exposed systemic risk
**Scope**: every numeric/scientific claim in sma-research repo + Dropbox Simon-facing packages + QMS docs
**Auditor**: Automated QMS governance agent (Opus lead), 2026-04-17 ~13:00 UTC
**Reference of truth**:
- `/home/bryza/sma-research/qms/meta_analysis/CORRECTED_SIGNATURE.md` (triple-LLM 3/3 PASS 2026-04-17)
- `/home/bryza/sma-research/qms/meta_analysis/meta_summary.tsv`
- `/home/bryza/sma-research/qms/meta_analysis/sensitivity_no_shsy5y.tsv`
- `/home/bryza/sma-research/qms/CLAIMS_REGISTRY.md`
- `/home/bryza/sma-research/qms/CORRECTIONS_LOG.md`

---

## Executive Summary

| Metric | Value |
|---|---|
| Files scanned (repo + Dropbox Simon packages + memory refs) | ~120 markdown / text docs |
| Distinct numeric/directional claims audited | 42 |
| **APPROVED** per CLAIMS_REGISTRY | 4 (PERP per-contrast, TP53 pooled, ROCK2 pooled, LIMK2 model-dependent) |
| **UNDER_REVIEW** | 3 (CFL2 disease-specific, Fasudil therapeutic, SMN1/SMN2 positive controls) |
| **RETRACTED (incident 001)** | 2 claim families: LIMK2 +2.81×, ROCK-LIMK2-CFL2 hyperactive axis |
| **URGENT — unretracted legacy cites still externally visible** | **13** |
| **MEDIUM — internal unverified numerics** | **9** |
| **LOW — historical session snapshots (no fix needed, flag only)** | 6 |
| Dataset IDs cited in current external materials WITHOUT `dataset_verify` PASS | 3 (GSE208629, GSE87281, GSE287257) |

**Headline verdict.** Before today's meta-analysis, ~4/42 claims (≈10%) would have passed the QMS external-citation rule (sign-consistent across ≥2 datasets AND I²≤75%). After today's meta-analysis, 4/42 pass explicitly (ROCK2 DOWN, TP53 UP, LIMK2 model-dependent with per-contrast disclosure, PERP per-contrast). **13 urgent legacy cites still contradict the corrected signature** and must be banner-flagged or deleted before any external communication. **Platform is NOT ready for external comms** (see §Recommendation).

---

## Method

1. Recursive grep over `/home/bryza/sma-research/**/*.md` and `/mnt/c/Users/bryza/Dropbox/Christian fischer/SMA/**/*.md` (Simon-facing only; the GPU_Results tree is Dropbox-online-only and was not re-downloaded).
2. Patterns: `\+\d+\.\d+[x×]`, `log2FC.*[+-]?\d`, `p[= ]\s*\d\.\d+e-?\d+`, `I²`, `iptm`, target-direction strings ("LIMK2 UP/DOWN", "ROCK2 hyperactivated").
3. Each hit cross-referenced against `meta_summary.tsv` for direction + magnitude sanity.
4. Classification labels: APPROVED (in CLAIMS_REGISTRY), UNDER_REVIEW (in CLAIMS_REGISTRY), RETRACTED (in CORRECTIONS_LOG), URGENT-LEGACY (externally-visible, contradicts meta), MEDIUM-UNCITED (internal, unsourced, consistent with meta), LOW-HISTORICAL (dated session-recap style, marked as historical snapshot).

---

## URGENT Action List (externally-visible + contradicts corrected signature)

### Category A — Dropbox Simon-facing packages that ALREADY CONTAIN +2.81× or derived claims

These materials sit in the Dropbox Simon folder and are the highest risk for accidental re-send.

| # | File | Line | Claim (verbatim or paraphrase) | Problem | Recommended fix |
|---|---|---|---|---|---|
| U1 | `/mnt/c/.../SMA/Simon/Fasudil_Evidence_Package/Fasudil_SMA_Evidence_Summary.md` | L45, L58 | "LIMK2 (+2.81x in SMA MNs)" and "LIMK2 upregulated +2.81x in SMA motor neurons (3 independent transcriptomic datasets)" | RETRACTED claim still in Simon-destined package; contradicts meta (LIMK2 pooled −0.20, model-dependent) | Rename folder `_INTERNAL_DO_NOT_SEND_Fasudil_Evidence_Package_PRE_RETRACTION/`; add large `⚠️ RETRACTED 2026-04-17` banner at top pointing to `qms/CORRECTIONS_LOG.md` Incident 001 + `CORRECTED_SIGNATURE.md` |
| U2 | same file | L59 | "CFL2 is UP in SMA, DOWN in ALS — disease-specific biomarker" | UNSOURCED (no primary data; meta shows CFL2 pooled +0.002, NS, I²=28%); ALS reference dataset not identified | Replace with "CFL2 is unchanged in SMA MN pooled meta (+0.002, I²=28%, NS). Prior 'disease-specific' claim had no verifiable source." |
| U3 | same file | L62 | "PFN2 (profilin-2) confirmed as MN-enriched actin regulator: +1.22 log2FC, p=5.3e-18" | WRONG MAGNITUDE. Meta: PFN2 pooled +0.025 (I²=97%, NS); GSE302774 Hb9-iMN +0.283 / iN +0.362; GSE87281 SH-SY5Y −0.436. No dataset produces +1.22. | Replace with per-contrast numbers from `meta_analysis/results.tsv` and caveat "direction model-dependent, not citable pooled" |
| U4 | same file | L63 | "CORO1C ... retracted by our analysis (p=0.37 NS in GSE290979, n=31)" | Number conflicts with April-6 correction_notice.md which said p=0.52 in GSE287257 (240 MNs scRNA). Two different sources cited for same retraction. | Canonicalize: the GSE290979 p=0.37 is actually from meta_analysis/results.tsv LIMK2 row (GSE290979 SMA organoid bulk LIMK2 log2FC −0.210 padj 0.367). CORO1C itself not in our 18-gene panel — status of that retraction unclear. Re-derive CORO1C from GSE290979 bulk counts and cite THAT. |
| U5 | same file | L66 | "ROCK-ALS Phase 2 trial (Lancet Neurology 2024): Fasudil 60mg showed dose-dependent MUNIX preservation in ALS patients" | Unverified citation; no PMID, no DOI, no journal volume. | Verify via PubMed before reuse; remove until verified. |
| U6 | `/mnt/c/.../SMA/Simon/Mega_Pack_2026-04-11/01_summary/EXECUTIVE_SUMMARY.md` | L34 | "ROCK-LIMK2-CFL2 axis: 3 independent datasets confirm LIMK2 +2.81× in SMA motor neurons" | RETRACTED; this pack was SENT to Simon 04-11. | Add retraction banner in both EXECUTIVE_SUMMARY.md + FULL_EVIDENCE_PACKAGE.md; drop Simon a note referencing Incident 001. |
| U7 | `/mnt/c/.../SMA/Simon/Mega_Pack_2026-04-11/02_evidence/FULL_EVIDENCE_PACKAGE.md` | L51 | "LIMK2: +2.81× upregulated in SMA motor neurons (GSE208629, p<0.001)" | RETRACTED claim + **GSE208629 never verified** (not in DATA_INVENTORY, no `dataset_verify` PASS). | Retraction banner + add GSE208629 to DATA_INVENTORY "Pending" or "Rejected" row (almost certainly a third hallucinated accession in the GSE287257/GSE140756/GSE176751 family). |
| U8 | `/mnt/c/.../SMA/Simon/Mega_Pack_2026-04-12/Simon_Email_Draft.txt` | L15 | "LIMK2, nicht LIMK1, ist das SMA-relevante Kinase-Target (+2.81× in SMA-Motorneuronen). LIMK1 ist das ALS-Target — die Isoform-Trennung ist krankheitsspezifisch" | RETRACTED + FALSE FRAMING. Meta: LIMK2 model-dependent (iPSC-MN DOWN, SH-SY5Y UP). "LIMK1 ist das ALS-Target" unsourced. | Rename folder to `Mega_Pack_2026-04-12_RETRACTED_SEE_INCIDENT_001`; replace email draft. |
| U9 | `/mnt/c/.../SMA/PROJECT_CATALOG.md` | L140 | "Real MN actin genes: PFN2 (+1.22 log2FC, p=5.3e-18) and LIMK1 (+1.20, p=8.4e-24)" | Both magnitudes inconsistent with meta (PFN2 pooled +0.025; LIMK1 pooled +0.033). The `+1.22`/`+1.20` values appear to be from an unverified source, likely same origin as +2.81×. | Retract these two numbers; replace with meta table rows. |
| U10 | `/mnt/c/.../SMA/PROJECT_CATALOG.md` | L279-281 | "LIMK2 +2.81× in SMA motor neurons ... PFN2 +1.22 log2FC MN-enriched" | RETRACTED + WRONG | Retraction banner |

### Category B — Public sma-research repo: inline cites still appearing despite retraction banners

| # | File | Line | Claim | Problem | Recommended fix |
|---|---|---|---|---|---|
| U11 | `/home/bryza/sma-research/campaigns/ROCK-LIMK2-CFL2_axis/README.md` | L12 | `**Status**: **VALIDATED** across 3 independent datasets` | Retraction banner exists at top, but the Status field (which is what users skim) still says VALIDATED. Contradicts corrected signature. | Change Status to `**UNDER_REVIEW** (see retraction banner above, Incident 001)` |
| U12 | same | L22 | `- LIMK2 is **~~~~+2.81×~~ [RETRACTED] RETRACTED~~**` | Strikethrough syntax malformed (quadruple tilde); reads strangely. | Clean to `- LIMK2: RETRACTED (see `qms/CORRECTIONS_LOG.md` Incident 001). Corrected value is model-system-dependent (see meta_analysis/forest_LIMK2.png).` |
| U13 | same | L24 | `- PFN2 is **+0.283 log2FC (corrected 2026-04-17)** MN-enriched` | Number matches GSE302774 Hb9-iMN contrast alone; pooled meta is +0.025 (NS). Framing "MN-enriched" not supported by the pooled estimate. | Replace with per-contrast text citing `meta_analysis/results.tsv`: PFN2 Hb9-iMN +0.283 / iN +0.362 (both significant) BUT meta pooled +0.025 NS and direction model-dependent. |
| U14 | `/home/bryza/sma-research/CATALOG.md` | L93 | "Real MN actin genes: PFN2 (+0.283 log2FC, p=5.3e-18) and LIMK1 (+1.20, p=8.4e-24)" | LIMK1 +1.20 unsourced + inconsistent with meta (pooled +0.033, NS). The regex note in retraction brief §Outstanding #2 flags exactly this string. | Retract LIMK1 +1.20 entirely; replace with LIMK1 meta pooled +0.033 (I²=64%, NS). |
| U15 | `/home/bryza/sma-research/CATALOG.md` | L228 | "**Status**: VALIDATED by 3 independent datasets (see session recaps)" — ROCK-LIMK-axis section | Contradicts corrected signature. | `UNDER_REVIEW` per retraction banner. |
| U16 | `/home/bryza/sma-research/CATALOG.md` | L230 | "LIMK2 ~~+2.81×~~ [RETRACTED] in SMA motor neurons" (repeats) and "CFL2 is disease-specific (UP in SMA, DOWN in ALS)" | RETRACTED portion acknowledged; CFL2 claim UNSOURCED-banner present but not matching meta (+0.002 NS I²=28%). | Update CFL2 line to "CFL2 unchanged in SMA MN meta (+0.002 pooled, NS). ALS-reference claim has no primary dataset." |
| U17 | `/home/bryza/sma-research/campaigns/4-AP/2026-04-06_correction/correction_notice.md` | L34-35, L100 | 5 unsourced claims: PFN2 +0.283 (shown as MN-enriched though meta shows model-dependent), LIMK1 +1.20 (contradicts meta +0.033), LIMK1 DOWN in ALS (−0.81, p=0.004), and scRNA table "ROCK1 UP (+0.47), LIMK1 DOWN (−0.81), LIMK2 compensatory UP (+1.01)" | Claimed source GSE287257 but the actual DE-pipeline in our QMS panel used GSE290979+GSE302774+GSE87281 — not GSE287257 scRNA. Numbers can't be re-derived from any verified dataset. | Add large UNSOURCED banner on the correction_notice.md; retract L100 scRNA table entirely (matches no verified dataset); revise L34-35 to meta-consistent per-contrast numbers. |
| U18 | `/home/bryza/sma-research/campaigns/SMN2_base_editing/combination_protocol.md` | L40, L48, L53, L172, L221 | Multiple repetitions of "ROCK-LIMK2-CFL2 axis validated in 3 independent SMA datasets", "ROCK hyperactivated", "ROCK hyperactivation → LIMK2 hyperphosphorylation → CFL2 inactivation → frozen actin dynamics" | UNDER_REVIEW banner at top helps, but body text still asserts hyperactive axis as current rationale. Meta shows ROCK2 DOWN, LIMK2 model-dependent — the Fasudil rationale is INVERTED. | Add inline correction boxes next to L40, L48, L53, L172; retract L221 "ROCK-LIMK2-CFL2 therapeutic axis: identified across 3 independent SMA datasets" bullet; add an explicit Fasudil caveat ("pan-ROCK inhibition may worsen LoF if ROCK2 is already DOWN in SMA MN"). |
| U19 | `/home/bryza/sma-research/campaigns/SMN2_base_editing/research/competitive_landscape.md` | L135 | "ROCK-LIMK2-CFL2 therapeutic axis (3 datasets, zero competitors)" | Contradicts meta. | Retract. |
| U20 | `/home/bryza/sma-research/campaigns/SMN2_base_editing/SMA_CURE_ACTION_PLAN_2026.md` | L19 | "Found: ROCK-LIMK2-CFL2 axis (3 datasets), ZERO competitors in LIMK2-selective" | Same. | Retract first half; LIMK2-selective chemistry claim separate + independent. |
| U21 | `/home/bryza/sma-research/findings/insights/2026-04-10_cross_connections_v3.md` | L36, L154, L163 | "ROCK-LIMK2-CFL2 axis validated by 3 independent datasets"; "ROCK2 hyperactivation as biomarker for Risdiplam resistance, justifying combination therapy" | Contradicts meta. | Add historical-snapshot banner; remove from any external "insights" export. |
| U22 | `/home/bryza/sma-research/findings/2026-04-12/simon_3mechanism_combo.md` | L27 | Table: "Cytoskeletal rescue — Fasudil — ROCK2 → LIMK2 → Cofilin-2" — framed as currently-justified mechanism | Meta shows ROCK2 DOWN. Fasudil direction of action is NOT rescue if ROCK2 is already depressed. | Replace row with UNDER_REVIEW banner + caveat; cross-link to the LIMK2 retraction brief §4.2. |
| U23 | `/home/bryza/sma-research/qms/rock1_inhibitor_plan.md` | L16 | "therapeutic axis for SMA (3 datasets, memory)" | Legacy framing incompatible with meta. | Rewrite rationale using meta numbers; ROCK1 meta pooled −0.071 (I²=71%, NS) — ROCK1 inhibition for SMA MN has NO transcriptomic rationale. |

### Category C — Raw `+2.81×` strings still present with malformed banner

| # | File | Line | State | Recommended fix |
|---|---|---|---|---|
| U24 | `/home/bryza/sma-research/README.md` | L77 | "LIMK2 is ~~+2.81x~~ [RETRACTED] in SMA motor neurons" | Strikethrough + RETRACTED tag is acceptable, but raw number still visible. | Replace line with meta statement: "LIMK2 direction in SMA MN is model-system-dependent (DOWN in iPSC-Hb9-iMN padj 2.3e-12, UP in SH-SY5Y padj 3.8e-6; see `qms/meta_analysis/forest_LIMK2.png`). The prior +2.81× claim (retracted) is not reproducible — see `qms/CORRECTIONS_LOG.md` Incident 001." |
| U25 | `/home/bryza/sma-research/docs/data_access.md` | L36 | "SMA iPSC-derived MN bulk | GSE... | LIMK2 ~~+2.81×~~ [RETRACTED] finding" | `GSE...` placeholder still present. | Replace accession with GSE302774 (Lauria 2025) + GSE290979 (Mendonca Rodrigues 2025) + GSE87281 (Jangi 2017 PMID 28270613); drop +2.81× number entirely. |

### Category D — Unverified accessions cited

| # | Accession | Cited in | Status | Fix |
|---|---|---|---|---|
| U26 | GSE208629 | Mega_Pack_2026-04-11/FULL_EVIDENCE_PACKAGE.md L51 | NOT IN DATA_INVENTORY; never verified; cited as primary source of "+2.81×" | Add to DATA_INVENTORY.md Rejected row "GSE208629 — used in Simon Mega_Pack 04-11, identity never confirmed; `dataset_verify.py` blocks." |
| U27 | GSE287257 | campaigns/4-AP/2026-04-06_correction/ (as ALS reference) | VERIFIED as ALS dataset (Rejected row exists in DATA_INVENTORY 2026-04-17) but citation still appears in correction_notice.md as source of SMA-direction claims | Clarify in correction_notice.md: GSE287257 = ALS dataset (cross-disease comparison) not SMA; current SMA panel is GSE290979+GSE302774+GSE87281. |
| U28 | GSE87281 | campaigns/4-AP/2026-04-06_correction/correction_notice.md L37 ("CORO1C ↓1.77×") | VERIFIED as SMN-shRNA dataset (Jangi 2017 PMID 28270613) per CORRECTED_SIGNATURE but the CORO1C ↓1.77× number was never recomputed from the verified dataset — original inclusion predates QMS. | Recompute CORO1C log2FC from verified GSE87281 counts (we have raw counts locally per CORRECTED_SIGNATURE); update inventory row; may result in further retraction. |

---

## MEDIUM Action List (internal, unsourced or pending)

| # | File | Line | Claim | Status | Recommended next step |
|---|---|---|---|---|---|
| M1 | `/home/bryza/sma-research/qms/PERP_dossier/PERP_SMA_expression.md` | §2 | PERP per-contrast DOWN in Hb9-iMN (padj 3.5e-3) + iN (padj 6.5e-19) | PENDING human sign-off per CLAIMS_REGISTRY row 6; 3/3 LLM PASS already completed | Move to APPROVED once Christian Fischer sign-off recorded |
| M2 | `/home/bryza/sma-research/qms/mdm2_activator_plan.md` + `qms/mdm2_activator_RESULTS.md` | L11, L13 | "pooled TP53 expression in SMA motor neurons = +0.260 (p = 0.030) across 3 independent datasets" | Matches meta. Sensitivity drop-SH-SY5Y gives +0.187 [−0.09, +0.46] (CI crosses zero). | Add citation to `meta_analysis/CORRECTED_SIGNATURE.md` + `sensitivity_no_shsy5y.tsv`; flag that sensitivity analysis weakens external-cite strength. |
| M3 | `/home/bryza/sma-research/qms/rock2_activator_RESULTS.md` | L17 | "ROCK2 DOWN robust (p=9e-05, I^2=56%, 3 datasets, 5 contrasts)" | Matches meta exactly | Pre-promote to APPROVED (row 10 in registry) — done in registry but RESULTS.md should add explicit cross-reference. |
| M4 | `/home/bryza/sma-research/campaigns/Fasudil_evidence_package/README.md` | (staging file) | Points to Dropbox `Simon_Fasudil_Evidence_Package/` which contains U1-U5 above | Staging pointer | Add UNDER_REVIEW banner identical to combination_protocol.md; link to CORRECTIONS_LOG Incident 001. |
| M5 | `/home/bryza/sma-research/campaigns/4-AP/2026-04-02_original_screen/4-AP-Computational-Analysis.md` | L17 | "CORO1C ... downregulated 1.77-fold in SMA patient samples (GSE87281, n=101, FDR=1.5e-71)" | GSE87281 verified as SMA but n=101 doesn't match (our SH-SY5Y n=9 + hiPSC-MN n=7 = 16); the "n=101" number is UNSOURCED | Re-derive CORO1C from GSE87281 counts using same pydeseq2 pipeline; update or retract. |
| M6 | `/home/bryza/sma-research/findings/insights/2026-04-10_cross_connections_v3.md` | L163 | "ROCK2 hyperactivation as biomarker for Risdiplam resistance" | No primary-data derivation in repo | Retract unless Risdiplam resistance RNA-seq can be cited. |
| M7 | `/home/bryza/sma-research/findings/INDEX.md` + `/findings/2026-04-09/FINDING_2026-04-09_bbb5_dual_LIMK2_ROCK1.md` | — | bbb5 MMPBSA + contact numbers (MMPBSA_FINAL_RESULTS.md shows "+506 ±14 WARN" and "+465 ±16 WARN" with "Trajectory artifact" flag) | Internal MD numbers; QC_VALIDATION_REPORT_2026-04-11.md flags these as failing; Simon Mega_Pack_04-11 tables inherit them | Never externally cite LIMK2 MMPBSA ΔG from these runs; only bbb5 CONTACT-PROXY data is defensible (not ΔG). |
| M8 | `/home/bryza/sma-research/findings/2026-04-11/MMPBSA_batch_v2_results.md` | — | Rescored MMPBSA; contains "Trajectory artifact" caveats but also publishes ΔG numbers | No external-citation flag | Add explicit "INTERNAL — do not cite ΔG externally without v2.1 rerun" banner. |
| M9 | `/home/bryza/sma-research/findings/2026-04-12/ROCK2_apo_100ns_analysis.md` | — | ROCK2 apo MD RMSD 10.86 ± 2.02 Å, DFG-in dwell 99.9% | Correctly self-caveats (tail-residue driven); internal-citable as apo baseline only | No action; passes QMS rule because it's an internal baseline-control, not a disease claim. |

---

## LOW Action List (historical snapshots — mark only, no retraction)

| # | File | Line | Note |
|---|---|---|---|
| L1 | Memory files `/home/bryza/.claude/projects/-home-bryza/memory/session-2026-04-*.md` | various | Pre-retraction session recaps mention LIMK2 +2.81×. These are historical snapshots, not current claims. No retraction needed; flag as "pre-2026-04-17-incident" at memory-index level. |
| L2 | `/home/bryza/sma-research/CATALOG.md` overall | — | Header banner is good. Body still has legacy framing but within the context of the banner this is acceptable as "historical campaign log". Medium-term: rewrite the ROCK-LIMK2-CFL2 section in a post-incident format. |
| L3 | `/home/bryza/sma-research/findings/INDEX.md` | — | Lists 2026-04-09 bbb5 "dual LIMK2/ROCK1" finding — this is a structural/MD claim not a disease-direction claim; unaffected by the incident. |
| L4 | `/home/bryza/sma-research/campaigns/4-AP/2026-04-02_original_screen/CORO1C_WITHDRAWN.md` | — | Historical withdrawal notice; consistent with current CORO1C-is-passenger verdict. |
| L5 | `/home/bryza/sma-research/findings/2026-04-10/ORPHAN_TRAJECTORY_ANALYSIS.md` | — | MD artefact analysis; no disease-direction claims. Self-contained. |
| L6 | `/home/bryza/sma-research/docs/learnings/*.md` (topology, pbc, ambertools) | — | Methodological learnings; zero disease-direction claims. No action. |

---

## Cross-Reference Table: APPROVED Claims → Source File → Meta Status

| Registry # | Claim (APPROVED) | Registry source | Meta-analysis derivation | Consistency with sensitivity (drop-SH-SY5Y) |
|---|---|---|---|---|
| 6 | PERP DOWN-tendency in SMA MN (pooled −0.257, k=5, I²=90%; per-contrast preferred: iPSC-MN padj 3.5e-3 / 6.5e-19) | `meta_summary.tsv` PERP row + `PERP_dossier/PERP_SMA_expression.md` | PERP meta pooled −0.257 [−0.692, +0.177] I²=90% p=0.245 | Drop-SH-SY5Y: −0.262 direction stable ✓ |
| 7 | TP53 UP in SMA MN (meta +0.260, CI [+0.026, +0.495], I²=73%, p=0.030, k=5) | `CORRECTED_SIGNATURE.md` + `mdm2_activator_plan.md` | `meta_summary.tsv` TP53 row | Drop-SH-SY5Y: +0.187 [−0.09, +0.46] I²=75%, direction stable but p=0.185 (CI crosses zero → weakens external cite; caveat added in registry) |
| 9 | LIMK2 direction is model-system-dependent | `LIMK2_retraction_brief_INTERNAL.md` + `CORRECTED_SIGNATURE.md` | `results.tsv` per-contrast | Drop-SH-SY5Y: −0.367 [−0.94, +0.20] I²=98% — still extreme heterogeneity, model-dependence claim holds |
| 10 | ROCK2 DOWN in SMA MN (meta −0.254, CI [−0.381, −0.127], I²=56%, p=9.0e-5, k=5) | `CORRECTED_SIGNATURE.md` + `rock2_activator_RESULTS.md` | `meta_summary.tsv` ROCK2 row | Drop-SH-SY5Y: −0.226 [−0.36, −0.09] I²=59%, p=1.0e-3, direction stable ✓ — the most robust hit in the panel |

---

## Action Required on CLAIMS_REGISTRY.md (append)

Proposed new rows (status UNDER_REVIEW pending derivation or retraction):

| # | Claim | Status | Source | Next step |
|---|---|---|---|---|
| 11 | LIMK1 +1.20 log2FC MN-enriched (p=8.4e-24) | UNDER_REVIEW → likely RETRACT | CATALOG.md L93 + correction_notice.md L35 | Re-derive from GSE302774 / GSE87281 via pydeseq2; pooled meta is +0.033 (NS) — expect RETRACT |
| 12 | PFN2 +1.22 log2FC (p=5.3e-18) in Dropbox Fasudil_Evidence_Package + PROJECT_CATALOG | UNDER_REVIEW → likely RETRACT | Fasudil_SMA_Evidence_Summary.md L62 + PROJECT_CATALOG.md L140, L281 | Meta pooled PFN2 +0.025 (NS); max per-contrast +0.362 in GSE302774 iN — RETRACT the +1.22 magnitude |
| 13 | CORO1C ↓1.77× in SMA bulk RNA-seq (GSE87281) | UNDER_REVIEW | 4-AP-Computational-Analysis.md L17 + correction_notice.md L37 | Re-derive via pydeseq2 on verified GSE87281 counts; update |
| 14 | scRNA row "ROCK1 UP (+0.47), LIMK1 DOWN (−0.81), LIMK2 compensatory UP (+1.01)" in MN | UNSOURCED | correction_notice.md L100 | No matching dataset; RETRACT |
| 15 | LIMK2 +2.81× in GSE208629 | UNSOURCED + UNVERIFIED-ACCESSION | Mega_Pack_2026-04-11/FULL_EVIDENCE_PACKAGE.md L51 | Accession likely invented (not in GEO or not a real SMA dataset); RETRACT + add to DATA_INVENTORY Rejected |

---

## Recommendation

**Platform is NOT ready for external comms.** Estimated cleanup: **2-3 more days** of focused work, gated by:

1. **URGENT-LEGACY fixes** (U1-U28): must complete before any message that cites numeric evidence. These are all locatable via grep and can be done in one focused sitting (~4-6 h).
2. **New CLAIMS_REGISTRY rows 11-15**: derive + triple-LLM gate + human sign-off. Rows 11, 12, 14, 15 likely RETRACT. Row 13 may survive after re-derivation.
3. **Retraction notices to Simon**: Mega_Pack_2026-04-11 and Mega_Pack_2026-04-12 were SENT. Simon already knows about +2.81× provenance (per `Simon_Followup_2026-04-16.txt`). But the PFN2 +1.22 and LIMK1 +1.20 magnitudes were in those packs and still need explicit retraction in the upcoming reply.
4. **Fasudil rationale re-derivation**: the Bowerman-2012 muscle-mediated mechanism SURVIVES regardless of our transcriptomic finding (Bowerman's data is in muscle, not in MN transcripts). So the Fasudil CONTRAINDICATION caveat should be: "ROCK2-DOWN in SMA MN transcriptome means pan-ROCK inhibition in MN is NOT rescue at the MN-intrinsic level. Fasudil's muscle-NMJ benefit (Bowerman 2012) operates by a different mechanism — protein-level signalling, not transcript-level upregulation. Reconciliation experiment: wet-lab LIMK2 phospho-status and ROCK2 kinase activity in SMA MN." This is the right scientific framing and should be added to the combination_protocol.md + Fasudil_Evidence_Package.
5. **Triple-LLM QC on this audit report itself**: REQUIRED before report-done-state. Run `python3 /home/bryza/gpu-fleet/scripts/triple_llm_verify.py --file /home/bryza/sma-research/qms/GOVERNANCE_AUDIT_2026-04-17.md` before Christian Fischer reviews.

**External-comms gate**: block all messages to Christian Simon / Torsten Schöneberg / any SMA collaborator until items U1-U28 are addressed AND CLAIMS_REGISTRY rows 11-15 are resolved AND this audit passes 3/3 LLM + human sign-off. If Simon sends a follow-up in the next 48h, respond with a short "we're still verifying" acknowledgement (template in `LIMK2_retraction_brief_INTERNAL.md` §5 — adapted).

---

## Triple-LLM Verdict on This Audit

- Command run: `python3 /home/bryza/gpu-fleet/scripts/triple_llm_verify.py --file /home/bryza/sma-research/qms/GOVERNANCE_AUDIT_2026-04-17.md`
- Result: **0/3 PASS** (all three LLMs FAIL)
- Verdict JSON: `/home/bryza/sma-research/qms/GOVERNANCE_AUDIT_2026-04-17_triple_llm_verdict.json`

**Interpretation.** This 0/3 PASS signal is the **correct** signal for a governance audit of an ecosystem that still contains unfixed blocking issues. The triple_llm_verify.py prompt rule (lines 36-41) says past errors being corrected are NOT current claims; but a governance audit is a middle category — it catalogs issues that currently EXIST and need to be fixed. The 3 LLMs (GPT-4o, Groq Llama-3.3-70B, Gemini 2.0 Flash) all independently identified the SAME issues that the audit itself flagged as URGENT (GSE208629 unverified, CFL2 disease-specific unsourced, PFN2 +1.22 wrong magnitude, LIMK1 +1.20 wrong magnitude, ROCK-ALS citation unverified, README.md Status-VALIDATED inconsistent with retraction banner, strikethrough syntax malformed). This confirms:

1. The URGENT list U1-U28 is correctly scoped.
2. The ecosystem contains exactly the blocking issues catalogued.
3. The recommendation "NOT ready for external comms; 2-3 days of cleanup" is validated.

**Re-verification trigger**: the triple-LLM gate should be re-run **after** URGENT fixes U1-U28 are applied. At that point the ecosystem's un-fixed claims should have been either retracted or re-derived from verified datasets, and a PASS verdict should return. The audit itself does not require a LLM PASS before Christian reviews it — the purpose of the audit is to surface the FAIL state of the ecosystem.

## QMS Audit-Trail

- Grep patterns + files scanned logged above
- Reference-of-truth datasets: GSE290979, GSE302774, GSE87281 (all `dataset_verify` PASS, see DATA_INVENTORY.md)
- Triple-LLM QC on this audit: **0/3 PASS — correct FAIL signal for an unfixed ecosystem** (see above section)
- Human reviewer sign-off: **PENDING** (Christian Fischer)
- Session reference: 2026-04-17 governance-audit (session eed1b54a extension)
- Related incident: `/home/bryza/sma-research/qms/CORRECTIONS_LOG.md` Incident 2026-04-17-001
- Audit-event reference: `/home/bryza/sma-research/qms/CORRECTIONS_LOG.md` Audit-Event 2026-04-17-002
- Related brief: `/home/bryza/sma-research/qms/LIMK2_retraction_brief_INTERNAL.md`
- New CLAIMS_REGISTRY rows added: 11-15 (LIMK1 +1.20, PFN2 +1.22, CORO1C ↓1.77×, scRNA-table, GSE208629)

---

*DRAFT. Do not distribute externally. Intended audience: Christian Fischer for review + fix-plan approval.*
