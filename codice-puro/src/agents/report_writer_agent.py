"""
ReportWriterAgent — compila un report di sintesi da più analisi individuali.

Responsabilità:
- Carica le analisi prodotte da DataAnalystAgent
- Produce un report di sintesi comparativa tra i periodi
- Identifica trend, anomalie e raccomandazioni

Skill disponibili: artifact (solo lettura/scrittura artifact)

Idempotenza: concatena il contenuto di tutti gli artifact di analisi,
calcola l'hash aggregato e lo confronta con l'artifact di sintesi.
"""

from typing import List, Optional

from src.artifacts.manager import ArtifactManager
from .base_agent import BaseAgent


class ReportWriterAgent(BaseAgent):
    """
    Agente che produce un report di sintesi comparativa.
    """

    system_prompt = """Sei un esperto business analyst. Il tuo compito è
sintetizzare più analisi di periodi diversi in un unico report esecutivo.

ISTRUZIONI:
1. Usa 'list_artifacts' per vedere quali analisi sono disponibili.
2. Carica ogni artifact di analisi con 'load_artifact'.
3. Controlla se il report di sintesi ('summary_report.md') è già aggiornato
   con 'check_artifact_status', passando come source_content la
   concatenazione di tutti i contenuti delle analisi caricate.
   Se è 'fresh' → restituisci il report esistente (load_artifact).

4. Se 'stale', scrivi un report di sintesi Markdown che include:
   ## Executive Summary
   - Riepilogo delle performance complessive di tutti i periodi

   ## Confronto tra Periodi
   - Tabella comparativa dei KPI principali (ricavi totali, media, top categoria)

   ## Trend e Insight
   - 3-5 osservazioni chiave sui trend tra i periodi

   ## Raccomandazioni
   - 3 raccomandazioni concrete basate sui dati

5. Salva il report con 'save_artifact' (id: 'summary_report.md').
6. Restituisci il contenuto del report.

Analizza SOLO gli artifact che iniziano con 'analysis_'.
"""

    def __init__(self, artifact_manager: Optional[ArtifactManager] = None) -> None:
        super().__init__(
            artifact_manager=artifact_manager,
            skill_groups=["artifact"],
        )

    def run(self, analysis_ids: Optional[List[str]] = None) -> str:
        """
        Produce il report di sintesi.

        Parametri:
            analysis_ids: lista opzionale di artifact ID da includere.
                          Se None, usa tutti gli artifact che iniziano
                          con 'analysis_'.

        Restituisce:
            Contenuto del report di sintesi in Markdown.
        """
        print("\n[ReportWriterAgent] Generazione report di sintesi...")

        if analysis_ids:
            ids_hint = f"Usa questi artifact specifici: {analysis_ids}"
        else:
            ids_hint = "Usa tutti gli artifact che iniziano con 'analysis_'."

        prompt = f"""Genera il report di sintesi comparativa.
{ids_hint}

Artifact ID del report finale: 'summary_report.md'

Segui le istruzioni del sistema passo per passo."""

        return self._run_loop(prompt)
