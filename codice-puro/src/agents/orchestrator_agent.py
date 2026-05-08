"""
OrchestratorAgent — coordina l'intera pipeline di analisi.

Questo agente NON chiama Claude: è puro Python.
Coordina DataAnalystAgent e ReportWriterAgent in modo idempotente.

Flusso:
  1. Elenca i file CSV nella data_dir
  2. Per ogni CSV, esegue DataAnalystAgent (con idempotenza integrata)
  3. Raccoglie gli artifact ID delle analisi prodotte
  4. Esegue ReportWriterAgent per la sintesi finale
  5. Restituisce un riepilogo dell'esecuzione

Nota di design: l'orchestratore non usa il loop di tool-use perché
la sua logica è deterministica e non richiede ragionamento adattivo.
Usare Claude per la pura orchestrazione sarebbe un anti-pattern costoso.
"""

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from src.artifacts.manager import ArtifactManager
from .data_analyst_agent import DataAnalystAgent
from .report_writer_agent import ReportWriterAgent


@dataclass
class PipelineResult:
    """Risultato dell'esecuzione della pipeline."""
    data_dir: str
    total_files: int
    processed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    failed: Dict[str, str] = field(default_factory=dict)
    summary_artifact: Optional[str] = None
    elapsed_seconds: float = 0.0

    @property
    def success(self) -> bool:
        return len(self.failed) == 0

    def __str__(self) -> str:
        lines = [
            "=" * 60,
            "PIPELINE RESULT",
            "=" * 60,
            f"  Data dir      : {self.data_dir}",
            f"  File totali   : {self.total_files}",
            f"  Processati    : {len(self.processed)}",
            f"  Saltati (ok)  : {len(self.skipped)}  ← idempotenza",
            f"  Falliti       : {len(self.failed)}",
            f"  Report finale : {self.summary_artifact or 'N/A'}",
            f"  Tempo         : {self.elapsed_seconds:.1f}s",
            "=" * 60,
        ]
        if self.failed:
            lines.append("ERRORI:")
            for f, err in self.failed.items():
                lines.append(f"  {f}: {err}")
        return "\n".join(lines)


class OrchestratorAgent:
    """
    Orchestratore della pipeline di analisi dati.

    Non eredita da BaseAgent perché non usa il loop di tool-use.
    Coordina gli altri agenti in Python puro.
    """

    def __init__(
        self,
        data_dir: str = "data",
        output_dir: str = "output",
        model: Optional[str] = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.artifact_manager = ArtifactManager(output_dir)
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-opus-4-5")

        # Gli agenti condividono lo stesso ArtifactManager
        self.analyst = DataAnalystAgent(artifact_manager=self.artifact_manager)
        self.writer = ReportWriterAgent(artifact_manager=self.artifact_manager)

    def run(self) -> PipelineResult:
        """
        Esegue la pipeline completa in modo idempotente.

        Restituisce:
            PipelineResult con statistiche dell'esecuzione.
        """
        start = time.time()

        csv_files = sorted(self.data_dir.glob("*.csv"))
        result = PipelineResult(
            data_dir=str(self.data_dir),
            total_files=len(csv_files),
        )

        if not csv_files:
            print(f"[Orchestrator] Nessun file CSV trovato in '{self.data_dir}'")
            result.elapsed_seconds = time.time() - start
            return result

        print(f"\n[Orchestrator] Trovati {len(csv_files)} file CSV")
        print("[Orchestrator] Avvio analisi individuali...\n")

        analysis_ids: List[str] = []

        for csv_path in csv_files:
            artifact_id = f"analysis_{csv_path.stem}.md"

            # Controllo idempotenza PRIMA di invocare l'agente
            # (risparmio anche il costo di avviare l'agente)
            try:
                csv_content = csv_path.read_text(encoding="utf-8")
                src_hash = self.artifact_manager.compute_hash(csv_content)

                if not self.artifact_manager.is_stale(artifact_id, src_hash):
                    print(f"[Orchestrator] SKIP {csv_path.name} — artifact aggiornato")
                    result.skipped.append(csv_path.name)
                    analysis_ids.append(artifact_id)
                    continue

                # Artifact stale o assente: procedi con l'analisi
                self.analyst.run(str(csv_path))
                result.processed.append(csv_path.name)
                analysis_ids.append(artifact_id)

            except Exception as exc:
                print(f"[Orchestrator] ERRORE {csv_path.name}: {exc}")
                result.failed[csv_path.name] = str(exc)

        # Report di sintesi finale
        print("\n[Orchestrator] Generazione report di sintesi...")
        try:
            self.writer.run(analysis_ids=analysis_ids)
            result.summary_artifact = "summary_report.md"
        except Exception as exc:
            print(f"[Orchestrator] ERRORE report sintesi: {exc}")
            result.failed["summary_report.md"] = str(exc)

        result.elapsed_seconds = time.time() - start
        print(f"\n{result}")
        return result
