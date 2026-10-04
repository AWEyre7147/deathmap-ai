"""Offline shared-search, provenance and archival regressions; no credentials used."""

import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from deathmap_ai.resource_migration import archive_workbook, review_values, stage, verify, write_json
from deathmap_ai.shared_search import SEARCH_ID, export_package, match_orcs


class SharedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_orcs_native_evidence_siblings_and_nulls(self):
        rows = [
            {"SCREEN_ID": "1", "SOURCE_ID": "P1", "SOURCE_TYPE": "pubmed", "NOTES": "CRISPR in cancer with T cells"},
            {"SCREEN_ID": "2", "SOURCE_ID": "P1", "SOURCE_TYPE": "pubmed", "NOTES": "baseline control"},
            {"SCREEN_ID": "3", "SOURCE_ID": "P2", "SOURCE_TYPE": "pubmed", "NOTES": "utility text"},
        ]
        cache = self.root / "outputs/orcs/cache/legacy/20260904T213941Z"
        write_json(cache / "orcs-screens.raw.json", rows)
        write_json(cache / "summary.json", {"screens_retrieved": 3, "retrieved_at": "original-date"})
        result = export_package(self.root, "orcs")
        self.assertEqual(result["counts"]["source_records"], 3)
        self.assertEqual(result["counts"]["candidates"], 2)
        self.assertEqual(result["sibling_context_candidates"], 1)
        folder = self.root / "outputs/orcs" / SEARCH_ID
        candidates = json.loads((folder / "candidates.json").read_text())["candidates"]
        self.assertIsNone(candidates[0]["title"])
        self.assertEqual(candidates[1]["inclusion_basis"], "publication_sibling_context")
        hit = json.loads((folder / "query_hits.json").read_text())["hits"][0]
        self.assertEqual(hit["source_text"], rows[0]["NOTES"])
        self.assertEqual(hit["source_field_path"], "NOTES")
        self.assertEqual(hit["provenance"]["retrieved_at"], "original-date")
        with patch("subprocess.run", side_effect=AssertionError("offline only")):
            export_package(self.root, "orcs", verify=True)
        with self.assertRaisesRegex(ValueError, "exists"):
            export_package(self.root, "orcs")

    def test_orcs_literal_matching_does_not_match_til_inside_utility(self):
        self.assertFalse(match_orcs({"text": "utility vector"}))
        self.assertTrue(match_orcs({"text": "TIL coculture"}))

    def test_migration_hashes_and_icraft_names_only(self):
        for package in ("orcs", "omicsdi"):
            write_json(self.root / "data/raw" / package / "run/metadata.json", {"native": "unchanged"})
        keep = self.root / "data/icraft"
        keep.mkdir()
        for i in range(5):
            (keep / f"reference{i}.xlsx").write_bytes(b"do not open")
        inventory = stage(self.root)
        self.assertEqual(verify(self.root)["icraft_files_not_opened"], 5)
        for entry in inventory["files"]:
            self.assertEqual((self.root / entry["old_path"]).read_bytes(), (self.root / entry["new_path"]).read_bytes())
        self.assertTrue((self.root / "data/raw").exists())

    def test_workbook_reviewer_values_and_every_part_survive_json_archival(self):
        path = self.root / "fixture.zip"
        xml = '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>reviewer_notes</t></is></c></row><row r="2"><c r="A2" t="inlineStr"><is><t>Keep this manual note</t></is></c></row></sheetData></worksheet>'
        with zipfile.ZipFile(path, "w") as book:
            book.writestr("xl/worksheets/sheet1.xml", xml)
            book.writestr("binary.bin", b'\x00\xff')
        output = self.root / "workbook.json"
        result = archive_workbook(path, output)
        self.assertEqual(result["members_verified"], 2)
        self.assertEqual(review_values(output)["values"][0]["value"], "Keep this manual note")


if __name__ == "__main__":
    unittest.main()
