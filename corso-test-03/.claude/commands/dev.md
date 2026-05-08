# Command: /dev

Avvia il backend Express e il frontend Angular in modalità sviluppo.

## Utilizzo

```
/dev
```

## Procedura

Fornisci le istruzioni per avviare entrambi i processi.
Non avviare processi direttamente: mostra i comandi all'utente.

### Output atteso

```
🚀 Per avviare l'ambiente di sviluppo, apri DUE terminali:

╔══════════════════════════════════════════════╗
║  TERMINALE 1 — Backend                       ║
╠══════════════════════════════════════════════╣
║  cd backend                                  ║
║  npm install   (solo la prima volta)         ║
║  npm start                                   ║
║                                              ║
║  → API disponibile su http://localhost:3001  ║
║  → Health: http://localhost:3001/api/health  ║
╚══════════════════════════════════════════════╝

╔══════════════════════════════════════════════╗
║  TERMINALE 2 — Frontend Angular              ║
╠══════════════════════════════════════════════╣
║  cd frontend                                 ║
║  npm install   (solo la prima volta)         ║
║  npx ng serve                                ║
║                                              ║
║  → App disponibile su http://localhost:4200  ║
╚══════════════════════════════════════════════╝

Poi in Claude Code puoi usare:
  /process-all           per processare tutti i ticket
  /process-ticket <id>   per processare un ticket specifico
  /show-state            per vedere lo stato della pipeline
```
