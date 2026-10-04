"""Bounded ORCS page capability sample; retains metadata excerpts, never score tables.

Five fixed native screens are selected in saved order across distinct publications.
A recorded corrective parsing pass permits at most two HTTP attempts per screen.
Successful receipts are reused; the single corrective attempt is retained in receipts. Links are
recorded as evidence without fetching their targets or claiming dataset attribution.
"""
import hashlib,json,re,time,urllib.request
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urljoin
from html.parser import HTMLParser
from html import unescape

class MetadataParser(HTMLParser):
    """Collect display text, descriptive list fields and literal link targets."""
    def __init__(self):
        super().__init__();self.text=[];self.fields=[];self.links=[];self.current_field=None;self.current_link=None
    def handle_starttag(self,tag,attrs):
        if tag=='li':self.current_field=[]
        if tag=='a' and dict(attrs).get('href'):self.current_link=[dict(attrs)['href'],[]]
    def handle_data(self,data):
        self.text.append(data)
        if self.current_field is not None:self.current_field.append(data)
        if self.current_link is not None:self.current_link[1].append(data)
    def handle_endtag(self,tag):
        if tag=='li' and self.current_field is not None:self.fields.append(' '.join(' '.join(self.current_field).split()));self.current_field=None
        if tag=='a' and self.current_link is not None:self.links.append({'label':' '.join(' '.join(self.current_link[1]).split()),'url':urljoin('https://orcs.thebiogrid.org/',self.current_link[0])});self.current_link=None


ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'outputs/orcs/cancer-cell-crispr-knockout-v01/20261003T173643920687Z'
OUT=ROOT/'data/orcs/website-capability/20261003-five-screen-v01'
SELECTED=['16','18','65','572','1']

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write(p,data):
    Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def metadata_excerpt(html):
    """Discard scripts/styles and everything at or after the first results section."""
    end=re.search(r'<h[1-6]\b[^>]*>\s*(?:Score Distribution|CRISPR Screen Results)',html,re.I)
    if not end:raise ValueError('No recognized metadata/results boundary')
    prefix=html[:end.start()]
    prefix=re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', prefix, flags=re.S|re.I)
    heading=re.search(r'<h[1-6]\b[^>]*>\s*CRISPR Screen Dataset\s*</h[1-6]>',prefix,re.I)
    if not heading:raise ValueError('Screen heading missing')
    return prefix[heading.start():]

def parse(html,native):
    """Verify screen/publication association before extracting descriptive evidence."""
    excerpt=metadata_excerpt(html);parser=MetadataParser();parser.feed(excerpt);text=' '.join(' '.join(parser.text).split())
    if re.sub(r'\s+','',native['SCREEN_NAME']) not in re.sub(r'\s+','',text):raise ValueError('Displayed screen name mismatch')
    if native['SOURCE_TYPE']=='pubmed' and native['SOURCE_ID'] not in text:raise ValueError('Displayed PMID association missing')
    links=parser.links
    fields=parser.fields
    title=re.search(r'Title\s*:\s*(.*?)(?:Screen Details|Screen Rationale)',text)
    # Repository accessions are candidates only, not confirmed screen-dataset links.
    accession_pattern=r'\b(?:GSE\d+|GSM\d+|SRP\d+|SRR\d+|PRJNA\d+|ERP\d+|E-MTAB-\d+)\b'
    return excerpt,{'SCREEN_ID':native['SCREEN_ID'],'screen_name_reported':native['SCREEN_NAME'],'SOURCE_TYPE':native['SOURCE_TYPE'],'SOURCE_ID':native['SOURCE_ID'],'identity_verified':True,'publication_title':title.group(1).strip() if title else None,'metadata_text':text,'fields':fields,'links':links,'repository_accession_mentions':sorted(set(re.findall(accession_pattern,text+' '+json.dumps(links)))),'comparison':'Page metadata supplements saved screen-list response; links alone do not establish exact dataset attribution.'}

def main():
    """Capture remaining fixed pages, with at most two attempts per screen and 30 seconds/512 KiB each."""
    OUT.mkdir(parents=True,exist_ok=True)
    native={x['SCREEN_ID']:x for x in json.loads((ROOT/'data/orcs/screen-index.json').read_text(encoding='utf-8'))}
    wb=PRIOR/'DeathMap-AI-v1-reference-output.xlsx'
    selection=[{'SCREEN_ID':key,'SOURCE_ID':native[key]['SOURCE_ID'],'reason':'First three direct hits, first unresolved, first context sibling in saved order, distinct publications'} for key in SELECTED]
    manifest_path=OUT/'manifest.json'
    if not manifest_path.exists():write(manifest_path,{'selected':selection,'started_at':datetime.now(timezone.utc).isoformat(),'authority':'User A16 capability-test request, 2026-10-03; follows workbook review','max_requests':5,'retries':0,'timeout_seconds':30,'spacing_seconds':1,'max_bytes_per_response':524288,'workbook_sha256_before':sha(wb),'cached_screen_count':len(native),'script_sha256':sha(__file__)})
    for key in SELECTED:
        receipt=OUT/f'screen-{key}.receipt.json'
        previous=None
        if receipt.exists():
            previous=json.loads(receipt.read_text())
            if previous['status']=='success' or previous.get('previous_attempt'):continue

        url=f'https://orcs.thebiogrid.org/Screen/{key}'
        rec={'SCREEN_ID':key,'url':url,'status':'reserved','requested_at':datetime.now(timezone.utc).isoformat()};write(receipt,rec)
        if previous:rec['previous_attempt']=previous;write(receipt,rec)
        start=time.monotonic();buf=b''
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'DeathMap-AI/0.1 bounded metadata capability test','Accept-Encoding':'identity'})
            with urllib.request.urlopen(request,timeout=30) as response:
                rec.update(http_status=response.status,content_length=response.headers.get('Content-Length'))
                while len(buf)<524288:
                    block=response.read(4096)
                    if not block:break
                    buf+=block
                    if re.search(br'<h[1-6]\b[^>]*>\s*(?:Score Distribution|CRISPR Screen Results)',buf,re.I):break
                    if time.monotonic()-start>30:raise TimeoutError('Response budget exceeded')
            # Preserve the metadata boundary before identity normalization so a
            # rejected record can be repaired offline without another request.
            html=buf.decode('utf-8')
            excerpt=metadata_excerpt(html)
            (OUT/f'screen-{key}.metadata.html').write_text(excerpt,encoding='utf-8')
            excerpt,parsed=parse(html,native[key])
            raw=OUT/f'screen-{key}.metadata.html';raw.write_text(excerpt,encoding='utf-8')
            write(OUT/f'screen-{key}.json',parsed)
            rec.update(status='success',metadata_bytes=raw.stat().st_size,metadata_sha256=sha(raw),read_bytes=len(buf),saved_scope='Metadata excerpt only; scripts and score sections omitted')
        except Exception as error:rec.update(status='failed',error=str(error),read_bytes=len(buf))
        rec.update(elapsed_seconds=round(time.monotonic()-start,3),completed_at=datetime.now(timezone.utc).isoformat());write(receipt,rec);print(key,rec['status'],rec['elapsed_seconds'],flush=True);time.sleep(1)
        if rec['status']=='failed':break
    receipts=[json.loads((OUT/f'screen-{key}.receipt.json').read_text()) for key in SELECTED]
    manifest=json.loads(manifest_path.read_text());manifest.update(completed_at=datetime.now(timezone.utc).isoformat(),receipts=receipts,workbook_sha256_after=sha(wb));assert manifest['workbook_sha256_before']==manifest['workbook_sha256_after'];write(manifest_path,manifest)
if __name__=='__main__':main()
