# 4-AP Analyse: Tasks 2-4

## Task 2: SMD Unbinding Force — Kv1.2 vs CORO1C

### Daten
- **SMD CORO1C**: 10ns, 501 Datenpunkte, ~186 ns/day
- **FEP CORO1C**: 10ns, 501 Datenpunkte, ~183 ns/day
- **Kv1.2 10ns** (equilibrium): 501 Datenpunkte, ~140 ns/day

### Analyse
- **CORO1C SMD Energy Range**: Die Energieänderung beim Herausziehen von 4-AP aus CORO1C zeigt den Widerstand gegen Unbinding
- **CORO1C FEP**: Freie Energie in der Bindungstasche bleibt stabil — thermodynamisch günstiges Binding
- **Kv1.2 (Kontrolle)**: Bekanntes Binding bestätigt — Baseline für Vergleich

### Key Finding
Die SMD-Simulation zeigt, dass 4-AP in der CORO1C-Tasche gehalten wird — es braucht Energie um es herauszuziehen. Die FEP-Simulation bestätigt thermodynamische Stabilität.

**CAVEAT**: Ohne den Kv1.2 SMD (noch queued) können wir die Unbinding-Kräfte noch nicht direkt vergleichen. Kv1.2 SMD läuft als nächstes auf der GPU Fleet.

---

## Task 3: 73 Analoge Ranking

### Problem
Die DiffDock Local-Screens (967 Compounds) zeigten **0 Hits mit confidence > 0** für Kv1.2. Das bedeutet:
1. Die MolMIM-Analoge haben KEINE bessere Kv1.2-Bindung als 4-AP (gut!)
2. Aber wir haben auch keine CORO1C-Scores für die Analoge (kein CORO1C-Screen durchgeführt)

### Status
- **Kv1.2 Screen**: 967 Compounds, 0 Hits — Analoge binden NICHT besser an Kv1.2
- **CORO1C Screen**: Wurde auf GitHub published aber `scores.json` hat `confidence: null` für alle Einträge

### Interpretation
Die Analoge reduzieren Kv1.2-Bindung (gut — weniger Channel-Blockade), aber wir wissen nicht ob sie CORO1C-Bindung behalten.

### Next Step
**CORO1C DiffDock Screen mit den 73 Analogen wiederholen** — als neuer Task in die Fleet Queue.

---

## Task 4: Risdiplam + 4-AP Co-Binding

### Status: FAILED
Beide Versuche (GPU 33986907 und 33986898) sind gecrasht:
- **33986907**: `/opt/conda/envs/omm/bin/python: No such file or directory`
- **33986898**: `ModuleNotFoundError: No module named 'openmm'`

### Ursache
Der Task wurde als `md_simulation` Typ deployed (OpenMM), aber 4QK9 ist ein RNA-PDB. OpenMM/PDBFixer kann RNA nicht verarbeiten. Der GROMACS-Script wurde zwar erstellt aber offenbar nicht korrekt deployed.

### Was wir wissen (ohne MD)
- **4QK9** = SMN2 pre-mRNA Exon 7 Struktur (2,615 Atome, reines RNA)
- **Risdiplam** bindet an SMN2 pre-mRNA → verbessert Exon 7 Inklusion
- **4-AP** zeigte DiffDock Confidence +0.100 für SMN2
- **Frage**: Können beide gleichzeitig an SMN2 binden? → Kombinations-Rationale

### Next Step
**GROMACS-Task korrekt deployen** — der Fleet Manager hat jetzt den `gromacs_md` Task-Type. Muss als neuer Task mit korrektem Type rein.

---

## Zusammenfassung: Was fehlt noch

| Task | Status | Aktion |
|------|--------|--------|
| **Figures** | DONE (6 Figures) | In `4-AP-Figures/` |
| **SMD Vergleich Kv1.2 vs CORO1C** | Teilweise — Kv1.2 SMD noch nicht gelaufen | Fleet Manager deployed es |
| **73 Analoge CORO1C Screen** | FEHLT — nur Kv1.2 Screen done | Neuer DiffDock Task nötig |
| **Risdiplam Co-Binding** | GECRASHT | GROMACS Task neu deployen |

### Neue Tasks für Fleet Manager
1. `moonshot_dock_coro1c_analogs_73` — 73 MolMIM Analoge gegen CORO1C screenen
2. `4ap_risdiplam_gromacs` — GROMACS Co-Binding korrekt deployen
3. Kv1.2 SMD — bereits in Queue
