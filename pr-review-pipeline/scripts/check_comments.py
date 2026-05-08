#!/usr/bin/env python3
"""
Verifica che i tre artifact review-comment esistano e siano in stato 'ready'.

Uso:
  python scripts/check_comments.py --pr-id pr-42
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMENTS_DIR = REPO_ROOT / "artifacts" / "comments"
AGENT_NAMES = ["security", "performance", "style"]


def parse_frontmatter_status(filepath: Path) -> str | None:
    """Estrae artifact:status dal frontmatter YAML del file Markdown."""
    try:
        text = filepath.read_text(encoding="utf-8")
        in_frontmatter = False
        for line in text.splitlines():
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter and line.startswith("artifact:status:"):
                return line.split(":", 2)[2].strip()
    except OSError:
        pass
    return None


def check_comments(pr_id: str) -> bool:
    all_ok = True
    print(f"\nVerifica artifact review-comment per {pr_id}:")
    print("-" * 50)

    for agent in AGENT_NAMES:
        file_name = f"{pr_id}_{agent}.md"
        file_path = COMMENTS_DIR / file_name
        exists = file_path.exists()
        status = parse_frontmatter_status(file_path) if exists else None
        is_ready = status == "ready"

        icon = "✅" if (exists and is_ready) else "❌"
        status_str = status or "N/A"
        print(f"  {icon} {file_name:<40} status={status_str}")

        if not exists or not is_ready:
            all_ok = False

    print()
    if all_ok:
        print("✅ Tutti i commenti sono pronti. Procedi con l'aggregazione.")
    else:
        print("❌ Alcuni commenti mancano o non sono in stato 'ready'.")
        print("   Rilancia i Task corrispondenti.")

    return all_ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifica commenti di review")
    parser.add_argument("--pr-id", required=True, help="Es: pr-42")
    args = parser.parse_args()

    ok = check_comments(args.pr_id)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
