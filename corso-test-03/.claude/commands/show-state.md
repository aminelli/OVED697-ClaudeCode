# Command: /show-state

Mostra lo stato corrente della pipeline in formato leggibile.

## Utilizzo

```
/show-state
```

## Procedura

### 1. Carica stato
Leggi `state/pipeline-state.json`.

### 2. Stampa tabella riassuntiva
```
╔══════════════════════════════════════════════════════════════════╗
║  STATO PIPELINE — <last_updated>                                ║
╠══════════╦══════════════╦════════════╦═════════════╦════════════╣
║  Ticket  ║  Status      ║  Categoria ║  Priorità   ║  Steps     ║
╠══════════╬══════════════╬════════════╬═════════════╬════════════╣
║ t-001    ║ draft-ready  ║ account    ║ high        ║ ✓ ✓        ║
║ t-002    ║ unprocessed  ║ —          ║ —           ║            ║
║ t-003    ║ approved     ║ billing    ║ medium      ║ ✓ ✓ ✓      ║
╚══════════╩══════════════╩════════════╩═════════════╩════════════╝

Totale: <n> ticket  |  In attesa revisione: <m>  |  Approvati: <k>
```

### 3. Evidenzia ticket con errori
Se ci sono ticket con `errors[]` non vuoto, mostrali separatamente:
```
⚠️  Ticket con errori:
   - ticket-002: "Errore lettura: file non trovato"
```

### 4. Suggerimenti
```
💡 Prossimi passi:
   - /process-ticket ticket-002  (non ancora processato)
   - Vai su http://localhost:4200 per approvare ticket-001
```
