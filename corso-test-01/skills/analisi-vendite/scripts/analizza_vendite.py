"""
analizza_vendite.py — Script di analisi dati di vendita

Implementa la logica a 4 fasi definita in:
  skills/analisi-vendite/references/logica-analisi.md

Le soglie usate per la classificazione semaforo corrispondono a:
  skills/analisi-vendite/references/soglie-kpi.md

Utilizzo:
  # Solo validazione
  python analizza_vendite.py --input data/vendite.csv --validate-only

  # Analisi completa
  python analizza_vendite.py --input data/vendite.csv --output output/report.md

  # Con separatore punto e virgola
  python analizza_vendite.py --input data/vendite.csv --output output/report.md --sep ";"
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

VERSION = "1.0.0"

# ─── Soglie RAG (fonte: references/soglie-kpi.md) ────────────────────────────

SOGLIE = {
    "margin_pct": {"verde": 30.0, "giallo": 15.0},          # >= verde, >= giallo, < giallo = rosso
    "avg_order_value": {"verde": 150.0, "giallo": 75.0},
    "mom_growth": {"verde": 5.0, "giallo": 0.0},
    "top_customer_pct": {"verde": 20.0, "giallo": 40.0},     # < verde, <= giallo, > giallo = rosso
    "top_product_pct": {"verde": 30.0, "giallo": 50.0},
    "data_quality_pct": {"verde": 98.0, "giallo": 90.0},
}

REQUIRED_COLS = {"order_id", "date", "product_id", "quantity", "unit_price"}
OPTIONAL_COLS = {"customer_id", "category", "discount_pct", "cost_price", "region"}


# ─── Strutture dati ───────────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)       # errori bloccanti
    warnings: list[str] = field(default_factory=list)     # warning non bloccanti
    valid_rows: int = 0
    total_rows: int = 0
    skipped_rows: int = 0

    @property
    def is_valid(self) -> bool:
        """Valido se gli errori bloccanti sono su meno del 5% delle righe."""
        if self.total_rows == 0:
            return False
        blocking_rate = self.skipped_rows / self.total_rows
        return blocking_rate < 0.05

    @property
    def quality_pct(self) -> float:
        if self.total_rows == 0:
            return 0.0
        return self.valid_rows / self.total_rows * 100


@dataclass
class SalesRow:
    order_id: str
    date: date
    product_id: str
    quantity: int
    unit_price: float
    customer_id: str | None = None
    category: str | None = None
    discount_pct: float = 0.0
    cost_price: float | None = None
    region: str | None = None

    @property
    def revenue(self) -> float:
        return self.quantity * self.unit_price * (1 - self.discount_pct / 100)

    @property
    def margin(self) -> float | None:
        if self.cost_price is None:
            return None
        return self.revenue - (self.quantity * self.cost_price)


# ─── Fase 1: Validazione ─────────────────────────────────────────────────────

def validate_and_parse(
    filepath: Path, sep: str
) -> tuple[ValidationResult, list[SalesRow]]:
    """
    Legge il CSV, valida ogni riga e restituisce ValidationResult + righe valide.
    """
    result = ValidationResult()
    rows: list[SalesRow] = []
    seen_order_ids: set[str] = set()

    try:
        raw = filepath.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
            result.warnings.append("Encoding: UTF-8 fallito, usato latin-1.")
    except OSError as e:
        result.errors.append(f"Impossibile leggere il file: {e}")
        return result, rows

    reader = csv.DictReader(io.StringIO(text), delimiter=sep)

    # Controlla colonne obbligatorie nell'header
    if reader.fieldnames is None:
        result.errors.append("File vuoto o header mancante.")
        return result, rows

    header = set(reader.fieldnames)
    missing = REQUIRED_COLS - header
    if missing:
        result.errors.append(
            f"Colonne obbligatorie mancanti: {', '.join(sorted(missing))}"
        )
        return result, rows

    for lineno, raw_row in enumerate(reader, start=2):
        result.total_rows += 1
        row_errors: list[str] = []

        # Campi obbligatori
        order_id = raw_row.get("order_id", "").strip()
        date_str = raw_row.get("date", "").strip()
        product_id = raw_row.get("product_id", "").strip()
        qty_str = raw_row.get("quantity", "").strip()
        price_str = raw_row.get("unit_price", "").strip()

        if not order_id:
            row_errors.append(f"Riga {lineno}: order_id vuoto.")
        if not product_id:
            row_errors.append(f"Riga {lineno}: product_id vuoto.")

        # Parsing data
        parsed_date: date | None = None
        try:
            parsed_date = date.fromisoformat(date_str)
            if parsed_date > date.today():
                result.warnings.append(f"Riga {lineno}: data futura ({date_str}).")
            if parsed_date.year < 2000:
                result.warnings.append(f"Riga {lineno}: data ante-2000 ({date_str}).")
        except ValueError:
            row_errors.append(f"Riga {lineno}: formato data non valido '{date_str}'.")

        # Parsing quantity
        parsed_qty: int | None = None
        try:
            parsed_qty = int(qty_str)
            if parsed_qty <= 0:
                result.warnings.append(f"Riga {lineno}: quantity = {parsed_qty} (≤ 0).")
        except ValueError:
            row_errors.append(f"Riga {lineno}: quantity non numerica '{qty_str}'.")

        # Parsing unit_price
        parsed_price: float | None = None
        try:
            parsed_price = float(price_str)
            if parsed_price <= 0:
                result.warnings.append(
                    f"Riga {lineno}: unit_price = {parsed_price} (≤ 0)."
                )
        except ValueError:
            row_errors.append(f"Riga {lineno}: unit_price non numerica '{price_str}'.")

        if row_errors:
            result.errors.extend(row_errors)
            result.skipped_rows += 1
            continue

        # Campi opzionali
        customer_id = raw_row.get("customer_id", "").strip() or None
        category = raw_row.get("category", "").strip() or None
        region = raw_row.get("region", "").strip() or None

        discount_pct = 0.0
        if raw_row.get("discount_pct", "").strip():
            try:
                discount_pct = float(raw_row["discount_pct"])
                if not (0 <= discount_pct <= 100):
                    result.warnings.append(
                        f"Riga {lineno}: discount_pct={discount_pct} fuori range, usato 0."
                    )
                    discount_pct = 0.0
            except ValueError:
                result.warnings.append(
                    f"Riga {lineno}: discount_pct non numerica, usato 0."
                )

        cost_price: float | None = None
        if raw_row.get("cost_price", "").strip():
            try:
                cost_price = float(raw_row["cost_price"])
                if cost_price > parsed_price:  # type: ignore[operator]
                    result.warnings.append(
                        f"Riga {lineno}: cost_price ({cost_price}) > unit_price "
                        f"({parsed_price}) — margine negativo."
                    )
            except ValueError:
                result.warnings.append(
                    f"Riga {lineno}: cost_price non numerica, ignorato."
                )

        # Duplicati order_id
        if order_id in seen_order_ids:
            result.warnings.append(
                f"Riga {lineno}: order_id duplicato '{order_id}', riga ignorata."
            )
            result.skipped_rows += 1
            continue
        seen_order_ids.add(order_id)

        rows.append(
            SalesRow(
                order_id=order_id,
                date=parsed_date,  # type: ignore[arg-type]
                product_id=product_id,
                quantity=parsed_qty,  # type: ignore[arg-type]
                unit_price=parsed_price,  # type: ignore[arg-type]
                customer_id=customer_id,
                category=category,
                discount_pct=discount_pct,
                cost_price=cost_price,
                region=region,
            )
        )
        result.valid_rows += 1

    if result.valid_rows == 0 and result.total_rows > 0:
        result.errors.append("Nessuna riga valida trovata nel file.")

    return result, rows


# ─── Fase 2: Calcolo KPI ─────────────────────────────────────────────────────

def compute_kpis(rows: list[SalesRow]) -> dict[str, Any]:
    """Calcola tutti i KPI nell'ordine definito in logica-analisi.md § 2.3."""

    has_cost = any(r.cost_price is not None for r in rows)
    has_customer = any(r.customer_id is not None for r in rows)
    has_category = any(r.category is not None for r in rows)

    total_revenue = sum(r.revenue for r in rows)
    total_margin = sum(r.margin for r in rows if r.margin is not None) if has_cost else None
    margin_pct = (total_margin / total_revenue * 100) if (has_cost and total_revenue > 0) else None
    order_count = len(rows)
    avg_order_value = total_revenue / order_count if order_count > 0 else 0.0

    # Clienti unici
    unique_customers = len({r.customer_id for r in rows if r.customer_id}) if has_customer else None

    # Top prodotti
    prod_rev: dict[str, float] = defaultdict(float)
    for r in rows:
        prod_rev[r.product_id] += r.revenue
    top_products = sorted(prod_rev.items(), key=lambda x: x[1], reverse=True)[:5]

    # Top clienti
    top_customers = None
    if has_customer:
        cust_rev: dict[str, float] = defaultdict(float)
        for r in rows:
            if r.customer_id:
                cust_rev[r.customer_id] += r.revenue
        top_customers = sorted(cust_rev.items(), key=lambda x: x[1], reverse=True)[:5]

    # Fatturato per categoria
    rev_by_category = None
    if has_category:
        cat_rev: dict[str, float] = defaultdict(float)
        for r in rows:
            cat_rev[r.category or "N/D"] += r.revenue
        rev_by_category = sorted(cat_rev.items(), key=lambda x: x[1], reverse=True)

    # Trend mensile
    monthly: dict[str, float] = defaultdict(float)
    for r in rows:
        key = r.date.strftime("%Y-%m")
        monthly[key] += r.revenue
    monthly_trend = sorted(monthly.items())

    # Crescita MoM
    mom_growth = None
    if len(monthly_trend) >= 2:
        last = monthly_trend[-1][1]
        prev = monthly_trend[-2][1]
        if prev > 0:
            mom_growth = (last - prev) / prev * 100

    # Periodo
    dates = [r.date for r in rows]
    date_start = min(dates)
    date_end = max(dates)

    return {
        "total_revenue": total_revenue,
        "total_margin": total_margin,
        "margin_pct": margin_pct,
        "order_count": order_count,
        "avg_order_value": avg_order_value,
        "unique_customers": unique_customers,
        "top_products": top_products,
        "top_customers": top_customers,
        "rev_by_category": rev_by_category,
        "monthly_trend": monthly_trend,
        "mom_growth": mom_growth,
        "date_start": date_start,
        "date_end": date_end,
        "days_covered": (date_end - date_start).days + 1,
        "has_cost": has_cost,
        "has_customer": has_customer,
        "has_category": has_category,
    }


# ─── Fase 3: Classificazione Semaforo ────────────────────────────────────────

def semaforo(value: float | None, kpi: str) -> str:
    """
    Restituisce 🟢 🟡 🔴 ⚪ in base alle soglie di soglie-kpi.md.
    """
    if value is None:
        return "⚪"
    s = SOGLIE[kpi]
    verde = s["verde"]
    giallo = s["giallo"]

    # KPI "più alto = meglio" (margin_pct, avg_order_value, mom_growth, data_quality_pct)
    if kpi in ("margin_pct", "avg_order_value", "mom_growth", "data_quality_pct"):
        if value >= verde:
            return "🟢"
        if value >= giallo:
            return "🟡"
        return "🔴"

    # KPI "più basso = meglio" (concentrazione)
    if kpi in ("top_customer_pct", "top_product_pct"):
        if value < verde:
            return "🟢"
        if value <= giallo:
            return "🟡"
        return "🔴"

    return "⚪"


# ─── Fase 4: Insight ─────────────────────────────────────────────────────────

def generate_insights(kpis: dict[str, Any]) -> list[str]:
    """
    Genera insight testuali secondo le regole di logica-analisi.md § Fase 4.
    Max 5, ordinati per priorità (🔴 prima).
    """
    insights: list[tuple[int, str]] = []  # (priorità, testo)

    mom = kpis["mom_growth"]
    margin_pct = kpis["margin_pct"]
    top_products = kpis["top_products"]
    top_customers = kpis["top_customers"]
    total_revenue = kpis["total_revenue"]
    avg_order_value = kpis["avg_order_value"]

    # Crescita MoM
    if mom is not None:
        if mom < -10:
            insights.append((1, f"🔴 Calo significativo del fatturato nell'ultimo mese "
                               f"({mom:+.1f}%): analizzare le cause."))
        elif mom < 0:
            insights.append((2, f"🟡 Crescita leggermente negativa nell'ultimo mese "
                               f"({mom:+.1f}%)."))
        elif mom > 20:
            insights.append((3, f"🟢 Crescita eccellente nell'ultimo mese (+{mom:.1f}%). "
                               "Analizzare i fattori positivi per replicarli."))

    # Margine %
    if margin_pct is not None:
        if margin_pct < 15:
            insights.append((1, f"🔴 Margine sotto la soglia critica ({margin_pct:.1f}%): "
                               "verificare i costi di acquisto."))
        elif margin_pct > 40:
            insights.append((3, f"🟢 Margine molto elevato ({margin_pct:.1f}%). "
                               "Verificare che i prezzi di costo siano aggiornati."))

    # Concentrazione cliente
    if top_customers and total_revenue > 0:
        top_cust_id, top_cust_rev = top_customers[0]
        top_cust_pct = top_cust_rev / total_revenue * 100
        if top_cust_pct > 40:
            insights.append((1, f"🔴 Concentrazione cliente elevata: {top_cust_id} rappresenta "
                               f"{top_cust_pct:.1f}% del fatturato totale. Rischio dipendenza."))
        elif top_cust_pct > 20:
            insights.append((2, f"🟡 {top_cust_id} rappresenta {top_cust_pct:.1f}% del "
                               "fatturato. Dipendenza moderata da un singolo cliente."))

    # Concentrazione prodotto
    if top_products and total_revenue > 0:
        top_prod_id, top_prod_rev = top_products[0]
        top_prod_pct = top_prod_rev / total_revenue * 100
        if top_prod_pct > 50:
            insights.append((2, f"🟡 Concentrazione prodotto: {top_prod_id} rappresenta "
                               f"{top_prod_pct:.1f}% del fatturato. Valutare diversificazione."))

    # Ticket medio
    if avg_order_value < 75:
        insights.append((2, f"🟡 Ticket medio basso (€{avg_order_value:.2f}). "
                           "Possibile erosione del mix prodotto."))

    if not insights:
        return ["✅ Nessuna anomalia rilevante rilevata."]

    insights.sort(key=lambda x: x[0])
    return [text for _, text in insights[:5]]


# ─── Generazione Report ───────────────────────────────────────────────────────

def fmt_eur(value: float | None) -> str:
    if value is None:
        return "N/D"
    return f"€{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "N/D"
    return f"{value:.1f}%"


def mini_chart(monthly_trend: list[tuple[str, float]]) -> tuple[str, str]:
    """Genera mini-chart ASCII e scala."""
    if len(monthly_trend) < 3:
        return "", ""
    max_val = max(v for _, v in monthly_trend)
    if max_val == 0:
        return "", ""
    scala = max_val / 20
    lines = []
    for month, val in monthly_trend:
        bars = int(val / scala) if scala > 0 else 0
        lines.append(f"{month}  {'█' * bars}  {fmt_eur(val)}")
    return "\n".join(lines), fmt_eur(scala)


def generate_report(
    filepath: Path,
    validation: ValidationResult,
    kpis: dict[str, Any],
    insights: list[str],
) -> str:
    total_revenue = kpis["total_revenue"]
    margin_pct = kpis["margin_pct"]
    avg_order_value = kpis["avg_order_value"]
    mom_growth = kpis["mom_growth"]

    s_margin = semaforo(margin_pct, "margin_pct")
    s_ticket = semaforo(avg_order_value, "avg_order_value")
    s_mom = semaforo(mom_growth, "mom_growth")

    # Semaforo globale = peggiore tra i 3 primari
    priority = {"🔴": 3, "🟡": 2, "🟢": 1, "⚪": 0}
    global_sem = max([s_margin, s_ticket, s_mom], key=lambda x: priority.get(x, 0))
    global_label = {"🟢": "Buona salute", "🟡": "Monitorare", "🔴": "Attenzione richiesta",
                    "⚪": "Dati insufficienti"}.get(global_sem, "")

    # Sommario
    sommario_parts = [f"Fatturato totale: {fmt_eur(total_revenue)} su {kpis['order_count']} ordini."]
    if margin_pct is not None:
        sommario_parts.append(f"Margine lordo: {fmt_pct(margin_pct)}.")
    if mom_growth is not None:
        sommario_parts.append(f"Crescita ultimo mese: {mom_growth:+.1f}%.")
    sommario = " ".join(sommario_parts)

    # Warning
    warning_block = ""
    if validation.warnings:
        items = "\n".join(f"- {w}" for w in validation.warnings)
        warning_block = items
    else:
        warning_block = "*Nessuna anomalia rilevata nella validazione.*"

    # Top prodotti
    prod_rows = []
    for i, (pid, rev) in enumerate(kpis["top_products"], 1):
        pct = rev / total_revenue * 100 if total_revenue > 0 else 0
        prod_rows.append(f"| {i} | {pid} | {fmt_eur(rev)} | {pct:.1f}% |")
    prod_table = "\n".join(prod_rows) if prod_rows else "| — | Nessun dato | — | — |"

    # Top clienti
    cust_section = ""
    if kpis["top_customers"]:
        rows_cust = []
        for i, (cid, rev) in enumerate(kpis["top_customers"], 1):
            pct = rev / total_revenue * 100 if total_revenue > 0 else 0
            conc = semaforo(pct, "top_customer_pct") if i == 1 else "—"
            rows_cust.append(f"| {i} | {cid} | {fmt_eur(rev)} | {pct:.1f}% | {conc} |")
        cust_section = (
            "## Top 5 Clienti per Fatturato\n\n"
            "| # | Cliente | Fatturato | % sul totale | Stato concentrazione |\n"
            "|---|---------|-----------|--------------|---------------------|\n"
            + "\n".join(rows_cust)
        )
    else:
        cust_section = "## Top 5 Clienti per Fatturato\n\n*Campo `customer_id` assente — dati non disponibili.*"

    # Categoria
    cat_section = ""
    if kpis["rev_by_category"]:
        cat_rows = []
        for cat, rev in kpis["rev_by_category"]:
            pct = rev / total_revenue * 100 if total_revenue > 0 else 0
            cat_rows.append(f"| {cat} | {fmt_eur(rev)} | {pct:.1f}% |")
        cat_section = (
            "## Fatturato per Categoria\n\n"
            "| Categoria | Fatturato | % sul totale |\n"
            "|-----------|-----------|----------|\n"
            + "\n".join(cat_rows)
        )
    else:
        cat_section = "## Fatturato per Categoria\n\n*Campo `category` assente — dati non disponibili.*"

    # Trend mensile
    trend_rows = []
    monthly = kpis["monthly_trend"]
    for i, (month, rev) in enumerate(monthly):
        if i == 0:
            var_str = "—"
        else:
            prev = monthly[i - 1][1]
            var = (rev - prev) / prev * 100 if prev > 0 else 0
            var_str = f"{var:+.1f}%"
        trend_rows.append(f"| {month} | {fmt_eur(rev)} | {var_str} |")
    trend_table = "\n".join(trend_rows) if trend_rows else "| — | Nessun dato | — |"

    chart, scala = mini_chart(monthly)
    chart_block = f"```\n{chart}\n```\n*(Mini-chart: ogni █ ≈ {scala})*" if chart else ""

    # Insight
    insight_text = "\n".join(f"{i+1}. {ins}" for i, ins in enumerate(insights))

    # Campi opzionali presenti
    optional_present = []
    if kpis["has_cost"]:
        optional_present.append("cost_price")
    if kpis["has_customer"]:
        optional_present.append("customer_id")
    if kpis["has_category"]:
        optional_present.append("category")

    report = f"""# 📊 Report Analisi Vendite

**File analizzato**: `{filepath.name}`
**Data analisi**: {datetime.today().strftime("%Y-%m-%d")}
**Periodo dati**: {kpis['date_start']} → {kpis['date_end']} ({kpis['days_covered']} giorni)
**Righe elaborate**: {validation.valid_rows} valide / {validation.total_rows} totali

---

## Sommario Esecutivo

{sommario}

**Stato complessivo**: {global_sem} {global_label}

---

## KPI Principali

| KPI | Valore | Stato |
|-----|--------|-------|
| Fatturato totale | {fmt_eur(total_revenue)} | — |
| Margine totale | {fmt_eur(kpis['total_margin'])} | — |
| Margine % | {fmt_pct(margin_pct)} | {s_margin} |
| Ticket medio | {fmt_eur(avg_order_value)} | {s_ticket} |
| Numero ordini | {kpis['order_count']} | — |
| Clienti unici | {kpis['unique_customers'] or 'N/D'} | — |
| Crescita MoM | {fmt_pct(mom_growth)} | {s_mom} |

---

## ⚠️ Warning Validazione

{warning_block}

---

## Top 5 Prodotti per Fatturato

| # | Prodotto | Fatturato | % sul totale |
|---|----------|-----------|--------------|
{prod_table}

---

{cust_section}

---

{cat_section}

---

## Trend Mensile

| Mese | Fatturato | Var. vs mese prec. |
|------|-----------|-------------------|
{trend_table}

{chart_block}

---

## Insight e Raccomandazioni

{insight_text}

---

## Metadati

| Campo | Valore |
|-------|--------|
| Script | `analizza_vendite.py` |
| Versione script | {VERSION} |
| Righe totali lette | {validation.total_rows} |
| Righe valide | {validation.valid_rows} |
| Righe scartate | {validation.skipped_rows} |
| Qualità dati | {semaforo(validation.quality_pct, 'data_quality_pct')} {validation.quality_pct:.1f}% |
| Margine calcolabile | {'Sì' if kpis['has_cost'] else 'No (cost_price assente)'} |
| Campi opzionali presenti | {', '.join(optional_present) or 'nessuno'} |
"""
    return report


# ─── Entry point ─────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analisi dati di vendita — logica a 4 fasi"
    )
    parser.add_argument("--input", required=True, help="Path al file CSV di input")
    parser.add_argument("--output", help="Path al file Markdown di output")
    parser.add_argument("--sep", default=",", help="Separatore CSV (default: ',')")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Esegui solo la validazione, non generare report",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERRORE: File non trovato: {input_path}", file=sys.stderr)
        sys.exit(1)

    # ── Fase 1: Validazione ──
    print(f"[1/4] Validazione: {input_path.name} …")
    validation, rows = validate_and_parse(input_path, args.sep)

    if validation.errors:
        print("\n⛔ ERRORI BLOCCANTI:")
        for e in validation.errors:
            print(f"  • {e}")

    if validation.warnings:
        print(f"\n⚠️  Warning ({len(validation.warnings)}):")
        for w in validation.warnings:
            print(f"  • {w}")

    if not validation.is_valid:
        print(
            f"\n❌ Validazione fallita: troppi errori bloccanti "
            f"({validation.skipped_rows}/{validation.total_rows} righe)."
        )
        sys.exit(2)

    print(
        f"   ✓ {validation.valid_rows}/{validation.total_rows} righe valide "
        f"({validation.quality_pct:.1f}%)"
    )

    if args.validate_only:
        print("\n✅ Validazione completata (--validate-only).")
        sys.exit(0)

    # ── Fase 2: Calcolo KPI ──
    print("[2/4] Calcolo KPI …")
    kpis = compute_kpis(rows)
    print(f"   ✓ Fatturato totale: {fmt_eur(kpis['total_revenue'])}")

    # ── Fase 3: Classificazione (integrata in generate_report) ──
    print("[3/4] Classificazione semaforo …")

    # ── Fase 4: Insight ──
    print("[4/4] Generazione insight …")
    insights = generate_insights(kpis)

    # ── Output ──
    report = generate_report(input_path, validation, kpis, insights)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"\n✅ Report salvato: {out_path}")
    else:
        print("\n" + report)


if __name__ == "__main__":
    main()
