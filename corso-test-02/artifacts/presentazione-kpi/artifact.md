---
artifact:type: html-presentation

artifact:title: Presentazione KPI Vendite

artifact:description: >
  Slide deck HTML navigabile nel browser, con una slide per ciascun KPI
  principale e una slide di riepilogo. Navigazione con frecce o click.
  USA QUESTO ARTIFACT PER: presentazioni interne, report a schermo intero,
  condivisione come file HTML allegato.
  NON USARE PER: presentazioni con animazioni avanzate (usare PowerPoint),
  contenuto con molte immagini esterne.

artifact:input:
  primary:
    description: Path al CSV di vendite
    required-columns:
      - punto_vendita
      - mese
      - fatturato

artifact:output:
  path-pattern: "output/presentazione_{{NOME_FILE}}_{{YYYYMMDD}}.html"
  format: html
  self-contained: true
  encoding: utf-8

artifact:dependencies: {}
# Nessuna CDN: la presentazione usa solo CSS/JS inline

artifact:quality-rules:
  - "Navigazione: tasti freccia sinistra/destra + click su aree laterali"
  - "Slide obbligatorie: 1) copertina, 2) KPI totali, 3) ranking PV, 4) trend, 5) conclusioni"
  - "Font leggibile a schermo intero (min 24px per body text, 48px per headline)"
  - "Colori ad alto contrasto"
  - "Numero slide visibile in ogni pagina"
  - "Nessuna dipendenza esterna: tutto self-contained"

artifact:version: "1.0"
---

# Artifact: presentazione-kpi

## Cosa genera

Un file `.html` con 5 slide navigabili:

1. **Copertina**: titolo + periodo + azienda
2. **KPI Overview**: 3 card con i numeri principali
3. **Ranking Punti Vendita**: tabella ordinata per fatturato
4. **Trend Mensile**: mini-grafico ASCII o tabella trend
5. **Conclusioni**: top performer + next steps

## Variabili del template

| Placeholder | Contenuto |
|------------|-----------|
| `{{TITOLO_PRESENTAZIONE}}` | Titolo slide copertina |
| `{{PERIODO}}` | Range di date del dataset |
| `{{TOTALE_FATTURATO}}` | KPI principale |
| `{{TOP_PV}}` | Punto vendita #1 |
| `{{TREND_TABELLA}}` | HTML table con trend mensile |
| `{{RANKING_TABELLA}}` | HTML table ranking PV |
| `{{N_SLIDE}}` | Numero totale slide (per il counter) |
