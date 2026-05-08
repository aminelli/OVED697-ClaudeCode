# Logica di Analisi Predefinita — 4 Fasi

Questo documento definisce **le regole fisse** che la skill `analisi-vendite`
deve seguire per ogni analisi. Non si tratta di suggerimenti: sono regole
obbligatorie che garantiscono risultati consistenti e confrontabili nel tempo.

---

## Fase 1 — Validazione dei dati

### 1.1 Controllo schema

Verifica la presenza dei campi obbligatori (vedi `data-schema.md`):

| Campo        | Controllo                                 | Tipo errore |
| ------------ | ----------------------------------------- | ----------- |
| `order_id`   | Presente e non nullo                      | Bloccante   |
| `date`       | Presente, formato ISO 8601 (`YYYY-MM-DD`) | Bloccante   |
| `product_id` | Presente e non nullo                      | Bloccante   |
| `quantity`   | Presente, intero > 0                      | Bloccante   |
| `unit_price` | Presente, float > 0                       | Bloccante   |

### 1.2 Controllo qualità

| Condizione                               | Tipo errore | Azione                                    |
| ---------------------------------------- | ----------- | ----------------------------------------- |
| `quantity` = 0                           | Warning     | Includi nel report, non escludere la riga |
| `unit_price` < 0                         | Warning     | Includi nel report, non escludere la riga |
| `discount_pct` > 100 o < 0               | Warning     | Tratta come 0 per il calcolo              |
| `cost_price` > `unit_price`              | Warning     | Indica margine negativo, non escludere    |
| Duplicati `order_id`                     | Warning     | Conta e segnala, usa prima occorrenza     |
| Date fuori range (> oggi o < 2000-01-01) | Warning     | Includi nel report                        |

### 1.3 Regola di stop

Se ci sono **errori bloccanti** su più del 5% delle righe → ferma l'analisi.
Se ci sono errori bloccanti su meno del 5% delle righe → escludi le righe
problematiche, procedi e includi il conteggio nel report.

---

## Fase 2 — Calcolo KPI

I KPI vanno calcolati **nell'ordine seguente** (alcuni dipendono da altri):

### 2.1 Revenue per riga

```
revenue_riga = quantity × unit_price × (1 - discount_pct / 100)
```

Se `discount_pct` è assente: usare 0.

### 2.2 Margine per riga

```
margin_riga = revenue_riga - (quantity × cost_price)
```

Se `cost_price` è assente: il margine non è calcolabile → segnalarlo nel report,
non mostrare i KPI di margine.

### 2.3 KPI aggregati

Calcolare nell'ordine:

1. **Fatturato totale** (`total_revenue`): somma di `revenue_riga`
2. **Margine totale** (`total_margin`): somma di `margin_riga` (se disponibile)
3. **Margine %** (`margin_pct`): `total_margin / total_revenue × 100`
4. **Numero ordini** (`order_count`): conteggio righe valide
5. **Ticket medio** (`avg_order_value`): `total_revenue / order_count`
6. **Clienti unici** (`unique_customers`): conteggio `customer_id` distinti (se presente)
7. **Top 5 prodotti** per fatturato (`top_products`): group by `product_id`
8. **Top 5 clienti** per fatturato (`top_customers`): group by `customer_id` (se presente)
9. **Fatturato per categoria** (`revenue_by_category`): group by `category` (se presente)
10. **Trend mensile** (`monthly_trend`): group by `YYYY-MM`, somma fatturato per mese
11. **Crescita MoM** (`mom_growth`): crescita % dell'ultimo mese vs penultimo mese
    (solo se ci sono ≥ 2 mesi di dati)

### 2.4 Periodo di analisi

Calcola sempre:
- `date_start`: data minima nel dataset
- `date_end`: data massima nel dataset
- `days_covered`: numero di giorni tra start e end

---

## Fase 3 — Classificazione Semaforo

Per ogni KPI, applica le soglie definite in `soglie-kpi.md`.

**Ordine di applicazione:**
1. Controlla se il KPI è calcolabile (dati sufficienti)
2. Se non calcolabile → mostra `⚪ N/D` (non disponibile)
3. Se calcolabile → applica la soglia → Verde 🟢 / Giallo 🟡 / Rosso 🔴

**Regola del semaforo globale:**
Il semaforo globale del report è il peggiore tra i semafori dei KPI primari
(fatturato trend, margine %, ticket medio). Si mostra nel sommario esecutivo.

---

## Fase 4 — Generazione Insight

Gli insight sono osservazioni testuali generate automaticamente **solo se**
le condizioni corrispondenti sono verificate. Non generare insight speculativi.

### Regole insight (in ordine di priorità)

| Priorità | Condizione                         | Insight da generare                                                                                |
| -------- | ---------------------------------- | -------------------------------------------------------------------------------------------------- |
| 🔴 Alta   | `mom_growth` < -10%                | "Calo significativo del fatturato nell'ultimo mese (–X%): analizzare le cause."                    |
| 🔴 Alta   | `margin_pct` < 15%                 | "Margine sotto la soglia critica (X%): verificare i costi di acquisto."                            |
| 🔴 Alta   | Top 1 cliente > 40% del fatturato  | "Concentrazione cliente elevata: [ID] rappresenta X% del fatturato totale. Rischio di dipendenza." |
| 🟡 Media  | `mom_growth` tra -10% e 0%         | "Crescita piatta o leggermente negativa nell'ultimo mese (X%)."                                    |
| 🟡 Media  | Top 1 prodotto > 50% del fatturato | "Concentrazione prodotto: [ID] rappresenta X% del fatturato. Valutare diversificazione."           |
| 🟡 Media  | `avg_order_value` in calo MoM > 5% | "Il ticket medio si sta riducendo. Possibile erosione del mix prodotto."                           |
| 🟢 Bassa  | `mom_growth` > 20%                 | "Crescita eccellente nell'ultimo mese (+X%). Analizzare i fattori positivi per replicarli."        |
| 🟢 Bassa  | `margin_pct` > 40%                 | "Margine molto elevato (X%). Verificare che i prezzi di costo siano aggiornati."                   |

### Limite insight

Mostrare al massimo **5 insight** nel report, in ordine di priorità (🔴 prima, 🟢 ultima).
Se non ci sono condizioni verificate, scrivere: *"Nessuna anomalia rilevante rilevata."*

---

## Ordine di presentazione nel report

Il report **deve** seguire quest'ordine (vedi anche `assets/report-template.md`):

1. Intestazione (nome file, data analisi, periodo dati)
2. Sommario Esecutivo (3 righe max + semaforo globale)
3. Tabella KPI con semaforo
4. Warning validazione (se presenti)
5. Top 5 prodotti
6. Top 5 clienti (se dati disponibili)
7. Fatturato per categoria (se dati disponibili)
8. Trend mensile (tabella + mini-chart ASCII se ≥ 3 mesi)
9. Insight e raccomandazioni
10. Metadati (righe elaborate, righe scartate, versione script)
