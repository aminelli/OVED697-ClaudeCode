---
description: "Testa il progetto analisi-vendite: validazione CSV, analisi completa e verifica del report generato. Usa quando vuoi eseguire un ciclo di test end-to-end sul progetto."
name: "Test Analisi Vendite"
argument-hint: "Percorso del file CSV da testare (default: data/vendite_esempio.csv)"
agent: "agent"
tools: ["read_file", "run_in_terminal"]
---

# Test end-to-end — Progetto analisi-vendite

Esegui un ciclo di test completo sul progetto `corso-test-01`.
Il file CSV da testare è: **$input** (se non specificato usa `data/vendite_esempio.csv`).

---

## Step 1 — Verifica struttura del progetto

Prima di eseguire qualsiasi test, controlla che tutti i file critici esistano:

- `data/vendite_esempio.csv`
- `skills/analisi-vendite/SKILL.md`
- `skills/analisi-vendite/scripts/analizza_vendite.py`
- `skills/analisi-vendite/references/data-schema.md`
- `skills/analisi-vendite/references/logica-analisi.md`
- `skills/analisi-vendite/references/soglie-kpi.md`
- `skills/analisi-vendite/assets/report-template.md`
- `.claude/settings.json`
- `.claude/commands/analizza.md`

Se uno di questi file è assente, **fermati** e segnala il file mancante.
Non procedere finché tutti i file non sono presenti.

---

## Step 2 — Test Fase 1: validazione sola

Esegui la validazione del CSV **senza** generare report:

```bash
python skills/analisi-vendite/scripts/analizza_vendite.py \
  --input data/vendite_esempio.csv \
  --validate-only
```

**Criteri di successo:**
- Exit code `0`
- Output contiene `✓` con numero di righe valide
- Nessun errore bloccante

**Se il test fallisce:**
- Riporta gli errori riga per riga
- Distingui errori bloccanti da warning
- **Non proseguire** agli step successivi se ci sono errori bloccanti > 5%

---

## Step 3 — Test Fase 2–4: analisi completa

Esegui l'analisi completa con output su file:

```bash
python skills/analisi-vendite/scripts/analizza_vendite.py \
  --input data/vendite_esempio.csv \
  --output output/report_test.md
```

**Criteri di successo:**
- Exit code `0`
- Il file `output/report_test.md` esiste ed è non vuoto
- Output console mostra `[1/4]`, `[2/4]`, `[3/4]`, `[4/4]`

---

## Step 4 — Verifica del report generato

Leggi il file `output/report_test.md` appena prodotto e verifica:

1. **Sezione Sommario Esecutivo** presente
2. Almeno un KPI classificato con semaforo (Verde 🟢 / Giallo 🟡 / Rosso 🔴)
3. Sezione "Top prodotti" presente con almeno 1 voce
4. Sezione "Top clienti" presente con almeno 1 voce
5. Nessun valore `None` o `N/A` per i KPI primari (fatturato, ticket medio)

---

## Step 5 — Test edge case: file inesistente

```bash
python skills/analisi-vendite/scripts/analizza_vendite.py \
  --input data/non_esiste.csv \
  --validate-only
```

**Criteri di successo:**
- Exit code `1`
- Messaggio di errore sul file non trovato
- Nessun file creato in `output/`

---

## Step 6 — Report finale dei test

Al termine, produci un riepilogo in questo formato:

```
## Risultati Test — analisi-vendite

| Step | Descrizione | Risultato |
|------|-------------|-----------|
| 1 | Struttura progetto | ✅ OK / ❌ FAIL |
| 2 | Validazione sola   | ✅ OK / ❌ FAIL |
| 3 | Analisi completa   | ✅ OK / ❌ FAIL |
| 4 | Verifica report    | ✅ OK / ❌ FAIL |
| 5 | Edge case          | ✅ OK / ❌ FAIL |

**Esito complessivo:** PASS / FAIL
**File report generato:** output/report_test.md
**Note:** <eventuali anomalie rilevate>
```

Se tutti gli step sono `✅ OK`, il progetto è funzionante.
Se anche solo uno è `❌ FAIL`, indica il problema e suggerisci la correzione.
