---
artifact:type: markdown-doc

artifact:title: Report Mensile Vendite

artifact:description: >
  Documento Markdown strutturato con KPI mensili, tabelle comparative per punto
  vendita e variazioni percentuali rispetto al mese precedente.
  Stile "report Word professionale" ma in formato leggibile e portabile.
  USA QUESTO ARTIFACT PER: report periodici da distribuire via email o Slack,
  documentazione delle performance mensili, brief per il management.
  NON USARE PER: presentazioni visive (usa presentazione-kpi), analisi interattive
  (usa dashboard-vendite).

artifact:input:
  primary:
    description: Path al CSV di vendite
    required-columns:
      - punto_vendita
      - mese
      - fatturato
    optional-columns:
      - regione
      - categoria
      - unita_vendute

artifact:output:
  path-pattern: "output/report_mensile_{{MESE_PRINCIPALE}}_{{YYYYMMDD}}.md"
  format: markdown
  self-contained: true
  encoding: utf-8

artifact:dependencies: {}

artifact:quality-rules:
  - "Il report deve avere un sommario esecutivo di max 3 righe in cima"
  - "Ogni KPI deve mostrare la variazione vs mese precedente (%, con freccia ▲▼)"
  - "Le tabelle devono essere in formato Markdown standard (pipe tables)"
  - "I valori monetari in formato €X.XXX,XX"
  - "Massimo 2 pagine A4 equivalenti (circa 600 parole)"
  - "Nessun placeholder residuo nel documento finale"

artifact:version: "1.0"
---

# Artifact: report-mensile

## Cosa genera

Un file `.md` con:

- **Intestazione**: periodo, data generazione, file sorgente
- **Sommario esecutivo**: 3 righe con i dati più rilevanti
- **Tabella KPI**: fatturato, unità, variazione MoM per ogni punto vendita
- **Top performer**: punto vendita con miglior crescita nel periodo
- **Alert**: eventuali punti vendita in calo > 10%
- **Note metodologiche**: fonte dati, data di generazione

## Variabili del template

| Placeholder | Contenuto |
|------------|-----------|
| `{{MESE_PRINCIPALE}}` | Mese analizzato, es. `2025-04` |
| `{{DATA_REPORT}}` | Data di generazione `DD/MM/YYYY` |
| `{{SOMMARIO}}` | 2-3 frasi con insight principali |
| `{{TABELLA_KPI}}` | Markdown pipe table con tutti i PV |
| `{{TOP_PERFORMER}}` | Nome PV con migliore crescita e % |
| `{{ALERT_SECTION}}` | Lista PV in calo (o "Nessun alert") |
| `{{TOTALE_FATTURATO}}` | Somma totale formattata |
| `{{VAR_MOM_TOTALE}}` | Variazione % vs mese precedente |
