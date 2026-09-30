# Review of sma-research.info, 2026-09-30

**Method and limits.** I fetched pages and the public API with a web fetcher that summarises pages through a small model, so individual details may be imprecise. I saw the first 5 records of each API list, not the whole corpus. I had no access to the site repository (`sma-platform-v2`), the database or the server. Nothing was changed on the site.

## What I observed

| Observation | Source |
|---|---|
| Site reachable on 2026-09-30; earlier the same day every endpoint returned 503 | fetches |
| API reports 430,087 claims, 318,459 evidence rows, 74,724 hypotheses, 27,983 sources, 17,770 targets, 85 drugs, 485 trials | `/api/v2/stats` |
| First 5 claims: all `confidence` 0.5, `claim_state` hypothesis, `provenance_status` needs_review; metadata says "NOT an SMA efficacy claim" | `/api/v2/claims?limit=5` |
| First 5 hypotheses: all the same MDM2 text, `confidence` 1.0, `status` proposed, `generated_by` a Claude model, "2 claims from 1 independent source" | `/api/v2/hypotheses?limit=5` |
| Drug records: Haloperidol and Riluzole `needs_review`, `approved_for` empty | `/api/v2/drugs` |
| `/drugs/haloperidol/` HTML contains only "Loading drug..." | page fetch |
| `/evidence/` and `/targets/limk2/` return 404 | page fetch |
| Sitemap: 137 URLs, no per-drug or per-target detail pages | `/sitemap.xml` |
| About page does not mention the retractions or how corrections are made | `/about/` |
| Disclaimers "computational predictions, not validated" are present | home, hypotheses |

## Assessment

**Good:** the disclaimers, the provenance and `needs_review` flags, and the "prior art, not an SMA claim" wording on ChEMBL and OpenTargets claims are the right approach.

**Problems:**

1. **Retractions are not visible on the site**, although the repo documents them. A reader can find the old claims in the corpus without the correction.
2. **Hypothesis confidence of 1.0 is not supported.** The text itself says 2 claims from 1 source. A saturated number from a language model reads as certainty.
3. **Duplicated hypotheses.** The five records I saw differ only in ID and timestamp. With 74,724 hypotheses, duplicates may inflate the count. I did not check the full set.
4. **A constant confidence of 0.5** on every sampled claim carries no information and should not be shown as a score.
5. **Detail pages are not indexable.** Drug and target pages load content in the browser. Search engines and readers without JavaScript see "Loading". The April plan for static detail pages (20,344 hypothesis pages, 803 target pages, 101 drug pages) does not appear in the live sitemap; I do not know whether it was merged.
6. **Counts without definitions.** "430,087 claims" mixes automatically extracted literature claims, ChEMBL and OpenTargets imports and model predictions. A reader cannot tell them apart.

## Proposed additions

1. Publish `website/corrections_page_DRAFT.md` as `/corrections/`, linked from About and from each affected target page.
2. Mark retracted claims in the corpus (`claim_state = retracted`) and show a banner on any page that cites one.
3. Replace hypothesis `confidence` with an evidence count (independent sources, claim count) and an explicit label "unvalidated hypothesis". Deduplicate by normalised title and target.
4. Split the headline counts by claim origin (literature extraction, database import, computed prediction).
5. Prerender drug, target and hypothesis pages, or add server-side rendering, and add them to the sitemap. Check first whether the April pull request was merged.
6. Add a "Data as of" date and a short methods paragraph on scoring (see the last section of the corrections draft).

## Open questions for Christian and Codex

- Is the April static-detail-page work live? If not, why?
- Who owns the duplicate and confidence logic in the hypothesis generator?
- Should retractions be recorded in the database or only in the QMS documents?
