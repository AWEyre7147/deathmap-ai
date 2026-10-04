"""Rebuild OmicsDI text records from saved responses without networking.

The source run is read-only. A new output directory preserves raw bytes and
historical checkpoints, maps request order to detail receipts, and blocks network
resume. Conflicting returned identities remain source claims attached by request
provenance; this repair does not adjudicate scientific or repository equivalence.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path

from deathmap_ai.omicsdi import ADAPTER_VERSION, DETAIL_ATTEMPT_LIMIT, _reported_fields, utc_now
from deathmap_ai.omicsdi_metadata import normalize_detail


def _hashes(directory):
    """Hash every original file so even historical outputs are checked for changes."""
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob("*")) if p.is_file()}


def _json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _jsonl(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def repair_saved_run(source_dir: Path, output_dir: Path):
    """Create a new, network-blocked repair directory from one historical run.

    Copies native responses byte-for-byte, preserves original invocation history,
    candidate IDs and errors, and emits corrected records plus a response inventory.
    The response order uses sequential request-log positions, never file timestamps.
    Missing/ambiguous ordering is reported rather than guessed. Raises ValueError
    for overlapping/existing output paths or an inconsistent source record map.
    No transport function is called and no source file is written.
    """
    source_dir, output_dir = source_dir.resolve(), output_dir.resolve()
    if output_dir.exists() or source_dir in output_dir.parents or output_dir in source_dir.parents:
        raise ValueError("Repair output must be a new directory outside the original run")
    before = _hashes(source_dir)
    original = json.loads((source_dir / "resume_state.json").read_text(encoding="utf-8"))
    state = copy.deepcopy(original)
    by_id = {record["record_id"]: key for key, record in state["records"].items()}
    if len(by_id) != len(state["records"]):
        raise ValueError("Duplicate internal record IDs prevent unambiguous repair")

    # Associate bodies with logged requests rather than interpreting the returned
    # repository label as a new candidate key. This preserves all native conflicts.
    events_by_ref = {}
    attempts = Counter()
    received_order = []
    for invocation_index, invocation in enumerate(original["invocations"], 1):
        for request_index, event in enumerate(invocation["requests"], 1):
            if event["kind"] != "detail":
                continue
            attempts[event["identity"]] += 1
            evidence = {"invocation_index": invocation_index, "request_index": request_index,
                        "event": event}
            events_by_ref.setdefault(event["raw_response_ref"], []).append(evidence)
            if event.get("status") == "received":
                received_order.append(evidence)
    positions = {(e["invocation_index"], e["request_index"]): i
                 for i, e in enumerate(received_order, 1)}
    files = {p.relative_to(source_dir).as_posix(): p for p in (source_dir / "raw/details").glob("*.json")}
    # Include receipts whose body is missing. Absence on disk cannot restore
    # capacity or make an already logged successful retrieval disappear.
    refs = set(files) | {e["event"]["raw_response_ref"] for e in received_order}
    all_ordered = all(len([e for e in events_by_ref.get(ref, [])
                          if e["event"].get("status") == "received"]) == 1 for ref in refs)
    inventory = []
    ledger = {}
    for ref in sorted(refs):
        received = [e for e in events_by_ref.get(ref, []) if e["event"].get("status") == "received"]
        candidate_id = Path(ref).stem
        key = by_id.get(candidate_id)
        event_keys = {e["event"]["identity"] for e in received}
        mapping_valid = key is not None and (not event_keys or event_keys == {key})
        ordinal = positions[(received[0]["invocation_index"], received[0]["request_index"])] if all_ordered else None
        band = ("within_first_50" if ordinal <= 50 else "excess_after_50") if ordinal is not None else "order_uncertain"
        entry = {"record_id": candidate_id, "requested_key": key, "raw_response_ref": ref,
                 "raw_file_present": ref in files, "sha256": before.get(ref),
                 "request_evidence": received, "retrieval_ordinal": ordinal,
                 "allowance_band": band, "mapping_valid": mapping_valid}
        if not mapping_valid:
            entry["mapping_error"] = "Filename candidate and logged requested identity disagree or are unknown"
        inventory.append(entry)
        # Unknown mappings still consume capacity under a separate explicit key.
        ledger_key = key if mapping_valid else "unmapped_response:" + ref
        receipt = ledger.setdefault(ledger_key, {"status": "received", "raw_response_refs": [],
            "raw_response_ref": ref,
            "record_id": candidate_id, "retrieval_ordinal": ordinal, "allowance_band": band})
        receipt["raw_response_refs"].append(ref)

    output_dir.mkdir(parents=True)
    shutil.copytree(source_dir / "raw", output_dir / "raw")
    historical = output_dir / "historical"
    historical.mkdir()
    for name in ("resume_state.json", "run_manifest.json", "records.jsonl", "query_hits.jsonl", "errors.jsonl"):
        if (source_dir / name).exists():
            shutil.copy2(source_dir / name, historical / name)
    if (source_dir / "diagnostics").exists():
        shutil.copytree(source_dir / "diagnostics", historical / "diagnostics")

    for key, record in state["records"].items():
        record.update(detail_metadata=None, detail_response_ref=None, detail_parse_status="not_attempted",
                      detail_retrieval_status="not_received", identifier_conflicts=[])
        # Correct the observed title mapping using the actual saved search row.
        # All original search observations and the historical top-level projection
        # are retained; no title is invented from a publication association.
        for observation in record["search_observations"]:
            page = json.loads((source_dir / observation["raw_response_ref"]).read_bytes())
            row = page["datasets"][observation["page_position"] - 1]
            observation["metadata"] = row
        first = record["search_observations"][0]["metadata"] if record["search_observations"] else {}
        record["title_original"] = first.get("title", first.get("name"))
    for entry in inventory:
        if not entry["mapping_valid"]:
            continue
        key, ref = entry["requested_key"], entry["raw_response_ref"]
        record = state["records"][key]
        record["detail_allowance_band"] = entry["allowance_band"]
        record["detail_retrieval_ordinal"] = entry["retrieval_ordinal"]
        if entry["raw_file_present"]:
            entry["parse_status"] = normalize_detail(record, files[ref].read_bytes(), ref, key)
            if entry["parse_status"].startswith("parsed"):
                _reported_fields(record, record["detail_metadata"], ref)
        else:
            record.update(detail_retrieval_status="received", detail_status="retrieved",
                          detail_parse_status="unavailable", detail_parse_error="Saved response body missing")
            entry["parse_status"] = "unavailable"
        entry["identifier_conflicts"] = record["identifier_conflicts"]

    state["historical_config"] = copy.deepcopy(state["config"])
    state["config"].update(adapter_version=ADAPTER_VERSION, detail_attempt_limit=DETAIL_ATTEMPT_LIMIT)
    state.update(detail_retrievals=ledger, detail_attempt_counts=dict(attempts),
                 detail_allowance_used=len(ledger),
                 network_blocked_reason="Offline repair: further retrieval is not authorized; historical detail allowance exceeded.",
                 repair_source_directory=str(source_dir))
    state["completed_details"] = [key for key, record in state["records"].items()
                                  if record["detail_parse_status"].startswith("parsed")]
    state["pending_details"] = [key for key in state["records"] if key not in ledger]
    conflicts = [{"record_id": r["record_id"], **conflict}
                 for r in state["records"].values() for conflict in r["identifier_conflicts"]]
    bands = Counter(entry["allowance_band"] for entry in inventory)
    counts = {"candidates": len(state["records"]), "query_hits": len(state["query_hits"]),
              "saved_detail_responses": len(files),
              "distinct_requested_records_with_saved_responses": len({e["requested_key"] for e in inventory
                  if e["raw_file_present"] and e["mapping_valid"]}),
              "detail_allowance_used": len(ledger), "details_parsed": len(state["completed_details"]),
              "details_with_identity_conflicts": sum(bool(r["identifier_conflicts"]) for r in state["records"].values()),
              "parse_failures": sum(r["detail_parse_status"] == "failed" for r in state["records"].values()),
              "records_without_received_details": len(state["pending_details"]),
              "within_first_50": bands["within_first_50"], "excess_after_50": bands["excess_after_50"],
              "order_uncertain": bands["order_uncertain"],
              "unmapped_responses": sum(not e["mapping_valid"] for e in inventory)}
    manifest = {"artifact_type": "offline_repair", "adapter_version": ADAPTER_VERSION,
                "run_id": state["run_id"], "source_directory": str(source_dir),
                "repaired_at": utc_now(), "network_requests": 0, "counts": counts,
                "limits": state["limits"], "config": state["config"],
                "historical_invocations": state["invocations"],
                "historical_cap_violation": len(ledger) > state["limits"]["detail_cap"],
                "order_basis": "Sequential invocation/request-log positions of received responses; no file timestamp ordering",
                "order_uncertainty": None if all_ordered else "At least one response lacks a unique received event; ordinal bands withheld",
                "network_blocked_reason": state["network_blocked_reason"],
                "state_ref": "resume_state.json", "inventory_ref": "detail_inventory.jsonl",
                "source_hashes_ref": "source_hashes.json", "historical_errors_ref": "historical/errors.jsonl"}
    _json(output_dir / "resume_state.json", state)
    _jsonl(output_dir / "records.jsonl", state["records"].values())
    _jsonl(output_dir / "query_hits.jsonl", state["query_hits"])
    _jsonl(output_dir / "identifier_conflicts.jsonl", conflicts)
    _jsonl(output_dir / "detail_inventory.jsonl", sorted(inventory, key=lambda e: (e["retrieval_ordinal"] or 10**9, e["raw_response_ref"])))
    _jsonl(output_dir / "errors.jsonl", state["errors"])
    if _hashes(source_dir) != before:
        raise RuntimeError("Source files changed during repair; inspect before accepting outputs")
    if any(hashlib.sha256((output_dir / ref).read_bytes()).hexdigest() != digest
           for ref, digest in before.items() if ref.startswith("raw/")):
        raise RuntimeError("Copied raw response hash mismatch")
    manifest["source_files_unchanged"] = True
    manifest["raw_copies_byte_identical"] = True
    manifest["candidate_ids_unchanged"] = list(by_id) == [r["record_id"] for r in state["records"].values()]
    _json(output_dir / "source_hashes.json", before)
    _json(output_dir / "repair_manifest.json", manifest)
    return manifest


def main():
    """Run an explicitly offline repair into a required new output directory."""
    parser = argparse.ArgumentParser(description="Rebuild saved OmicsDI responses offline; no network")
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = repair_saved_run(args.source_dir, args.output_dir)
    print(json.dumps({"output_directory": str(args.output_dir.resolve()), "counts": result["counts"]}, indent=2))


if __name__ == "__main__":
    main()
