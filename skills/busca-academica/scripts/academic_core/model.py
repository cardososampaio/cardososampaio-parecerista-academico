"""Canonical records, conservative deduplication and explicit eligibility."""
from __future__ import annotations
import hashlib
import html
import json
import re
import unicodedata
from copy import deepcopy
from difflib import SequenceMatcher
from urllib.parse import unquote, urlsplit

DEFAULT_TYPES = {"article", "review"}
TYPE_MAP = {"journal-article": "article", "article": "article", "review": "review",
            "proceedings-article": "conference-paper", "conference-paper": "conference-paper",
            "conference": "conference-paper", "book-chapter": "book-chapter",
            "book-section": "book-chapter", "posted-content": "preprint", "preprint": "preprint",
            "dissertation": "thesis", "thesis": "thesis"}
LANGUAGE_ALIASES = {"por": "pt", "portuguese": "pt", "português": "pt", "eng": "en", "english": "en", "inglês": "en",
                    "spa": "es", "spanish": "es", "español": "es", "espanhol": "es", "fre": "fr", "fra": "fr", "french": "fr",
                    "deu": "de", "ger": "de", "german": "de", "ita": "it", "italian": "it", "pol": "pl", "rus": "ru",
                    "zho": "zh", "chi": "zh", "jpn": "ja", "ara": "ar"}

def clean(value):
    return re.sub(r"\s+", " ", html.unescape(str(value or ""))).strip()

def normalize_text(value):
    text = unicodedata.normalize("NFKD", clean(value)).casefold()
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^\w]+", " ", text).strip()

def normalize_doi(value):
    text = unquote(clean(value))
    text = re.sub(r"^https?://(?:dx\.)?doi\.org/|^doi\s*:\s*", "", text, flags=re.I)
    # Parentheses are legal inside DOIs. Do not strip them indiscriminately.
    return text.rstrip(".,;").lower() if re.match(r"^10\.\d{4,9}/\S+$", text, re.I) else ""

def public_url(value):
    value = clean(value)
    try:
        p = urlsplit(value)
        return value if p.scheme in ("https", "http") and p.hostname and not p.username and not p.password else ""
    except ValueError:
        return ""

def as_list(value):
    return value if isinstance(value, list) else ([] if value in (None, "") else [value])

def unique(items):
    out, seen = [], set()
    for item in items:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out

def people(value):
    if isinstance(value, str):
        value = [a.strip() for a in value.split(";") if a.strip()]
    entries = [({"name": clean(a)} if isinstance(a, str) else deepcopy(a)) for a in as_list(value)]
    result = []
    for a in entries:
        if not isinstance(a, dict):
            continue
        a["name"] = clean(a.get("name") or " ".join(filter(None, [a.get("given"), a.get("family")])))
        if a.get("name") or a.get("family"):
            result.append(a)
    return result

def canonical(record):
    r = deepcopy(record)
    r["title"] = clean(r.get("title") or r.get("titulo"))
    r["doi"] = normalize_doi(r.get("doi"))
    year = r.get("year") or r.get("ano")
    try:
        r["year"] = int(year) if year is not None and str(year).strip() else None
    except (TypeError, ValueError):
        r["year"] = None
    if r["year"] is not None and not 1400 <= r["year"] <= 2200:
        r.setdefault("notes", []).append("Invalid publication year retained in raw metadata")
        r["year"] = None
    r["authors"] = people(r.get("authors") or r.get("autores"))
    r["editors"] = people(r.get("editors"))
    raw_type = r.get("document_type") or r.get("type") or "unknown"
    r["document_type"] = TYPE_MAP.get(raw_type, raw_type)
    for field in ("container_title", "publisher", "publisher_place", "edition", "series", "event_title", "event_location", "event_date", "institution", "degree", "accessed_date", "publication_date", "volume", "issue", "pages", "article_number", "language", "abstract"):
        r[field] = clean(r.get(field))
    language = r["language"].lower()
    r["language"] = LANGUAGE_ALIASES.get(language, language)
    if re.fullmatch(r"[a-z]{2}[-_][a-z]{2}", r["language"]):
        r["language"] = r["language"][:2]
    for field in ("keywords", "issn", "isbn", "pdf_urls", "licenses", "affiliations", "countries", "themes", "sources", "provenance", "notes"):
        r[field] = unique(as_list(r.get(field)))
    r["url"] = public_url(r.get("url")) or ("https://doi.org/" + r["doi"] if r["doi"] else "")
    r["pdf_urls"] = unique([public_url(x) for x in r["pdf_urls"] if public_url(x)])
    r.setdefault("source_ids", {})
    r.setdefault("citations_by_source", {})
    r.setdefault("metadata_by_source", {})
    r.setdefault("metadata_conflicts", [])
    r.setdefault("reading_level", "metadata")
    r.setdefault("selection", "unassessed")
    r.setdefault("exclusion_reason", "")
    r.setdefault("study_kind", "unassessed")
    r.setdefault("brazil_topic", None)
    r.setdefault("brazil_venue", None)
    r.setdefault("is_oa", None)
    r["brazil_affiliation"] = ("BR" in r["countries"]) if r["countries"] else r.get("brazil_affiliation")
    r["missing_fields"] = [f for f in ("title", "authors", "year", "container_title", "doi", "url", "abstract", "language") if r.get(f) in (None, "", [])]
    if not r.get("record_id"):
        # Include authors and source identifiers. Equal titles alone are not unique IDs.
        key = {f: r.get(f) for f in ("title", "authors", "year", "doi", "source_ids", "url", "document_type")}
        r["record_id"] = "R" + hashlib.sha256(json.dumps(key, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]
    return r

def author_keys(r):
    # Surname alone is insufficient: unrelated authors can share "Silva".
    names = [(normalize_text(a.get("name") or " ".join(filter(None, [a.get("given"), a.get("family")]))), a) for a in r.get("authors", [])]
    return {name for name, author in names if name and (len(name.split()) >= 2 or author.get("literal"))}

def merge_records(a, b):
    out = deepcopy(a)
    list_fields = {"sources", "provenance", "pdf_urls", "keywords", "issn", "isbn", "affiliations", "countries", "licenses", "notes", "themes"}
    for k, v in b.items():
        if k in list_fields:
            out[k] = unique(out.get(k, []) + v)
        elif k in ("source_ids", "citations_by_source"):
            out.setdefault(k, {}).update(v)
        elif k == "metadata_by_source":
            for source, values in v.items():
                out.setdefault(k, {})[source] = unique(out.get(k, {}).get(source, []) + as_list(values))
        elif k not in ("record_id", "missing_fields", "metadata_conflicts"):
            if out.get(k) in (None, "", [], {}):
                out[k] = deepcopy(v)
            elif v not in (None, "", [], {}) and out[k] != v and k in ("title", "authors", "editors", "year", "document_type", "container_title", "volume", "issue", "pages", "publisher", "publisher_place", "edition", "event_title"):
                conflict = {"field": k, "kept": out[k], "alternative": v, "sources": b.get("sources", [])}
                out.setdefault("metadata_conflicts", []).append(conflict)
    out["metadata_conflicts"] = unique(out.get("metadata_conflicts", []) + b.get("metadata_conflicts", []))
    return canonical(out)

def deduplicate(records):
    result, candidates, doi_index = [], [], {}
    for original in records:
        r = canonical(original)
        if r["doi"] and r["doi"] in doi_index:
            ix = doi_index[r["doi"]]
            result[ix] = merge_records(result[ix], r)
            continue
        source_match = None
        for ix, prior in enumerate(result):
            if prior["doi"] and r["doi"] and prior["doi"] != r["doi"]:
                continue
            stable_sources = ("openalex", "scielo", "doaj", "crossref", "semantic_scholar", "bdtd")
            if any(r["source_ids"].get(s) and r["source_ids"].get(s) == prior["source_ids"].get(s) for s in stable_sources):
                source_match = ix
                break
        if source_match is not None:
            result[source_match] = merge_records(result[source_match], r)
            if r["doi"]:
                doi_index[r["doi"]] = source_match
            continue
        if not r["title"]:
            # Incomplete source records remain exportable for metadata repair.
            if r["doi"]:
                doi_index[r["doi"]] = len(result)
            result.append(r)
            continue
        match = None
        for ix, prior in enumerate(result):
            if prior["doi"] and r["doi"] and prior["doi"] != r["doi"]:
                continue
            # Different versions and document types stay separate without an identical DOI.
            if prior["document_type"] != r["document_type"]:
                continue
            shared_authors = bool(author_keys(prior) & author_keys(r))
            same_year = r["year"] is not None and r["year"] == prior["year"]
            compatible_venue = not (r["container_title"] and prior["container_title"]) or normalize_text(r["container_title"]) == normalize_text(prior["container_title"])
            similarity = SequenceMatcher(None, normalize_text(prior["title"]), normalize_text(r["title"])).ratio()
            if same_year and shared_authors and compatible_venue and similarity == 1:
                match = ix
                break
            if similarity >= .94:
                candidates.append({"left": prior["record_id"], "right": r["record_id"], "similarity": round(similarity, 4), "action": "manual_review"})
        if match is not None:
            result[match] = merge_records(result[match], r)
            if r["doi"]:
                doi_index[r["doi"]] = match
        else:
            if r["doi"]:
                doi_index[r["doi"]] = len(result)
            result.append(r)
    return result, unique(candidates)

def eligibility(r, config):
    reasons = []
    if not r["title"] or not r["authors"]:
        reasons.append("bibliographic_identity_unverified")
    permitted = set(config.get("types") or DEFAULT_TYPES)
    if r["document_type"] not in permitted:
        reasons.append("document_type_outside_scope" if r["document_type"] != "unknown" else "document_type_unverified")
    if r["year"] is None:
        if config.get("year_start") or config.get("year_end"):
            reasons.append("year_unverified")
    elif ((config.get("year_start") and r["year"] < config["year_start"]) or
          (config.get("year_end") and r["year"] > config["year_end"])):
        reasons.append("year_outside_scope")
    languages = config.get("languages") or []
    if languages and not r["language"]:
        reasons.append("language_unverified")
    elif languages and r["language"].lower() not in languages:
        reasons.append("language_outside_scope")
    return reasons
