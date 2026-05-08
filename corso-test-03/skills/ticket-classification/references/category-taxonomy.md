# Tassonomia delle categorie ticket

## billing

Qualsiasi questione relativa a pagamenti, fatturazione, abbonamenti.

**Esempi di trigger**:
- "ho ricevuto una fattura sbagliata"
- "mi è stato addebitato due volte"
- "voglio un rimborso"
- "il mio piano è stato cambiato senza consenso"

**Sotto-categorie**:
- `billing/fattura` — errori su fatture emesse
- `billing/rimborso` — richieste di rimborso
- `billing/abbonamento` — modifiche piano, upgrade/downgrade
- `billing/pagamento` — problemi con metodo di pagamento

---

## technical

Bug, malfunzionamenti, errori software/hardware.

**Esempi di trigger**:
- "il sistema va in errore quando faccio X"
- "la pagina non carica"
- "ho perso dei dati"
- "l'API restituisce 500"

**Sotto-categorie**:
- `technical/bug` — comportamento errato dell'applicazione
- `technical/performance` — lentezza, timeout
- `technical/integrazione` — problemi con sistemi terzi
- `technical/dati` — perdita o corruzione dati

---

## account

Gestione account, credenziali, profilo utente.

**Esempi di trigger**:
- "non riesco ad accedere"
- "ho dimenticato la password"
- "voglio cambiare email"
- "il mio account è stato bloccato"

---

## complaint

Lamentele generali senza categoria operativa specifica.

**Esempi di trigger**:
- "questo servizio fa schifo"
- "sono deluso della qualità"
- "valuto di cancellare l'abbonamento"

**Nota**: spesso ha sentiment `frustrated`. Priorità di default: `medium`.

---

## feature-request

Richieste di nuove funzionalità o miglioramenti.

**Esempi di trigger**:
- "sarebbe utile avere X"
- "perché non supportate Y"
- "ho un suggerimento"

**Nota**: sempre priorità `low` a meno di cliente premium critico.

---

## general

Tutto il resto: domande informative, richieste di documentazione.

**Esempi di trigger**:
- "come funziona X"
- "dove trovo la documentazione"
- "quali sono gli orari di supporto"
