"""Lossless JSON/CSV, BibTeX/CSL JSON and reviewable reference lists."""
from __future__ import annotations
import csv
import hashlib
import json
import re
from pathlib import Path
from .http import atomic_json
from .model import canonical, clean, normalize_text

CSV_FIELDS = ["record_id", "title", "authors", "authors_json", "editors_json", "year", "publication_date", "document_type", "container_title", "publisher", "publisher_place", "edition", "series", "event_title", "event_location", "event_date", "institution", "degree", "accessed_date", "volume", "issue", "pages", "article_number", "doi", "url", "pdf_urls", "abstract", "keywords", "language", "issn", "isbn", "is_oa", "oa_status", "retracted", "licenses", "affiliations_json", "countries", "brazil_affiliation", "brazil_topic", "brazil_venue", "sources", "source_ids_json", "citations_by_source_json", "reading_level", "selection", "exclusion_reason", "study_kind", "themes", "missing_fields", "metadata_conflicts_json", "provenance_json", "notes", "metadata_json"]

def csv_safe(value):
    text = "" if value is None else str(value)
    # Preserve the exact original in JSON, while preventing spreadsheet formulas.
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@")) else text

def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)

def write_csv(records, path):
    with Path(path).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in records:
            row = {key: r.get(key, "") for key in CSV_FIELDS}
            row.update(authors=" | ".join(a.get("name", "") for a in r["authors"]), authors_json=dump(r["authors"]),
                       editors_json=dump(r["editors"]),
                       affiliations_json=dump(r["affiliations"]), source_ids_json=dump(r["source_ids"]),
                       citations_by_source_json=dump(r["citations_by_source"]), metadata_conflicts_json=dump(r["metadata_conflicts"]),
                       provenance_json=dump(r["provenance"]), metadata_json=dump(r.get("metadata_by_source", {})))
            for key, value in row.items():
                if isinstance(value, (list, dict)):
                    row[key] = dump(value)
            writer.writerow({key: csv_safe(value) for key, value in row.items()})

def tex_escape(value):
    replacements = {"\\": r"{\textbackslash}", "{": r"\{", "}": r"\}", "%": r"\%", "&": r"\&", "#": r"\#", "_": r"\_", "$": r"\$", "~": r"{\textasciitilde}", "^": r"{\textasciicircum}"}
    return "".join(replacements.get(c, c) for c in str(value))

def bib_people(entries):
    names = []
    for a in entries:
        name = (a.get("family", "") + ", " + a.get("given", "")).rstrip(", ") if a.get("family") else a.get("name", "")
        if name:
            names.append("{" + tex_escape(name) + "}" if a.get("literal") else tex_escape(name))
    return " and ".join(names)

def bib_entry(r):
    kind = {"article": "article", "review": "article", "conference-paper": "inproceedings", "book-chapter": "incollection", "book": "book", "thesis": "phdthesis" if r.get("degree") == "doctoral" else "mastersthesis" if r.get("degree") == "masters" else "misc"}.get(r["document_type"], "misc")
    key = "ref" + r["record_id"][1:]
    values = {"title": r["title"], "year": r["year"], "doi": r["doi"], "url": r["url"], "publisher": r["publisher"],
              "volume": r["volume"], "number": r["issue"], "pages": r["pages"], "eid": r["article_number"], "abstract": r["abstract"],
              "keywords": ", ".join(map(str, r["keywords"])), "language": r["language"], "issn": ", ".join(map(str, r["issn"])), "isbn": ", ".join(map(str, r["isbn"]))}
    values.update(edition=r["edition"], series=r["series"], address=r["publisher_place"], eventtitle=r["event_title"],
                  venue=r["event_location"], eventdate=r["event_date"], school=r["institution"], urldate=r["accessed_date"])
    values["journal" if kind == "article" else "booktitle" if kind in ("inproceedings", "incollection") else "howpublished"] = r["container_title"]
    fields = []
    for k, v in values.items():
        if v not in (None, ""):
            value = str(v).replace("{", "%7B").replace("}", "%7D") if k in ("doi", "url") else tex_escape(v)
            fields.append(f"  {k} = {{{value}}}")
    for field, entries in (("author", r["authors"]), ("editor", r["editors"])):
        names = bib_people(entries)
        if names:
            fields.insert(1, "  " + field + " = {" + names + "}")
    if r["pdf_urls"]:
        fields.append("  pdf = {" + r["pdf_urls"][0].replace("{", "%7B").replace("}", "%7D") + "}")
    fields.append("  note = {" + tex_escape("Record " + r["record_id"] + ". Sources " + ", ".join(r["sources"])) + "}")
    return "@" + kind + "{" + key + ",\n" + ",\n".join(fields) + "\n}\n"

def csl_item(r):
    types = {"article": "article-journal", "review": "article-journal", "conference-paper": "paper-conference", "book-chapter": "chapter", "thesis": "thesis", "book": "book"}
    authors = []
    for a in r["authors"]:
        authors.append({"family": a["family"], "given": a.get("given", "")} if a.get("family") else {"literal": a.get("name", "")})
    item = {"id": r["record_id"], "type": types.get(r["document_type"], "article"), "title": r["title"], "author": authors,
            "container-title": r["container_title"], "publisher": r["publisher"], "volume": r["volume"], "issue": r["issue"], "page": r["pages"], "DOI": r["doi"], "URL": r["url"], "abstract": r["abstract"], "language": r["language"], "ISSN": r["issn"], "ISBN": r["isbn"]}
    item.update(editor=[{"family": a["family"], "given": a.get("given", "")} if a.get("family") else {"literal": a.get("name", "")} for a in r["editors"]])
    item.update({"publisher-place": r["publisher_place"], "edition": r["edition"], "collection-title": r["series"],
                 "event-title": r["event_title"], "event-place": r["event_location"], "number": r["article_number"]})
    if r["year"]:
        parts = [r["year"]]
        if re.fullmatch(r"\d{4}-\d{2}(?:-\d{2})?", r["publication_date"]):
            candidate = list(map(int, r["publication_date"].split("-")))
            if candidate[0] == r["year"] and 1 <= candidate[1] <= 12 and (len(candidate) < 3 or 1 <= candidate[2] <= 31):
                parts = candidate
        item["issued"] = {"date-parts": [parts]}
    return {k: v for k, v in item.items() if v not in (None, "", [], {})}

def choose_style(config, records):
    explicit = config.get("citation_style", "auto")
    if explicit in ("apa", "abnt"):
        return explicit
    languages = set(config.get("languages") or [])
    if languages:
        return "abnt" if languages == {"pt"} else "apa"
    known = {r["language"] for r in records if r["language"]}
    return "abnt" if known == {"pt"} and all(r["language"] for r in records) else "apa"

def author_display(a, style):
    if a.get("family"):
        if style == "abnt":
            return a["family"].upper() + (", " + a["given"] if a.get("given") else "")
        initials = " ".join(word[0].upper() + "." for word in a.get("given", "").split() if word)
        return a["family"] + (", " + initials if initials else "")
    return a.get("name", "")

def reference(r, style):
    names = [author_display(a, style) for a in r["authors"] if a.get("name") or a.get("family")]
    if style == "apa" and len(names) > 20:
        names = names[:19] + ["…", names[-1]]
    author = ("; " if style == "abnt" else ", ").join(names)
    if style == "apa" and 1 < len(names) <= 20:
        author = ", ".join(names[:-1]) + ", & " + names[-1]
    year = str(r["year"]) if r["year"] else "s.d." if style == "abnt" else "n.d."
    prefix = author + ". " if author else ""
    chapter = r["document_type"] in ("book-chapter", "conference-paper")
    editors = [author_display(a, style) for a in r["editors"]]
    if style == "apa":
        text = prefix + "(" + year + "). " + r["title"] + "."
        if chapter:
            if r["container_title"]:
                text += " In "
                if editors:
                    display = []
                    for a in r["editors"]:
                        initials = " ".join(w[0].upper() + "." for w in a.get("given", "").split() if w)
                        display.append((initials + " " + a["family"]).strip() if a.get("family") else a["name"])
                    text += ", ".join(display) + (" (Ed.), " if len(display) == 1 else " (Eds.), ")
                text += "*" + r["container_title"] + "*"
                details = []
                if r["edition"]:
                    details.append("edition " + r["edition"])
                if r["pages"]:
                    details.append("pp. " + r["pages"])
                if details:
                    text += " (" + ", ".join(details) + ")"
                text += "."
            elif r["event_title"]:
                text += " " + r["event_title"] + "."
            if r["publisher"]:
                text += " " + r["publisher"] + "."
        elif r["document_type"] == "thesis":
            degree = {"doctoral": "Doctoral dissertation", "masters": "Master's thesis"}.get(r["degree"], "Thesis, degree not verified")
            text += " [" + degree + (", " + r["institution"] if r["institution"] else "") + "]."
        elif r["document_type"] == "book":
            if r["edition"]:
                text += " (edition " + r["edition"] + ")."
            if r["publisher"]:
                text += " " + r["publisher"] + "."
        elif r["container_title"]:
            text += " *" + r["container_title"] + "*"
            if r["volume"]:
                text += ", *" + r["volume"] + "*"
            if r["issue"]:
                text += "(" + r["issue"] + ")"
            if r["pages"]:
                text += ", " + r["pages"]
            elif r["article_number"]:
                text += ", Article " + r["article_number"]
            text += "."
    else:
        text = prefix + r["title"] + "."
        if chapter:
            text += " In: "
            if editors:
                text += "; ".join(editors) + " (org.). "
            text += "*" + (r["container_title"] or r["event_title"] or "[Veículo não recuperado]") + "*."
            if r["edition"]:
                text += " " + r["edition"] + ". ed."
            location = r["publisher_place"] or r["event_location"]
            if location or r["publisher"]:
                text += " " + ((location + ": ") if location else "") + r["publisher"] + ", " + year + "."
            else:
                text += " " + year + "."
            if r["pages"]:
                text += " p. " + r["pages"] + "."
        elif r["document_type"] == "thesis":
            degree = {"doctoral": "Tese (Doutorado)", "masters": "Dissertação (Mestrado)"}.get(r["degree"], "Trabalho acadêmico, grau não verificado")
            text += " " + year + ". " + degree + (" — " + r["institution"] if r["institution"] else "") + "."
        else:
            if r["container_title"]:
                text += " *" + r["container_title"] + "*"
            if r["volume"]:
                text += ", v. " + r["volume"]
            if r["issue"]:
                text += ", n. " + r["issue"]
            if r["pages"]:
                text += ", p. " + r["pages"]
            elif r["article_number"]:
                text += ", " + r["article_number"]
            if r["document_type"] == "book" and r["publisher"]:
                text += " " + ((r["publisher_place"] + ": ") if r["publisher_place"] else "") + r["publisher"]
            text += ", " + year + "."
    links = []
    if r["doi"]:
        links.append("https://doi.org/" + r["doi"])
    if r["url"] and r["url"] not in links:
        links.append(r["url"])
    text += (" " + " | ".join(links) if links else " [URL não recuperada]")
    if style == "abnt" and r["accessed_date"]:
        text += " Acesso em: " + r["accessed_date"] + "."
    return text

def export_all(records, out, config, manifest=None):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    records = [canonical(r) for r in records]
    atomic_json(out / "registros.json", records)
    write_csv(records, out / "referencias.csv")
    (out / "referencias.bib").write_text("\n".join(bib_entry(r) for r in records), encoding="utf-8")
    atomic_json(out / "referencias.csl.json", [csl_item(r) for r in records])
    style = choose_style(config, records)
    # Automated formatting cannot verify publication facts or decide every style convention.
    bibliography = "# Bibliografia completa\n\nEstilo " + style.upper() + ". Conferir nomes, versões e campos ausentes antes da entrega final.\n\n"
    for r in sorted(records, key=lambda x: normalize_text(x["authors"][0].get("name") if x["authors"] else x["title"])):
        bibliography += "- " + reference(r, style) + "\n"
    (out / "bibliografia_completa.md").write_text(bibliography, encoding="utf-8")
    missing = [{"record_id": r["record_id"], "missing_fields": r["missing_fields"], "metadata_conflicts": r["metadata_conflicts"], "reading_level": r["reading_level"]} for r in records if r["missing_fields"] or r["metadata_conflicts"]]
    atomic_json(out / "pendencias_metadados.json", missing)
    evidence_fields = ["record_id", "title", "selection", "exclusion_reason", "reading_level", "study_kind", "themes", "method", "main_finding", "supports", "contradicts", "limitations", "locator", "url"]
    with (out / "matriz_evidencias.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=evidence_fields)
        writer.writeheader()
        for r in records:
            writer.writerow({k: csv_safe(dump(r[k]) if isinstance(r.get(k), (list, dict)) else r.get(k)) for k in evidence_fields})
    if manifest is not None:
        atomic_json(out / "manifesto_busca.json", manifest)
    checksums = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name != "checksums.json"}
    atomic_json(out / "checksums.json", checksums)
    return {"records": len(records), "citation_style": style, "metadata_pending": len(missing)}
