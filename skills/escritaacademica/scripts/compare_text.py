#!/usr/bin/env python3
"""Local, advisory comparison. No semantic or scientific certification."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata


NUMBER = re.compile(r"(?<![\w])[-+−]?\d+(?:[.,]\d+)*(?:[eE][-+−]?\d+)?%?(?![\w])")
PAREN_CITATION = re.compile(r"\([^()\n]{0,240}\b(?:18|19|20)\d{2}[a-z]?\b[^()\n]{0,240}\)")
NARRATIVE_CITATION = re.compile(
    r"\b[A-ZÀ-Ý][\wÀ-ÿ'-]*(?:\s+(?:et\s+al\.|e|and|&|[A-ZÀ-Ý][\wÀ-ÿ'-]*)){0,4}"
    r"\s*\((?:18|19|20)\d{2}[a-z]?(?:\s*,\s*p{1,2}\.\s*\d+(?:[-–]\d+)?)?\)"
)
QUOTES = re.compile(r'"([^"\n]*(?:\n[^"\n]*)*)"|“([^”]*)”|«([^»]*)»')


def normalize(text):
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", text).strip())


def word_count(text):
    """Whitespace-delimited words, explicitly not a universal journal convention."""
    return len(text.split())


def difference(before, after):
    left, right = Counter(before), Counter(after)
    return {"removed": dict(left - right), "added": dict(right - left)}


def citation_tokens(text):
    return [normalize(m.group()) for m in PAREN_CITATION.finditer(text)] + [
        normalize(m.group()) for m in NARRATIVE_CITATION.finditer(text)
    ]


def quote_tokens(text):
    return [normalize(next(g for g in m.groups() if g is not None)) for m in QUOTES.finditer(text)]


def fingerprint_counts(values):
    """Do not echo quotation content in reports."""
    return [
        {"sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(), "count": count}
        for value, count in sorted(values.items())
    ]


def compare(before, after, protected=None, max_words=None):
    protected = protected or []
    numeric = difference(NUMBER.findall(before), NUMBER.findall(after))
    citations = difference(citation_tokens(before), citation_tokens(after))
    quoted = difference(quote_tokens(before), quote_tokens(after))
    normalized_before, normalized_after = normalize(before), normalize(after)
    protected_findings = []
    for fragment in protected:
        fragment = normalize(fragment)
        before_count = normalized_before.count(fragment)
        after_count = normalized_after.count(fragment)
        if before_count == 0 or after_count < before_count:
            protected_findings.append({
                "sha256": hashlib.sha256(fragment.encode("utf-8")).hexdigest(),
                "before_count": before_count,
                "after_count": after_count,
                "issue": "not_found_in_original" if before_count == 0 else "occurrences_removed",
            })
    words = {"before": word_count(before), "after": word_count(after), "convention": "whitespace"}
    if max_words is not None:
        words.update({"maximum": max_words, "within_maximum": words["after"] <= max_words})
    has_findings = bool(
        numeric["removed"] or numeric["added"] or citations["removed"] or citations["added"]
        or quoted["removed"] or quoted["added"] or protected_findings
        or (max_words is not None and words["after"] > max_words)
    )
    return {
        "schema_version": "1.0",
        "assessment": "differences_require_review" if has_findings else "no_tracked_differences",
        "semantic_fidelity": "not_assessed",
        "words": words,
        "numbers": numeric,
        "citation_candidates": citations,
        "quotation_candidates": {
            "removed": fingerprint_counts(quoted["removed"]),
            "added": fingerprint_counts(quoted["added"]),
        },
        "protected_fragments": protected_findings,
        "limitations": [
            "Changes may be legitimate in condensation, translation or authorized development.",
            "Quoted fragments are candidates; block quotes, single quotes and complex nesting need manual review.",
            "Citation detection is heuristic and does not verify metadata or source support.",
            "Matching text does not establish semantic fidelity; negations and inference need manual review.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path, help="Original UTF-8 text")
    parser.add_argument("after", type=Path, help="Revised UTF-8 text")
    parser.add_argument("--protected", type=Path, help="JSON array of exact nonempty protected fragments")
    parser.add_argument("--max-words", type=int, help="Maximum whitespace-delimited words")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on tracked differences; only use when all such changes are forbidden")
    args = parser.parse_args(argv)
    if args.max_words is not None and args.max_words < 0:
        parser.error("--max-words must be nonnegative")
    try:
        before = args.before.read_text(encoding="utf-8-sig")
        after = args.after.read_text(encoding="utf-8-sig")
        protected = [] if args.protected is None else json.loads(args.protected.read_text(encoding="utf-8-sig"))
        if not isinstance(protected, list) or any(not isinstance(s, str) or not s.strip() for s in protected):
            raise ValueError("--protected must contain a JSON array of nonempty strings")
        report = compare(before, after, protected, args.max_words)
    except (OSError, ValueError, UnicodeError) as exc:
        print("Input error: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if args.strict and report["assessment"] == "differences_require_review" else 0


if __name__ == "__main__":
    sys.exit(main())
