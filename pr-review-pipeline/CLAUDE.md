# PR Review Pipeline — Claude Code Project

## Obiettivo

Questo progetto dimostra come **orchestrare più agent specializzati** per
eseguire una code review automatica di una Pull Request.

Dato un diff di PR in input, il sistema:
1. Delega l'analisi a tre **sub-agent specializzati** (sicurezza, performance, stile)
2. Ogni sub-agent produce artifact `review-comment` indipendenti
3. L'orchestratore aggrega i risultati in un artifact `review-report` finale

---

## Architettura multi-agent

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATORE (questo file)               │
│                                                              │
│  Riceve: pr-diff/*.diff                                      │
│  Produce: artifacts/reports/review_<pr-id>.md               │
│                                                              │
│    ┌──────────────────────────────────────────────────┐     │
│    │  Task: security-agent                             │     │
│    │  Skill: security-analysis                        │     │
│    │  Produce: artifacts/comments/<pr-id>_security.md │     │
│    └──────────────────────────────────────────────────┘     │
│    ┌──────────────────────────────────────────────────┐     │
│    │  Task: performance-agent                          │     │
│    │  Skill: performance-analysis                     │     │
│    │  Produce: artifacts/comments/<pr-id>_perf.md     │     │
│    └──────────────────────────────────────────────────┘     │
│    ┌──────────────────────────────────────────────────┐     │
│    │  Task: style-agent                                │     │
│    │  Skill: style-checking                           │     │
│    │  Produce: artifacts/comments/<pr-id>_style.md    │     │
│    └──────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Principio fondamentale: gli agent comunicano tramite artifact

> Gli agent **non comunicano direttamente** tra loro.
> Il loro unico canale di comunicazione sono gli artifact che scrivono su disco.
> L'orchestratore li legge dopo che ogni sub-agent ha terminato.

---

## Struttura del progetto

```
pr-review-pipeline/
├── CLAUDE.md                        ← istruzioni dell'orchestratore (questo file)
├── .claude/
│   ├── settings.json
│   └── commands/
│       └── review-pr.md             ← /review-pr <pr-id>
├── agents/
│   ├── security-agent.md            ← definizione sub-agent sicurezza
│   ├── performance-agent.md         ← definizione sub-agent performance
│   └── style-agent.md               ← definizione sub-agent stile
├── skills/
│   ├── security-analysis/           ← skill del security-agent
│   ├── performance-analysis/        ← skill del performance-agent
│   └── style-checking/              ← skill dello style-agent
├── pr-diffs/
│   └── pr-42.diff                   ← PR diff di esempio (input)
└── artifacts/
    ├── manifests/
    │   └── artifact-registry.json   ← registro centrale di tutti gli artifact
    ├── comments/                    ← artifact prodotti dai sub-agent
    └── reports/                     ← artifact prodotti dall'orchestratore
```

---

## Catalogo degli Artifact

### 1. `review-comment` — Commenti di un singolo agent

| Proprietà   | Valore                                          |
|-------------|-------------------------------------------------|
| Posizione   | `artifacts/comments/`                           |
| Naming      | `<pr-id>_<agent>.md` (es. `pr42_security.md`)   |
| Prodotto da | Sub-agent (security / performance / style)      |
| Stati       | `draft` → `ready`                               |

**Header frontmatter obbligatori:**
```yaml
---
artifact:type: review-comment
artifact:id: pr42_security
artifact:pr-id: pr-42
artifact:agent: security-agent
artifact:status: ready
artifact:severity-counts:
  critical: 0
  high: 2
  medium: 1
  low: 3
  info: 5
artifact:created-by: claude/security-agent
artifact:created-at: 2026-05-08T14:00:00Z
---
```

---

### 2. `review-report` — Report aggregato finale

| Proprietà   | Valore                                      |
|-------------|---------------------------------------------|
| Posizione   | `artifacts/reports/`                        |
| Naming      | `review_<pr-id>.md`                         |
| Prodotto da | Orchestratore (questo agent)                |
| Dipende da  | I tre artifact `review-comment` corrispondenti |
| Stati       | `pending` → `complete`                      |

```yaml
---
artifact:type: review-report
artifact:id: review_pr42
artifact:pr-id: pr-42
artifact:status: complete
artifact:verdict: REQUEST_CHANGES | APPROVE | COMMENT
artifact:sources:
  - pr42_security
  - pr42_performance
  - pr42_style
artifact:created-by: claude/orchestrator
artifact:created-at: 2026-05-08T14:05:00Z
---
```

---

### 3. `artifact-registry` — Manifesto centrale

Ogni artifact prodotto (commenti + report) viene registrato nel registry
**prima** di essere considerato completato.

---

## Workflow dell'orchestratore

Quando ricevi la richiesta `/review-pr <pr-id>`:

### Fase 1 — Preparazione

```python
# Verifica che il diff esista
pr_diff = f"pr-diffs/{pr_id}.diff"
# Leggi il diff per avere contesto
# Genera un timestamp per questa sessione di review
```

### Fase 2 — Delegazione ai sub-agent (in parallelo)

Invoca i tre sub-agent usando il tool `Task`. Passagli sempre:
- Il percorso del file diff: `pr-diffs/<pr-id>.diff`
- Il PR ID: usato per il naming dell'artifact output
- Il percorso dove scrivere il loro artifact

```
Task(security-agent):
  "Esegui una security review del diff in pr-diffs/<pr-id>.diff.
   Scrivi i tuoi commenti in artifacts/comments/<pr-id>_security.md
   seguendo le istruzioni in agents/security-agent.md"

Task(performance-agent):
  "Esegui una performance review del diff in pr-diffs/<pr-id>.diff.
   Scrivi i tuoi commenti in artifacts/comments/<pr-id>_performance.md
   seguendo le istruzioni in agents/performance-agent.md"

Task(style-agent):
  "Esegui una style review del diff in pr-diffs/<pr-id>.diff.
   Scrivi i tuoi commenti in artifacts/comments/<pr-id>_style.md
   seguendo le istruzioni in agents/style-agent.md"
```

> **I tre Task possono essere lanciati in parallelo**: non hanno dipendenze
> tra loro, leggono tutti lo stesso diff in sola lettura.

### Fase 3 — Attesa e verifica

Dopo che i Task sono completati, verifica che i tre artifact esistano
e abbiano `artifact:status: ready`:

```python
python scripts/check_comments.py --pr-id <pr-id>
```

Se uno o più artifact mancano o sono in stato `draft`, riprova il Task
corrispondente (massimo 1 retry).

### Fase 4 — Aggregazione

Leggi i tre artifact `review-comment` e produci il `review-report`:

```python
python scripts/aggregate_reviews.py --pr-id <pr-id>
```

### Fase 5 — Registrazione nel registry

Registra tutti e quattro gli artifact (3 commenti + 1 report) nel registry.

### Fase 6 — Output finale

Mostra all'utente:
- Il verdetto (`APPROVE` / `REQUEST_CHANGES` / `COMMENT`)
- Il riepilogo dei problemi trovati per categoria
- Il link al report completo

---

## Regole operative dell'orchestratore

1. **Non fare review dirette**: l'orchestratore non analizza il codice —
   delega sempre ai sub-agent specializzati.
2. **Leggi gli artifact, non i processi**: la comunicazione avviene tramite
   file, non tramite stato in memoria.
3. **Verdetto deterministico**: il verdetto finale segue questa logica:
   - Almeno 1 `critical` → `REQUEST_CHANGES`
   - Almeno 1 `high` → `REQUEST_CHANGES`
   - Solo `medium`/`low` → `COMMENT`
   - Solo `info` o nessun problema → `APPROVE`
4. **Registry always last**: aggiorna il registry solo quando tutti gli
   artifact sono in stato finale (`ready` / `complete`).

---

## Convenzioni di codice

- **Python**: 3.11+, type hints, pathlib per i percorsi
- **Markdown**: ogni artifact ha il frontmatter YAML obbligatorio
- **Severity**: `critical > high > medium > low > info`
