"""Stage and verify the shared-search cache migration, without deleting sources.

Every legacy metadata file keeps its bytes and a hash-addressed inventory entry.
Generated workbooks are decoded to JSON (including all OOXML parts) so reviewer
values, formulas, links and annotations survive cleanup. ICRAFT is never opened.
Deletion is a separate, explicitly inventoried PowerShell operation after exports
and regeneration have passed verification.
"""

import argparse
import base64
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

SCHEMA = "deathmap-resource-archive-v1"


def write_json(path, value):
    """Write deterministic, indented UTF-8 JSON without a spreadsheet dependency."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive_workbook(path, output):
    """Extract every cell and ZIP member to JSON; never modify or execute a workbook.

    XML parts remain verbatim UTF-8 strings; non-UTF-8 members use base64. ZIP
    compression/container timestamps are not preserved, but each member's bytes
    and hash are, allowing content reconstruction. Reviewer authorship cannot be
    inferred from XLSX alone, so all populated values are retained, not just cells
    guessed to be manual edits.
    """
    import zipfile
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as book:
        parts = {}
        for name in book.namelist():
            body = book.read(name)
            try:
                value, encoding = body.decode("utf-8"), "utf-8"
            except UnicodeDecodeError:
                value, encoding = base64.b64encode(body).decode(), "base64"
            parts[name] = {"encoding": encoding, "content": value, "sha256": hashlib.sha256(body).hexdigest()}
        strings = []
        if "xl/sharedStrings.xml" in parts:
            strings = ["".join(x.itertext()) for x in ET.fromstring(book.read("xl/sharedStrings.xml")).findall("s:si", ns)]
        cells = {}
        for name in book.namelist():
            if not name.startswith("xl/worksheets/sheet") or not name.endswith(".xml"):
                continue
            rows = []
            for cell in ET.fromstring(book.read(name)).findall(".//s:sheetData/s:row/s:c", ns):
                value = cell.findtext("s:v", default=None, namespaces=ns)
                if cell.get("t") == "s" and value is not None:
                    value = strings[int(value)]
                elif cell.get("t") == "inlineStr":
                    value = "".join(cell.find("s:is", ns).itertext())
                formula = cell.findtext("s:f", default=None, namespaces=ns)
                if value is not None or formula is not None:
                    rows.append({"cell": cell.get("r"), "native_type": cell.get("t"), "value": value, "formula": formula})
            cells[name] = rows
        result = {"schema_version": SCHEMA, "original_file": str(path), "original_sha256": digest(path),
                  "transformation": "ZIP members decoded losslessly; cell values/formulas additionally projected; no evaluation",
                  "review_authorship": "Unknown; all values, comments and other OOXML parts retained",
                  "cells": cells, "ooxml_parts": parts}
        write_json(output, result)
        saved = json.loads(output.read_text(encoding="utf-8"))
        for name, part in saved["ooxml_parts"].items():
            body = part["content"].encode() if part["encoding"] == "utf-8" else base64.b64decode(part["content"])
            if body != book.read(name):
                raise ValueError(f"Workbook archive content mismatch: {name}")
    return {"old_path": str(path), "new_path": str(output), "sha256": result["original_sha256"],
            "archive_sha256": digest(output), "cells": sum(map(len, cells.values())), "members_verified": len(parts),
            "recoverability": "All original uncompressed ZIP member bytes in JSON; original ZIP container not retained"}


def review_values(archive_path):
    """Return populated reviewer columns with row context from archived cells.

    Header names identify review fields, not who edited them. All cells and OOXML
    remain in the main archive; this projection only makes possible manual values
    easier to locate and does not apply them as scientific adjudication.
    """
    import re
    book = json.loads(archive_path.read_text(encoding="utf-8"))
    entries = []
    for sheet, cells in book["cells"].items():
        headings = {re.sub(r"\d", "", c["cell"]): c["value"] for c in cells
                    if re.sub(r"\D", "", c["cell"]) == "1" and isinstance(c["value"], str)}
        columns = {col: name for col, name in headings.items()
                   if "review" in name.casefold() or name == "library_scope_evidence"}
        for cell in cells:
            col, row = re.sub(r"\d", "", cell["cell"]), re.sub(r"\D", "", cell["cell"])
            if row != "1" and col in columns and cell["value"] not in (None, ""):
                context = {headings.get(re.sub(r"\d", "", c["cell"]), c["cell"]): c["value"]
                           for c in cells if re.sub(r"\D", "", c["cell"]) == row}
                entries.append({"sheet_part": sheet, "cell": cell["cell"], "field": columns[col],
                                "value": cell["value"], "row_context": context})
    return {"schema_version": SCHEMA, "source_archive": str(archive_path), "review_authorship": "unknown",
            "values": entries}


def stage(root):
    """Copy all data/raw metadata to per-package caches and inventory exact cleanup.

    Existing identical copies are reusable; a differing destination raises. No
    credentials or ICRAFT contents are read. Generated Excel sources are archived
    as JSON before their deletion can be approved by the separate verify step.
    """
    root = root.resolve()
    raw = root / "data/raw"
    inventory_path = root / "outputs/migration_inventory.json"
    if inventory_path.exists():
        verify(root)
        return json.loads(inventory_path.read_text(encoding="utf-8"))
    unexpected = [p.name for p in raw.iterdir() if p.name not in ("omicsdi", "orcs", ".gitkeep")]
    if unexpected:
        raise ValueError(f"Uninventoried raw sources: {unexpected}")
    inventory = {"schema_version": SCHEMA, "repository": str(root), "raw_directory": str(raw),
                 "files": [], "workbooks": [], "deletions": [str(raw)], "deletion_status": "staged_not_deleted"}
    for package in ("omicsdi", "orcs"):
        archive = {"schema_version": SCHEMA, "package": package, "historical_paths_remain_historical": True,
                   "serialization": "No native metadata byte transformations", "files": [], "historical_runs": []}
        for src in sorted((raw / package).rglob("*")):
            if not src.is_file():
                continue
            target = root / "outputs" / package / "cache/legacy" / src.relative_to(raw / package)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and digest(src) != digest(target):
                raise ValueError(f"Conflicting cache destination: {target}")
            if not target.exists():
                shutil.copy2(src, target)
            entry = {"old_path": src.relative_to(root).as_posix(), "new_path": target.relative_to(root).as_posix(),
                     "sha256": digest(src), "size": src.stat().st_size, "verified": digest(src) == digest(target)}
            archive["files"].append(entry)
            inventory["files"].append(entry)
            if src.name in ("summary.json", "run_manifest.json", "repair_manifest.json", "run-context.json"):
                data = json.loads(src.read_text(encoding="utf-8"))
                archive["historical_runs"].append({"source_ref": entry["new_path"], "old_ref": entry["old_path"],
                    "context": {k: v for k, v in data.items() if k in (
                        "run_id", "query_strategy_id", "retrieved_at", "created_at", "config", "counts",
                        "query_text", "queries", "limits", "stop_reasons", "invocations", "screens_retrieved",
                        "candidate_records", "export_rows", "historical_cap_violation", "elapsed_seconds")}})
        groups = defaultdict(list)
        for entry in archive["files"]:
            groups[entry["sha256"]].append(entry["new_path"])
        archive["identical_copy_groups"] = [v for v in groups.values() if len(v) > 1]
        archive["deduplication"] = "Identical bytes verified; cache paths retained for direct historical reprocessing"
        write_json(root / "outputs" / package / "archive.json", archive)
    keep = raw / ".gitkeep"
    if keep.exists():
        target = root / "outputs/orcs/cache/legacy/raw-root.gitkeep"
        shutil.copy2(keep, target)
        inventory["files"].append({"old_path": "data/raw/.gitkeep", "new_path": target.relative_to(root).as_posix(),
                                   "sha256": digest(keep), "verified": True})
    folder = root / "outputs/01a0690b-243f-73e0-98f2-8404aab1b9c8"
    for package in ("orcs",):
        workbook = folder / f"{package}-pilot-results.xlsx"
        if workbook.exists():
            target = root / "outputs" / package / "cache/legacy-excel" / f"{package}-pilot-results.workbook.json"
            item = archive_workbook(workbook, target)
            inventory["workbooks"].append(item)
            inventory["deletions"].append(str(workbook))
            archive_path = root / "outputs" / package / "archive.json"
            archive = json.loads(archive_path.read_text(encoding="utf-8"))
            archive["workbook_archive"] = item
            write_json(archive_path, archive)
    inventory["icraft_reference_names"] = sorted(p.name for p in (root / "data/icraft").glob("*.xlsx"))
    write_json(inventory_path, inventory)
    verify(root)
    return inventory


def verify(root):
    """Verify staged bytes and workbook JSON archives before or after cleanup."""
    root = root.resolve()
    inventory = json.loads((root / "outputs/migration_inventory.json").read_text(encoding="utf-8"))
    for entry in inventory["files"]:
        if digest(root / entry["new_path"]) != entry["sha256"]:
            raise ValueError(f"Archive hash mismatch: {entry['new_path']}")
        old = root / entry["old_path"]
        if old.exists() and digest(old) != entry["sha256"]:
            raise ValueError(f"Original changed after inventory: {entry['old_path']}")
    for item in inventory["workbooks"]:
        if digest(Path(item["new_path"])) != item["archive_sha256"]:
            raise ValueError("Workbook JSON archive changed")
        if Path(item["old_path"]).exists() and digest(Path(item["old_path"])) != item["sha256"]:
            raise ValueError("Original workbook changed after review-value archival")
    raw = root / "data/raw"
    if raw.exists():
        actual = {p.relative_to(root).as_posix() for p in raw.rglob("*") if p.is_file()}
        expected = {e["old_path"] for e in inventory["files"] if e["old_path"].startswith("data/raw/")}
        if actual != expected:
            raise ValueError("Raw directory inventory changed; cleanup is not safe")
    if sorted(p.name for p in (root / "data/icraft").glob("*.xlsx")) != inventory["icraft_reference_names"]:
        raise ValueError("ICRAFT reference inventory changed")
    return {"files_verified": len(inventory["files"]), "workbooks_verified": len(inventory["workbooks"]),
            "icraft_files_not_opened": len(inventory["icraft_reference_names"])}


def main():
    parser = argparse.ArgumentParser(description="Stage/verify shared-resource migration; no deletion")
    parser.add_argument("action", choices=["stage", "verify"])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result = stage(args.root) if args.action == "stage" else verify(args.root)
    print(json.dumps({k: v for k, v in result.items() if k not in ("files", "excel_temporary_files")}, indent=2))


if __name__ == "__main__":
    main()
