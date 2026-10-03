#!/usr/bin/env python3
"""Check corpus/export consistency and report structure, without claiming to verify scientific conclusions."""
from __future__ import annotations
import argparse
import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from academic_core.http import atomic_json
from academic_core.model import normalize_text

def marked(text, name):
    match = re.search(r"<!--\s*" + name + r":start\s*-->(.*?)<!--\s*" + name + r":end\s*-->", text, re.S)
    return match[1] if match else ""

def words(text):
    text = re.sub(r"```.*?```|<!--.*?-->", "", text, flags=re.S)
    text = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("|"))
    text = re.sub(r"https?://\S+", "", text)
    return len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b", text, flags=re.UNICODE))

def balanced_bib(text):
    depth, escaped = 0, False
    for char in text:
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0

def audit(directory, report=None, mode="simple", insufficient_reason=""):
    directory = Path(directory)
    errors, warnings, stats = [], [], {}
    required = ("registros.json", "referencias.csv", "referencias.bib", "referencias.csl.json", "bibliografia_completa.md", "matriz_evidencias.csv", "manifesto_busca.json")
    for name in required:
        if not (directory / name).exists():
            errors.append("missing_file " + name)
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings, "stats": stats}
    records = json.loads((directory / "registros.json").read_text(encoding="utf-8"))
    ids = [r["record_id"] for r in records]
    if len(ids) != len(set(ids)):
        errors.append("duplicate_record_ids")
    with (directory / "referencias.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if {row["record_id"] for row in rows} != set(ids) or len(rows) != len(records):
        errors.append("csv_corpus_mismatch")
    bib = (directory / "referencias.bib").read_text(encoding="utf-8")
    keys = re.findall(r"^@\w+\{([^,\n]+),", bib, flags=re.M)
    if len(keys) != len(records) or len(set(keys)) != len(keys):
        errors.append("bibtex_count_or_key_mismatch")
    if set(keys) != {"ref" + rid[1:] for rid in ids}:
        errors.append("bibtex_corpus_key_mismatch")
    if not balanced_bib(bib):
        errors.append("unbalanced_bibtex")
    csl = json.loads((directory / "referencias.csl.json").read_text(encoding="utf-8"))
    if {r["id"] for r in csl} != set(ids) or len(csl) != len(records):
        errors.append("csl_corpus_mismatch")
    bibliography = (directory / "bibliografia_completa.md").read_text(encoding="utf-8")
    for r in records:
        if normalize_text(r["title"]) not in normalize_text(bibliography):
            errors.append("bibliography_missing_record " + r["record_id"])
        if r.get("missing_fields"):
            warnings.append("metadata_pending " + r["record_id"])
        if r.get("selection") == "included" and any(not reason.endswith("unverified") for reason in r.get("eligibility_checks", [])):
            errors.append("included_record_outside_configured_scope " + r["record_id"])
    stats.update(records=len(records), included=sum(r.get("selection") == "included" for r in records), missing_year=sum(not r.get("year") for r in records))
    if report:
        text = Path(report).read_text(encoding="utf-8")
        if re.search(r"\[(?:preencher|inserir|Escrever|Título descritivo|Tema da busca)", text, re.I):
            errors.append("unfilled_report_template")
        final_bib = marked(text, "bibliography")
        if not final_bib:
            errors.append("missing_bibliography_markers")
        else:
            norm = normalize_text(final_bib)
            for r in records:
                if normalize_text(r["title"]) not in norm:
                    errors.append("report_bibliography_missing_record " + r["record_id"])
                if r.get("url") and r["url"] not in final_bib and (not r.get("doi") or "https://doi.org/" + r["doi"] not in final_bib):
                    errors.append("report_bibliography_missing_url " + r["record_id"])
        if mode == "deep":
            narrative = marked(text, "narrative")
            executive = marked(text, "executive")
            top = marked(text, "top20")
            stats.update(narrative_words=words(narrative), executive_words=words(executive))
            if not narrative or not executive:
                errors.append("missing_deep_report_markers")
            if not insufficient_reason:
                if not 2000 <= stats["narrative_words"] <= 5000:
                    errors.append("deep_narrative_outside_2000_5000_words")
                if not 300 <= stats["executive_words"] <= 650:
                    errors.append("executive_outside_one_page_approximation")
                if not stats["included"]:
                    errors.append("no_included_corpus_for_complete_deep_review")
            if not re.search(r"^\|.*\|", marked(text, "summary"), re.M):
                errors.append("missing_summary_table")
            top_ids = re.findall(r"\bR[0-9a-f]{16}\b", top)
            expected = min(20, stats["included"])
            if len(top_ids) != expected or len(set(top_ids)) != len(top_ids):
                errors.append("top20_count_or_duplicate_mismatch")
            included = {r["record_id"] for r in records if r.get("selection") == "included"}
            if any(rid not in included for rid in top_ids):
                errors.append("top20_contains_nonincluded_record")
            figures = directory / "figuras" / "manifesto_figuras.json"
            if not figures.exists():
                errors.append("missing_figures_manifest_or_documented_limit")
            else:
                fig = json.loads(figures.read_text(encoding="utf-8"))
                for name in fig.get("figures", []):
                    path = figures.parent / name
                    if not path.exists():
                        errors.append("missing_figure " + name)
                    elif path.suffix == ".svg":
                        try:
                            ET.parse(path)
                        except ET.ParseError:
                            errors.append("invalid_svg " + name)
            if insufficient_reason:
                warnings.append("incomplete_deep_investigation " + insufficient_reason)
    return {"ok": not errors, "errors": errors, "warnings": warnings, "stats": stats, "insufficient_reason": insufficient_reason,
            "limit": "Structural checks do not verify claim support, thematic classification or style compliance"}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--directory", required=True); p.add_argument("--report")
    p.add_argument("--mode", choices=("simple", "deep"), default="simple")
    p.add_argument("--insufficient-reason", default="")
    args = p.parse_args()
    try:
        result = audit(args.directory, args.report, args.mode, args.insufficient_reason)
        atomic_json(Path(args.directory) / "auditoria_entrega.json", result)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["ok"] else 1
    except (OSError, ValueError, KeyError) as exc:
        print("ERROR " + str(exc)); return 1

if __name__ == "__main__":
    raise SystemExit(main())
