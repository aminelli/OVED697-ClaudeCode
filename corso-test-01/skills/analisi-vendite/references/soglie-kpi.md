# Soglie KPI — Classificazione Semaforo RAG

Questo documento definisce le soglie per la classificazione Verde / Giallo / Rosso
di ciascun KPI. Aggiornare questo file quando le soglie aziendali cambiano.

**Ultimo aggiornamento**: 2026-05-08
**Versione**: 1.0

---

## Soglie per KPI primari

### Margine %

| Stato | Condizione | Significato |
|-------|-----------|-------------|
| 🟢 Verde | `margin_pct` ≥ 30% | Salute ottimale |
| 🟡 Giallo | 15% ≤ `margin_pct` < 30% | Monitorare |
| 🔴 Rosso | `margin_pct` < 15% | Azione richiesta |
| ⚪ N/D | `cost_price` assente | Non calcolabile |

### Ticket medio (valore ordine medio)

| Stato | Condizione | Significato |
|-------|-----------|-------------|
| 🟢 Verde | `avg_order_value` ≥ €150 | Ottimo mix prodotto |
| 🟡 Giallo | €75 ≤ `avg_order_value` < €150 | Nella norma |
| 🔴 Rosso | `avg_order_value` < €75 | Possibile erosione mix |

### Crescita MoM (mese su mese, ultimo vs penultimo mese)

| Stato | Condizione | Significato |
|-------|-----------|-------------|
| 🟢 Verde | `mom_growth` ≥ 5% | Crescita sana |
| 🟡 Giallo | 0% ≤ `mom_growth` < 5% | Crescita piatta |
| 🔴 Rosso | `mom_growth` < 0% | Calo — analizzare |
| ⚪ N/D | Meno di 2 mesi di dati | Non calcolabile |

---

## Soglie per KPI secondari

### Concentrazione cliente (% fatturato del top 1 cliente)

| Stato | Condizione | Significato |
|-------|-----------|-------------|
| 🟢 Verde | Top 1 cliente < 20% | Buona diversificazione |
| 🟡 Giallo | 20% ≤ top 1 cliente ≤ 40% | Dipendenza moderata |
| 🔴 Rosso | Top 1 cliente > 40% | Rischio concentrazione |
| ⚪ N/D | `customer_id` assente | Non calcolabile |

### Concentrazione prodotto (% fatturato del top 1 prodotto)

| Stato | Condizione | Significato |
|-------|-----------|-------------|
| 🟢 Verde | Top 1 prodotto < 30% | Buona diversificazione |
| 🟡 Giallo | 30% ≤ top 1 prodotto ≤ 50% | Dipendenza moderata |
| 🔴 Rosso | Top 1 prodotto > 50% | Rischio concentrazione |

### Qualità dati (% righe valide)

| Stato | Condizione | Significato |
|-------|-----------|-------------|
| 🟢 Verde | Righe valide ≥ 98% | Dati eccellenti |
| 🟡 Giallo | 90% ≤ righe valide < 98% | Qualità accettabile |
| 🔴 Rosso | Righe valide < 90% | Problemi di qualità dati |

---

## Note sull'applicazione

- Le soglie si applicano **dopo** la fase di calcolo, non durante
- In caso di dataset con meno di 10 righe, aggiungere una nota
  "⚠️ Dataset ridotto — classificazione indicativa"
- I valori monetari sono in **Euro (€)**
- La crescita MoM si calcola solo se ci sono **almeno 2 mesi completi** di dati
