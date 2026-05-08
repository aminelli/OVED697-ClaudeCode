# corso-test-02 — Artifact Modeling con Claude Code

Progetto didattico che dimostra come **modellare artifact** per Claude Code:
definire contratti precisi su cosa Claude deve produrre, in quale formato,
con quali vincoli di qualità.

> **Scenario**: partendo da un CSV con dati di vendita per punto vendita,
> Claude genera output pronti all'uso — dashboard interattive, report,
> presentazioni — senza scrivere codice dall'utente.

---

## Skill vs Artifact — la distinzione chiave

| Concetto | File principale | Risponde alla domanda... |
|----------|----------------|--------------------------|
| **Skill** | `skills/*/SKILL.md` | *Come* deve procedere Claude? (processo) |
| **Artifact** | `artifacts/*/artifact.md` | *Cosa* deve produrre Claude? (risultato) |

Analogia: la **skill** è la ricetta (passi da seguire),
l'**artifact** è la scheda prodotto (cosa deve essere il piatto finito).

---

## Struttura del progetto

```
corso-test-02/
├── CLAUDE.md                          ← istruzioni per Claude
├── .claude/
│   ├── settings.json                  ← permessi e variabili d'ambiente
│   └── commands/
│       ├── genera-dashboard.md        ← /genera-dashboard <csv>
│       ├── genera-documento.md        ← /genera-documento <tipo> <csv>
│       └── genera-presentazione.md   ← /genera-presentazione <csv>
│
├── artifacts/                         ← ★ definizioni degli artifact
│   ├── README.md                      ← guida al sistema artifact
│   ├── dashboard-vendite/
│   │   ├── artifact.md               ← contratto: tipo, input, output, regole
│   │   └── template.html             ← struttura HTML con {{PLACEHOLDER}}
│   ├── report-mensile/
│   │   ├── artifact.md
│   │   └── template.md
│   ├── presentazione-kpi/
│   │   ├── artifact.md
│   │   └── template.html
│   └── componente-card/
│       ├── artifact.md
│       └── template.html
│
├── skills/
│   └── artifact-generator/
│       ├── SKILL.md                   ← workflow in 5 fasi
│       └── references/
│           └── artifact-types.md      ← regole per ogni tipo di artifact
│
└── data/
    └── vendite_punti_vendita.csv      ← 120 righe, 5 PV × 6 mesi × 4 categorie
```

---

## Artifact disponibili

| Artifact | Tipo | Output | Comando |
|----------|------|--------|---------|
| `dashboard-vendite` | `html-interactive` | Dashboard filtri + grafici Chart.js | `/genera-dashboard` |
| `report-mensile` | `markdown-doc` | Report KPI con tabelle Markdown | `/genera-documento report-mensile` |
| `presentazione-kpi` | `html-presentation` | Slide deck navigabile (← →) | `/genera-presentazione` |
| `componente-card` | `html-component` | Card UI standalone 320px | `/genera-documento componente-card` |

---

## Quick Start

### 1. Genera la dashboard

```
/genera-dashboard data/vendite_punti_vendita.csv
```

Claude legge il CSV, costruisce il JSON embedded, popola `template.html`
e salva in `output/`. Poi aprire il file nel browser — doppio click.

### 2. Genera un report Markdown

```
/genera-documento report-mensile data/vendite_punti_vendita.csv
```

Output in `output/report_mensile_2025-06_<data>.md`.

### 3. Genera la presentazione

```
/genera-presentazione data/vendite_punti_vendita.csv
```

Slide deck navigabile con tasti freccia. Self-contained, nessuna CDN.

---

## Dataset di esempio

Il file `data/vendite_punti_vendita.csv` contiene **120 righe**:

| Dimensione | Valori |
|-----------|--------|
| Punti vendita | Milano Centro, Roma Prati, Torino Nord, Napoli Est, Bologna Sud |
| Regioni | Nord, Centro, Sud |
| Mesi | 2025-01 → 2025-06 |
| Categorie | Elettronica, Abbigliamento, Casa, Sport |
| Colonne | `punto_vendita`, `regione`, `mese`, `categoria`, `fatturato`, `unita_vendute` |

---

## Punti chiave dell'apprendimento

1. **Il frontmatter YAML di `artifact.md` è un contratto** — ogni campo è
   una garanzia per l'utente finale: tipo di output, colonne richieste,
   path di salvataggio, regole di qualità.

2. **Il template usa `{{PLACEHOLDER}}`** — Claude sostituisce ogni segnaposto
   con dati reali prima di salvare. Nessun placeholder residuo nel file finale.

3. **Self-contained = doppio click** — tutti gli HTML embeddano CSS, JS e dati
   inline. Nessun server, nessun npm install.

4. **Skill + Artifact = separazione delle responsabilità** — la skill gestisce
   il processo (come), l'artifact definisce il risultato (cosa).
   Cambiare il template non richiede di cambiare la skill.

---

## Confronto con corso-test-01

| | corso-test-01 | corso-test-02 |
|--|---|---|
| Focus | Skill modeling | Artifact modeling |
| File principale | `SKILL.md` (come procedere) | `artifact.md` (cosa produrre) |
| Output | Report Markdown (testo) | HTML interattivo, slide deck |
| Dataset | Ordini di vendita (1 PV) | Vendite multi-punto-vendita |
| Scenario | Analisi con logica predefinita | Generazione output visivi |
