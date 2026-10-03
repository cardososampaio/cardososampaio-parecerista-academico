#!/usr/bin/env python3
"""Generate exact SVG charts and their CSV data, with no optional dependencies."""
from __future__ import annotations
import argparse
import csv
import html
import json
from collections import Counter
from datetime import date
from pathlib import Path
from academic_search import load_records
from academic_core.model import canonical
from academic_core.http import atomic_json

def svg_start(title, width=1040, height=540):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
            f'<title>{html.escape(title)}</title>', '<rect width="100%" height="100%" fill="#ffffff"/>',
            '<style>text{font-family:Arial,sans-serif;fill:#20334b} .label{font-size:15px} .small{font-size:12px} .heading{font-size:22px;font-weight:bold}</style>',
            f'<text x="55" y="40" class="heading">{html.escape(title)}</text>']

def temporal_chart(counts, path, kind, current_year, start=None, end=None):
    first, last = start or min(counts), end or max(counts)
    if first > last or first > min(counts) or last < max(counts):
        raise ValueError("Chart range must include every verified year in its selected population")
    years = list(range(first, last + 1))
    if len(years) > 70:
        raise ValueError("Temporal range exceeds 70 years; aggregate by decade before plotting")
    width = max(1040, len(years) * 32 + 160)
    parts = svg_start("Produção recuperada por ano", width)
    left, top, graphw, graphh = 70, 90, width - 130, 335
    peak = max(counts.values()) or 1
    step = graphw / len(years)
    for t in range(6):
        y = top + graphh * (1 - t / 5)
        parts.append(f'<line x1="{left}" y1="{y}" x2="{left + graphw}" y2="{y}" stroke="#e2e7ed"/>')
        parts.append(f'<text x="{left-10}" y="{y+5}" text-anchor="end" class="label">{round(peak*t/5,1):g}</text>')
    points = []
    for i, year in enumerate(years):
        x, n = left + step * (i + .5), counts.get(year, 0)
        y = top + graphh * (1 - n / peak)
        color = "#c8922a" if year == current_year else "#0d7b6e"
        if kind == "bar":
            parts.append(f'<rect x="{x-step*.34}" y="{y}" width="{step*.68}" height="{top+graphh-y}" fill="{color}"><title>{year} {n} documentos</title></rect>')
        else:
            points.append(f"{x},{y}")
            parts.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"><title>{year} {n} documentos</title></circle>')
        if len(years) <= 28 or i % max(1, len(years)//20) == 0:
            parts.append(f'<text x="{x}" y="450" text-anchor="middle" class="small">{year}</text>')
    if kind == "line":
        parts.append('<polyline points="' + " ".join(points) + '" fill="none" stroke="#0d7b6e" stroke-width="2.5"/>')
    footnote = "Corpus deduplicado recuperado. Ausência na busca não demonstra ausência de produção."
    parts.append(f'<text x="55" y="488" class="small">{html.escape(footnote)}</text>')
    if current_year in years:
        parts.append(f'<text x="55" y="509" class="small">{current_year} é um ano em curso. Não comparar sua contagem como se fosse um ano completo.</text>')
    parts.append("</svg>")
    Path(path).write_text("\n".join(parts), encoding="utf-8")

def heatmap(matrix, path, title):
    rows = sorted(matrix)
    years = sorted({year for counts in matrix.values() for year in counts})
    if len(rows) > 30 or len(years) > 35:
        raise ValueError("Heatmap exceeds readable dimensions; reduce categories or aggregate years")
    cellw, cellh, left, top = 54, 36, 290, 100
    width, height = max(1040, left + len(years)*cellw + 50), max(360, top + len(rows)*cellh + 100)
    parts = svg_start(title, width, height)
    peak = max((n for counts in matrix.values() for n in counts.values()), default=1) or 1
    for j, year in enumerate(years):
        parts.append(f'<text x="{left+j*cellw+cellw/2}" y="82" text-anchor="middle" class="small">{year}</text>')
    for i, row in enumerate(rows):
        shown = row[:36] + "…" if len(row) > 36 else row
        parts.append(f'<text x="{left-12}" y="{top+i*cellh+24}" text-anchor="end" class="label">{html.escape(shown)}<title>{html.escape(row)}</title></text>')
        for j, year in enumerate(years):
            n = matrix[row].get(year, 0)
            ratio = n/peak
            rgb = tuple(round(a + ratio*(b-a)) for a, b in zip((241, 245, 248), (13, 123, 110)))
            color = "#" + "".join(f"{c:02x}" for c in rgb)
            x, y = left+j*cellw, top+i*cellh
            parts.append(f'<rect x="{x}" y="{y}" width="{cellw-2}" height="{cellh-2}" fill="{color}"><title>{html.escape(row)} {year} {n}</title></rect>')
            textcolor = "#ffffff" if ratio > .60 else "#20334b"
            parts.append(f'<text x="{x+cellw/2}" y="{y+23}" text-anchor="middle" style="fill:{textcolor};font-size:14px">{n}</text>')
    parts.append(f'<text x="55" y="{height-55}" class="small">Cor clara 0. Cor mais escura {peak}. Categorias podem se sobrepor.</text>')
    parts.append(f'<text x="55" y="{height-32}" class="small">Contagens descrevem os documentos recuperados, sem estimar a produção total do campo.</text>')
    parts.append("</svg>")
    Path(path).write_text("\n".join(parts), encoding="utf-8")

def generate(records, out, population="included", start=None, end=None):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    records = [canonical(r) for r in records]
    if population == "included":
        records = [r for r in records if r["selection"] == "included"]
    elif population == "candidates":
        records = [r for r in records if r["selection"] in ("candidate", "included")]
    valid = [r for r in records if r["year"] is not None]
    counts = Counter(r["year"] for r in valid)
    result = {"population": population, "records": len(records), "missing_year": len(records)-len(valid), "figures": [], "limitations": []}
    with (out / "producao_por_ano.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f); writer.writerow(["year", "records"])
        if counts:
            first, last = start or min(counts), end or max(counts)
            grid = range(first, last+1) if first <= min(counts) <= max(counts) <= last and last-first < 70 else sorted(counts)
            for year in grid:
                writer.writerow([year, counts.get(year, 0)])
    if counts:
        kinds = ("bar", "line") if len(counts) >= 2 else ("bar",)
        if len(counts) < 2:
            result["limitations"].append("Line chart omitted because fewer than two verified publication years were recovered")
        for kind in kinds:
            path = out / ("producao_" + kind + ".svg")
            try:
                temporal_chart(counts, path, kind, date.today().year, start, end)
                result["figures"].append(path.name)
            except ValueError as exc:
                if str(exc) not in result["limitations"]:
                    result["limitations"].append(str(exc))
        for field, title in (("sources", "Fontes de recuperação por ano"), ("themes", "Temas atribuídos na leitura por ano")):
            matrix = {}
            for r in valid:
                for cat in set(r[field]):
                    matrix.setdefault(str(cat), Counter())[r["year"]] += 1
            if matrix:
                path = out / ("heatmap_" + field + ".svg")
                try:
                    heatmap(matrix, path, title)
                    result["figures"].append(path.name)
                except ValueError as exc:
                    result["limitations"].append(str(exc))
                with (out / ("heatmap_" + field + ".csv")).open("w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.writer(f); writer.writerow([field, "year", "records"])
                    grid_years = sorted({year for values in matrix.values() for year in values})
                    for cat, values in sorted(matrix.items()):
                        for year in grid_years: writer.writerow([cat, year, values.get(year, 0)])
    else:
        result["limitations"].append("No records with a verified year in the selected population")
    atomic_json(out / "manifesto_figuras.json", result)
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True); p.add_argument("--out", required=True)
    p.add_argument("--population", choices=("included", "candidates", "all"), default="included")
    p.add_argument("--year-start", type=int); p.add_argument("--year-end", type=int)
    args = p.parse_args()
    try:
        result = generate(load_records(args.input), args.out, args.population, args.year_start, args.year_end)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError) as exc:
        print("ERROR " + str(exc)); return 1

if __name__ == "__main__":
    raise SystemExit(main())
