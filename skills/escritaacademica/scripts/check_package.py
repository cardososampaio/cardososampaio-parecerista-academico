#!/usr/bin/env python3
"""Validate package structure and optional deterministic comparator regressions."""

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True


REQUIRED = {
    "SKILL.md", "agents/openai.yaml", "assets/modelos.md", "assets/casos-avaliacao.json",
    "scripts/compare_text.py", "scripts/check_package.py",
    "references/integridade-fontes.md", "references/argumentacao.md",
    "references/generos-secoes.md", "references/redacao-revisao.md",
    "references/literatura.md", "references/qualitativa.md", "references/quantitativa.md",
    "references/teoria-historia.md", "references/prosa-estilo.md", "references/traducao.md",
    "references/internacionalizacao.md", "references/textos-longos.md",
    "references/auditoria.md", "references/avaliacao.md",
}


def inspect(root):
    errors = []
    for relative in sorted(REQUIRED):
        path = root / relative
        if not path.is_file() or path.stat().st_size == 0:
            errors.append("Missing or empty file: " + relative)
    if errors:
        return errors, {}
    main = (root / "SKILL.md").read_text(encoding="utf-8")
    parts = main.split("---", 2)
    if not main.startswith("---\n") or len(parts) != 3:
        errors.append("SKILL.md must start with delimited frontmatter")
    else:
        fields = {}
        for line in parts[1].splitlines():
            if line.strip():
                if ":" not in line:
                    errors.append("Malformed frontmatter")
                    continue
                key, value = line.split(":", 1)
                fields[key.strip()] = value.strip()
        if set(fields) != {"name", "description"} or fields.get("name") != "escritaacademica":
            errors.append("Frontmatter must contain name and description for escritaacademica")
        if not fields.get("description"):
            errors.append("Description is empty")
    if len(main.splitlines()) > 500:
        errors.append("SKILL.md exceeds 500 lines")
    markdowns = list(root.rglob("*.md"))
    for path in markdowns:
        body = path.read_text(encoding="utf-8")
        if "\x00" in body or "/root/.codex/" in body or "/workspace/scratch/" in body:
            errors.append("Nonportable content: " + str(path.relative_to(root)))
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", body):
            if re.match(r"^(?:https?|mailto):", target) or target.startswith("#"):
                continue
            relative = target.split("#", 1)[0]
            resolved = (path.parent / relative).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                errors.append("Link escapes package: " + target)
                continue
            if not resolved.exists():
                errors.append("Broken link in " + str(path.relative_to(root)) + ": " + target)
    for relative in sorted(REQUIRED):
        if relative not in {"SKILL.md", "agents/openai.yaml"} and relative not in main:
            errors.append("Resource not discoverable from SKILL.md: " + relative)
    metadata = (root / "agents/openai.yaml").read_text(encoding="utf-8")
    if "$escritaacademica" not in metadata:
        errors.append("UI prompt must invoke $escritaacademica")
    data = json.loads((root / "assets/casos-avaliacao.json").read_text(encoding="utf-8"))
    cases = data.get("cases", [])
    ids = set()
    for case in cases:
        if not all(case.get(key) for key in ("id", "request", "material", "criteria")):
            errors.append("Incomplete behavioral case")
        if case.get("id") in ids:
            errors.append("Duplicate case ID: " + str(case.get("id")))
        ids.add(case.get("id"))
        if not isinstance(case.get("criteria"), list):
            errors.append("Case criteria must be a list")
    if len(cases) < 10:
        errors.append("Missing operation coverage in behavioral cases")
    for reference in (root / "references").glob("*.md"):
        body = reference.read_text(encoding="utf-8")
        if len(body.splitlines()) > 100 and "## Percurso" not in body:
            errors.append("Long reference needs a contents list: " + reference.name)
    return errors, {"files": len(REQUIRED), "markdown_files": len(markdowns), "behavioral_cases": len(cases)}


def regressions(root):
    spec = importlib.util.spec_from_file_location("compare_text", root / "scripts/compare_text.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checks = []

    def check(label, condition):
        checks.append({"case": label, "passed": bool(condition)})

    original = 'Entrevistamos 34 gestores. Um afirmou "Não houve formação" (Souza, 2025, p. 12).'
    unchanged = module.compare(original, original, ["Não houve formação"])
    check("unchanged_invariants", unchanged["assessment"] == "no_tracked_differences")
    changed = module.compare(original, original.replace("34", "36").replace("Não houve", "Houve"), ["Não houve formação"])
    check("sample_difference_detected", changed["numbers"]["removed"].get("34") == 1 and changed["numbers"]["added"].get("36") == 1)
    check("protected_negation_detected", bool(changed["protected_fragments"]))
    check("changed_quote_detected", bool(changed["quotation_candidates"]["removed"]))
    check("citation_removal_detected", bool(module.compare(original, original.replace(" (Souza, 2025, p. 12)", ""))["citation_candidates"]["removed"]))
    check("citation_author_change_detected", bool(module.compare(original, original.replace("Souza", "Lima"))["citation_candidates"]["removed"]))
    check("negative_decimal_percent", module.NUMBER.findall("-0,25; 12,5%; 0.05; +3; 1e-3") == ["-0,25", "12,5%", "0.05", "+3", "1e-3"])
    check("unicode_minus_preserved", module.NUMBER.findall("−0,25") == ["−0,25"])
    check("duplicate_numeric_removed", module.compare("34 34", "34")["numbers"]["removed"].get("34") == 1)
    check("linewrap_in_quote_tolerated", module.compare('"texto longo"', '"texto\n longo"')["assessment"] == "no_tracked_differences")
    check("word_ceiling", module.compare("a", "a b c", max_words=2)["words"]["within_maximum"] is False)
    check("absent_protected_fragment", module.compare("a", "a", ["b"])["protected_fragments"][0]["issue"] == "not_found_in_original")
    check("semantic_limit_visible", module.compare("Esteve associado", "Causou")["semantic_fidelity"] == "not_assessed")
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    try:
        errors, counts = inspect(args.root)
        tests = regressions(args.root) if args.self_test and not errors else []
        errors.extend("Comparator regression failed: " + test["case"] for test in tests if not test["passed"])
    except (OSError, ValueError, UnicodeError, ImportError) as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    print(json.dumps({
        "passed": not errors, "counts": counts, "errors": errors, "deterministic_tests": tests,
        "behavioral_outputs_evaluated": False,
        "scope": "Package integrity and comparator regressions; not scientific or semantic validation",
    }, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
