# Guida Completa: Skills, Artifacts e Agents con Claude

## Indice

1. [Prerequisiti](#1-prerequisiti)
2. [Scenario: Pipeline di Analisi Dati](#2-scenario-pipeline-di-analisi-dati)
3. [Struttura del Progetto](#3-struttura-del-progetto)
4. [Concetto di Idempotenza](#4-concetto-di-idempotenza)
5. [Skills — Come Scriverle Correttamente](#5-skills--come-scriverle-correttamente)
6. [Artifacts — Gestione Idempotente degli Output](#6-artifacts--gestione-idempotente-degli-output)
7. [Agents — Il Loop di Tool-Use](#7-agents--il-loop-di-tool-use)
8. [Installazione e Configurazione](#8-installazione-e-configurazione)
9. [Esecuzione della Pipeline](#9-esecuzione-della-pipeline)
10. [Eseguire i Test](#10-eseguire-i-test)
11. [Estendere il Progetto](#11-estendere-il-progetto)
12. [Errori Comuni e Soluzioni](#12-errori-comuni-e-soluzioni)

---

## 1. Prerequisiti

### Software da installare

| Software | Versione minima | Verifica |
|----------|----------------|---------|
| Python | 3.10+ | `python --version` |
| pip | 23+ | `pip --version` |
| Git | qualsiasi | `git --version` |

### Account necessari

- **Anthropic API Key**: registrati su [console.anthropic.com](https://console.anthropic.com) e genera una chiave API dalla sezione *API Keys*.

### Installare Python su Windows

```powershell
# Opzione 1: winget (Windows 11/10)
winget install Python.Python.3.12

# Opzione 2: scarica da python.org
# https://www.python.org/downloads/
# IMPORTANTE: seleziona "Add Python to PATH" durante l'installazione
```

### Installare Python su macOS

```bash
# Con Homebrew (raccomandato)
brew install python@3.12

# Oppure scarica da python.org
```

### Installare Python su Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

---

## 2. Scenario: Pipeline di Analisi Dati

### Perché questo scenario?

Abbiamo scelto una **pipeline di analisi dati di vendita** perché:

1. **È realistico**: molte aziende hanno CSV di dati periodici (mensili, trimestrali).
2. **È costoso**: chiamare Claude per analizzare ogni file richiede tempo e token API.
3. **È perfetto per l'idempotenza**: i file CSV cambiano raramente; rielaborarli ogni volta sarebbe uno spreco.
4. **Usa tutte e 3 le componenti**: skills (leggi/analizza CSV), artifacts (salva report), agents (ragionamento adattivo).

### Cosa fa la pipeline

```
data/
  products_q1.csv ──→ DataAnalystAgent ──→ output/analysis_products_q1.md
  products_q2.csv ──→ DataAnalystAgent ──→ output/analysis_products_q2.md
  products_q3.csv ──→ DataAnalystAgent ──→ output/analysis_products_q3.md
                                               ↓
                                        ReportWriterAgent
                                               ↓
                                  output/summary_report.md
```

**Comportamento idempotente:**
- Prima esecuzione: analizza tutti e 3 i CSV, genera 4 artifact.
- Seconda esecuzione (nessun file modificato): **0 chiamate a Claude**, 0 token sprecati.
- Dopo modifica di `products_q2.csv`: rigenera solo `analysis_products_q2.md` e `summary_report.md`.

---

## 3. Struttura del Progetto

```
C001/
├── .env.example              # Template per le variabili d'ambiente
├── .env                      # (da creare) Chiave API e configurazione
├── requirements.txt          # Dipendenze Python
│
├── data/                     # File CSV di input (dati di vendita)
│   ├── products_q1.csv
│   ├── products_q2.csv
│   └── products_q3.csv
│
├── output/                   # Artifact generati (report, analisi)
│   ├── .gitkeep
│   ├── artifacts.json        # Registro degli artifact (creato a runtime)
│   ├── analysis_products_q1.md
│   ├── analysis_products_q2.md
│   ├── analysis_products_q3.md
│   └── summary_report.md
│
├── src/
│   ├── __init__.py
│   │
│   ├── artifacts/
│   │   ├── __init__.py
│   │   └── manager.py        # ⭐ ArtifactManager — cuore dell'idempotenza
│   │
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── registry.py       # ⭐ SkillRegistry — dispatcher centralizzato
│   │   ├── file_skills.py    # Skill: read_text_file, list_directory
│   │   ├── data_skills.py    # Skill: parse_csv_schema, compute_column_stats, aggregate_by_category
│   │   └── artifact_skills.py # Skill: check_artifact_status, save_artifact, load_artifact, list_artifacts
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py     # ⭐ BaseAgent — loop tool-use
│   │   ├── data_analyst_agent.py   # Analizza un singolo CSV
│   │   ├── report_writer_agent.py  # Compila il report di sintesi
│   │   └── orchestrator_agent.py   # Coordina la pipeline (puro Python)
│   │
│   └── pipeline.py           # Entry point con CLI
│
└── tests/
    ├── __init__.py
    ├── test_artifact_manager.py  # Test idempotenza (no API key)
    └── test_skills.py            # Test skill (no API key)
```

---

## 4. Concetto di Idempotenza

### Definizione

> Un'operazione è **idempotente** se eseguirla N volte produce lo stesso risultato di eseguirla una sola volta.

Nel contesto delle pipeline Claude, l'idempotenza significa:
- Stessi dati in input → stesso output, senza chiamate API ridondanti.
- La pipeline può essere interrotta e riavviata senza problemi.
- Modifiche parziali ai dati causano rielaborazione parziale, non totale.

### Come funziona in questo progetto

Il meccanismo si basa su **content-addressed storage** con hash SHA-256:

```
┌─────────────────────────────────────────────────────────────┐
│                   FLUSSO IDEMPOTENTE                         │
│                                                             │
│  Input CSV                                                  │
│     │                                                       │
│     ▼                                                       │
│  compute_hash(csv_content)  →  "a3f8b2..."                  │
│     │                                                       │
│     ▼                                                       │
│  is_stale("analysis_q1.md", "a3f8b2...")?                   │
│     │                                                       │
│     ├─ NO (hash uguale) ──→  SKIP  ←── IDEMPOTENZA!        │
│     │                                                       │
│     └─ SÌ (hash diverso o assente)                         │
│           │                                                  │
│           ▼                                                  │
│        Claude analizza il CSV                               │
│           │                                                  │
│           ▼                                                  │
│        save_artifact(id, content, source_hash)              │
│           │                                                  │
│           ▼                                                  │
│        Registro aggiornato: { source_hash: "a3f8b2..." }    │
└─────────────────────────────────────────────────────────────┘
```

### Il registro `artifacts.json`

```json
{
  "version": "1.0",
  "artifacts": {
    "analysis_products_q1.md": {
      "source_hash": "a3f8b2c1d4e5f6...",
      "content_hash": "9f8e7d6c5b4a3...",
      "path": "/percorso/assoluto/output/analysis_products_q1.md",
      "saved_at": "2026-05-08T10:30:00+00:00",
      "metadata": {}
    }
  }
}
```

**`source_hash`**: hash del **file di input** (il CSV). Cambia solo se cambia il CSV.  
**`content_hash`**: hash del **file di output** (il report). Per verificare integrità.

---

## 5. Skills — Come Scriverle Correttamente

### Cos'è una Skill

Una **skill** è uno strumento (tool) che rendi disponibile a Claude. Quando Claude incontra un problema che richiede accesso a dati esterni o esecuzione di codice, invoca uno dei tool che hai definito.

Una skill è composta da **due parti obbligatorie**:

1. **Definizione JSON** → descrive il tool a Claude (cosa fa, che parametri accetta).
2. **Implementazione Python** → esegue l'azione reale quando Claude la invoca.

### Struttura di una Definizione

```python
{
    "name": "nome_dello_strumento",          # snake_case, descrittivo
    "description": "Descrizione chiara...",  # Fondamentale! Claude legge questo
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",            # string, number, boolean, array, object
                "description": "Cosa rappresenta questo parametro."
            },
            "param2_opzionale": {
                "type": "number",
                "description": "Parametro opzionale."
            }
        },
        "required": ["param1"]               # Solo i parametri obbligatori
    }
}
```

### Regole d'Oro per le Skill

#### ✅ 1. Descrizioni chiare e complete

La `description` è il messaggio più importante: Claude decide **quando e come usare** la skill basandosi su di essa.

```python
# ❌ Scarso
"description": "Legge un file."

# ✅ Ottimo
"description": (
    "Legge il contenuto di un file di testo dal disco. "
    "Usa questo strumento per leggere file CSV, Markdown, JSON o testo. "
    "Restituisce il contenuto grezzo come stringa."
)
```

#### ✅ 2. Descrizioni dei parametri esplicite

```python
# ❌ Scarso
"filepath": {"type": "string", "description": "Il file."}

# ✅ Ottimo
"filepath": {
    "type": "string",
    "description": "Percorso relativo o assoluto al file da leggere."
}
```

#### ✅ 3. Output sempre stringhe

Il risultato di una skill deve essere sempre una stringa. Se restituisci dati strutturati, usa JSON:

```python
def execute_my_skill(tool_name: str, tool_input: dict) -> str:
    result = {"key": "value", "count": 42}
    return json.dumps(result, ensure_ascii=False)  # ← sempre stringa
```

#### ✅ 4. Errori con prefisso "ERROR:"

Segnala gli errori con un messaggio che inizia con `ERROR:`. L'agente base controlla questo prefisso per impostare `is_error=True` nel tool_result:

```python
def _read_file(filepath: str) -> str:
    if not Path(filepath).exists():
        return f"ERROR: File non trovato: '{filepath}'"  # ← prefisso standard
    ...
```

#### ✅ 5. Funzioni deterministiche

Le skill **devono essere deterministiche**: stesso input → stesso output. Questo è prerequisito per l'idempotenza.

```python
# ❌ Non deterministico
def get_stats(csv: str) -> str:
    return json.dumps({"timestamp": datetime.now().isoformat(), ...})

# ✅ Deterministico
def get_stats(csv: str) -> str:
    return json.dumps({"sum": 42, "mean": 14.0, ...})
```

#### ✅ 6. Sicurezza: prevenire path traversal

```python
def _safe_path(raw_path: str) -> Path:
    cwd = Path.cwd().resolve()
    resolved = (cwd / raw_path).resolve()
    resolved.relative_to(cwd)  # ValueError se fuori dalla CWD
    return resolved
```

### Pattern: SkillRegistry

Invece di passare le skill direttamente agli agenti, usa un registro centralizzato:

```python
registry = SkillRegistry(artifact_manager=manager)

# Tutte le definizioni per l'API
tools = registry.get_all_definitions()

# Dispatch automatico
result = registry.execute("read_text_file", {"filepath": "data/q1.csv"})
```

---

## 6. Artifacts — Gestione Idempotente degli Output

### Cos'è un Artifact

Un **artifact** è qualsiasi file prodotto da Claude (report, analisi, configurazioni, codice generato). L'`ArtifactManager` gestisce il ciclo di vita di questi file con garanzie di idempotenza.

### API dell'ArtifactManager

```python
from src.artifacts.manager import ArtifactManager

manager = ArtifactManager("output")  # directory di output

# 1. Calcola hash del contenuto sorgente
src_hash = manager.compute_hash(csv_content)

# 2. Controlla se serve rigenerare
if manager.is_stale("report_q1.md", src_hash):
    # 3. Genera il contenuto (costoso)
    content = ask_claude_to_analyze(csv_content)

    # 4. Salva l'artifact
    path = manager.save(
        artifact_id="report_q1.md",
        content=content,
        source_hash=src_hash,
        metadata={"quarter": "Q1", "type": "analysis"}
    )
    print(f"Salvato in: {path}")
else:
    print("Artifact già aggiornato, skip!")
    content = manager.load("report_q1.md")
```

### Operazioni disponibili

| Metodo | Descrizione |
|--------|-------------|
| `compute_hash(content)` | SHA-256 del contenuto (statico) |
| `is_stale(id, src_hash)` | True se va rigenerato |
| `save(id, content, src_hash)` | Salva atomicamente |
| `load(id)` | Legge il contenuto |
| `get_info(id)` | Metadati dal registro |
| `list_artifacts()` | Tutti gli ID registrati |
| `invalidate(id)` | Forza rigenerazione al prossimo run |
| `delete(id)` | Elimina file e registro |

### Scrittura Atomica

`ArtifactManager.save()` usa scrittura atomica: scrive su un file `.tmp` e poi lo rinomina. Questo garantisce che il file sia sempre completo o assente, mai corrotto a metà scrittura:

```python
# Internamente:
tmp_path = artifact_path.with_suffix(".tmp")
with open(tmp_path, "w") as fh:
    fh.write(content)
tmp_path.replace(artifact_path)  # ← operazione atomica sul filesystem
```

### Skill per gli Artifact

Claude può interagire con gli artifact tramite le **artifact skills**:

```python
# Claude verifica se deve rigenerare
check_artifact_status(
    artifact_id="analysis_q1.md",
    source_content=csv_content    # Claude calcola internamente l'hash
)
# → {"status": "fresh"} oppure {"status": "stale"}

# Claude salva il report appena generato
save_artifact(
    artifact_id="analysis_q1.md",
    content="# Report Q1\n...",
    source_content=csv_content
)

# Claude carica un artifact esistente
load_artifact(artifact_id="analysis_q1.md")
```

---

## 7. Agents — Il Loop di Tool-Use

### Il Protocollo Tool-Use di Anthropic

Quando Claude riceve una lista di tool, può decidere di **invocare** uno o più tool invece di rispondere direttamente. Il flusso è:

```
Client                          Claude API
  │                                │
  │  messages + tools ────────────→│
  │                                │  (Claude ragiona)
  │  ←─────────── tool_use blocks  │
  │                                │
  │  (client esegue i tool)        │
  │                                │
  │  tool_results ────────────────→│
  │                                │  (Claude continua il ragionamento)
  │  ←─────────── end_turn (text)  │
  │                                │
```

### Il Loop in Python

```python
messages = [{"role": "user", "content": "Analizza il file data/q1.csv"}]
tools = registry.get_all_definitions()

while True:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system="Sei un analista dati...",
        tools=tools,
        messages=messages,
    )

    # Aggiungi la risposta alla cronologia
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason == "end_turn":
        # Claude ha finito → estrai il testo
        return extract_text(response.content)

    if response.stop_reason == "tool_use":
        # Esegui i tool richiesti da Claude
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = registry.execute(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                    "is_error": result.startswith("ERROR:"),
                })
        messages.append({"role": "user", "content": tool_results})
```

### Struttura degli Agenti nel Progetto

```
BaseAgent (loop tool-use)
    │
    ├── DataAnalystAgent
    │     system_prompt: "Sei un analista dati..."
    │     skill_groups:  ["file", "data", "artifact"]
    │     run(csv_filepath) → str (report Markdown)
    │
    └── ReportWriterAgent
          system_prompt: "Sei un business analyst..."
          skill_groups:  ["artifact"]
          run(analysis_ids) → str (summary Markdown)

OrchestratorAgent (puro Python, NO loop Claude)
    │
    ├── Elenca CSV in data/
    ├── Per ogni CSV → verifica is_stale() → DataAnalystAgent (se stale)
    └── ReportWriterAgent (per la sintesi finale)
```

### System Prompt: Istruzioni Operative

Il `system_prompt` deve descrivere **esattamente** il comportamento atteso, inclusa la logica di idempotenza. Esempio da `DataAnalystAgent`:

```python
system_prompt = """Sei un analista dati esperto.

ISTRUZIONI:
1. Usa 'check_artifact_status' per verificare se l'analisi esiste già.
   Se status è 'fresh' → carica con load_artifact, NON rigenerare.

2. Se è 'stale':
   a. Leggi il file CSV con 'read_text_file'
   b. Analizza con 'parse_csv_schema' e 'compute_column_stats'
   c. Scrivi il report Markdown
   d. Salva con 'save_artifact'

3. Restituisci SEMPRE il contenuto del report.
"""
```

**Regola**: il system prompt deve specificare il flusso passo per passo. Claude seguirà le istruzioni ordinatamente.

### Quando usare Claude vs puro Python

| Situazione | Usa Claude | Usa Python |
|------------|-----------|------------|
| Ragionamento adattivo sui dati | ✅ | |
| Scrittura di testo (report, analisi) | ✅ | |
| Loop deterministico (for, if) | | ✅ |
| Chiamate API a servizi esterni | | ✅ |
| Ordinamento/aggregazione numerica | | ✅ |
| Coordinamento orchestrazione | | ✅ |

> L'`OrchestratorAgent` è Python puro proprio perché la sua logica è deterministica.

---

## 8. Installazione e Configurazione

### Step 1: Clona / apri il progetto

```powershell
# Se il progetto è su Git
git clone <url-repository> C001
cd C001

# Se è già in locale (questo caso)
cd "d:\Temp\Claude_Docs\C001"
```

### Step 2: Crea un ambiente virtuale Python

```powershell
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

> Dopo l'attivazione, il prompt dovrebbe mostrare `(.venv)`.

### Step 3: Installa le dipendenze

```powershell
pip install -r requirements.txt
```

Output atteso:
```
Successfully installed anthropic-0.40.x python-dotenv-1.0.x ...
```

### Step 4: Configura le variabili d'ambiente

```powershell
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

Modifica `.env` con un editor di testo:

```ini
ANTHROPIC_API_KEY=sk-ant-api03-TUA-CHIAVE-QUI
CLAUDE_MODEL=claude-opus-4-5
DATA_DIR=data
OUTPUT_DIR=output
```

### Step 5: Verifica l'installazione

```powershell
python -c "import anthropic; print('anthropic OK')"
python -c "from src.artifacts.manager import ArtifactManager; print('src OK')"
```

---

## 9. Esecuzione della Pipeline

### Primo avvio (processa tutto)

```powershell
python -m src.pipeline
```

Output atteso:
```
[Orchestrator] Trovati 3 file CSV
[Orchestrator] Avvio analisi individuali...

[DataAnalystAgent] Analisi: data/products_q1.csv
  Artifact target: analysis_products_q1.md
  → Tool invocato: check_artifact_status([...])
  → Tool invocato: read_text_file([...])
  → Tool invocato: parse_csv_schema([...])
  → Tool invocato: compute_column_stats([...])
  → Tool invocato: aggregate_by_category([...])
  → Tool invocato: save_artifact([...])

[DataAnalystAgent] Analisi: data/products_q2.csv
  ...
[DataAnalystAgent] Analisi: data/products_q3.csv
  ...

[ReportWriterAgent] Generazione report di sintesi...
  ...

============================================================
PIPELINE RESULT
============================================================
  Data dir      : data
  File totali   : 3
  Processati    : 3
  Saltati (ok)  : 0  ← idempotenza
  Falliti       : 0
  Report finale : summary_report.md
  Tempo         : 45.2s
============================================================
```

### Secondo avvio (idempotenza in azione)

```powershell
python -m src.pipeline
```

Output atteso:
```
[Orchestrator] Trovati 3 file CSV

[Orchestrator] SKIP products_q1.csv — artifact aggiornato
[Orchestrator] SKIP products_q2.csv — artifact aggiornato
[Orchestrator] SKIP products_q3.csv — artifact aggiornato

[ReportWriterAgent] Generazione report di sintesi...
  → Tool invocato: check_artifact_status([...])
  (status: fresh — skip)

============================================================
PIPELINE RESULT
============================================================
  Processati    : 0
  Saltati (ok)  : 3  ← tutti saltati!
  Tempo         : 2.1s  ← molto più veloce!
============================================================
```

### Vedere gli artifact registrati

```powershell
python -m src.pipeline list
```

Output:
```
ID Artifact                         Salvato il                 Source Hash
------------------------------------------------------------------------------------
analysis_products_q1.md             2026-05-08T10:30:00        a3f8b2c1d4e5...
analysis_products_q2.md             2026-05-08T10:31:15        b4c9d3e2f1a0...
analysis_products_q3.md             2026-05-08T10:32:40        c5d0e4f3g2b1...
summary_report.md                   2026-05-08T10:34:05        x1y2z3a4b5c6...
```

### Forzare la rigenerazione di un artifact

```powershell
# Invalida uno specifico artifact
python -m src.pipeline invalidate analysis_products_q2

# Ora riesegui: solo q2 verrà rielaborato
python -m src.pipeline
```

### Reset completo

```powershell
python -m src.pipeline reset
python -m src.pipeline   # tutto verrà rielaborato
```

### Aggiungere un nuovo file CSV

```powershell
# Copia un CSV nella directory data/
Copy-Item "nuovo_file.csv" data/

# Riesegui: processa solo il nuovo file
python -m src.pipeline
```

---

## 10. Eseguire i Test

I test **non richiedono API key** perché testano solo le componenti Python (ArtifactManager, skill deterministiche).

### Tutti i test

```powershell
python -m pytest tests/ -v
```

### Solo i test di idempotenza

```powershell
python -m pytest tests/test_artifact_manager.py -v -k "Idempotency"
```

### Solo i test delle skill

```powershell
python -m pytest tests/test_skills.py -v
```

### Output atteso

```
tests/test_artifact_manager.py::TestHashing::test_same_content_same_hash PASSED
tests/test_artifact_manager.py::TestHashing::test_different_content_different_hash PASSED
tests/test_artifact_manager.py::TestIsStale::test_new_artifact_is_stale PASSED
tests/test_artifact_manager.py::TestIsStale::test_fresh_artifact_not_stale PASSED
tests/test_artifact_manager.py::TestIdempotencyEndToEnd::test_pipeline_skip_count PASSED
...
tests/test_skills.py::TestSkillDefinitions::test_file_skills_have_required_fields PASSED
tests/test_skills.py::TestDataSkills::test_data_skills_are_deterministic PASSED
...
================ 30 passed in 0.8s ================
```

---

## 11. Estendere il Progetto

### Aggiungere una nuova Skill

**Step 1**: crea la definizione e l'implementazione in un nuovo file `src/skills/my_skills.py`:

```python
def get_my_skill_definitions():
    return [{
        "name": "fetch_exchange_rate",
        "description": "Recupera il tasso di cambio EUR/USD attuale.",
        "input_schema": {
            "type": "object",
            "properties": {
                "from_currency": {"type": "string"},
                "to_currency": {"type": "string"},
            },
            "required": ["from_currency", "to_currency"],
        }
    }]

def execute_my_skill(tool_name: str, tool_input: dict) -> str:
    if tool_name == "fetch_exchange_rate":
        # implementazione...
        return json.dumps({"rate": 1.08})
    return f"ERROR: Skill sconosciuta: {tool_name}"
```

**Step 2**: registrala in `SkillRegistry`:

```python
# src/skills/registry.py — aggiungi al metodo get_all_definitions()
from .my_skills import get_my_skill_definitions, execute_my_skill

if "my_group" in self._enabled:
    definitions.extend(get_my_skill_definitions())
```

**Step 3**: aggiorna il dispatcher in `SkillRegistry.execute()`:

```python
if group == "my_group":
    return execute_my_skill(tool_name, tool_input)
```

### Aggiungere un nuovo Agente

```python
# src/agents/my_agent.py
from .base_agent import BaseAgent

class MyAgent(BaseAgent):
    system_prompt = """Sei un esperto di...

ISTRUZIONI:
1. Prima controlla se l'artifact è aggiornato con check_artifact_status.
2. ...
"""

    def run(self, input_data: str) -> str:
        return self._run_loop(f"Elabora: {input_data}")
```

### Tipi di Artifact Supportati

L'`ArtifactManager` supporta qualsiasi tipo di file testuale:

```python
# Report Markdown
manager.save("report.md", markdown_content, src_hash)

# Dati JSON strutturati
manager.save("data.json", json.dumps(data), src_hash)

# Codice generato
manager.save("script.py", python_code, src_hash)

# File di configurazione
manager.save("config.yaml", yaml_content, src_hash)
```

### Gestire Artifact Binari

Per file binari (immagini, PDF), estendi `ArtifactManager` con supporto bytes:

```python
def save_binary(self, artifact_id: str, data: bytes, source_hash: str) -> str:
    artifact_path = self.output_dir / artifact_id
    tmp = artifact_path.with_suffix(".tmp")
    try:
        tmp.write_bytes(data)
        tmp.replace(artifact_path)
    except Exception:
        if tmp.exists(): tmp.unlink()
        raise
    # Aggiorna registro...
```

---

## 12. Errori Comuni e Soluzioni

### ❌ `ANTHROPIC_API_KEY not set`

```
ERRORE: La variabile ANTHROPIC_API_KEY non è impostata.
```

**Soluzione:**
```powershell
Copy-Item .env.example .env
# Modifica .env con la tua chiave API
```

### ❌ `ModuleNotFoundError: No module named 'src'`

```
ModuleNotFoundError: No module named 'src'
```

**Soluzione:** esegui il comando dalla root del progetto (dove si trova la cartella `src/`):
```powershell
cd "d:\Temp\Claude_Docs\C001"
python -m src.pipeline
```

### ❌ `anthropic.AuthenticationError`

La chiave API non è valida o è scaduta.

**Soluzione:** verifica la chiave su [console.anthropic.com](https://console.anthropic.com/settings/keys).

### ❌ `anthropic.RateLimitError`

Hai superato il limite di richieste al minuto.

**Soluzione:** attendi qualche secondo e riprova. Considera di ridurre la concorrenza.

### ❌ Artifact sempre stale

Se ogni esecuzione rigenera gli artifact, verifica che:
1. Il file CSV non venga modificato da un altro processo (es. Excel che aggiunge metadata).
2. L'encoding sia consistente (usa sempre `utf-8`).
3. La directory `output/` non sia in sola lettura.

```powershell
# Debug: verifica l'hash manualmente
python -c "
from src.artifacts.manager import ArtifactManager
m = ArtifactManager()
import pathlib
content = pathlib.Path('data/products_q1.csv').read_text(encoding='utf-8')
print('Hash attuale:', m.compute_hash(content))
info = m.get_info('analysis_products_q1.md')
print('Hash salvato:', info.get('source_hash') if info else 'N/A')
"
```

### ❌ `ValueError: Path non consentito`

Le skill di file bloccano path traversal fuori dalla CWD.

**Soluzione:** usa percorsi relativi dalla directory del progetto:
```python
# ❌ Percorso assoluto esterno
{"filepath": "C:/Users/utente/Desktop/mio_file.csv"}

# ✅ Percorso relativo alla CWD del progetto
{"filepath": "data/products_q1.csv"}
```

---

## Riepilogo dei Concetti Chiave

| Concetto | Dove | Ruolo |
|----------|------|-------|
| **Skill** | `src/skills/` | Tool che Claude può invocare; definizione JSON + implementazione Python |
| **SkillRegistry** | `src/skills/registry.py` | Raccoglie e dispatcha tutte le skill |
| **Artifact** | `output/*.md`, `output/artifacts.json` | File generati da Claude con tracking dell'hash |
| **ArtifactManager** | `src/artifacts/manager.py` | Gestisce il ciclo di vita degli artifact con idempotenza SHA-256 |
| **BaseAgent** | `src/agents/base_agent.py` | Implementa il loop tool-use dell'API Anthropic |
| **DataAnalystAgent** | `src/agents/data_analyst_agent.py` | Agente specializzato, eredita da BaseAgent |
| **OrchestratorAgent** | `src/agents/orchestrator_agent.py` | Coordinamento Python puro, no Claude |
| **Idempotenza** | Ovunque | `is_stale()` → processa solo se l'input è cambiato |
