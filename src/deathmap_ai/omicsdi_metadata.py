"""Map observed OmicsDI metadata without replacing requested dataset identity.

Saved search rows use source/id/title; detail objects use database/accession/name.
Both original pairs survive. Repository spelling differences are explicit
conflicts, not an inferred alias map or grounds for merging candidate records.
"""

import json


def native_identity(metadata):
    """Return a source/ID pair and its original field observations.

    Supports the two complete pairs observed in saved OmicsDI metadata. Raises
    ValueError for absent/incomplete identifiers or conflicting paired fields.
    Field values are never stripped, case-folded, or otherwise normalized.
    """
    if not isinstance(metadata, dict):
        raise ValueError("Metadata is not an object")
    pairs = []
    for repo_field, id_field in (("source", "id"), ("database", "accession")):
        if repo_field in metadata or id_field in metadata:
            values = [metadata.get(repo_field), metadata.get(id_field)]
            if not all(isinstance(value, str) and value for value in values):
                raise ValueError(f"Incomplete or invalid {repo_field}/{id_field} pair")
            pairs.append({"fields": [repo_field, id_field], "values": values})
    if not pairs:
        raise ValueError("Metadata lacks source/id or database/accession")
    if any(pair["values"] != pairs[0]["values"] for pair in pairs):
        raise ValueError("Conflicting source/id and database/accession pairs")
    return pairs[0]["values"], pairs


def normalize_detail(record, body, ref, requested_key):
    """Attach a retrieved response to its requested record, without changing its ID.

    JSON/schema failures are parsing outcomes, never retrieval failures. Complete
    JSON metadata and original identifier fields survive even when inconsistent.
    A parsed response with a different returned pair stays attached by *request
    provenance*, with an explicit conflict; it is not asserted to be that dataset.
    Returns the parsing status. This function performs no I/O or network access.
    """
    requested = json.loads(requested_key)
    record.update(detail_response_ref=ref, detail_retrieval_status="received",
                  detail_status="retrieved", detail_parse_status="failed",
                  detail_parse_error=None, detail_metadata=None,
                  detail_fields_original=None,
                  detail_identity_observations=None, identifier_conflicts=[])
    try:
        metadata = json.loads(body)
        record["detail_metadata"] = metadata
        if isinstance(metadata, dict):
            fields = {key: metadata[key] for key in ("source", "id", "database", "accession") if key in metadata}
            record["detail_identity_observations"] = {"requested_pair": requested,
                                                      "returned_fields": fields}
        returned, pairs = native_identity(metadata)
        record["detail_identity_observations"]["returned_pairs"] = pairs
    except (ValueError, UnicodeError) as error:
        record["detail_parse_error"] = str(error)
        if record["detail_identity_observations"] is not None:
            record["identifier_conflicts"].append({"kind": "invalid_or_conflicting_identifier_fields",
                "requested_pair": requested, "returned_fields": fields, "raw_response_ref": ref,
                "explanation": str(error)})
        return "failed"
    if returned != requested:
        record["identifier_conflicts"].append({"kind": "requested_returned_pair_difference",
            "requested_pair": requested, "returned_pair": returned, "raw_response_ref": ref})
    record["detail_parse_status"] = "parsed_with_identity_conflict" if returned != requested else "parsed"
    # Keep detail projections separate from the first search observation. A
    # conflicting response may be inspected, but must not overwrite intake facts.
    record["detail_fields_original"] = {"title": metadata.get("name", metadata.get("title")),
        "description": metadata.get("description"), "cross_references": metadata.get("cross_references"),
        "dates": metadata.get("dates"), "additional": metadata.get("additional")}
    return record["detail_parse_status"]
