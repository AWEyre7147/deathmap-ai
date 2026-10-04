"""Accepted SQ01 query data and immutable semantic-plan contract.

The eleven literals come only from handoff 10. The executable plan deliberately
contains no SQ02, historical query state, evaluation inputs or detail allowance.
ORCS uses the same term sets as all-of rules over named native fields; this is
literal discovery evidence, not an assignment of perturbation or selection roles.
"""
import copy
import hashlib
import json
from pathlib import Path

VERSION = 'immune-crispr-coculture-v03'
RUN_ID = VERSION + '-sq01'
QUESTION = 'pooled CRISPR knockout screens in cancer cells under immune selection'
ENDPOINT = 'https://www.omicsdi.org/ws/dataset/search'
INDEX = 'outputs/orcs/cache/legacy/20260904T213941Z/orcs-screens.raw.json'
INDEX_SUMMARY = 'outputs/orcs/cache/legacy/20260904T213941Z/summary.json'
FIELDS = ['SCREEN_NAME', 'SCREEN_FORMAT', 'SCREEN_TYPE', 'METHODOLOGY', 'ENZYME',
          'LIBRARY', 'LIBRARY_TYPE', 'EXPERIMENTAL_SETUP', 'CELL_LINE', 'CELL_TYPE',
          'CONDITION_NAME', 'PHENOTYPE', 'NOTES', 'SCREEN_RATIONALE']
LITERALS = [
    ('strict reference', 'pooled AND CRISPR AND knockout AND screens AND "cancer cells" AND immune AND selection', 'Closest literal representation of SQ01.'),
    ('relaxed reference', 'CRISPR AND knockout AND "cancer cells" AND immune', 'Tests omitted pooled, screen or selection wording.'),
    ('singular screen', 'pooled AND CRISPR AND knockout AND screen AND "cancer cells" AND immune AND selection', 'Changes screens to screen only.'),
    ('singular cancer cell', 'pooled AND CRISPR AND knockout AND screens AND "cancer cell" AND immune AND selection', 'Changes cancer cells to cancer cell only.'),
    ('tumor-cell wording', 'pooled AND CRISPR AND knockout AND screens AND "tumor cell" AND immune AND selection', 'Tests tumor cell wording independently.'),
    ('coculture', 'pooled AND CRISPR AND knockout AND "cancer cells" AND coculture', 'Tests unhyphenated interaction wording without selection.'),
    ('co-culture', 'pooled AND CRISPR AND knockout AND "cancer cells" AND co-culture', 'Tests hyphenated interaction wording independently.'),
    ('co culture', 'pooled AND CRISPR AND knockout AND "cancer cells" AND "co culture"', 'Tests spaced interaction wording; phrase semantics unresolved.'),
    ('immune killing', 'pooled AND CRISPR AND knockout AND "cancer cells" AND "immune killing"', 'Tests an outcome-oriented description.'),
    ('immune pressure', 'pooled AND CRISPR AND knockout AND "cancer cells" AND "immune pressure"', 'Tests alternative selection-pressure wording.'),
    ('immune selection phrase', 'pooled AND CRISPR AND knockout AND "cancer cells" AND "immune selection"', 'Tests explicit selection phrase without screen wording.'),
]


def build_plan():
    """Return detached accepted data; no clock, file, cache or network reads."""
    queries = []
    for i, (variant, literal, purpose) in enumerate(LITERALS, 1):
        queries.append({'query_id': f'OM3-SQ01-Q{i:02}', 'variant': variant,
            'scientific_question_ids': ['SQ01'], 'intended_query': literal,
            'submitted_query': literal, 'purpose': purpose, 'filters': [], 'sort': None,
            'known_semantic_gaps': ['Quotation is preserved syntax, not proven exact-phrase behavior.',
                'Hyphen handling, tokenization and stemming remain unresolved.',
                'Co-occurrence does not establish cell roles, pooled knockout eligibility or selection causality.']})
    rules = [{'rule_id': q['query_id'].replace('OM3', 'OR3'), 'scientific_question_ids': ['SQ01'],
              'comparison_query_id': q['query_id'], 'purpose': q['purpose'],
              'terms': [term.strip('"') for term in q['intended_query'].split(' AND ')],
              'operation': 'all terms within the same screen, possibly across different allowed fields; case-insensitive bounded literal word/phrase matches'} for q in queries]
    return {'schema_version': 'deathmap-sq01-discovery-plan-v1', 'plan_version': 'sq01-blind-v03.2',
        'run_id': RUN_ID, 'status': 'accepted_for_search_only_after_preflight',
        'authorization_ref': 'docs/specifications/10 SQ01 Blind Discovery Handoff.md',
        'scientific_questions': [{'question_id': 'SQ01', 'question': QUESTION}],
        'resources': [
            {'resource_name': 'OmicsDI', 'query_strategy_id': 'omicsdi-sq01-v03.2',
             'interface': {'endpoint': ENDPOINT, 'method': 'GET', 'detail_requests_enabled': False},
             'queries': queries, 'pagination': {'size': 50, 'initial_offset': 0, 'schedule': 'stable query ID order; exhaust one before next', 'advance': 'actual returned row count'},
             'limits': {'candidate_cap': None, 'page_cap': None, 'runtime_cap': None, 'null_means': 'explicitly uncapped successful pagination', 'detail_requests': 0},
             'request_policy': {'timeout_seconds': 20, 'concurrency': 1, 'minimum_start_interval_seconds': 1,
                 'max_attempts_per_query_offset': 2, 'retry_delay_seconds': 2, 'stop_after_consecutive_failures': 3,
                 'uncertain_requests': 'block without automatic repetition', 'reserve_before_request': True,
                 'checkpoint_replace_attempts': 5, 'retry_after': 'honor service delay up to 60 seconds, otherwise block for review'},
             'resume_policy': 'New SQ01 ledger, no historical offsets/candidates/buffers/allowances. Recover durable receipts offline. Preserve complete raw bytes, duplicate observations, overflow and conflicting identities.'},
            {'resource_name': 'ORCS', 'query_strategy_id': 'orcs-sq01-v03.2',
             'routing': {'trigger': 'case-insensitive CRISPR substring', 'included': 'crispr' in QUESTION.casefold()},
             'index_path': INDEX, 'index_summary_path': INDEX_SUMMARY, 'refresh': False,
             'rules': rules, 'searched_fields': FIELDS.copy(), 'candidate_cap': None, 'network_requests': 0,
             'evidence_roles': {'direct': 'literal rule matches, unreviewed', 'siblings': 'publication context only; parent match references required'},
             'normalization': 'case-insensitive regex comparison; retain exact original values and casefolded comparison forms; no stemming or aliases'}],
        'forbidden_discovery_inputs': ['data/brainstorming/week3_papers_metadata.tsv', 'All local ICRAFT content regardless of location', 'Known-publication identifiers/titles/accessions or expected-publication knowledge'],
        'deferred': ['SQ02', 'CRISPR AND screen AND cancer AND immune', 'detail requests', 'enrichment', 'evaluation comparison', 'scientific classification', 'entity projection', 'Excel', 'experimental data'],
        'preservation': 'V01/v02 immutable; resource observations remain separate; completed native outputs are hash-frozen before any separately authorized evaluation.',
        'semantic_gaps': 'Search variants measure literal wording differences; pagination completes a variant. No accepted-query performance or scientific qualification is assumed.'}


def digest(value):
    """Hash stable JSON, retaining every semantic value and list order."""
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def validate_plan(plan):
    """Reject any difference from this specifically authorized executable plan."""
    if plan != build_plan():
        raise ValueError('Accepted SQ01 semantic plan mismatch; no execution permitted')
    return digest(plan)


def load_plan(root):
    """Read the frozen accepted plan and bind it to the current implementation."""
    plan = json.loads((Path(root)/'outputs'/VERSION/'query_plan.json').read_text(encoding='utf-8'))
    validate_plan(plan)
    return plan
