# corso-test-01 — Esempio Didattico: Skill Modeling in Claude Code

## Scopo del progetto

Questo progetto è un esempio **didattico** su come modellare una *skill*
in Claude Code nel modo corretto, seguendo le best practice ufficiali.

**Scenario**: analisi di dati di vendita seguendo una logica predefinita a 4 fasi.

---

## Cos'è una Skill in Claude Code?

Una **skill** è un pacchetto di conoscenza specializzata che insegni a Claude
come affrontare una categoria specifica di task.

Non è codice eseguibile: è **documentazione strutturata** che Claude legge
per sapere:

1. **Quando attivarsi** — descrizione + trigger nel frontmatter YAML
2. **Come procedere** — istruzioni passo-passo nel corpo del `SKILL.md`
3. **Quali regole applicare** — file di riferimento (`references/`)
4. **Cosa produrre** — output contract esplicito

---

## Anatomia di una skill ben modellata

```
skills/nome-skill/
├── SKILL.md                ← ★ punto di ingresso obbligatorio
│                              (frontmatter YAML + workflow procedurale)
├── references/             ← regole, schemi, soglie (conoscenza statica)
│   ├── logica-analisi.md   ←   "come ragionare"
│   ├── soglie-kpi.md       ←   "come classificare"
│   └── data-schema.md      ←   "che dati accettare"
├── assets/                 ← template e pattern di output
│   └── report-template.md  ←   "come formattare il risultato"
└── scripts/                ← strumenti eseguibili
    └── analizza_vendite.py ←   "cosa eseguire per il calcolo"
```

### Separazione delle responsabilità

| Cartella | Contiene | Domanda a cui risponde |
|----------|----------|----------------------|
| `SKILL.md` | Procedura, workflow | **Come** fare il task? |
| `references/` | Regole, schemi, soglie | **Quali** regole applicare? |
| `assets/` | Template, esempi | **Come** deve apparire l'output? |
| `scripts/` | Script eseguibili | **Cosa** eseguire per calcolare? |

### Il frontmatter YAML è fondamentale

```yaml
---
name: analisi-vendite
description: >
  … breve descrizione …
  USA QUESTA SKILL PER: … trigger positivi …
  NON USARE PER: … esclusioni …
tools:
  - python
  - read_file
  - write_file
---
```

Il campo `description` è quello che Claude usa per **routing automatico**:
ogni volta che l'utente fa una richiesta, Claude confronta la richiesta
con le `description` di tutte le skill disponibili e sceglie quella più
pertinente. Senza una description chiara, la skill non viene attivata.

---

## Skill incluse in questo progetto

| Skill | File | Trigger principale |
|-------|------|--------------------|
| `analisi-vendite` | `skills/analisi-vendite/SKILL.md` | "analizza le vendite" |

---

## Come invocare la skill

### Comando slash (modo consigliato)

```
/analizza data/vendite_esempio.csv
```

### Richiesta in linguaggio naturale

Claude attiva automaticamente la skill quando sente frasi come:
- "analizza le vendite del file CSV"
- "calcola il fatturato e il margine"
- "dammi i KPI di vendita"
- "genera il report vendite"

---

## Struttura del progetto

```
corso-test-01/
├── CLAUDE.md                              ← questo file
├── README.md
├── .claude/
│   ├── settings.json                      ← permessi
│   └── commands/
│       └── analizza.md                    ← /analizza <file>
├── skills/
│   └── analisi-vendite/                   ← skill principale (focus didattico)
│       ├── SKILL.md                       ← ★ cuore del progetto
│       ├── references/
│       │   ├── logica-analisi.md          ← logica predefinita a 4 fasi
│       │   ├── soglie-kpi.md              ← soglie RAG per classificazione
│       │   └── data-schema.md             ← schema CSV atteso
│       ├── assets/
│       │   └── report-template.md         ← template output
│       └── scripts/
│           └── analizza_vendite.py        ← script Python
├── data/
│   └── vendite_esempio.csv                ← dataset di esempio (30 righe)
└── output/                                ← report generati qui (auto-creata)
```

---

## Regole operative

- L'output dei report va sempre in `output/` — non modificare questo default
- I file in `skills/` non vanno mai modificati durante un'analisi
- Lo script Python non va invocato direttamente: usa sempre il workflow
  definito in `SKILL.md`
- Se il file CSV non esiste, fermati e chiedi all'utente il path corretto
