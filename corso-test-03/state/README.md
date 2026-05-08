# State — Gestione dello Stato della Pipeline

## Cos'è lo stato

Il file `pipeline-state.json` è il **registro centrale** di tutto ciò che
è successo nella pipeline. Ogni agente legge questo file prima di agire
e lo aggiorna dopo aver completato il proprio step.

## Perché è importante

Senza stato condiviso, gli agenti non possono:
- Sapere quali ticket sono già stati processati
- Riprendere da dove si erano fermati se interrotti
- Coordinarsi senza dipendere dall'output testuale dell'altro agente

## Ciclo di vita di un ticket

```
unprocessed → processing → classified → draft-ready → approved
                                                    ↘ rejected
```

## Come leggere il file JSON

```json
{
  "pipeline_version": "1.0",        ← versione schema (per compatibilità futura)
  "last_updated": "ISO timestamp",  ← ultima modifica
  "tickets": {
    "ticket-001": {
      "status": "...",              ← stato corrente
      "classification_artifact": "path|null",
      "draft_artifact": "path|null",
      "steps_completed": [],        ← "classify", "draft", "approve"
      "current_step": null,         ← step in esecuzione (null se idle)
      "errors": []                  ← errori accumulati (non bloccanti)
    }
  },
  "global": {
    "total_processed": 0,           ← quanti ticket hanno completato draft
    "pending_review": 0             ← quanti sono in draft-ready
  }
}
```
