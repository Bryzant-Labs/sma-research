# Standard Operating Procedure — Quality Management System (QMS)

**Zweck**: Pharma-Grade-Qualität für SMA Research Claims.
**Etabliert**: 2026-04-17 nach LIMK2 +2.81× Integritätsvorfall.
**Verbindlich ab**: sofort. Keine externen Comms oder Repo-Commits neuer Claims ohne SOP-Kompliance.

## Die Regel

**Kein numerischer Wert** (log2FC, Fold-Change, p-Value, Effect-Size, %-Wert mit biologischer Bedeutung) darf in einem öffentlichen Dokument (sma-research Repo, Slack, Mega_Pack, PDF, Mail an Kollaborateure, Publikation) erscheinen, **ohne** vorher den kompletten Claims-Lifecycle durchlaufen zu haben.

## Claims-Lifecycle

```
DRAFT → UNDER_REVIEW → APPROVED → [public commit OK]
                               ↓
                         (später: RETRACTED wenn falsch)
```

### Übergang DRAFT → UNDER_REVIEW

- [ ] Primär-Dataset explizit genannt (GEO/SRA/EBI-Accession, **nie Platzhalter wie `GSE...`**)
- [ ] `dataset_verify.py <ACCESSION> --expect-disease ... --expect-organism ... --expect-tissue ... --reject-any ...` → PASS
- [ ] Analyse-Code eincheckbar im Repo (`_scripts/` oder `analysis/`)
- [ ] Rohdaten reproduzierbar abrufbar (FTP-Link in DATA_INVENTORY.md)
- [ ] Positive-Kontrolle dokumentiert (z.B. SMN1/SMN2 bei SMA-Datasets)
- [ ] QC-Metriken (n_samples, mean_depth, mapping_rate) im Output

### Übergang UNDER_REVIEW → APPROVED

- [ ] `triple_llm_verify.py` → **3/3 LLMs PASS**
- [ ] **≥ 2 unabhängige Datasets** bestätigen die Richtung + Größenordnung
- [ ] Mensch-Reviewer signiert im CLAIMS_REGISTRY.md (Datum + Name)
- [ ] Effect-Size-Plausibilität gegen publizierte Literatur geprüft
- [ ] Korrekturliste vorhanden (falls irgendein Check non-trivial fail war)

### Retraction (APPROVED → RETRACTED)

- [ ] Incident-Doc in CORRECTIONS_LOG.md mit Grund
- [ ] Git commit mit "CORRECTION: ..." prefix
- [ ] Alle Orte wo die Claim zitiert wurde (grep-scan) werden aktualisiert
- [ ] Öffentlich-sichtbare Retractions haben ein sichtbares Banner (nicht silent edit)

## Verbotene Praktiken

- ❌ Zahlenplatzhalter wie `GSE...`, `TBD`, `???`, `+X×`
- ❌ Claim aus memory-Datei ins Repo kopieren ohne neu zu verifizieren
- ❌ "Inherited claim from old analysis" ohne explizite Re-Verifikation
- ❌ Einzeldataset-Claims (pharma-standard = mehrfach validiert)
- ❌ Silent edits wenn Claim sich ändert — immer Change-Control Record

## Dateien im QMS

- `CLAIMS_REGISTRY.md` — jede externe numerische Claim mit Status + Reviewer
- `CORRECTIONS_LOG.md` — jede Retraction mit Incident-Doc
- `DATA_INVENTORY.md` — jede GSE/SRA-Accession: verified? code-pfad? n_samples?
- `CHANGE_CONTROL.md` — Protokoll für Claim-Änderungen
- `SOP.md` — diese Datei

## Tools

- `/home/bryza/gpu-fleet/scripts/dataset_verify.py` — Metadata-Gate
- `/home/bryza/gpu-fleet/scripts/triple_llm_verify.py` — 3-LLM Claim-Review
- `/home/bryza/.claude/projects/-home-bryza/memory/rule-dataset-verify-before-use.md` — Hintergrund zur Regel

## Prinzip

Wir wollen Pharma-Grade. Pharma bedeutet: wenn Du es nicht beweisen kannst, hat es nicht stattgefunden. Wenn die Datenspur nicht sauber ist, ist die Claim nicht existent — egal wie überzeugend sie klingt.
