"""Optional PDF retrieval, only after the user has accepted the offer."""
from __future__ import annotations
import os
from pathlib import Path
from urllib.parse import quote
from .http import atomic_json, blocked
from .model import unique

def validate_pdf(body):
    if blocked(body) or b"%PDF-" not in body[:1024]:
        return False, "not_a_pdf"
    if b"%%EOF" not in body[-4096:]:
        return False, "pdf_incomplete_or_unrecognized"
    try:
        from pypdf import PdfReader
        from io import BytesIO
        reader = PdfReader(BytesIO(body), strict=False)
        if not len(reader.pages):
            return False, "pdf_without_pages"
        return True, "structural_validation"
    except ImportError:
        return True, "signature_and_eof_only"
    except Exception:
        return False, "pdf_structural_error"

def retrieve_pdfs(records, client, out, approved=False, maximum=20):
    if not approved:
        raise ValueError("PDF retrieval requires the user's explicit acceptance. Pass --approved only after acceptance.")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    log = []
    email = os.getenv("UNPAYWALL_EMAIL", "")
    for r in records[:maximum]:
        urls = list(r.get("pdf_urls") or [])
        if email and r.get("doi"):
            response = client.get("https://api.unpaywall.org/v2/" + quote(r["doi"], safe=""), {"email": email})
            if response.status == 200 and not blocked(response.body):
                try:
                    data = response.json()
                    urls.extend(l["url_for_pdf"] for l in data.get("oa_locations", []) or [] if l.get("url_for_pdf"))
                except (ValueError, TypeError):
                    pass
        row = {"record_id": r["record_id"], "title": r["title"], "status": "not_found", "attempts": [], "file": ""}
        dest = out / (r["record_id"] + ".pdf")
        if dest.exists():
            ok, validation = validate_pdf(dest.read_bytes())
            if ok:
                row.update(status="already_downloaded", file=str(dest), validation=validation)
                log.append(row)
                continue
        for url in unique(urls)[:8]:
            response = client.get(url, cache=False, headers={"Accept": "application/pdf"}, max_bytes=32_000_000)
            if response.status != 200:
                row["attempts"].append({"url": response.url, "reason": "access_or_network_error", "status": response.status})
                continue
            ok, validation = validate_pdf(response.body)
            row["attempts"].append({"url": response.url, "validation": validation})
            if ok:
                dest.write_bytes(response.body)
                row.update(status="downloaded", file=str(dest), validation=validation)
                break
        log.append(row)
        atomic_json(out / "download_log.json", log)
    atomic_json(out / "download_log.json", log)
    return log
