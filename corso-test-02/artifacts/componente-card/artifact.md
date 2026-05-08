---
artifact:type: html-component

artifact:title: Card Punto Vendita

artifact:description: >
  Componente HTML standalone che mostra una "card" per un singolo punto
  vendita con KPI sintetici. Può essere aperto nel browser o embedded
  in altre pagine come snippet HTML.
  USA QUESTO ARTIFACT PER: mockup UI, prototipazione rapida, esempi di
  design system, snippet da copiare in applicazioni web esistenti.
  NON USARE PER: visualizzare tutti i punti vendita insieme (usa dashboard-vendite).

artifact:input:
  primary:
    description: Path al CSV, oppure specificare direttamente i valori come parametri
    required-columns:
      - punto_vendita
      - fatturato
    optional-columns:
      - regione
      - variazione_pct   # variazione vs periodo precedente

artifact:output:
  path-pattern: "output/componente_card_{{NOME_PV}}_{{YYYYMMDD}}.html"
  format: html
  self-contained: true

artifact:dependencies: {}

artifact:quality-rules:
  - "Componente autonomo: funziona sia standalone che embedded"
  - "Larghezza fissa 320px (card mobile-first)"
  - "Deve includere: nome PV, fatturato, badge regione, indicatore trend (▲ verde / ▼ rosso)"
  - "CSS scoped: nessuna regola globale che impatti il resto della pagina se embedded"

artifact:version: "1.0"
---

# Artifact: componente-card

## Cosa genera

Un file `.html` con una singola card componente, riutilizzabile:

- **Header**: nome punto vendita + badge regione
- **KPI principale**: fatturato con formattazione €
- **Trend indicator**: variazione % con colore (verde ▲ / rosso ▼)
- **Footer**: data di riferimento

## Variabili del template

| Placeholder | Contenuto |
|------------|-----------|
| `{{NOME_PV}}` | Nome del punto vendita |
| `{{REGIONE}}` | Badge regione (o nascosto se assente) |
| `{{FATTURATO}}` | Valore formattato €X.XXX,XX |
| `{{VAR_PCT}}` | Es. "+12.3%" oppure "-4.1%" |
| `{{TREND_CLASS}}` | `trend-up` o `trend-down` (CSS class) |
| `{{DATA_RIF}}` | Data/mese di riferimento |
