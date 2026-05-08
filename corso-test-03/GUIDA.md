# GUIDA — Corso-Test-03: Agent con Tool Use e State Management

## Indice

1. [Prerequisiti](#1-prerequisiti)
2. [Primo avvio — setup completo](#2-primo-avvio--setup-completo)
3. [Usare Claude Code — comandi agent](#3-usare-claude-code--comandi-agent)
4. [Flusso operatore — revisione bozze](#4-flusso-operatore--revisione-bozze)
5. [Struttura del progetto spiegata](#5-struttura-del-progetto-spiegata)
6. [Build di produzione e deploy](#6-build-di-produzione-e-deploy)
7. [Troubleshooting](#7-troubleshooting)
8. [Comandi rapidi di riferimento](#8-comandi-rapidi-di-riferimento)

---

## 1. Prerequisiti

| Tool | Versione minima | Verifica |
|------|----------------|---------|
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Angular CLI | 17+ | `npx ng version` |
| Claude Code | ultima | `claude --version` |

---

## 2. Primo avvio — setup completo

### Passo 1 — Entra nella directory del progetto

```bash
cd corso-test-03
```

### Passo 2 — Installa le dipendenze del backend

```bash
cd backend
npm install
```

Output atteso:
```
added 58 packages in 3s
```

### Passo 3 — Installa le dipendenze del frontend Angular

```bash
cd ../frontend
npm install
```

Output atteso (può richiedere 1-2 minuti):
```
added 920 packages in 45s
```

### Passo 4 — Avvia il backend

Apri un terminale e avvia il server Express:

```bash
cd backend
npm start
```

Output atteso:
```
 Backend API  → http://localhost:3001/api
  Health check → http://localhost:3001/api/health
  State API    → http://localhost:3001/api/state
```

Verifica che funzioni:
```bash
curl http://localhost:3001/api/health
# oppure apri nel browser: http://localhost:3001/api/health
```

Risposta attesa:
```json
{ "status": "ok", "timestamp": "2026-05-08T..." }
```

### Passo 5 — Avvia il frontend Angular

Apri un **secondo terminale** e avvia Angular Dev Server:

```bash
cd frontend
npx ng serve
```

Output atteso:
```
✔ Compiled successfully.
Application bundle generation complete.
Watch mode enabled. Watching for file changes...
  ➜ Local: http://localhost:4200/
```

Apri http://localhost:4200 nel browser.

### Passo 6 — Apri Claude Code sul progetto

In un **terzo terminale**:

```bash
cd corso-test-03
claude
```

Ora sei pronto per usare i comandi agent.

---

## 3. Usare Claude Code — comandi agent

### `/dev` — mostra istruzioni di avvio

```
/dev
```

Mostra i comandi per avviare backend e frontend.

---

### `/process-ticket <id>` — processa un singolo ticket

```
/process-ticket ticket-001
```

Cosa fa:
1. Carica lo stato da `state/pipeline-state.json`
2. Verifica che il ticket non sia già processato (idempotenza)
3. Delega a **classifier-agent** → genera `artifacts/classifications/ticket-001_classification.md`
4. Delega a **responder-agent** → genera `artifacts/drafts/ticket-001_draft.md`
5. Aggiorna lo stato della pipeline
6. Mostra riepilogo

Output atteso:
```
╔══════════════════════════════════════════╗
║  Pipeline completata per ticket-001      ║
╠══════════════════════════════════════════╣
║  Classificazione                         ║
║    Categoria:  account                   ║
║    Priorità:   high                      ║
║    Sentiment:  frustrated                ║
╠══════════════════════════════════════════╣
║  Bozza                                   ║
║    Oggetto:    Re: Accesso account ...   ║
║    Tono:       apologetic                ║
║    Placeholder: 4                        ║
╠══════════════════════════════════════════╣
║  Vai su http://localhost:4200 per        ║
║  revisionare e approvare la bozza.       ║
╚══════════════════════════════════════════╝
```

---

### `/process-all` — processa tutti i ticket non ancora elaborati

```
/process-all
```

Processa in sequenza tutti i ticket con status `unprocessed`.
I ticket già processati vengono saltati (idempotenza).

Output atteso:
```
📋 Ticket da processare: 3
   - ticket-002  [unprocessed]
   - ticket-003  [unprocessed]
   - ticket-004  [unprocessed]

   Salto:
   - ticket-001  [draft-ready]

[... elaborazione ...]

╔═══════════════════════════════════╗
║  Processo-all completato          ║
╠═══════════════════════════════════╣
║  Processati con successo: 3       ║
║  Saltati (già processati): 1      ║
║  Errori: 0                        ║
╚═══════════════════════════════════╝
```

---

### `/show-state` — visualizza stato pipeline

```
/show-state
```

Output atteso:
```
╔══════════════════════════════════════════════════════════════════╗
║  STATO PIPELINE — 2026-05-08T10:30:00Z                         ║
╠══════════╦══════════════╦════════════╦═════════════╦════════════╣
║  Ticket  ║  Status      ║  Categoria ║  Priorità   ║  Steps     ║
╠══════════╬══════════════╬════════════╬═════════════╬════════════╣
║ ticket-001 ║ draft-ready ║ account   ║ high        ║ ✓ ✓       ║
║ ticket-002 ║ draft-ready ║ billing   ║ high        ║ ✓ ✓       ║
║ ticket-003 ║ draft-ready ║ technical ║ high        ║ ✓ ✓       ║
║ ticket-004 ║ draft-ready ║ feature-r ║ low         ║ ✓ ✓       ║
╚══════════╩══════════════╩════════════╩═════════════╩════════════╝
```

---

## 4. Flusso operatore — revisione bozze

Dopo che Claude ha processato i ticket:

1. **Apri** http://localhost:4200
2. **Dashboard**: vedi tutti i ticket ordinati per priorità
3. **Clicca** su un ticket con status `draft-ready` (indicato in arancione)
4. **Pannello sinistro**: leggi la classificazione e il messaggio originale
5. **Pannello destro**: revisiona la bozza
   - Sostituisci tutti i `[PLACEHOLDER: ...]` con dati reali
   - Modifica il testo se necessario
6. **Salva** la bozza con il pulsante "💾 Salva bozza"
7. Quando tutti i placeholder sono compilati, **Approva** con "✓ Approva risposta"

Il contatore di placeholder nella barra in alto si azzera man mano che li compili.
Il bottone "Approva" è disabilitato finché rimangono placeholder.

---

## 5. Struttura del progetto spiegata

```
corso-test-03/
│
├── CLAUDE.md          ← Orchestratore: leggi qui per capire la pipeline
├── README.md          ← Overview del progetto
├── GUIDA.md           ← Questo file
│
├── tools/             ← CORE: definizioni tool use con schema JSON
│   ├── README.md      ← Spiegazione del concetto tool use
│   ├── read-ticket.json
│   ├── save-classification.json
│   ├── read-classification.json
│   ├── save-draft.json
│   ├── load-state.json
│   ├── save-state.json
│   └── update-ticket-status.json
│
├── agents/            ← Sub-agent specializzati
│   ├── classifier-agent.md   ← Classifica per categoria/priorità/sentiment
│   └── responder-agent.md    ← Genera bozza risposta con tone appropriato
│
├── skills/            ← Knowledge base riutilizzabile
│   ├── ticket-classification/
│   │   ├── SKILL.md          ← Criteri SLA e regole classificazione
│   │   └── references/
│   │       └── category-taxonomy.md
│   └── response-drafting/
│       ├── SKILL.md          ← Linee guida redazione risposte
│       └── templates/        ← Template per categoria
│
├── state/             ← CORE: gestione stato pipeline
│   ├── README.md      ← Spiegazione del pattern state management
│   └── pipeline-state.json  ← Stato corrente (aggiornato dagli agenti)
│
├── tickets/           ← Input: messaggi grezzi dei clienti
│   ├── ticket-001.txt
│   ├── ticket-002.txt
│   ├── ticket-003.txt
│   └── ticket-004.txt
│
├── artifacts/         ← Output: file generati dagli agenti
│   ├── classifications/    ← output di classifier-agent
│   ├── drafts/             ← output di responder-agent
│   └── manifests/
│
├── .claude/           ← Configurazione Claude Code
│   ├── settings.json
│   └── commands/
│       ├── process-ticket.md
│       ├── process-all.md
│       ├── show-state.md
│       └── dev.md
│
├── backend/           ← API Express.js
│   ├── server.js
│   ├── package.json
│   └── routes/
│       ├── tickets.js    ← CRUD ticket + approve/reject
│       ├── artifacts.js  ← Lista artifact
│       └── state.js      ← R/W stato pipeline
│
└── frontend/          ← Angular 17 (standalone components)
    ├── src/app/
    │   ├── components/
    │   │   ├── dashboard/            ← Lista ticket con stats
    │   │   ├── ticket-detail/        ← Editor bozza + approval
    │   │   └── pipeline-state-panel/ ← Sidebar stato pipeline
    │   ├── services/
    │   │   ├── tickets.service.ts
    │   │   └── state.service.ts
    │   └── models/
    │       ├── ticket.model.ts
    │       └── pipeline-state.model.ts
    └── proxy.conf.json   ← Proxy /api → localhost:3001
```

---

## 6. Build di produzione e deploy

### Build Angular

```bash
cd frontend
npx ng build --configuration production
```

Output: `frontend/dist/frontend/browser/`

### Avvia backend in produzione (serve anche il frontend)

```bash
cd backend
NODE_ENV=production node server.js
```

Il backend servirà la build Angular da `frontend/dist/frontend/browser/`.
Accedi su http://localhost:3001

### Deploy su server Linux

```bash
# 1. Copia il progetto sul server
scp -r corso-test-03/ user@server:/opt/app/

# 2. Sul server: installa dipendenze backend
cd /opt/app/corso-test-03/backend
npm install --omit=dev

# 3. Build frontend
cd ../frontend
npm install
npx ng build --configuration production

# 4. Avvia con PM2 (process manager)
npm install -g pm2
cd ../backend
pm2 start server.js --name corso-test-03 --env production
pm2 save
pm2 startup
```

### Docker (opzionale)

```bash
# Crea Dockerfile nella root del progetto
cat > Dockerfile << 'EOF'
FROM node:20-alpine AS build-frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npx ng build --configuration production

FROM node:20-alpine AS runtime
WORKDIR /app
COPY backend/package*.json ./backend/
RUN cd backend && npm ci --omit=dev
COPY backend/ ./backend/
COPY --from=build-frontend /app/frontend/dist ./frontend/dist
COPY tickets/ ./tickets/
COPY state/ ./state/
COPY artifacts/ ./artifacts/
ENV NODE_ENV=production PORT=3001
EXPOSE 3001
CMD ["node", "backend/server.js"]
EOF

docker build -t corso-test-03 .
docker run -p 3001:3001 -v $(pwd)/state:/app/state -v $(pwd)/artifacts:/app/artifacts corso-test-03
```

---

## 7. Troubleshooting

### Backend non si avvia — porta occupata

```bash
# Trova il processo che usa la porta 3001
netstat -ano | findstr :3001     # Windows
lsof -ti:3001 | xargs kill       # macOS/Linux

# Oppure cambia porta
PORT=3002 node server.js
```

### Frontend non si connette al backend

Verifica che `frontend/proxy.conf.json` punti alla porta giusta:
```json
{ "/api": { "target": "http://localhost:3001" } }
```

Verifica che il backend sia in esecuzione:
```bash
curl http://localhost:3001/api/health
```

### Errore Angular CLI: `ng: command not found`

```bash
# Usa npx
npx ng serve

# oppure installa globalmente
npm install -g @angular/cli
```

### Claude Code non trova i tool

Assicurati di essere nella directory `corso-test-03/` quando avvii `claude`.
I path nei tool JSON sono relativi alla root del progetto.

### Pipeline state corrotto

Ripristina lo stato iniziale:
```bash
cp state/pipeline-state.json state/pipeline-state.backup.json
cat > state/pipeline-state.json << 'EOF'
{
  "pipeline_version": "1.0",
  "last_updated": "2026-01-01T00:00:00.000Z",
  "tickets": {},
  "global": { "total_processed": 0, "pending_review": 0 }
}
EOF
```

### Rieseguire la classificazione di un ticket già processato

```bash
# Cancella gli artifact esistenti
rm artifacts/classifications/ticket-001_classification.md
rm artifacts/drafts/ticket-001_draft.md
```

Poi modifica `state/pipeline-state.json` e reimposta lo status del ticket a `unprocessed`.
Poi riesegui `/process-ticket ticket-001` in Claude Code.

---

## 8. Comandi rapidi di riferimento

### Backend

```bash
cd backend && npm install        # installa dipendenze
cd backend && npm start          # avvia server (porta 3001)
cd backend && npm run dev        # avvia con auto-reload
```

### Frontend Angular

```bash
cd frontend && npm install       # installa dipendenze
cd frontend && npx ng serve      # dev server (porta 4200)
cd frontend && npx ng build      # build produzione
cd frontend && npx ng test       # esegui test
```

### Claude Code

```bash
claude                           # avvia Claude Code nella dir corrente
/process-ticket ticket-001       # processa ticket specifico
/process-all                     # processa tutti i ticket non elaborati
/show-state                      # mostra stato pipeline
/dev                             # mostra istruzioni avvio
```

### API REST (test rapido)

```bash
# Lista ticket
curl http://localhost:3001/api/tickets

# Ticket specifico
curl http://localhost:3001/api/tickets/ticket-001

# Stato pipeline
curl http://localhost:3001/api/state

# Health check
curl http://localhost:3001/api/health

# Approva bozza
curl -X POST http://localhost:3001/api/tickets/ticket-001/approve \
  -H "Content-Type: application/json" \
  -d '{"body": "Testo risposta finale..."}'

# Rifiuta bozza
curl -X POST http://localhost:3001/api/tickets/ticket-001/reject \
  -H "Content-Type: application/json" \
  -d '{"reason": "Tono non appropriato"}'
```

### Gestione artifact manuale

```bash
# Visualizza classificazione
cat artifacts/classifications/ticket-001_classification.md

# Visualizza bozza
cat artifacts/drafts/ticket-001_draft.md

# Visualizza stato pipeline
cat state/pipeline-state.json | python -m json.tool
```
