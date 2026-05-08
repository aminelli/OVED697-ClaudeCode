# Claude Code — Skills, Artifacts & Agents (con Idempotenza)

Progetto didattico completo che mostra come costruire una **pipeline AI idempotente** con l'API Claude di Anthropic.

## Scenario

Pipeline di analisi dati di vendita:
- Legge file CSV trimestrali
- Genera report di analisi per ciascun trimestre (Markdown)
- Produce un report di sintesi comparativa finale
- **Rigenera solo i report i cui dati sono cambiati** (idempotenza SHA-256)

## Avvio rapido

```powershell
# 1. Crea ambiente virtuale
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
# source .venv/bin/activate       # macOS/Linux

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Configura API key
Copy-Item .env.example .env
# Modifica .env: ANTHROPIC_API_KEY=sk-ant-...

# 4. Esegui la pipeline
python -m src.pipeline

# 5. Seconda esecuzione: 0 chiamate API (idempotenza!)
python -m src.pipeline

# 6. Elenca artifact generati
python -m src.pipeline list

# 7. Forza ricalcolo di un artifact
python -m src.pipeline invalidate analysis_products_q2

# 8. Esegui i test (no API key necessaria)
python -m pytest tests/ -v
```

## Struttura

```
src/
  artifacts/manager.py      — ArtifactManager (idempotenza SHA-256)
  skills/                   — Tool definiti per Claude
    file_skills.py          — read_text_file, list_directory
    data_skills.py          — parse_csv_schema, compute_column_stats, aggregate_by_category
    artifact_skills.py      — check_artifact_status, save_artifact, load_artifact
    registry.py             — SkillRegistry (dispatcher)
  agents/
    base_agent.py           — Loop tool-use Anthropic
    data_analyst_agent.py   — Analisi CSV individuale
    report_writer_agent.py  — Sintesi comparativa
    orchestrator_agent.py   — Coordinamento Python puro
  pipeline.py               — CLI entry point
tests/
  test_artifact_manager.py  — Test idempotenza
  test_skills.py            — Test skill deterministiche
```

## Guida completa

Leggi [GUIDE.md](GUIDE.md) per la spiegazione dettagliata in italiano di tutti i concetti.
