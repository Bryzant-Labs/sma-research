# Übergabe Claude -> Codex: Treffer-Eichung vor Skalierung

**Datum:** 2026-09-30
**Von:** Claude-Session `sma-research-79` (Cloud-Sandbox, nur Repo + öffentliches HTTPS)
**An:** Codex (über Christian; es gibt keinen direkten Kanal)
**Status:** Vorschlag, nichts davon ist ausgeführt oder verifiziert

## Was ich nicht gesehen habe

- Den Dropbox-Ordner `Simon/00 - DAY - 00` und Codex' Arbeit der letzten Wochen (liegt nicht im Repo).
- Den B300-Plan.
- Keinen Zugriff auf moltbot, Flotte oder Postgres. Alle Aussagen unten stützen sich auf die committeten Dokumente bis 2026-05-27 und den Index-Branch vom 2026-08-16.

## Befund aus dem Repo (Kurzfassung)

1. `qms/chembl_ki_calibration_RESULTS.md`: Boltz-2-ipTM sagt Ki kaum voraus (R² 0,007 LIMK2, 0,022 JAK2, 0,158 ROCK2, 0,307 MAPK14; n=20 je Kinase). ipTM sättigt bei 0,88–0,99.
2. `findings/2026-04-26/off_target_cluster_triage.md`: über 60 Treffer bei ipTM >= 0,97 werden als "Repurposing-Leads" bzw. "Sicherheitssignale" gelesen. Riluzole und 4-AP treffen dieselben Kinasen (BTK, PTK6, PRKX, TEC, FGR, CSK): Verdacht auf ATP-Taschen-Bias.
3. `qms/CLAIMS_REGISTRY.md`: Claims #6/#7 sind `APPROVED`, obwohl das Konfidenzintervall nach Entfernen von SH-SY5Y die Null einschließt (I² 75–92 %). Freigabe durch 3-LLM-Konsens ist keine Validierung.
4. README nennt ROCK2-Hemmung "Flagship", Registry hat "Achse hyperaktiv" zurückgezogen (ROCK2 in allen 5 Kontrasten herunterreguliert). Begründung muss neu geschrieben werden (Expression ist nicht Aktivität).

## Vorschlag: Eichung vor dem Skalieren

Ziel: klären, ob ein Score (ipTM, Affinity-Head, Vina/GNINA) echte Information trägt oder nur Molekülgröße, Assayformat oder Veröffentlichung.

**Schritte (billigster zuerst):**

1. **Trivialdecke:** AUROC der besten Einzeldeskriptoren (Ringzahl, aromatische Ringe, HBD, Schweratome, logP, TPSA, FractionCSP3), beide Vorzeichen.
2. **Gruppentrennung:** Murcko-Gerüst UND `document_chembl_id`; die strengere zählt. Kein Zufallssplit.
3. **Gewinn gegen die Decke:** gepaarter Bootstrap auf Gruppenebene (ganze Veröffentlichungen ziehen). Gewinn belegt nur, wenn die untere Grenze des 95-%-KI > 0.
4. **Konfounder stratifizieren:** Assayformat (`bao_label`), Messgröße (Ki/Kd vs. IC50), Molekülgröße (Docking-Score vs. Schweratome), Unordnungsfraktion.

**Negativklasse (Reihenfolge):** Inaktive aus demselben Assay > zensierte ChEMBL-Werte (`standard_relation = '>'`) > Zufallsmoleküle (nur mit Vermerk, dann optimistisch). Mindestens 20 je Klasse und mindestens 5 Gruppen, sonst "trägt keine Eichung".

**Strukturkennzahlen (ipTM etc.):** Positivklasse = etablierte Interaktionen aus der Literatur; je Konstrukt ein Median; nach Komplextyp aufteilen; gegen die Unordnungsfraktion als naheliegende Alternative prüfen.

### Kill-Kriterium (vor der Rechnung festgelegt)

Der Score wird als Rangfolge für die Trefferauswahl gestrichen, wenn bei dokumentgetrennter Auswertung der Gewinn gegen die beste Einzeldeskriptor-Decke kein `lo > 0` erreicht. Ein belegter Gewinn bei AUROC < 0,5 zählt nicht.

### Konkrete Aufgaben

- [ ] Je Ziel 200–1.000 ChEMBL-Aktive gegen Negative (siehe oben) mit Boltz-2 rechnen; **Affinity-Head mitrechnen**, nicht nur ipTM.
- [ ] Bekannten Chai-1-Fehler beheben (`'StructureCandidates' object is not iterable`, PERP R3 Cross-Val), damit die orthogonale Stufe überhaupt Werte liefert.
- [ ] Tabelle je Ziel: `n_aktiv/n_inaktiv | Gruppen | Decke (Deskriptor) | Modell gerüstgetrennt | Modell dokumentgetrennt | Gewinn mit 95-%-KI | Urteil`.
- [ ] Shortlist (~100–200) mit alchemischen Bindungsenergien nachrechnen (z. B. OpenFE), statt sich auf MM-PBSA zu stützen.

## Rückmeldung an Christian / Claude

Bitte die Antworten in `handoff/CODEX_REPLY_<datum>.md` ablegen (gleicher Branch oder Dropbox-Ordner `00 - DAY - 00`) und dort ausdrücklich nennen:

1. Was wurde in den letzten Wochen gemacht, wo liegen die Ergebnisse (Pfad/Branch)?
2. Wo liegt der B300-Plan, und welche Annahmen stecken drin (Ziele, Bibliothek, Score)?
3. Welche Checks aus der Liste oben wurden schon gerechnet, mit welchem Ergebnis?
4. Was hat keinen Zugang bzw. wurde nicht geprüft? ("Kein Zugang" ist eine vollwertige Antwort.)

## Nicht enthalten

Keine Zugangsdaten, Hostnamen oder Cluster-Details. Diese gehören nicht in ein öffentliches Repo.
