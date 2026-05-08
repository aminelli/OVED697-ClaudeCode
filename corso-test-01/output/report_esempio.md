# 📊 Report Analisi Vendite

**File analizzato**: `vendite_esempio.csv`
**Data analisi**: 2026-05-08
**Periodo dati**: 2025-01-08 → 2025-04-29 (112 giorni)
**Righe elaborate**: 30 valide / 30 totali

---

## Sommario Esecutivo

Fatturato totale: €9.149,08 su 30 ordini. Margine lordo: 50.8%. Crescita ultimo mese: -6.6%.

**Stato complessivo**: 🔴 Attenzione richiesta

---

## KPI Principali

| KPI | Valore | Stato |
|-----|--------|-------|
| Fatturato totale | €9.149,08 | — |
| Margine totale | €4.651,09 | — |
| Margine % | 50.8% | 🟢 |
| Ticket medio | €304,97 | 🟢 |
| Numero ordini | 30 | — |
| Clienti unici | 6 | — |
| Crescita MoM | -6.6% | 🔴 |

---

## ⚠️ Warning Validazione

*Nessuna anomalia rilevata nella validazione.*

---

## Top 5 Prodotti per Fatturato

| # | Prodotto | Fatturato | % sul totale |
|---|----------|-----------|--------------|
| 1 | PROD-HW-05 | €2.900,30 | 31.7% |
| 2 | PROD-SW-03 | €1.637,60 | 17.9% |
| 3 | PROD-SW-01 | €1.374,74 | 15.0% |
| 4 | PROD-HW-12 | €1.134,30 | 12.4% |
| 5 | PROD-SRV-04 | €849,30 | 9.3% |

---

## Top 5 Clienti per Fatturato

| # | Cliente | Fatturato | % sul totale | Stato concentrazione |
|---|---------|-----------|--------------|---------------------|
| 1 | CUST-BETA | €2.325,20 | 25.4% | 🟡 |
| 2 | CUST-ALPHA | €2.139,50 | 23.4% | — |
| 3 | CUST-DELTA | €1.393,30 | 15.2% | — |
| 4 | CUST-GAMMA | €1.259,66 | 13.8% | — |
| 5 | CUST-ZETA | €1.069,03 | 11.7% | — |

---

## Fatturato per Categoria

| Categoria | Fatturato | % sul totale |
|-----------|-----------|----------|
| Hardware | €4.034,60 | 44.1% |
| Software | €3.696,05 | 40.4% |
| Servizi | €1.418,44 | 15.5% |

---

## Trend Mensile

| Mese | Fatturato | Var. vs mese prec. |
|------|-----------|-------------------|
| 2025-01 | €1.523,67 | — |
| 2025-02 | €1.812,84 | +19.0% |
| 2025-03 | €3.004,88 | +65.8% |
| 2025-04 | €2.807,70 | -6.6% |

```
2025-01  ██████████  €1.523,67
2025-02  ████████████  €1.812,84
2025-03  ████████████████████  €3.004,88
2025-04  ██████████████████  €2.807,70
```
*(Mini-chart: ogni █ ≈ €150,24)*

---

## Insight e Raccomandazioni

1. 🟡 Crescita leggermente negativa nell'ultimo mese (-6.6%).
2. 🟡 CUST-BETA rappresenta 25.4% del fatturato. Dipendenza moderata da un singolo cliente.
3. 🟢 Margine molto elevato (50.8%). Verificare che i prezzi di costo siano aggiornati.

---

## Metadati

| Campo | Valore |
|-------|--------|
| Script | `analizza_vendite.py` |
| Versione script | 1.0.0 |
| Righe totali lette | 30 |
| Righe valide | 30 |
| Righe scartate | 0 |
| Qualità dati | 🟢 100.0% |
| Margine calcolabile | Sì |
| Campi opzionali presenti | cost_price, customer_id, category |
