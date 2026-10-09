"""Resolve DOI/PMID/PMCID mappings without title matching or article downloads.

Inputs are publication dictionaries with any of doi, pmid and pmcid. Exact
NCBI mappings are cached as raw responses with retrieval dates. Ambiguous or
contradictory mappings never replace supplied identifiers. No dataset accession
resolution or preprint-to-publication equivalence is inferred.
"""
import argparse
from datetime import datetime, timezone
import hashlib,json,re,time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen,Request
import xml.etree.ElementTree as ET

KINDS=('pmid','doi','pmcid')


def normalize(kind,value):
    """Validate identifiers; DOI comparison is case-insensitive."""
    if not value:return None
    value=str(value).strip()
    if kind=='doi':
        value=re.sub(r'^(?:https?://(?:dx\.)?doi.org/|doi:\s*)','',value,flags=re.I).lower()
        if not re.fullmatch(r'10\.\d{4,9}/\S+',value):raise ValueError('Invalid DOI')
    elif kind=='pmid':
        if not re.fullmatch(r'[1-9]\d*',value):raise ValueError('Invalid PMID')
    else:
        value=value.upper()
        if not re.fullmatch(r'PMC[1-9]\d*',value):raise ValueError('Invalid PMCID')
    return value


class Resolver:
    """Batched exact identifier resolution with durable response caching.

    Each uncached request has a 30-second timeout and at most three attempts.
    Successful responses are reused across callers and runs; errors are surfaced
    so interrupted runs can resume without interpreting failure as missing data.
    """
    def __init__(self,cache):
        self.cache=Path(cache);self.cache.mkdir(parents=True,exist_ok=True)

    def request(self,url):
        key=hashlib.sha256(url.encode()).hexdigest();path=self.cache/(key+'.json')
        if path.exists():return json.loads(path.read_text(encoding='utf-8'))
        for attempt in range(3):
            time.sleep(0.4 if attempt==0 else 2**attempt)
            try:
                with urlopen(Request(url,headers={'User-Agent':'DeathMap-AI/0.1 publication-identifiers'}),timeout=30) as response:
                    body=response.read().decode('utf-8')
                receipt={'url':url,'retrieved_at':datetime.now(timezone.utc).isoformat(),'body':body,'response_sha256':hashlib.sha256(body.encode()).hexdigest()}
                if body.lstrip().startswith('<'):
                    tree=ET.fromstring(body)
                    if tree.find('.//ERROR') is not None:raise ValueError('NCBI returned an application error')
                else:
                    parsed=json.loads(body)
                    if parsed.get('error') or parsed.get('status')=='error':raise ValueError('NCBI returned an application error')
                path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                return receipt
            except Exception:
                if attempt==2:raise

    def resolve(self,publications):
        """Return input-preserving records with resolved values and evidence.

        Multiple inputs are separate publications. More than one identifier can
        constrain each publication. A conflict yields no automatic additions.
        """
        inputs=[{k:normalize(k,p.get(k)) for k in KINDS} for p in publications]
        if any(not any(p.values()) for p in inputs):raise ValueError('At least one identifier is required per publication')
        mappings=[]
        pmids={p['pmid'] for p in inputs if p['pmid']}
        for doi in sorted({p['doi'] for p in inputs if p['doi'] and not p['pmid']}):
            url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urlencode({'db':'pubmed','term':doi+'[AID]','retmode':'json','retmax':10,'tool':'deathmap_ai'})
            receipt=self.request(url);ids=json.loads(receipt['body'])['esearchresult']['idlist'];pmids.update(ids)
        for kind in KINDS:
            ids=sorted({p[kind] for p in inputs if p[kind]})
            for start in range(0,len(ids),200):
                url='https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/?'+urlencode({'ids':','.join(ids[start:start+200]),'idtype':kind,'format':'json','tool':'deathmap_ai'})
                receipt=self.request(url)
                for record in json.loads(receipt['body']).get('records',[]):
                    if record.get('errmsg') or record.get('status')=='error':continue
                    mapped={k:normalize(k,record.get(k)) for k in KINDS}
                    if mapped['pmid']:pmids.add(mapped['pmid'])
                    mappings.append((mapped,receipt))
        ids=sorted(pmids)
        for start in range(0,len(ids),100):
            url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urlencode({'db':'pubmed','id':','.join(ids[start:start+100]),'retmode':'xml','tool':'deathmap_ai'})
            receipt=self.request(url)
            for article in ET.fromstring(receipt['body']).findall('PubmedArticle'):
                mapped={k:None for k in KINDS};mapped['pmid']=normalize('pmid',article.findtext('MedlineCitation/PMID'))
                for item in article.findall('PubmedData/ArticleIdList/ArticleId'):
                    kind={'pubmed':'pmid','doi':'doi','pmc':'pmcid'}.get(item.get('IdType'))
                    if kind:mapped[kind]=normalize(kind,item.text)
                mappings.append((mapped,receipt))
        results=[]
        for original in inputs:
            matches=[(m,e) for m,e in mappings if any(original[k] and original[k]==m[k] for k in KINDS)]
            choices={k:{m[k] for m,e in matches if m[k]}|({original[k]} if original[k] else set()) for k in KINDS}
            conflict=any(len(values)>1 for values in choices.values())
            resolved=original.copy() if conflict else {k:next(iter(v)) if v else None for k,v in choices.items()}
            results.append({'input':original,'identifiers':resolved,'status':'conflicting' if conflict else 'resolved' if all(resolved.values()) else 'partial' if matches else 'unresolved',
                            'alternatives':{k:sorted(v) for k,v in choices.items()},'evidence':[{'identifiers':m,**{k:e[k] for k in ['url','retrieved_at','response_sha256']}} for m,e in matches]})
        return results


def main():
    """Resolve positional IDs individually, or grouped records from JSON input."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('identifiers',nargs='*');parser.add_argument('--input',type=Path)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--cache',type=Path,default=Path('data/publication-identifiers/cache'))
    args=parser.parse_args()
    records=json.loads(args.input.read_text(encoding='utf-8')) if args.input else [{'pmcid' if v.upper().startswith('PMC') else 'pmid' if v.isdigit() else 'doi':v} for v in args.identifiers]
    if not records:parser.error('Supply identifiers or --input JSON')
    if args.output.exists():parser.error('Output exists; choose a new path')
    results=Resolver(args.cache).resolve(records);args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
