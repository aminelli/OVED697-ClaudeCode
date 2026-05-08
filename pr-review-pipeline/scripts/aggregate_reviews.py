#!/usr/bin/env python3
"""
Aggrega i tre artifact review-comment in un review-report finale
e aggiorna l'artifact-registry.

Uso:
  python scripts/aggregate_reviews.py --pr-id pr-42
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMENTS_DIR = REPO_ROOT / "artifacts" / "comments"
REPORTS_DIR = REPO_ROOT / "artifacts" / "reports"
REGISTRY_FILE = REPO_ROOT / "artifacts" / "manifests" / "artifact-registry.json"
AGENT_NAMES = ["security", "performance", "style"]
AGENT_EMOJIS = {"security": "🔴", "performance": "🟡", "style": "🔵"}


def load_registry() -> list[dict]:
    if not REGISTRY_FILE.exists():
        return []
    with REGISTRY_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def save_registry(records: list[dict]) -> None:
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with REGISTRY_FILE.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
        f.write("\n")


def parse_frontmatter(filepath: Path) -> dict[str, object]:
    """Estrae il frontmatter YAML semplice (chiave: valore) dal file."""
    result: dict[str, object] = {}
    try:
        text = filepath.read_text(encoding="utf-8")
        in_fm = False
        in_counts = False
        current_parent: str | None = None

        for line in text.splitlines():
            stripped = line.strip()
            if stripped == "---":
                if not in_fm:
                    in_fm = True
                else:
                    break
                continue
            if not in_fm:
                continue

            # Blocco annidato severity-counts
            if stripped == "artifact:severity-counts:":
                in_counts = True
                current_parent = "severity_counts"
                result[current_parent] = {}
                continue
            if in_counts and line.startswith("  "):
                key, _, val = stripped.partition(":")
                result["severity_counts"][key.strip()] = int(val.strip() or 0)
                continue
            in_counts = False
            current_parent = None

            if ":" in stripped:
                key, _, val = stripped.partition(":")
                key = key.strip().replace("artifact:", "").replace("-", "_")
                result[key] = val.strip()

    except OSError:
        pass
    return result


def compute_verdict(all_counts: dict[str, dict[str, int]]) -> str:
    totals: dict[str, int] = {}
    for counts in all_counts.values():
        for sev, n in counts.items():
            totals[sev] = totals.get(sev, 0) + n

    if totals.get("critical", 0) > 0 or totals.get("high", 0) > 0:
        return "REQUEST_CHANGES"
    if totals.get("medium", 0) > 0 or totals.get("low", 0) > 0:
        return "COMMENT"
    return "APPROVE"


def verdict_emoji(verdict: str) -> str:
    return {"REQUEST_CHANGES": "❌", "COMMENT": "⚠️", "APPROVE": "✅"}.get(verdict, "")


def render_severity_row(counts: dict[str, int]) -> str:
    return (
        f"| 🔴 Critical | {counts.get('critical', 0)} |\n"
        f"| 🟠 High     | {counts.get('high', 0)} |\n"
        f"| 🟡 Medium   | {counts.get('medium', 0)} |\n"
        f"| 🔵 Low      | {counts.get('low', 0)} |\n"
        f"| ℹ️  Info    | {counts.get('info', 0)} |"
    )


def extract_body(filepath: Path) -> str:
    """Restituisce il contenuto Markdown dopo il secondo ---."""
    text = filepath.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    return parts[2].strip() if len(parts) >= 3 else text.strip()


def aggregate(pr_id: str) -> int:
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    all_metadata: dict[str, dict] = {}
    all_counts: dict[str, dict[str, int]] = {}
    comment_sources: list[str] = []
    comment_bodies: dict[str, str] = {}

    for agent in AGENT_NAMES:
        file_path = COMMENTS_DIR / f"{pr_id}_{agent}.md"
        if not file_path.exists():
            print(f"❌ Artifact mancante: {file_path}", file=sys.stderr)
            return 1
        metadata = parse_frontmatter(file_path)
        all_metadata[agent] = metadata
        all_counts[agent] = metadata.get("severity_counts", {})
        artifact_id = metadata.get("id", f"{pr_id}_{agent}")
        comment_sources.append(str(artifact_id))
        comment_bodies[agent] = extract_body(file_path)

    verdict = compute_verdict(all_counts)
    report_id = f"review_{pr_id}"

    # Costruisci sezione riepilogo per agent
    agent_summary_rows = []
    for agent in AGENT_NAMES:
        counts = all_counts[agent]
        c = counts.get("critical", 0)
        h = counts.get("high", 0)
        m = counts.get("medium", 0)
        lo = counts.get("low", 0)
        inf = counts.get("info", 0)
        emoji = AGENT_EMOJIS[agent]
        agent_summary_rows.append(
            f"| {emoji} {agent.capitalize():<14} | {c} | {h} | {m} | {lo} | {inf} |"
        )

    agent_summary = "\n".join(agent_summary_rows)

    # Totali
    totals: dict[str, int] = {}
    for counts in all_counts.values():
        for sev, n in counts.items():
            totals[sev] = totals.get(sev, 0) + n

    frontmatter = f"""---
artifact:type: review-report
artifact:id: {report_id}
artifact:pr-id: {pr_id}
artifact:status: complete
artifact:verdict: {verdict}
artifact:sources:
{chr(10).join(f'  - {s}' for s in comment_sources)}
artifact:created-by: claude/orchestrator
artifact:created-at: {created_at}
---"""

    body = f"""# Code Review Report — {pr_id}

_Generato il: {created_at}_

## Verdetto: {verdict_emoji(verdict)} {verdict}

## Riepilogo per agent

| Agent          | Critical | High | Medium | Low | Info |
|----------------|----------|------|--------|-----|------|
{agent_summary}
| **Totale**     | **{totals.get('critical', 0)}** | **{totals.get('high', 0)}** | **{totals.get('medium', 0)}** | **{totals.get('low', 0)}** | **{totals.get('info', 0)}** |

---

## Dettaglio Security Review

{comment_bodies['security']}

---

## Dettaglio Performance Review

{comment_bodies['performance']}

---

## Dettaglio Style Review

{comment_bodies['style']}
"""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / f"{report_id}.md"
    report_file.write_text(frontmatter + "\n\n" + body, encoding="utf-8")

    # Aggiorna registry
    registry = load_registry()

    # Aggiungi i 3 commenti al registry (se non già presenti)
    existing_ids = {r["id"] for r in registry}
    for agent in AGENT_NAMES:
        artifact_id = all_metadata[agent].get("id", f"{pr_id}_{agent}")
        if artifact_id not in existing_ids:
            registry.append({
                "id": artifact_id,
                "type": "review-comment",
                "status": "ready",
                "pr_id": pr_id,
                "agent": agent,
                "file": f"artifacts/comments/{pr_id}_{agent}.md",
                "severity_counts": all_counts[agent],
                "created_at": all_metadata[agent].get("created_at", created_at),
                "created_by": f"claude/{agent}-agent",
                "relationships": {"part_of_report": report_id},
            })

    # Aggiungi il report
    registry.append({
        "id": report_id,
        "type": "review-report",
        "status": "complete",
        "pr_id": pr_id,
        "verdict": verdict,
        "file": f"artifacts/reports/{report_id}.md",
        "created_at": created_at,
        "created_by": "claude/orchestrator",
        "relationships": {
            "sources": comment_sources,
        },
        "metadata": {
            "total_critical": totals.get("critical", 0),
            "total_high": totals.get("high", 0),
            "total_medium": totals.get("medium", 0),
            "total_low": totals.get("low", 0),
            "total_info": totals.get("info", 0),
        },
    })

    save_registry(registry)

    print(f"\n{'═' * 50}")
    print(f"  PR Review: {pr_id}")
    print(f"  Verdetto: {verdict_emoji(verdict)}  {verdict}")
    print(f"{'═' * 50}")
    for agent in AGENT_NAMES:
        counts = all_counts[agent]
        print(
            f"  {AGENT_EMOJIS[agent]} {agent.capitalize():<14} — "
            f"{counts.get('critical', 0)} critical, "
            f"{counts.get('high', 0)} high, "
            f"{counts.get('medium', 0)} medium"
        )
    print(f"\n  Report completo: artifacts/reports/{report_id}.md")
    print(f"{'═' * 50}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggrega review-comment in review-report")
    parser.add_argument("--pr-id", required=True, help="Es: pr-42")
    args = parser.parse_args()
    return aggregate(args.pr_id)


if __name__ == "__main__":
    sys.exit(main())
