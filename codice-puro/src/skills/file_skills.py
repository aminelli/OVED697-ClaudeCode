"""
File Skills — skill per operazioni su file system.

Ogni skill ha:
- Una definizione JSON che Claude riceve per capire come usarla.
- Un'implementazione Python che viene eseguita quando Claude la invoca.

Principio di sicurezza: nessuna skill accede a percorsi fuori dalla
directory di lavoro del progetto (path traversal prevention).
"""

import os
from pathlib import Path
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Definizioni — descrivono le skill a Claude
# ---------------------------------------------------------------------------

def get_file_skill_definitions() -> List[Dict[str, Any]]:
    """
    Restituisce le definizioni degli strumenti per operazioni su file.
    Queste vengono passate all'API Anthropic nel campo `tools`.
    """
    return [
        {
            "name": "read_text_file",
            "description": (
                "Legge il contenuto di un file di testo dal disco. "
                "Usa questo strumento per leggere file CSV, Markdown, JSON o testo. "
                "Restituisce il contenuto grezzo come stringa."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Percorso relativo o assoluto al file da leggere.",
                    }
                },
                "required": ["filepath"],
            },
        },
        {
            "name": "list_directory",
            "description": (
                "Elenca i file presenti in una directory. "
                "Usa questo strumento per scoprire quali file sono disponibili "
                "prima di decidere quali leggere. "
                "Opzionalmente filtra per estensione (es. '.csv')."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Percorso della directory da elencare.",
                    },
                    "extension": {
                        "type": "string",
                        "description": (
                            "Estensione per filtrare i file (es. '.csv', '.md'). "
                            "Ometti per elencare tutti i file."
                        ),
                    },
                },
                "required": ["directory"],
            },
        },
    ]


# ---------------------------------------------------------------------------
# Implementazioni — eseguono l'azione reale
# ---------------------------------------------------------------------------

def execute_file_skill(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """
    Esegue la skill file indicata e restituisce il risultato come stringa.
    In caso di errore restituisce un messaggio che inizia con 'ERROR:'.
    """
    if tool_name == "read_text_file":
        return _read_text_file(tool_input["filepath"])
    if tool_name == "list_directory":
        return _list_directory(
            tool_input["directory"],
            tool_input.get("extension", ""),
        )
    return f"ERROR: Skill file sconosciuta: '{tool_name}'"


def _safe_path(raw_path: str) -> Path:
    """
    Risolve il percorso e impedisce il path traversal fuori dalla CWD.
    Solleva ValueError se il percorso punta fuori dalla working directory.
    """
    cwd = Path.cwd().resolve()
    resolved = (cwd / raw_path).resolve()
    # Sicurezza: il percorso deve essere dentro la CWD
    resolved.relative_to(cwd)  # solleva ValueError se fuori
    return resolved


def _read_text_file(filepath: str) -> str:
    try:
        path = _safe_path(filepath)
    except ValueError:
        return f"ERROR: Percorso non consentito: '{filepath}'"

    if not path.exists():
        return f"ERROR: File non trovato: '{filepath}'"
    if not path.is_file():
        return f"ERROR: Il percorso non è un file: '{filepath}'"

    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        return f"ERROR: Impossibile leggere il file: {exc}"


def _list_directory(directory: str, extension: str = "") -> str:
    try:
        path = _safe_path(directory)
    except ValueError:
        return f"ERROR: Percorso non consentito: '{directory}'"

    if not path.exists():
        return f"ERROR: Directory non trovata: '{directory}'"
    if not path.is_dir():
        return f"ERROR: Il percorso non è una directory: '{directory}'"

    files = sorted(
        f.name
        for f in path.iterdir()
        if f.is_file() and (not extension or f.suffix == extension)
    )
    if not files:
        return f"Nessun file trovato in '{directory}'" + (
            f" con estensione '{extension}'" if extension else ""
        )
    return "\n".join(files)
