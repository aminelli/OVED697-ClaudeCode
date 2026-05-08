"""
Skills package — definizioni degli strumenti (tools) che Claude può invocare.

Ogni "skill" è composta da due parti:
  1. La DEFINIZIONE (dict compatibile con l'API Anthropic) che descrive
     lo strumento a Claude (nome, descrizione, schema JSON dell'input).
  2. L'IMPLEMENTAZIONE (funzione Python) che esegue l'azione reale.

Il SkillRegistry aggrega tutte le skill e funge da dispatcher.
"""
from .registry import SkillRegistry
from .file_skills import get_file_skill_definitions, execute_file_skill
from .data_skills import get_data_skill_definitions, execute_data_skill
from .artifact_skills import get_artifact_skill_definitions, execute_artifact_skill

__all__ = [
    "SkillRegistry",
    "get_file_skill_definitions",
    "execute_file_skill",
    "get_data_skill_definitions",
    "execute_data_skill",
    "get_artifact_skill_definitions",
    "execute_artifact_skill",
]
