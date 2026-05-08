---
# ── FRONTMATTER YAML ─────────────────────────────────────────────────────────
# Questo blocco è il "biglietto da visita" della skill.
# Claude lo legge per decidere se attivare questa skill per la richiesta corrente.
#
# REGOLA D'ORO: la `description` deve essere abbastanza specifica da evitare
# falsi positivi, ma abbastanza ampia da catturare tutte le varianti linguistiche
# del task. Usa sempre il pattern "USA QUESTA SKILL PER / NON USARE PER".
# ─────────────────────────────────────────────────────────────────────────────

name: analisi-vendite

description: >
  Analizza file CSV di dati di vendita applicando una logica predefinita
  a 4 fasi: validazione → calcolo KPI → classificazione semaforo → insight.
  Produce un report Markdown strutturato con fatturato, margine, trend mensile,
  top prodotti e top clienti, con ogni KPI classificato Verde/Giallo/Rosso.
  USA QUESTA SKILL PER: analizzare file CSV di vendite, calcolare fatturato
  e margine, identificare top prodotti e clienti, generare report KPI,
  classificare performance con semaforo RAG, rilevare anomalie nei dati.
  NON USARE PER: creare grafici o visualizzazioni (usa data-viz), generare
  app web (usa web-app-generator), analizzare dati non di vendita (ordini
  logistici, dati HR, dati finanziari non commerciali).

tools:
  - python
  - read_file
  - write_file

# I trigger sono frasi che l'utente potrebbe dire per attivare questa skill.
# NON sono keyword rigide: servono come guida per il routing semantico.
triggers:
  - "analizza le vendite"
  - "analizza il file CSV"
  - "calcola il fatturato"
  - "calcola il margine"
  - "dammi i KPI di vendita"
  - "genera il report vendite"
  - "top prodotti"
  - "top clienti"
  - "trend mensile vendite"
---

# Skill: analisi-vendite

## Responsabilità

Questa skill governa **l'intera pipeline di analisi** dei dati di vendita:
dal file CSV grezzo fino al report finale con classificazione semaforo.

Non esegue visualizzazioni (grafici, dashboard): si ferma al report Markdown.

---

## Documenti di riferimento da caricare

**Prima di iniziare qualsiasi analisi**, leggi questi file nell'ordine indicato:

```
1. skills/analisi-vendite/references/data-schema.md      ← schema CSV atteso
2. skills/analisi-vendite/references/logica-analisi.md   ← le 4 fasi e le regole
3. skills/analisi-vendite/references/soglie-kpi.md       ← soglie Verde/Giallo/Rosso
4. skills/analisi-vendite/assets/report-template.md      ← template output
```

> **Perché caricarli subito?**
> La logica di analisi e le soglie cambiano periodicamente. Leggerli prima
> garantisce che si usi sempre la versione aggiornata, non quella memorizzata
> dal modello in fase di training.

---

## Workflow a 4 fasi

```
File CSV input
     │
     ▼
┌──────────────────┐
│  FASE 1          │  Validazione schema e qualità dati
│  Validazione     │  → fermati se ci sono errori bloccanti
└────────┬─────────┘
         │ dati validi
         ▼
┌──────────────────┐
│  FASE 2          │  Calcolo KPI (fatturato, margine, trend, top N)
│  Calcolo KPI     │  → usa lo script Python per precisione numerica
└────────┬─────────┘
         │ KPI calcolati
         ▼
┌──────────────────┐
│  FASE 3          │  Classifica ogni KPI → Verde / Giallo / Rosso
│  Semaforo RAG    │  → applica le soglie da soglie-kpi.md
└────────┬─────────┘
         │ KPI classificati
         ▼
┌──────────────────┐
│  FASE 4          │  Genera insight testuali con regole predefinite
│  Insight         │  → applica le regole da logica-analisi.md § Fase 4
└────────┬─────────┘
         │
         ▼
    Report Markdown
    output/report_<id>_<data>.md
```

---

## Istruzioni passo-passo

### Passo 1 — Verifica file di input

```python
# Verifica che il file esista prima di procedere
import os
assert os.path.exists(input_file), f"File non trovato: {input_file}"
```

Se il file non esiste: **fermati**, avvisa l'utente, suggerisci il path corretto.
Non inventare percorsi, non creare file di test al posto suo.

---

### Passo 2 — Carica i documenti di riferimento

Leggi nell'ordine:
1. `skills/analisi-vendite/references/data-schema.md`
2. `skills/analisi-vendite/references/logica-analisi.md`
3. `skills/analisi-vendite/references/soglie-kpi.md`
4. `skills/analisi-vendite/assets/report-template.md`

Tienili in memoria per i passi successivi.

---

### Passo 3 — Fase 1: Validazione

Esegui lo script con il flag `--validate-only`:

```bash
python skills/analisi-vendite/scripts/analizza_vendite.py \
  --input <file> \
  --validate-only
```

**Se la validazione fallisce:**
- Mostra all'utente l'elenco degli errori (riga per riga per errori di schema)
- Distingui tra **errori bloccanti** (campo obbligatorio mancante) e
  **warning** (campo opzionale anomalo)
- Per errori bloccanti: **fermati** e chiedi all'utente di correggere il file
- Per soli warning: continua ma includi i warning nel report finale

---

### Passo 4 — Fase 2 + 3 + 4: Analisi completa

```bash
python skills/analisi-vendite/scripts/analizza_vendite.py \
  --input <file> \
  --output output/report_<nome-file>_<YYYYMMDD>.md \
  --sep ","
```

Sostituisci `<nome-file>` con il nome base del file (senza estensione)
e `<YYYYMMDD>` con la data odierna.

Il nome del file di output deve essere deterministico e tracciabile.

---

### Passo 5 — Leggi e presenta il report

Dopo l'esecuzione:

1. Leggi il file `output/report_*.md` appena generato
2. Estrai il **sommario esecutivo** (sezione `## Sommario Esecutivo`)
3. Presenta all'utente:
   - I 3 KPI principali con il loro colore semaforo
   - Gli insight più rilevanti (max 3)
   - Il path del report completo
4. Chiedi se vuole approfondire un aspetto specifico

---

## Output atteso

```
output/
└── report_vendite_esempio_20260508.md    ← file principale
```

Il report segue il template in `assets/report-template.md`.
Non inventare sezioni extra non presenti nel template.

---

## Gestione degli errori

| Errore | Comportamento |
|--------|---------------|
| File non trovato | Fermati, avvisa, suggerisci path |
| Schema non valido (campi obbligatori mancanti) | Fermati, mostra errori riga per riga |
| Valori anomali (prezzi negativi, quantità = 0) | Warning nel report, continua |
| File vuoto o solo header | Fermati, avvisa che non ci sono dati |
| Encoding non UTF-8 | Riprova con latin-1; se fallisce ancora, chiedi all'utente |
| Script Python non trovato | Non eseguire il calcolo manualmente — avvisa l'utente |

---

## Formato della risposta all'utente

Alla fine dell'analisi, struttura sempre la risposta così:

```
## Analisi completata ✓

**File analizzato**: data/vendite_esempio.csv (N righe)
**Report salvato**: output/report_vendite_esempio_20260508.md

### KPI principali
| KPI | Valore | Stato |
|-----|--------|-------|
| Fatturato totale | €X.XXX,XX | 🟢 Verde |
| Margine % | XX% | 🟡 Giallo |
| Crescita MoM | X% | 🔴 Rosso |

### Insight principali
1. …
2. …
3. …

Vuoi approfondire qualche aspetto (trend, top prodotti, anomalie)?
```
