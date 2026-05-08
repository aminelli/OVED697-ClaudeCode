---
artifact:type: review-report
artifact:id: review_pr-42
artifact:pr-id: pr-42
artifact:status: complete
artifact:verdict: REQUEST_CHANGES
artifact:sources:
  - pr42_security
  - pr42_performance
  - pr42_style
artifact:created-by: claude/orchestrator
artifact:created-at: 2026-05-08T14:05:00Z
---

# Code Review Report — pr-42

_Generato il: 2026-05-08T14:05:00Z_

## Verdetto: ❌ REQUEST_CHANGES

> Sono stati trovati **1 critical** e **4 high** problemi che devono essere
> risolti prima del merge.

## Riepilogo per agent

| Agent          | Critical | High | Medium | Low | Info |
|----------------|----------|------|--------|-----|------|
| 🔴 Security    | 1        | 2    | 0      | 0   | 1    |
| 🟡 Performance | 0        | 2    | 1      | 0   | 0    |
| 🔵 Style       | 0        | 0    | 2      | 3   | 0    |
| **Totale**     | **1**    | **4**| **3**  | **3**| **1**|

---

## Dettaglio Security Review

### 🔴 CRITICAL — SQL Injection

**File**: `app/api/orders.py` · Riga ~18

```python
cursor.execute(
    "SELECT * FROM orders WHERE user_id = " + user_id
)
```

Usa sempre parametri prepared:
```python
cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
```

### 🟠 HIGH — Hard-coded credentials

Righe ~6–7: `SECRET_KEY` e `DB_PASSWORD` hard-coded nel sorgente.
Migra a variabili d'ambiente (`os.environ["SECRET_KEY"]`).

### 🟠 HIGH — Command injection

Funzione `run_report`: input non validato passato a `os.system`.
Sostituisci con `subprocess.run(["python", "generate_report.py", validated_type])`.

### ℹ️ INFO — MD5 per hashing password

MD5 non è sicuro per password. Usa `bcrypt` o `argon2`.

---

## Dettaglio Performance Review

### 🟠 HIGH — N+1 query in `get_orders` (101 query per richiesta)

Loop che esegue 1 query per ogni ordine per caricare items e utente.
Sostituisci con JOIN:
```sql
SELECT o.*, u.name, i.product_id, i.quantity
FROM orders o
JOIN users u ON u.id = o.user_id
LEFT JOIN order_items i ON i.order_id = o.id
WHERE o.user_id = %s
```

### 🟠 HIGH — N+1 annidato in `get_user_data`

Loop annidato su ordini × sub_items → 50 query extra per utente.
Usa `prefetch_related` + `aggregate(Count(...))`.

### 🟡 MEDIUM — Indici mancanti su `Order.status` e `Order.created_at`

Aggiungi `db_index=True` ai campi e genera la migrazione.

---

## Dettaglio Style Review

### 🟡 MEDIUM — Duplicazione del blocco `format_full_name`

Estrai una funzione helper condivisa.

### 🟡 MEDIUM — `get_user_data` supera le 80 righe

Separa in sotto-funzioni con responsabilità singola.

### 🔵 LOW — Type hints mancanti sulle funzioni pubbliche

Aggiungi annotazioni su parametri e valori di ritorno.

### 🔵 LOW — TODO senza ticket (#GH-123)

Associa ogni TODO a un issue tracker.

### 🔵 LOW — Import `requests` non usato

Rimuovi l'import inutilizzato.
