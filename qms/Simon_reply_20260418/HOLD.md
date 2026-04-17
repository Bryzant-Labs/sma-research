---
status: HOLD
gate_state: RED — 2 of 3 PERP artifacts failed triple-LLM
built_by: overnight autonomous agent (2026-04-17 → 2026-04-18)
escalation: do NOT send. do NOT promote any DRAFT → APPROVED. Simon-Comms-Gate HELD.
rule: "IF any of the 3 triple-LLM gates FAILS: STOP, write HOLD.md, do NOT proceed" (Christian sleep brief, 2026-04-17)
---

# Simon-Reply PERP Arm — HOLD

The PERP arm of the 2026-04-18 Simon reply was gated overnight. Two of the three
required triple-LLM gates returned FAIL. Per hard rule, chapter assembly and send-pack
construction were NOT performed. Christian must decide how to proceed (re-compute,
re-draft, or cut the PERP arm from the reply) before any send can happen.

## Gate state summary

| # | Artifact                                                      | Verdict    | Pass/Total | Notes |
|---|---------------------------------------------------------------|------------|------------|-------|
| 1 | `perp_pocket3_RESULTS.md` (Pocket 3 PXM, 600 mol, top iptm 0.874 diphenyl-quinazolinone)   | **PASS**  | 3/3  | Clean. Caveats already present in doc. |
| 2 | `perp_genmol_hop_RESULTS.md` (4915 mol GenMol-hop, top sel_z +2.16 THP-sulfonamide)        | **FAIL**  | 0/3  | Partial Boltz-2 rescore (33/150). All 3 LLMs flagged same blocker. |
| 3 | `PERP_dossier/` (5 core biology .md files, 673 lines, agent aef1e237)                       | **FAIL**  | 4/5 files PASS; 1 file FAIL 2/3 | `PERP_NMJ_interface_druggability.md` blocked by Groq for AF2-Multimer weakness + membrane context. |

**Aggregate: RED.** Chapter and send-pack NOT built.

---

## Gate 1 — perp_pocket3 → PASS 3/3

Verdict file: `perp_pocket3_triple_llm.json`

- OpenAI GPT-4o: PASS
- Groq Llama-3.3-70B: PASS
- Gemini 2.0 Flash: PASS

Non-blocking notes (for future polish, not failure):
- Add a short explanation of what Boltz-2 iptm means for non-modeller readers
- Membrane-aware refinement of AF2 monomer would strengthen Pocket 3 geometry
- State limitations of a single AF2 model for pocket ID, especially low pLDDT N-terminus

**Status: ready for external reference IF the other gates had passed.** They did not.

---

## Gate 2 — perp_genmol_hop → FAIL 3/3

Verdict file: `perp_genmol_hop_triple_llm.json` (mirrored from `/home/bryza/sma-research/qms/perp_genmol_hop_triple_llm.json`)

All three LLMs independently flagged the same root cause: **the Boltz-2 rescore
was terminated mid-run** (33 / 150 compounds fully scored across the 5-target panel),
and the top-5 selectivity_z ranking is derived from that partial library. The document
itself contains the sentence:

> "Do not cite specific selectivity_z values in external communication until
> rescore reaches n ≥ 100 compounds."

…and then lists specific selectivity_z values in a table. Gemini flagged this as a
direct internal contradiction. OpenAI flagged unsourced numerical claims and
preliminary status. Groq flagged DRAFT status + server-instability truncation.

### Root cause

`sma-h100-two:8003` Boltz-2 server instability: supervisor-restart cycles,
concurrent `perp_pocket3_alphaC` rescore consuming the same queue, zombie CLI
processes holding GPU memory. Rescore stopped at ~182 of 750 calls (24 %).

### Remediation (not done tonight, queued for Christian decision)

- [ ] Re-stabilise `sma-h100-two:8003` (clear zombie processes, restart supervisor)
- [ ] Re-run `run_boltz2_rescore.py` to drain to full n=150 (or at least n ≥ 100
      so the within-library z-scores are defensible)
- [ ] Re-run `aggregate_top_hits.py` to refresh `top_hits.tsv`
- [ ] Re-gate document through `triple_llm_verify.py`
- [ ] **Do NOT re-cite current top-5 selectivity_z values in any Simon-facing text.**
      The numbers WILL shift. Current values must be treated as "rank-signal only",
      not as citable.

---

## Gate 3 — PERP_dossier → FAIL (4/5 files PASS; 1 file blocked)

The PERP dossier was gated file-by-file (5 files × 3 LLMs = 15 verdicts)
because the consolidated concat is 54 KB and the triple_llm_verify tool truncates
input at 8 000 chars. Per-file verdict files live in
`/home/bryza/sma-research/qms/Simon_reply_20260418/dossier_gates/`.

| File                                     | Lines | Chars | OpenAI | Groq | Gemini | Overall |
|------------------------------------------|-------|-------|--------|------|--------|---------|
| PERP_SMA_expression.md                   | 89    | 7 763 | PASS   | PASS | PASS   | **PASS** |
| PERP_NMJ_relevance.md                    | 131   | 9 683 | PASS   | PASS | PASS   | **PASS** |
| PERP_NMJ_interface_druggability.md       | 96    | 9 572 | PASS   | **FAIL** | PASS | **FAIL** (2/3) |
| PERP_structure_biology.md                | 178   | 12 541| PASS   | PASS | PASS   | **PASS** |
| PERP_literature_review.md                | 179   | 14 531| PASS   | PASS | PASS   | **PASS** |

### The blocker: PERP_NMJ_interface_druggability.md

Groq Llama-3.3-70B flagged 4 blocking issues (OpenAI + Gemini PASS, both noted
minor suggestions only):

1. **Low iptm confidence for all heterodimers (0.14–0.29 range).** The document
   presents AF2-Multimer iptm scores for PERP-NMJ-partner heterodimers that are
   in the weak-interface band. These values are too low to support a confident
   druggability claim.
2. **C-terminal-tail dominance in interfaces, potentially an AF2-Multimer artifact.**
   AF2-Multimer is known to over-weight flexible regions (C-terminal tails,
   disordered loops) because these give the model the easiest way to satisfy the
   contact-plausibility objective. The document flags multiple C-terminal-tail-
   mediated interfaces — Groq called these out as potentially spurious.
3. **Missing membrane context in ColabFold multimer folds.** PERP is a 4-pass TM
   protein. The ColabFold folds used for interface analysis are in solution,
   without an explicit POPC bilayer. TM-face interfaces cannot be trusted without
   membrane-embedded refinement.
4. **Incomplete analysis.** 12 of the 14 scheduled PERP heterodimer folds are not
   yet locally available at draft time; the interface claims are made from a
   partial sample (2 of 14, extrapolated).

### Why this matters for Simon

Simon is a neurobiologist working on NMJ / Schwann-cell biology. Showing him
a druggability claim derived from weak-confidence AF2-Multimer folds with known
artifact-prone C-terminal-tail dominance, no membrane context, and a 2-of-14
sample size, would expose the methodology to a first-round objection we cannot
answer tonight. That is exactly the kind of unforced error the QMS process was
put in place to prevent (after the LIMK2 placeholder incident, 2026-04-17).

### Remediation (not done tonight, queued for Christian decision)

- [ ] Boltz-2 multimer re-fold of the 14 PERP-partner heterodimers (higher iptm
      calibration, less C-tail bias in the pairing model)
- [ ] Membrane-embedded MD refinement (OpenMM + POPC bilayer, 20 ns) on the 2
      folds already in hand before any new comms uses them
- [ ] Complete the 12 pending PERP heterodimer folds so the sample size is 14/14
- [ ] Re-write `PERP_NMJ_interface_druggability.md` with the stricter confidence
      framing (iptm bands, explicit AF2-Multimer caveats, membrane-context
      limitation)
- [ ] Re-gate through triple_llm_verify

---

## What was NOT done (per hard rule)

- No `PERP_chapter.md` written
- No `email_body_DE.txt` drafted
- No PDFs exported to `attachments/`
- No `READY_TO_SEND.md` status file created
- No DRAFT → APPROVED promotion of any artifact
- No touch to Dropbox, Slack, Telegram, Gmail, LinkedIn
- No change to CLAIMS_REGISTRY.md status columns

The `Simon_reply_20260418/` directory contains ONLY the triple-LLM verdict JSONs
and this HOLD.md. No external-facing assets.

---

## Decisions Christian needs to make in the morning

1. **genmol_hop:** re-run rescore to n ≥ 100 and re-gate? Or drop this arm from
   the reply and go with pocket3 only?
2. **interface_druggability:** Boltz-2 multimer re-fold + membrane MD on the 2
   existing folds (plus completing the 12 missing ones)? Or cut the "binder
   modality" / NMJ-interface section from the Simon reply and ship only the
   small-molecule story (pocket3 + pocket biology)?
3. **Scope of the PERP arm:** If (1) and (2) are both "defer", we can still send
   a narrower chapter built ONLY from the 4 passing dossier files
   (SMA_expression + NMJ_relevance + structure_biology + literature_review) +
   pocket3 small-molecule druggability. That would be biology + first-pass small
   molecule only, no binder/bispecific claims, no NMJ-interface druggability
   claims. Viable but scope-cut.

None of these decisions can be made autonomously — they involve trade-offs
between compute time cost (re-run ~4–8 GPU hours for rescore + multimer re-fold
+ 20 ns membrane MD) and delay to Simon.

---

## Paths

- This file: `/home/bryza/sma-research/qms/Simon_reply_20260418/HOLD.md`
- Verdict: pocket3 → `/home/bryza/sma-research/qms/Simon_reply_20260418/perp_pocket3_triple_llm.json`
- Verdict: genmol_hop → `/home/bryza/sma-research/qms/Simon_reply_20260418/perp_genmol_hop_triple_llm.json`
- Per-file dossier verdicts → `/home/bryza/sma-research/qms/Simon_reply_20260418/dossier_gates/`
- Consolidated dossier (for reference only, not gated as one unit) → `/home/bryza/sma-research/qms/Simon_reply_20260418/PERP_dossier_consolidated.md`
- Existing LIMK2 retraction brief §5 (German, already drafted) → `/home/bryza/sma-research/qms/LIMK2_retraction_brief_INTERNAL.md`
- Existing meta-analysis → `/home/bryza/sma-research/qms/meta_analysis/CORRECTED_SIGNATURE.md`

## Simon-Comms-Gate

**HELD.** Status unchanged from pre-sleep state. No send authorised. Christian
must type the send command manually tomorrow after reviewing this HOLD + making
the scope decisions above.
