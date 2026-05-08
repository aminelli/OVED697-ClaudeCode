---
artifact:type: review-comment
artifact:id: pr42_style
artifact:pr-id: pr-42
artifact:agent: style-agent
artifact:status: ready
artifact:severity-counts:
  critical: 0
  high: 0
  medium: 2
  low: 3
  info: 0
artifact:created-by: claude/style-agent
artifact:created-at: 2026-05-08T14:00:00Z
---

## Style Review — pr-42

### 🟡 MEDIUM — Duplicazione di codice: `format_full_name`

**File**: `app/api/orders.py` · funzioni `get_user_data` e `get_admin_data`

Blocco identico (5 righe) ripetuto in entrambe le funzioni:
```python
full_name = person.first_name.strip()
if person.last_name:
    full_name = full_name + " " + person.last_name.strip()
full_name = full_name.title()
```

**Correzione** — estrai una funzione helper:
```python
def format_full_name(person) -> str:
    name = person.first_name.strip()
    if person.last_name:
        name += " " + person.last_name.strip()
    return name.title()
```

---

### 🟡 MEDIUM — Funzione `get_user_data` troppo lunga

**File**: `app/api/orders.py`

La funzione supera le 80 righe e gestisce troppi compiti:
recupero utente, calcolo conteggio items, formattazione nome, costruzione response.

**Suggerimento**: separa in sotto-funzioni:
```python
def get_user_data(request, user_id: int) -> JsonResponse:
    user = _get_user_or_404(user_id)
    return JsonResponse(_build_user_response(user))

def _build_user_response(user: User) -> dict:
    return {
        "name": format_full_name(user),
        "email": user.email,
        "item_count": _count_user_items(user),
    }
```

---

### 🔵 LOW — Type hints mancanti sulle funzioni pubbliche

**File**: `app/api/orders.py`

Le funzioni `get_orders`, `get_user_data`, `get_admin_data` e `run_report`
non hanno type hints sui parametri e sul valore di ritorno.

```python
# Attuale
def get_orders(request):
def hash_password(password):

# Corretto
from django.http import HttpRequest, JsonResponse

def get_orders(request: HttpRequest) -> JsonResponse:
def hash_password(password: str) -> str:
```

---

### 🔵 LOW — TODO senza riferimento a issue tracker

**File**: `app/api/orders.py`

```python
# TODO: validare i permessi
```

Il commento non ha un riferimento a un ticket. Usa:
```python
# TODO(GH-123): validare i permessi dell'utente prima di restituire i dati
```

---

### 🔵 LOW — Import non usato: `requests`

**File**: `app/api/orders.py` · Riga ~4

```python
import requests   # non usato nel diff
```

Rimuovi l'import o aggiungilo solo quando necessario.
