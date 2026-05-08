# Skill: Ticket Classification

## Scopo

Questa skill fornisce i criteri e le regole per classificare ticket di
supporto clienti in modo consistente e riproducibile.

## SLA per priorità

| Priorità | SLA risposta | Escalation |
|----------|-------------|------------|
| `critical` | 2 ore | Immediata al team senior |
| `high` | 8 ore | Notifica manager se non chiuso in 4h |
| `medium` | 24 ore | Standard |
| `low` | 72 ore | Standard |

## Criteri di priorità dettagliati

### Critical
- Servizio completamente non disponibile per il cliente
- Perdita o rischio di perdita di dati
- Problemi di sicurezza (accessi non autorizzati, breach)
- Blocco operativo con impatto economico immediato

### High
- Funzionalità principale degradata (non bloccata)
- Fattura con importo errato superiore a 100€
- Accesso bloccato a servizi business-critical
- Bug che impatta operatività quotidiana

### Medium
- Funzionalità secondaria non disponibile
- Workaround disponibile e comunicato
- Richiesta di chiarimento su fattura
- Lentezza o degrado performance

### Low
- Domande informative
- Richieste di funzionalità future
- Aggiornamenti dati profilo non urgenti
- Feedback e suggerimenti

## Tag predefiniti

Usa questi tag standardizzati quando possibile:

**Account**: `accesso-bloccato`, `cambio-password`, `dati-profilo`,
`permessi`, `autenticazione-2fa`, `account-sospeso`

**Billing**: `fattura-errata`, `rimborso`, `addebito-duplicato`,
`piano-abbonamento`, `scadenza-pagamento`, `credito`

**Technical**: `bug-critico`, `performance`, `errore-api`, `timeout`,
`perdita-dati`, `integrazione`, `aggiornamento`

**Generale**: `urgente`, `escalation`, `cliente-premium`, `prima-segnalazione`

## Regole di tiebreaking categoria

Quando un ticket può appartenere a più categorie:
1. Se c'è un aspetto `billing` → priorità a `billing`
2. Se c'è perdita dati + technical → `technical`
3. Se c'è sfogo emotivo senza problema specifico → `complaint`
4. In tutti gli altri casi di dubbio → categoria con priorità più alta
