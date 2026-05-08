# corso-test-01 — Skill Modeling in Claude Code

Esempio didattico su come modellare una **skill** in Claude Code,
usando come scenario l'analisi di dati di vendita con logica predefinita.

---

## Cos'è questo progetto

Un progetto Claude Code costruito per insegnare **come si modella una skill**:
una skill non è codice, è documentazione strutturata che guida Claude nel
seguire una procedura specifica per una categoria di task.

Il progetto contiene **una sola skill** (`analisi-vendite`) ma la sviluppa
in profondità, mostrando tutti i layer di una skill ben costruita.

---

## Struttura del progetto

```
corso-test-01/
├── CLAUDE.md                              ← orchestratore + guida didattica skill modeling
├── README.md
├── .claude/
│   ├── settings.json                      ← permessi (deny writes su skills/)
│   └── commands/
│       └── analizza.md                    ← /analizza <file>
│
├── skills/
│   └── analisi-vendite/                   ← ★ LA SKILL (focus del progetto)
│       │
│       ├── SKILL.md                       ← punto di ingresso: frontmatter + workflow
│       │                                     • YAML con name, description USE/NON USARE
│       │                                     • lista trigger
│       │                                     • workflow ASCII a 4 fasi
│       │                                     • istruzioni passo-passo
│       │                                     • output contract
│       │                                     • tabella gestione errori
│       │                                     • formato risposta atteso
│       │
│       ├── references/                    ← conoscenza statica (regole, schemi)
│       │   ├── logica-analisi.md          ← la logica a 4 fasi con regole precise
│       │   ├── soglie-kpi.md              ← soglie Verde/Giallo/Rosso per ogni KPI
│       │   └── data-schema.md             ← schema CSV con colonne e vincoli
│       │
│       ├── assets/                        ← template di output
│       │   └── report-template.md         ← struttura esatta del report finale
│       │
│       └── scripts/                       ← strumento eseguibile
│           └── analizza_vendite.py        ← implementa la logica a 4 fasi
│
├── data/
│   └── vendite_esempio.csv                ← 30 ordini su 4 mesi (Gen–Apr 2025)
│
└── output/                                ← report generati (auto-creata)
```

---

## I layer di una skill ben modellata

| Layer | File | Scopo |
|-------|------|-------|
| **Frontmatter YAML** | `SKILL.md` | Routing: quando Claude usa questa skill |
| **Workflow procedurale** | `SKILL.md` | Come: passi numerati da seguire |
| **Logica e regole** | `references/logica-analisi.md` | Cosa fare in ciascuna fase |
| **Soglie e parametri** | `references/soglie-kpi.md` | Come classificare i risultati |
| **Schema dati** | `references/data-schema.md` | Quali dati accettare |
| **Template output** | `assets/report-template.md` | Come formattare il risultato |
| **Script** | `scripts/analizza_vendite.py` | Come calcolare (delegato a Python) |

---

## Avvio rapido

### Prerequisiti

```bash
python --version   # >= 3.10
```

Nessuna dipendenza esterna — lo script usa solo la libreria standard Python.

### Analizzare il dataset di esempio

```bash
python skills/analisi-vendite/scripts/analizza_vendite.py \
  --input data/vendite_esempio.csv \
  --output output/report_esempio.md
```

### Oppure, da Claude Code

```
/analizza data/vendite_esempio.csv
```

### Solo validazione

```bash
python skills/analisi-vendite/scripts/analizza_vendite.py \
  --input data/vendite_esempio.csv \
  --validate-only
```

---

## Cosa dimostra il progetto

### 1. Il frontmatter YAML come meccanismo di routing

```yaml
---
name: analisi-vendite
description: >
  Analizza file CSV di dati di vendita …
  USA QUESTA SKILL PER: analizzare file CSV, calcolare KPI …
  NON USARE PER: creare grafici, analizzare dati non di vendita …
triggers:
  - "analizza le vendite"
  - "calcola il fatturato"
---
```

Il campo `description` è la chiave: Claude lo confronta semanticamente
con la richiesta dell'utente per decidere se attivare la skill.

### 2. La separazione tra procedura e conoscenza

- `SKILL.md` dice **come fare** (passi 1-5)
- `references/logica-analisi.md` dice **quali regole applicare**
- `references/soglie-kpi.md` dice **come classificare**

Questa separazione permette di aggiornare le soglie senza toccare la procedura.

### 3. L'output contract

`SKILL.md` specifica esattamente cosa produrre, dove salvarlo e con quale nome.
Claude non inventa percorsi: segue il contratto.

### 4. La gestione degli errori dichiarativa

La tabella errori in `SKILL.md` è un contratto comportamentale:
Claude sa cosa fare in ogni caso anomalo prima ancora di incontrarlo.

---

## Dataset di esempio

Il file `data/vendite_esempio.csv` contiene 30 ordini su 4 mesi (Gen–Apr 2025):
- 6 prodotti (`PROD-SW-01`, `PROD-HW-05`, `PROD-SRV-02`, ...)
- 6 clienti (`CUST-ALPHA`, `CUST-BETA`, `CUST-GAMMA`, ...)
- 4 categorie (Software, Hardware, Servizi)
- 5 regioni (Nord, Centro, Sud, Est, Ovest)
- Tutti i campi opzionali presenti (costo, sconto, cliente, categoria, regione)
