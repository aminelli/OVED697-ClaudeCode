"""
SkillRegistry — registro centralizzato di tutte le skill disponibili.

Funziona come un dispatcher: raccoglie le definizioni da tutti i moduli
di skill e smista l'esecuzione alla funzione corretta in base al nome
dello strumento invocato da Claude.

Uso tipico in un agente:
    registry = SkillRegistry(artifact_manager)

    # Passa a Claude la lista di tutti gli strumenti disponibili
    response = client.messages.create(
        model="claude-opus-4-5",
        tools=registry.get_all_definitions(),
        messages=[...],
    )

    # Esegui le skill richieste da Claude
    for block in response.content:
        if block.type == "tool_use":
            result = registry.execute(block.name, block.input)
"""

from typing import Any, Dict, List, Optional

from src.artifacts.manager import ArtifactManager
from .file_skills import get_file_skill_definitions, execute_file_skill
from .data_skills import get_data_skill_definitions, execute_data_skill
from .artifact_skills import get_artifact_skill_definitions, make_artifact_skill_executor


class SkillRegistry:
    """
    Registro centralizzato di tutte le skill (tool) del progetto.

    Parametri:
        artifact_manager: istanza di ArtifactManager da iniettare
                          nelle artifact_skills.
        enabled_groups:   lista opzionale di gruppi da abilitare
                          ('file', 'data', 'artifact'). None = tutti.
    """

    ALL_GROUPS = ("file", "data", "artifact")

    def __init__(
        self,
        artifact_manager: Optional[ArtifactManager] = None,
        enabled_groups: Optional[List[str]] = None,
    ) -> None:
        self._manager = artifact_manager or ArtifactManager()
        self._enabled = set(enabled_groups or self.ALL_GROUPS)
        self._artifact_executor = make_artifact_skill_executor(self._manager)

        # Mappa nome-skill → gruppo, per il dispatch
        self._skill_groups: Dict[str, str] = {}
        for defn in self.get_all_definitions():
            group = self._detect_group(defn["name"])
            self._skill_groups[defn["name"]] = group

    # ------------------------------------------------------------------
    # Definizioni
    # ------------------------------------------------------------------

    def get_all_definitions(self) -> List[Dict[str, Any]]:
        """
        Restituisce tutte le definizioni di skill abilitate.
        Questo elenco viene passato direttamente all'API Anthropic.
        """
        definitions: List[Dict[str, Any]] = []
        if "file" in self._enabled:
            definitions.extend(get_file_skill_definitions())
        if "data" in self._enabled:
            definitions.extend(get_data_skill_definitions())
        if "artifact" in self._enabled:
            definitions.extend(get_artifact_skill_definitions())
        return definitions

    def get_group_definitions(self, group: str) -> List[Dict[str, Any]]:
        """Restituisce le definizioni di un singolo gruppo di skill."""
        if group == "file":
            return get_file_skill_definitions()
        if group == "data":
            return get_data_skill_definitions()
        if group == "artifact":
            return get_artifact_skill_definitions()
        raise ValueError(f"Gruppo skill sconosciuto: '{group}'")

    # ------------------------------------------------------------------
    # Esecuzione
    # ------------------------------------------------------------------

    def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Esegue la skill con il nome indicato e restituisce il risultato.

        Questo metodo è il dispatcher principale: riceve il nome dello
        strumento invocato da Claude e lo instrada all'implementazione
        corretta.

        Parametri:
            tool_name:  nome dello strumento (es. 'read_text_file')
            tool_input: dizionario con i parametri forniti da Claude

        Restituisce:
            Risultato come stringa (testo o JSON), compatibile con
            il formato tool_result dell'API Anthropic.
        """
        group = self._skill_groups.get(tool_name)

        if group == "file":
            return execute_file_skill(tool_name, tool_input)
        if group == "data":
            return execute_data_skill(tool_name, tool_input)
        if group == "artifact":
            return self._artifact_executor(tool_name, tool_input)

        return f"ERROR: Skill sconosciuta: '{tool_name}'. Skill disponibili: {list(self._skill_groups)}"

    # ------------------------------------------------------------------
    # Utilità
    # ------------------------------------------------------------------

    def _detect_group(self, tool_name: str) -> str:
        """Inferisce il gruppo di una skill dal suo nome."""
        file_names = {d["name"] for d in get_file_skill_definitions()}
        data_names = {d["name"] for d in get_data_skill_definitions()}
        artifact_names = {d["name"] for d in get_artifact_skill_definitions()}

        if tool_name in file_names:
            return "file"
        if tool_name in data_names:
            return "data"
        if tool_name in artifact_names:
            return "artifact"
        return "unknown"

    def tool_names(self) -> List[str]:
        """Elenco dei nomi di tutte le skill registrate."""
        return [d["name"] for d in self.get_all_definitions()]
