# PERP — Digital Twin Integration

**STATUS: DRAFT, 2026-04-17. Awaits triple_llm_verify 3/3 PASS. Not for external comms.**

---

## 1. Summary

The sma-research MCP server exposes a `simulate_sma_digital_twin` tool. Its published signature ONLY accepts a drug-name string from a **fixed 6-drug whitelist**: `Nusinersen, Risdiplam, 4-Aminopyridine, Apitegromab, NMN, GV-58`. It does NOT accept:
- arbitrary target-gene names as input,
- knockdown / overexpression scenarios,
- peptide or small-molecule SMILES.

**Consequence: the digital twin tool cannot simulate "PERP knockdown" or "PERP overexpression" as the task brief requested.** PERP is a target gene, not a drug in the twin's library. Attempting to call the tool with `drugs="PERP"` would either error out or silently return results for a mis-parsed drug name — neither is scientifically valid output.

**Additional permission blocker.** The tools `simulate_sma_digital_twin`, `validate_sma_hypothesis`, `get_sma_evidence_for_target`, `search_sma_targets`, `get_sma_nmj_signaling`, and `get_sma_regulatory_pathways` all returned "Permission to use ... has been denied" when invoked from this Claude Agent session. The tools that DID return data were `get_sma_target`, `search_sma_claims`, and `get_sma_hypotheses`.

Task 2 is therefore split into two deliverables:
1. **What the twin COULD tell us about a PERP-targeted arm** (mechanistic reasoning, not simulation).
2. **Evidence from the MCP knowledge base (allowed tools)**.

No external comms.

---

## 2. Target-registry verification

`mcp__sma-research__get_sma_target(symbol="PERP")` returned:

```
Name: TP53 Apoptosis Effector Related To PMP-22
Type: gene
Organism: Homo sapiens
Description: p53-regulated tetraspanin-like protein involved in apoptosis and cell
adhesion. Direct p53 target gene upregulated during apoptosis. Dual function:
pro-apoptotic p53 effector and desmosomal component. Homology to PMP-22/GAS3
(hereditary neuropathy gene). Rationale for SMA: p53 is activated in SMA motor
neurons pre-symptomatically, p53 inhibition rescues MNs in severe SMA models.
PERP is an unexplored p53 effector in neurodegeneration.
ID: f32cd9b9-30ef-4aea-b092-bf71f9488ddc
Created: 2026-03-31T12:11:11.792159+00:00
```

Notes:
- The MCP registry knows PERP as a gene (not a drug).
- The description's SMA framing cites the p53-MN activation evidence (well-established) and labels PERP as "unexplored" — consistent with our dossier's own literature review.
- **Family assignment disagreement**: MCP describes PERP as "homologous to PMP-22/GAS3". UniProt Q96FX8 places PERP in the **TMEM47 subfamily** of the PF00822 clan, with only ~1.1-1.6% 4-mer identity to PMP22. The MCP's wording is technically correct at the Pfam-clan level but is misleading at the subfamily level. Fix in next MCP curation cycle: update the PERP description to say "PMP-22/EMP/MP20/Claudin Pfam clan (PF00822), TMEM47 subfamily".

---

## 3. Hypothesis-base search for PERP

`mcp__sma-research__get_sma_hypotheses()` returned 7.1 MB of hypothesis records. Grep on `\bPERP\b` (case-sensitive, word-boundary): **0 hits**. The curated hypothesis library contains NO PERP-specific mechanism statements.

By contrast, ROCK1/ROCK2/LIMK1/LIMK2 each have 10+ hypothesis entries. PERP is a completely uncultivated target in this knowledge base.

**Action item**: after the Simon reply pack lands, feed the PERP literature review (`PERP_literature_review.md`), NMJ relevance (`PERP_NMJ_relevance.md`), and structure biology (`PERP_structure_biology.md`) into the MCP ingestion pipeline to populate 3-5 tier-C PERP hypotheses in the knowledge base.

---

## 4. What the digital twin COULD tell us about PERP indirectly

Since the twin is drug-centric, the relevant question is: **are any of its 6 drugs predicted to modulate PERP-adjacent biology?**

Available drug list:
| Drug | Primary target / mechanism | PERP link? |
|---|---|---|
| Nusinersen | ASO, SMN2 exon 7 splicing, increases SMN protein | Indirect only (raises SMN -> reduces MN stress -> may lower p53 activation -> may lower PERP transcription). Cannot test PERP-specific effect in drug-centric twin. |
| Risdiplam | Small-molecule SMN2 splice modifier | Same as Nusinersen (indirect). |
| 4-Aminopyridine | Potassium channel (Kv) blocker, broadens axonal AP | No direct PERP link. Modulates NMJ excitability; PERP interactome at NMJ is speculative. |
| Apitegromab | Anti-myostatin mAb | Muscle-side only (satellite/myofiber GDF8). No PERP overlap. |
| NMN | NAD+ precursor, sirtuin/PARP substrate | Upstream of many p53 pathways but PERP is downstream of p53 activation; NMN effect on PERP would be context-dependent (p53/SIRT1 acetylation) and not captured by the twin. |
| GV-58 | T-type Ca2+ channel agonist, boosts NMJ transmission | No direct PERP link. |

**Conclusion**: the twin's 6-drug panel cannot directly simulate a PERP-knockdown arm. Running `simulate_sma_digital_twin` with any of these drugs produces results about their canonical mechanisms, NOT about PERP.

**If the twin is extended in a future cycle**, two natural additions would enable a PERP arm:
1. **"H2b_9_s2 binder" OR "PERP-ECL2 peptide"** as a new drug-like entity whose target is PERP. Would require adding a PERP-NMJ signaling compartment to the twin's compartment model.
2. **"PERP siRNA" / "PERP ASO"** entry that directly models transcript suppression. Would require the twin to model gene-expression state, not just drug-target pharmacodynamics.

Both are tractable additions to the twin codebase (`/home/bryza/.claude/mcp-servers/sma-research/sma_server.py`) but are outside the "3-4 hr, no GPU rental" scope of the current nice-to-have task.

---

## 5. Recommended "PERP scenario" to ingest when twin is extended

For later implementation (not executed in this task):

| Perturbation | Predicted twin output (mechanistic reasoning, not simulation) | Confidence |
|---|---|---|
| **PERP knockdown, SMA MN** | -- p53 -> caspase amplification via PERP (published mechanism), -- apoptosis at NMJ, + NMJ viability. Side effect: possible keratinocyte defect (mirrors EKVP7/OLMS2 patient skin phenotype — but note PERP null patients have NORMAL nervous system in published reports, so the CNS is safe). | Medium |
| **PERP overexpression, SMA MN** | + p53/caspase signaling, + MN loss, worse NMJ phenotype. | Low — no published overexpression data, hypothetical. |
| **PERP ECL2 binder (H2b_9_s2), SMA MN** | Blocks PERP extracellular face (homo/heterodimer assembly at the NMJ). If PERP's pathogenic role is via desmosome-like junctions with a post-synaptic partner (our compute hypothesis), binder would disrupt that interaction, rescue NMJ. | Low — depends on whether PERP physically engages an NMJ partner; our 6 heterodimer folds (iptm 0.14-0.29) do NOT support high-confidence physical PERP-NMJ complexes. See `PERP_compute_status.md` §2. |

**Honest position**: this table is mechanistic inference, NOT simulation output. It is included for completeness of the dossier and to document what the digital-twin extension would have to model in a future sprint.

---

## 6. What we DID use from the MCP

| Tool | Called | Result |
|---|---|---|
| `get_sma_target(symbol="PERP")` | Yes | Returned curated target record (see §2) |
| `search_sma_claims(query="PERP NMJ motor neuron apoptosis p53")` | Yes | Returned 50 claims, NONE specific to PERP — all hits were generic SMA claims containing the query words. Zero PERP-specific evidence rows in the registry. |
| `get_sma_hypotheses()` | Yes | Returned full library (7.1 MB); grep found 0 PERP hypothesis entries. |
| `simulate_sma_digital_twin(drugs="...")` | Attempted | **Permission denied** + tool is drug-only anyway (see §1). |
| `validate_sma_hypothesis(...)` | Attempted | Permission denied. |
| `get_sma_evidence_for_target(target_id="...")` | Attempted | Permission denied. |
| `get_sma_nmj_signaling()` | Attempted | Permission denied. |
| `get_sma_regulatory_pathways()` | Attempted | Permission denied. |

The denied tools would have enabled deeper pathway-level integration. Flag for next session: request these permissions be whitelisted for PERP-dossier completion.

---

## 7. Deliverables

- `/home/bryza/sma-research/qms/PERP_dossier/PERP_digital_twin.md` (this file)
- `/home/bryza/sma-research/qms/PERP_dossier/digital_twin/` — empty directory reserved for future extension runs

---

DRAFT — update after triple_llm_verify PASS. No external comms.
