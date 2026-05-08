---
artifact:type: review-comment
artifact:id: pr42_security
artifact:pr-id: pr-42
artifact:agent: security-agent
artifact:status: ready
artifact:severity-counts:
  critical: 1
  high: 2
  medium: 0
  low: 0
  info: 1
artifact:created-by: claude/security-agent
artifact:created-at: 2026-05-08T14:00:00Z
---

## Security Review — pr-42

### 🔴 CRITICAL — SQL Injection

**File**: `app/api/orders.py` · Riga ~18

**Codice problematico:**
```python
cursor.execute(
    "SELECT * FROM orders WHERE user_id = " + user_id
)
```

**Problema**: `user_id` è preso direttamente da `request.GET` senza alcuna sanitizzazione.
Un attaccante può iniettare SQL arbitrario, ad esempio:

```
GET /orders?user_id=1 OR 1=1 --
```

**Correzione:**
```python
cursor.execute(
    "SELECT * FROM orders WHERE user_id = %s",
    (user_id,),
)
```

---

### 🟠 HIGH — Hard-coded credentials

**File**: `app/api/orders.py` · Righe ~6–7

**Codice problematico:**
```python
SECRET_KEY = "mysecretkey123"
DB_PASSWORD = "Passw0rd!"
```

**Problema**: Credenziali hard-coded nel codice sorgente sono esposte a chiunque
abbia accesso al repository (compresi eventuali fork pubblici o log di CI/CD).

**Correzione**: usa variabili d'ambiente o un secret manager.
```python
import os
SECRET_KEY = os.environ["SECRET_KEY"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
```

---

### 🟠 HIGH — Command injection

**File**: `app/api/orders.py` · Ultima funzione

**Codice problematico:**
```python
def run_report(report_type):
    os.system("python generate_report.py " + report_type)
```

**Problema**: `report_type` non è validato. Un input come
`; rm -rf /` eseguirebbe un comando arbitrario sul server.

**Correzione:**
```python
import subprocess
ALLOWED_REPORT_TYPES = {"daily", "weekly", "monthly"}

def run_report(report_type: str) -> None:
    if report_type not in ALLOWED_REPORT_TYPES:
        raise ValueError(f"Tipo report non valido: {report_type}")
    subprocess.run(
        ["python", "generate_report.py", report_type],
        check=True,
    )
```

---

### ℹ️ INFO — Weak hashing (MD5)

**File**: `app/api/orders.py` · funzione `hash_password`

MD5 non è considerato sicuro per l'hashing di password.
Per password usa `bcrypt` o `argon2`. Per hash non-crittografici (checksum)
MD5 è accettabile se non riguarda dati sensibili.
