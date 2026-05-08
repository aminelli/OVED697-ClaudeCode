# Corso-Test-03 — Agent con Tool Use e State Management

## Obiettivo didattico

Questo progetto mostra come costruire **da zero** un sistema multi-agent con:

- **Tool Use** — definire strumenti che gli agenti invocano con schema JSON
- **State Management** — stato condiviso e persistente tra agenti diversi
- **Pipeline orchestrata** — flusso sequenziale con dipendenze tra step
- **Frontend Angular** — interfaccia web per la revisione operatore

## Scenario: Customer Service Triage

Un agente riceve richieste di supporto clienti, le classifica per
**priorità** (critical / high / medium / low) e **tipologia**
(billing / technical / account / general), e **abbozza una risposta**.
L'operatore umano rivede solo la bozza finale e la approva.

```
Ticket grezzo ──► [Classifier Agent] ──► Classificazione
                                              │
                                              ▼
                                     [Responder Agent] ──► Bozza risposta
                                                                │
                                                                ▼
                                                     [Operatore] ──► Approva / Modifica
```

## Cosa rende questo progetto educativo rispetto agli altri

| Feature | corso-test-01 | corso-test-02 | **corso-test-03** |
|---------|--------------|--------------|-------------------|
| Tool Use esplicito con schema JSON | ✗ | ✗ | **✓** |
| State management strutturato | ✗ | ✗ | **✓** |
| Idempotenza pipeline | ✗ | ✗ | **✓** |
| Frontend Angular | ✗ | ✗ | **✓** |
| Panel stato pipeline in tempo reale | ✗ | ✗ | **✓** |

## Stack tecnologico

| Componente | Tecnologia | Porta |
|------------|-----------|-------|
| Frontend | Angular 17 + standalone components | 4200 |
| Backend API | Express.js (Node.js) | 3001 |
| Stato | JSON file su disco (`state/pipeline-state.json`) | — |
| Artifact | Markdown + YAML frontmatter su disco | — |

## Avvio rapido

```bash
# Backend
cd backend && npm install && npm start

# Frontend (in un altro terminale)
cd frontend && npm install && ng serve
```

Vai su http://localhost:4200 e http://localhost:3001/api/health

Vedi `GUIDA.md` per la sequenza completa.

## Struttura concettuale dei Tool

I tool sono definiti in `tools/` come file JSON con lo schema input/output.
In un'integrazione reale con Claude API si passano direttamente nell'array
`tools` della request. Qui servono come **documentazione eseguibile** che
Claude Code legge per capire come interagire con il filesystem del progetto.

## Struttura concettuale dello Stato

```
state/pipeline-state.json
    └── tickets
        └── ticket-001
            ├── status: "draft-ready"
            ├── classification_artifact: "artifacts/classifications/..."
            ├── draft_artifact: "artifacts/drafts/..."
            ├── steps_completed: ["classify", "draft"]
            └── errors: []
```

Lo stato viene letto all'inizio di ogni command e scritto dopo ogni step.
Questo rende la pipeline **riprendibile**: se Claude si interrompe a metà,
al riavvio riparte dall'ultimo step completato.
