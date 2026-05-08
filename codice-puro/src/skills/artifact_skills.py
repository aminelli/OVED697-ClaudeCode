"""
Artifact Skills — skill che espongono l'ArtifactManager a Claude.

Claude può usare queste skill per:
- Verificare se un artifact esiste già e non è "stale"
- Salvare un artifact appena generato
- Caricare un artifact precedentemente salvato
- Elencare tutti gli artifact esistenti

In questo modo Claude partecipa attivamente alla logica di idempotenza:
può decidere autonomamente di skippare la generazione se l'artifact
è già aggiornato.
"""

import json
from typing import Any, Dict, List, Optional

from src.artifacts.manager import ArtifactManager


# ---------------------------------------------------------------------------
# Definizioni
# ---------------------------------------------------------------------------

def get_artifact_skill_definitions() -> List[Dict[str, Any]]:
    """Restituisce le definizioni degli strumenti per la gestione degli artifact."""
    return [
        {
            "name": "check_artifact_status",
            "description": (
                "Controlla se un artifact esiste già ed è aggiornato rispetto "
                "al contenuto sorgente. Restituisce 'fresh' se l'artifact è "
                "già valido (puoi saltare la generazione) oppure 'stale' se "
                "deve essere rigenerato."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": (
                            "Identificatore univoco dell'artifact "
                            "(es. 'report_q1.md', 'summary.json')."
                        ),
                    },
                    "source_content": {
                        "type": "string",
                        "description": (
                            "Il contenuto sorgente da cui si genererebbe l'artifact. "
                            "Usato per calcolare l'hash e confrontarlo con quello salvato."
                        ),
                    },
                },
                "required": ["artifact_id", "source_content"],
            },
        },
        {
            "name": "save_artifact",
            "description": (
                "Salva un artifact generato su disco con il suo hash sorgente. "
                "Usa questa skill dopo aver generato il contenuto dell'artifact. "
                "La scrittura è atomica: o va a buon fine o non lascia file corrotti."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "Identificatore univoco dell'artifact.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Contenuto da salvare nell'artifact.",
                    },
                    "source_content": {
                        "type": "string",
                        "description": "Il contenuto sorgente originale (per calcolare l'hash).",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Metadati opzionali da associare all'artifact (es. titolo, tipo).",
                    },
                },
                "required": ["artifact_id", "content", "source_content"],
            },
        },
        {
            "name": "load_artifact",
            "description": (
                "Carica il contenuto di un artifact già salvato. "
                "Utile per leggere artifact precedentemente generati "
                "come input per nuove elaborazioni."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "Identificatore univoco dell'artifact da caricare.",
                    }
                },
                "required": ["artifact_id"],
            },
        },
        {
            "name": "list_artifacts",
            "description": (
                "Elenca tutti gli artifact presenti nel registro. "
                "Restituisce un array JSON con gli ID e i metadati essenziali."
            ),
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    ]


# ---------------------------------------------------------------------------
# Dispatcher (closure con manager iniettato)
# ---------------------------------------------------------------------------

def make_artifact_skill_executor(manager: ArtifactManager):
    """
    Factory che restituisce un executor pre-configurato con l'ArtifactManager.
    Uso della closure per iniettare la dipendenza senza variabili globali.

    Esempio:
        manager = ArtifactManager("output")
        execute = make_artifact_skill_executor(manager)
        result = execute("check_artifact_status", {...})
    """

    def execute_artifact_skill(tool_name: str, tool_input: Dict[str, Any]) -> str:
        if tool_name == "check_artifact_status":
            return _check_status(manager, tool_input)
        if tool_name == "save_artifact":
            return _save(manager, tool_input)
        if tool_name == "load_artifact":
            return _load(manager, tool_input)
        if tool_name == "list_artifacts":
            return _list(manager)
        return f"ERROR: Artifact skill sconosciuta: '{tool_name}'"

    return execute_artifact_skill


# Executor standalone (usa un manager di default) — utile per test rapidi
def execute_artifact_skill(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Executor di fallback: usa ArtifactManager("output")."""
    mgr = ArtifactManager("output")
    executor = make_artifact_skill_executor(mgr)
    return executor(tool_name, tool_input)


# ---------------------------------------------------------------------------
# Implementazioni private
# ---------------------------------------------------------------------------

def _check_status(manager: ArtifactManager, tool_input: Dict[str, Any]) -> str:
    artifact_id: str = tool_input["artifact_id"]
    source_hash = manager.compute_hash(tool_input["source_content"])
    stale = manager.is_stale(artifact_id, source_hash)
    info = manager.get_info(artifact_id)

    result = {
        "artifact_id": artifact_id,
        "status": "stale" if stale else "fresh",
        "source_hash": source_hash,
        "existing_info": info,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def _save(manager: ArtifactManager, tool_input: Dict[str, Any]) -> str:
    artifact_id: str = tool_input["artifact_id"]
    content: str = tool_input["content"]
    source_hash = manager.compute_hash(tool_input["source_content"])
    metadata: Optional[Dict] = tool_input.get("metadata")

    saved_path = manager.save(artifact_id, content, source_hash, metadata)
    result = {
        "artifact_id": artifact_id,
        "saved_path": saved_path,
        "source_hash": source_hash,
        "content_hash": manager.compute_hash(content),
        "status": "saved",
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def _load(manager: ArtifactManager, tool_input: Dict[str, Any]) -> str:
    artifact_id: str = tool_input["artifact_id"]
    content = manager.load(artifact_id)
    if content is None:
        return json.dumps({"artifact_id": artifact_id, "status": "not_found"})
    return json.dumps(
        {"artifact_id": artifact_id, "status": "found", "content": content},
        ensure_ascii=False,
    )


def _list(manager: ArtifactManager) -> str:
    artifacts = manager.list_artifacts()
    details = []
    for aid in artifacts:
        info = manager.get_info(aid) or {}
        details.append(
            {
                "artifact_id": aid,
                "saved_at": info.get("saved_at"),
                "metadata": info.get("metadata", {}),
            }
        )
    return json.dumps({"count": len(details), "artifacts": details}, ensure_ascii=False, indent=2)
