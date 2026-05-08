"""
ArtifactManager — cuore dell'idempotenza del progetto.

Un artifact è un file generato da Claude (report, analisi, ecc.).
La logica è content-addressed: si rigenera SOLO se il contenuto
sorgente è cambiato (hash SHA-256 diverso).

Flusso idempotente:
  1. Calcola hash(source_content)
  2. Cerca artifact_id nel registro
  3. Se source_hash corrisponde → restituisce il file esistente (SKIP)
  4. Se diverso o assente    → genera, salva atomicamente, aggiorna registro
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class ArtifactManager:
    """
    Gestisce il ciclo di vita degli artifact con idempotenza basata su hash.

    Esempio d'uso:
        manager = ArtifactManager("output")
        src_hash = manager.compute_hash(csv_content)

        if manager.is_stale("report_q1.md", src_hash):
            content = generate_report(csv_content)          # costoso
            manager.save("report_q1.md", content, src_hash)
        else:
            print("Report già aggiornato, skip.")
    """

    REGISTRY_FILENAME = "artifacts.json"

    def __init__(self, output_dir: str = "output") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path = self.output_dir / self.REGISTRY_FILENAME
        self._registry: Dict[str, Any] = self._load_registry()

    # ------------------------------------------------------------------
    # Registry persistence
    # ------------------------------------------------------------------

    def _load_registry(self) -> Dict[str, Any]:
        """Carica il registro da disco; crea uno vuoto se assente."""
        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        return {"version": "1.0", "artifacts": {}}

    def _save_registry(self) -> None:
        """Persiste il registro su disco in modo atomico."""
        tmp = self.registry_path.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(self._registry, fh, indent=2, ensure_ascii=False)
            tmp.replace(self.registry_path)   # atomic rename
        except Exception:
            if tmp.exists():
                tmp.unlink()
            raise

    # ------------------------------------------------------------------
    # Hashing
    # ------------------------------------------------------------------

    @staticmethod
    def compute_hash(content: str) -> str:
        """
        Restituisce lo SHA-256 hex del contenuto.
        Deterministico: stesso input → stesso hash sempre.
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # Idempotency check
    # ------------------------------------------------------------------

    def is_stale(self, artifact_id: str, source_hash: str) -> bool:
        """
        Ritorna True se l'artifact deve essere rigenerato.

        Un artifact è "stale" (scaduto) quando:
        - non esiste ancora nel registro, OPPURE
        - il file fisico è stato eliminato, OPPURE
        - il source_hash è diverso da quello registrato.
        """
        entry = self._registry["artifacts"].get(artifact_id)
        if entry is None:
            return True  # mai generato

        artifact_path = Path(entry["path"])
        if not artifact_path.exists():
            return True  # file fisico cancellato

        return entry.get("source_hash") != source_hash

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def save(
        self,
        artifact_id: str,
        content: str,
        source_hash: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Salva l'artifact su disco in modo atomico e aggiorna il registro.

        Returns:
            Percorso assoluto del file salvato.
        """
        artifact_path = self.output_dir / artifact_id
        artifact_path.parent.mkdir(parents=True, exist_ok=True)

        # Scrittura atomica: scrivi su .tmp poi rinomina
        tmp_path = artifact_path.with_suffix(artifact_path.suffix + ".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as fh:
                fh.write(content)
            tmp_path.replace(artifact_path)
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink()
            raise

        self._registry["artifacts"][artifact_id] = {
            "source_hash": source_hash,
            "content_hash": self.compute_hash(content),
            "path": str(artifact_path.resolve()),
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        self._save_registry()
        return str(artifact_path.resolve())

    def load(self, artifact_id: str) -> Optional[str]:
        """Legge e restituisce il contenuto dell'artifact, o None se assente."""
        entry = self._registry["artifacts"].get(artifact_id)
        if entry is None:
            return None
        artifact_path = Path(entry["path"])
        if not artifact_path.exists():
            return None
        with open(artifact_path, "r", encoding="utf-8") as fh:
            return fh.read()

    def get_info(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Restituisce i metadati dell'artifact dal registro."""
        return self._registry["artifacts"].get(artifact_id)

    def list_artifacts(self) -> List[str]:
        """Elenca tutti gli artifact registrati."""
        return list(self._registry["artifacts"].keys())

    def delete(self, artifact_id: str) -> bool:
        """Elimina un artifact dal disco e dal registro. Ritorna True se eliminato."""
        entry = self._registry["artifacts"].pop(artifact_id, None)
        if entry is None:
            return False
        artifact_path = Path(entry["path"])
        if artifact_path.exists():
            artifact_path.unlink()
        self._save_registry()
        return True

    def invalidate(self, artifact_id: str) -> bool:
        """
        Invalida un artifact nel registro senza eliminare il file.
        Al prossimo controllo is_stale() tornerà True.
        """
        if artifact_id not in self._registry["artifacts"]:
            return False
        self._registry["artifacts"][artifact_id]["source_hash"] = "__invalidated__"
        self._save_registry()
        return True
