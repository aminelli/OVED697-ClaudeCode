---
artifact:type: review-comment
artifact:id: pr42_performance
artifact:pr-id: pr-42
artifact:agent: performance-agent
artifact:status: ready
artifact:severity-counts:
  critical: 0
  high: 2
  medium: 1
  low: 0
  info: 0
artifact:created-by: claude/performance-agent
artifact:created-at: 2026-05-08T14:00:00Z
---

## Performance Review — pr-42

### 🟠 HIGH — N+1 query in `get_orders`

**File**: `app/api/orders.py` · Righe ~21–35

**Codice problematico:**
```python
for row in rows:
    order_id = row[0]
    # 1 query per ogni ordine → N query su order_items
    c.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
    # 1 query per ogni utente → N query su users
    c.execute("SELECT * FROM users WHERE id = %s", (row[1],))
```

**Impatto stimato:**
- Con 50 ordini: 1 (ordini) + 50 (items) + 50 (users) = **101 query per richiesta**
- A 100 req/min: **10.100 query/min** evitabili
- Con ottimizzazione: **1 query per richiesta**

**Correzione — usa JOIN:**
```python
cursor.execute("""
    SELECT o.id, o.user_id, o.created_at,
           u.name  AS user_name,
           i.product_id, i.quantity
    FROM orders o
    JOIN users u ON u.id = o.user_id
    LEFT JOIN order_items i ON i.order_id = o.id
    WHERE o.user_id = %s
""", (user_id,))
```

---

### 🟠 HIGH — N+1 annidato in `get_user_data`

**File**: `app/api/orders.py` · funzione `get_user_data`

**Codice problematico:**
```python
for item in user.orders.all():       # 1 query per ogni ordine
    for sub in item.sub_items.all(): # 1 query per ogni sub_item
        n = n + 1
```

**Impatto stimato:**
- Con 10 ordini × 5 sub_items = **50 query extra per utente**

**Correzione:**
```python
from django.db.models import Count
count = (
    user.orders
    .prefetch_related("sub_items")
    .aggregate(n=Count("sub_items"))["n"]
)
```

---

### 🟡 MEDIUM — Indici database mancanti su `Order`

**File**: `app/models.py`

Le colonne `status` e `created_at` del modello `Order` non hanno indice.
Qualsiasi query con `WHERE status = 'pending'` o `ORDER BY created_at`
eseguirà un full table scan.

**Correzione:**
```python
class Order(models.Model):
    status = models.CharField(max_length=20, default="pending", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
```

Genera la migrazione con:
```bash
python manage.py makemigrations --name add_order_indexes
```
