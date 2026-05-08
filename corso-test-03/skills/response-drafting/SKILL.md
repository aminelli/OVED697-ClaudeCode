# Skill: Response Drafting

## Scopo

Questa skill guida la generazione di bozze di risposta professionali
per i ticket di supporto. Le bozze devono essere:

1. **Complete** — coprono tutti gli aspetti sollevati dal cliente
2. **Personalizzabili** — usano [PLACEHOLDER] per dati specifici
3. **Appropriate al tono** — rispecchiano il sentiment del cliente
4. **Azionabili** — includono passi concreti o richieste chiare

## Struttura standard di una risposta

```
[Saluto personalizzato]

[Riconoscimento del problema - 1-2 frasi]

[Corpo: soluzione, spiegazione, o passaggi successivi]

[Eventuale richiesta di informazioni aggiuntive]

[Stima tempi di risoluzione]

[Formula di chiusura]

[Firma]
```

## Linee guida per tono

### apologetic (per sentiment: frustrated)
- Prima frase: riconoscimento esplicito del disagio
- NO frasi difensive o giustificatorie
- Sii concreto sulle azioni intraprese
- Esempio apertura: "Capisco il suo disappunto e mi scuso per l'inconveniente causato."

### formal (per sentiment: neutral)
- Tono professionale ma accessibile
- Evita tecnicismi non necessari
- Sii diretto e strutturato

### technical (per categoria technical + sentiment neutral)
- Puoi usare terminologia tecnica
- Struttura in bullet point le istruzioni
- Include passi di troubleshooting

### empathetic (per casi delicati)
- Riconosci l'impatto umano del problema
- Usa "noi" e "lei/tu" in modo bilanciato

## Regole per i [PLACEHOLDER]

- Usa `[PLACEHOLDER: descrizione]` con descrizione chiara e specifica
- Esempi corretti:
  - `[PLACEHOLDER: nome e cognome del cliente]`
  - `[PLACEHOLDER: numero ticket interno CRM]`
  - `[PLACEHOLDER: data stimata di risoluzione]`
  - `[PLACEHOLDER: link alla documentazione specifica]`
- Mai lasciare campi vuoti: usa sempre il placeholder
- Conta i placeholder e riportali nel tool save-draft

## Lunghezza consigliata

| Categoria | Lunghezza risposta |
|-----------|-------------------|
| billing | 150-250 parole |
| technical | 200-350 parole (include passi troubleshooting) |
| account | 100-200 parole |
| complaint | 150-200 parole |
| general | 80-150 parole |
