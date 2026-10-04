"""Offline v03 query-plan preparation and semantic verification.

The only runtime inputs are the adjacent data-only configuration and, for
verification, an existing query_plan.json. This module does not import retrieval,
evaluation, cache-processing or export adapters. It never executes proposed local
ORCS rules either. Semantic comparison excludes only the optional generated_at
field; changes to queries or policy require review and are never overwritten.
"""
import argparse
import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

from deathmap_ai import query_plan_v03 as config


class PlanError(ValueError):
    """An incomplete, inconsistent or unreviewed planning artifact was supplied."""


def orcs_question_ids(questions):
    """Return IDs whose original question contains CRISPR, case-insensitively.

    This pure routing helper accepts question_id/question mappings. It neither
    interprets scientific intent nor reads or searches the ORCS cache.
    """
    return [q['question_id'] for q in questions if 'crispr' in q['question'].casefold()]


def build_plan(generated_at=None):
    """Build and validate a detached proposed plan from the fixed v03 configuration.

    generated_at may be an ISO-8601 timestamp with a timezone, or null. No clock,
    filesystem or network input influences the semantic plan.
    """
    questions = copy.deepcopy(config.SCIENTIFIC_QUESTIONS)
    resources = copy.deepcopy(config.RESOURCE_POLICIES)
    for resource in resources:
        omics = resource['resource_name'] == 'OmicsDI'
        resource['routing_rule'] = {
            'rule': 'always primary' if omics else 'case-insensitive substring CRISPR in each original question',
            'scientific_question_ids': [q['question_id'] for q in questions] if omics else orcs_question_ids(questions),
            'included_in_plan': True if omics else bool(orcs_question_ids(questions)),
            'executed': False,
        }
        resource['queries'] = copy.deepcopy(config.OMICS_QUERIES if omics else config.ORCS_QUERIES)
        for query in resource['queries']:
            query['submitted_query'] = query['intended_query'] if omics else None
            query['submission_status'] = 'proposed_not_submitted' if omics else 'not_applicable_local_rule_not_executed'
            query['filters'] = []
            query['sort'] = None
            query['local_matching'] = None if omics else {
                'operator': 'all_of', 'terms': query.pop('matching_terms'),
                'case_sensitive': False, 'word_boundaries': True,
                'scope': 'Any native text fields within the same screen record; each term may match a different field.',
                'synonym_expansion': False, 'stemming': False,
            }
    plan = {
        'schema_version': config.SCHEMA_VERSION,
        'plan_version': config.PLAN_VERSION,
        'status': 'proposed_for_owner_review',
        'generated_at': generated_at,
        'authorization': {'offline_planning': True, 'live_retrieval': False, 'local_index_search': False},
        'scientific_questions': questions,
        'resources': resources,
        'forbidden_discovery_inputs': copy.deepcopy(config.FORBIDDEN_INPUTS),
        'preservation_rules': copy.deepcopy(config.PRESERVATION_RULES),
        'review_gates': copy.deepcopy(config.REVIEW_GATES),
        'source_documentation': copy.deepcopy(config.SOURCE_DOCUMENTATION),
        'interface_research': copy.deepcopy(config.INTERFACE_RESEARCH),
        'comparison_policy': 'Ignore only top-level generated_at; preserve list order and every other value.',
        'interpretation': 'Questions express intent, not submitted queries or eligibility rules. Proposed queries are unvalidated and not claimed exhaustive or high-recall.',
    }
    validate_plan(plan)
    return plan


def _require(condition, message):
    if not condition:
        raise PlanError(message)


def _object(value, keys, location):
    _require(isinstance(value, dict), f'{location} must be an object')
    missing = set(keys) - value.keys()
    _require(not missing, f'{location} missing fields: {sorted(missing)}')


def _text(value, location):
    _require(isinstance(value, str) and bool(value.strip()), f'{location} must be nonempty text')


def _strings(value, location):
    _require(isinstance(value, list) and bool(value), f'{location} must be a nonempty list')
    for item in value:
        _text(item, location)


def _positive(value, location):
    _require(type(value) in (int, float) and 0 < value <= 3600, f'{location} must be a bounded positive number')


def validate_plan(plan):
    """Reject unsupported versions, missing fields and unsafe policy assertions.

    Validation is structural and scope-aware, not an API probe or scientific
    assessment. It raises PlanError before writing and performs no I/O.
    """
    _object(plan, ['schema_version', 'plan_version', 'status', 'generated_at', 'authorization',
                   'scientific_questions', 'resources', 'forbidden_discovery_inputs',
                   'preservation_rules', 'review_gates', 'source_documentation',
                   'interface_research', 'comparison_policy', 'interpretation'], 'plan')
    _require(plan['schema_version'] == config.SCHEMA_VERSION, 'Unsupported or unversioned schema')
    _require(plan['plan_version'] == config.PLAN_VERSION, 'Unsupported or unversioned plan')
    _require(plan['status'] == 'proposed_for_owner_review', 'Plan must remain proposed for review')
    authorization = {'offline_planning': True, 'live_retrieval': False, 'local_index_search': False}
    _object(plan['authorization'], authorization.keys(), 'authorization')
    _require(all(plan['authorization'][key] is value for key, value in authorization.items()), 'Only offline planning is authorized')
    timestamp = plan['generated_at']
    if timestamp is not None:
        _text(timestamp, 'generated_at')
        try:
            _require(datetime.fromisoformat(timestamp.replace('Z', '+00:00')).tzinfo is not None, 'Timestamp needs a timezone')
        except ValueError as error:
            raise PlanError('Invalid generation timestamp') from error
    _require(plan['scientific_questions'] == config.SCIENTIFIC_QUESTIONS, 'Preserve SQ01/SQ02 and their verbatim questions')
    qids = {q['question_id'] for q in plan['scientific_questions']}
    resources = plan['resources']
    _require(isinstance(resources, list) and len(resources) == 2, 'Two separate resource proposals required')
    _require(all(isinstance(r, dict) for r in resources), 'Resource proposals must be objects')
    _require([r.get('resource_name') for r in resources] == ['OmicsDI', 'ORCS'], 'Keep OmicsDI and ORCS separate and in stable order')
    for resource in resources:
        _object(resource, ['resource_name', 'resource_role', 'interface', 'routing_rule', 'query_strategy_id',
                           'queries', 'pagination', 'limits', 'retry_policy', 'rate_limit_policy',
                           'stop_conditions', 'resume_policy'], 'resource')
        name = resource['resource_name']
        _text(resource['resource_role'], 'resource_role')
        _require(isinstance(resource['query_strategy_id'], str) and re.fullmatch(r'[a-z]+-questions-v03\.\d+', resource['query_strategy_id']), 'Versioned query strategy required')
        _object(resource['interface'], ['kind', 'live_enabled'], 'interface')
        _require(resource['interface']['live_enabled'] is False, 'Live interface is forbidden')
        routing = resource['routing_rule']
        _object(routing, ['rule', 'scientific_question_ids', 'included_in_plan', 'executed'], 'routing_rule')
        _text(routing['rule'], 'routing_rule.rule')
        expected = list(q['question_id'] for q in plan['scientific_questions']) if name == 'OmicsDI' else orcs_question_ids(plan['scientific_questions'])
        _require(routing['scientific_question_ids'] == expected and routing['included_in_plan'] is bool(expected) and routing['executed'] is False, 'Incorrect or executed routing')
        queries = resource['queries']
        _require(isinstance(queries, list) and bool(queries), 'Resource needs proposed queries')
        seen = set()
        covered = set()
        for query in queries:
            _object(query, ['query_id', 'scientific_question_ids', 'intended_query', 'submitted_query', 'purpose',
                            'concepts_represented', 'known_semantic_gaps', 'filters', 'sort', 'submission_status', 'local_matching'], 'query')
            identity = query['query_id']
            prefix = 'OM3' if name == 'OmicsDI' else 'OR3'
            _require(isinstance(identity, str) and re.fullmatch(prefix + r'-Q\d{2}', identity), 'Invalid stable query ID')
            _require(identity not in seen, 'Duplicate query ID within resource')
            seen.add(identity)
            _strings(query['scientific_question_ids'], 'query scientific_question_ids')
            _require(len(set(query['scientific_question_ids'])) == len(query['scientific_question_ids']) and set(query['scientific_question_ids']) <= qids, 'Invalid question association')
            covered.update(query['scientific_question_ids'])
            for field in ('intended_query', 'purpose'):
                _text(query[field], field)
            for field in ('concepts_represented', 'known_semantic_gaps'):
                _strings(query[field], field)
            _require(query['filters'] == [] and query['sort'] is None, 'This proposal uses no filters or explicit sort')
            if name == 'OmicsDI':
                _require(query['submitted_query'] == query['intended_query'] and query['submission_status'] == 'proposed_not_submitted', 'Keep exact proposed strings without claiming submission')
                _require(query['local_matching'] is None, 'No local OmicsDI matcher')
                # Restricted proposed grammar avoids silently inventing OR/NOT,
                # field aliases, precedence or executable query expressions.
                atoms = query['submitted_query'].split(' AND ')
                _require(len(atoms) >= 2 and all(re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*|"[A-Za-z][A-Za-z0-9 -]*"', atom) for atom in atoms), 'Only reviewed AND terms and quoted phrases are proposed')
            else:
                _require(query['submitted_query'] is None and query['submission_status'] == 'not_applicable_local_rule_not_executed', 'ORCS rule must not claim a submitted request')
                matching = query['local_matching']
                _object(matching, ['operator', 'terms', 'case_sensitive', 'word_boundaries', 'scope', 'synonym_expansion', 'stemming'], 'local_matching')
                _strings(matching['terms'], 'matching terms')
                _text(matching['scope'], 'matching scope')
                _require(matching['operator'] == 'all_of' and matching['case_sensitive'] is False and matching['word_boundaries'] is True and matching['synonym_expansion'] is False and matching['stemming'] is False, 'Unsupported local matching proposal')
                _require(query['intended_query'] == 'ALL_OF(' + '; '.join(matching['terms']) + ')', 'Local display rule and terms disagree')
        _require(covered == qids, 'Each resource must represent both questions')
        _strings(resource['stop_conditions'], 'stop_conditions')
        # Validate all nested policy fields against the declared configuration
        # shape, then enforce the non-negotiable authorization/accounting bounds.
        template = next(r for r in config.RESOURCE_POLICIES if r['resource_name'] == name)
        for section in ('interface', 'pagination', 'limits', 'retry_policy', 'rate_limit_policy', 'resume_policy'):
            _object(resource[section], template[section].keys(), section)
        if name == 'OmicsDI':
            limits, retry, rate = resource['limits'], resource['retry_policy'], resource['rate_limit_policy']
            for section in ('pagination', 'limits', 'retry_policy', 'rate_limit_policy'):
                _require(resource[section]['status'] == 'proposed_not_authorized', 'Policy must remain an unauthorized proposal')
            for field in ('candidate_cap', 'detail_attempt_cap', 'search_request_cap'):
                _require(limits[field] is None, 'Retrieval caps await owner decision in this plan version')
            _positive(limits['request_timeout_seconds'], 'timeout')
            _require(limits['concurrent_requests'] == 1, 'Only serial pacing is proposed')
            _positive(rate['minimum_request_interval_seconds'], 'minimum request interval')
            _require(rate['honor_retry_after'] is True and rate['published_service_quota'] is None, 'Honor service guidance; do not invent quota')
            _require(type(retry['search_attempts_per_query_offset']) is int and 1 <= retry['search_attempts_per_query_offset'] <= 3 and retry['detail_attempts_per_native_key'] == 1, 'Bound cumulative attempts')
            _positive(retry['retry_delay_seconds'], 'retry delay')
            _require(retry['reserve_before_request'] is True and retry['repeat_uncertain_automatically'] is False, 'Preserve reservation and uncertain-request accounting')
            pagination = resource['pagination']
            _require(type(pagination['size']) is int and 1 <= pagination['size'] <= 100 and pagination['start'] == 0, 'Invalid initial pagination proposal')
            resume = resource['resume_policy']
            _require(resume['new_ledger_required'] is True and resume['reuse_v01_v02_state'] is False and resume['ledger_created_in_this_slice'] is False, 'No borrowing or creating retrieval ledgers')
            _require(resume['identity_fields'] == {'search': ['source', 'id'], 'detail': ['database', 'accession']}, 'Preserve observed native identity fields')
            _strings(resume['state_to_preserve'], 'resume state description')
        else:
            _require(resource['interface']['refresh_authorized'] is False and resource['interface']['index_loaded_as_discovery_input'] is False, 'No ORCS refresh or local execution')
            _require(resource['limits']['candidate_cap'] is None and resource['limits']['network_requests'] == 0, 'ORCS uses uncapped local index without requests')
            _object(resource.get('evidence_roles'), ['direct_matches', 'publication_siblings'], 'ORCS evidence_roles')
            for text in resource['evidence_roles'].values():
                _text(text, 'evidence role')
    for field, required, idfield in [
        ('forbidden_discovery_inputs', config.FORBIDDEN_INPUTS, 'input_id'),
        ('preservation_rules', config.PRESERVATION_RULES, 'rule_id'),
        ('review_gates', config.REVIEW_GATES, 'gate_id'),
        ('source_documentation', config.SOURCE_DOCUMENTATION, 'source_id'),
    ]:
        rows = plan[field]
        _require(isinstance(rows, list) and len(rows) == len(required), f'Incomplete {field}')
        for row, template in zip(rows, required):
            _object(row, template.keys(), field)
            _require(row[idfield] == template[idfield], f'Unstable {field} identifier')
            for value in row.values():
                _text(value, field)
            if field == 'review_gates':
                _require(row['status'] == 'pending', 'Review is not yet approved')
        if field == 'forbidden_discovery_inputs':
            _require(rows == required, 'Explicit TSV and all-local-ICRAFT exclusions are required')
    _object(plan['interface_research'], config.INTERFACE_RESEARCH.keys(), 'interface_research')
    sources = {r['source_id'] for r in plan['source_documentation']}
    for topic, template in config.INTERFACE_RESEARCH.items():
        observation = plan['interface_research'][topic]
        _object(observation, template.keys(), 'interface research ' + topic)
        _strings(observation['sources'], 'research source references')
        _require(set(observation['sources']) <= sources, 'Unknown documentation reference')


def semantic_plan(plan):
    """Return the validated semantic content, ignoring only generation timestamp."""
    validate_plan(plan)
    semantic = copy.deepcopy(plan)
    semantic.pop('generated_at')
    return semantic


def semantic_digest(plan):
    """Hash canonical semantic JSON for review; this is not an approval token."""
    payload = json.dumps(semantic_plan(plan), ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def _plan_path(root):
    intended = root.resolve() / config.OUTPUT_DIRECTORY / 'query_plan.json'
    _require(intended.resolve() == intended, 'Planning output must not redirect through a symlink or junction')
    return intended


def _load(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise PlanError(f'Cannot read saved query plan: {path}: {error}') from error


def prepare(root, generated_at=None):
    """Write only the proposed plan, or retain an identical existing artifact.

    root is a repository path. Validation precedes directory creation. An existing
    divergent plan is never overwritten; review/reversion must be explicit.
    """
    proposed = build_plan(generated_at)
    path = _plan_path(Path(root))
    if path.exists():
        saved = _load(path)
        _require(semantic_plan(saved) == semantic_plan(proposed), 'Existing plan differs; refusing to overwrite review material')
        return saved
    encoded = json.dumps(proposed, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also protects a plan created by a concurrent prepare.
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        handle.write(encoded)
    return proposed


def verify(root):
    """Regenerate in memory and compare; never create directories or write files."""
    proposed = build_plan()
    saved = _load(_plan_path(Path(root)))
    _require(semantic_plan(saved) == semantic_plan(proposed), 'Saved semantic plan differs from current configuration')
    return saved


def main(argv=None):
    """Expose only prepare/verify; reject every other action before plan I/O."""
    parser = argparse.ArgumentParser(description='Offline v03 proposed query plan; no discovery execution')
    parser.add_argument('action', help='prepare or verify only; live retrieval is not authorized')
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--generated-at', help='Optional ISO-8601 timestamp with timezone, for prepare only')
    args = parser.parse_args(argv)
    if args.action not in ('prepare', 'verify'):
        parser.error('V03 is offline-only: live retrieval and local discovery execution are not authorized. Use prepare or verify.')
    if args.action == 'verify' and args.generated_at is not None:
        parser.error('--generated-at applies only to prepare')
    try:
        plan = prepare(args.root, args.generated_at) if args.action == 'prepare' else verify(args.root)
    except (PlanError, OSError) as error:
        parser.error(str(error))
    print(json.dumps({'action': args.action, 'status': plan['status'], 'path': str(_plan_path(args.root)),
                      'semantic_sha256': semantic_digest(plan), 'retrieval_authorized': False}, indent=2))


if __name__ == '__main__':
    main()
