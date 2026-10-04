"""Bounded OmicsDI metadata evaluation with persistent continuation state.

Search and dataset-detail responses are retained verbatim. Repository plus native
ID defines identity; publication/accession associations never merge datasets.
State is authoritative and inspection files are regenerated from it. This module
does not classify experiments or follow returned links.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode

from deathmap_ai.omicsdi_queries import QUERIES, QUERY_STRATEGY_ID
from deathmap_ai.omicsdi_metadata import native_identity, normalize_detail

ADAPTER_VERSION = "2.0.0"
DETAIL_ATTEMPT_LIMIT = 2
BASE = "https://www.omicsdi.org/ws/dataset/"

# A child process bounds DNS, connection and body-read time together. Socket
# timeouts alone can exceed the run deadline on a slowly streaming response.
# Redirects are rejected so returned links cannot expand the metadata boundary.
_HTTP_WORKER = '''import sys, urllib.request
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
opener = urllib.request.build_opener(NoRedirect)
request = urllib.request.Request(sys.argv[1], headers={"Accept":"application/json", "User-Agent":"deathmap-ai/0.1 omicsdi-pilot"})
with opener.open(request, timeout=float(sys.argv[2])) as response:
    sys.stdout.buffer.write(response.read())
'''


def utc_now():
    """Return an explicit UTC retrieval timestamp."""
    return datetime.now(timezone.utc).isoformat()


def fetch_metadata(url, timeout):
    """Return original response bytes within a hard per-request time limit.

    Only URLs built for OmicsDI search or a repository/identifier detail pair
    are accepted. Network/HTTP/process failures raise RuntimeError or TimeoutExpired.
    """
    suffix = url.removeprefix(BASE)
    if not url.startswith(BASE) or not (
        suffix.startswith("search?query=") or
        (len(suffix.split("/")) == 2 and "?" not in suffix)
    ):
        raise ValueError("Only OmicsDI search and dataset detail endpoints are allowed")
    result = subprocess.run(
        [sys.executable, "-c", _HTTP_WORKER, url, str(timeout)],
        capture_output=True, timeout=timeout, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace")[-2000:])
    return result.stdout


def _write_json(path, value):
    """Replace a checkpoint atomically; incomplete writes cannot truncate it."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def _key(row):
    """Encode original repository/ID without delimiter collisions or normalization."""
    pair, _ = native_identity(row)
    return json.dumps(pair, ensure_ascii=False)


def _record(row, key, state, ref, timestamp):
    """Wrap source metadata without guessing absent scientific or identifier fields."""
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]
    repository, identifier = json.loads(key)
    return {
        "record_id": f"omicsdi-{state['run_id']}-{digest}",
        "run_id": state["run_id"], "resource_name": "OmicsDI", "resource_version": None,
        "retrieved_at": timestamp, "query_strategy_id": QUERY_STRATEGY_ID,
        "native_record_id": identifier, "repository_original": repository,
        "native_url": row.get("url"), "candidate_type": "dataset",
        "title_original": row.get("title", row.get("name")), "pmid_reported": row.get("pubmed"),
        "doi_reported": row.get("doi"), "accessions_reported": [identifier],
        "evidence_text_original": row.get("description"),
        "raw_response_ref": ref, "review_status": "unreviewed",
        "search_observations": [], "detail_metadata": None,
        "detail_response_ref": None, "detail_status": "pending",
        "detail_retrieval_status": "not_requested", "detail_parse_status": "not_attempted",
        "reported_field_observations": [],
    }


def _reported_fields(record, metadata, ref):
    """Retain explicitly named identifier fields with their response provenance.

    Cross-reference objects are preserved intact: an unfamiliar namespace is not
    guessed to be a dataset or publication. Conflicting values across search and
    detail are observations rather than an overwrite of the initial search fields.
    """
    fields = {name: metadata[name] for name in (
        "pubmed", "doi", "accessions", "crossReferences", "cross_references",
        "publications", "organisms", "taxonomy", "dates", "keywords",
    ) if name in metadata}
    record["reported_field_observations"].append({"raw_response_ref": ref, "fields": fields})


def reconcile_detail_receipts(state, run_dir):
    """Account for saved responses before any resume scheduling or cap check.

    Raw files recover a crash between response persistence and checkpointing.
    Receipts without a saved body still consume allowance; an in-flight request
    at interruption is uncertain and is never silently repeated. Unmapped files
    stop resume rather than letting incomplete accounting authorize more work.
    """
    ledger = state.setdefault("detail_retrievals", {})
    state.setdefault("detail_attempt_counts", {})
    state.setdefault("search_attempt_counts", {})
    by_id = {r["record_id"]: key for key, r in state["records"].items()}
    for path in (run_dir / "raw" / "details").glob("*.json"):
        if path.stem not in by_id:
            raise ValueError(f"Unmapped saved detail response prevents safe resume: {path.name}")
        key = by_id[path.stem]
        ref = path.relative_to(run_dir).as_posix()
        receipt = ledger.setdefault(key, {"raw_response_ref": ref, "recovered_from_saved_file": True})
        receipt["status"] = "received"
        normalize_detail(state["records"][key], path.read_bytes(), ref, key)
    for key, receipt in ledger.items():
        record = state["records"][key]
        if not (run_dir / receipt["raw_response_ref"]).exists():
            received = receipt["status"] == "received"
            record.update(detail_retrieval_status="received" if received else "unknown_after_interruption",
                          detail_status="retrieved" if received else "pending",
                          detail_parse_status="unavailable", detail_parse_error="Saved response body unavailable")
    state["completed_details"] = [key for key, record in state["records"].items()
                                  if record.get("detail_parse_status", "").startswith("parsed")]


def detail_allowance_used(state):
    """Count received responses plus unresolved reservations, independent of parsing."""
    return len(state["detail_retrievals"])


def run_pilot(run_dir: Path, *, resume=False, candidate_cap=None, detail_cap=None,
              budget_seconds=None, request_timeout=10, retries=1,
              fetch=fetch_metadata, clock=time.monotonic):
    """Run one bounded invocation and return its manifest.

    A new run admits at most 100 source/ID pairs and retrieves up to 50 details.
    Resume requires the same adapter/query/scheduling configuration. Explicit cap
    arguments may raise cumulative limits; omitted arguments retain saved limits.
    Detail transport attempts are capped separately at two per requested record
    cumulatively. Received bodies consume allowance even if parsing fails.
    The injected fetch/clock support deterministic fixture tests without networking.
    Writes UTF-8 state, native responses, records, hits, errors and invocation logs.
    """
    started = clock()
    if (budget_seconds is not None and budget_seconds < 15) or not 0 < request_timeout <= 30 or retries not in (0, 1):
        raise ValueError("Optional budget must be >=15 seconds, timeout <=30, retries 0 or 1")
    # Shared searches have no fixed total deadline. An explicit optional budget
    # still supports interrupted-run tests; request timeouts and caps always apply.
    deadline = float("inf") if budget_seconds is None else started + budget_seconds - 10
    config = {"adapter_version": ADAPTER_VERSION, "query_strategy_id": QUERY_STRATEGY_ID,
              "queries": QUERIES, "base_url": BASE, "page_size": 10,
              "scheduler": "query-cycle-search-page-then-one-detail-v1",
              "request_timeout": request_timeout, "retries": retries,
              "detail_attempt_limit": DETAIL_ATTEMPT_LIMIT}
    state_path = run_dir / "resume_state.json"
    if resume:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if state.get("network_blocked_reason"):
            raise ValueError(state["network_blocked_reason"])
        if state["config"] != config:
            raise ValueError("Incompatible resume configuration; legacy accounting requires an offline repair; queries, adapter and request settings must match")
        for name, value in (("candidate_cap", candidate_cap), ("detail_cap", detail_cap)):
            if value is not None:
                if value < state["limits"][name]:
                    raise ValueError("Resume caps cannot decrease; raising caps must be explicit")
                state["limits"][name] = value
    else:
        if run_dir.exists():
            raise ValueError("Run directory already exists; choose --resume explicitly")
        state = {"run_id": run_dir.name, "created_at": utc_now(), "config": config,
                 "limits": {"candidate_cap": 100 if candidate_cap is None else candidate_cap,
                            "detail_cap": 50 if detail_cap is None else detail_cap},
                 "queries": {qid: {"offset": 0, "buffer": [], "keys": [], "exhausted": False,
                                   "reported_total": None, "pages": []} for qid in QUERIES},
                 "records": {}, "query_hits": [], "errors": [], "completed_details": [],
                 "detail_retrievals": {}, "detail_attempt_counts": {},
                 "turn": 0, "invocations": []}
    if any(type(v) is not int or v < 0 for v in state["limits"].values()):
        raise ValueError("Caps must be nonnegative integers")
    if not resume and (state["limits"]["candidate_cap"] > 100 or state["limits"]["detail_cap"] > 50):
        raise ValueError("First-run caps cannot exceed 100 candidates or 50 details")
    (run_dir / "raw" / "details").mkdir(parents=True, exist_ok=True)
    reconcile_detail_receipts(state, run_dir)
    invocation = {"invocation_id": len(state["invocations"]) + 1, "started_at": utc_now(),
                  "budget_seconds": budget_seconds, "limits": dict(state["limits"]),
                  "requests": [], "stop_reasons": []}
    state["invocations"].append(invocation)
    attempted = set(state["detail_retrievals"]) | {
        key for key, count in state["detail_attempt_counts"].items() if count >= DETAIL_ATTEMPT_LIMIT}
    failed_queries = set()

    def checkpoint():
        state["admitted_record_keys"] = list(state["records"])
        state["pending_details"] = [k for k in state["records"] if k not in state["detail_retrievals"]]
        state["detail_allowance_used"] = detail_allowance_used(state)
        _write_json(state_path, state)

    def request(url, ref, kind, identity):
        path = run_dir / ref
        # A response persisted just before interruption can be reused even if
        # its admission checkpoint was not reached. Never overwrite native bytes.
        if path.exists():
            body = path.read_bytes()
            if kind == "detail":
                return body
            try:
                return json.loads(body)
            except (ValueError, UnicodeError) as exc:
                state["errors"].append({"raw_response_ref": ref, "error": str(exc), "stage": "parse"})
                return None
        for attempt in range(retries + 1):
            remaining = deadline - clock()
            if remaining <= 0.1:
                return None
            if kind == "search":
                attempt_key = identity + ":" + ref
                if state["search_attempt_counts"].get(attempt_key, 0) >= 2:
                    return None
                state["search_attempt_counts"][attempt_key] = state["search_attempt_counts"].get(attempt_key, 0) + 1
            if kind == "detail":
                if identity in state["detail_retrievals"] or detail_allowance_used(state) >= state["limits"]["detail_cap"]:
                    return None
                count = state["detail_attempt_counts"].get(identity, 0)
                if count >= DETAIL_ATTEMPT_LIMIT:
                    return None
                state["detail_attempt_counts"][identity] = count + 1
                # Reserve before networking. An interrupted request has unknown
                # completion and must not free capacity or be repeated on resume.
                state["detail_retrievals"][identity] = {"status": "in_flight",
                    "raw_response_ref": ref, "invocation_id": invocation["invocation_id"]}
            event = {"url": url, "kind": kind, "identity": identity,
                     "attempt": attempt + 1, "retrieved_at": utc_now(), "raw_response_ref": ref}
            invocation["requests"].append(event)
            checkpoint()
            try:
                body = fetch(url, min(request_timeout, remaining))
            except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
                if kind == "detail":
                    del state["detail_retrievals"][identity]
                event["status"] = "failed"
                state["errors"].append({**event, "error": str(exc), "invocation_id": invocation["invocation_id"]})
                checkpoint()
                continue
            event["status"] = "received"
            if kind == "detail":
                state["detail_retrievals"][identity].update(status="received", retrieved_at=utc_now())
            # Persist receipt independently of raw storage and parsing. A JSON
            # error (or disk error) cannot turn a completed request into a retry.
            checkpoint()
            temporary = path.with_suffix(".json.tmp")
            temporary.write_bytes(body)
            temporary.replace(path)
            if kind == "detail":
                return body
            try:
                return json.loads(body)
            except (ValueError, UnicodeError) as exc:
                state["errors"].append({**event, "error": str(exc), "stage": "parse"})
                return None
        return None

    def admit(qid):
        query = state["queries"][qid]
        while query["buffer"]:
            entry = query["buffer"][0]
            row = entry["metadata"]
            try:
                key = _key(row)
            except ValueError as exc:
                # Unidentifiable entries remain in the full native page and an
                # explicit error record; no fabricated native key is admitted.
                state["errors"].append({"query_id": qid, **entry, "error": str(exc)})
                query["buffer"].pop(0)
                continue
            if key not in state["records"]:
                if len(state["records"]) >= state["limits"]["candidate_cap"]:
                    break
                state["records"][key] = _record(row, key, state, entry["raw_response_ref"], entry["retrieved_at"])
            record = state["records"][key]
            hit = {k: v for k, v in entry.items() if k != "metadata"}
            hit.update(query_id=qid, record_id=record["record_id"],
                       intended_query=QUERIES[qid], submitted_query=QUERIES[qid])
            state["query_hits"].append(hit)
            record["search_observations"].append({**hit, "metadata": row})
            _reported_fields(record, row, entry["raw_response_ref"])
            if key not in query["keys"]:
                query["keys"].append(key)
            query["buffer"].pop(0)

    checkpoint()
    # Consume all buffered pages before making any new network requests.
    for qid in QUERIES:
        admit(qid)
    idle = 0
    while clock() < deadline and idle < len(QUERIES):
        qid = list(QUERIES)[state["turn"] % len(QUERIES)]
        state["turn"] += 1
        query = state["queries"][qid]
        progress = False
        detail_available = detail_allowance_used(state) < state["limits"]["detail_cap"]
        pending = next((key for key in query["keys"] if key not in attempted), None)
        if (not query["buffer"] and not query["exhausted"] and qid not in failed_queries
                and len(state["records"]) < state["limits"]["candidate_cap"]
                and (pending is None or not detail_available)):
            offset = query["offset"]
            ref = f"raw/search_{qid}_page_{offset}.json"
            url = BASE + "search?" + urlencode({"query": QUERIES[qid], "start": offset, "size": 10})
            payload = request(url, ref, "search", qid)
            progress = True
            if not isinstance(payload, dict) or not isinstance(payload.get("datasets"), list) or not all(isinstance(r, dict) for r in payload.get("datasets", [])):
                failed_queries.add(qid)
                if payload is not None:
                    state["errors"].append({"query_id": qid, "raw_response_ref": ref, "error": "Unexpected search envelope; not an empty result"})
            else:
                rows = payload["datasets"]
                query["reported_total"] = payload.get("count")
                query["pages"].append(ref)
                query["offset"] += len(rows)
                total = payload.get("count")
                query["exhausted"] = not rows or (isinstance(total, int) and query["offset"] >= total)
                query["buffer"] = [{"metadata": row, "page_offset": offset, "page_position": i,
                                    "result_position": offset + i, "native_rank": row.get("rank"),
                                    "retrieved_at": utc_now(), "raw_response_ref": ref}
                                   for i, row in enumerate(rows, 1)]
                admit(qid)
        pending = next((key for key in query["keys"] if key not in attempted), None)
        if detail_available and pending is not None and clock() < deadline:
            record = state["records"][pending]
            attempted.add(pending)
            repository, identifier = json.loads(pending)
            url = BASE + quote(repository, safe="") + "/" + quote(identifier, safe="")
            ref = f"raw/details/{record['record_id']}.json"
            payload = request(url, ref, "detail", pending)
            progress = True
            if payload is not None:
                status = normalize_detail(record, payload, ref, pending)
                record["detail_retrieved_at"] = state["detail_retrievals"][pending].get("retrieved_at")
                if status.startswith("parsed"):
                    _reported_fields(record, record["detail_metadata"], ref)
                    state["completed_details"].append(pending)
                else:
                    state["errors"].append({"record_id": record["record_id"], "raw_response_ref": ref,
                        "error": record["detail_parse_error"], "stage": "parse"})
            else:
                record["detail_status"] = "failed" if clock() < deadline else "pending"
                record["detail_retrieval_status"] = record["detail_status"]
        idle = 0 if progress else idle + 1
        checkpoint()

    reasons = invocation["stop_reasons"]
    if clock() >= deadline:
        reasons.append("network_deadline")
    if len(state["records"]) >= state["limits"]["candidate_cap"]:
        reasons.append("candidate_cap")
    if detail_allowance_used(state) >= state["limits"]["detail_cap"]:
        reasons.append("detail_cap")
    if failed_queries or any(r["detail_status"] == "failed" for r in state["records"].values()):
        reasons.append("request_failures")
    if all(q["exhausted"] and not q["buffer"] for q in state["queries"].values()):
        reasons.append("search_results_exhausted")
    if not reasons:
        reasons.append("no_work_available_this_invocation")
    invocation["finished_at"] = utc_now()
    invocation["elapsed_seconds"] = round(clock() - started, 3)
    checkpoint()
    for name, rows in (("records", state["records"].values()), ("query_hits", state["query_hits"]), ("errors", state["errors"])):
        (run_dir / f"{name}.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    manifest = {"run_id": state["run_id"], "resource_name": "OmicsDI", "resource_version": None,
                "api_version": None, "api_documentation_version_claim": "Version 1; unversioned /ws/ URL",
                "tool_version": "deathmap-ai 0.1.0", "python_version": platform.python_version(),
                "config": config, "limits": state["limits"], "created_at": state["created_at"],
                "queries": {qid: {"intended_query": QUERIES[qid], "submitted_query": QUERIES[qid],
                                   **{k: v for k, v in q.items() if k not in ("keys", "buffer")},
                                   "buffered_entries": len(q["buffer"])} for qid, q in state["queries"].items()},
                "counts": {"unique_candidates": len(state["records"]),
                           "successful_details": sum(r["status"] == "received" for r in state["detail_retrievals"].values()),
                           "details_parsed": len(state["completed_details"]),
                           "detail_retrievals_received": sum(r["status"] == "received" for r in state["detail_retrievals"].values()),
                           "detail_allowance_used": detail_allowance_used(state),
                           "detail_parse_failures": sum(r.get("detail_parse_status") == "failed" for r in state["records"].values()),
                           "query_hits": len(state["query_hits"]), "errors": len(state["errors"]),
                           "pending_details": len(state["pending_details"])},
                "search_complete": all(q["exhausted"] and not q["buffer"] for q in state["queries"].values()),
                "stop_reasons": reasons, "state_ref": "resume_state.json", "invocations": state["invocations"]}
    _write_json(run_dir / "run_manifest.json", manifest)
    invocation["elapsed_seconds"] = round(clock() - started, 3)
    checkpoint()
    _write_json(run_dir / "run_manifest.json", manifest)
    return manifest
