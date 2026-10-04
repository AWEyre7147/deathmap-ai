"""Offline v03 contract tests; fixtures contain only synthetic, non-evaluation text.

A fresh-process audit blocks networking, reads outside the planning directory
within a fake repository, and reads of TSV/ICRAFT paths even during import. Other
regressions use temporary roots, never regenerate historical discovery outputs.
"""
import ast
from contextlib import redirect_stderr, redirect_stdout
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from deathmap_ai import discovery_v03 as planner
from deathmap_ai import query_plan_v03 as config


class V03PlanningTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.path = self.root / config.OUTPUT_DIRECTORY / 'query_plan.json'

    def test_verbatim_questions_and_stable_query_identifiers(self):
        plan = planner.build_plan()
        self.assertEqual(plan['scientific_questions'], [
            {'question_id': 'SQ01', 'question': 'pooled CRISPR knockout screens in cancer cells under immune selection'},
            {'question_id': 'SQ02', 'question': 'pooled CRISPR knockout screens in immune cells under cancer-cell-mediated selection'},
        ])
        self.assertEqual([q['query_id'] for q in plan['resources'][0]['queries']], ['OM3-Q01', 'OM3-Q02', 'OM3-Q03', 'OM3-Q04'])
        self.assertEqual([q['query_id'] for q in plan['resources'][1]['queries']], ['OR3-Q01', 'OR3-Q02', 'OR3-Q03'])
        before = planner.build_plan()
        plan['resources'][0]['queries'][0]['purpose'] = 'synthetic detached mutation'
        self.assertEqual(planner.build_plan(), before)

    def test_queries_have_question_links_purpose_and_semantic_gaps(self):
        for resource in planner.build_plan()['resources']:
            identities = [q['query_id'] for q in resource['queries']]
            self.assertEqual(len(identities), len(set(identities)))
            for query in resource['queries']:
                self.assertTrue(set(query['scientific_question_ids']) <= {'SQ01', 'SQ02'})
                for field in ('scientific_question_ids', 'purpose', 'concepts_represented', 'known_semantic_gaps'):
                    self.assertTrue(query[field])
                self.assertEqual(query['filters'], [])
                self.assertIsNone(query['sort'])
        shared = planner.build_plan()['resources'][0]['queries'][2]
        self.assertEqual(shared['scientific_question_ids'], ['SQ01', 'SQ02'])

    def test_case_insensitive_orcs_routing_and_absent_trigger(self):
        questions = [{'question_id': 'synthetic-one', 'question': 'a cRiSpR test'},
                     {'question_id': 'synthetic-two', 'question': 'a fluorescence test'}]
        self.assertEqual(planner.orcs_question_ids(questions), ['synthetic-one'])
        self.assertEqual(planner.orcs_question_ids(questions[1:]), [])
        self.assertEqual(planner.orcs_question_ids([]), [])
        orcs = planner.build_plan()['resources'][1]
        self.assertFalse(orcs['routing_rule']['executed'])
        self.assertFalse(orcs['interface']['refresh_authorized'])
        self.assertIsNone(orcs['limits']['candidate_cap'])
        self.assertIn('publication_siblings', orcs['evidence_roles'])

    def test_explicit_forbidden_inputs_and_independent_accounting(self):
        plan = planner.build_plan()
        exclusions = {e['input_id']: e for e in plan['forbidden_discovery_inputs']}
        self.assertEqual(exclusions['known-publication-evaluation']['path'], 'data/brainstorming/week3_papers_metadata.tsv')
        self.assertIn('regardless of location', exclusions['icraft']['restriction'])
        omics = plan['resources'][0]
        self.assertFalse(omics['resume_policy']['reuse_v01_v02_state'])
        self.assertFalse(omics['resume_policy']['ledger_created_in_this_slice'])
        self.assertTrue(omics['retry_policy']['reserve_before_request'])
        self.assertFalse(omics['retry_policy']['repeat_uncertain_automatically'])
        for field in ('candidate_cap', 'detail_attempt_cap', 'search_request_cap'):
            self.assertIsNone(omics['limits'][field])

    def test_rejects_every_missing_top_level_and_resource_field(self):
        original = planner.build_plan()
        for field in original:
            broken = copy.deepcopy(original)
            del broken[field]
            with self.subTest(field=field), self.assertRaises(planner.PlanError):
                planner.validate_plan(broken)
        for index, resource in enumerate(original['resources']):
            for field in resource:
                broken = copy.deepcopy(original)
                del broken['resources'][index][field]
                with self.subTest(resource=index, field=field), self.assertRaises(planner.PlanError):
                    planner.validate_plan(broken)

    def test_rejects_unversioned_and_incomplete_queries(self):
        changes = [
            (('schema_version',), 'unversioned'), (('plan_version',), ''),
            (('scientific_questions', 0, 'question'), 'synthetic altered question'),
            (('resources', 0, 'query_strategy_id'), 'unversioned'),
            (('resources', 0, 'queries', 0, 'scientific_question_ids'), []),
            (('resources', 0, 'queries', 0, 'scientific_question_ids'), ['unknown']),
            (('resources', 0, 'queries', 0, 'purpose'), ''),
            (('resources', 0, 'queries', 0, 'known_semantic_gaps'), []),
            (('resources', 0, 'queries', 0, 'query_id'), 'OM3-Q02'),
            (('resources', 0, 'limits', 'candidate_cap'), 5000),
            (('resources', 0, 'pagination', 'size'), 101),
            (('resources', 0, 'retry_policy', 'reserve_before_request'), False),
            (('authorization', 'live_retrieval'), True),
        ]
        for path, value in changes:
            plan = planner.build_plan()
            target = plan
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with self.subTest(path=path), self.assertRaises(planner.PlanError):
                planner.validate_plan(plan)

    def test_rejects_missing_nested_policies_before_any_write(self):
        for index in (0, 1):
            for section in ('interface', 'pagination', 'limits', 'retry_policy', 'rate_limit_policy', 'resume_policy'):
                plan = planner.build_plan()
                field = next(iter(plan['resources'][index][section]))
                del plan['resources'][index][section][field]
                with self.subTest(index=index, section=section), self.assertRaises(planner.PlanError):
                    planner.validate_plan(plan)
        with patch.object(config, 'SCIENTIFIC_QUESTIONS', []), self.assertRaises(planner.PlanError):
            planner.prepare(self.root)
        self.assertFalse((self.root / 'outputs').exists())

    def test_deterministic_semantics_ignore_only_generation_timestamp(self):
        first = planner.build_plan('2026-09-27T00:00:00+00:00')
        second = planner.build_plan('2026-09-28T00:00:00Z')
        self.assertEqual(planner.semantic_digest(first), planner.semantic_digest(second))
        self.assertEqual(planner.build_plan(), planner.build_plan())
        second['resources'][0]['queries'][0]['purpose'] = 'synthetic changed purpose'
        self.assertNotEqual(planner.semantic_digest(first), planner.semantic_digest(second))
        with self.assertRaises(planner.PlanError):
            planner.build_plan('2026-09-27T00:00:00')

    def test_prepare_verify_idempotence_and_existing_review_protection(self):
        saved = planner.prepare(self.root, '2026-09-27T00:00:00Z')
        original = self.path.read_bytes()
        self.assertEqual(planner.verify(self.root), saved)
        self.assertEqual(planner.prepare(self.root, '2026-09-28T00:00:00Z'), saved)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual([p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_file()], [config.OUTPUT_DIRECTORY + '/query_plan.json'])
        saved['resources'][0]['queries'][0]['purpose'] = 'synthetic reviewer edit'
        self.path.write_text(json.dumps(saved), encoding='utf-8')
        edited = self.path.read_bytes()
        with self.assertRaises(planner.PlanError):
            planner.verify(self.root)
        with self.assertRaises(planner.PlanError):
            planner.prepare(self.root)
        self.assertEqual(self.path.read_bytes(), edited)

    def test_verify_missing_plan_writes_nothing(self):
        with self.assertRaises(planner.PlanError):
            planner.verify(self.root)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_live_actions_refused_before_read_or_write(self):
        for action in ('run', 'retrieve', 'search', 'resume', 'fetch', 'execute', 'download', 'RUN'):
            with self.subTest(action=action), patch.object(planner, 'build_plan', side_effect=AssertionError('must not initialize')), redirect_stderr(io.StringIO()) as error, self.assertRaises(SystemExit) as stopped:
                planner.main([action, '--root', str(self.root)])
            self.assertEqual(stopped.exception.code, 2)
            self.assertIn('not authorized', error.getvalue())
        self.assertEqual(list(self.root.iterdir()), [])

    def test_no_adapter_evaluation_or_network_import_dependencies(self):
        allowed = {'argparse', 'copy', 'datetime', 'hashlib', 'json', 'pathlib', 're', 'deathmap_ai'}
        for module in (planner, config):
            tree = ast.parse(Path(module.__file__).read_text(encoding='utf-8-sig'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertTrue({alias.name for alias in node.names} <= allowed)
                elif isinstance(node, ast.ImportFrom):
                    self.assertIn(node.module, allowed)
                    if node.module == 'deathmap_ai':
                        self.assertEqual([a.name for a in node.names], ['query_plan_v03'])

    def test_fresh_process_offline_io_boundary_and_historical_preservation(self):
        historical = []
        for version in ('v01', 'v02'):
            for package in ('omicsdi', 'orcs'):
                for name in ('manifest.json', 'resume_state.json', 'datasets.json'):
                    path = self.root / 'outputs' / package / ('synthetic-' + version) / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text('{"synthetic":"unchanged"}', encoding='utf-8')
                    historical.append(path)
        for relative in ('data/brainstorming/week3_papers_metadata.tsv', 'data/icraft/synthetic.txt'):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('synthetic forbidden contents', encoding='utf-8')
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in historical}
        script = r'''
import sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
sys.path.insert(0, sys.argv[2])
allowed = root / 'outputs/immune-crispr-coculture-v03/query_plan.json'
def audit(event, args):
    if event.startswith(('socket.', 'urllib.')) or event in ('subprocess.Popen', 'os.system'):
        raise AssertionError('Network/process operation is forbidden')
    if event == 'open' and isinstance(args[0], (str, bytes)):
        text = str(args[0]).casefold()
        if 'week3_papers_metadata.tsv' in text or 'icraft' in text:
            raise AssertionError('Forbidden evaluation read')
        path = Path(args[0]).resolve()
        if path.is_relative_to(root) and path != allowed:
            raise AssertionError('Unexpected repository file I/O: ' + str(path))
sys.addaudithook(audit)
from deathmap_ai.discovery_v03 import main
main(['prepare', '--root', str(root)])
main(['verify', '--root', str(root)])
assert not any(name in sys.modules for name in ('deathmap_ai.discovery_v02', 'deathmap_ai.shared_search', 'deathmap_ai.omicsdi', 'deathmap_ai.resource_migration'))
'''
        result = subprocess.run([sys.executable, '-B', '-c', script, str(self.root), str(Path(planner.__file__).resolve().parents[1])], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.path.exists())
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in historical})
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])


if __name__ == '__main__':
    unittest.main()
