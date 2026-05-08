"""
Data Skills — skill per analisi e trasformazione di dati CSV.

Queste skill permettono a Claude di:
- Analizzare la struttura di un CSV (colonne, tipi)
- Calcolare statistiche descrittive
- Aggregare dati per categoria

Tutte le funzioni sono deterministiche: stesso input → stesso output.
Questo è fondamentale per garantire l'idempotenza della pipeline.
"""

import csv
import io
import json
import statistics
from typing import Any, Dict, List, Tuple


# ---------------------------------------------------------------------------
# Definizioni
# ---------------------------------------------------------------------------

def get_data_skill_definitions() -> List[Dict[str, Any]]:
    """Restituisce le definizioni degli strumenti di analisi dati."""
    return [
        {
            "name": "parse_csv_schema",
            "description": (
                "Analizza un contenuto CSV e restituisce lo schema: "
                "nomi delle colonne, tipi rilevati e numero di righe. "
                "Utile prima di eseguire analisi più profonde."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "csv_content": {
                        "type": "string",
                        "description": "Contenuto grezzo del file CSV come stringa.",
                    }
                },
                "required": ["csv_content"],
            },
        },
        {
            "name": "compute_column_stats",
            "description": (
                "Calcola statistiche descrittive (min, max, media, mediana, totale) "
                "per una colonna numerica di un CSV. "
                "Restituisce un oggetto JSON con le statistiche."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "csv_content": {
                        "type": "string",
                        "description": "Contenuto grezzo del file CSV.",
                    },
                    "column_name": {
                        "type": "string",
                        "description": "Nome della colonna da analizzare.",
                    },
                },
                "required": ["csv_content", "column_name"],
            },
        },
        {
            "name": "aggregate_by_category",
            "description": (
                "Raggruppa i dati CSV per una colonna categorica e somma "
                "una colonna numerica per ciascun gruppo. "
                "Es.: somma dei ricavi per categoria di prodotto."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "csv_content": {
                        "type": "string",
                        "description": "Contenuto grezzo del file CSV.",
                    },
                    "group_column": {
                        "type": "string",
                        "description": "Colonna da usare come chiave di raggruppamento.",
                    },
                    "value_column": {
                        "type": "string",
                        "description": "Colonna numerica da sommare per ogni gruppo.",
                    },
                },
                "required": ["csv_content", "group_column", "value_column"],
            },
        },
    ]


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def execute_data_skill(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Esegue la skill dati indicata e restituisce il risultato JSON."""
    if tool_name == "parse_csv_schema":
        return _parse_csv_schema(tool_input["csv_content"])
    if tool_name == "compute_column_stats":
        return _compute_column_stats(
            tool_input["csv_content"], tool_input["column_name"]
        )
    if tool_name == "aggregate_by_category":
        return _aggregate_by_category(
            tool_input["csv_content"],
            tool_input["group_column"],
            tool_input["value_column"],
        )
    return f"ERROR: Skill dati sconosciuta: '{tool_name}'"


# ---------------------------------------------------------------------------
# Implementazioni
# ---------------------------------------------------------------------------

def _read_csv_rows(csv_content: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """Parsifica il CSV e restituisce (headers, rows)."""
    reader = csv.DictReader(io.StringIO(csv_content.strip()))
    headers = reader.fieldnames or []
    rows = list(reader)
    return list(headers), rows


def _parse_csv_schema(csv_content: str) -> str:
    try:
        headers, rows = _read_csv_rows(csv_content)
    except Exception as exc:
        return f"ERROR: Impossibile parsificare il CSV: {exc}"

    # Rileva tipo di ogni colonna (numerico vs testo)
    column_types: Dict[str, str] = {}
    for col in headers:
        values = [r[col] for r in rows if col in r and r[col].strip()]
        numeric_count = sum(1 for v in values if _is_numeric(v))
        column_types[col] = "numeric" if numeric_count > len(values) * 0.8 else "text"

    schema = {
        "columns": headers,
        "column_types": column_types,
        "row_count": len(rows),
        "has_header": True,
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def _compute_column_stats(csv_content: str, column_name: str) -> str:
    try:
        headers, rows = _read_csv_rows(csv_content)
    except Exception as exc:
        return f"ERROR: Impossibile parsificare il CSV: {exc}"

    if column_name not in headers:
        return f"ERROR: Colonna '{column_name}' non trovata. Colonne disponibili: {headers}"

    values: List[float] = []
    for row in rows:
        raw = row.get(column_name, "").strip()
        if raw and _is_numeric(raw):
            values.append(float(raw.replace(",", "")))

    if not values:
        return f"ERROR: Nessun valore numerico in '{column_name}'"

    stats = {
        "column": column_name,
        "count": len(values),
        "sum": round(sum(values), 2),
        "mean": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "stdev": round(statistics.stdev(values), 2) if len(values) > 1 else 0.0,
    }
    return json.dumps(stats, ensure_ascii=False, indent=2)


def _aggregate_by_category(
    csv_content: str, group_column: str, value_column: str
) -> str:
    try:
        headers, rows = _read_csv_rows(csv_content)
    except Exception as exc:
        return f"ERROR: Impossibile parsificare il CSV: {exc}"

    for col in (group_column, value_column):
        if col not in headers:
            return f"ERROR: Colonna '{col}' non trovata. Colonne: {headers}"

    aggregated: Dict[str, float] = {}
    for row in rows:
        key = row.get(group_column, "N/A").strip()
        raw_val = row.get(value_column, "0").strip()
        val = float(raw_val.replace(",", "")) if _is_numeric(raw_val) else 0.0
        aggregated[key] = aggregated.get(key, 0.0) + val

    # Ordina per valore decrescente (deterministico)
    result = {
        "group_column": group_column,
        "value_column": value_column,
        "aggregation": "sum",
        "groups": [
            {"category": k, "total": round(v, 2)}
            for k, v in sorted(aggregated.items(), key=lambda x: -x[1])
        ],
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def _is_numeric(value: str) -> bool:
    try:
        float(value.replace(",", ""))
        return True
    except ValueError:
        return False
