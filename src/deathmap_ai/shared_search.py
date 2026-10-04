"""Resource-specific shared-intent searches and deterministic JSON exports.

ORCS searches its complete cached metadata index locally. OmicsDI reuses the
repaired intake and all historical receipts. Outputs retain separate
resource identities and original text without scientific classification or merge.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path

from deathmap_ai.orcs import _flatten_text
from deathmap_ai.omicsdi import utc_now
from deathmap_ai.omicsdi_queries import QUERIES as OMICSDI_QUERIES
from deathmap_ai.resource_migration import write_json, digest

SEARCH_ID = "immune-crispr-coculture-v01"
SCHEMA = "deathmap-shared-resource-v1"
INTENT = "CRISPR cancer-immune coculture; either perturbed population, human/mouse, direct/indirect configurations, all library breadths; missing metadata is not automatic exclusion"
ORCS_RULES = {
    "Q01": ["coculture"], "Q02": ["co-culture"], "Q03": ["co culture"],
    "Q04": ["t cell", "t-cell", "t cells", "t-cells", "t lymphocyte", "t-lymphocyte", "til", "car-t"],
    "Q05": ["natural killer", "nk cell", "nk-cell", "nk cells", "nk-cells"],
    "Q06": ["immune killing", "immune-mediated killing", "immune mediated killing", "immune cytotoxicity"],
}


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _reference(path, folder):
    import os
    return Path(os.path.relpath(path, folder)).as_posix()


def reported_fields(metadata):
    """Expose publication/accession/URL-bearing native fields with their paths.

    This is a structural projection, not identifier extraction from prose. Full
    native metadata remains available even for unrecognized field names.
    """
    fields = []
    def visit(value, path):
        if isinstance(value, dict):
            for key, child in value.items():
                name = str(key)
                child_path = path + "." + name if path else name
                if re.search(r"pubmed|pmid|doi|publication|author|accession|cross.reference|url|link|gse_id|ena_project|source_id", name, re.I):
                    fields.append({"field_path": child_path, "value": child})
                else:
                    visit(child, child_path)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                visit(child, f"{path}[{i}]")
        elif isinstance(value, str) and value.startswith(("https://", "http://")):
            fields.append({"field_path": path, "value": value})
    visit(metadata, "")
    return fields


def match_orcs(row):
    """Return boundary-aware literal matches with full original field text.

    Case-insensitive matching adapts native T-cell/NK-cell terms to shared
    concepts. No species, library breadth or CRISPR subtype eligibility gate is
    applied. ORCS membership supplies search scope, not a qualifying assertion.
    """
    hits = []
    for field, text in _flatten_text(row):
        for qid, terms in ORCS_RULES.items():
            for term in terms:
                match = re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, re.I)
                if match:
                    hits.append({"query_id": qid, "rule_term": term, "source_field_path": field,
                                 "source_text": text, "matched_text": match.group(), "native_rank": None})
    return hits


def orcs_package(cache, folder):
    """Search all cached native screens; retain publication siblings as context."""
    run = cache / "legacy/20260904T213941Z"
    from deathmap_ai.orcs_paths import resolve_historical
    raw = resolve_historical(run / "orcs-screens.raw.json")
    rows, context = _read(raw), _read(run / "summary.json")
    if len(rows) != context["screens_retrieved"] or len({r["SCREEN_ID"] for r in rows}) != len(rows):
        raise ValueError("ORCS cache is not the recorded complete unique screen index")
    sources, candidates, hits = [], [], []
    direct = {r["SCREEN_ID"]: match_orcs(r) for r in rows}
    publication_matches = {}
    for row in rows:
        if direct[row["SCREEN_ID"]] and row.get("SOURCE_ID"):
            publication_matches.setdefault((row.get("SOURCE_TYPE"), row["SOURCE_ID"]), []).append(row["SCREEN_ID"])
    for index, row in enumerate(rows):
        rid = "orcs-" + SEARCH_ID + "-" + row["SCREEN_ID"]
        reference = {"file": _reference(raw, folder), "json_index": index,
                     "retrieved_at": context["retrieved_at"], "reuse": "cached_complete_index"}
        sources.append({"source_record_id": rid, "native_metadata": row, "provenance": reference})
        matches = direct[row["SCREEN_ID"]]
        siblings = publication_matches.get((row.get("SOURCE_TYPE"), row.get("SOURCE_ID")), [])
        if not matches and not siblings:
            continue
        candidates.append({"record_id": rid, "candidate_type": "screen", "native_record_id": row["SCREEN_ID"],
            "source_record_refs": [rid], "title": row.get("TITLE"), "screen_name": row.get("SCREEN_NAME"),
            "description": row.get("NOTES"), "publication_information": {
                "source_type": row.get("SOURCE_TYPE"), "source_id": row.get("SOURCE_ID"), "author": row.get("AUTHOR")},
            "reported_identifiers_and_links": reported_fields(row),
            "inclusion_basis": "direct_metadata_match" if matches else "publication_sibling_context",
            "context_for_record_ids": ["orcs-" + SEARCH_ID + "-" + other for other in siblings if other != row["SCREEN_ID"]],
            "review_status": "unreviewed", "retrieved_at": context["retrieved_at"]})
        hits.extend({**hit, "record_id": rid, "provenance": reference} for hit in matches)
    info = {"queries": ORCS_RULES, "query_translation": "Case-insensitive literal native-field matches with word boundaries; no biological eligibility filters",
            "source_index_records": len(rows), "cache_date": context["retrieved_at"],
            "direct_candidates": sum(c["inclusion_basis"] == "direct_metadata_match" for c in candidates),
            "sibling_context_candidates": sum(c["inclusion_basis"] == "publication_sibling_context" for c in candidates),
            "candidate_cap": None, "detail_cap": None, "detail_availability": "Full cached native metadata for every indexed screen",
            "completion": "complete_cached_index_searched", "new_metadata_requests": 0,
            "reuse": "Complete index and source dates reused; historical candidate subset not used as search input",
            "source_references": [_reference(raw, folder), _reference(run / "summary.json", folder)],
            "stop_reasons": ["complete_cached_index_searched"]}
    return sources, candidates, hits, [{"type": "resource_limitation", "message": "Local matches and publication siblings are unadjudicated; no source-reported publication titles when absent"}], info


def omicsdi_package(cache, folder):
    """Reuse repaired OmicsDI candidates and all 89 receipts without any retrieval."""
    run = cache / "legacy/20260908T144947226699Z-repair-v2"
    state, repair = _read(run / "resume_state.json"), _read(run / "repair_manifest.json")
    sources, candidates, hits, issues = [], [], [], []
    for record in state["records"].values():
        rid = record["record_id"]
        native = {"search": [o["metadata"] for o in record["search_observations"]], "detail": record["detail_metadata"]}
        refs = list(dict.fromkeys([o["raw_response_ref"] for o in record["search_observations"]] +
                                  ([record["detail_response_ref"]] if record.get("detail_response_ref") else [])))
        sources.append({"source_record_id": rid, "native_metadata": native,
                        "provenance": {"files": [_reference(run / ref, folder) for ref in refs],
                                       "original_retrieved_at": record["retrieved_at"], "historical_record": record}})
        candidates.append({"record_id": rid, "candidate_type": "dataset", "source_record_refs": [rid],
            "native_record_id": record["native_record_id"], "repository_original": record["repository_original"],
            "title": record["title_original"], "description": record["evidence_text_original"],
            "reported_identifiers_and_links": reported_fields(native), "review_status": "unreviewed",
            "detail_retrieval_status": record["detail_retrieval_status"], "detail_parse_status": record["detail_parse_status"],
            "detail_allowance_band": record.get("detail_allowance_band"),
            "detail_retrieval_ordinal": record.get("detail_retrieval_ordinal"),
            "identifier_conflicts": record["identifier_conflicts"]})
        issues.extend({"type": "identifier_difference", "record_id": rid, "evidence": conflict}
                      for conflict in record["identifier_conflicts"])
        if record["detail_retrieval_status"] != "received":
            issues.append({"type": "missing_detail", "record_id": rid, "status": record["detail_retrieval_status"]})
    for hit in state["query_hits"]:
        hits.append({**hit, "current_response_ref": _reference(run / hit["raw_response_ref"], folder),
                     "raw_response_ref_is_historical_relative_to_original_run": True})
    issues.append({"type": "historical_cap_violation", "detail_receipts": 89, "cap": 50,
                   "within_allowance": 50, "excess": 39, "history_ref": _reference(run / "historical/run_manifest.json", folder)})
    issues.extend({"type": "historical_error", "evidence": e} for e in state["errors"])
    info = {"queries": OMICSDI_QUERIES, "query_translation": "Six established literal queries unchanged",
            "candidate_cap": 100, "detail_cap": 50, "detail_receipts": len(state["detail_retrievals"]),
            "within_allowance": 50, "excess_details": 39, "identifier_discrepancies": 38, "missing_details": 11,
            "completion": "reused_bounded_search_candidate_cap", "new_metadata_requests": 0,
            "reuse": "Repaired 100-candidate search and all 89 saved details; original dates and histories retained",
            "cache_date": state["created_at"], "historical_invocations": state["invocations"],
            "query_progress": {q: {k: v for k, v in data.items() if k not in ("keys", "buffer")}
                               for q, data in state["queries"].items()},
            "detail_availability": repair["counts"], "network_blocked_reason": state["network_blocked_reason"],
            "source_references": [_reference(run / "resume_state.json", folder), _reference(run / "repair_manifest.json", folder)],
            "stop_reasons": ["candidate_cap", "historical_detail_cap_exceeded_no_more_retrieval"]}
    return sources, candidates, hits, issues, info


def export_package(root: Path, package: str, *, verify=False, destination=None):
    """Build or verify six JSON files deterministically from current cached inputs.

    Existing search versions are never overwritten. Verification reuses the saved
    transformation timestamp and compares exact JSON bytes after regenerating in
    memory. It performs no network requests and imports no spreadsheet runtime.
    """
    root = root.resolve()
    folder = root / "outputs" / package / SEARCH_ID
    cache = root / "outputs" / package / "cache"
    manifest_path = folder / "search_manifest.json"
    if manifest_path.exists() and not verify and destination is None:
        raise ValueError("Search version exists; use --verify for offline regeneration or explicitly increment version")
    transformed_at = _read(manifest_path)["transformed_at"] if verify else utc_now()
    builder = {"orcs": orcs_package, "omicsdi": omicsdi_package}[package]
    sources, candidates, hits, issues, info = builder(cache, folder)
    by_id = {source["source_record_id"]: source for source in sources}
    if len(by_id) != len(sources) or len({c["record_id"] for c in candidates}) != len(candidates):
        raise ValueError("Duplicate record identity in export")
    candidate_ids = {c["record_id"] for c in candidates}
    if any(hit["record_id"] not in candidate_ids for hit in hits):
        raise ValueError("Unresolved query-to-candidate reference")
    if any(ref not in by_id for c in candidates for ref in c["source_record_refs"]):
        raise ValueError("Unresolved candidate-to-native reference")
    for ref in info["source_references"]:
        if not (folder / ref).resolve().is_file():
            raise ValueError(f"Missing migrated source: {ref}")
    base = {"schema_version": SCHEMA, "package": package, "search_id": SEARCH_ID}
    manifest = {**base, "shared_intent": INTENT, "transformed_at": transformed_at,
        "resource_version": None, "counts": {"source_records": len(sources), "candidates": len(candidates),
        "query_hits": len(hits), "issues": len(issues)}, **info,
        "source_hashes": {ref: digest((folder / ref).resolve()) for ref in info["source_references"]}}
    files = {"search_manifest.json": manifest, "source_records.json": {**base, "records": sources},
             "candidates.json": {**base, "candidates": candidates}, "query_hits.json": {**base, "hits": hits},
             "issues.json": {**base, "issues": issues},
             "candidate_summary.json": {**base, "candidates": [
                 {**candidate, "native_metadata": [by_id[ref]["native_metadata"] for ref in candidate["source_record_refs"]]}
                 for candidate in candidates]}}
    for name, value in files.items():
        text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        if verify:
            if (folder / name).read_text(encoding="utf-8") != text:
                raise ValueError(f"Offline regeneration mismatch: {package}/{name}")
        else:
            write_json((destination or folder) / name, value)
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Shared-intent resource search and Python JSON export")
    parser.add_argument("package", choices=["orcs", "omicsdi", "all"])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    packages = ("orcs", "omicsdi") if args.package == "all" else (args.package,)
    results = {}
    for package in packages:
        manifest = export_package(args.root, package, verify=args.verify)
        results[package] = {"counts": manifest["counts"], "completion": manifest["completion"]}
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
