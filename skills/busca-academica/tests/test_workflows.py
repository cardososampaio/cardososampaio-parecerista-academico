"""End-to-end control flow with isolated, explicitly synthetic fixtures."""
import contextlib
import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import academic_search as cli
from academic_core.model import canonical
from academic_core.http import Client
from academic_core.exports import export_all, reference, bib_entry, csl_item
from academic_core.sources import SearchResult, crossref_record, search, easyscielopack_record
from audit_delivery import audit
from visualize_corpus import generate

def record(**extra):
    return canonical({"title": "Fixture bibliográfica sintética", "authors": [{"given": "Ana", "family": "Silva"}],
                      "year": 2025, "document_type": "article", "language": "pt", "container_title": "Veículo sintético",
                      "url": "https://example.org/synthetic", "sources": ["synthetic"], **extra})

class EmptyClient:
    events = []

class WorkflowTests(unittest.TestCase):
    def invoke(self, args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            namespace = cli.parser().parse_args(args)
            return namespace.func(namespace)

    def test_resume_only_retries_failed_job_and_preserves_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = root / "plan.json"
            plan.write_text(json.dumps({"queries": [{"source": "doaj", "query": "q"}, {"source": "openalex", "query": "q"}]}))
            args = ["search", "--plan", str(plan), "--out", str(root / "out")]
            calls = []
            def first(client, source, query, config):
                calls.append(source)
                return SearchResult(source, query, status="ok" if source == "openalex" else "blocked",
                                    records=[record()] if source == "openalex" else [], complete=source == "openalex")
            with patch.object(cli, "Client", return_value=EmptyClient()), patch.object(cli, "search", side_effect=first):
                self.assertEqual(self.invoke(args), 2)
            self.assertEqual(calls, ["openalex", "doaj"])
            def second(client, source, query, config):
                self.assertEqual(source, "doaj")
                return SearchResult(source, query, records=[record(title="Segunda fixture sintética")], complete=True)
            with patch.object(cli, "Client", return_value=EmptyClient()), patch.object(cli, "search", side_effect=second):
                self.assertEqual(self.invoke(args + ["--resume"]), 0)
            rows = cli.load_records(root / "out" / "registros.json")
            self.assertEqual(len(rows), 2)
            self.assertTrue(audit(root / "out")["ok"])
            manifest = json.loads((root / "out" / "manifesto_busca.json").read_text())
            self.assertEqual(len(manifest["query_attempts"]), 3)
            self.assertEqual([a["status"] for a in manifest["query_attempts"]], ["ok", "blocked", "ok"])

    def test_resume_changed_plan_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan, out = Path(tmp) / "plan.json", Path(tmp) / "out"
            plan.write_text(json.dumps({"queries": [{"source": "openalex", "query": "first"}]}))
            args = ["search", "--plan", str(plan), "--out", str(out)]
            with patch.object(cli, "Client", return_value=EmptyClient()), patch.object(cli, "search", return_value=SearchResult("openalex", "first", status="empty", complete=True)):
                self.invoke(args)
            plan.write_text(json.dumps({"queries": [{"source": "openalex", "query": "changed"}]}))
            with self.assertRaisesRegex(ValueError, "exactly the same plan"):
                self.invoke(args + ["--resume"])

    def test_partial_retry_replaces_its_own_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = ["search", "--query", "q", "--stage", "secondary", "--out", tmp]
            first = [SearchResult("crossref", "q", status="partial", records=[record(title="Old partial fixture")]),
                     SearchResult("semantic_scholar", "q", status="empty", complete=True)]
            with patch.object(cli, "Client", return_value=EmptyClient()), patch.object(cli, "search", side_effect=first):
                self.invoke(args)
            result = SearchResult("crossref", "q", records=[record(title="New complete fixture")], complete=True)
            with patch.object(cli, "Client", return_value=EmptyClient()), patch.object(cli, "search", return_value=result) as query:
                self.invoke(args + ["--resume"])
                self.assertEqual(query.call_count, 1)
            self.assertEqual([r["title"] for r in cli.load_records(Path(tmp) / "registros.json")], ["New complete fixture"])

    def test_import_whole_plan_applies_its_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data, config, out = root / "input.json", root / "plan.json", root / "out"
            data.write_text(json.dumps([record(document_type="book-chapter")]))
            config.write_text(json.dumps({"config": {"types": ["article"], "languages": ["pt"]}}))
            self.invoke(["import", "--input", str(data), "--config", str(config), "--out", str(out)])
            self.assertEqual(cli.load_records(out / "registros.json")[0]["selection"], "outside_scope")
    def test_easyscielopack_csv_is_imported_without_invented_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data, out = root / "scielo.csv", root / "out"
            with data.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["title", "authors", "year", "doi", "abstract"])
                writer.writeheader()
                writer.writerow({"title": "Fixture SciELO sintética", "authors": "Ana Silva; João Souza", "year": "2025", "doi": "https://doi.org/10.1234/synthetic", "abstract": "Texto sintético " * 500})
            self.invoke(["import", "--input", str(data), "--format", "easy_scielo_pack", "--coverage", "partial", "--out", str(out)])
            r = cli.load_records(out / "registros.json")[0]
            self.assertEqual(len(r["authors"]), 2)
            self.assertEqual(r["doi"], "10.1234/synthetic")
            self.assertEqual(r["url"], "https://doi.org/10.1234/synthetic")
            self.assertEqual(r["language"], "")
            self.assertEqual(r["document_type"], "unknown")
            self.assertEqual(r["selection"], "needs_verification")
            self.assertEqual(r["sources"], ["scielo"])
            self.assertEqual(r["provenance"][0]["format"], "easy_scielo_pack")
            self.assertGreater(len(r["abstract"]), 2000)
            self.assertTrue(audit(out)["ok"])
    def test_native_import_without_source_still_records_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data, out = root / "native.json", root / "out"
            data.write_text(json.dumps([{"id": "W-synthetic", "title": "Synthetic", "type": "article"}]))
            self.invoke(["import", "--input", str(data), "--format", "openalex", "--out", str(out)])
            r = cli.load_records(out / "registros.json")[0]
            self.assertEqual(r["sources"], ["openalex"])
            self.assertTrue(r["metadata_by_source"]["openalex"])

    def test_enrich_no_doi_still_produces_complete_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            export_all([record()], root / "initial", {}, {"plan": {"config": {"languages": ["pt"]}}})
            self.invoke(["enrich", "--input", str(root / "initial" / "registros.json"), "--out", str(root / "enriched")])
            self.assertTrue(audit(root / "enriched")["ok"])
            self.assertIn("ABNT", (root / "enriched" / "bibliografia_completa.md").read_text())

    def test_audit_rejects_changed_bibtex_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = record()
            export_all([r], tmp, {}, {})
            path = Path(tmp) / "referencias.bib"
            path.write_text(path.read_text().replace("ref" + r["record_id"][1:], "wrongkey"))
            self.assertIn("bibtex_corpus_key_mismatch", audit(tmp)["errors"])

    def test_complete_deep_structure_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = [record(title=f"Fixture sintética {i}", year=2024+i%2, selection="included", themes=["Tema sintético"]) for i in range(21)]
            export_all(rows, root, {}, {})
            generate(rows, root / "figuras")
            bibliography = (root / "bibliografia_completa.md").read_text()
            # Word-count fixture exercises structure, and is never a research report.
            text = "<!-- narrative:start -->\n<!-- executive:start -->" + "palavra " * 400 + "<!-- executive:end -->\n"
            text += "<!-- summary:start -->\n| Tema | Documentos |\n|---|---|\n| Sintético | 21 |\n<!-- summary:end -->\n"
            text += "<!-- top20:start -->\n" + "\n".join(r["record_id"] for r in rows[:20]) + "\n<!-- top20:end -->\n"
            text += "palavra " * 1700 + "\n<!-- narrative:end -->\n<!-- bibliography:start -->\n" + bibliography + "\n<!-- bibliography:end -->"
            report = root / "report.md"
            report.write_text(text)
            result = audit(root, report, "deep")
            self.assertTrue(result["ok"], result)

    def test_included_record_known_out_of_scope_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            export_all([record(selection="included", eligibility_checks=["year_outside_scope"])], tmp, {}, {})
            self.assertTrue(any("included_record_outside_configured_scope" in e for e in audit(tmp)["errors"]))

class BibliographicTypesTests(unittest.TestCase):
    def test_crossref_chapter_keeps_editor_and_book_metadata(self):
        raw = {"title": ["Capítulo sintético"], "type": "book-chapter", "editor": [{"given": "Beatriz", "family": "Souza"}],
               "edition-number": "2", "publisher-location": "Recife", "publisher": "Editora sintética",
               "container-title": ["Livro sintético"], "event": {"name": "Congresso sintético", "location": "Brasília"}}
        r = canonical(crossref_record(raw))
        self.assertEqual(r["editors"][0]["family"], "Souza")
        self.assertIn("editor = {Souza, Beatriz}", bib_entry(r))
        self.assertEqual(csl_item(r)["publisher-place"], "Recife")
        self.assertIn("In:", reference(r, "abnt"))
        self.assertIn("Editora sintética", reference(r, "apa"))

    def test_structured_date_is_not_replaced_by_year_only(self):
        self.assertEqual(csl_item(record(publication_date="2025-04-12"))["issued"]["date-parts"], [[2025, 4, 12]])
        self.assertEqual(csl_item(record(publication_date="2025-99-12"))["issued"]["date-parts"], [[2025]])

    def test_editor_csv_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = record(editors=[{"given": "Beatriz", "family": "Souza"}])
            export_all([r], tmp, {}, {})
            self.assertEqual(cli.load_records(Path(tmp) / "referencias.csv")[0]["editors"], r["editors"])

    def test_article_number_survives_reference_formatting(self):
        r = record(article_number="e123456")
        self.assertIn("e123456", reference(r, "apa"))
        self.assertIn("e123456", reference(r, "abnt"))
    def test_easyscielopack_record_without_doi_does_not_invent_url(self):
        r = canonical(easyscielopack_record({"title": "Fixture sintética", "authors": "Ana Silva", "year": "2025", "doi": "", "abstract": "English abstract"}))
        self.assertEqual(r["url"], "")
        self.assertEqual(r["language"], "")

class CacheAndGraphTests(unittest.TestCase):
    def test_distinct_pagination_tokens_do_not_share_cache(self):
        calls = []
        class Handle:
            status, headers = 200, {"Content-Type": "application/json"}
            def __init__(self, request): self.request = request
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def geturl(self): return self.request.full_url
            def read(self, limit): return json.dumps({"page": len(calls)}).encode()
        def opener(req, timeout):
            calls.append(req.full_url)
            return Handle(req)
        with tempfile.TemporaryDirectory() as tmp:
            client = Client(tmp, opener=opener)
            first = client.get("https://example.org/api", {"token": "one"})
            second = client.get("https://example.org/api", {"token": "two"})
            again = client.get("https://example.org/api", {"token": "one"})
            self.assertEqual(len(calls), 2)
            self.assertNotEqual(first.raw_path, second.raw_path)
            self.assertTrue(again.cached)
            self.assertNotIn("token=one", first.url)

    def test_bad_schema_becomes_failure_instead_of_aborting_search(self):
        from academic_core.http import Response
        class Fake:
            def get(self, *args, **kwargs): return Response(200, b'{"message": {"items": ["wrong"]}}')
        result = search(Fake(), "crossref", "q", {"max_per_query": 1})
        self.assertEqual(result.status, "error")
        self.assertFalse(result.complete)

    def test_single_year_omits_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = generate([record(selection="included")], tmp)
            self.assertNotIn("producao_line.svg", result["figures"])
            self.assertTrue(result["limitations"])

    def test_oversized_chart_records_limit_without_losing_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = generate([record(year=1900, selection="included"), record(year=2025, selection="included")], tmp)
            self.assertTrue(any("70 years" in v for v in result["limitations"]))
            self.assertTrue((Path(tmp) / "producao_por_ano.csv").exists())
            self.assertTrue((Path(tmp) / "manifesto_figuras.json").exists())
    def test_chart_csv_has_the_same_zero_years_as_the_figure(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate([record(year=2024, selection="included"), record(year=2026, selection="included")], tmp)
            self.assertIn("2025,0", (Path(tmp) / "producao_por_ano.csv").read_text())

if __name__ == "__main__":
    unittest.main()
