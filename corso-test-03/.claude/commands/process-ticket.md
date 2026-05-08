# Command: /process-ticket <ticket-id>

Processa un singolo ticket attraverso la pipeline completa:
classificazione → generazione bozza.

## Utilizzo

```
/process-ticket ticket-001
```

## Procedura

Sei l'orchestratore. Segui ESATTAMENTE questa sequenza:

### 1. Carica stato (load-state)
Leggi `state/pipeline-state.json`.
Se il file non esiste, crea la struttura iniziale.

### 2. Verifica idempotenza
Controlla lo status del ticket `$ARGUMENTS` nello stato.

- Se status è `approved` o `draft-ready` → stampa messaggio e fermati:
  ```
  ℹ️  Ticket $ARGUMENTS è già in stato "<status>". Usa /review-draft per revisionarlo.
  ```
- Se status è `processing` → potrebbe esserci un'esecuzione precedente interrotta.
  Chiedi conferma prima di riprocessare.
- Se status è `unprocessed` o non presente → procedi.

### 3. Avvia processing
```
update-ticket-status:
  ticket_id: $ARGUMENTS
  new_status: "processing"
```

### 4. Delega a classifier-agent
Leggi `agents/classifier-agent.md` e segui la sua procedura
per il ticket `$ARGUMENTS`.

### 5. Verifica completamento classificazione
Controlla che `artifacts/classifications/$ARGUMENTS_classification.md` esista.
Se non esiste → gestisci l'errore, aggiorna stato, fermati.

### 6. Delega a responder-agent
Leggi `agents/responder-agent.md` e segui la sua procedura
per il ticket `$ARGUMENTS`.

### 7. Verifica completamento bozza
Controlla che `artifacts/drafts/$ARGUMENTS_draft.md` esista.

### 8. Report finale
Stampa il riepilogo:
```
╔══════════════════════════════════════════╗
║  Pipeline completata per $ARGUMENTS     ║
╠══════════════════════════════════════════╣
║  Classificazione                        ║
║    Categoria:  <categoria>              ║
║    Priorità:   <priorità>              ║
║    Sentiment:  <sentiment>             ║
╠══════════════════════════════════════════╣
║  Bozza                                  ║
║    Oggetto:    <subject>               ║
║    Tono:       <tone>                  ║
║    Placeholder: <n>                    ║
╠══════════════════════════════════════════╣
║  Vai su http://localhost:4200 per       ║
║  revisionare e approvare la bozza.      ║
╚══════════════════════════════════════════╝
```
