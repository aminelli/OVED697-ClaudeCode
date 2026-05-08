---
name: performance-analysis
description: >
  Knowledge base per l'analisi di performance del codice. Contiene i
  pattern di detection per N+1 query, complessità algoritmica, blocking I/O,
  memory leak e ottimizzazioni di caching, con esempi Python e SQL.
  USATA DA: performance-agent.
tools:
  - read_file
---

# Skill: Performance Analysis

## Categorie e pattern di detection

### 1. N+1 Query

**Il problema**: una query eseguita dentro un loop produce N query invece di 1.

**Pattern da cercare:**
```python
# Pericoloso: query dentro loop
for order in orders:                    # 1 query → N oggetti
    items = order.items.all()           # N query aggiuntive
    user = User.objects.get(id=order.user_id)  # N query aggiuntive

# Sicuro: prefetch
orders = Order.objects.prefetch_related("items").select_related("user")
for order in orders:
    items = order.items.all()  # nessuna query aggiuntiva
```

**Pattern SQL raw:**
```python
# Pericoloso
for row in cursor.fetchall():
    cursor.execute("SELECT * FROM items WHERE order_id = %s", (row["id"],))

# Sicuro
cursor.execute("""
    SELECT o.*, i.*
    FROM orders o
    JOIN order_items i ON i.order_id = o.id
    WHERE o.user_id = %s
""", (user_id,))
```

**Severity**: `high` su endpoint pubblici, `medium` su endpoint interni.

---

### 2. Complessità algoritmica

**Pattern da cercare:**

```python
# O(n²) — ricerca in lista dentro loop
for item in items:
    if item in another_list:  # O(n) per ogni iterazione → O(n²) totale
        ...

# O(n log n) preferibile → O(n) con set
lookup = set(another_list)  # O(n) una volta
for item in items:
    if item in lookup:  # O(1)
        ...

# O(n²) — sort dentro loop
for i in range(len(data)):
    data[i:] = sorted(data[i:])  # sort ad ogni iterazione

# Sorting duplicato
result = sorted(sorted(items, key=lambda x: x.name), key=lambda x: x.date)
# → usa chiave di ordinamento composta
result = sorted(items, key=lambda x: (x.date, x.name))
```

**Severity**: `critical` per O(n!) o O(2^n), `high` per O(n²) su dataset > 1000.

---

### 3. Blocking I/O in contesto async

**Pattern da cercare:**
```python
# Pericoloso: sync I/O in async function
async def get_user(user_id: int):
    time.sleep(0.1)                    # blocca l'event loop
    response = requests.get(url)       # blocca l'event loop
    with open("file.txt") as f:        # blocca l'event loop (meglio aiofiles)
        data = f.read()

# Sicuro
async def get_user(user_id: int):
    await asyncio.sleep(0.1)
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
    async with aiofiles.open("file.txt") as f:
        data = await f.read()
```

**Severity**: `high` in produzione, `medium` in background task.

---

### 4. Memory leak

**Pattern da cercare:**
```python
# Accumulatore senza limite
cache = {}
def get_data(key):
    if key not in cache:
        cache[key] = fetch(key)  # cresce indefinitamente
    return cache[key]

# Meglio con LRU cache limitata
from functools import lru_cache
@lru_cache(maxsize=1000)
def get_data(key): ...

# File/connessione non chiusi
f = open("file.txt")
data = f.read()
# f.close() manca → usa sempre with

conn = psycopg2.connect(...)
cursor = conn.cursor()
# conn.close() manca
```

**Severity**: `high` se in loop hot path, `medium` altrimenti.

---

### 5. Caching mancante

**Pattern:**
```python
# Chiamata costosa ripetuta senza cache
def get_config():
    return db.query("SELECT * FROM config")  # ogni chiamata = query

# Con cache (Django)
from django.core.cache import cache
def get_config():
    result = cache.get("config")
    if result is None:
        result = db.query("SELECT * FROM config")
        cache.set("config", result, timeout=300)
    return result
```

**Segnali**: funzione costosa chiamata più volte nello stesso request scope,
risultato non cambia tra le chiamate, calcolo deterministico.

**Severity**: `medium`.

---

### 6. Indici database assenti

**Pattern SQL da cercare nel diff:**
```sql
-- Query che filtrano su colonne senza indice
WHERE status = 'pending'        -- se status non ha indice
WHERE email LIKE '%@domain.com' -- LIKE con % prefisso non usa indice
ORDER BY created_at DESC        -- se created_at non ha indice

-- JOIN su colonne senza indice FK
SELECT * FROM orders o
JOIN users u ON u.id = o.user_id  -- user_id deve avere indice
```

**Severity**: `high` su tabelle > 10k righe, `medium` su tabelle piccole.

---

## Stima impatto

Per ogni problema di performance, includi una stima dell'impatto:

```
Impatto stimato:
- Con 100 oggetti: 100 query extra (attuale) → 1 query (ottimizzato)
- Differenza: ~99 round-trip database per richiesta
- A 1000 req/min: 99.000 query extra al minuto evitabili
```
