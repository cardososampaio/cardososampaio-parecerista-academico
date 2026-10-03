"""Source adapters. A failed lookup never becomes a successful empty search."""
from __future__ import annotations
import json
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import quote, urljoin
from .http import blocked, now
from .model import canonical, clean, normalize_doi, as_list, public_url, TYPE_MAP

PRIMARY = ("openalex", "scielo", "doaj")
SECONDARY = ("crossref", "semantic_scholar")
ALL_SOURCES = PRIMARY + SECONDARY + ("bdtd",)
LANGS = {"portuguese": "pt", "português": "pt", "english": "en", "inglês": "en", "spanish": "es", "español": "es", "espanhol": "es"}

@dataclass
class SearchResult:
    source: str
    query: str
    status: str = "ok"
    records: list = field(default_factory=list)
    reported_total: int | None = None
    truncated: bool = False
    complete: bool = False
    error: str = ""
    raw_paths: list = field(default_factory=list)
    retrieved_at: str = field(default_factory=now)
    def manifest(self):
        return {k: v for k, v in self.__dict__.items() if k != "records"} | {"retrieved_count": len(self.records)}

def failure(response):
    if response.status in (401, 403):
        return "blocked", "authentication_or_access_denied"
    if response.status == 429:
        return "rate_limited", "request_quota_or_rate_limit"
    if blocked(response.body):
        return "blocked", "security_challenge"
    if not 200 <= response.status < 300:
        return "error", response.error or f"http_{response.status}"
    return "", ""

def attach(r, source, query, response, raw):
    r["sources"] = [source]
    r["provenance"] = [{"source": source, "query": query, "retrieved_at": now(), "raw_path": response.raw_path, "source_url": response.url}]
    r["metadata_by_source"] = {source: [raw]}
    return canonical(r)

def openalex_record(w):
    authors, affiliations, countries = [], [], set()
    for a in w.get("authorships", []) or []:
        author = a.get("author") or {}
        institutions = a.get("institutions") or []
        aff = [{"id": i.get("id"), "name": i.get("display_name"), "country": i.get("country_code")} for i in institutions]
        countries.update(i["country"] for i in aff if i.get("country"))
        affiliations.extend(aff)
        authors.append({"name": author.get("display_name", ""), "orcid": author.get("orcid"), "affiliations": aff})
    inv = w.get("abstract_inverted_index") or {}
    words = {p: word for word, positions in inv.items() for p in positions} if isinstance(inv, dict) else {}
    locations = w.get("locations") or []
    loc = w.get("primary_location") or {}
    best = w.get("best_oa_location") or {}
    source = loc.get("source") or {}
    oa = w.get("open_access") or {}
    biblio = w.get("biblio") or {}
    return {"title": w.get("title") or w.get("display_name"), "authors": authors,
            "year": w.get("publication_year"), "publication_date": w.get("publication_date"),
            "document_type": w.get("type"), "doi": w.get("doi"), "language": w.get("language"),
            "container_title": source.get("display_name"), "issn": source.get("issn") or [],
            "volume": biblio.get("volume"), "issue": biblio.get("issue"), "pages": "-".join(filter(None, [biblio.get("first_page"), biblio.get("last_page")])),
            "abstract": " ".join(words[p] for p in sorted(words)),
            "url": loc.get("landing_page_url") or best.get("landing_page_url") or w.get("doi"),
            "pdf_urls": [l["pdf_url"] for l in [best, loc] + locations if l.get("pdf_url")],
            "is_oa": oa.get("is_oa"), "oa_status": oa.get("oa_status"),
            "licenses": [l["license"] for l in [best] + locations if l.get("license")],
            "keywords": [k.get("display_name") for k in w.get("keywords", []) or [] if k.get("display_name")],
            "affiliations": affiliations, "countries": sorted(countries), "source_ids": {"openalex": w.get("id")},
            "citations_by_source": {"openalex": w.get("cited_by_count")}, "retracted": w.get("is_retracted")}

def crossref_record(w):
    parts, date_kind = [], ""
    for key in ("published-print", "published-online", "issued"):
        dp = (w.get(key) or {}).get("date-parts") or []
        if dp and dp[0]:
            parts, date_kind = dp[0], key
            break
    authors = [{"given": a.get("given", ""), "family": a.get("family", ""), "name": a.get("name", ""), "orcid": a.get("ORCID"), "affiliations": a.get("affiliation") or [], "literal": bool(a.get("name"))} for a in w.get("author", []) or []]
    editors = [{"given": a.get("given", ""), "family": a.get("family", ""), "name": a.get("name", ""), "orcid": a.get("ORCID"), "literal": bool(a.get("name"))} for a in w.get("editor", []) or []]
    event = w.get("event") or {}
    abstract = clean(re.sub(r"<[^>]+>", " ", w.get("abstract") or ""))
    return {"title": (w.get("title") or [""])[0], "authors": authors, "editors": editors, "year": parts[0] if parts else None,
            "publication_date": "-".join(map(str, parts)), "date_kind": date_kind, "document_type": w.get("type"),
            "doi": w.get("DOI"), "container_title": (w.get("container-title") or [""])[0],
            "publisher": w.get("publisher"), "issn": w.get("ISSN") or [], "isbn": w.get("ISBN") or [],
            "publisher_place": w.get("publisher-location"), "edition": w.get("edition-number"),
            "series": next(iter(as_list(w.get("group-title"))), ""), "event_title": event.get("name"), "event_location": event.get("location"),
            "volume": w.get("volume"), "issue": w.get("issue"), "pages": w.get("page"), "article_number": w.get("article-number"),
            "abstract": abstract, "language": w.get("language"), "url": w.get("URL"),
            # A PDF link in Crossref does not establish an open license. Do not automatically download it.
            "pdf_urls": [], "crossref_links": w.get("link") or [], "licenses": [l.get("URL") for l in w.get("license", []) or [] if l.get("URL")],
            "keywords": w.get("subject") or [], "source_ids": {"crossref": w.get("DOI")},
            "citations_by_source": {"crossref": w.get("is-referenced-by-count")}, "updates": w.get("update-to") or []}

def doaj_record(w):
    b = w.get("bibjson") or {}
    j = b.get("journal") or {}
    identifiers = b.get("identifier") or []
    languages = as_list(b.get("language"))
    if not languages:
        journal_languages = as_list(j.get("language"))
        # A multilingual journal does not establish the language of this article.
        languages = journal_languages if len(journal_languages) == 1 else []
    lang = LANGS.get(str(languages[0]).lower(), str(languages[0]).lower()) if len(languages) == 1 else ""
    links = b.get("link") or []
    r = {"title": b.get("title"), "authors": [{"name": a.get("name"), "orcid": a.get("orcid_id"), "affiliations": as_list(a.get("affiliation"))} for a in b.get("author", []) or []],
         "year": b.get("year"), "publication_date": (str(b.get("year")) + "-" + str(b.get("month")).zfill(2)) if b.get("year") and b.get("month") else str(b.get("year") or ""), "document_type": "article",
         "doi": next((x.get("id") for x in identifiers if x.get("type", "").lower() == "doi"), ""),
         "issn": [x.get("id") for x in identifiers if "issn" in x.get("type", "").lower()],
         "container_title": j.get("title"), "publisher": j.get("publisher"), "volume": j.get("volume"), "issue": j.get("number"),
         "pages": "-".join(str(x) for x in (b.get("start_page"), b.get("end_page")) if x not in (None, "")),
         "abstract": b.get("abstract"), "keywords": b.get("keywords") or [], "language": lang,
         "url": next((x.get("url") for x in links if x.get("url")), ""),
         "pdf_urls": [x["url"] for x in links if x.get("url") and (x.get("content_type") == "application/pdf" or x.get("type") == "pdf")],
         "is_oa": True, "licenses": [l.get("url") or l.get("type") for l in j.get("license", []) or [] if l.get("url") or l.get("type")],
         "source_ids": {"doaj": w.get("id")}, "brazil_venue": str(j.get("country", "")).upper() in ("BR", "BRAZIL", "BRASIL") if j.get("country") else None}
    if not lang:
        r["notes"] = ["Article language is not verified by a multilingual journal's language field"]
    return r

def s2_record(w):
    j = w.get("journal") or {}
    pdf = w.get("openAccessPdf") or {}
    types = w.get("publicationTypes") or []
    doc = "review" if "Review" in types else ("article" if "JournalArticle" in types else "conference-paper" if "Conference" in types else "book-chapter" if "BookSection" in types else "unknown")
    return {"title": w.get("title"), "authors": [{"name": a.get("name"), "source_id": a.get("authorId")} for a in w.get("authors", []) or []],
            "year": w.get("year"), "publication_date": w.get("publicationDate"), "document_type": doc,
            "doi": (w.get("externalIds") or {}).get("DOI"), "container_title": j.get("name") or w.get("venue"),
            "volume": j.get("volume"), "pages": j.get("pages"), "abstract": w.get("abstract"), "url": w.get("url"),
            "pdf_urls": [pdf["url"]] if pdf.get("url") else [], "is_oa": w.get("isOpenAccess"), "licenses": [pdf["license"]] if pdf.get("license") else [],
            "source_ids": {"semantic_scholar": w.get("paperId"), **(w.get("externalIds") or {})},
            "citations_by_source": {"semantic_scholar": w.get("citationCount")}}

def easyscielopack_record(w):
    """Import the five-column data.frame exported by easyScieloPack 0.1.1.

    Neither the abstract language nor the query's collection establishes the
    document language, authors' countries or publication type.
    """
    return {"title": w.get("title"), "authors": w.get("authors") or [], "year": w.get("year"), "doi": w.get("doi"),
            "abstract": w.get("abstract"), "url": w.get("url") or w.get("link"), "document_type": "unknown",
            "language": "", "retrieval_tool": "easyScieloPack", "sources": ["scielo"],
            "notes": ["easyScieloPack search-result import. Verify publication type, article language, journal and canonical URL."]}

class Node:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.parent, self.parts = tag, dict(attrs or []), parent, []
    def walk(self):
        yield self
        for x in self.parts:
            if isinstance(x, Node):
                yield from x.walk()
    def text(self):
        return clean(" ".join(x.text() if isinstance(x, Node) else x for x in self.parts))
    def has(self, cls):
        return cls in self.attrs.get("class", "").split()

class DOM(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Node("root")
        self.current = self.root
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.parts.append(node)
        if tag not in self.VOID:
            self.current = node
    def handle_startendtag(self, tag, attrs):
        self.current.parts.append(Node(tag, attrs, self.current))
    def handle_endtag(self, tag):
        n = self.current
        while n.parent:
            if n.tag == tag:
                self.current = n.parent
                return
            n = n.parent
    def handle_data(self, data):
        self.current.parts.append(data)

def parse_scielo(text):
    root = DOM(text).root
    candidates = [n for n in root.walk() if n.has("item") or n.has("result-item") or n.has("record") or n.tag == "article"]
    records = []
    for node in candidates:
        title_node = next((n for n in node.walk() if n.has("title") or n.has("title-article") or n.tag in ("h2", "h3")), None)
        if not title_node:
            continue
        link = next((n for n in title_node.walk() if n.tag == "a" and n.attrs.get("href")), None)
        if not link:
            continue
        url = urljoin("https://search.scielo.org/", link.attrs["href"])
        if not re.search(r"scielo\.(org|br)|doi\.org", url, re.I):
            continue
        source = next((n for n in node.walk() if n.has("source") or n.has("journal")), None)
        author = next((n for n in node.walk() if n.has("authors")), None)
        author_links = [n.text() for n in author.walk() if n.tag == "a" and n.has("author")] if author else []
        abstract = next((n for n in node.walk() if n.has("abstract") or n.has("abstract_display")), None)
        # SciELO can place abstracts outside the result item, keyed by item ID.
        article_id = node.attrs.get("id")
        if article_id:
            external = next((n for suffix in ("pt", "en", "es") for n in root.walk() if n.attrs.get("id") == article_id + "_" + suffix), None)
            abstract = external or abstract
        year_node = next((n for n in node.walk() if n.has("publication-year") or n.has("year")), None)
        year_text = node.attrs.get("data-year") or (year_node.text() if year_node else source.text() if source else "")
        year = re.search(r"\b(19|20)\d{2}\b", year_text)
        doi = next((n.attrs["href"] for n in node.walk() if n.tag == "a" and "doi.org/" in n.attrs.get("href", "")), "")
        language = node.attrs.get("data-language", "")
        records.append({"title": link.text(), "url": url, "authors": author_links or (author.text() if author else "").split(";"),
                        "container_title": source.text() if source else "", "year": year[0] if year else None,
                        "doi": doi, "abstract": abstract.text() if abstract else "", "language": language,
                        "document_type": "article", "is_oa": True, "source_ids": {"scielo": url},
                        "notes": ["SciELO result-page metadata requires article-page verification"]})
    # Do not extract years from article titles, which may contain historical periods.
    total_node = next((n for n in root.walk() if n.attrs.get("id") == "TotalHits"), None)
    total_node = total_node or next((n for n in root.walk() if n.has("results-count") or n.has("result-count") or n.has("count")), None)
    total = None
    if total_node:
        digits = re.search(r"\d[\d.,\s]*", total_node.text())
        if digits:
            total = int(re.sub(r"\D", "", digits[0]))
    has_next = any(n.tag == "a" and (n.attrs.get("rel") == "next" or n.has("next")) for n in root.walk())
    explicit_empty = bool(re.search(r"no results|no records found|nenhum resultado|nenhum documento|não foram encontrados|no se encontraron", text, re.I))
    return records, total, has_next, explicit_empty

def parse_bdtd_rss(text):
    root = ET.fromstring(text)
    records = []
    def bylocal(node, name):
        return [n for n in node.iter() if n.tag.split("}")[-1] == name]
    for item in bylocal(root, "item"):
        values = {name: [clean("".join(n.itertext())) for n in bylocal(item, name)] for name in ("title", "link", "creator", "author", "date", "pubDate", "description", "type", "language")}
        # RSS pubDate may be a harvest/update date, not the defense year.
        date = next(iter(values["date"]), "")
        match = re.search(r"\b(19|20)\d{2}\b", date)
        records.append({"title": next(iter(values["title"]), ""), "url": next(iter(values["link"]), ""), "authors": values["creator"] or values["author"],
                        "year": match[0] if match else None, "document_type": "thesis", "language": next(iter(values["language"]), ""),
                        "abstract": clean(re.sub(r"<[^>]+>", " ", next(iter(values["description"]), ""))),
                        "source_ids": {"bdtd": next(iter(values["link"]), "")}, "is_oa": None,
                        "notes": ["Verify defense year and thesis type on the institutional repository"]})
    totals = bylocal(root, "totalResults")
    return records, int(totals[0].text) if totals and (totals[0].text or "").isdigit() else None

def search(client, source, query, config):
    if source not in ALL_SOURCES:
        raise ValueError(f"Unsupported source: {source}")
    if source == "bdtd" and not config.get("bdtd_requested"):
        raise ValueError("BDTD requires an explicit user request and bdtd_requested=true")
    out = SearchResult(source, query)
    maximum, cursor, page, seen = config.get("max_per_query", 60), "*", 1, set()
    while len(out.records) < maximum:
        # Numbered-page APIs require a constant page size throughout the search.
        count = min(100 if source != "scielo" else 50, maximum) if source in ("doaj", "bdtd") else min(100 if source != "scielo" else 50, maximum - len(out.records))
        filters = []
        start, end = config.get("year_start"), config.get("year_end")
        if source == "openalex":
            params = {"search": query, "per_page": count, "cursor": cursor}
            if start:
                filters.append(f"from_publication_date:{start}-01-01")
            if end:
                filters.append(f"to_publication_date:{end}-12-31")
            if config.get("affiliation_country"):
                filters.append("authorships.institutions.country_code:" + config["affiliation_country"])
            if filters:
                params["filter"] = ",".join(filters)
            key = os.getenv("OPENALEX_API_KEY")
            headers = {"Authorization": "Bearer " + key} if key else {}
            response = client.get("https://api.openalex.org/works", params, headers)
        elif source == "crossref":
            params = {"query": query, "rows": count, "cursor": cursor}
            if start:
                filters.append(f"from-pub-date:{start}-01-01")
            if end:
                filters.append(f"until-pub-date:{end}-12-31")
            if filters:
                params["filter"] = ",".join(filters)
            if os.getenv("CROSSREF_EMAIL"):
                params["mailto"] = os.getenv("CROSSREF_EMAIL")
            response = client.get("https://api.crossref.org/works", params)
        elif source == "doaj":
            response = client.get("https://doaj.org/api/search/articles/" + quote(query, safe=""), {"page": page, "pageSize": count})
        elif source == "semantic_scholar":
            params = {"query": query, "fields": "paperId,title,year,authors,venue,abstract,externalIds,publicationTypes,journal,url,openAccessPdf,citationCount"}
            if start or end:
                params["year"] = f"{start or ''}:{end or ''}"
            if page > 1:
                params["token"] = cursor
            key = os.getenv("S2_API_KEY")
            response = client.get("https://api.semanticscholar.org/graph/v1/paper/search/bulk", params, {"x-api-key": key} if key else {})
        elif source == "scielo":
            response = client.get("https://search.scielo.org/", {"q": query, "lang": "pt", "count": count, "from": len(out.records) + 1, "output": "site", "format": "summary"})
        else:
            response = client.get("https://bdtd.ibict.br/vufind/Search/Results", {"lookfor": query, "type": "AllFields", "view": "rss", "page": page, "limit": count})
        if response.raw_path:
            out.raw_paths.append(response.raw_path)
        status, error = failure(response)
        if status:
            out.status, out.error = ("partial" if out.records else status), error
            break
        try:
            next_cursor, has_next = None, False
            if source == "scielo":
                items, total, has_next, empty = parse_scielo(response.text())
                out.reported_total = total if total is not None else out.reported_total
                if out.reported_total is not None and len(out.records) + len(items) < out.reported_total:
                    has_next = True
                if not items and not empty and total != 0:
                    raise ValueError("unrecognized_scielo_layout")
                mapped = items
            elif source == "bdtd":
                items, total = parse_bdtd_rss(response.text())
                out.reported_total = total
                mapped = items
                has_next = total is not None and page * count < total
            else:
                data = response.json()
                if not isinstance(data, dict):
                    raise ValueError("unexpected_response_root")
                if source == "openalex":
                    if "results" not in data or not isinstance(data.get("meta"), dict):
                        raise ValueError("unexpected_openalex_schema")
                    items = data["results"]
                    out.reported_total = data["meta"].get("count")
                    next_cursor = data["meta"].get("next_cursor")
                    mapped = [openalex_record(w) for w in items]
                elif source == "crossref":
                    message = data.get("message")
                    if not isinstance(message, dict) or "items" not in message:
                        raise ValueError("unexpected_crossref_schema")
                    items = message["items"]
                    out.reported_total = message.get("total-results")
                    next_cursor = message.get("next-cursor")
                    mapped = [crossref_record(w) for w in items]
                elif source == "doaj":
                    if "results" not in data:
                        raise ValueError("unexpected_doaj_schema")
                    items = data["results"]
                    out.reported_total = data.get("total")
                    has_next = isinstance(out.reported_total, int) and page * count < out.reported_total
                    mapped = [doaj_record(w) for w in items]
                else:
                    if "data" not in data:
                        raise ValueError("unexpected_s2_schema")
                    items = data["data"]
                    out.reported_total = data.get("total")
                    next_cursor = data.get("token")
                    mapped = [s2_record(w) for w in items]
            if not isinstance(items, list) or not all(isinstance(w, dict) for w in items):
                raise ValueError("unexpected_record_collection")
            page_key = json.dumps(items, sort_keys=True, ensure_ascii=False)
            if items and page_key in seen:
                out.status, out.error = "partial", "repeated_page"
                break
            seen.add(page_key)
            for raw, record in zip(items, mapped):
                out.records.append(attach(record, source, query, response, raw))
                if len(out.records) >= maximum:
                    break
            if not items and out.reported_total is not None and len(out.records) < out.reported_total:
                out.status, out.error = "partial" if out.records else "error", "empty_page_with_nonzero_total"
                break
            if not items or (out.reported_total is not None and len(out.records) >= out.reported_total):
                out.complete = True
                break
            if len(out.records) >= maximum:
                out.truncated = bool(next_cursor or has_next or out.reported_total is None or len(out.records) < out.reported_total)
                break
            if next_cursor:
                if next_cursor == cursor:
                    out.status, out.error = "partial", "repeated_cursor"
                    break
                cursor = next_cursor
            elif not has_next:
                out.complete = out.reported_total is not None and len(out.records) >= out.reported_total
                if not out.complete:
                    out.status, out.error = "partial", "pagination_extent_unverified"
                break
            page += 1
        except (ValueError, TypeError, KeyError, AttributeError, ET.ParseError) as exc:
            out.status, out.error = "partial" if out.records else "error", str(exc)[:180]
            if hasattr(client, "invalidate"):
                client.invalidate(response)
            break
    if out.status == "ok" and not out.records:
        out.status = "empty"
    return out
