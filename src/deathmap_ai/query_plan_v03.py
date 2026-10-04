"""Reviewable v03 planning data, independent of every retrieval adapter.

Only the two handoff questions, human-authored literal rules and documented
interface observations enter this configuration. No cache, evaluation file or
historical query configuration is loaded. All execution policies are proposals.
"""

SCHEMA_VERSION = 'deathmap-query-plan-v1'
PLAN_VERSION = 'immune-crispr-coculture-v03.1'
OUTPUT_DIRECTORY = 'outputs/immune-crispr-coculture-v03'

SCIENTIFIC_QUESTIONS = [
    {'question_id': 'SQ01', 'question': 'pooled CRISPR knockout screens in cancer cells under immune selection'},
    {'question_id': 'SQ02', 'question': 'pooled CRISPR knockout screens in immune cells under cancer-cell-mediated selection'},
]

# Explicit IDs survive reordering. A shared query retains both question links;
# its hits could not by themselves establish either perturbation direction.
OMICS_QUERIES = [
    {
        'query_id': 'OM3-Q01', 'scientific_question_ids': ['SQ01'],
        'intended_query': 'pooled AND CRISPR AND knockout AND screens AND "cancer cells" AND immune AND selection',
        'purpose': 'Represent the full SQ01 wording, emphasizing cancer-cell context without asserting the perturbed population.',
        'concepts_represented': ['pooled design', 'CRISPR', 'knockout', 'screening', 'cancer-cell context', 'immune context', 'selection'],
        'known_semantic_gaps': [
            'The cancer-cell phrase does not assign the perturbation to cancer cells or the selection to immune cells.',
            'Requiring every term may miss relevant records with sparse metadata or alternative wording.',
            'Free-text quotation and stemming of screens are unverified; acceptance would not prove phrase semantics.',
        ],
    },
    {
        'query_id': 'OM3-Q02', 'scientific_question_ids': ['SQ02'],
        'intended_query': 'pooled AND CRISPR AND knockout AND screens AND "immune cells" AND cancer AND selection',
        'purpose': 'Represent SQ02 with an immune-cell phrase and cancer/selection terms while exposing the missing causal relationship.',
        'concepts_represented': ['pooled design', 'CRISPR', 'knockout', 'screening', 'immune-cell context', 'cancer context', 'selection'],
        'known_semantic_gaps': [
            'Cancer and selection do not encode cancer-cell-mediated selection; the causal agent remains unknown.',
            'The immune-cell phrase does not establish immune-cell perturbation rather than a co-mentioned population.',
            'Free-text quotation, hyphen handling and plural stemming are unverified; strict terms may reduce retrieval.',
        ],
    },
    {
        'query_id': 'OM3-Q03', 'scientific_question_ids': ['SQ01', 'SQ02'],
        'intended_query': 'CRISPR AND pooled AND knockout AND cancer AND immune',
        'purpose': 'A shared, unquoted alternative relaxing screens, cell phrases and selection when those descriptions are absent.',
        'concepts_represented': ['CRISPR', 'pooled design', 'knockout', 'cancer context', 'immune context'],
        'known_semantic_gaps': [
            'Screening and selection are not explicitly required.',
            'Co-occurring words establish neither an interaction nor which population is perturbed.',
            'No synonym expansion or stemming is assumed; relevant records using other labels may be missed.',
        ],
    },
    {
        'query_id': 'OM3-Q04', 'scientific_question_ids': ['SQ01', 'SQ02'],
        'intended_query': 'CRISPR AND screen AND cancer AND immune',
        'purpose': 'A broader shared alternative for screen descriptions omitting pooled, knockout or selection; explicitly uses singular screen.',
        'concepts_represented': ['CRISPR', 'screening', 'cancer context', 'immune context'],
        'known_semantic_gaps': [
            'Pooling, knockout and selection are not required, so unrelated CRISPR modalities may be retrieved.',
            'Singular screen is an explicit proposed spelling, not evidence that screens stems to screen.',
            'Population roles, cancer-mediated selection and scientific eligibility remain unresolved.',
        ],
    },
]

ORCS_QUERIES = [
    {
        'query_id': 'OR3-Q01', 'scientific_question_ids': ['SQ01'],
        'intended_query': 'ALL_OF(pooled; knockout; cancer cells; immune; selection)',
        'purpose': 'Propose a local SQ01-oriented rule emphasizing the cancer-cell phrase in native screen metadata.',
        'concepts_represented': ['pooled design', 'knockout', 'cancer-cell context', 'immune context', 'selection'],
        'known_semantic_gaps': ['CRISPR scope comes from routing/resource membership, not a qualifying assertion.', 'Terms may appear in different fields and do not bind cell roles; exact phrases and sparse metadata may miss screens.'],
        'matching_terms': ['pooled', 'knockout', 'cancer cells', 'immune', 'selection'],
    },
    {
        'query_id': 'OR3-Q02', 'scientific_question_ids': ['SQ02'],
        'intended_query': 'ALL_OF(pooled; knockout; immune cells; cancer; selection)',
        'purpose': 'Propose an immune-cell-oriented local rule for SQ02 without claiming cancer-mediated causality.',
        'concepts_represented': ['pooled design', 'knockout', 'immune-cell context', 'cancer context', 'selection'],
        'known_semantic_gaps': ['Neither immune-cell perturbation nor cancer-cell-mediated selection follows from co-occurrence.', 'Literal phrases are not synonyms; metadata can omit experimental design terms.'],
        'matching_terms': ['pooled', 'knockout', 'immune cells', 'cancer', 'selection'],
    },
    {
        'query_id': 'OR3-Q03', 'scientific_question_ids': ['SQ01', 'SQ02'],
        'intended_query': 'ALL_OF(cancer; immune)',
        'purpose': 'Propose a broad local context rule retaining screens whose structured metadata omit design details.',
        'concepts_represented': ['cancer context', 'immune context'],
        'known_semantic_gaps': ['No pooling, knockout, selection or direction requirement; false positives and misses are expected.', 'Publication siblings are context only, not direct hits or qualifying screens.'],
        'matching_terms': ['cancer', 'immune'],
    },
]

FORBIDDEN_INPUTS = [
    {'input_id': 'known-publication-evaluation', 'path': 'data/brainstorming/week3_papers_metadata.tsv',
     'restriction': 'Do not read, import, hash identifiers or use contents in planning/discovery. Evaluation only after a separately authorized frozen blind run.'},
    {'input_id': 'icraft', 'path': 'data/icraft/**',
     'restriction': 'All local ICRAFT materials regardless of location: no titles, identifiers, accessions or metadata as discovery inputs or dependencies.'},
]

SOURCE_DOCUMENTATION = [
    {'source_id': 'omicsdi-api-help', 'kind': 'official_documentation', 'url': 'https://www.omicsdi.org/help/api',
     'reviewed_at': '2026-09-27', 'scope': 'Documentation page only; example search links were not followed.'},
    {'source_id': 'v02-interface-observations', 'kind': 'saved_observation_summary', 'path': 'docs/omicsdi/search-information.md',
     'reviewed_at': '2026-09-27', 'observation_date': '2026-09-19', 'scope': 'Interface behavior only; no v02 query or candidate state inherited.'},
    {'source_id': 'v02-field-guide', 'kind': 'saved_schema_observations', 'path': 'docs/field guide/omicsdi/README.md',
     'reviewed_at': '2026-09-27', 'scope': 'Source labels and identity differences; no biological examples used in queries.'},
    {'source_id': 'v02-common-fields', 'kind': 'saved_schema_observations', 'path': 'docs/field guide/omicsdi/common-fields.md',
     'reviewed_at': '2026-09-27', 'scope': 'Identity paths and distinctions between resource objects and scientific entities.'},
    {'source_id': 'v03-handoff', 'kind': 'authorization', 'path': 'docs/specifications/09 V03 Query Planning and Initialization Handoff.md',
     'reviewed_at': '2026-09-27', 'scope': 'Offline planning only; no retrieval authorization.'},
]

INTERFACE_RESEARCH = {
    'boolean_operators': {'status': 'documented_limited', 'finding': 'AND combines filters; other logical operators are described as future work. OR, NOT, grouping and precedence are not assumed.', 'sources': ['omicsdi-api-help']},
    'quotation': {'status': 'unresolved', 'finding': 'Quoted field values are illustrated. Free-text phrase behavior is not established; prior quoted requests returned results without proving phrase matching.', 'sources': ['omicsdi-api-help', 'v02-interface-observations']},
    'tokenization_stemming': {'status': 'undocumented', 'finding': 'No tokenizer, stemming or hyphen equivalence is assumed.', 'sources': ['omicsdi-api-help', 'v02-interface-observations']},
    'fielded_filters': {'status': 'documented_with_inconsistencies', 'fields': ['repository', 'omics_type', 'TAXONOMY', 'tissue', 'disease', 'modification', 'instrument_platform', 'publication_date', 'technology_type'], 'syntax': 'Fielded terms inside query, combined with AND.', 'sources': ['omicsdi-api-help']},
    'repository_omics_filters': {'status': 'documented_not_used', 'finding': 'repository and omics_type are fielded terms; documented display labels are not presumed identical to native identity labels.', 'sources': ['omicsdi-api-help', 'v02-field-guide']},
    'sort': {'status': 'documented_options_unknown_default', 'options': ['title', 'description', 'publication_date', 'id', 'relevance'], 'finding': 'sort_field is illustrated; omitted-sort ordering and tie-break stability are unspecified. No sort is proposed; preserve native order and flag pagination drift.', 'sources': ['omicsdi-api-help', 'v02-interface-observations']},
    'pagination': {'status': 'documented_and_observed', 'maximum_size': 100, 'documented_default_size': 20, 'documented_default_start': 0, 'finding': 'start is a zero-based offset; size bounds a page. Prior mixed-date counts changed, so offset exhaustion is not a fresh-snapshot completeness claim.', 'sources': ['omicsdi-api-help', 'v02-interface-observations']},
    'identity': {'status': 'observed', 'search_fields': ['source', 'id'], 'detail_fields': ['database', 'accession'], 'finding': 'Keep original pairs. Detail repository labels may conflict with requested labels; retain uncertainty without alias merging.', 'sources': ['v02-common-fields', 'v02-field-guide']},
    'documentation_discrepancies': {'status': 'documented_inconsistency_and_observed_variation', 'finding': 'Version examples reuse /ws/; no pinned server version is inferred. Disease examples use tissue; modification prose and examples disagree. Detail identity shapes differ from search. No v03 acceptance testing performed.', 'sources': ['omicsdi-api-help', 'v02-common-fields']},
    'service_quota': {'status': 'unknown', 'requests_per_second': None, 'finding': 'No numeric service quota established by reviewed help. Proposed pacing is a client limit, not a service entitlement.', 'sources': ['omicsdi-api-help']},
}

PRESERVATION_RULES = [
    {'rule_id': 'historical-immutable', 'rule': 'Do not alter v01/v02 outputs, receipts, hashes or historical excess-detail accounting.'},
    {'rule_id': 'separate-observations', 'rule': 'OmicsDI and ORCS observations remain independent, including duplicate observations and native identities.'},
    {'rule_id': 'raw-and-conflicts', 'rule': 'Future authorized retrieval preserves complete raw responses, overflow buffers, original fields, conflicts and uncertain requests.'},
    {'rule_id': 'no-historical-ledger-inheritance', 'rule': 'A future authorized v03 ledger starts separately; never reset or borrow v01/v02 offsets, candidates or attempt allowances.'},
    {'rule_id': 'planning-only-files', 'rule': 'This slice writes only query_plan.json in the v03 planning directory; no candidate, hit, detail, raw, entity or attempt ledger artifacts.'},
]

REVIEW_GATES = [
    {'gate_id': 'query-family', 'status': 'pending', 'decision': 'Review exact OmicsDI queries and ORCS local matching rules, including strict versus broad alternatives and semantic gaps.'},
    {'gate_id': 'limits-and-ordering', 'status': 'pending', 'decision': 'Set candidate, detail and search-request caps; approve timeout, retry, pacing, filters, ordering and new-ledger rules.'},
    {'gate_id': 'live-authorization', 'status': 'pending', 'decision': 'Freeze an accepted version and separately authorize/implement live discovery. This planner cannot execute it.'},
]

RESOURCE_POLICIES = [
    {
        'resource_name': 'OmicsDI', 'resource_role': 'primary cross-repository discovery, proposed only',
        'interface': {'kind': 'REST_metadata_proposal', 'search_endpoint': 'https://www.omicsdi.org/ws/dataset/search', 'query_parameter': 'query', 'server_version': None, 'live_enabled': False},
        'query_strategy_id': 'omicsdi-questions-v03.1',
        'pagination': {'status': 'proposed_not_authorized', 'start': 0, 'size': 50, 'documented_maximum_size': 100, 'schedule': 'round-robin queries; preserve returned native order', 'offset_rule': 'Advance by actual returned rows; retain complete raw pages and unadmitted overflow.'},
        'limits': {'status': 'proposed_not_authorized', 'candidate_cap': None, 'detail_attempt_cap': None, 'search_request_cap': None, 'unset_caps_mean': 'pending project-owner decision, not unlimited', 'request_timeout_seconds': 20, 'concurrent_requests': 1, 'total_runtime_seconds': None, 'total_runtime_meaning': 'proposal: no total budget; bounded requests and explicit stop conditions'},
        'retry_policy': {'status': 'proposed_not_authorized', 'search_attempts_per_query_offset': 2, 'detail_attempts_per_native_key': 1, 'retry_delay_seconds': 2, 'accounting': 'Cumulative within the future v03 ledger; received, failed and uncertain reservations consume detail capacity independently of parsing.', 'reserve_before_request': True, 'repeat_uncertain_automatically': False},
        'rate_limit_policy': {'status': 'proposed_not_authorized', 'minimum_request_interval_seconds': 1, 'published_service_quota': None, 'honor_retry_after': True, 'rule': 'Use the stricter of client pacing, Retry-After and applicable service guidance; never claim a service entitlement.'},
        'stop_conditions': ['No approved plan and separate live authorization: no requests.', 'Future approved candidate/detail/search-request allowance reached: stop affected retrieval.', 'Every query exhausted or blocked; preserve pagination and overflow.', 'Three consecutive failed operations: stop invocation rather than retry indefinitely.', 'Persistent throttling, unrecognized schema, identity uncertainty or checkpoint failure: preserve evidence and stop affected work for review.'],
        'resume_policy': {'ledger_version': 'omicsdi-attempt-ledger-v03-proposed', 'new_ledger_required': True, 'reuse_v01_v02_state': False, 'ledger_created_in_this_slice': False, 'identity_fields': {'search': ['source', 'id'], 'detail': ['database', 'accession']}, 'state_to_preserve': ['approved plan semantic digest', 'query IDs and offsets', 'buffered unadmitted rows', 'native repository/identifier pairs', 'duplicate query observations', 'attempt reservations and outcomes', 'raw response references and original dates', 'conflicts and uncertainties'], 'rule': 'Only a separately authorized future executor may create/resume this ledger; uncertain requests are not repeated and historical allowances are never reset.'},
    },
    {
        'resource_name': 'ORCS', 'resource_role': 'complementary native screen/publication discovery, proposed only',
        'interface': {'kind': 'local_complete_cached_index_proposal', 'index_path': 'outputs/orcs/cache/legacy/20260904T213941Z/orcs-screens.raw.json', 'index_loaded_as_discovery_input': False, 'refresh_authorized': False, 'live_enabled': False},
        'query_strategy_id': 'orcs-questions-v03.1',
        'pagination': {'status': 'not_applicable', 'start': None, 'size': None, 'rule': 'A future approved pass searches the complete existing cached index in native order.'},
        'limits': {'status': 'local_search_proposal_not_executed', 'candidate_cap': None, 'candidate_cap_meaning': 'No fixed cap for complete cached-index search.', 'network_requests': 0, 'request_timeout_seconds': None, 'total_runtime_seconds': None},
        'retry_policy': {'status': 'not_applicable', 'network_attempts': 0, 'rule': 'No network retries or refresh; missing/corrupt cache stops a future pass.'},
        'rate_limit_policy': {'status': 'not_applicable', 'network_requests_per_second': 0},
        'stop_conditions': ['Proposed matching rules require review before local execution.', 'Complete cached index examined in a future authorized pass.', 'Missing/corrupt cache or unrecognized native schema: stop without refresh.'],
        'resume_policy': {'status': 'proposed_local_only', 'reuse_v01_v02_results': False, 'rule': 'Future local results use a separate v03 manifest tied to the accepted plan and unchanged index hash; never overwrite v01/v02 outputs.'},
        'evidence_roles': {'direct_matches': 'Preserve native screen metadata and every matching field; a match is not scientific qualification.', 'publication_siblings': 'Preserve as contextual records with explicit parent match references, never relabel as direct hits or qualifying screens.'},
    },
]
