# Schema Dati di Vendita

Specifica del formato CSV accettato dalla skill `analisi-vendite`.

---

## Formato file

- **Tipo**: CSV
- **Separatore**: `,` (virgola) oppure `;` (punto e virgola — specificare con `--sep ";"`)
- **Encoding**: UTF-8 preferito, latin-1 accettato come fallback
- **Prima riga**: intestazione (header) obbligatoria
- **Date**: formato ISO 8601 — `YYYY-MM-DD`
- **Numeri decimali**: punto come separatore (es. `29.99`, non `29,99`)

---

## Colonne obbligatorie

| Colonna      | Tipo         | Vincoli             | Esempio        |
| ------------ | ------------ | ------------------- | -------------- |
| `order_id`   | string / int | Univoco, non nullo  | `ORD-2025-001` |
| `date`       | string       | ISO 8601, non nulla | `2025-03-15`   |
| `product_id` | string       | Non nullo           | `PROD-042`     |
| `quantity`   | int          | > 0                 | `5`            |
| `unit_price` | float        | > 0                 | `29.99`        |

---

## Colonne opzionali

| Colonna        | Tipo   | Vincoli | Sblocca KPI                         |
| -------------- | ------ | ------- | ----------------------------------- |
| `customer_id`  | string | —       | Top clienti, concentrazione cliente |
| `category`     | string | —       | Fatturato per categoria             |
| `discount_pct` | float  | 0–100   | Revenue netta corretta              |
| `cost_price`   | float  | > 0     | Margine %, margine assoluto         |
| `region`       | string | —       | (futura: analisi geografica)        |

---

## Formule di calcolo

```
revenue_riga  = quantity × unit_price × (1 - discount_pct / 100)
margin_riga   = revenue_riga - (quantity × cost_price)    ← solo se cost_price presente
```

---

## Esempio CSV completo

```csv
order_id,date,product_id,quantity,unit_price,customer_id,category,discount_pct,cost_price,region
ORD-001,2025-01-10,PROD-A,3,49.90,CUST-01,Software,0,22.00,Nord
ORD-002,2025-01-12,PROD-B,1,299.00,CUST-02,Hardware,5,150.00,Centro
ORD-003,2025-01-18,PROD-A,2,49.90,CUST-03,Software,10,22.00,Sud
ORD-004,2025-02-03,PROD-C,5,19.90,CUST-01,Servizi,0,8.00,Nord
ORD-005,2025-02-14,PROD-B,2,299.00,CUST-04,Hardware,0,150.00,Est
```

## Esempio CSV minimale (solo campi obbligatori)

```csv
order_id,date,product_id,quantity,unit_price
ORD-001,2025-01-10,PROD-A,3,49.90
ORD-002,2025-01-12,PROD-B,1,299.00
```

Con il CSV minimale, i KPI di margine e concentrazione cliente non saranno disponibili.
