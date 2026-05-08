# corso-test-02 — Esempio Didattico: Artifact Modeling in Claude Code

## Scopo del progetto

Questo progetto è un esempio **didattico** su come modellare un *artifact*
in Claude Code nel modo corretto, seguendo le best practice ufficiali.

**Scenario**: partendo da un CSV con dati di vendita per punto vendita,
Claude genera una dashboard interattiva HTML con filtri e grafici,
visualizzabile nel browser senza installare nulla.
Stesso pattern per documenti Word-like, presentazioni e componenti UI.

---

## Skill vs Artifact: la distinzione fondamentale

| Concetto | Cosa definisce | Risponde a |
|----------|----------------|------------|
| **Skill** (`corso-test-01`) | Come Claude deve *ragionare* e *procedere* | "Qual è il processo?" |
| **Artifact** (questo progetto) | Cosa Claude deve *produrre* | "Com'è fatto l'output?" |

Una **skill** guida il processo. Un **artifact** specifica il contratto di output.
Spesso si usano insieme: la skill guida Claude nel *come* generare l'artifact.

---

## Cos'è un Artifact in Claude Code?

Un **artifact** è un file di output auto-contenuto che Claude genera.
Ogni tipo di artifact ha una **definizione** (`artifact.md`) che specifica:

1. **Tipo** — che tecnologia usare (HTML, Markdown, React…)
2. **Contratto di input** — quali dati Claude deve leggere prima
3. **Contratto di output** — dove salvare, naming, formato
4. **Template** — la struttura base da compilare con i dati
5. **Regole di qualità** — vincoli che l'artifact deve rispettare
6. **Istruzioni di preview** — come verificare il risultato

---

## Anatomia di un artifact ben modellato

```
artifacts/nome-artifact/
├── artifact.md      ← ★ definizione: frontmatter YAML + regole + preview
└── template.*       ←   struttura base con {{PLACEHOLDER}}
```

### Il frontmatter YAML di artifact.md

```yaml
---
artifact:type: html-interactive
artifact:title: Dashboard Vendite per Punto Vendita
artifact:description: >
  Dashboard HTML con filtri per regione/mese/categoria
  e grafici Chart.js. Nessuna dipendenza locale.
  USA QUESTO ARTIFACT PER: visualizzare dati tabellari in modo
  interattivo nel browser, senza server né build step.
  NON USARE PER: applicazioni multi-pagina, auth utente, dati in tempo reale.
artifact:input:
  primary: csv_path          # il CSV con i dati grezzi
  required-columns:          # schema minimo atteso
    - punto_vendita
    - regione
    - mese
    - fatturato
artifact:output:
  path: output/dashboard_{{NOME_FILE}}_{{DATA}}.html
  format: html
  self-contained: true       # tutto inline: CSS, JS, dati
artifact:dependencies:
  cdn:
    - https://cdn.jsdelivr.net/npm/chart.js@4
artifact:quality-rules:
  - "Nessun file esterno: CSS e JS devono essere inline o CDN"
  - "I dati CSV vanno convertiti in JSON e inseriti nel <script>"
  - "Il file deve funzionare aprendo direttamente in qualsiasi browser"
  - "Filtri: almeno regione, mese, e reset"
  - "Grafici: almeno 1 bar chart e 1 line chart"
artifact:version: 1.0
---
```

---

## Catalog degli artifact inclusi

| Artifact | Tipo | Scenario |
|----------|------|----------|
| `dashboard-vendite` | `html-interactive` | Dashboard con filtri e grafici per punto vendita |
| `report-mensile` | `markdown-doc` | Report mensile con KPI e tabelle (stile Word) |
| `presentazione-kpi` | `html-presentation` | Slide deck HTML visualizzabile nel browser |
| `componente-card` | `html-component` | Card UI riutilizzabile (standalone HTML) |

---

## Come invocare la generazione

### Comando slash (modo consigliato)

```
/genera-dashboard data/vendite_punti_vendita.csv
/genera-documento report-mensile data/vendite_punti_vendita.csv
/genera-presentazione data/vendite_punti_vendita.csv
```

### Richiesta in linguaggio naturale

Claude attiva la skill `artifact-generator` quando sente:
- "genera la dashboard dal CSV"
- "crea il report mensile"
- "fai una presentazione con i KPI"
- "genera il componente card"

---

## Struttura del progetto

```
corso-test-02/
├── CLAUDE.md                              ← questo file
├── README.md
├── .claude/
│   ├── settings.json
│   └── commands/
│       ├── genera-dashboard.md            ← /genera-dashboard <file>
│       ├── genera-documento.md            ← /genera-documento <tipo> <file>
│       └── genera-presentazione.md        ← /genera-presentazione <file>
│
├── artifacts/                             ← ★ FOCUS DIDATTICO
│   ├── README.md                          ←   guida al sistema artifact
│   ├── dashboard-vendite/
│   │   ├── artifact.md                    ←   spec (frontmatter + regole)
│   │   └── template.html                  ←   template con {{PLACEHOLDER}}
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
│       ├── SKILL.md                       ←   procedura di generazione
│       └── references/
│           └── artifact-types.md          ←   catalogo pattern per tipo
│
├── data/
│   └── vendite_punti_vendita.csv          ← dataset esempio (120 righe)
│
└── output/                                ← artifact generati (auto-creata)
```

---

## Regole operative

- I file in `artifacts/` e `skills/` non vanno mai modificati durante la generazione
- L'output va sempre in `output/` con il naming convention definito nell'artifact
- Ogni artifact deve essere **self-contained**: apribile senza server locale
- Se il CSV non ha le colonne richieste, fermarsi e mostrare le colonne mancanti
