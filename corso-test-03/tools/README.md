# Tool Use — Guida ai Tool di questo Progetto

## Cos'è un Tool Use?

Il **tool use** (o function calling) è il meccanismo con cui un agente Claude
può eseguire azioni nel mondo reale invece di limitarsi a produrre testo.

### Flusso di una chiamata tool

```
Agente              Sistema
  │                    │
  │  "Ho bisogno di    │
  │   leggere il       │
  │   ticket 001"      │
  │                    │
  │──► [tool_use] ────►│   { name: "read-ticket",
  │                    │     input: { ticket_id: "ticket-001" } }
  │                    │
  │◄── [tool_result] ──│   { content: "Buongiorno, ho un problema..." }
  │                    │
  │  (ora l'agente ha  │
  │   il testo e può   │
  │   classificare)    │
```

### Anatomia di un tool (schema JSON)

```json
{
  "name": "nome-kebab-case",
  "description": "Descrizione precisa: cosa fa, quando usarlo, cosa ritorna",
  "input_schema": {
    "type": "object",
    "properties": {
      "param1": {
        "type": "string",
        "description": "Cosa rappresenta questo parametro"
      }
    },
    "required": ["param1"]
  }
}
```

## Tool di questo progetto

| File | Tool | Agente che lo usa |
|------|------|-------------------|
| `read-ticket.json` | Legge testo grezzo di un ticket | classifier-agent |
| `save-classification.json` | Scrive artifact di classificazione | classifier-agent |
| `read-classification.json` | Legge artifact di classificazione | responder-agent |
| `save-draft.json` | Scrive artifact bozza risposta | responder-agent |
| `load-state.json` | Carica stato pipeline da JSON | orchestratore |
| `save-state.json` | Salva stato pipeline su JSON | orchestratore |
| `update-ticket-status.json` | Aggiorna status di un singolo ticket | tutti |

## Best practice tool use

1. **Descrizioni precise**: la description è ciò che Claude legge per decidere
   se e quando usare il tool. Deve rispondere a: "cosa fa", "quando usarlo",
   "cosa restituisce in caso di errore".

2. **Parametri minimi**: ogni tool deve avere solo i parametri strettamente
   necessari. Troppi parametri obbligatori rendono il tool difficile da usare.

3. **Risposta strutturata**: il tool result deve essere sempre JSON parseable,
   con un campo `success: true|false` e un campo `error` in caso di fallimento.

4. **Idempotenza**: se possibile, il tool deve essere chiamabile più volte
   con lo stesso input senza effetti collaterali duplicati.
