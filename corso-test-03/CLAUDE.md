# Corso-Test-03 — Agent con Tool Use e State Management

Sei l'**orchestratore** del sistema di triage per il customer service.
Coordini due sub-agent specializzati e gestisci lo **stato della pipeline**
tramite strumenti (tool use) espliciti.

Questo progetto è pensato come **laboratorio didattico** per imparare a:
- costruire agenti con **tool use** da zero
- gestire lo **stato condiviso** tra più agenti
- orchestrare una pipeline multi-step con dipendenze

---

## Architettura del sistema

```
                     ┌──────────────────────────────────┐
                     │         ORCHESTRATORE            │
                     │  (questo CLAUDE.md)              │
                     │                                  │
                     │  Tool: load-state                │
                     │  Tool: save-state                │
                     │  Tool: update-ticket-status      │
                     └──────┬──────────────┬────────────┘
                            │              │
               Step 1       │              │  Step 2
                            ▼              ▼
              ┌─────────────────┐   ┌──────────────────┐
              │  classifier-    │   │  responder-      │
              │  agent          │   │  agent           │
              │                 │   │                  │
              │  Tool: read-    │   │  Tool: read-     │
              │    ticket       │   │    classification│
              │  Tool: save-    │   │  Tool: save-     │
              │    classification│  │    draft         │
              └────────┬────────┘   └────────┬─────────┘
                       │                     │
                       ▼                     ▼
            artifacts/classifications/  artifacts/drafts/
            <id>_classification.md      <id>_draft.md
                                             │
                                             ▼
                                  ┌────────────────────┐
                                  │  ANGULAR WEB APP   │
                                  │  http://localhost  │
                                  │  :4200             │
                                  │                    │
                                  │  Operatore rivede, │
                                  │  edita, approva    │
                                  └────────────────────┘
```

> **Principio chiave — Tool Use**: ogni azione concreta (leggere, scrivere,
> aggiornare stato) è modellata come un **tool** con schema JSON esplicito.
> L'agente non "fa" cose direttamente: *chiama tool* e *interpreta risposte*.

> **Principio chiave — State**: lo stato della pipeline vive in
> `state/pipeline-state.json`. Ogni agente lo legge prima di agire
> e lo aggiorna dopo. Questo rende ogni step **idempotente** e **riprendibile**.

---

## Concetto di Tool Use

Un "tool" in Claude è una funzione che l'agente può invocare.
La definizione segue uno schema JSON standard:

```json
{
  "name": "nome-del-tool",
  "description": "Cosa fa questo tool e quando usarlo",
  "input_schema": {
    "type": "object",
    "properties": {
      "parametro": {
        "type": "string",
        "description": "Descrizione del parametro"
      }
    },
    "required": ["parametro"]
  }
}
```

I tool di questo progetto sono definiti in `tools/`.
Ogni file JSON descrive un tool con schema, scopo e comportamento atteso.

---

## State Management: il contratto di stato

Lo stato della pipeline è un documento JSON strutturato:

```json
{
  "pipeline_version": "1.0",
  "last_updated": "<ISO timestamp>",
  "tickets": {
    "<ticket-id>": {
      "status": "unprocessed | classified | draft-ready | approved | rejected",
      "classification_artifact": "<path | null>",
      "draft_artifact": "<path | null>",
      "steps_completed": [],
      "current_step": null,
      "errors": []
    }
  },
  "global": {
    "total_processed": 0,
    "pending_review": 0
  }
}
```

**Regole di stato**:
1. Ogni agente legge lo stato prima di iniziare (`load-state`)
2. Se il ticket è già nello stato desiderato → skip (idempotenza)
3. Dopo ogni step, l'agente aggiorna lo stato (`save-state`)
4. In caso di errore, l'agente scrive in `errors[]` e non blocca la pipeline

---

## Struttura del progetto

```
corso-test-03/
├── CLAUDE.md                          ← questo file (orchestratore)
├── README.md                          ← descrizione del progetto
├── GUIDA.md                           ← guida comandi (avvio, deploy, ...)
├── .claude/
│   ├── settings.json
│   └── commands/
│       ├── dev.md                     ← /dev: avvia Angular + backend
│       ├── process-ticket.md          ← /process-ticket <id>
│       ├── process-all.md             ← /process-all
│       └── show-state.md              ← /show-state
├── tools/                             ← definizioni tool use (schema JSON)
│   ├── README.md
│   ├── read-ticket.json
│   ├── save-classification.json
│   ├── read-classification.json
│   ├── save-draft.json
│   ├── load-state.json
│   ├── save-state.json
│   └── update-ticket-status.json
├── agents/
│   ├── classifier-agent.md
│   └── responder-agent.md
├── skills/
│   ├── ticket-classification/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── category-taxonomy.md
│   └── response-drafting/
│       ├── SKILL.md
│       └── templates/
│           ├── billing.md
│           ├── technical.md
│           ├── account.md
│           └── general.md
├── state/
│   ├── README.md
│   └── pipeline-state.json
├── tickets/
│   ├── ticket-001.txt
│   ├── ticket-002.txt
│   ├── ticket-003.txt
│   └── ticket-004.txt
├── artifacts/
│   ├── classifications/
│   ├── drafts/
│   └── manifests/
│       └── artifact-registry.json
├── backend/
│   ├── package.json
│   ├── server.js
│   └── routes/
│       ├── tickets.js
│       ├── artifacts.js
│       └── state.js
└── frontend/                          ← Angular 17+
    ├── package.json
    ├── angular.json
    ├── tsconfig.json
    ├── tsconfig.app.json
    └── src/
        ├── main.ts
        ├── index.html
        ├── styles.scss
        └── app/
            ├── app.component.ts
            ├── app.component.html
            ├── app.component.scss
            ├── app.routes.ts
            ├── app.config.ts
            ├── models/
            │   ├── ticket.model.ts
            │   └── pipeline-state.model.ts
            ├── services/
            │   ├── tickets.service.ts
            │   └── state.service.ts
            └── components/
                ├── dashboard/
                ├── ticket-detail/
                ├── draft-editor/
                └── pipeline-state-panel/
```

---

## Comandi Claude Code disponibili

| Comando | Descrizione |
|---------|-------------|
| `/process-ticket <id>` | Esegue classifier → responder per un ticket |
| `/process-all` | Processa tutti i ticket non ancora elaborati |
| `/show-state` | Mostra lo stato corrente della pipeline |
| `/dev` | Avvia backend Node.js + frontend Angular |

---

## Come procedere (flusso orchestratore)

### `/process-ticket <ticket-id>`

1. **Load state** — chiama tool `load-state`
2. **Controlla idempotenza** — se status ≠ `unprocessed`, logga e termina
3. **Aggiorna status** → `processing` via `update-ticket-status`
4. **Delega a classifier-agent** — leggi `agents/classifier-agent.md`
   - Il classifier usa tool `read-ticket` + `save-classification`
   - Al termine aggiorna status → `classified`
5. **Delega a responder-agent** — leggi `agents/responder-agent.md`
   - Il responder usa tool `read-classification` + `save-draft`
   - Al termine aggiorna status → `draft-ready`
6. **Report finale** — mostra all'operatore un riepilogo

### `/process-all`

Ripeti `/process-ticket` per ogni ticket con status `unprocessed`.
Processa in sequenza, non in parallelo (per evitare race condition sullo stato).

### `/show-state`

1. Chiama tool `load-state`
2. Formatta e mostra la tabella riassuntiva di tutti i ticket
