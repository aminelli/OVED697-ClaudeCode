# Comando: /review-pr

Avvia la pipeline completa di code review per una Pull Request.
Invoca i tre sub-agent in parallelo, poi aggrega i risultati in un report finale.

## Utilizzo

```
/review-pr <pr-id>
```

**Esempi:**
```
/review-pr pr-42
/review-pr pr-107
```

## Prerequisiti

Il file diff deve esistere in `pr-diffs/<pr-id>.diff`.
Per generarne uno da git: `git diff main...feature-branch > pr-diffs/pr-42.diff`

## Passi da eseguire

### 1. Verifica input

```python
import sys
from pathlib import Path
pr_id = "<pr-id>"
diff_file = Path(f"pr-diffs/{pr_id}.diff")
if not diff_file.exists():
    print(f"❌ Diff non trovato: {diff_file}")
    sys.exit(1)
print(f"✅ Diff trovato: {diff_file} ({diff_file.stat().st_size} bytes)")
```

### 2. Lancia i tre sub-agent IN PARALLELO

Usa il tool `Task` tre volte contemporaneamente con questi prompt:

**Task 1 — security-agent:**
```
Sei il security-agent. Leggi le tue istruzioni complete in agents/security-agent.md.
Analizza il diff in pr-diffs/<pr-id>.diff.
Scrivi il tuo artifact review-comment in artifacts/comments/<pr-id>_security.md.
Registra l'artifact in artifacts/manifests/artifact-registry.json.
```

**Task 2 — performance-agent:**
```
Sei il performance-agent. Leggi le tue istruzioni complete in agents/performance-agent.md.
Analizza il diff in pr-diffs/<pr-id>.diff.
Scrivi il tuo artifact review-comment in artifacts/comments/<pr-id>_performance.md.
Registra l'artifact in artifacts/manifests/artifact-registry.json.
```

**Task 3 — style-agent:**
```
Sei lo style-agent. Leggi le tue istruzioni complete in agents/style-agent.md.
Analizza il diff in pr-diffs/<pr-id>.diff.
Scrivi il tuo artifact review-comment in artifacts/comments/<pr-id>_style.md.
Registra l'artifact in artifacts/manifests/artifact-registry.json.
```

### 3. Verifica completamento sub-agent

```bash
python scripts/check_comments.py --pr-id <pr-id>
```

Se un artifact manca: rilancia il Task corrispondente (max 1 retry).

### 4. Aggrega i risultati

```bash
python scripts/aggregate_reviews.py --pr-id <pr-id>
```

Output: `artifacts/reports/review_<pr-id>.md`

### 5. Mostra il risultato all'utente

Presenta il verdetto e il riepilogo. Esempio:

```
═══════════════════════════════════════
  PR Review: pr-42
  Verdetto: ⚠️  REQUEST_CHANGES
═══════════════════════════════════════

  🔴 Security   — 0 critical, 1 high, 2 medium
  🟡 Performance — 0 critical, 0 high, 3 medium
  🔵 Style      — 0 critical, 0 high, 1 medium, 4 low

  Report completo: artifacts/reports/review_pr-42.md
═══════════════════════════════════════
```

## Output atteso

- ✅ `artifacts/comments/<pr-id>_security.md`    (artifact: review-comment)
- ✅ `artifacts/comments/<pr-id>_performance.md` (artifact: review-comment)
- ✅ `artifacts/comments/<pr-id>_style.md`       (artifact: review-comment)
- ✅ `artifacts/reports/review_<pr-id>.md`       (artifact: review-report)
- ✅ Tutti e 4 registrati in `artifact-registry.json`
