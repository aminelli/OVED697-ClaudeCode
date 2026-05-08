---
# ── FRONTMATTER YAML ─────────────────────────────────────────────────────────
#
# Questo è il CONTRATTO dell'artifact: Claude si impegna a produrre
# esattamente ciò che è descritto qui, né più né meno.
#
# REGOLA D'ORO: sii specifico nei vincoli. Un artifact vago produce output
# inconsistente. Ogni campo è una garanzia che dai all'utente finale.
# ─────────────────────────────────────────────────────────────────────────────

artifact:type: html-interactive

artifact:title: Dashboard Vendite per Punto Vendita

artifact:description: >
  Dashboard HTML completamente interattiva con filtri a cascata e grafici
  Chart.js per l'analisi delle vendite per punto vendita.
  Funziona aprendo il file .html nel browser — nessun server, nessun npm install.
  USA QUESTO ARTIFACT PER: visualizzare dati tabellari CSV in modo esplorativo,
  confrontare performance tra punti vendita, vedere trend nel tempo, mostrare KPI
  in formato professionale pronto per presentazioni interne.
  NON USARE PER: applicazioni web multi-pagina, auth utente, dati in tempo reale,
  dataset superiori a 10.000 righe (usare invece un tool BI dedicato).

artifact:input:
  primary:
    description: Path al file CSV con dati di vendita per punto vendita
    required-columns:
      - punto_vendita    # string: nome del negozio
      - regione          # string: area geografica
      - mese             # string: YYYY-MM
      - fatturato        # float: ricavi nel mese
    optional-columns:
      - unita_vendute    # int: abilita grafico unità
      - categoria        # string: abilita filtro per categoria

artifact:output:
  path-pattern: "output/dashboard_{{NOME_FILE}}_{{YYYYMMDD}}.html"
  format: html
  self-contained: true
  encoding: utf-8

artifact:dependencies:
  cdn:
    - name: Chart.js 4
      url: https://cdn.jsdelivr.net/npm/chart.js@4
  # Nessuna dipendenza locale: tutto inline o CDN

artifact:quality-rules:
  - "Self-contained: CSS e JS devono essere dentro <style> e <script>, non file esterni"
  - "I dati CSV devono essere convertiti in JSON e embedded nel tag <script> come variabile const"
  - "Il file deve funzionare con doppio-click in Chrome, Firefox, Safari, Edge"
  - "Filtri obbligatori: regione (select), mese (select), reset button"
  - "Filtro categoria se il campo è presente nel CSV, altrimenti omettere"
  - "Grafici obbligatori: 1 bar chart (fatturato per punto vendita) + 1 line chart (trend mensile)"
  - "KPI cards obbligatorie: fatturato totale, punto vendita top, mese migliore"
  - "I colori dei grafici devono usare la palette definita nel template"
  - "Layout responsivo: funzionare su schermi da 1024px in su"
  - "Niente lorem ipsum: tutti i valori visualizzati derivano dal CSV reale"

artifact:version: "1.0"
---

# Artifact: dashboard-vendite

## Cosa genera

Un singolo file `.html` che l'utente apre nel browser e ottiene:

- **Filtri interattivi**: dropdown per Regione, Mese, Categoria (se presente) + Reset
- **KPI Cards**: Fatturato Totale filtrato, Punto Vendita Top, Mese Migliore
- **Grafico 1 — Bar chart**: fatturato per punto vendita (filtrato)
- **Grafico 2 — Line chart**: trend mensile (filtrato)
- **Grafico 3 — Doughnut**: mix per categoria (se presente)
- **Tabella ranking**: tutti i punti vendita con fatturato e variazione

## Come Claude genera questo artifact

1. Legge il CSV indicato dall'utente
2. Valida che le colonne obbligatorie siano presenti
3. Converte tutti i dati in un oggetto JSON
4. Legge `template.html` (questo file è la struttura di riferimento)
5. Sostituisce ogni `{{PLACEHOLDER}}` con il valore reale
6. Salva il file HTML in `output/` con il naming convention definito sopra

## Istruzioni di preview

Dopo la generazione, l'utente può aprire il file così:
- **Windows**: doppio click sul file `.html` oppure `start output\dashboard_*.html`
- **Mac/Linux**: `open output/dashboard_*.html`
- **Da terminale**: il browser di default aprirà il file

Nessun server richiesto. Funziona offline.

## Variabili del template

| Placeholder | Tipo | Contenuto |
|------------|------|-----------|
| `{{TITOLO}}` | string | Titolo della dashboard (es. "Vendite per Punto Vendita") |
| `{{DATA_GENERAZIONE}}` | string | Data in formato `DD/MM/YYYY` |
| `{{NOME_FILE_SORGENTE}}` | string | Nome del CSV di input |
| `{{DATA_JSON}}` | JSON | Array di oggetti con tutti i dati del CSV |
| `{{MESI_DISPONIBILI_JSON}}` | JSON | Array di mesi unici ordinati |
| `{{REGIONI_DISPONIBILI_JSON}}` | JSON | Array di regioni uniche ordinate |
| `{{CATEGORIE_DISPONIBILI_JSON}}` | JSON | Array di categorie uniche (o `[]` se assente) |
