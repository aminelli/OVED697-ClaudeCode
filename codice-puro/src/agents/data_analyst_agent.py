"""
DataAnalystAgent — analizza un singolo file CSV di dati di vendita.

Responsabilità:
- Legge e comprende la struttura del CSV
- Calcola statistiche chiave (ricavi, volumi, categorie)
- Produce un'analisi strutturata in formato JSON/Markdown

Skill disponibili: file, data, artifact

Idempotenza: prima di elaborare, verifica se l'artifact di analisi
esiste già e non è stale (source_hash invariato). In quel caso,
restituisce l'analisi esistente senza chiamate extra a Claude.
"""

from pathlib import Path
from typing import Optional

from src.artifacts.manager import ArtifactManager
from .base_agent import BaseAgent


class DataAnalystAgent(BaseAgent):
    """
    Agente specializzato nell'analisi di file CSV di vendita.
    Produce un artifact Markdown per ogni file analizzato.
    """

    system_prompt = """Sei un analista dati esperto. Il tuo compito è analizzare
file CSV di dati di vendita e produrre report di analisi chiari e strutturati.

ISTRUZIONI:
1. Usa 'check_artifact_status' per verificare se l'analisi esiste già
   e non è cambiata (status 'fresh'). Se è 'fresh', carica e restituisci
   l'analisi esistente con load_artifact — NON rigenerare.

2. Se è 'stale', procedi con l'analisi:
   a. Leggi il file CSV con 'read_text_file'
   b. Analizza lo schema con 'parse_csv_schema'
   c. Calcola statistiche sui ricavi con 'compute_column_stats'
   d. Aggrega per categoria con 'aggregate_by_category'
   e. Scrivi un report Markdown strutturato con:
      - Titolo e riepilogo esecutivo
      - Statistiche principali (totale ricavi, media, min, max)
      - Top 3 categorie per ricavo
      - Insight chiave in 3-5 punti
   f. Salva il report con 'save_artifact'

3. Restituisci SEMPRE il contenuto del report come testo finale.

FORMATO ARTIFACT ID: usa 'analysis_{nome_file_senza_estensione}.md'
"""

    def __init__(self, artifact_manager: Optional[ArtifactManager] = None) -> None:
        super().__init__(
            artifact_manager=artifact_manager,
            skill_groups=["file", "data", "artifact"],
        )

    def run(self, csv_filepath: str) -> str:
        """
        Analizza il file CSV indicato e restituisce il report Markdown.

        Parametri:
            csv_filepath: percorso al file CSV da analizzare.

        Restituisce:
            Contenuto del report di analisi in formato Markdown.
        """
        filename = Path(csv_filepath).stem
        artifact_id = f"analysis_{filename}.md"

        print(f"\n[DataAnalystAgent] Analisi: {csv_filepath}")
        print(f"  Artifact target: {artifact_id}")

        prompt = f"""Analizza il file CSV: '{csv_filepath}'
Artifact ID da usare: '{artifact_id}'

Segui le istruzioni del sistema: controlla prima se l'artifact è già aggiornato,
poi procedi di conseguenza."""

        return self._run_loop(prompt)
