---
name: style-checking
description: >
  Knowledge base per l'analisi di code style e qualità. Contiene le
  convenzioni Python/JavaScript del progetto, soglie per funzioni lunghe
  e complessità ciclomatica, e pattern di detection per dead code,
  magic numbers e duplicazione.
  USATA DA: style-agent.
tools:
  - read_file
---

# Skill: Style Checking

## Convenzioni Python

### Naming
| Costrutto          | Convenzione   | Esempio                    |
|--------------------|---------------|----------------------------|
| Variabili/funzioni | `snake_case`  | `user_id`, `get_orders()`  |
| Classi             | `PascalCase`  | `OrderService`             |
| Costanti           | `UPPER_SNAKE` | `MAX_RETRY_COUNT = 3`      |
| Parametri privati  | `_prefixed`   | `_internal_state`          |
| Booleani           | `is_/has_/can_` | `is_active`, `has_permission` |

**Segnali di naming problematico:**
```python
# Nomi troppo corti e non descrittivi
def f(x, y): ...           # → def calculate_total(price, quantity):
for i in items: ...        # OK solo per indici numerici
data = get_data()          # troppo generico → orders = get_orders()

# Nomi fuorvianti
user_list = {}             # è un dict, non una list
is_valid = validate()      # se validate() ritorna None su errore
```

---

### Lunghezza funzioni e classi

| Soglia     | Severity | Azione consigliata                   |
|------------|----------|--------------------------------------|
| > 50 righe | `low`    | Considera di estrarre sotto-funzioni |
| > 80 righe | `medium` | Refactor quasi certamente necessario |
| > 150 righe| `high`   | Violazione del single responsibility |

**Come contare**: righe di codice, escludi docstring e commenti.

---

### Complessità ciclomatica

Conta rami: ogni `if`, `elif`, `for`, `while`, `except`, `and`, `or` in una funzione.

| Complessità | Severity | Stato                          |
|-------------|----------|--------------------------------|
| ≤ 5         | `info`   | Ottimale                       |
| 6–10        | `low`    | Accettabile, considera refactor|
| 11–15       | `medium` | Difficile da testare           |
| > 15        | `high`   | Refactor necessario            |

---

### Type hints

```python
# Mancante (segnala come low su funzioni interne, medium su API pubbliche)
def process_order(order_id, user):
    ...

# Corretto
def process_order(order_id: int, user: User) -> OrderResult:
    ...

# Casi accettabili senza type hint
# - Lambda semplici
# - Funzioni di test
# - Script one-shot
```

---

### Docstring

**Regola**: obbligatorie su classi pubbliche e funzioni pubbliche (non `_prefixed`).

```python
# Mancante — segnala come medium se funzione pubblica in modulo importato
def calculate_discount(price: float, user_tier: str) -> float:
    ...

# Corretto (Google style)
def calculate_discount(price: float, user_tier: str) -> float:
    """Calcola lo sconto applicabile al prezzo in base al tier utente.

    Args:
        price: Prezzo originale in euro.
        user_tier: Livello utente ('bronze', 'silver', 'gold').

    Returns:
        Prezzo scontato in euro.

    Raises:
        ValueError: Se user_tier non è riconosciuto.
    """
```

---

## Dead code

### Import non usati

```python
import os          # se os non è usato nel file
from typing import List  # se List non è usato
```

Severity: `low`.

### Variabili non usate

```python
result = calculate()    # result non usato
x, y = get_coords()    # x non usato
```

Severity: `low`.

### Codice commentato

```python
# old_value = get_value()   ← codice commentato da rimuovere
# for item in items:
#     process(item)
```

Severity: `low`. Meglio usare git per la storia del codice.

---

## Magic numbers

```python
# Pericoloso: numero senza nome
if retry_count > 3:          # cosa significa 3?
    time.sleep(0.5)           # perché 0.5?
if len(items) > 100:         # soglia magic

# Corretto: costante named
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 0.5
PAGINATION_LIMIT = 100

if retry_count > MAX_RETRIES:
    time.sleep(RETRY_DELAY_SECONDS)
```

Severity: `low`. Eccezioni: `0`, `1`, `-1`, `True`, `False`.

---

## TODO e FIXME senza riferimento

```python
# Da segnalare come low
# TODO: fix this
# FIXME: broken

# Accettabile
# TODO(GH-123): implementa validazione email
# FIXME(#456): gestisci il caso edge del timezone
```

---

## Duplicazione

Segnala quando vedi blocchi identici o quasi-identici > 5 righe.

```python
# Duplicazione — segnala come medium se > 10 righe
def format_user_name(user):
    name = user.first_name.strip()
    if user.last_name:
        name += " " + user.last_name.strip()
    return name.title()

def format_admin_name(admin):
    name = admin.first_name.strip()
    if admin.last_name:
        name += " " + admin.last_name.strip()
    return name.title()

# Soluzione
def format_full_name(person) -> str:
    name = person.first_name.strip()
    if person.last_name:
        name += " " + person.last_name.strip()
    return name.title()
```
