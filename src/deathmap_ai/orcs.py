"""Retrieve and inspect BioGRID ORCS metadata without downloading screen results.

This module owns the metadata-only boundary for the first ORCS evaluation. It
retrieves controlled vocabularies and screen descriptions, preserves the native
responses, and emits unreviewed discovery records. It intentionally does not call
the per-screen score endpoint or download experimental files.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ORCS_BASE_URL = "https://orcsws.thebiogrid.org"
QUERY_STRATEGY_ID = "orcs-coculture-metadata-v3"
DIRECT_COCULTURE_RULES = frozenset({"co-culture", "coculture", "co culture"})

# Keep spelling variants separate so the summary can reveal whether ORCS metadata
# treats them differently. The normalized form is used only for matching.
CANDIDATE_RULES: dict[str, tuple[str, ...]] = {
    "co-culture": ("co-culture",),
    "coculture": ("coculture",),
    "co culture": ("co culture",),
    "cell-cell": ("cell-cell", "cell cell"),
    "car-t": ("car-t", "car t", "cart"),
    "t-cell": ("t-cell", "t cell"),
    "nk-cell": ("nk-cell", "nk cell", "natural killer"),
    "immune-killing": ("immune killing", "immune-mediated killing"),
    "effector-target": ("effector-to-target", "effector target", "e:t ratio"),
}


@dataclass(frozen=True)
class RunPaths:
    """Files produced by one metadata retrieval and candidate-generation run."""

    run_dir: Path
    screens_raw: Path
    vocabs_raw: Path
    screen_metadata_csv: Path
    records_jsonl: Path
    review_csv: Path
    summary_json: Path


def load_access_key(key_file: Path) -> str:
    """Read and validate an ORCS key without returning it in diagnostic messages."""

    key = key_file.read_text(encoding="utf-8-sig").strip()
    if not re.fullmatch(r"[A-Za-z0-9]{32}", key):
        raise ValueError("The ORCS access-key file must contain one 32-character key.")
    return key


def _fetch_json(endpoint: str, access_key: str, params: dict[str, Any], timeout: int) -> Any:
    """Fetch one JSON metadata endpoint while keeping the secret out of logs."""

    query = {**params, "accesskey": access_key, "format": "json"}
    request = Request(
        f"{ORCS_BASE_URL}/{endpoint.lstrip('/')}?{urlencode(query)}",
        headers={"User-Agent": "deathmap-ai/0.1 metadata-pilot"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except HTTPError as error:
        # HTTPError includes the complete request URL, which contains the access
        # key. Replace it with a status-only message before it reaches logs.
        raise RuntimeError(f"ORCS metadata request failed with HTTP status {error.code}.") from None
    except URLError:
        raise RuntimeError("ORCS metadata request failed because the service was unreachable.") from None


def _records_from_payload(payload: Any) -> list[dict[str, Any]]:
    """Locate the native screen-record list without assuming one JSON envelope."""

    if isinstance(payload, list) and all(isinstance(item, dict) for item in payload):
        return payload
    if isinstance(payload, dict):
        for key in ("screens", "results", "data"):
            value = payload.get(key)
            if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                return value
        # Some APIs serialize numeric record IDs as mapping keys.
        if payload and all(isinstance(value, dict) for value in payload.values()):
            return list(payload.values())
    raise ValueError("The ORCS screen response did not contain a recognizable record list.")


def _flatten_text(value: Any) -> list[tuple[str, str]]:
    """Return source field paths and scalar text for transparent rule matching."""

    flattened: list[tuple[str, str]] = []

    def visit(item: Any, path: str) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                visit(child, f"{path}.{key}" if path else str(key))
        elif isinstance(item, list):
            for index, child in enumerate(item):
                visit(child, f"{path}[{index}]")
        elif item is not None:
            flattened.append((path, str(item)))

    visit(value, "")
    return flattened


def match_candidate_rules(record: dict[str, Any]) -> list[dict[str, str]]:
    """Report every generic co-culture rule and source field that matched."""

    matches: list[dict[str, str]] = []
    for field, original in _flatten_text(record):
        searchable = re.sub(r"\s+", " ", original.casefold())
        for rule_name, variants in CANDIDATE_RULES.items():
            for variant in variants:
                if variant in searchable:
                    matches.append(
                        {"rule": rule_name, "matched_text": variant, "source_field": field}
                    )
                    break
    # A field can repeat the same term in nested values; retain only distinct
    # evidence locations so review output stays readable.
    unique = {(m["rule"], m["matched_text"], m["source_field"]): m for m in matches}
    return list(unique.values())


def _first_value(record: dict[str, Any], aliases: Iterable[str]) -> Any:
    """Read a native field by normalized alias without changing the raw record."""

    normalized = {re.sub(r"[^a-z0-9]", "", str(k).casefold()): v for k, v in record.items()}
    for alias in aliases:
        value = normalized.get(re.sub(r"[^a-z0-9]", "", alias.casefold()))
        if value not in (None, ""):
            return value
    return None


def _stable_record_id(run_id: str, native_id: Any, native_record: dict[str, Any]) -> str:
    """Create a stable identifier even when ORCS omits its native screen ID."""

    identity = str(native_id) if native_id is not None else json.dumps(
        native_record, sort_keys=True, ensure_ascii=True
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
    return f"orcs-{run_id}-{digest}"


def build_discovery_record(
    native_record: dict[str, Any],
    run_id: str,
    retrieved_at: str,
    raw_response_ref: str,
    *,
    matches: list[dict[str, str]] | None = None,
    inclusion_basis: str = "direct_rule_match",
    anchor_screen_ids: list[str] | None = None,
) -> dict[str, Any] | None:
    """Convert one matching ORCS screen description into an unreviewed intake record."""

    matches = match_candidate_rules(native_record) if matches is None else matches
    if not matches:
        return None

    native_id = _first_value(native_record, ("screen_id", "screenid", "id"))
    source_type = _first_value(native_record, ("source_type",))
    source_id = _first_value(native_record, ("source_id",))
    # ORCS represents the publication as a typed SOURCE_ID rather than a PMID
    # field. Preserve the type check so another source identifier is never
    # silently relabeled as a PubMed identifier.
    pmid = source_id if str(source_type).casefold() == "pubmed" else None
    return {
        "record_id": _stable_record_id(run_id, native_id, native_record),
        "run_id": run_id,
        "resource_name": "BioGRID ORCS",
        "resource_version": None,
        "retrieved_at": retrieved_at,
        "query_strategy_id": QUERY_STRATEGY_ID,
        "result_rank": None,
        "native_record_id": native_id,
        "native_url": (
            f"https://orcs.thebiogrid.org/Screen/{native_id}" if native_id is not None else None
        ),
        "candidate_type": "screen",
        "title_original": _first_value(native_record, ("title", "publication_title")),
        "screen_name_reported": _first_value(native_record, ("screen_name",)),
        "pmid_reported": pmid,
        "doi_reported": _first_value(native_record, ("doi",)),
        "accessions_reported": [],
        "evidence_text_original": matches,
        "inclusion_basis": inclusion_basis,
        "anchor_screen_ids": anchor_screen_ids or [],
        "screen_format_reported": _first_value(native_record, ("screen_format",)),
        "experimental_setup_reported": _first_value(native_record, ("experimental_setup",)),
        "condition_name_reported": _first_value(native_record, ("condition_name",)),
        "condition_dosage_reported": _first_value(native_record, ("condition_dosage",)),
        "library_name_reported": _first_value(native_record, ("library",)),
        "library_type_reported": _first_value(native_record, ("library_type",)),
        "library_size_reported": _first_value(native_record, ("full_size",)),
        "methodology_reported": _first_value(native_record, ("methodology",)),
        "enzyme_reported": _first_value(native_record, ("enzyme",)),
        "cell_line_reported": _first_value(native_record, ("cell_line",)),
        "cell_type_reported": _first_value(native_record, ("cell_type",)),
        "phenotype_original": _first_value(native_record, ("phenotype",)),
        "organism_reported": _first_value(
            native_record, ("organism_official", "organism_id")
        ),
        "raw_response_ref": raw_response_ref,
        "source_metadata": native_record,
        "review_status": "unreviewed",
    }


def _make_run_paths(output_root: Path, run_id: str) -> RunPaths:
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return RunPaths(
        run_dir=run_dir,
        screens_raw=run_dir / "orcs-screens.raw.json",
        vocabs_raw=run_dir / "orcs-vocabs.raw.json",
        screen_metadata_csv=run_dir / "orcs-screen-metadata.csv",
        records_jsonl=run_dir / "discovery-records.jsonl",
        review_csv=run_dir / "review-sample.csv",
        summary_json=run_dir / "summary.json",
    )


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_screen_metadata_csv(path: Path, native_records: list[dict[str, Any]]) -> None:
    """Write every ORCS screen-description field without downloading result rows.

    Native field names and values are preserved. If ORCS later introduces a
    nested value, it is serialized as JSON in one cell instead of being dropped
    or flattened into a scientifically ambiguous column.
    """

    fieldnames = list(dict.fromkeys(key for record in native_records for key in record))
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in native_records:
            writer.writerow(
                {
                    field: (
                        json.dumps(value, ensure_ascii=False)
                        if isinstance(value, (dict, list))
                        else value
                    )
                    for field, value in record.items()
                }
            )


def _write_review_sample(path: Path, records: list[dict[str, Any]], limit: int) -> None:
    """Write a compact table for human inspection without asserting eligibility."""

    fields = [
        "record_id",
        "native_record_id",
        "screen_name_reported",
        "pmid_reported",
        "inclusion_basis",
        "screen_format_reported",
        "experimental_setup_reported",
        "condition_name_reported",
        "condition_dosage_reported",
        "library_name_reported",
        "library_type_reported",
        "library_size_reported",
        "methodology_reported",
        "enzyme_reported",
        "cell_line_reported",
        "phenotype_original",
        "matched_rules",
        "screen_evidence_role_reviewed",
        "perturbed_population_reviewed",
        "interacting_population_reviewed",
        "library_scope_reviewed",
        "library_scope_evidence",
        "phenotype_normalized",
        "review_status",
        "reviewer_notes",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records[:limit]:
            writer.writerow(
                {
                    "record_id": record["record_id"],
                    "native_record_id": record["native_record_id"],
                    "screen_name_reported": record["screen_name_reported"],
                    "pmid_reported": record["pmid_reported"],
                    "inclusion_basis": record["inclusion_basis"],
                    "screen_format_reported": record["screen_format_reported"],
                    "experimental_setup_reported": record["experimental_setup_reported"],
                    "condition_name_reported": record["condition_name_reported"],
                    "condition_dosage_reported": record["condition_dosage_reported"],
                    "library_name_reported": record["library_name_reported"],
                    "library_type_reported": record["library_type_reported"],
                    "library_size_reported": record["library_size_reported"],
                    "methodology_reported": record["methodology_reported"],
                    "enzyme_reported": record["enzyme_reported"],
                    "cell_line_reported": record["cell_line_reported"],
                    "phenotype_original": record["phenotype_original"],
                    "matched_rules": " | ".join(
                        sorted({m["rule"] for m in record["evidence_text_original"]})
                    ),
                    "screen_evidence_role_reviewed": "",
                    "perturbed_population_reviewed": "",
                    "interacting_population_reviewed": "",
                    "library_scope_reviewed": "",
                    "library_scope_evidence": "",
                    "phenotype_normalized": "",
                    "review_status": "unreviewed",
                    "reviewer_notes": "",
                }
            )


def build_candidate_records(
    native_records: list[dict[str, Any]],
    run_id: str,
    retrieved_at: str,
    raw_response_ref: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Build direct candidates plus screen context from anchored publications.

    Returns the complete ordered candidate list, direct rule matches, and added
    publication-context records. Context expansion uses exact co-culture spelling
    rules only; broad T-cell wording is not sufficient to pull in sibling screens.
    """

    direct_records = [
        converted
        for native in native_records
        if (converted := build_discovery_record(
            native, run_id, retrieved_at, raw_response_ref
        ))
        is not None
    ]
    candidate_anchor_screen_ids_by_pmid: dict[str, list[str]] = {}
    for record in direct_records:
        matched_rules = {match["rule"] for match in record["evidence_text_original"]}
        if record["pmid_reported"] is not None and matched_rules & DIRECT_COCULTURE_RULES:
            candidate_anchor_screen_ids_by_pmid.setdefault(
                str(record["pmid_reported"]), []
            ).append(
                str(record["native_record_id"])
            )

    # The anchor links are useful on both direct and contextual records, so a
    # reviewer never has to reconstruct which screens caused the expansion.
    for record in direct_records:
        pmid = str(record["pmid_reported"])
        if pmid in candidate_anchor_screen_ids_by_pmid:
            record["anchor_screen_ids"] = candidate_anchor_screen_ids_by_pmid[pmid]

    direct_native_ids = {str(record["native_record_id"]) for record in direct_records}
    context_records: list[dict[str, Any]] = []
    for native in native_records:
        native_id = _first_value(native, ("screen_id", "screenid", "id"))
        source_type = _first_value(native, ("source_type",))
        source_id = _first_value(native, ("source_id",))
        pmid = str(source_id) if str(source_type).casefold() == "pubmed" else None
        if (
            pmid not in candidate_anchor_screen_ids_by_pmid
            or str(native_id) in direct_native_ids
        ):
            continue
        context_match = [
            {
                "rule": "publication-context",
                "matched_text": pmid,
                "source_field": "SOURCE_ID",
            }
        ]
        converted = build_discovery_record(
            native,
            run_id,
            retrieved_at,
            raw_response_ref,
            matches=context_match,
            inclusion_basis="publication_sibling_context",
            anchor_screen_ids=candidate_anchor_screen_ids_by_pmid[pmid],
        )
        if converted is not None:
            context_records.append(converted)

    records = direct_records + context_records
    priority = {name: index for index, name in enumerate(CANDIDATE_RULES)}
    priority["publication-context"] = len(priority)
    anchor_pmids = set(candidate_anchor_screen_ids_by_pmid)
    records.sort(
        key=lambda record: (
            0 if str(record["pmid_reported"]) in anchor_pmids else 1,
            str(record["pmid_reported"] or ""),
            int(record["native_record_id"])
            if str(record["native_record_id"]).isdigit()
            else 0,
            min(priority[match["rule"]] for match in record["evidence_text_original"]),
        )
    )
    return records, direct_records, context_records


def run_metadata_probe(
    access_key: str,
    output_root: Path,
    *,
    timeout_seconds: int | None = None,
    review_sample_size: int = 10,
) -> tuple[RunPaths, dict[str, Any]]:
    """Run the metadata-only ORCS probe and return paths plus its summary.

    The deadline is checked between network operations and transformations. The
    individual HTTP requests also receive the remaining timeout so a stalled
    service cannot silently violate the iterative runtime budget.
    """

    started = time.monotonic()
    retrieved_at = datetime.now(timezone.utc).isoformat()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    def remaining_timeout() -> int:
        if timeout_seconds is None:
            return 20
        remaining = int(timeout_seconds - (time.monotonic() - started))
        if remaining < 1:
            raise TimeoutError("ORCS metadata probe exceeded its runtime budget.")
        return min(20, remaining)

    vocab_categories = _fetch_json("vocabs/", access_key, {}, remaining_timeout())
    if not isinstance(vocab_categories, dict):
        raise ValueError("The ORCS vocabulary-category response was not a mapping.")
    vocab_terms = {
        str(category_id): _fetch_json(
            f"vocab/{category_id}", access_key, {}, remaining_timeout()
        )
        for category_id in vocab_categories
    }
    vocabs_payload = {"categories": vocab_categories, "terms_by_category": vocab_terms}
    screens_payload = _fetch_json(
        "screens/", access_key, {"start": 0, "max": 10000}, remaining_timeout()
    )
    # Create durable output only after both requests succeed, so a transient
    # network failure cannot leave a directory that resembles a completed run.
    paths = _make_run_paths(output_root, run_id)
    _write_json(paths.vocabs_raw, vocabs_payload)
    _write_json(paths.screens_raw, screens_payload)

    native_records = _records_from_payload(screens_payload)
    _write_screen_metadata_csv(paths.screen_metadata_csv, native_records)
    # References are relative to the run directory so a run can be moved or
    # archived without embedding one researcher's local filesystem path.
    relative_raw_ref = paths.screens_raw.name
    records, direct_records, context_records = build_candidate_records(
        native_records, run_id, retrieved_at, relative_raw_ref
    )
    with paths.records_jsonl.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    _write_review_sample(paths.review_csv, records, review_sample_size)
    # Count candidate records per rule, not repeated field-level occurrences.
    rule_counts = Counter(
        rule
        for record in records
        for rule in {match["rule"] for match in record["evidence_text_original"]}
    )
    unique_pmids = {str(r["pmid_reported"]) for r in records if r["pmid_reported"] is not None}
    completeness_fields = {
        "screen_id": ("screen_id",),
        "publication_source_id": ("source_id",),
        "screen_name": ("screen_name",),
        "organism": ("organism_official", "organism_id"),
        "cell_line": ("cell_line",),
        "cell_type": ("cell_type",),
        "phenotype": ("phenotype",),
        "condition": ("condition_name",),
        "experimental_setup": ("experimental_setup",),
        "library": ("library",),
        "methodology": ("methodology",),
    }
    candidate_field_non_null = {
        label: sum(
            _first_value(record["source_metadata"], aliases) is not None for record in records
        )
        for label, aliases in completeness_fields.items()
    }
    elapsed = round(time.monotonic() - started, 3)
    summary = {
        "run_id": run_id,
        "resource_name": "BioGRID ORCS",
        "query_strategy_id": QUERY_STRATEGY_ID,
        "retrieved_at": retrieved_at,
        "metadata_only": True,
        "screens_retrieved": len(native_records),
        "candidate_records": len(records),
        "direct_rule_match_records": len(direct_records),
        "publication_context_records": len(context_records),
        "unique_reported_pmids": len(unique_pmids),
        "candidate_rule_matches": dict(sorted(rule_counts.items())),
        "candidate_field_non_null": candidate_field_non_null,
        "review_sample_size": min(review_sample_size, len(records)),
        "elapsed_seconds": elapsed,
        "runtime_budget_seconds": timeout_seconds,
    }
    _write_json(paths.summary_json, summary)
    return paths, summary
