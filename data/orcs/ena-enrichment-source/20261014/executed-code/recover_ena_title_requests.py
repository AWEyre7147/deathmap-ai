"""Recover only failed complete-title searches in an existing ENA metadata run.

No full discovery is repeated. Portal TSV avoids malformed JSON; EBI quoted
complete-title search is a fallback for rejected quote syntax. Original failures
and responses are preserved as resolved issues. Newly found study metadata is
fetched only when its native accession has not already been resolved.
"""
import argparse
import csv
import io
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlencode
from deathmap_ai.ena_collection import API, REPORT_FIELDS, STUDY_ID, Transport, _load, _phrase, _save, _now, parse_study
from deathmap_ai.ena_projection import project


def recover(folder):
    """Recover up to ten failed title requests and refresh only saved projections.

    Parameters
    ----------
    folder : Path
        Existing completed run directory; original discovery issues are retained.

    Returns
    -------
    dict
        Recovery observations, unresolved failures and resulting metadata counts.

    Raises
    ------
    ValueError
        There are more than ten failed requests or a response schema is invalid.
    """
    folder = Path(folder)
    database = _load(folder / 'database.json')
    failures = [(pub, issue) for pub in database['publications'] for issue in pub['issues'] if issue['route'] == 'complete-title']
    if len(failures) > 10:
        raise ValueError('More than ten failed title requests; checkpoint required')
    transport = Transport(folder)
    aliases = {alias: accession for accession, s in database['studies'].items() for alias in s['aliases']}
    recovery = [{'publication_key': pub['key'], 'status': 'recovered',
                 'attempts': issue['recovery_attempts']} for pub in database['publications']
                for issue in pub.get('resolved_issues', []) if issue['route'] == 'complete-title']
    for pub, original in failures:
        title = pub['publication']['TITLE']
        attempts = []
        rows, receipt = None, None
        query = {'result': 'study', 'query': 'study_title=' + _phrase(title), 'format': 'tsv', 'fields': 'study_accession,study_title', 'limit': 1000}
        try:
            body, receipt = transport.get(API + 'portal/api/search?' + urlencode(query))
            reader = csv.DictReader(io.StringIO(body.decode('utf-8')), delimiter='\t')
            if 'study_accession' not in (reader.fieldnames or []):
                raise ValueError('Invalid Portal TSV header')
            rows = list(reader)
            if len(rows) >= 1000:
                raise ValueError('Recovery hit cap reached')
            attempts.append({'interface': 'Portal TSV', 'status': 'complete', 'response': receipt['file']})
        except Exception as error:
            attempts.append({'interface': 'Portal TSV', 'error': str(error)})
        if rows is None:
            url = 'https://www.ebi.ac.uk/ebisearch/ws/rest/sra-study?' + urlencode({'query': _phrase(title), 'format': 'json', 'fields': 'acc,study_title,PUBMED', 'size': 100})
            try:
                body, receipt = transport.get(url)
                native = json.loads(body)
                if 'hitCount' not in native or native['hitCount'] > len(native.get('entries', [])):
                    raise ValueError('Incomplete or invalid EBI title result')
                rows = [dict(row, study_accession=row['id']) for row in native.get('entries', [])]
                attempts.append({'interface': 'EBI complete quoted title', 'status': 'complete', 'response': receipt['file']})
            except Exception as error:
                attempts.append({'interface': 'EBI complete quoted title', 'error': str(error)})
        if rows is None:
            recovery.append({'publication_key': pub['key'], 'status': 'unresolved', 'attempts': attempts})
            continue
        for index, row in enumerate(rows):
            seed = row['study_accession']
            if not STUDY_ID.fullmatch(seed):
                raise ValueError('Invalid title-recovery study accession')
            observation = {'accession': seed, 'route': 'complete-title', 'evidence': {'response': receipt['file'], 'row': index, 'native_record': row, 'recovery_interface': attempts[-1]['interface']}}
            pub['observations'].append(observation)
            if seed not in aliases:
                body, native_receipt = transport.get(API + 'browser/api/xml/' + seed)
                study = parse_study(body)
                if seed not in study['aliases']:
                    raise ValueError('Recovery study alias mismatch')
                accession = study['accession']
                if accession not in database['studies']:
                    study.update(source_response=native_receipt['file'], source_url=native_receipt['url'], source_sha256=native_receipt['sha256'], associations=[])
                    body, report_receipt = transport.get(API + 'portal/api/filereport?' + urlencode({'accession': accession, 'result': 'read_run', 'fields': ','.join(REPORT_FIELDS), 'format': 'tsv'}))
                    reader = csv.DictReader(io.StringIO(body.decode('utf-8')), delimiter='\t')
                    if not set(REPORT_FIELDS) <= set(reader.fieldnames or []):
                        raise ValueError('Recovery run report header mismatch')
                    runs = list(reader)
                    study.update(runs=runs, run_report_response=report_receipt['file'], run_report_url=report_receipt['url'], run_report_status='complete',
                        run_count=len({r['run_accession'] for r in runs}), sample_count=len({r['sample_accession'] for r in runs}), experiment_count=len({r['experiment_accession'] for r in runs}))
                    database['studies'][accession] = study
                aliases.update({a: accession for a in study['aliases']})
            study = database['studies'][aliases[seed]]
            pmid = pub['publication'].get('PMID')
            status = 'search-pmid-unavailable' if not pmid else 'native-pmid-match' if pmid in study['pmids'] else 'native-pmid-differs' if study['pmids'] else 'no-native-pmid'
            study['associations'].append(dict(observation, publication_key=pub['key'], search_pmid=pmid, publication_association=status, screen_attribution='unassessed'))
        pub['issues'].remove(original)
        pub.setdefault('resolved_issues', []).append(dict(original, recovery_attempts=attempts))
        pub['routes'].append({'route': 'complete-title', 'status': 'recovered', 'hits': len(rows), 'requests': attempts})
        pub['status'] = 'complete_with_issues' if pub['issues'] else 'complete'
        recovery.append({'publication_key': pub['key'], 'status': 'recovered', 'hits': len(rows), 'attempts': attempts})
        _save(folder / 'database.json', database)
        print(json.dumps(recovery[-1]), flush=True)
    database['rows'] = project(database)
    route_sets = {}
    pairs = {}
    for accession, study in database['studies'].items():
        for a in study['associations']:
            pair = a['publication_key'], accession
            route_sets.setdefault(a['route'], set()).add(pair)
            pairs[pair] = a['publication_association']
    non_title = set().union(*(v for k, v in route_sets.items() if k != 'complete-title'))
    summary = database.setdefault('summary', {'publications_processed': len(database['publications']),
        'failed_study_accessions': len(database['study_failures']), 'run_report_issues': len(database['issues'])})
    summary.update(studies=len(database['studies']), publications_with_candidates=len({p[0] for p in pairs}), association_pairs=len(pairs),
        route_counts={k: {'studies': len({p[1] for p in v}), 'publication_study_pairs': len(v)} for k, v in route_sets.items()},
        title_only_pairs=sorted(route_sets.get('complete-title', set()) - non_title),
        association_status_counts=dict(Counter(pairs.values())), discovery_issues=sum(len(p['issues']) for p in database['publications']),
        sheet_rows={k: len(v) for k, v in database['rows'].items()}, distinct_runs=len({r['run_accession'] for s in database['studies'].values() for r in s['runs']}),
        live_attempts=transport.attempts, cached_responses=sum(bool(r.get('reused_from')) for r in transport.receipts))
    pending = any(s.get('run_report_status', '').startswith('pending-') for s in database['studies'].values())
    database['status'] = ('pending-size-checkpoint' if pending else 'complete_with_issues'
                          if database['study_failures'] or database['issues'] or summary['discovery_issues'] else 'complete')
    database['finished_utc'] = _now()
    _save(folder / 'database.json', database)
    _save(folder / 'summary.json', summary)
    _save(folder / 'title-recovery.json', recovery)
    return recovery


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    print(json.dumps(recover(parser.parse_args().run)))
