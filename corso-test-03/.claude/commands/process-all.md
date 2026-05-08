# Command: /process-all

Processa tutti i ticket con status `unprocessed` in sequenza.

## Utilizzo

```
/process-all
```

## Procedura

### 1. Carica stato
Leggi `state/pipeline-state.json`.

### 2. Scopri tutti i ticket
Leggi la directory `tickets/` e lista tutti i file `.txt`.
Estrai gli ID (nome file senza estensione).

### 3. Filtra i ticket da processare
Per ogni ticket ID trovato:
- Controlla lo status nello stato
- Includi nella lista di lavoro solo quelli con status `unprocessed` o non presenti

### 4. Stampa piano di lavoro
```
📋 Ticket da processare: <n>
   - ticket-001  [unprocessed]
   - ticket-003  [not in state]

   Salto:
   - ticket-002  [draft-ready]
```

### 5. Processa in sequenza
Per ogni ticket nella lista di lavoro, esegui la stessa procedura
di `/process-ticket <id>` (classificazione + bozza).

**IMPORTANTE**: processa un ticket alla volta, in sequenza.
Non avviare il prossimo finché il precedente non è completato.
Questo evita race condition sullo stato condiviso.

### 6. Riepilogo finale
```
╔═══════════════════════════════════╗
║  Processo-all completato          ║
╠═══════════════════════════════════╣
║  Processati con successo: <n>     ║
║  Saltati (già processati): <m>    ║
║  Errori: <k>                      ║
╠═══════════════════════════════════╣
║  Vai su http://localhost:4200     ║
║  per revisionare le bozze.        ║
╚═══════════════════════════════════╝
```
