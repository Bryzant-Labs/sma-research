# Corrections Log — SMA Research QMS

Alle Retractions und signifikante Claim-Änderungen werden hier dokumentiert. Kein silent edit.

---

## Incident 2026-04-17-005: LIMK2-αC top-4 iptm-based ranking — RETRACTED (affinity-head recalibration)

**Status**: RETRACTED
**Retracted on**: 2026-04-17 evening
**Upstream finding**: agent ae345009, `chembl_ki_affinity_head_RESULTS.md` (R² iptm-vs-Ki = 0.007 for LIMK2 vs R² affinity-head-vs-Ki = 0.690)
**Original sources**:
- `/home/bryza/sma-research/qms/limk2_activator_alphaC_RESULTS.md` §4.1 (prior top-4)
- `/home/bryza/sma-research/qms/LIMK2_NEW_STORY_FOR_SIMON.md` Arm 1 (recommended lead `CS(=O)(=O)c1ccccc1-c1cccc(Oc2ccc(C(N)=O)cc2)c1`, sel_z +0.83, 43.sdf)

### Was behauptet wurde

> "LIMK2-αC Arm 1 recommended lead: `CS(=O)(=O)c1ccccc1-c1cccc(Oc2ccc(C(N)=O)cc2)c1` (43.sdf), sel_z +0.83, iptm 0.942, recommended for 20 ns MD follow-up." — based on iptm + selectivity_z across a 15-kinase Boltz-2 panel.

> "§4.1 Top Hits: 4 compounds passing Gate 4 (iptm-based, sel_z > 0), ranked #1 → #4 by sel_z." — pipeline output.

### Warum es falsch war

Agent ae345009 calibrated Boltz-2 iptm vs published ChEMBL Ki using 20 (SMILES, Ki_nM) pairs for LIMK2:
- **R² = 0.007** — iptm is statistical noise against Ki for LIMK2
- Pearson r = 0.086 — no monotonic relation
- Same 20 pairs rescored through Boltz-2 **affinity head** (`properties: - affinity: binder: L1`): **R² = 0.690**, Pearson r = 0.831, RMSE 0.378 log10-Ki (≈ ±2.4× multiplicative uncertainty)

Therefore the iptm-based ranking in the prior top-4 is equivalent to random against LIMK2 Ki, and the selectivity_z metric (which sums iptm ranks across a 15-kinase panel) inherits the same limitation for the LIMK2 dimension.

Rescoring the 4 leads via the affinity head with the LIMK2 calibration fit (slope 1.249, intercept 3.549, RMSE 0.378) produced:

| Prior rank (iptm) | SMILES | File | aff_pred | prob_binary | **Ki (calibrated)** | 95 % PI |
|---|---|---|---|---|---|---|
| 1 (sel_z +0.86) | `COc1cc(C)ccc1C(C)NCC1=CC=[N+]2C1=Nc1c[n+](Cc3cncc[nH+]3)ccc12` | 14.sdf | −0.186 | 0.060 | **2.1 µM** | 380 nM – 11 µM |
| 2 (sel_z +0.83) | `CS(=O)(=O)c1ccccc1-c1cccc(Oc2ccc(C(N)=O)cc2)c1` | 43.sdf | +1.679 | 0.048 | **442 µM** | 80 – 2,400 µM |
| 3 (sel_z +0.15) | `CCc1nc2ccc[nH+]c2cc1OCc1ccc2[nH]cc(C(=O)O)c2c1` | 176.sdf | +0.747 | 0.076 | **30 µM** | 5.5 – 170 µM |
| 4 (sel_z +0.01) | `COc1cc(OC)c(OC)c(C(=O)N2CCN(C(=O)c3ccncc3)CC2)c1` | 3.sdf | +1.630 | 0.070 | **380 µM** | 70 – 2,100 µM |

All 4 FAIL the binary-binder gate (`affinity_probability_binary > 0.3`). None is a credible nanomolar LIMK2 binder. The Arm-1 Simon-pack-recommended lead (43.sdf) is particularly affected: calibrated Ki ≈ 442 µM, 30×–10,000× weaker than originally implied by iptm-based ranking and outside the sub-µM range any "lead" classification would imply.

### Re-filter of the full library

All 109 BBB-filtered compounds rerun through the Boltz-2 affinity head on sma-h100-two (tmux session `limk2_aff`, H100 PCIe, 4m 29s structural + 12m 12s affinity = 16m 41s total, 99/109 successful after RDKit rejected 10 PocketXMol-incomplete SMILES, $0 marginal self-host cost).

**Binary-binder gate (`affinity_probability_binary > 0.3`) survivors: 4 of 99 (4.0 %).**

| rank | SMILES | File | prior C_rel | Ki (nM) | 95 % PI | prob_binary |
|---|---|---|---|---|---|---|
| 1 | `CNc1cc2c(c3ccc[nH+]c13)=CC1=CC(OCCc3cccc[nH+]3)=CNC1=CC=2` | 539.sdf | −0.278 (fail prior Gate 3) | **1.1 µM** | 198 nM – 6.0 µM | 0.309 |
| 2 | `Oc1cccc(-c2cc(N3CCc4ncc5ccccc5c4C3)ncn2)c1` | 374.sdf | −0.257 (fail prior Gate 3) | **1.4 µM** | 251 nM – 7.6 µM | 0.307 |
| 3 | `COc1ccc(O)c(NC(=O)C=Cc2cccc(-c3cnccn3)c2)c1` | 1.sdf | −0.792 (fail prior Gate 3) | **4.4 µM** | 800 nM – 24 µM | 0.314 |
| 4 | `Cn1cccc1C(=O)c1cccc(Oc2ccc(-c3cnccn3)nn2)c1` | 162.sdf | +0.054 (pass prior Gate 3) | **15 µM** | 2.7 – 83 µM | 0.320 |

### Honest conclusion

The LIMK2-αC PocketXMol library contains **no nanomolar binder** under Boltz-2 affinity-head calibration. The 4 binary-binder survivors are all µM-range point estimates (1.1 – 15 µM), 0 of 4 have z-score panel data (they were outside the prior 15-compound iptm-selected top subset that got paneled), and 3 of 4 fail the prior DiffDock C_rel > 0 geometry gate. The single survivor that passes all historical gates (162.sdf rank 4) is 15 µM — far from a drug lead.

Library requires redesign via different anchoring strategy (e.g. co-crystal Asp460-oriented scaffolds, LIMKi3-fragment-seeded PocketXMol, alternative αC pocket anchors) before any further LIMK2 compute. Do NOT advance any compound from this library to wet-lab.

### Ergriffene Maßnahmen

1. `/home/bryza/sma-research/qms/limk2_activator_alphaC_RESULTS.md`:
   - Added §0 Retraction Note with prior-top-4 rescoring table + new 4-survivor table (pass `prob_binary > 0.3`) + honest "no nanomolar binder" conclusion.
   - Added ⚠️ RETRACTED banner above §4.1 "Top Hits" table; old iptm-based ranking kept unmodified for audit history.
   - Expanded §1 Hard Caveats: new caveat #1 flagging retraction, #3 deprecating prior Gate 4, #5 clarifying iptm is not Ki, #6 documenting affinity head as new primary Ki signal.
   - Version bumped to "DRAFT v4, post-affinity-head".
2. `/home/bryza/sma-research/qms/LIMK2_NEW_STORY_FOR_SIMON.md`:
   - Arm 1 narrative retracted. Old recommended lead (43.sdf, sel_z +0.83) explicitly superseded.
   - New §Arm 1 presents affinity-head rerun summary: 4 survivors, µM-range, not nanomolar. Best-numerical µM-range candidate flagged with protonation caveat. Recommendation changed from "advance 43.sdf to 20 ns MD" to "library redesign required; do not advance any compound".
3. This entry in `CORRECTIONS_LOG.md` (Incident 2026-04-17-005).
4. Reproducibility trail:
   - `/home/bryza/sma-research/qms/limk2_affinity_rerun/build_yamls.py` (YAML builder)
   - `/home/bryza/sma-research/qms/limk2_affinity_rerun/rescore.py` (calibration + gate)
   - `/home/bryza/sma-research/qms/limk2_affinity_rerun/rescored_full.json` (all 99 parsed)
   - `/home/bryza/fleet-results/limk2_activator_alphaC/top_hits_affinity_v2.tsv` (4 survivors)
   - `/home/bryza/fleet-results/limk2_activator_alphaC/full_affinity_ranked_v2.tsv` (full 99, sorted by log10 Ki)

### Externe Kommunikation

**No external comms** — this retraction strengthens the Simon-Comms-Gate hold. The Simon pack Arm 1 narrative must be replaced before any revised Simon reply is considered for transmission. Triple-LLM gate on the updated LIMK2_NEW_STORY_FOR_SIMON.md is mandatory before that gate can be lifted.

### Reviewer

- Triple-LLM gate: **pending** (run after this CORRECTIONS_LOG entry)
- Human sign-off: **pending** (Christian Fischer)

---

## Incident 2026-04-17-003: Claim #2 (CFL2 disease-specific) — RETRACTED (U30 closing, evening)

**Status**: RETRACTED
**Retracted on**: 2026-04-17 evening
**Original sources**:
- `README.md` L68 (disease-specific marker list)
- `CLAIMS_REGISTRY.md` Claim #2 (status was UNDER_REVIEW since 2026-04-17 morning)

### Was behauptet wurde

> "CFL2 is disease-specific (UP in SMA, DOWN in ALS)"

### Warum es retracted wird

1. **SMA-side "UP" half** — pooled RE meta across the 3 VERIFIED datasets (GSE290979 + GSE302774 + GSE87281, k=5 contrasts) shows **log2FC = +0.002 ± 0.096, p = 0.96 NS, I² = 86 %**. Direction MIXED: 2 slightly UP, 2 slightly DOWN, 1 flat; none reach padj < 0.05. Per-contrast numbers:
   - GSE290979 organoid: +0.142 (padj 0.53 NS)
   - GSE302774 Hb9-iMN: +0.035 (padj 0.63 NS)
   - GSE302774 iN: +0.008 (padj 0.93 NS)
   - GSE87281 hiPSC-MN: −0.140 (padj 0.76 NS)
   - GSE87281 SH-SY5Y: −0.321 (padj 0.14 NS)
2. **ALS-side "DOWN" half** — only ALS accession in inventory (GSE287257) is snRNA-seq of post-mortem cervical spinal cord. Per-cluster MN pseudobulk DE requires Cell Ranger / Scanpy pipeline on GSE287257_RAW.tar (several GB); not runnable in local-CPU QMS session. No other ALS-MN dataset is in the inventory.
3. Both halves fail the SOP "claim must trace to verified source" test.

### Conditional un-retraction pathway

Claim #2 can be un-retracted if ALL of:
1. GSE287257 pseudobulk per-MN-cluster CFL2 log2FC shows robust DOWN direction (padj < 0.05) in ALS vs control, methodologically matched to SMA-side
2. SMA-side CFL2 is re-derived with a tissue/cell-type-matched dataset showing UP direction
3. Triple-LLM 3/3 PASS on the new derivation document
4. Christian Fischer sign-off

Until then: **RETRACTED**.

### Ergriffene Maßnahmen

1. `CLAIMS_REGISTRY.md` Row 2 status: UNDER_REVIEW → RETRACTED 2026-04-17 evening
2. `CLAIMS_REGISTRY.md` top-banner updated to reflect Claim #2 RETRACTED
3. `DATA_INVENTORY.md` Accession Still Needing Work table: ALS-reference-for-Claim-#2 row moved to Closed
4. `DATA_INVENTORY.md` executive summary: Claim #2 anchoring row → RETRACTED
5. Retraction document: `/home/bryza/sma-research/qms/cfl2_claim2_review.md` (DRAFT, triple-LLM + human sign-off pending)

### README.md L68 cleanup

`README.md` L68 still lists CFL2 in the "disease-specific markers" context — banner + strikethrough pending human approval of this retraction. Retraction document scope includes the README cleanup as a manual step.

### Human sign-off

PENDING — Christian Fischer.

---

## Incident 2026-04-17-004: GSE52941 PENDING → REJECTED (U29 closing, evening)

**Status**: REJECTED (wrong project scope — B-cell immunology)
**Resolved on**: 2026-04-17 evening
**Historical claim**: "GSE52941 is Ng 2015 SMA iPSC-MN" (WRONG — attributed to a Ng-group paper that does not exist at this accession)

### Resolution

Previous attempts via `dataset_verify.py` failed with HTTP 502 on the FTP path `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE52nnn/GSE52941/matrix/`. Direct re-fetch 2026-04-17 evening confirmed the series_matrix file is **not** published by the authors (only GSE52941_RAW.tar and GSE52941_CIITA.peaks.annotated.txt.gz supplementary files exist — see `!Series_supplementary_file` entries in NCBI GEO record). The 502 on the matrix subpath is permanent, not transient.

Direct GEO record fetch via `https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE52941&targ=self&view=quick&form=text` returned the canonical SERIES record:

- Title: *"CIITA regulated genes in human B cells"*
- Author: Scharer & Boss (Emory University, Dept Microbiology & Immunology)
- PMID: 25753668
- Platforms: GPL11154 + GPL16791 (Illumina HiSeq 2000)
- Organism: Homo sapiens (correct), but…
- Tissue: Raji + RJ2.2.5 B cell lines — **not** SMA, **not** motor neurons
- Study type: ChIP-seq (CIITA) + H3K4me3/H3K27ac + ATAC-seq — **not** DESeq2-ready bulk RNA-seq

### Classification

REJECTED (wrong project scope). The legacy "Ng 2015 SMA iPSC-MN" label in historical inventory is a **documentation error** — this accession has no SMA / MN content. It is not relevant to any SMA claim and must never be cited in SMA context. If a "Ng 2015 SMA iPSC-MN" dataset is genuinely needed in the future, its real accession must be located independently from the Ng group publication list.

### Ergriffene Maßnahmen

1. `DATA_INVENTORY.md` Master Table row 12: PENDING → REJECTED with full metadata, citation, rejection reason
2. `DATA_INVENTORY.md` Per-Accession Detail §12: rewritten with confirmed metadata, legacy-label retraction note, and action = closed
3. `DATA_INVENTORY.md` Accessions Still Needing Work: row closed (RESOLVED)
4. `DATA_INVENTORY.md` Executive Summary counts: REJECTED 7→8, PENDING 1→0
5. `CLAIMS_REGISTRY.md` sign-off events entry 2026-04-17 evening U29

### Human sign-off

PENDING — Christian Fischer.

---

## Incident 2026-04-17-001: "LIMK2 +2.81× hoch in SMA Motoneuronen" — RETRACTED

**Status**: RETRACTED
**Retracted on**: 2026-04-17
**Original sources (wo die Claim zitiert war)**:
- `README.md` Zeile 68 — public Repo
- `CATALOG.md` Zeile 221
- `docs/data_access.md` Zeile 30 — `GSE...` Platzhalter
- `campaigns/ROCK-LIMK2-CFL2_axis/README.md` Zeile 13

### Was behauptet wurde

> "LIMK2 is **+2.81×** in SMA motor neurons" — an vier Stellen zitiert, teils als Achsen-Kernaussage.

### Warum es falsch war

Zwei unabhängige, metadata-verifizierte SMA-MN-Datasets zeigen:

| Dataset | n | LIMK2 log2FC | padj | Bewertung |
|---|---|---|---|---|
| **GSE290979** (SMA Organoide bulk, pydeseq2) | 31 | **−0.21** | 0.37 (NS) | Nicht signifikant, leichter Abwärtstrend |
| **GSE302774** (Hb9-iMN SMN-KD, Author-DESeq2) | 12 | **−0.407** | **2.35e-12 (***)** | Hochsignifikant **ABWÄRTS** |

Die ursprüngliche Zahl **+2.81×** (entspricht log2FC ≈ +1.49) ist nicht nur **nicht reproduzierbar**, sondern direction-invertiert falsch. LIMK2 ist in SMA MN **mild DOWN**-reguliert, nicht **UP**.

### Datenspur-Untersuchung

- Repos zitieren den Wert ohne primäre Datenquelle (`GSE...` Platzhalter)
- Keine Analyse-Notebook oder Skript im Repo berechnet +2.81×
- Kein PMID oder Publikations-Zitat lokalisiert
- Ursprung vermutlich: frühe Session-Output, der nicht verifiziert wurde und dann über mehrere Dokumente kopiert
- Prior Simon Mega_Pack 2026-04-11/12 zitierten den Wert — diese müssen ggf. nachträglich korrigiert werden

### Ergriffene Maßnahmen

1. `README.md` Zeile 68: Claim entfernt, Korrektur-Banner eingefügt
2. `CATALOG.md` Zeile 221: Claim mit Retraction-Markierung versehen
3. `docs/data_access.md` Zeile 30: Platzhalter-Eintrag entfernt, durch real-derived Eintrag ersetzt
4. `campaigns/ROCK-LIMK2-CFL2_axis/README.md`: **großer CORRECTION NOTICE** oben, Axis-Framing als "under review" markiert
5. Re-Analyse dokumentiert in `_INTERNAL_DO_NOT_SEND_Mega_Pack_2026-04-17/02_evidence/01_LIMK2_reanalysis_GSE287257.md`
6. QMS-Regeln etabliert (`qms/SOP.md`) damit dieser Fehlertyp nicht wiederkommt

### Implikation für die ROCK-LIMK2-CFL2 Achsen-Hypothese

Die Claim dass diese Achse "hyperaktiv" in SMA MN ist, ist **nicht haltbar**. Daten zeigen:
- LIMK2 DOWN (beide Datasets)
- ROCK2 DOWN (GSE302774 padj 6e-3)
- CFL1 DOWN (GSE302774 padj 3e-7)
- CFL2 unchanged
- PFN2 UP (die einzige reproduzierbare positive Claim)
- TP53 UP (die echte aktive Pathologie-Achse)
- PERP DOWN (konsistent mit Simons NMJ-Befund)

Die Fasudil-Therapie-Rationale muss neu untersucht werden — wenn ROCK2 in SMA MN bereits DOWN ist, bedeutet ROCK-Inhibition potenziell Schaden, nicht Rescue.

### Externe Kommunikation

**Keine externe Kommunikation** (an Christian Simon, Torsten Schöneberg, Publikationen) mit ROCK-LIMK2-CFL2-Achsen-Framing bis:
1. QMS-Audit aller anderen Claims abgeschlossen
2. Neue Hypothese entwickelt (vermutlich p53-getrieben)
3. Neue Hypothese durch QMS-Lifecycle validiert (APPROVED-Status)

### Reviewer

- Automatischer 3-LLM-Gate: 3/3 PASS auf dem Re-Analyse-Brief (GPT-4o, Groq Llama-3.3-70B, Gemini 2.0 Flash) am 2026-04-17
- Mensch-Reviewer: pending (Christian Fischer Sign-off nach Audit)

---

## Audit-Event 2026-04-17-002: Platform-weite Governance Audit

**Status**: DRAFT (pending triple_llm_verify + Christian Fischer sign-off)
**Durchgeführt**: 2026-04-17 ~13:00 UTC
**Auslöser**: Incident 2026-04-17-001 (LIMK2 +2.81× retraction) exposed systemisches Risiko dass andere Claims ebenfalls un-audited sind.
**Scope**: `/home/bryza/sma-research/**/*.md` + `/mnt/c/Users/bryza/Dropbox/Christian fischer/SMA/**/*.md` (Simon-facing + Master-Catalog)

### Was gefunden wurde

| Kategorie | Anzahl |
|---|---|
| Claims insgesamt auditiert | 42 |
| URGENT (external-visible + wrong) | 13 |
| MEDIUM (internal, unverified, needs re-derivation) | 9 |
| LOW (historical snapshots, flag only) | 6 |
| Neue CLAIMS_REGISTRY Rows (11-15) eingetragen | 5 |
| Unverifizierte Accessions gefunden | 3 (GSE208629, GSE287257-als-SMA-miscited, GSE87281-CORO1C-not-re-derived) |

### Key findings

1. **GSE208629** wurde in Mega_Pack_2026-04-11 FULL_EVIDENCE_PACKAGE als Primärquelle von +2.81× zitiert, existiert aber **nicht** in unserem verifizierten Dataset-Inventar. Vierter Accession in der Familie mit GSE287257/GSE140756/GSE176751 → Retraction-Kandidat.
2. **LIMK1 +1.20 log2FC (p=8.4e-24)** ist in zwei öffentlichen Repo-Dateien zitiert (CATALOG.md L93 + correction_notice.md L35). Meta-pooled LIMK1 = +0.033 NS. Likely Retraction.
3. **PFN2 +1.22 log2FC** erscheint im Dropbox Fasudil_Evidence_Package Simon-handout UND im Master PROJECT_CATALOG. Meta-pooled PFN2 = +0.025 NS (max per-contrast +0.362 in GSE302774 iN). Magnitude retrahiert.
4. **ROCK-LIMK2-CFL2 "validated across 3 independent datasets"** Framing erscheint in 7+ weiteren Dateien über das Repo (SMN2_base_editing/combination_protocol, competitive_landscape, SMA_CURE_ACTION_PLAN, cross_connections, rock1_inhibitor_plan, simon_3mechanism_combo, bbb5_Dual_Pathway_Brief). Alle widersprechen der korrigierten Signatur.
5. **Fasudil_SMA_Evidence_Summary.md** (Simon-destined) enthält 5 unkorrigierte Claims (+2.81× × 2, CFL2 disease-specific, PFN2 +1.22, ROCK-ALS Lancet 2024 Zitat ohne PMID).

### Ergriffene Maßnahmen (durch Audit)

1. Audit-Report dokumentiert: `/home/bryza/sma-research/qms/GOVERNANCE_AUDIT_2026-04-17.md` (DRAFT, pending triple_llm_verify)
2. CLAIMS_REGISTRY.md um 5 neue Rows (11-15) ergänzt — alle UNDER_REVIEW oder RETRACT-Kandidaten
3. Dieser CORRECTIONS_LOG-Eintrag als Audit-Event-Record erstellt

### Noch NICHT ergriffene Maßnahmen (URGENT-Liste)

Die 28 URGENT-Aktionen (U1-U28 im Audit-Report) sind **nicht** silent-fixed worden. Jede erfordert:
- Banner-Update ODER Text-Replacement
- Git commit mit "CORRECTION:" prefix
- Cross-Link in diesen CORRECTIONS_LOG

Geschätzte Cleanup-Zeit: 2-3 Arbeitstage mit Fokus.

### Externe Kommunikations-Gate

**Alle Comms an Christian Simon / Torsten Schöneberg / SMA-Kollaborateure gesperrt** bis:
1. Audit-Report selbst triple_llm_verify 3/3 PASS
2. URGENT-Liste U1-U28 abgeschlossen
3. CLAIMS_REGISTRY Rows 11-15 resolved (APPROVED oder RETRACTED)
4. Mensch-Sign-off auf revidierter SMA-MN-Signatur (ROCK2-DOWN / TP53-UP / PERP-per-contrast / LIMK2-model-dependent)

### Reviewer

- Automatischer 3-LLM-Gate auf Audit-Report: **pending**
- Mensch-Reviewer: **pending** (Christian Fischer)

---

## Sub-Entries (Audit-Event 2026-04-17-002 — Cleanup Execution Log)

Ausgeführt 2026-04-17 nachmittags im Rahmen des URGENT-Cleanup-Passes. Jede Zeile
unten = ein konkreter Fix gegen die URGENT-Liste U1-U28 aus
`GOVERNANCE_AUDIT_2026-04-17.md`. **Keine silent edits** — alle ursprünglichen
Zeichenketten als ~~striked through~~ oder zitiert-im-Banner preserved für
Audit-Historie.

### Fix 2026-04-17-002-A (U1, U2, U3, U4, U5) — Fasudil_SMA_Evidence_Summary.md

**Datei**: `/mnt/c/Users/bryza/Dropbox/Christian fischer/SMA/Simon/Fasudil_Evidence_Package/Fasudil_SMA_Evidence_Summary.md`
**Aktion**: Großes RETRACTED-Banner oben angehängt (enumeriert alle 5 U1-U5 Probleme
+ ROCK2-DOWN-Korrektur + Pan-ROCK-Kontraindikation-Flag). §3 Mechanism-Sektion
mit inline-RETRACTED-Banner versehen. Status von "Stage 5 PASS" auf "RETRACTED"
geändert. Ursprüngliche Zeilen L45/L58 ("LIMK2 +2.81x in SMA MNs" / "+2.81x in
SMA motor neurons (3 independent transcriptomic datasets)"), L59 (CFL2
disease-specific), L62 (PFN2 +1.22), L63 (CORO1C p=0.37), L66 (ROCK-ALS Lancet
2024) sind im Text erhalten unter der Banner-Warnung. Folder-Umbenennung
(`_INTERNAL_DO_NOT_SEND_Fasudil_Evidence_Package_PRE_RETRACTION/`) **DEFERRED**
— Christian entscheidet ob Dropbox-path-rename opportun vor nächster Simon-Reply.

### Fix 2026-04-17-002-B (U6) — Mega_Pack_2026-04-11/01_summary/EXECUTIVE_SUMMARY.md

**Datei**: `/mnt/c/Users/bryza/Dropbox/Christian fischer/SMA/Simon/Mega_Pack_2026-04-11/01_summary/EXECUTIVE_SUMMARY.md`
**Aktion**: Top-level RETRACTED-Banner mit explizitem Hinweis "This pack was sent
to Simon on 2026-04-11" + Referenz auf Incident 001 + Audit-Event 002. Line 34
("ROCK-LIMK2-CFL2 axis: 3 independent datasets confirm LIMK2 +2.81×") durch
inline-RETRACTED mit Meta-Zahlen ersetzt. PDF-Version (EXECUTIVE_SUMMARY.pdf) ist
NICHT neu generiert — beim nächsten Revisions-Pack muss das PDF mit-retrahiert
werden, nicht re-exportiert.

### Fix 2026-04-17-002-C (U7) — Mega_Pack_2026-04-11/02_evidence/FULL_EVIDENCE_PACKAGE.md

**Datei**: `/mnt/c/Users/bryza/Dropbox/Christian fischer/SMA/Simon/Mega_Pack_2026-04-11/02_evidence/FULL_EVIDENCE_PACKAGE.md`
**Aktion**: Top-level RETRACTED-Banner enumeriert alle 5 Claim-Probleme inklusive
**GSE208629-Verifikation** (siehe separater Fix 002-Z unten). §Background Why
this pathway Section mit inline-RETRACTED-Banner versehen; Originalzeilen (LIMK2
+2.81× GSE208629, PFN2 +1.22, LIMK1 +1.20 ALS, CFL2 disease-specific, ROCK2
hyperactivation, GSE287257 ALS-miscited als SMA) bleiben im Dokument unter
Banner-Warnung. PDF analog zu 002-B nicht regeneriert.

### Fix 2026-04-17-002-D (U8) — Mega_Pack_2026-04-12/Simon_Email_Draft.txt

**Datei**: `/mnt/c/Users/bryza/Dropbox/Christian fischer/SMA/Simon/Mega_Pack_2026-04-12/Simon_Email_Draft.txt`
**Aktion**: Plaintext-Banner (#-prefixed) oben angehängt. Enumeriert 5 Probleme:
L15 "+2.81x in SMA-Motorneuronen", L15 "LIMK1 ist das ALS-Target", L17 CFL2
+1.83× / SMA vs ALS, L53-54 p53-Kaskade baut auf retracted axis, gesamter
Fasudil-als-Werkzeug-Abschnitt. Folder-Umbenennung nach
`_RETRACTED_SEE_INCIDENT_001` **DEFERRED** (Dropbox-lock-in-Risiko). Flag:
Christian entscheidet ob es Simon eine kurze Notiz wert ist ("Numeric claims in
Apr-11+Apr-12 packs retracted; revised pack coming").

### Fix 2026-04-17-002-E (U9, U10) — Dropbox PROJECT_CATALOG.md

**Datei**: `/mnt/c/Users/bryza/Dropbox/Christian fischer/SMA/PROJECT_CATALOG.md`
**Aktion**: Zeile 140 (PFN2 +1.22 / LIMK1 +1.20 als "Real MN actin genes") mit
inline-RETRACTED-Strikethrough und korrigierten per-contrast + pooled meta
Zahlen versehen. Zeile 274-283 (ROCK-LIMK2-CFL2-Axis-Sektion) komplett
neu-gerahmt: Status VALIDATED → UNDER_REVIEW, Hypothese als RETRACTED markiert,
alle 3 bisherigen "Key findings" als retrahiert/unsourced/per-contrast-only
umgeschrieben.

### Fix 2026-04-17-002-F (U11, U12, U13) — campaigns/ROCK-LIMK2-CFL2_axis/README.md

**Datei**: `/home/bryza/sma-research/campaigns/ROCK-LIMK2-CFL2_axis/README.md`
**Aktion**: Status-Feld von "VALIDATED across 3 independent datasets" →
"UNDER_REVIEW (see retraction banner above)". Hypothesis-Block explizit als
RETRACTED gekennzeichnet + ROCK2 DOWN Meta-Zahl. Evidence-Liste (LIMK2 +2.81×,
CFL2 disease-specific, PFN2 +0.283) komplett neu-geschrieben mit per-contrast
Werten, model-dependence-Flag, UNSOURCED-Flag für CFL2 ALS-Referenz.

### Fix 2026-04-17-002-G (U14, U15, U16) — sma-research/CATALOG.md

**Datei**: `/home/bryza/sma-research/CATALOG.md`
**Aktion**: Zeile 93 (LIMK1 +1.20) mit Strikethrough + RETRACTED-Markierung +
Meta-pooled-Referenz. Zeile 225-283 (ROCK-LIMK2-CFL2 Axis-Sektion): neues
RETRACTED/UNDER_REVIEW-Banner oben, Status-Feld VALIDATED → UNDER_REVIEW,
Hypothesis als RETRACTED gekennzeichnet, alle 4 Key-Findings retrahiert/korrigiert.

### Fix 2026-04-17-002-H (U24) — sma-research/README.md

**Datei**: `/home/bryza/sma-research/README.md`
**Aktion**: Zeile 77 (ROCK-LIMK2-CFL2 "core therapeutic axis" Bullet) komplett
neu-geschrieben: ursprünglicher "validated across 3 independent datasets" +
"+2.81x [RETRACTED]" + "CFL2 disease-specific" ersetzt durch korrigierte Meta-
Statements (ROCK2 DOWN pooled −0.254 p=9.0e-5; LIMK2 model-dependent pooled
−0.20 NS; CFL2 unchanged +0.002 NS; ALS-Referenz UNSOURCED).

### Fix 2026-04-17-002-I (U25) — sma-research/docs/data_access.md

**Datei**: `/home/bryza/sma-research/docs/data_access.md`
**Aktion**: "Raw sequencing data"-Tabelle überarbeitet. GSE287257 als
"ALS cross-disease reference" neu markiert mit CORO1C-miscitation-Flag.
Original-Platzhalter-Zeile `GSE...` ersetzt durch explizite
RETRACTED-Dokumentation + GSE208629-Verifikations-Note (mouse scRNA, nicht
human bulk). Drei verifizierte SMA-MN-Datasets (GSE290979, GSE302774,
GSE87281) als neue Tabellenzeilen mit Meta-analysis-Pointer hinzugefügt.

### Fix 2026-04-17-002-J (U17) — campaigns/4-AP/2026-04-06_correction/correction_notice.md

**Datei**: `/home/bryza/sma-research/campaigns/4-AP/2026-04-06_correction/correction_notice.md`
**Aktion**: Top-level SUPERSEDED/UNSOURCED-Banner enumeriert 5 Probleme (L34
PFN2 +0.283 mit falscher p-value, L35 LIMK1 +1.20, L35 LIMK1 ALS −0.81
unsourced, L37 CORO1C ↓1.77×, L100 scRNA-Table). Inline-Strikethroughs auf
Zeile 34-35 (PFN2 + LIMK1) und Zeile 100 (scRNA ROCK1/LIMK1/LIMK2 Row)
appliziert mit vollständiger Meta-Kontext-Note.

### Fix 2026-04-17-002-K (U18) — campaigns/SMN2_base_editing/combination_protocol.md

**Datei**: `/home/bryza/sma-research/campaigns/SMN2_base_editing/combination_protocol.md`
**Aktion**: Drei Inline-RETRACTED-Annotations gesetzt: Zeile 40 ("ROCK-LIMK2-CFL2
axis, validated in 3 independent SMA datasets"), Zeile 48 ("ROCK-LIMK2-CFL2 is a
therapeutic axis we identified across 3 independent SMA datasets"), Zeile 172
("ROCK hyperactivation -> LIMK2 hyperphosphorylation -> CFL2 inactivation ->
frozen actin dynamics"), Zeile 221 ("ROCK-LIMK2-CFL2 therapeutic axis:
identified across 3 independent SMA datasets"). Neuer Caveat-Absatz in
"Supporting Evidence for the ROCK Pathway in SMA" eingefügt: Bowerman-2012
Muskel-layer-Mechanismus überlebt als separate Hypothese unabhängig von der
retrahierten MN-intrinsischen Transkriptions-Achse.

### Fix 2026-04-17-002-L (U19) — campaigns/SMN2_base_editing/research/competitive_landscape.md

**Datei**: `/home/bryza/sma-research/campaigns/SMN2_base_editing/research/competitive_landscape.md`
**Aktion**: Zeile 135 ("ROCK-LIMK2-CFL2 therapeutic axis (3 datasets, zero
competitors)") mit Strikethrough + RETRACTED + Meta-Referenz. "Zero competitors
in LIMK2-selective chemistry" als chemistry-side-Aussage separat erhalten.

### Fix 2026-04-17-002-M (U20) — campaigns/SMN2_base_editing/SMA_CURE_ACTION_PLAN_2026.md

**Datei**: `/home/bryza/sma-research/campaigns/SMN2_base_editing/SMA_CURE_ACTION_PLAN_2026.md`
**Aktion**: Top-level UNDER_REVIEW-Banner für gesamten Plan (Line 6 "ABE base
editing + ROCK-LIMK2-CFL2 recovery = the cure nobody else is building"). Zeile
19 ("Found: ROCK-LIMK2-CFL2 axis (3 datasets)...") mit Strikethrough + Meta-
Korrektur. Track A (ABE) als independent-surviving markiert.

### Fix 2026-04-17-002-N (U21) — findings/insights/2026-04-10_cross_connections_v3.md

**Datei**: `/home/bryza/sma-research/findings/insights/2026-04-10_cross_connections_v3.md`
**Aktion**: Top-level HISTORICAL-SNAPSHOT / PARTIAL-RETRACTION-Banner. Insight 1
Line 36 ("ROCK-LIMK2-CFL2 axis validated by 3 independent datasets"), Insight 6
Line 154 ("ROCK-LIMK axis validated by 3 independent datasets"), Insight 6 Line
163 ("ROCK2 hyperactivation as biomarker for Risdiplam resistance") alle im
Banner als RETRACTED markiert. Body der Insights unverändert gelassen für
Audit-Historie. Flag gesetzt: Dokument darf nicht in öffentliche "insights"
Feeds exportiert werden ohne Re-synthese.

### Fix 2026-04-17-002-O (U22) — findings/2026-04-12/simon_3mechanism_combo.md

**Datei**: `/home/bryza/sma-research/findings/2026-04-12/simon_3mechanism_combo.md`
**Aktion**: Front-matter status von "public-summary" auf "UNDER_REVIEW
2026-04-17" geändert. UNDER_REVIEW-Banner oben eingefügt. Tabellenzeile
"Cytoskeletal rescue — Fasudil — ROCK2 → LIMK2 → Cofilin-2" mit
Strikethrough + "direction-inverted per 3-dataset meta" + Muskel-layer-Fallback
markiert. MuSK + NRF2 Tracks als independent-surviving.

### Fix 2026-04-17-002-P (U23) — qms/rock1_inhibitor_plan.md

**Datei**: `/home/bryza/sma-research/qms/rock1_inhibitor_plan.md`
**Aktion**: "Framing and purpose"-Section Zeile 14-16 ("The ROCK-LIMK2-CFL2 axis
is the therapeutic axis for SMA (3 datasets, memory)") mit Strikethrough +
RETRACTED + ROCK1-Meta-pooled-Note (−0.071, NS — keine SMA-MN-Rationale für
ROCK1-Inhibition). Campaign-Selectivity-Control-Framing bleibt unangefochten.

### Fix 2026-04-17-002-Z (GSE208629 Accession-Verifikation)

**Aktion**: Live-Fetch vom NCBI GEO `?acc=GSE208629&targ=self&view=quick&form=text`
durchgeführt 2026-04-17. **Resultat**: GSE208629 existiert und ist
`Series_title: "Single-cell transcriptomic data in the spinal cord of Taiwanese
type I SMA mice"`, Sun et al. 2022, PMID 36074806, Mus musculus, Platform
GPL24247, scRNA-seq von postnatal-day-4 SMA+Heterozygote-Mouse-Spinalrückenmark.
**Klassifikation**: die Accession ist REAL, aber in Mega_Pack 2026-04-11
FULL_EVIDENCE_PACKAGE.md als Primärquelle für **human bulk RNA-seq "+2.81× LIMK2
log2FC p<0.001"** zitiert. Das ist eine CITATION-HALLUCINATION (falscher
Datentyp, falsche Species, falsche Contrast-Struktur für den behaupteten
Scalar-log2FC-Wert). Update in CLAIMS_REGISTRY Row 15 ("HALLUCINATED-CITATION
subtype: accession real but mis-cited"). DATA_INVENTORY Rejected-Row noch zu
pflegen in separatem Pass (nicht Teil dieses Cleanup-Events, da DATA_INVENTORY
evtl. noch nicht existiert als Datei).

---

## Audit-Event 2026-04-17-002 — CLOSING SECTION

**Closing timestamp**: 2026-04-17 (nachmittags UTC, session eed1b54a-Extension)

### Cleanup-Statistik

| Metric | Count |
|---|---|
| URGENT-Items gefixt (U1-U5, U6, U7, U8, U9-U10, U11-U13, U14-U16, U17, U18, U19, U20, U21, U22, U23, U24, U25) | **25/28** (U24, U25 kombiniert; U26-U28 DATA_INVENTORY-pflichtig → DEFERRED) |
| Dateien mit Retraction-Banner versehen | **13** (siehe Fix-Liste 002-A bis 002-P + 002-Z) |
| Neue Strikethrough-Annotations | ~30 Einzelaussagen |
| CLAIMS_REGISTRY Rows promoviert (11-15) | **5**: Row 11 RETRACTED, Row 12 RETRACTED, Row 13 UNDER_REVIEW (derivation pending), Row 14 RETRACTED, Row 15 RETRACTED (HALLUCINATED-CITATION) |
| Externally-visible Fixes (Dropbox/Simon/sma-research public) | **11/13** Zieldateien |
| Internally-only Fixes (qms/, findings/) | **3** Zieldateien (rock1_inhibitor_plan.md, correction_notice.md, cross_connections_v3.md) |
| GSE-Accession-Verifikationen durchgeführt | **1** (GSE208629 — REAL but MIS-CITED) |

### Noch offene URGENT-Items (DEFERRED)

- **U26** (GSE208629 → DATA_INVENTORY Rejected-Row): die Datei
  `qms/DATA_INVENTORY.md` existiert zum Zeitpunkt dieses Cleanup-Events noch
  nicht als separate File. Accession-Verifikation oben dokumentiert; formeller
  Inventory-Row wird beim DATA_INVENTORY-Build nachgetragen.
- **U27** (GSE287257 als ALS nicht SMA): die Klarstellung ist in
  `correction_notice.md` (Fix 002-J) + `data_access.md` (Fix 002-I) bereits
  appliziert. Keine weitere Aktion nötig, ausser DATA_INVENTORY-Row.
- **U28** (GSE87281 CORO1C re-derivation): nicht Teil des Banner-Passes;
  erfordert Compute-Run (pydeseq2 auf GSE87281 RSEM counts für CORO1C
  spezifisch). CLAIMS_REGISTRY Row 13 bleibt UNDER_REVIEW bis Compute
  ausgeführt.

### Noch offene MEDIUM-Items (M1-M9 aus Audit-Report)

Nicht Teil dieses Passes. Separate Cleanup-Runde empfohlen nach:
1. Triple-LLM-Gate 3/3 PASS auf diesem Closing-Report
2. Human Sign-off auf CORRECTED_SIGNATURE.md
3. Simon-Reply-Template abgestimmt

### Qualitäts-Gates dieses Cleanup-Passes

| Gate | Status |
|---|---|
| Kein silent edit (alle Original-Strings preserved als strikethrough oder im Banner zitiert) | ✅ PASS |
| Jedes Banner verweist auf CORRECTIONS_LOG Incident 001 oder Audit-Event 002 | ✅ PASS |
| Alle modifizierten Dateien in diesem Sub-Entry-Block dokumentiert | ✅ PASS |
| CLAIMS_REGISTRY Rows 11-15 Status-Update angewandt | ✅ PASS |
| Keine externe Kommunikation (Simon/Torsten) während Cleanup | ✅ PASS |
| Keine neuen Claims eingeführt (nur Retraktion + Korrektur bestehender) | ✅ PASS |
| Kein GitHub-Push auf sma-research (external comms gate hold) | ✅ PASS |

### Reviewer

- Automatischer QMS-Cleanup-Agent (Opus Master Agent) 2026-04-17 nachmittags
- Triple-LLM-Gate auf diesem Closing-Report: **pending** (ausgeführt nach
  Schreiben des GOVERNANCE_CLEANUP_20260417_REPORT.md)
- Human Sign-off: **pending** (Christian Fischer)

### Nächste Schritte nach Sign-off

1. Triple-LLM-Gate re-run auf GOVERNANCE_AUDIT_2026-04-17.md (sollte jetzt
   3/3 PASS liefern, da Ecosystem-Zustand konsistent ist)
2. MEDIUM-Cleanup (M1-M9) scheduling
3. Simon-Reply-Template-Überarbeitung (retraction-aware)
4. DATA_INVENTORY.md erstmalige Erstellung mit Rejected-Rows für GSE208629 +
   GSE287257 + GSE287257-variant-family
5. Revidierter Simon-Pack (Mega_Pack_2026-04-18 oder später) auf Basis
   CORRECTED_SIGNATURE nach Rule-dataset-verify-before-use.md

---

## Audit-Event 2026-04-17-002 — U26 / U27 / U28 CLOSING SUB-ENTRIES

Added 2026-04-17 evening (session eed1b54a-Extension-2). Closes the three
URGENT items that were DEFERRED in the main 002 cleanup pass because they
required DATA_INVENTORY.md rows + a compute re-derivation.

### Fix 2026-04-17-002-AA (U26) — DATA_INVENTORY.md GSE208629 MIS-ATTRIBUTED row

**Datei**: `/home/bryza/sma-research/qms/DATA_INVENTORY.md` §5 (GSE208629)

**Aktion**: Existierende MIS-ATTRIBUTED-Row erweitert um expliziten
"Accession reality check (U26 closing)"-Block mit drei Punkten:

1. Accession IS real (NCBI GEO live-fetch bestätigt 2026-04-17).
2. Scalar "+2.81× log2FC LIMK2 p<0.001" ist aus einem scRNA-seq-Dataset
   **ohne vorausgehendes Pseudobulking + Ortholog-Mapping nicht
   derivierbar**. Keiner dieser Schritte wurde durchgeführt. Die Zahl ist
   eine Hallucinated-Scalar-from-scRNA.
3. Unser verifiziertes SMA-MN-Panel enthält GSE208629 nicht; die Claim
   ist aus unseren verifizierten Quellen nicht re-derivierbar.

Zusätzlich "Legitimate future use"-Note: nur als Mouse-SMA-Cross-Species-
Referenz mit vollständiger Caveat-Labelling, nie als Quelle eines
Human-Bulk-log2FC.

**Gate**: U26 → CLOSED. Inventory row ist jetzt explizit über Warum ein
scalar log2FC aus diesem Dataset nicht kommen kann, nicht nur Warum es
mis-cited wurde.

### Fix 2026-04-17-002-BB (U27) — DATA_INVENTORY.md GSE287257 REJECTED row mit ALS-Reuse-Protokoll

**Datei**: `/home/bryza/sma-research/qms/DATA_INVENTORY.md` §4 (GSE287257)

**Aktion**: Existierende REJECTED-Row erweitert um "Legitimate future
use — ALS-REFERENCE (U27 closing)"-Block mit vier Punkten:

1. Das Dataset IS valid als ALS-MN Resource — ist nur kein SMA-Dataset.
2. Claim #2 in CLAIMS_REGISTRY (CFL2 UP in SMA, DOWN in ALS) ist
   UNSOURCED weil kein ALS-Referenzdataset je aufgezeichnet wurde.
   GSE287257 ist der leading Kandidat für Claim-#2-Re-derivation.
3. Vor jeder ALS-reference-Nutzung: verifiziere CFL2 DOWN an per-cluster
   MN DE, kennzeichne snRNA-vs-bulk-Methodikdifferenz als Caveat,
   verwende matched ALS-MN vs ALS-control-Design.
4. Falls GSE287257 Claim #2 beim Re-derive nicht stützt → Claim #2
   MUSS RETRACTED werden. Kein anderes ALS-MN-Transcriptomics-Dataset
   ist aktuell in unserer Inventory.

Plus header-tag der Section auf "REJECTED (with ALS-reference reuse note)"
aktualisiert.

**Gate**: U27 → CLOSED. Inventory gibt jetzt eindeutiges Protokoll wie
das REJECTED-für-SMA-aber-ALS-usable Dataset formell wiederverwendet
werden kann, ohne die Original-REJECTED-for-SMA-Klassifikation zu
gefährden.

### Fix 2026-04-17-002-CC (U28) — CORO1C Re-derivation + Claim #13 RETRACTED

**Datei**: Neu:
- `/home/bryza/sma-research/qms/coro1c_rederivation.py` (Re-derivation-Skript)
- `/home/bryza/sma-research/qms/coro1c_rederivation.md` (Markdown-Resultat)
- `/home/bryza/sma-research/qms/coro1c_rederivation.json` (strukturierte Zahlen)

Modifiziert:
- `/home/bryza/sma-research/qms/CLAIMS_REGISTRY.md` Row 13 Status-Übergang

**Methode**: Inverse-variance weighted DerSimonian-Laird random-effects
meta-analysis (gleiche Spec wie das 18-Gen-Panel in
`meta_deseq2_3dataset.py`). 5 Contrasts extrahiert:

| Dataset | Contrast | log2FC | lfcSE | padj |
|---|---|---:|---:|---:|
| GSE290979 | organoid SMA vs CTRL (NT) | +0.1506 | 0.1932 | 0.670 |
| GSE87281 | SH-SY5Y shSMN vs shCtrl | **−0.5455** | 0.1608 | **0.00367** |
| GSE87281 | hiPSC-MN shSMN vs shCtrl | −0.0421 | 0.1377 | 0.906 |
| GSE302774 | Hb9-iMN SMN-KD vs Scramble | −0.0027 | 0.0327 | 0.960 |
| GSE302774 | iN SMN-KD vs Scramble | +0.1447 | 0.0437 | **0.00209** |

**Meta (k=5, random effects)**:
- log2FC pooled = **−0.0252**
- 95 % CI = [−0.1826, +0.1322]
- p = 0.754 (NS)
- I² = 81.3 % (hoch-heterogen)
- Linear fold change = 0.983×

**Sensitivity (drop SH-SY5Y, k=4)**:
- log2FC pooled = **+0.0595** (DIRECTION FLIPS)
- 95 % CI = [−0.0503, +0.1694]
- p = 0.2882 (NS)

**Konsistenz mit Original-Claim ↓1.77×** (= log2FC −0.823):
- Target −0.823 liegt **außerhalb** des pooled 95 % CI [−0.183, +0.132].
- Nur 1 von 5 Contrasts enthält −0.823 im 95 % CI (GSE87281 SH-SY5Y,
  und selbst der Punktwert ist −0.546 = ↓1.46×, nicht ↓1.77×).

**Decision (automatisch)**: RETRACTED.

Logik: pooled direction NS (p 0.75) + sensitivity-drop-SH-SY5Y kippt
Richtung → der einzige Signal-Contrast ist ein Outlier, und selbst
dieser produziert nicht den behaupteten Magnitude. Weder Magnitude
noch Direction überleben das Meta.

**CLAIMS_REGISTRY Row 13 Update**: UNDER_REVIEW → **RETRACTED 2026-04-17**
mit vollem Datenanchor-Detail + Hinweis auf `coro1c_rederivation.md`.

**Gate**: U28 → CLOSED. Registry Row 13 ist jetzt definitiv entschieden.
Human Sign-off weiterhin PENDING (Christian Fischer).

**Impact auf Platform-Health**: keine APPROVED-Claim betroffen (Row 13
war bereits non-APPROVED), aber die Governance-Integrität steigt weil
ein weiterer unsourced Claim aus der "UNDER_REVIEW"-Kategorie definitiv
aufgelöst wurde. Platform-wide data anchor health score bleibt 27 %
(4/15) APPROVED-anchored; jetzt 1 zusätzlicher RETRACTED (6/15 RETRACTED
gesamt: #1, #4, #11, #12, #13, #14, #15 → korrigiert 7/15 RETRACTED).

### Cleanup-Statistik U26 + U27 + U28 closing

| Metric | Count |
|---|---|
| URGENT-Items final gefixt | **28/28** (U1-U25 im Hauptpass, U26-U28 in diesem Sub-Pass) |
| Neue DATA_INVENTORY-Row-Anreicherungen | 2 (GSE208629 + GSE287257) |
| Neue Re-derivation-Compute-Runs | 1 (CORO1C meta, k=5, DerSimonian-Laird) |
| CLAIMS_REGISTRY Row-Übergänge | 1 (Row 13: UNDER_REVIEW → RETRACTED) |
| Externe Kommunikation während Cleanup | **0** (gate hold) |

### Qualitäts-Gates dieses Sub-Passes

| Gate | Status |
|---|---|
| Kein silent edit (alle Rows explizit erweitert, nicht ersetzt) | ✅ PASS |
| Re-derivation-Skript + Resultat persistent auf Disk | ✅ PASS (coro1c_rederivation.{py,md,json}) |
| Numerische Werte traceable zu DESeq2 raw outputs | ✅ PASS (raw CSVs unverändert unter meta_analysis/raw/ + data/scrnaseq/GSE302774/) |
| Alle modifizierten Dateien in diesem Sub-Entry-Block dokumentiert | ✅ PASS |
| Triple-LLM-Gate auf coro1c_rederivation.md | PENDING (run as last step) |
| Human Sign-off | PENDING (Christian Fischer) |

### Nächste Schritte

1. `triple_llm_verify.py --file coro1c_rederivation.md` — 3/3 PASS erwartet
   (dokumentierte Retraction mit vollem numerischem Backup)
2. Triple-LLM-Re-run auf GOVERNANCE_AUDIT_2026-04-17.md (jetzt mit 28/28
   URGENT-Items adressiert; sollte 3/3 PASS liefern)
3. Human Sign-off durch Christian Fischer auf Audit-Event 002 End-to-End
4. MEDIUM-Cleanup (M1-M9) scheduling für separate Session

---
