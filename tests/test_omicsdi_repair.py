"""Offline regressions for the observed schema and receipt-based detail limit.

Observed-shape fixtures retain selected fields and provenance from the saved
pilot; malformed payloads and conflict mutations are deliberately synthetic.
All transports below are local fakes. No live metadata requests are made.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from deathmap_ai.omicsdi import run_pilot
from deathmap_ai.omicsdi_metadata import native_identity, normalize_detail
from deathmap_ai.omicsdi_repair import repair_saved_run

EXAMPLES = json.loads((Path(__file__).parent / "fixtures/omicsdi-observed-shapes.json").read_text(encoding="utf-8"))


class RepairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "run"
        self.calls = []

    def service(self, url, timeout):
        self.calls.append(url)
        if "search?" in url:
            return json.dumps({"count": 3, "datasets": [e["search"] for e in EXAMPLES]}).encode()
        identifier = url.rsplit("/", 1)[1]
        return json.dumps(next(e["detail"] for e in EXAMPLES if e["search"]["id"] == identifier)).encode()

    def state(self):
        return json.loads((self.path / "resume_state.json").read_text(encoding="utf-8"))

    def test_observed_identifier_fields_and_explicit_label_conflicts(self):
        result = run_pilot(self.path, fetch=self.service)
        self.assertEqual(result["counts"]["detail_retrievals_received"], 3)
        self.assertEqual(result["counts"]["details_parsed"], 3)
        records = list(self.state()["records"].values())
        for record, example in zip(records, EXAMPLES):
            self.assertEqual(record["title_original"], example["search"]["title"])
            self.assertEqual(record["native_record_id"], example["search"]["id"])
            self.assertEqual(record["repository_original"], example["search"]["source"])
            self.assertEqual(record["detail_metadata"], example["detail"])
        self.assertFalse(records[0]["identifier_conflicts"])
        self.assertEqual(records[1]["identifier_conflicts"][0]["requested_pair"][0], "project")
        self.assertEqual(records[1]["identifier_conflicts"][0]["returned_pair"][0], "ENA")
        self.assertEqual(records[2]["detail_parse_status"], "parsed_with_identity_conflict")

    def test_conflicting_identifier_fields_preserved_without_forced_resolution(self):
        metadata = {**EXAMPLES[0]["detail"], "source": "different", "id": "conflict"}
        record = {}
        status = normalize_detail(record, json.dumps(metadata).encode(), "raw.json", '["repo", "id"]')
        self.assertEqual(status, "failed")
        self.assertEqual(record["detail_metadata"], metadata)
        self.assertIn("Conflicting", record["detail_parse_error"])
        self.assertTrue(record["identifier_conflicts"])
        self.assertEqual(native_identity(EXAMPLES[0]["search"])[0],
                         [EXAMPLES[0]["search"]["source"], EXAMPLES[0]["search"]["id"]])

    def test_parsing_failures_consume_allowance_and_cannot_repeat_on_resume(self):
        for body in (b'not JSON', b'{"unrecognized":true}'):
            with self.subTest(body=body):
                self.path = Path(self.temp.name) / ("invalid-json" if body == b'not JSON' else "invalid-schema")
                def malformed(url, timeout):
                    if "search?" in url:
                        return self.service(url, timeout)
                    self.calls.append(url)
                    return body
                result = run_pilot(self.path, fetch=malformed, candidate_cap=3, detail_cap=1)
                self.assertEqual(result["counts"]["detail_allowance_used"], 1)
                self.assertEqual(result["counts"]["successful_details"], 1)
                self.assertEqual(result["counts"]["detail_parse_failures"], 1)
                self.assertEqual(result["counts"]["details_parsed"], 0)
                self.assertIn("detail_cap", result["stop_reasons"])
                self.assertEqual(next((self.path / "raw/details").glob("*.json")).read_bytes(), body)
                count = len(self.calls)
                run_pilot(self.path, resume=True, fetch=malformed)
                self.assertEqual(len(self.calls), count)

    def test_raw_response_reconciliation_precedes_cumulative_cap_check(self):
        run_pilot(self.path, fetch=self.service, candidate_cap=3, detail_cap=2)
        state = self.state()
        state["detail_retrievals"] = {}
        state["completed_details"] = []
        (self.path / "resume_state.json").write_text(json.dumps(state), encoding="utf-8")
        count = len(self.calls)
        result = run_pilot(self.path, resume=True, fetch=self.service)
        self.assertEqual(result["counts"]["detail_allowance_used"], 2)
        self.assertEqual(len(self.calls), count)

    def test_failed_transport_attempts_have_a_separate_cumulative_bound(self):
        def fail(url, timeout):
            if "search?" in url:
                return self.service(url, timeout)
            self.calls.append(url)
            raise RuntimeError("synthetic HTTP failure")
        result = run_pilot(self.path, fetch=fail, candidate_cap=1)
        self.assertEqual(result["counts"]["detail_allowance_used"], 0)
        self.assertEqual(list(self.state()["detail_attempt_counts"].values()), [2])
        count = len(self.calls)
        run_pilot(self.path, resume=True, fetch=fail)
        self.assertEqual(len(self.calls), count)

    def test_interrupted_request_reserves_capacity_and_is_not_repeated(self):
        def interrupt(url, timeout):
            if "search?" in url:
                return self.service(url, timeout)
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            run_pilot(self.path, fetch=interrupt, candidate_cap=3, detail_cap=1)
        result = run_pilot(self.path, resume=True, fetch=lambda *args: self.fail("Unexpected request"))
        self.assertEqual(result["counts"]["detail_allowance_used"], 1)
        self.assertEqual(result["counts"]["detail_retrievals_received"], 0)

    def test_received_receipt_survives_raw_storage_failure(self):
        original_write = Path.write_bytes
        def broken(path, data):
            if path.parent.name == "details":
                raise OSError("synthetic disk failure")
            return original_write(path, data)
        with patch.object(Path, "write_bytes", broken):
            with self.assertRaises(OSError):
                run_pilot(self.path, fetch=self.service, candidate_cap=3, detail_cap=1)
        result = run_pilot(self.path, resume=True, fetch=lambda *args: self.fail("Repeated receipt"))
        self.assertEqual(result["counts"]["detail_retrievals_received"], 1)

    def test_repair_is_offline_preserves_originals_and_blocks_network_resume(self):
        run_pilot(self.path, fetch=self.service)
        before = {p.relative_to(self.path): p.read_bytes() for p in self.path.rglob("*") if p.is_file()}
        output = Path(self.temp.name) / "repair"
        with patch("subprocess.run", side_effect=AssertionError("No subprocess/network permitted")):
            result = repair_saved_run(self.path, output)
        after = {p.relative_to(self.path): p.read_bytes() for p in self.path.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(result["counts"]["distinct_requested_records_with_saved_responses"], 3)
        self.assertEqual(result["counts"]["details_with_identity_conflicts"], 2)
        self.assertEqual(result["counts"]["within_first_50"], 3)
        fixed = json.loads((output / "resume_state.json").read_text(encoding="utf-8"))
        self.assertEqual(fixed["invocations"], self.state()["invocations"])
        self.assertEqual(list(fixed["records"]), list(self.state()["records"]))
        self.assertTrue(all((output / receipt["raw_response_ref"]).exists()
                            for receipt in fixed["detail_retrievals"].values()))
        with self.assertRaisesRegex(ValueError, "not authorized"):
            run_pilot(output, resume=True, fetch=lambda *a: self.fail("No network"))

    def test_repair_reports_order_uncertainty_instead_of_using_file_dates(self):
        run_pilot(self.path, fetch=self.service)
        state = self.state()
        state["invocations"][0]["requests"] = [e for e in state["invocations"][0]["requests"] if e["kind"] != "detail"]
        (self.path / "resume_state.json").write_text(json.dumps(state), encoding="utf-8")
        result = repair_saved_run(self.path, Path(self.temp.name) / "uncertain")
        self.assertEqual(result["counts"]["order_uncertain"], 3)
        self.assertEqual(result["counts"]["within_first_50"], 0)

    def test_legacy_state_requires_offline_accounting_repair(self):
        run_pilot(self.path, fetch=self.service)
        state = self.state()
        state["config"]["adapter_version"] = "1.0.0"
        (self.path / "resume_state.json").write_text(json.dumps(state), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "offline repair"):
            run_pilot(self.path, resume=True, fetch=lambda *a: self.fail("No network"))

    def test_fifty_malformed_responses_stop_before_fifty_first_detail(self):
        detail_calls = []
        def service(url, timeout):
            if "search?" in url:
                query = parse_qs(urlsplit(url).query)["query"][0]
                return json.dumps({"count": 10, "datasets": [
                    {"source": "fixture", "id": query + str(i)} for i in range(10)]}).encode()
            detail_calls.append(url)
            return b'invalid JSON after successful HTTP receipt'
        result = run_pilot(self.path, fetch=service)
        self.assertEqual(result["counts"]["unique_candidates"], 60)
        self.assertEqual(result["counts"]["detail_allowance_used"], 50)
        self.assertEqual(result["counts"]["detail_parse_failures"], 50)
        self.assertEqual(len(detail_calls), 50)
        run_pilot(self.path, resume=True, fetch=lambda *a: self.fail("No request after exhaustion and cap"))

    def test_repair_preserves_excess_responses_and_received_event_order(self):
        def service(url, timeout):
            if "search?" in url:
                query = parse_qs(urlsplit(url).query)["query"][0]
                # This fixture deliberately includes a large page to keep a
                # 51-receipt historical-violation regression manually simple.
                return json.dumps({"count": 51, "datasets": [
                    {"source": "fixture", "id": str(i)} for i in range(51)]}).encode()
            return json.dumps({"database": "fixture", "accession": url.rsplit("/", 1)[1]}).encode()
        run_pilot(self.path, fetch=service)
        run_pilot(self.path, resume=True, fetch=service, detail_cap=51)
        # Deliberately synthesize the legacy violation, without disabling the
        # repaired adapter's live accounting or using any network transport.
        state = self.state()
        state["limits"]["detail_cap"] = 50
        (self.path / "resume_state.json").write_text(json.dumps(state), encoding="utf-8")
        output = Path(self.temp.name) / "excess"
        result = repair_saved_run(self.path, output)
        self.assertEqual(result["counts"]["within_first_50"], 50)
        self.assertEqual(result["counts"]["excess_after_50"], 1)
        self.assertEqual(result["counts"]["distinct_requested_records_with_saved_responses"], 51)
        self.assertTrue(result["historical_cap_violation"])
        self.assertEqual(len(list((output / "raw/details").glob("*.json"))), 51)
        self.assertEqual(json.loads((output / "resume_state.json").read_text())["invocations"], state["invocations"])


if __name__ == "__main__":
    unittest.main()
