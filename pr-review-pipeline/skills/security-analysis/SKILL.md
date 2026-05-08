---
name: security-analysis
description: >
  Knowledge base per l'analisi di sicurezza del codice. Contiene le
  categorie di vulnerabilità OWASP Top 10, pattern di detection per
  linguaggi comuni (Python, JavaScript, SQL) e linee guida per la
  classificazione della severity.
  USATA DA: security-agent.
tools:
  - read_file
---

# Skill: Security Analysis

## Categorie di vulnerabilità e pattern di detection

### 1. Segreti e credenziali hardcoded

**Pattern da cercare nel diff:**
```
password\s*=\s*["'][^"']+["']
api_key\s*=\s*["'][^"']+["']
secret\s*=\s*["'][^"']+["']
token\s*=\s*["'][^"']+["']
AWS_SECRET|PRIVATE_KEY|-----BEGIN
```

**Severity**: `critical` se in chiaro, `high` se offuscato ma recuperabile.

**Eccezioni legittime** (non segnalare):
- Valori placeholder: `"your-api-key-here"`, `"<SECRET>"`, `"TODO"`
- Variabili d'ambiente: `os.environ["API_KEY"]`, `os.getenv("SECRET")`
- File di test con valori ovviamente finti

---

### 2. SQL Injection

**Pattern da cercare:**
```python
# Pericoloso: concatenazione di stringa
f"SELECT * FROM users WHERE id = {user_id}"
"SELECT * FROM users WHERE id = " + str(user_id)
cursor.execute("SELECT ... WHERE id = %s" % user_id)  # % formattazione

# Sicuro: parametrized query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
cursor.execute("SELECT * FROM users WHERE id = :id", {"id": user_id})
```

**Severity**: `critical` se su endpoint autenticato, `high` altrimenti.

---

### 3. Command Injection

**Pattern da cercare:**
```python
# Pericoloso
os.system(f"ls {user_input}")
subprocess.run(f"convert {filename}", shell=True)
eval(user_input)
exec(user_code)

# Sicuro
subprocess.run(["convert", filename], shell=False)
```

**Severity**: `critical`.

---

### 4. XSS (Cross-Site Scripting)

**Pattern JavaScript:**
```javascript
// Pericoloso
element.innerHTML = userInput
document.write(data)
eval(jsonData)

// Sicuro
element.textContent = userInput
element.setAttribute("data-value", escapeHtml(userInput))
```

**Pattern template engine:**
```
# Jinja2 pericoloso
{{ user_input | safe }}
Markup(user_input)

# Sicuro
{{ user_input }}  (autoescaping attivo)
```

**Severity**: `high` per XSS stored, `medium` per reflected.

---

### 5. Autenticazione e autorizzazione

**Segnali da cercare:**
- Endpoint che modificano dati senza `@login_required` o middleware auth
- Confronto di ID senza verificare che appartengano all'utente corrente
- JWT verificato senza controllo della firma (`algorithm=None`)
- Password confrontate con `==` invece di `bcrypt.checkpw()`

```python
# Pericoloso
if request.args.get("user_id") == str(target_user_id):  # IDOR

# Sicuro
if current_user.id != target_user_id:
    raise PermissionDenied
```

**Severity**: `critical` per auth bypass, `high` per IDOR.

---

### 6. Crittografia debole

**Pattern:**
```python
# Pericoloso
hashlib.md5(password)
hashlib.sha1(data)
Fernet(key)  # se key è derivata da password senza KDF

# Sicuro
bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))
hashlib.sha256(data)
```

**Severity**: `high` per password, `medium` per dati non-password.

---

### 7. Path Traversal

**Pattern:**
```python
# Pericoloso
open(f"/uploads/{filename}")
os.path.join("/uploads", filename)  # se filename contiene ../

# Sicuro
safe_path = os.path.realpath(os.path.join("/uploads", filename))
if not safe_path.startswith("/uploads"):
    raise ValueError("Path traversal detected")
```

**Severity**: `high`.

---

## Riferimento severity per security

```
critical: RCE, auth bypass totale, segreti esposti, SQLi con DROP/INSERT
high:     SQLi, XSS stored, IDOR, path traversal, command injection
medium:   XSS reflected, weak crypto, missing auth su endpoint non critico
low:      Info leakage minore, log di dati sensibili, header mancanti
info:     Security best practice non seguite, hardening suggerito
```
