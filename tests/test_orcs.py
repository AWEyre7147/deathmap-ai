"""Small, inspectable tests for metadata matching and provenance behavior."""

from __future__ import annotations

import tempfile
import unittest
import csv
from pathlib import Path

from deathmap_ai.orcs import (
    _fetch_json,
    _records_from_payload,
    _write_screen_metadata_csv,
    build_candidate_records,
    build_discovery_record,
    load_access_key,
    match_candidate_rules,
    _write_review_sample,
)
from unittest.mock import patch
from urllib.error import HTTPError, URLError


class AccessKeyTests(unittest.TestCase):
    def test_key_file_accepts_one_32_character_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "key.txt"
            path.write_text("A" * 32 + "\n", encoding="utf-8")
            self.assertEqual(load_access_key(path), "A" * 32)

    def test_invalid_key_error_does_not_echo_secret(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "key.txt"
            path.write_text("sensitive-but-invalid", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "32-character") as raised:
                load_access_key(path)
            self.assertNotIn("sensitive-but-invalid", str(raised.exception))


class PayloadTests(unittest.TestCase):
    def test_list_and_enveloped_screen_payloads_are_supported(self) -> None:
        expected = [{"SCREEN_ID": 1}]
        self.assertEqual(_records_from_payload(expected), expected)
        self.assertEqual(_records_from_payload({"screens": expected}), expected)


class NetworkSafetyTests(unittest.TestCase):
    @patch("deathmap_ai.orcs.urlopen")
    def test_http_errors_do_not_expose_secret_url(self, mocked_open) -> None:
        mocked_open.side_effect = HTTPError(
            "https://example.test/?accesskey=SECRET", 401, "Unauthorized", {}, None
        )
        with self.assertRaisesRegex(RuntimeError, "HTTP status 401") as raised:
            _fetch_json("screens/", "A" * 32, {}, 5)
        self.assertNotIn("accesskey", str(raised.exception))
        self.assertNotIn("SECRET", str(raised.exception))

    @patch("deathmap_ai.orcs.urlopen")
    def test_connection_errors_use_a_safe_message(self, mocked_open) -> None:
        mocked_open.side_effect = URLError("secret-bearing diagnostic")
        with self.assertRaisesRegex(RuntimeError, "service was unreachable") as raised:
            _fetch_json("screens/", "A" * 32, {}, 5)
        self.assertNotIn("secret-bearing", str(raised.exception))


class CandidateRuleTests(unittest.TestCase):
    def test_spelling_variants_remain_distinguishable(self) -> None:
        record = {
            "SCREEN_NAME": "Tumor co-culture screen",
            "NOTES": "A separate coculture validation used T cells.",
        }
        rules = {match["rule"] for match in match_candidate_rules(record)}
        self.assertIn("co-culture", rules)
        self.assertIn("coculture", rules)
        self.assertIn("t-cell", rules)

    def test_discovery_record_preserves_native_metadata(self) -> None:
        native = {
            "SCREEN_ID": 17,
            "SCREEN_NAME": "Cancer cell coculture with CAR-T cells",
            "PUBMED_ID": "12345678",
            "PHENOTYPE": "Resistance to immune-mediated killing",
        }
        converted = build_discovery_record(
            native,
            run_id="test-run",
            retrieved_at="2026-09-04T00:00:00+00:00",
            raw_response_ref="data/raw/orcs/test/orcs-screens.raw.json",
        )
        self.assertIsNotNone(converted)
        assert converted is not None
        self.assertEqual(converted["native_record_id"], 17)
        self.assertIsNone(converted["pmid_reported"])
        self.assertEqual(converted["screen_name_reported"], "Cancer cell coculture with CAR-T cells")
        self.assertEqual(converted["source_metadata"], native)
        self.assertEqual(converted["review_status"], "unreviewed")

    def test_source_supplied_enzyme_and_library_fields_remain_visible(self) -> None:
        native = {
            "SCREEN_ID": 21,
            "SCREEN_NAME": "Targeted tumor co-culture screen",
            "LIBRARY": "Immune Target Library",
            "LIBRARY_TYPE": "CRISPRn",
            "FULL_SIZE": "248",
            "METHODOLOGY": "Knockout",
            "ENZYME": "Cas9",
        }
        converted = build_discovery_record(native, "test-run", "2026-09-04", "raw.json")
        assert converted is not None
        self.assertEqual(converted["library_name_reported"], "Immune Target Library")
        self.assertEqual(converted["library_size_reported"], "248")
        self.assertEqual(converted["enzyme_reported"], "Cas9")

    def test_exact_coculture_anchor_adds_sibling_screen_as_context(self) -> None:
        native_records = [
            {
                "SCREEN_ID": "1910",
                "SCREEN_NAME": "Control screen",
                "SOURCE_TYPE": "pubmed",
                "SOURCE_ID": "33649592",
            },
            {
                "SCREEN_ID": "1912",
                "SCREEN_NAME": "TIL co-culture screen",
                "SOURCE_TYPE": "pubmed",
                "SOURCE_ID": "33649592",
            },
        ]
        records, direct, context = build_candidate_records(
            native_records, "test-run", "2026-09-04", "raw.json"
        )
        self.assertEqual([record["native_record_id"] for record in records], ["1910", "1912"])
        self.assertEqual(len(direct), 1)
        self.assertEqual(len(context), 1)
        self.assertEqual(context[0]["inclusion_basis"], "publication_sibling_context")
        self.assertEqual(context[0]["anchor_screen_ids"], ["1912"])

    def test_typed_source_id_becomes_reported_pmid(self) -> None:
        native = {
            "SCREEN_ID": 19,
            "SCREEN_NAME": "Tumor co-culture screen",
            "SOURCE_TYPE": "pubmed",
            "SOURCE_ID": "12345678",
        }
        converted = build_discovery_record(native, "test-run", "2026-09-04T00:00:00+00:00", "raw.json")
        assert converted is not None
        self.assertEqual(converted["pmid_reported"], "12345678")
        self.assertIsNone(converted["title_original"])

    def test_nonmatching_record_is_not_promoted_to_candidate(self) -> None:
        native = {"SCREEN_ID": 18, "SCREEN_NAME": "Drug resistance screen"}
        self.assertIsNone(
            build_discovery_record(native, "test-run", "2026-09-04T00:00:00+00:00", "raw.json")
        )

    def test_review_sample_labels_screen_name_as_screen_name(self) -> None:
        native = {
            "SCREEN_ID": 20,
            "SCREEN_NAME": "Tumor co-culture screen",
            "SOURCE_TYPE": "pubmed",
            "SOURCE_ID": "12345678",
        }
        converted = build_discovery_record(native, "test-run", "2026-09-04T00:00:00+00:00", "raw.json")
        assert converted is not None
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "review.csv"
            _write_review_sample(path, [converted], 10)
            with path.open(encoding="utf-8-sig", newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row["screen_name_reported"], "Tumor co-culture screen")
            self.assertNotIn("title_original", row)
            self.assertEqual(row["library_scope_reviewed"], "")
            self.assertEqual(row["screen_evidence_role_reviewed"], "")

    def test_screen_metadata_csv_preserves_native_headings(self) -> None:
        native = [{"SCREEN_ID": "1912", "ENZYME": "Cas9", "NESTED": ["a", "b"]}]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "screen-metadata.csv"
            _write_screen_metadata_csv(path, native)
            with path.open(encoding="utf-8-sig", newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row["SCREEN_ID"], "1912")
            self.assertEqual(row["ENZYME"], "Cas9")
            self.assertEqual(row["NESTED"], '["a", "b"]')


if __name__ == "__main__":
    unittest.main()
