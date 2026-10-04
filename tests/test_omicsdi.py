"""Small synthetic metadata fixtures verify retrieval mechanics, not eligibility."""

import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from deathmap_ai.omicsdi import BASE, fetch_metadata, run_pilot
from deathmap_ai.omicsdi_queries import QUERIES

FIXTURE = json.loads((Path(__file__).parent / "fixtures/omicsdi-metadata.json").read_text())


class Service:
    def __init__(self, pages=None):
        self.calls = []
        self.pages = pages

    def __call__(self, url, timeout):
        self.calls.append(url)
        if "search?" in url:
            params = parse_qs(urlsplit(url).query)
            query = params["query"][0]
            offset = int(params["start"][0])
            body = self.pages(query, offset) if self.pages else FIXTURE["search"]
        else:
            repo, identifier = [unquote(x) for x in url.removeprefix(BASE).split("/")]
            body = {**FIXTURE["detail"], "source": repo, "id": identifier}
        return json.dumps(body, ensure_ascii=False).encode()


class OmicsdiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "run"

    def state(self):
        return json.loads((self.path / "resume_state.json").read_text(encoding="utf-8"))

    def test_queries_identity_provenance_and_lossless_details(self):
        service = Service()
        manifest = run_pilot(self.path, fetch=service)
        self.assertEqual(manifest["counts"]["unique_candidates"], 3)
        self.assertEqual(manifest["counts"]["successful_details"], 3)
        self.assertEqual(manifest["counts"]["query_hits"], 18)
        self.assertTrue(manifest["search_complete"])
        searches = [parse_qs(urlsplit(u).query) for u in service.calls if "search?" in u]
        self.assertEqual([q["query"][0] for q in searches], list(QUERIES.values()))
        self.assertTrue(all(set(q) == {"query", "start", "size"} and q["size"] == ["10"] for q in searches))
        records = list(self.state()["records"].values())
        first = records[0]
        self.assertEqual(first["title_original"], "Search title")
        self.assertEqual(first["detail_metadata"], FIXTURE["detail"])
        self.assertEqual(len(first["search_observations"]), 6)
        self.assertIsNone(records[1]["evidence_text_original"])
        self.assertNotEqual(records[0]["record_id"], records[1]["record_id"])
        self.assertEqual((self.path / first["detail_response_ref"]).read_bytes(), json.dumps(FIXTURE["detail"], ensure_ascii=False).encode())
        self.assertTrue(all(u.startswith(BASE) for u in service.calls))

    def test_caps_buffer_resume_and_no_duplicates(self):
        service = Service()
        run_pilot(self.path, fetch=service, candidate_cap=1, detail_cap=1)
        state = self.state()
        self.assertEqual(len(state["queries"]["Q01"]["buffer"]), 2)
        old_id = next(iter(state["records"].values()))["record_id"]
        count = len(service.calls)
        run_pilot(self.path, fetch=service, resume=True)
        self.assertEqual(len(service.calls), count)
        result = run_pilot(self.path, fetch=service, resume=True, candidate_cap=3, detail_cap=3)
        self.assertEqual(result["counts"]["unique_candidates"], 3)
        self.assertEqual(result["counts"]["successful_details"], 3)
        self.assertEqual(next(iter(self.state()["records"].values()))["record_id"], old_id)
        self.assertEqual(len([u for u in service.calls if "search?" not in u]), 3)
        hits = self.state()["query_hits"]
        self.assertEqual(len(hits), len({(h["query_id"], h["page_offset"], h["page_position"]) for h in hits}))

    def test_round_robin_details_and_pagination(self):
        def pages(query, offset):
            qid = list(QUERIES.values()).index(query)
            return {"count": 12, "datasets": [{"source": "geo", "id": f"{qid}-{i}"} for i in range(offset, min(offset + 10, 12))]}
        service = Service(pages)
        result = run_pilot(self.path, fetch=service)
        self.assertEqual(result["counts"]["unique_candidates"], 72)
        self.assertEqual(result["counts"]["successful_details"], 50)
        details = [u.rsplit("/", 1)[1] for u in service.calls if "search?" not in u]
        self.assertEqual(details[:12], [f"{q}-{i}" for i in range(2) for q in range(6)])
        searches = [parse_qs(urlsplit(u).query) for u in service.calls if "search?" in u]
        self.assertEqual([q["start"][0] for q in searches], ["0"] * 6 + ["10"] * 6)

    def test_failures_bounded_and_resumable_not_empty(self):
        calls = []
        def broken(url, timeout):
            calls.append(url)
            raise RuntimeError("service unavailable")
        result = run_pilot(self.path, fetch=broken, retries=0)
        self.assertEqual(len(calls), 6)
        self.assertFalse(result["search_complete"])
        self.assertEqual(result["counts"]["errors"], 6)
        self.assertTrue(all(q["offset"] == 0 for q in self.state()["queries"].values()))
        self.assertEqual(run_pilot(self.path, fetch=Service(), resume=True, retries=0)["counts"]["successful_details"], 3)

    def test_deadline_preserves_state(self):
        ticks = [0.0]
        def clock():
            return ticks[0]
        def slow(url, timeout):
            ticks[0] += timeout
            raise RuntimeError("timeout")
        result = run_pilot(self.path, fetch=slow, clock=clock, budget_seconds=15)
        self.assertIn("network_deadline", result["stop_reasons"])
        self.assertEqual(ticks[0], 5)
        self.assertTrue((self.path / "records.jsonl").exists())

    def test_resume_rejects_configuration_changes_and_cap_decreases(self):
        run_pilot(self.path, fetch=Service())
        with self.assertRaisesRegex(ValueError, "Incompatible"):
            run_pilot(self.path, fetch=Service(), resume=True, request_timeout=2)
        with self.assertRaisesRegex(ValueError, "cannot decrease"):
            run_pilot(self.path, fetch=Service(), resume=True, candidate_cap=1)
        state = self.state()
        state["config"]["queries"]["Q01"] = "changed"
        (self.path / "resume_state.json").write_text(json.dumps(state))
        with self.assertRaisesRegex(ValueError, "Incompatible"):
            run_pilot(self.path, fetch=Service(), resume=True)

    def test_only_approved_endpoints_and_invalid_run_caps(self):
        for url in ("https://example.org/data", BASE + "geo/id/files", BASE + "geo/id?files=true"):
            with self.assertRaises(ValueError):
                fetch_metadata(url, 1)
        with self.assertRaises(ValueError):
            run_pilot(self.path, candidate_cap=101)

    def test_saved_response_reused_without_repeat_request(self):
        service = Service()
        run_pilot(self.path, fetch=service, candidate_cap=1, detail_cap=0)
        state = self.state()
        record = next(iter(state["records"].values()))
        ref = self.path / "raw" / "details" / (record["record_id"] + ".json")
        ref.write_text(json.dumps(FIXTURE["detail"]))
        count = len(service.calls)
        run_pilot(self.path, fetch=service, resume=True, detail_cap=1)
        self.assertEqual(len(service.calls), count)
        self.assertEqual(len(self.state()["completed_details"]), 1)

    def test_failed_details_resume_and_preserve_multiple_identifiers(self):
        service = Service()
        def fail_detail(url, timeout):
            if "search?" not in url:
                raise RuntimeError("detail failure")
            return service(url, timeout)
        first = run_pilot(self.path, fetch=fail_detail, retries=0)
        self.assertEqual(first["counts"]["successful_details"], 0)
        self.assertEqual(first["counts"]["pending_details"], 3)
        self.assertEqual(first["counts"]["errors"], 3)
        result = run_pilot(self.path, resume=True, fetch=service, retries=0)
        self.assertEqual(result["counts"]["successful_details"], 3)
        record = next(iter(self.state()["records"].values()))
        fields = record["reported_field_observations"][-1]["fields"]
        self.assertEqual(fields["crossReferences"]["pubmed"], ["111", "222"])
        self.assertEqual(fields["crossReferences"]["ena"], ["PRJ-test-1", "PRJ-test-2"])

    def test_invalid_search_schema_and_missing_native_identity_remain_visible(self):
        result = run_pilot(self.path, fetch=lambda u, t: b'{"error":"unavailable"}', retries=0)
        self.assertFalse(result["search_complete"])
        self.assertEqual(result["counts"]["unique_candidates"], 0)
        self.assertEqual(len(list((self.path / "raw").glob("search*.json"))), 6)

    def test_unidentifiable_row_is_preserved_in_raw_and_errors(self):
        body = b'{"count":1,"datasets":[{"name":"No identifier"}]}'
        result = run_pilot(self.path, fetch=lambda u, t: body)
        self.assertEqual(result["counts"]["unique_candidates"], 0)
        self.assertEqual(result["counts"]["errors"], 6)
        self.assertEqual((self.path / "raw/search_Q01_page_0.json").read_bytes(), body)


if __name__ == "__main__":
    unittest.main()
