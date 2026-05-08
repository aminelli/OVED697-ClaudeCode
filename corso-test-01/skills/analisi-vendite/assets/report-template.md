# Report Analisi Vendite — Template

<!-- 
  ISTRUZIONI PER CLAUDE:
  - Sostituisci ogni {{PLACEHOLDER}} con il valore reale calcolato
  - Non rimuovere sezioni; se i dati non sono disponibili, scrivi "N/D"
  - Mantieni l'ordine delle sezioni così com'è
  - I semafori: usa 🟢 🟡 🔴 ⚪ (non testo come "verde" o "rosso")
-->

# 📊 Report Analisi Vendite

**File analizzato**: `{{NOME_FILE}}`
**Data analisi**: {{DATA_ANALISI}}
**Periodo dati**: {{DATA_INIZIO}} → {{DATA_FINE}} ({{GIORNI_COPERTI}} giorni)
**Righe elaborate**: {{RIGHE_VALIDE}} valide / {{RIGHE_TOTALI}} totali

---

## Sommario Esecutivo

{{SOMMARIO_3_RIGHE_MAX}}

**Stato complessivo**: {{SEMAFORO_GLOBALE}} {{TESTO_STATO_GLOBALE}}

---

## KPI Principali

| KPI              | Valore               | Stato                     |
| ---------------- | -------------------- | ------------------------- |
| Fatturato totale | {{FATTURATO_TOTALE}} | {{SEMAFORO_FATTURATO}}    |
| Margine totale   | {{MARGINE_TOTALE}}   | {{SEMAFORO_MARGINE_ABS}}  |
| Margine %        | {{MARGINE_PCT}}%     | {{SEMAFORO_MARGINE_PCT}}  |
| Ticket medio     | {{TICKET_MEDIO}}     | {{SEMAFORO_TICKET_MEDIO}} |
| Numero ordini    | {{NUM_ORDINI}}       | —                         |
| Clienti unici    | {{CLIENTI_UNICI}}    | —                         |
| Crescita MoM     | {{CRESCITA_MOM}}%    | {{SEMAFORO_MOM}}          |

---

## ⚠️ Warning Validazione

<!-- Ometti questa sezione se non ci sono warning -->

{{LISTA_WARNING_O_MESSAGGIO_NESSUNA_ANOMALIA}}

---

## Top 5 Prodotti per Fatturato

| #   | Prodotto      | Fatturato      | % sul totale    |
| --- | ------------- | -------------- | --------------- |
| 1   | {{PROD_1_ID}} | {{PROD_1_REV}} | {{PROD_1_PCT}}% |
| 2   | {{PROD_2_ID}} | {{PROD_2_REV}} | {{PROD_2_PCT}}% |
| 3   | {{PROD_3_ID}} | {{PROD_3_REV}} | {{PROD_3_PCT}}% |
| 4   | {{PROD_4_ID}} | {{PROD_4_REV}} | {{PROD_4_PCT}}% |
| 5   | {{PROD_5_ID}} | {{PROD_5_REV}} | {{PROD_5_PCT}}% |

---

## Top 5 Clienti per Fatturato

<!-- Ometti questa sezione se customer_id non è presente nei dati -->

| #   | Cliente       | Fatturato      | % sul totale    | Stato concentrazione |
| --- | ------------- | -------------- | --------------- | -------------------- |
| 1   | {{CUST_1_ID}} | {{CUST_1_REV}} | {{CUST_1_PCT}}% | {{SEMAFORO_CONC_1}}  |
| 2   | {{CUST_2_ID}} | {{CUST_2_REV}} | {{CUST_2_PCT}}% | —                    |
| 3   | {{CUST_3_ID}} | {{CUST_3_REV}} | {{CUST_3_PCT}}% | —                    |
| 4   | {{CUST_4_ID}} | {{CUST_4_REV}} | {{CUST_4_PCT}}% | —                    |
| 5   | {{CUST_5_ID}} | {{CUST_5_REV}} | {{CUST_5_PCT}}% | —                    |

---

## Fatturato per Categoria

<!-- Ometti questa sezione se category non è presente nei dati -->

| Categoria | Fatturato | % sul totale |
| --------- | --------- | ------------ |
{{RIGHE_CATEGORIA}}

---

## Trend Mensile

| Mese | Fatturato | Var. vs mese prec. |
| ---- | --------- | ------------------ |
{{RIGHE_TREND}}

```
{{MINI_CHART_ASCII}}
```
*(Mini-chart: ogni █ = {{SCALA_CHART}} di fatturato)*

---

## Insight e Raccomandazioni

{{LISTA_INSIGHT_NUMERATA}}

---

## Metadati

| Campo                    | Valore                  |
| ------------------------ | ----------------------- |
| Script                   | `analizza_vendite.py`   |
| Versione script          | {{VERSIONE_SCRIPT}}     |
| Righe totali lette       | {{RIGHE_TOTALI}}        |
| Righe valide             | {{RIGHE_VALIDE}}        |
| Righe scartate           | {{RIGHE_SCARTATE}}      |
| Margine calcolabile      | {{MARGINE_DISPONIBILE}} |
| Campi opzionali presenti | {{CAMPI_OPZIONALI}}     |
