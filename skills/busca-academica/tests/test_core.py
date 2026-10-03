"""Regression tests use synthetic examples, never citations for a real review."""
import csv
import json
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.error import HTTPError
from io import BytesIO

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from academic_core.model import canonical, deduplicate, normalize_doi, eligibility
from academic_core.http import Client, Response, redacted_url, allowed_url
from academic_core.sources import search, openalex_record, doaj_record, crossref_record, parse_scielo, parse_bdtd_rss
from academic_core.exports import export_all, choose_style, bib_entry, csv_safe
from academic_core.downloads import validate_pdf, retrieve_pdfs
from academic_search import load_records, validate_plan, finalize
from audit_delivery import audit, balanced_bib
from visualize_corpus import generate

def record(**kwargs):
    return canonical({"title": "Estudo sintético sobre democracia", "authors": [{"given": "Ana", "family": "Silva"}], "year": 2025, "document_type": "article", "language": "pt", "url": "https://example.org/article", "sources": ["test"], **kwargs})

def response(data, status=200):
    return Response(status, json.dumps(data).encode(), "application/json", url="https://example.org/api")

class FakeClient:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []
    def get(self, url, params=None, headers=None, **kwargs):
        self.calls.append((url, params, headers))
        return self.replies.pop(0)

class ModelTests(unittest.TestCase):
    def test_conflicting_dois_do_not_merge(self):
        rows, _ = deduplicate([record(doi="10.1234/a"), record(doi="10.1234/b")])
        self.assertEqual(len(rows), 2)
    def test_same_doi_merges_sources_preserving_conflicts(self):
        rows, _ = deduplicate([record(doi="https://doi.org/10.1234/A", sources=["openalex"]), record(doi="10.1234/a", year=2024, sources=["crossref"])])
        self.assertEqual(len(rows), 1)
        self.assertEqual(set(rows[0]["sources"]), {"openalex", "crossref"})
        self.assertTrue(rows[0]["metadata_conflicts"])
    def test_same_title_different_authors_stays_separate(self):
        rows, _ = deduplicate([record(), record(authors=[{"name": "João Souza"}])])
        self.assertEqual(len(rows), 2)
    def test_shared_surname_is_not_author_identity(self):
        rows, _ = deduplicate([record(authors=[{"given": "Ana", "family": "Silva"}]), record(authors=[{"given": "João", "family": "Silva"}])])
        self.assertEqual(len(rows), 2)
    def test_full_author_name_matches_structured_and_unstructured_forms(self):
        rows, _ = deduplicate([record(authors=[{"given": "Ana", "family": "Silva"}]), record(authors=[{"name": "Ana Silva"}])])
        self.assertEqual(len(rows), 1)
    def test_conflicting_known_venues_need_manual_review_without_doi(self):
        rows, suspects = deduplicate([record(container_title="Revista sintética A"), record(container_title="Revista sintética B")])
        self.assertEqual(len(rows), 2)
        self.assertTrue(suspects)
    def test_versions_stay_separate(self):
        rows, _ = deduplicate([record(), record(document_type="preprint")])
        self.assertEqual(len(rows), 2)
    def test_exact_compatible_records_merge_without_doi(self):
        rows, _ = deduplicate([record(), record(sources=["doaj"])])
        self.assertEqual(len(rows), 1)
    def test_similar_title_is_review_candidate(self):
        rows, suspects = deduplicate([record(title="Democracia e participação política digital"), record(title="Democracia e participação política digitais")])
        self.assertEqual(len(rows), 2)
        self.assertTrue(suspects)
    def test_doi_parentheses_are_preserved(self):
        self.assertEqual(normalize_doi("https://doi.org/10.1234/A(B)"), "10.1234/a(b)")
    def test_empty_author_is_absent(self):
        r = record(authors=["", " "])
        self.assertEqual(r["authors"], [])
        self.assertIn("authors", r["missing_fields"])
    def test_missing_data_is_not_negative(self):
        r = record(language="", year=None)
        self.assertEqual(set(eligibility(r, {"languages": ["pt"], "year_start": 2024})), {"language_unverified", "year_unverified"})
        self.assertIsNone(r["brazil_affiliation"])
    def test_english_brazil_affiliation_is_kept(self):
        r = record(language="en", countries=["BR"])
        self.assertTrue(r["brazil_affiliation"])
        self.assertEqual(eligibility(r, {"languages": ["pt", "en"]}), [])
    def test_chapter_is_opt_in(self):
        r = record(document_type="book-chapter")
        self.assertIn("document_type_outside_scope", eligibility(r, {}))
        self.assertEqual(eligibility(r, {"types": ["article", "book-chapter"]}), [])
    def test_incomplete_record_is_preserved_for_verification(self):
        rows, _ = deduplicate([record(title="", authors=[], doi="10.1234/partial")])
        self.assertEqual(len(rows), 1)
        self.assertIn("bibliographic_identity_unverified", eligibility(rows[0], {}))
    def test_same_source_identifier_repairs_missing_identity(self):
        rows, _ = deduplicate([record(title="", authors=[], source_ids={"openalex": "W-synthetic"}), record(source_ids={"openalex": "W-synthetic"})])
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["title"])
    def test_source_identifier_does_not_override_conflicting_dois(self):
        rows, _ = deduplicate([record(doi="10.1234/a", source_ids={"openalex": "W-synthetic"}), record(doi="10.1234/b", source_ids={"openalex": "W-synthetic"})])
        self.assertEqual(len(rows), 2)
    def test_language_codes_are_normalized_without_title_inference(self):
        self.assertEqual(record(language="por")["language"], "pt")
        self.assertEqual(record(language="pt-BR")["language"], "pt")
        self.assertEqual(record(language="eng")["language"], "en")
        self.assertEqual(record(language="")["language"], "")

class SourceTests(unittest.TestCase):
    def test_blocked_scielo_is_not_empty(self):
        result = search(FakeClient([Response(200, b"<html>Verificando seu navegador...</html>")]), "scielo", "democracia", {"max_per_query": 2})
        self.assertEqual(result.status, "blocked")
        self.assertFalse(result.complete)
    def test_scielo_layout_change_is_an_error(self):
        result = search(FakeClient([Response(200, b"<html>Interface changed</html>")]), "scielo", "q", {"max_per_query": 2})
        self.assertEqual(result.status, "error")
    def test_true_empty_openalex(self):
        result = search(FakeClient([response({"meta": {"count": 0}, "results": []})]), "openalex", "q", {"max_per_query": 2})
        self.assertEqual(result.status, "empty")
        self.assertTrue(result.complete)
    def test_inconsistent_empty_page_is_not_complete(self):
        result = search(FakeClient([response({"meta": {"count": 10}, "results": []})]), "openalex", "q", {"max_per_query": 2})
        self.assertEqual(result.status, "error")
        self.assertFalse(result.complete)
    def test_partial_second_page_keeps_first(self):
        w = {"id": "W1", "title": "Synthetic", "type": "article", "publication_year": 2025}
        result = search(FakeClient([response({"meta": {"count": 4, "next_cursor": "next"}, "results": [w]}), Response(403, b"Denied")]), "openalex", "q", {"max_per_query": 4})
        self.assertEqual(result.status, "partial")
        self.assertEqual(len(result.records), 1)
    def test_limit_is_reported(self):
        w = {"id": "W1", "title": "Synthetic", "type": "article"}
        result = search(FakeClient([response({"meta": {"count": 100, "next_cursor": "next"}, "results": [w]})]), "openalex", "q", {"max_per_query": 1})
        self.assertTrue(result.truncated)
        self.assertFalse(result.complete)
    def test_numbered_pagination_has_constant_size(self):
        items = [{"id": str(i), "bibjson": {"title": f"Synthetic {i}", "year": "2025"}} for i in range(100)]
        c = FakeClient([response({"total": 200, "results": items}), response({"total": 200, "results": [{"id": str(i+100), "bibjson": {"title": f"Synthetic {i+100}"}} for i in range(100)]})])
        result = search(c, "doaj", "q", {"max_per_query": 150})
        self.assertEqual([x[1]["pageSize"] for x in c.calls], [100, 100])
        self.assertEqual(len(result.records), 150)
    def test_repeated_page_is_detected(self):
        payload = {"meta": {"count": 10, "next_cursor": "next"}, "results": [{"id": "W1", "title": "Synthetic", "type": "article"}]}
        result = search(FakeClient([response(payload), response(payload)]), "openalex", "q", {"max_per_query": 3})
        self.assertEqual(result.error, "repeated_page")
    def test_unknown_language_not_copied_from_multilingual_journal(self):
        r = doaj_record({"id": "x", "bibjson": {"title": "Synthetic", "journal": {"language": ["Portuguese", "English"]}}})
        self.assertEqual(r["language"], "")
    def test_abstract_is_not_truncated(self):
        text = "palavra " * 1200
        r = crossref_record({"title": ["Synthetic"], "abstract": text})
        self.assertGreater(len(r["abstract"]), 2000)
    def test_scielo_does_not_infer_year_from_title(self):
        markup = '<div class="item"><h2><a href="https://www.scielo.br/j/a/a/x/">Política entre 2016 e 2020</a></h2><span class="source">Revista acadêmica</span></div>'
        rows, _, _, _ = parse_scielo(markup)
        self.assertIsNone(rows[0]["year"])
    def test_scielo_parses_metadata_year(self):
        markup = '<div class="item" data-year="2025" data-language="pt"><div class="title"><a href="https://www.scielo.br/j/a/a/x/">Synthetic</a></div><span class="authors">Ana Silva; João Souza</span></div>'
        rows, _, _, _ = parse_scielo(markup)
        self.assertEqual(rows[0]["year"], "2025")
        self.assertEqual(len(rows[0]["authors"]), 2)
    def test_scielo_totalhits_authors_and_external_abstract(self):
        markup = '<span id="TotalHits">1 234</span><div class="item" id="synthetic-item" data-year="2025"><div class="title"><a href="https://www.scielo.br/j/a/a/x/">Synthetic</a></div><div class="authors"><a class="author">Ana Silva</a><a class="author">João Souza</a></div></div><div id="synthetic-item_pt">Resumo sintético completo</div>'
        rows, total, _, _ = parse_scielo(markup)
        self.assertEqual(total, 1234)
        self.assertEqual(rows[0]["authors"], ["Ana Silva", "João Souza"])
        self.assertEqual(rows[0]["abstract"], "Resumo sintético completo")
        self.assertEqual(rows[0]["language"], "")
    def test_scielo_zero_total_is_an_explicit_empty_result(self):
        result = search(FakeClient([Response(200, b'<span id="TotalHits">0</span>')]), "scielo", "q", {"max_per_query": 2})
        self.assertEqual(result.status, "empty")
        self.assertTrue(result.complete)
    def test_scielo_total_allows_pagination_without_next_css(self):
        def markup(item, total):
            return (f'<span id="TotalHits">{total}</span><div class="item"><h2><a href="https://www.scielo.br/j/a/a/{item}/">Synthetic {item}</a></h2></div>').encode()
        c = FakeClient([Response(200, markup("one", 2)), Response(200, markup("two", 2))])
        result = search(c, "scielo", "q", {"max_per_query": 3})
        self.assertEqual(len(result.records), 2)
        self.assertTrue(result.complete)
        self.assertEqual([call[1]["from"] for call in c.calls], [1, 2])
    def test_bdtd_requires_explicit_request(self):
        with self.assertRaises(ValueError):
            search(FakeClient([]), "bdtd", "q", {})
    def test_rss_update_date_is_not_defense_year(self):
        rss = '<rss><channel><item><title>Synthetic</title><link>https://example.org/thesis</link><pubDate>Fri, 3 Oct 2026</pubDate></item></channel></rss>'
        rows, _ = parse_bdtd_rss(rss)
        self.assertIsNone(rows[0]["year"])

class ExportAndDeliveryTests(unittest.TestCase):
    def test_portuguese_scope_uses_abnt(self):
        self.assertEqual(choose_style({"languages": ["pt"]}, [record()]), "abnt")
        self.assertEqual(choose_style({"languages": ["pt", "en"]}, [record()]), "apa")
    def test_explicit_style_wins(self):
        self.assertEqual(choose_style({"languages": ["pt"], "citation_style": "apa"}, [record()]), "apa")
    def test_bibtex_unicode_escaping_and_identifiers(self):
        text = bib_entry(record(title="Educação & democracia {Brasil}", doi="10.1234/a_b", url="https://example.org/a_b?x=10%20"))
        self.assertIn("Educação", text)
        self.assertIn(r"\&", text)
        self.assertIn("10.1234/a_b", text)
        self.assertIn("https://example.org/a_b?x=10%20", text)
        self.assertTrue(balanced_bib(text))
    def test_exports_include_outside_scope_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = [record(doi="10.1234/a"), record(title="Chapter", document_type="book-chapter", selection="outside_scope", doi="10.1234/b")]
            finalize(rows, tmp, {}, {"source": "synthetic"})
            self.assertEqual(len(load_records(Path(tmp)/"referencias.csv")), 2)
            self.assertTrue(audit(tmp)["ok"])
    def test_csv_roundtrip_authors_and_abstract(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = record(abstract="resumo completo " * 500)
            export_all([row], tmp, {}, {})
            recovered = canonical(load_records(Path(tmp)/"referencias.csv")[0])
            self.assertEqual(recovered["authors"], row["authors"])
            self.assertEqual(recovered["abstract"], row["abstract"])
    def test_formula_content_is_preserved_in_json_but_safe_in_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = record(title="=HYPERLINK(unsafe)")
            export_all([row], tmp, {}, {})
            self.assertEqual(load_records(Path(tmp)/"registros.json")[0]["title"], row["title"])
            self.assertTrue(load_records(Path(tmp)/"referencias.csv")[0]["title"].startswith("'="))
    def test_graph_counts_use_selected_population(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = [record(selection="included", themes=["Participação"], year=2024), record(selection="outside_scope", year=2025)]
            result = generate(rows, tmp)
            self.assertEqual(result["records"], 1)
            for name in result["figures"]:
                ET.parse(Path(tmp)/name)
            self.assertNotIn("2025", (Path(tmp)/"producao_por_ano.csv").read_text())
    def test_missing_year_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = generate([record(year=None, selection="included")], tmp)
            self.assertEqual(result["missing_year"], 1)
            self.assertEqual(result["figures"], [])
    def test_deep_delivery_rejects_short_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = record(selection="included")
            export_all([row], tmp, {}, {})
            report = Path(tmp)/"relatorio.md"
            report.write_text("<!-- narrative:start --><!-- executive:start -->Curto<!-- executive:end --><!-- narrative:end -->")
            result = audit(tmp, report, "deep")
            self.assertFalse(result["ok"])
            self.assertIn("deep_narrative_outside_2000_5000_words", result["errors"])
    def test_plan_rejects_bdtd_without_opt_in(self):
        with self.assertRaises(ValueError):
            validate_plan({"queries": [{"source": "bdtd", "query": "q"}]})
    def test_plan_rejects_reversed_years(self):
        with self.assertRaises(ValueError):
            validate_plan({"config": {"year_start": 2026, "year_end": 2024}, "queries": [{"source": "openalex", "query": "q"}]})
    def test_plan_rejects_duplicate_jobs(self):
        with self.assertRaises(ValueError):
            validate_plan({"queries": [{"source": "openalex", "query": "q"}]*2})
    def test_plan_supports_additional_iso_languages(self):
        plan = validate_plan({"config": {"languages": ["pt", "en", "pl", "zh"]}, "queries": [{"source": "openalex", "query": "q"}]})
        self.assertIn("pl", plan["config"]["languages"])
    def test_plan_rejects_invalid_scalar_and_collection_types(self):
        for bad in ({"year_start": "2020"}, {"max_per_query": True}, {"languages": "pt"}, {"types": "article"}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                validate_plan({"config": bad, "queries": [{"source": "openalex", "query": "q"}]})

class TransportAndDownloadTests(unittest.TestCase):
    def test_key_redaction(self):
        self.assertNotIn("sensitive", redacted_url("https://example.org?q=x&api_key=sensitive"))
    def test_reject_nonpublic_and_nonhttp_urls(self):
        for url in ("file:///tmp/a", "https://127.0.0.1/a", "http://localhost/a", "https://user:pass@example.org/a"):
            self.assertFalse(allowed_url(url))
    def test_retry_is_bounded_and_respects_retry_after(self):
        calls, delays = [], []
        def opener(req, timeout):
            calls.append(req)
            raise HTTPError(req.full_url, 429, "limit", {"Retry-After": "999"}, BytesIO(b"limited"))
        with tempfile.TemporaryDirectory() as tmp:
            r = Client(tmp, retries=2, opener=opener, sleeper=delays.append).get("https://example.org/api")
        self.assertEqual(r.status, 429)
        self.assertEqual(len(calls), 3)
        self.assertEqual(delays, [30, 30])
    def test_download_requires_user_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                retrieve_pdfs([record()], FakeClient([]), tmp)
    def test_html_is_not_a_pdf(self):
        self.assertFalse(validate_pdf(b"<html>Blocked</html>")[0])
    def test_incomplete_pdf_is_rejected(self):
        self.assertFalse(validate_pdf(b"%PDF-1.4\nunfinished")[0])

if __name__ == "__main__":
    unittest.main()
