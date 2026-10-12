"""Run one resumable, metadata-only ArrayExpress enrichment of saved ORCS.

This command-line module owns retrieval, native evidence and workbook projection.
Saved publication identifiers nominate studies; native collection membership is
checked before inclusion. Study associations are not exact screen attribution.
Only explicitly listed IDF/SDRF descriptive files are fetched, never experimental
contents. Existing source databases and owner templates remain unchanged.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import platform
import shutil
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, quote, urlencode, urlsplit
from urllib.request import Request, urlopen

from .arrayexpress_enrichment import API, _phrase, walk_metadata
from .arrayexpress_europepmc import ANNOTATIONS, annotation_candidates

STRATEGY = 'arrayexpress-orcs-metadata-v2'


def _now():
    return datetime.now(timezone.utc).isoformat()


def _load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def _save(path, value):
    # A temporary sibling prevents interruption from corrupting completed state.
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


def _key(url):
    p = urlsplit(url)
    return p.netloc, p.path, tuple(sorted(parse_qsl(p.query)))


class Transport:
    """Preserve serial HTTP responses and reuse exact, hash-verified requests.

    Parameters
    ----------
    folder : Path
        Run directory with raw bytes and request receipts.
    cache_roots : list of Path
        Explicit saved metadata locations; no cache content becomes query input.
    opener : callable
        HTTP opener, injectable for offline tests.

    Notes
    -----
    Limits are client checkpoints: 5,000 attempts, three hours of live retrieval,
    10 MiB per response, 2 GiB total. Starts are serial and spaced one second.
    Successful cache reuse retains original retrieval dates and adds reuse dates.
    """
    def __init__(self, folder, cache_roots=(), opener=urlopen):
        self.folder, self.opener = Path(folder), opener
        (self.folder / 'raw').mkdir(exist_ok=True)
        self.receipts = _load(self.folder / 'requests.json') if (self.folder / 'requests.json').exists() else []
        self.cache = {}
        self.started, self.last = time.monotonic(), 0.
        self.live_attempts = sum(not r.get('reused_from') for r in self.receipts)
        self.total = sum(r.get('bytes', 0) for r in self.receipts)
        paths = []
        for root in cache_roots:
            if root.exists():
                paths.extend(sorted(root.rglob('requests.json')))
        paths.append(self.folder / 'requests.json')
        for path in paths:
            if not path.exists():
                continue
            for r in _load(path):
                if r.get('file') and r.get('sha256') and not r.get('error') and not r.get('incomplete'):
                    self.cache[_key(r['url'])] = (path.parent / r['file'], r)

    def get(self, url):
        """Return response bytes and a run-relative source, preserving failures.

        Parameters
        ----------
        url : str
            Fully encoded metadata endpoint or allowlisted metadata-file URL.

        Returns
        -------
        tuple
            Native bytes and relative raw-response filename.

        Raises
        ------
        RuntimeError
            Operational checkpoint or mismatched cache hash.
        HTTPError, URLError, TimeoutError
            Unrecoverable or repeated network failure; receipts are retained.
        """
        cached = self.cache.get(_key(url))
        if cached:
            path, old = cached
            body = path.read_bytes()
            if hashlib.sha256(body).hexdigest() != old['sha256']:
                raise RuntimeError('Cached native response hash mismatch: ' + str(path))
            name = f'raw/{len(self.receipts)+1:05d}.response'
            (self.folder / name).write_bytes(body)
            receipt = {**old, 'url': url, 'file': name, 'bytes': len(body),
                       'reused_from': str(path), 'reused_utc': _now()}
            self.receipts.append(receipt)
            self.total += len(body)
            _save(self.folder / 'requests.json', self.receipts)
            return body, name
        for attempt in (1, 2):
            if self.live_attempts >= 5000 or time.monotonic()-self.started >= 10800 or self.total >= 2*1024**3:
                raise RuntimeError('Full-run attempt/time/byte checkpoint reached')
            time.sleep(max(0., 1.-(time.monotonic()-self.last)))
            self.last = time.monotonic()
            self.live_attempts += 1
            receipt = {'url': url, 'attempt': attempt, 'retrieved_utc': _now()}
            self.receipts.append(receipt)
            try:
                request = Request(url, headers={'User-Agent':'DeathMap-AI/0.1 ArrayExpress metadata',
                    'Accept':'application/json' if '/api/' in url or '/annotations_api/' in url else 'text/plain'})
                with self.opener(request, timeout=30) as response:
                    body = response.read(10*1024**2+1)
                    receipt.update(http_status=response.status, content_type=response.headers.get('Content-Type'))
                name = f'raw/{len(self.receipts):05d}.response'
                (self.folder / name).write_bytes(body)
                self.total += len(body)
                receipt.update(file=name, bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
                if len(body) > 10*1024**2:
                    receipt['incomplete'] = True
                    raise RuntimeError('Ten-MiB response checkpoint reached')
                self.cache[_key(url)] = (self.folder / name, dict(receipt))
                return body, name
            except (HTTPError, URLError, TimeoutError) as error:
                receipt['error'] = str(error)
                retry = not isinstance(error, HTTPError) or error.code in (408, 429) or error.code >= 500
                if not retry or attempt == 2:
                    raise
                delay = 5
                if isinstance(error, HTTPError) and error.headers.get('Retry-After'):
                    header = error.headers['Retry-After']
                    if not header.isdigit() or int(header) > 60:
                        raise RuntimeError('Retry-After requires a checkpoint') from error
                    delay = max(delay, int(header))
                time.sleep(delay)
            finally:
                _save(self.folder / 'requests.json', self.receipts)


def discovery_routes(publication):
    """Build retained routes from publication fields, never validation accessions.

    Parameters
    ----------
    publication : dict
        Saved ORCS record with optional DOI/PMID and complete TITLE.

    Returns
    -------
    list
        Route name and exact encoded URL. Missing IDs omit their routes.
    """
    routes = []
    if publication.get('DOI'):
        params = {'link_type':'doi','link_value':_phrase(publication['DOI']), 'pagination':'cursor','pageSize':100}
        routes.append(('native_quoted_doi', API+'ArrayExpress/search?'+urlencode(params)))
    if publication.get('TITLE'):
        params = {'query':_phrase(publication['TITLE']), 'pagination':'cursor','pageSize':100}
        routes.append(('native_complete_title', API+'ArrayExpress/search?'+urlencode(params)))
    if publication.get('PMID'):
        routes.append(('europepmc_annotations', ANNOTATIONS+'?'+urlencode({
            'articleIds':'MED:'+str(publication['PMID']), 'type':'Accession Numbers','format':'JSON'})))
    return routes


def _discover(get, route, url, publication):
    observations, seen = [], set()
    for page in range(10):
        body, source = get(url)
        native = json.loads(body)
        if route == 'europepmc_annotations':
            observations = annotation_candidates(native, str(publication['PMID']))
            for o in observations:
                o.update(source=source, route=route)
            return observations
        if not isinstance(native.get('hits'), list) or 'nextCursor' not in native:
            raise ValueError('Incomplete native search schema')
        if native.get('expandedSynonyms') or native.get('expandedEfoTerms'):
            raise ValueError('Unexpected native query expansion')
        for rank, hit in enumerate(native['hits']):
            if not hit.get('accession') or hit.get('type') != 'study':
                raise ValueError('Invalid native study identity')
            observations.append({'accession':hit['accession'],'source':source,
                'locator':f'$.hits[{rank}]','route':route,'page':page+1,
                'evidence_kind':'native_search_candidate','native':hit})
        if len({o['accession'] for o in observations}) > 100:
            raise RuntimeError('One-hundred-study publication checkpoint reached')
        cursor = native['nextCursor']
        if cursor is None:
            return observations
        if not isinstance(cursor,str) or not cursor or cursor in seen:
            raise ValueError('Repeated/invalid cursor')
        seen.add(cursor)
        p = urlsplit(url)
        params = dict(parse_qsl(p.query)); params.pop('pagination',None); params['cursor']=cursor
        url = p._replace(query=urlencode(params)).geturl()
    raise RuntimeError('Ten-page route checkpoint reached')


def parse_metadata_file(body, kind):
    """Parse UTF-8 MAGE-TAB without collapsing duplicate columns or records.

    Parameters
    ----------
    body : bytes
        Native descriptive file, not an experimental matrix.
    kind : str
        idf or sdrf, determined from the native file listing.

    Returns
    -------
    list of list of str
        Ordered rows, retaining repeated headers and empty fields.

    Raises
    ------
    ValueError
        Markup, empty file or inconsistent SDRF row width.
    UnicodeDecodeError
        Undecodable native text; bytes remain saved for inspection.
    """
    text = body.decode('utf-8-sig')
    if text.lstrip().startswith('<'):
        raise ValueError('Metadata file returned markup')
    rows = list(csv.reader(io.StringIO(text), delimiter='\t'))
    if not rows:
        raise ValueError('Empty metadata file')
    if kind == 'sdrf' and any(row and len(row)!=len(rows[0]) for row in rows[1:]):
        raise ValueError('Inconsistent SDRF row width')
    return rows


def _study(get, accession):
    body, source = get(API+'studies/'+quote(accession,safe=''))
    native = json.loads(body)
    if native.get('accno') != accession:
        raise ValueError('Native study identity mismatch')
    members = [a.get('value') for a in native.get('attributes',[]) if a.get('name')=='AttachTo']
    record = {'accession':accession,'source':source,'native':native,
              'arrayexpress_membership_confirmed':'ArrayExpress' in members,
              'metadata_files':[],'issues':[]}
    if not record['arrayexpress_membership_confirmed']:
        return record
    chosen = {}
    for locator, file in walk_metadata(native):
        if file.get('type')!='file' or not file.get('path'):
            continue
        path = file['path']
        kind = next((k for k in ('idf','sdrf') if path.lower().endswith('.'+k+'.txt')),None)
        if not kind:
            continue
        declaration = json.dumps(file.get('attributes',[])).lower()
        if kind not in declaration or path.startswith('/') or '..' in path.split('/') or '://' in path:
            record['issues'].append({'kind':kind,'error':'Unsafe/undeclared metadata listing','locator':locator})
            continue
        if kind in chosen:
            chosen[kind] = None
            record['issues'].append({'kind':kind,'error':'Multiple native files require review'})
        else:
            chosen[kind] = (path,locator)
    for kind, entry in chosen.items():
        if entry is None:
            continue
        path, locator = entry
        url = 'https://www.ebi.ac.uk/biostudies/files/'+quote(accession,safe='')+'/'+quote(path,safe='/')
        try:
            body, source = get(url)
            rows = parse_metadata_file(body,kind)
            record['metadata_files'].append({'kind':kind,'source':source,'listing_locator':locator,'rows':rows})
        except Exception as error:
            record['issues'].append({'kind':kind,'url':url,'error':str(error)})
    return record


def project(database):
    """Project owner-selected display records while preserving native evidence.

    Parameters
    ----------
    database : dict
        Completed/partial publications, association observations and native studies.

    Returns
    -------
    dict
        Eight tables keyed by accepted sheet names, containing header-keyed rows.

    Notes
    -----
    One native attribute is one row; long values are kept whole. SDRF is long
    form, retaining native row and column indices. Neither SDRF rows nor native
    sample summaries are automatically distinct screens. No truncation occurs.
    """
    tables = {n:[] for n in ['Studies','Repository citations','Protocols','Sample metadata',
        'Assay metadata','File listings','SDRF metadata','IDF metadata']}
    memberships = {}
    for p in database['publications']:
        for a in sorted({o['accession'] for o in p['observations']}):
            memberships.setdefault(a,[]).append(p)
    def join(attrs,name):
        return '; '.join(str(a['value']) for a in attrs if a.get('name')==name and a.get('value') is not None)
    for accession, study in sorted(database['studies'].items()):
        if not study.get('arrayexpress_membership_confirmed'):
            continue
        native=study['native']; attrs=native.get('section',{}).get('attributes',[])
        allattrs=[node for _,node in walk_metadata(native) if 'name' in node and 'value' in node]
        linked=memberships.get(accession,[])
        pmids=sorted({str(p['publication'].get('PMID')) for p in linked if p['publication'].get('PMID')},key=int)
        kinds=sorted({o['evidence_kind'] for p in linked for o in p['observations'] if o['accession']==accession})
        def number(name):
            values={str(a['value']) for a in allattrs if a.get('name')==name and str(a.get('value','')).isdigit()}
            return int(next(iter(values))) if len(values)==1 else None
        tables['Studies'].append({'Study accession':accession,'PMID':'; '.join(pmids),
            'Study title':join(attrs,'Title'),'Organism':join(attrs,'Organism'),'Study type':join(attrs,'Study type'),
            'Samples reported':number('Sample count'),'Assays reported':number('Assay count'),
            'Study description':join(attrs,'Description'),'Publication association':'; '.join(kinds),
            'Source URL':API+'studies/'+accession})
        def walk(value,context='submission'):
            if isinstance(value,list):
                for item in value:walk(item,context)
            elif isinstance(value,dict):
                section=value.get('type',context)
                attributes=value.get('attributes',[])
                if value.get('type')=='Publication':
                    tables['Repository citations'].append({'Study accession':accession,
                        'Native citation title':join(attributes,'Title'),'Native DOI':join(attributes,'DOI'),
                        'Native PMID':join(attributes,'PubMed ID') or join(attributes,'PMID'),
                        'Native authors':join(attributes,'Authors'),'Native status':join(attributes,'Status'),
                        'Source URL':API+'studies/'+accession})
                target=None
                if value.get('type')=='Protocols':target='Protocols'
                elif value.get('type') in ('Samples','Experimental Factors','Factors Table','Source Characteristics','Characteristics Table'):target='Sample metadata'
                elif value.get('type') in ('Assays and Data','Raw Data','Processed Data','Additional Files','MAGE-TAB Files'):target='Assay metadata'
                if target:
                    for a in attributes:
                        row={'Study accession':accession,'Field':a.get('name',''),'Original value':a.get('value',''),
                             'Value state':'Not supplied' if 'value' not in a else 'Reported empty' if a['value']=='' else 'Reported'}
                        if target=='Protocols':row['Native protocol ID']=value.get('accno') or join(attributes,'Name')
                        else:row.update({'Native section type':section,'Native section ID':value.get('accno','')})
                        tables[target].append(row)
                if value.get('type')=='file' and value.get('path'):
                    tables['File listings'].append({'Study accession':accession,'Native section type':context,
                        'File path':value['path'],'Size (bytes)':value.get('size'),'Declared type':join(attributes,'Type'),
                        'Format':join(attributes,'Format'),'Description':join(attributes,'Description')})
                for v in value.values():
                    if isinstance(v,(dict,list)):walk(v,section)
        walk(native)
        for file in study['metadata_files']:
            rows=file['rows']
            if file['kind']=='sdrf':
                for r,row in enumerate(rows[1:],1):
                    for c,value in enumerate(row,1):
                        tables['SDRF metadata'].append({'Study accession':accession,'Source name':row[0],
                            'Native data row':r,'Native column':c,'Native field':rows[0][c-1],
                            'Original value':value,'Part':1})
            else:
                for r,row in enumerate(rows,1):
                    for c,value in enumerate(row[1:],2):
                        tables['IDF metadata'].append({'Study accession':accession,'Native line':r,
                            'Native column':c,'Native field':row[0],'Original value':value})
    return tables


def run(index, folder, cache_roots=(), resume=False):
    """Enrich every saved publication once with per-route failure accounting.

    Parameters
    ----------
    index : Path
        Existing ORCS publication index; no benchmark accessions accepted.
    folder : Path
        Fresh output directory, or the same checkpoint with resume=True.
    cache_roots : list of Path
        Saved native response locations for exact request reuse.
    resume : bool
        Continue incomplete work after validating input and executed code hashes.

    Returns
    -------
    dict
        Canonical publication/study records, issues and workbook projection.

    Raises
    ------
    ValueError
        Changed checkpoint input or code.
    FileExistsError
        Existing directory without explicit resume.

    Notes
    -----
    Network requests and new run files are side effects. Individual failures do
    not masquerade as no results and do not prevent processing other publications.
    """
    index,folder=Path(index),Path(folder)
    payload=index.read_bytes(); publications=json.loads(payload)
    code_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    identity={'input_sha256':hashlib.sha256(payload).hexdigest(),'source_code_sha256':code_hash}
    if resume:
        database=_load(folder/'database.json')
        if any(database[k]!=v for k,v in identity.items()):raise ValueError('Changed resume input/code')
    else:
        folder.mkdir(parents=True,exist_ok=False)
        database={'strategy':STRATEGY,**identity,'input_path':str(index.resolve()),'created_utc':_now(),
            'python_version':platform.python_version(),'interface':'BioStudies API v1; Europe PMC annotations',
            'status':'running','publications':[],'studies':{},'study_failures':{},'issues':[],
            'limits':{'live_attempts':5000,'elapsed_seconds':10800,'response_bytes':10*1024**2,
                      'total_bytes':2*1024**3,'studies_per_route':100,'pages_per_route':10,'start_interval_seconds':1}}
        shutil.copyfile(__file__,folder/'executed-collection.py')
    transport=Transport(folder,cache_roots)
    existing={p['publication']['PUBLICATION_ID']:p for p in database['publications']}
    for number,publication in enumerate(publications,1):
        key=publication['PUBLICATION_ID']
        if key in existing:continue
        result={'publication':publication,'input_locator':'PUBLICATION_ID='+key,'routes':[], 'observations':[]}
        for route,url in discovery_routes(publication):
            state={'route':route,'url':url}
            try:
                observations=_discover(transport.get,route,url,publication)
                result['observations'].extend(observations)
                state.update(status='complete' if observations else 'no_results',
                             accessions=sorted({o['accession'] for o in observations}))
            except Exception as error:
                state.update(status='incomplete',error=str(error))
            result['routes'].append(state)
        result['status']='incomplete' if any(r['status']=='incomplete' for r in result['routes']) else 'complete'
        if not publication.get('PMID'):
            result['routes'].append({'route':'europepmc_annotations','status':'skipped_missing_identifier'})
        database['publications'].append(result)
        _save(folder/'database.json',database)
        print(json.dumps({'stage':'publications','processed':number,'total':len(publications),
            'publications_with_candidates':sum(bool(p['observations']) for p in database['publications']),
            'distinct_candidates':len({o['accession'] for p in database['publications'] for o in p['observations']}),
            'live_attempts':transport.live_attempts,'incomplete_publications':sum(p['status']=='incomplete' for p in database['publications'])}),flush=True)
    candidates=sorted({o['accession'] for p in database['publications'] for o in p['observations']})
    for number,accession in enumerate(candidates,1):
        if accession in database['studies'] or accession in database['study_failures']:continue
        try:database['studies'][accession]=_study(transport.get,accession)
        except Exception as error:database['study_failures'][accession]={'error':str(error)}
        _save(folder/'database.json',database)
        print(json.dumps({'stage':'studies','processed':number,'total':len(candidates),
                          'metadata_files':sum(len(s['metadata_files']) for s in database['studies'].values()),
                          'failed_studies':len(database['study_failures'])}),flush=True)
    database['rows']=project(database)
    database['finished_utc']=_now()
    incomplete=sum(p['status']=='incomplete' for p in database['publications'])
    file_issues=sum(len(s['issues']) for s in database['studies'].values())
    database['status']='complete_with_issues' if incomplete or database['study_failures'] or file_issues else 'complete'
    routes=Counter();counts={}
    for p in database['publications']:
        for r in p['routes']:routes[(r['route'],r['status'])]+=1
        for o in p['observations']:counts.setdefault(o['route'],set()).add(o['accession'])
    database['summary']={'publications_processed':len(database['publications']),
        'publications_with_candidates':sum(bool(p['observations']) for p in database['publications']),
        'candidate_accessions':len(candidates),'arrayexpress_studies':len(database['rows']['Studies']),
        'publication_study_associations':sum(len({o['accession'] for o in p['observations'] if o['accession'] in database['studies'] and database['studies'][o['accession']].get('arrayexpress_membership_confirmed')}) for p in database['publications']),
        'incomplete_publications':incomplete,'failed_studies':len(database['study_failures']),
        'metadata_file_issues':file_issues,'metadata_files':sum(len(s['metadata_files']) for s in database['studies'].values()),
        'route_states':[{'route':k[0],'status':k[1],'publications':v} for k,v in sorted(routes.items())],
        'distinct_candidates_by_route':{k:len(v) for k,v in counts.items()},
        'sheet_rows':{k:len(v) for k,v in database['rows'].items()},'live_attempts':transport.live_attempts,
        'cached_responses':sum(bool(r.get('reused_from')) for r in transport.receipts)}
    _save(folder/'database.json',database);_save(folder/'summary.json',database['summary'])
    print(json.dumps(database['summary']),flush=True)
    return database


def main():
    """Parse the explicit index, new run directory and optional same-run resume."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publication-index',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--cache-root',type=Path,action='append',default=[])
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args()
    run(args.publication_index,args.output_dir,args.cache_root,args.resume)


if __name__=='__main__':main()
