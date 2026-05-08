"""
BaseAgent — classe base per tutti gli agenti del progetto.

Implementa il loop standard di tool-use dell'API Anthropic:

  ┌──────────────────────────────────────────────────────────┐
  │  1. Invia messaggi + lista tool a Claude                 │
  │  2. Claude risponde con tool_use blocks                  │
  │  3. Esegui ogni tool via SkillRegistry                   │
  │  4. Aggiungi risultati come tool_result                  │
  │  5. Invia di nuovo a Claude                              │
  │  6. Ripeti finché stop_reason == "end_turn"              │
  └──────────────────────────────────────────────────────────┘

Ogni sotto-agente sovrascrive:
  - system_prompt: istruzioni specifiche del ruolo
  - skill_groups:  quali gruppi di skill sono disponibili
  - run():         entry point con la logica di alto livello

Limite di sicurezza: max_iterations impedisce loop infiniti.
"""

import os
from typing import Any, Dict, List, Optional

import anthropic
from dotenv import load_dotenv

from src.skills.registry import SkillRegistry
from src.artifacts.manager import ArtifactManager

load_dotenv()

# Costante di sicurezza: numero massimo di turni nel loop
DEFAULT_MAX_ITERATIONS = 20


class BaseAgent:
    """
    Agente base con loop di tool-use integrato.

    Parametri:
        artifact_manager: ArtifactManager condiviso tra agenti.
        skill_groups:     gruppi di skill da abilitare (None = tutti).
        model:            modello Claude da usare.
        max_iterations:   limite di sicurezza sul loop.
    """

    # Da sovrascrivere nelle sottoclassi
    system_prompt: str = "Sei un assistente utile e preciso."

    def __init__(
        self,
        artifact_manager: Optional[ArtifactManager] = None,
        skill_groups: Optional[List[str]] = None,
        model: Optional[str] = None,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
    ) -> None:
        self.client = anthropic.Anthropic(
            api_key=os.environ["ANTHROPIC_API_KEY"]
        )
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-opus-4-5")
        self.max_iterations = max_iterations
        self.artifact_manager = artifact_manager or ArtifactManager(
            os.getenv("OUTPUT_DIR", "output")
        )
        self.registry = SkillRegistry(
            artifact_manager=self.artifact_manager,
            enabled_groups=skill_groups,
        )

    # ------------------------------------------------------------------
    # Tool-use loop
    # ------------------------------------------------------------------

    def _run_loop(
        self,
        user_message: str,
        extra_context: Optional[str] = None,
    ) -> str:
        """
        Esegue il loop di tool-use e restituisce la risposta testuale finale.

        Parametri:
            user_message:  il messaggio iniziale dell'utente/pipeline.
            extra_context: testo aggiuntivo da anteporre al messaggio.
        """
        full_message = (
            f"{extra_context}\n\n{user_message}" if extra_context else user_message
        )

        messages: List[Dict[str, Any]] = [
            {"role": "user", "content": full_message}
        ]

        tools = self.registry.get_all_definitions()

        for iteration in range(self.max_iterations):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                tools=tools,
                messages=messages,
            )

            # Aggiungi la risposta di Claude alla cronologia
            messages.append({"role": "assistant", "content": response.content})

            # ── Terminazione normale ──────────────────────────────────
            if response.stop_reason == "end_turn":
                return self._extract_text(response.content)

            # ── Esecuzione tool ───────────────────────────────────────
            if response.stop_reason == "tool_use":
                tool_results = self._execute_tools(response.content)
                messages.append({"role": "user", "content": tool_results})
                continue

            # Altro stop_reason (max_tokens, ecc.)
            break

        # Sicurezza: loop esaurito
        return f"[Agente terminato dopo {self.max_iterations} iterazioni]"

    def _execute_tools(
        self, content_blocks: List[Any]
    ) -> List[Dict[str, Any]]:
        """
        Esegue tutti i tool_use blocks e restituisce i tool_result
        nel formato atteso dall'API Anthropic.
        """
        results = []
        for block in content_blocks:
            if block.type != "tool_use":
                continue

            print(f"  → Tool invocato: {block.name}({list(block.input.keys())})")

            try:
                output = self.registry.execute(block.name, block.input)
                is_error = output.startswith("ERROR:")
            except Exception as exc:
                output = f"ERROR: Eccezione durante {block.name}: {exc}"
                is_error = True

            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                    "is_error": is_error,
                }
            )

        return results

    @staticmethod
    def _extract_text(content_blocks: List[Any]) -> str:
        """Estrae il testo dai content blocks della risposta finale."""
        parts = []
        for block in content_blocks:
            if hasattr(block, "type") and block.type == "text":
                parts.append(block.text)
        return "\n".join(parts).strip()

    # ------------------------------------------------------------------
    # Entry point (da sovrascrivere)
    # ------------------------------------------------------------------

    def run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Implementa run() nella sottoclasse.")
