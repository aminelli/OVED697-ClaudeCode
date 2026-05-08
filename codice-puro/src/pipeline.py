"""
Pipeline entry point — avvia la pipeline di analisi dati.

Uso:
    python -m src.pipeline                     # analisi completa
    python -m src.pipeline --data-dir data     # specifica data dir
    python -m src.pipeline --invalidate q1     # forza ricalcolo di q1
    python -m src.pipeline --list              # elenca artifact esistenti
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Assicura che la root del progetto sia nel Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()


def check_env() -> None:
    """Verifica che le variabili d'ambiente necessarie siano presenti."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERRORE: La variabile ANTHROPIC_API_KEY non è impostata.")
        print("  Copia .env.example in .env e inserisci la tua chiave API.")
        sys.exit(1)


def cmd_run(args: argparse.Namespace) -> None:
    """Esegue la pipeline completa."""
    check_env()
    from src.agents.orchestrator_agent import OrchestratorAgent

    orchestrator = OrchestratorAgent(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
    )
    result = orchestrator.run()
    sys.exit(0 if result.success else 1)


def cmd_list(args: argparse.Namespace) -> None:
    """Elenca gli artifact esistenti nel registro."""
    from src.artifacts.manager import ArtifactManager

    manager = ArtifactManager(args.output_dir)
    artifacts = manager.list_artifacts()

    if not artifacts:
        print("Nessun artifact trovato.")
        return

    print(f"\n{'ID Artifact':<35} {'Salvato il':<26} {'Source Hash'}")
    print("-" * 85)
    for aid in sorted(artifacts):
        info = manager.get_info(aid) or {}
        saved_at = info.get("saved_at", "N/A")[:19]
        src_hash = info.get("source_hash", "N/A")[:12] + "..."
        print(f"{aid:<35} {saved_at:<26} {src_hash}")


def cmd_invalidate(args: argparse.Namespace) -> None:
    """Invalida un artifact per forzarne la rigenerazione."""
    from src.artifacts.manager import ArtifactManager

    manager = ArtifactManager(args.output_dir)

    # Supporta sia l'ID completo che il nome parziale
    matching = [
        aid for aid in manager.list_artifacts()
        if args.artifact_id in aid
    ]

    if not matching:
        print(f"Nessun artifact trovato che contenga '{args.artifact_id}'")
        return

    for aid in matching:
        success = manager.invalidate(aid)
        status = "invalidato" if success else "non trovato"
        print(f"  {aid}: {status}")
    print(f"\n{len(matching)} artifact invalidati. Riesegui la pipeline.")


def cmd_delete(args: argparse.Namespace) -> None:
    """Elimina tutti gli artifact (reset completo)."""
    from src.artifacts.manager import ArtifactManager
    import shutil

    output_path = Path(args.output_dir)
    if output_path.exists():
        # Mantieni solo .gitkeep
        for item in output_path.iterdir():
            if item.name != ".gitkeep":
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
    print(f"Output directory '{args.output_dir}' ripulita.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pipeline di analisi dati con Claude — idempotente",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python -m src.pipeline                          # avvia pipeline
  python -m src.pipeline --list                   # elenca artifact
  python -m src.pipeline --invalidate analysis_products_q1
  python -m src.pipeline --reset                  # elimina tutto e ricomincia
        """,
    )
    parser.add_argument(
        "--data-dir",
        default=os.getenv("DATA_DIR", "data"),
        help="Directory con i file CSV (default: data)",
    )
    parser.add_argument(
        "--output-dir",
        default=os.getenv("OUTPUT_DIR", "output"),
        help="Directory per gli artifact (default: output)",
    )

    subparsers = parser.add_subparsers(dest="command")

    # run (default)
    subparsers.add_parser("run", help="Esegui la pipeline (default)")

    # list
    subparsers.add_parser("list", help="Elenca gli artifact esistenti")

    # invalidate
    inv_parser = subparsers.add_parser(
        "invalidate", help="Invalida un artifact per forzarne la rigenerazione"
    )
    inv_parser.add_argument("artifact_id", help="ID o parte dell'ID dell'artifact")

    # reset
    subparsers.add_parser("reset", help="Elimina tutti gli artifact (reset completo)")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "invalidate":
        cmd_invalidate(args)
    elif args.command == "reset":
        cmd_delete(args)
    else:
        # Default: esegui la pipeline
        cmd_run(args)


if __name__ == "__main__":
    main()
