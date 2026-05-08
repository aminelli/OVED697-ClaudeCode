---
# ── FRONTMATTER YAML ─────────────────────────────────────────────────────────
#
# Questo è il CONTRATTO della skill: definisce come Claude deve comportarsi
# quando genera un artifact da un CSV.
#
# DIFFERENZA CHIAVE rispetto all'artifact.md:
#   • artifact.md  → definisce il RISULTATO (cosa produrre)
#   • SKILL.md     → definisce il PROCESSO (come produrlo)
#
# La skill orchestra tutte le fasi: legge il CSV, sceglie l'artifact,
# popola il template, valida l'output.
# ─────────────────────────────────────────────────────────────────────────────

name: artifact-generator

description: >
  Skill per generare artifact (HTML, Markdown) a partire da un file CSV.
  Legge la definizione artifact.md, valida i dati in input, popola il
  template con i dati reali, verifica la qualità e salva il file.
  USA QUESTA SKILL PER: qualsiasi comando che produce un file HTML o
  Markdown da dati CSV in questo progetto.
  NON USARE PER: analisi statistiche approfondite (usa analisi-vendite),
  generare codice applicativo, rispondere a domande sui dati.

triggers:
  - "genera dashboard"
  - "genera report"
  - "genera presentazione"
  - "genera componente"
  - "crea dashboard"
  - "visualizza dati"
---

# Skill: artifact-generator

## Workflow

```
┌────────────────────────────────────────────────────────────┐
│  FASE 1 — Leggi la definizione artifact                    │
│  Apri artifacts/<nome>/artifact.md                         │
│  Estrai: tipo, colonne obbligatorie, path output, regole   │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  FASE 2 — Carica e valida il CSV                           │
│  Leggi il file CSV con csv.DictReader                      │
│  Verifica che tutte le required-columns siano presenti     │
│  Se mancano colonne → stop con messaggio chiaro            │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  FASE 3 — Trasforma i dati                                 │
│  Calcola KPI aggregati (groupby, sum, max, ecc.)           │
│  Costruisci le strutture dati per i placeholder            │
│  Serializza in JSON per i template HTML                    │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  FASE 4 — Genera l'artifact                                │
│  Leggi artifacts/<nome>/template.*                         │
│  Sostituisci ogni {{PLACEHOLDER}} con il valore reale      │
│  NON lasciare placeholder residui nel file finale          │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  FASE 5 — Valida e salva                                   │
│  Verifica le quality-rules dell'artifact                   │
│  Calcola il path output dal pattern nell'artifact.md       │
│  Salva nella cartella output/                              │
│  Conferma all'utente con il path completo                  │
└────────────────────────────────────────────────────────────┘
```

## Istruzioni passo per passo

### Passo 1 — Leggi il contratto artifact

Prima di toccare il CSV, apri `artifacts/<nome>/artifact.md` e leggi:
- `artifact:type` → ti dice che tipo di file generare
- `artifact:input.primary.required-columns` → colonne obbligatorie nel CSV
- `artifact:input.primary.optional-columns` → colonne opzionali (abilita funzioni extra)
- `artifact:output.path-pattern` → come costruire il nome del file
- `artifact:quality-rules` → lista di verifiche da fare sull'output

### Passo 2 — Carica e valida il CSV

Usa Python (`python` via Bash) per leggere il CSV:
```python
import csv, json
with open(csv_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    headers = reader.fieldnames
```

**Validazione obbligatoria:**
- Verifica che ogni `required-column` sia in `headers`
- Se una colonna è mancante, fermati e mostra: `ERRORE: colonna '<nome>' non trovata. Colonne presenti: [...]`
- Le `optional-columns` non bloccano, ma abilitano/disabilitano sezioni del template

### Passo 3 — Trasforma i dati

Per il tipo `html-interactive` (dashboard):
- Serializza tutte le righe in JSON: `json.dumps(rows, ensure_ascii=False)`
- Calcola liste univoche ordinate: mesi, regioni, categorie
- I valori numerici devono essere `float` nel JSON (non stringhe)

Per il tipo `markdown-doc` (report):
- Calcola totali per gruppo con un dizionario
- Costruisci le tabelle Markdown come stringhe Python (pipe tables)
- Calcola le variazioni MoM: `(val_mese - val_prec) / val_prec * 100`

Per il tipo `html-presentation`:
- Genera le righe `<tr>` delle tabelle come stringhe HTML
- Sintetizza i top-3 insight in frasi brevi (max 1 riga ciascuna)

### Passo 4 — Popola il template

Leggi il template come testo grezzo, poi sostituisci:
```python
with open('artifacts/<nome>/template.<ext>', encoding='utf-8') as f:
    output = f.read()

output = output.replace('{{DATA_JSON}}', json_str)
output = output.replace('{{TITOLO}}', titolo)
# ... tutti i placeholder
```

**Regola critica:** Dopo le sostituzioni, controlla con una regex che non ci siano
`{{...}}` residui. Se ce ne sono, qualcosa è andato storto — non salvare.

### Passo 5 — Valida e salva

1. Costruisci il path di output dal `path-pattern`:
   - `{{NOME_FILE}}` → basename del CSV senza estensione
   - `{{YYYYMMDD}}` → data odierna in formato `20250508`
   - `{{MESE_PRINCIPALE}}` → mese più recente nel CSV, es. `2025-06`
2. Crea la cartella `output/` se non esiste
3. Salva con `encoding='utf-8'`
4. Verifica le `quality-rules` (se l'artifact è HTML: è self-contained? Mancano file esterni?)
5. Rispondi all'utente:
   ```
   ✅ Artifact generato: output/<nome-file>
   📊 Righe elaborate: <N>
   🌐 Per visualizzare: apri il file nel browser (doppio click)
   ```

## Gestione errori

| Situazione | Risposta |
|-----------|---------|
| CSV non trovato | `ERRORE: file non trovato: <path>` |
| Colonna obbligatoria mancante | `ERRORE: colonna '<nome>' richiesta ma non trovata` |
| CSV vuoto (0 righe) | `ERRORE: il file CSV non contiene dati` |
| Placeholder residui | `ERRORE interno: placeholder non sostituiti: {{...}}` |
| Cartella output/ non scrivibile | `ERRORE: impossibile scrivere in output/` |

## Riferimento ai tipi

Per le regole specifiche di ogni tipo di artifact, vedi:
`skills/artifact-generator/references/artifact-types.md`
