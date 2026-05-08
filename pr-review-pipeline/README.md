# PR Review Pipeline — Esempio Claude Code

Progetto didattico che illustra come **skill**, **artifact** e **agent** collaborano
in un sistema multi-agente orchestrato da Claude Code.

**Scenario**: una pipeline di code review automatica che analizza una PR da tre
angolazioni (security, performance, style) in parallelo e produce un verdetto finale.

---

## Struttura del progetto

```
pr-review-pipeline/
├── CLAUDE.md                        ← istruzioni orchestratore (letto per primo)
├── .claude/
│   ├── settings.json                ← permessi allow/deny + env vars
│   └── commands/
│       └── review-pr.md             ← comando slash /review-pr <pr-id>
│
├── agents/                          ← definizioni sub-agent
│   ├── security-agent.md
│   ├── performance-agent.md
│   └── style-agent.md
│
├── skills/                          ← knowledge base caricata dagli agent
│   ├── security-analysis/SKILL.md
│   ├── performance-analysis/SKILL.md
│   └── style-checking/SKILL.md
│
├── artifacts/                       ← output prodotti dagli agent
│   ├── comments/                    ← review-comment (1 per agent per PR)
│   │   ├── pr42_security.md
│   │   ├── pr42_performance.md
│   │   └── pr42_style.md
│   ├── reports/                     ← review-report aggregato
│   │   └── review_pr-42.md
│   └── manifests/
│       └── artifact-registry.json   ← catalogo di tutti gli artifact
│
├── pr-diffs/                        ← input: diff delle PR da revisionare
│   └── pr-42.diff
│
└── scripts/                         ← script Python dell'orchestratore
    ├── check_comments.py            ← verifica completamento sub-agent
    └── aggregate_reviews.py         ← aggrega commenti in report finale
```

---

## Come funziona

### 1. Lancia una review

```
/review-pr pr-42
```

Claude (orchestratore) legge `CLAUDE.md` e il comando slash `review-pr.md`,
poi avvia **tre Task in parallelo** — uno per ogni sub-agent.

### 2. I sub-agent lavorano in parallelo

Ogni agent:
1. Legge `pr-diffs/pr-42.diff`
2. Carica la propria skill (`skills/<name>/SKILL.md`)
3. Applica i pattern di detection della skill al diff
4. Scrive il proprio `artifacts/comments/pr42_<agent>.md` con frontmatter YAML
5. Aggiorna `artifact-registry.json`

### 3. Aggregazione

Dopo che i Task sono completati, l'orchestratore:
1. Esegue `scripts/check_comments.py --pr-id pr-42` per verificare lo stato
2. Esegue `scripts/aggregate_reviews.py --pr-id pr-42` per costruire il report
3. Mostra il verdetto: `REQUEST_CHANGES` / `COMMENT` / `APPROVE`

---

## Principi dimostrati

| # | Principio                         | Dove vederlo                                    |
|---|-----------------------------------|-------------------------------------------------|
| 1 | **Definizione di un agent**       | `agents/*.md` — frontmatter YAML + workflow     |
| 2 | **Skill caricata da un agent**    | Ogni agent carica la propria `skills/*/SKILL.md`|
| 3 | **Comunicazione via artifact**    | Gli agent non si parlano; scrivono file su disco|
| 4 | **Invocazione parallela**         | 3 Task lanciati contemporaneamente in `review-pr.md` |
| 5 | **Lifecycle dell'artifact**       | `draft` → `ready` → incluso nel `complete` report |
| 6 | **Registry pattern**              | `artifact-registry.json` come catalogo centrale |
| 7 | **Orchestrator pattern**          | `CLAUDE.md` coordina tutto senza fare review    |

---

## Eseguire gli script manualmente

```bash
# Verifica che i 3 commenti siano pronti
python scripts/check_comments.py --pr-id pr-42

# Aggrega i commenti in un report finale
python scripts/aggregate_reviews.py --pr-id pr-42
```

---

## Logica di verdetto

| Condizione                             | Verdetto          |
|----------------------------------------|-------------------|
| Almeno 1 `critical` o 1 `high`         | `REQUEST_CHANGES` |
| Solo `medium` e/o `low`, nessun `critical`/`high` | `COMMENT` |
| Solo `info` o nessun problema          | `APPROVE`         |

---

## Esempio di output

La PR `pr-42` contiene deliberatamente:
- **SQL injection** (security, critical)
- **Hard-coded credentials** (security, high)
- **Command injection** (security, high)
- **N+1 query** × 2 (performance, high × 2)
- **Indici mancanti** (performance, medium)
- **Duplicazione di codice** (style, medium)
- **Funzione troppo lunga** (style, medium)
- **Type hints mancanti, TODO senza ticket, import inutilizzato** (style, low × 3)

Verdetto finale: **❌ REQUEST_CHANGES** (1 critical + 4 high trovati).
