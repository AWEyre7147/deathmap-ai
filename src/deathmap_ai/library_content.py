"""Select compact publisher-written sections and explicit supporting listings.

HTML/XML/JSON bodies are transient inputs. Outputs contain selected source text,
native headings/types, links and provenance, never a whole article or generated
scientific classifications. Ambiguous boundaries produce omissions, not guesses.
"""
from html.parser import HTMLParser
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit

METHOD = re.compile(r'^(?:materials? and methods?|methods?(?: and materials?)?|experimental procedures|experimental methods|star\s*methods|online methods|method details|research design and methods)$', re.I)
AVAILABILITY = re.compile(r'^(?:(?:data|code|software|materials?|resource)(?: and (?:data|code|software|materials?|resource))? (?:availability|accessibility)|availability of (?:data|code|data and materials)|data sharing|data deposition|accession numbers?)$', re.I)
EXCLUDED = re.compile(r'^(?:results?|discussion|abstract|introduction|references|acknowledg|author contributions?|lead contact|figure\s*\d|table\s*\d)\b', re.I)
SUPPLEMENT = re.compile(r'supplement|supporting (?:information|material)|additional files?', re.I)
PATHOGEN = re.compile(r'coronavirus|SARS|MERS|influenza|Ebola|Marburg|\bHIV\b|hepatitis|dengue|Zika|West Nile|chikungunya|orthopox|vaccinia|smallpox|anthrax|viral (?:entry|infection|replication)|virus infection', re.I)
ACCESSION = re.compile(r'\b(?:GSE\d+|GSM\d+|GPL\d+|PRJ(?:NA|EB|DB)\d+|[SED]R[PRSX]\d+|E-(?:MTAB|GEOD|MEXP)-\d+|S-(?:EPMC|BSST)\d+)\b', re.I)
REPOSITORIES = {'github.com':'GitHub','gitlab.com':'GitLab','bitbucket.org':'Bitbucket',
                'zenodo.org':'Zenodo','figshare.com':'Figshare','data.mendeley.com':'Mendeley Data',
                'osf.io':'OSF','datadryad.org':'Dryad','addgene.org':'Addgene','depmap.org':'DepMap'}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}


def normalize_doi(value):
    """Remove DOI wrappers for exact identity comparison, without title matching."""
    return re.sub(r'^(?:https?://(?:dx\.)?doi.org/|doi:\s*)', '', unquote(str(value or '')).strip(), flags=re.I).casefold()


def text(value):
    """Normalize display whitespace while preserving the source's wording."""
    return ' '.join(str(value or '').split())


def heading_key(value):
    return re.sub(r'^\d+(?:\.\d+)*[.\s]+', '', text(value)).replace('â˜…',' ').replace('&','and').strip()


def safe_url(value, base=''):
    """Resolve supplied web links and remove all transient query/fragment state."""
    u = urlsplit(urljoin(base, str(value or '')))
    if u.scheme not in ('http','https') or u.username or u.password:
        return ''
    return urlunsplit((u.scheme,u.netloc,u.path,'',''))


def native_reference(value):
    """Keep native file identifiers, removing query/fragment authentication state."""
    return str(value or '').split('?',1)[0].split('#',1)[0]


def video_material(item):
    """Identify video supporting entries by their own labels, MIME or file type.

    A data table is retained when its description merely mentions a video.
    Description-only video listings are excluded even without a title or URL.
    """
    label=text(item.get('label') or item.get('title'))
    description=text(item.get('description'))
    if re.search(r'\b(?:videos?|movies?|animations?)\b',label,re.I):return True
    if text(item.get('media_type') or item.get('mimetype')).lower().startswith('video/'):return True
    types=[]
    for value in (item.get('url'),item.get('native_reference')):
        suffix=urlsplit(str(value or '')).path.lower().rsplit('.',1)[-1]
        types.append(suffix)
        if suffix in {'mp4','mov','avi','m4v','webm','wmv','mpeg','mpg','ogv','flv','mkv','3gp'}:return True
    nonvideo={'pdf','xlsx','xls','csv','tsv','doc','docx','txt'}
    return not label and not any(t in nonvideo for t in types) and bool(re.search(r'\b(?:videos?|movies?|animations?)\b',description,re.I))


def section_allowed(chain):
    """Accept only clear methods/availability boundaries outside excluded regions."""
    headings = [heading_key(h) for h in chain]
    return bool(headings) and not any(EXCLUDED.search(h) for h in headings) and any(METHOD.fullmatch(h) or AVAILABILITY.fullmatch(h) for h in headings)


class ArticleHTML(HTMLParser):
    """Read heading ancestry, paragraphs and explicit supporting sections only.

    Parameters
    ----------
    address : str
        Observed article URL, used only to resolve publisher-supplied links.
    """
    def __init__(self, address):
        super().__init__()
        self.address=address; self.stack=[]; self.headings=[]; self.capture=None
        self.paragraph=None; self.anchor=None; self.dois=[]; self.context=[]
        self.materials=[]; self.scripts=[]; self.script=None; self.skip=0
        self.title_parts=[]; self.in_title=False; self.restricted_depth=0; self.pii=None

    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='meta':
            key=a.get('name',a.get('property','')).lower()
            if key=='citation_pii':self.pii=a.get('content')
            if key in ('citation_doi','dc.identifier','dc.identifier.doi','prism.doi'):
                value=a.get('content','')
                if normalize_doi(value).startswith('10.'):
                    self.dois.append(normalize_doi(value))
        if tag=='script':
            self.script={'type':a.get('type',''),'parts':[]}; self.skip+=1
        elif tag=='style':self.skip+=1
        if self.skip:return
        if tag=='title':self.in_title=True
        restricted=tag in ('figure','figcaption','table','nav','footer','aside')
        marker=' '.join(a.get(k,'') for k in ('id','class','data-title'))
        explicit=bool(SUPPLEMENT.search(marker))
        if tag not in VOID:
            self.stack.append((tag,explicit,restricted))
            if restricted:self.restricted_depth+=1
        if re.fullmatch(r'h[1-6]',tag) and not self.restricted_depth:self.capture={'tag':tag,'parts':[]}
        if tag=='p':self.paragraph={'parts':[],'chain':[h for _,h in self.headings], 'id':a.get('id'), 'restricted':self.restricted_depth>0}
        if tag=='a' and a.get('href'):
            self.anchor={'href':a['href'],'parts':[], 'explicit':any(s[1] for s in self.stack) or bool(self.headings and SUPPLEMENT.search(self.headings[-1][1])),'heading':self.headings[-1][1] if self.headings else ''}

    def handle_data(self, value):
        if self.script is not None:self.script['parts'].append(value)
        if self.skip:return
        if self.in_title:self.title_parts.append(value)
        if self.capture:self.capture['parts'].append(value)
        if self.paragraph:self.paragraph['parts'].append(value)
        if self.anchor:self.anchor['parts'].append(value)

    def handle_endtag(self, tag):
        if tag=='script':
            if self.script and 'json' in self.script['type']:
                try:self.scripts.append(json.loads(''.join(self.script['parts'])))
                except (ValueError,TypeError):pass
            self.script=None;self.skip=max(0,self.skip-1);return
        if tag=='style':self.skip=max(0,self.skip-1);return
        if self.skip:return
        if tag=='title':self.in_title=False
        if self.capture and tag==self.capture['tag']:
            level=int(tag[1]); heading=text(''.join(self.capture['parts']))
            while self.headings and self.headings[-1][0]>=level:self.headings.pop()
            self.headings.append((level,heading)); self.capture=None
        if tag=='p' and self.paragraph:
            p=self.paragraph
            if not p['restricted']:
                self.context.append({'heading':p['chain'][-1] if p['chain'] else '', 'ancestors':p['chain'], 'text':text(''.join(p['parts'])), 'native_id':p['id'], 'source_format':'HTML','native_type':''})
            self.paragraph=None
        if tag=='a' and self.anchor:
            a=self.anchor
            if a['explicit']:
                url=safe_url(a['href'],self.address)
                if url and url!=safe_url(self.address):
                    self.materials.append({'label':text(''.join(a['parts'])) or a['heading'],'description':'','url':url,'native_reference':native_reference(a['href']),'native_id':'','source_format':'HTML'})
            self.anchor=None
        # Pop to the matching element, tolerating HTML optional closing tags.
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                self.restricted_depth-=sum(s[2] for s in self.stack[i:])
                del self.stack[i:];break


def json_sections(payload):
    """Read XML-like publisher JSON, carrying native section ancestry directly.

    Parameters
    ----------
    payload : dict or list
        Article-bound JSON from an observed publisher content response.

    Returns
    -------
    tuple
        Paragraph records, supporting records and extraction-limit notes.
    """
    paragraphs=[]; materials=[]; notes=set(); visited=0
    def name(node):return str(node.get('#name','')).split(':')[-1].lower()
    def words(node):
        if isinstance(node,str):return node
        if isinstance(node,list):return ''.join(words(v) for v in node)
        if isinstance(node,dict):return str(node.get('_',node.get('#text','')))+words(node.get('$$',[]))
        return ''
    def walk(node,path,chain,inside=False,restricted=False,depth=0):
        nonlocal visited
        visited+=1
        if visited>60000 or depth>64:notes.add('JSON traversal limit');return
        if isinstance(node,dict):
            kind=name(node); children=node.get('$$',[])
            if kind in ('section','sec','appendix'):
                title=next((c for c in children if isinstance(c,dict) and name(c) in ('section-title','title')),None)
                if title:chain=chain+[text(words(title))]
            restricted=restricted or kind in ('figure','fig','table','table-wrap','ref-list','bibliography','abstract')
            is_para=kind in ('para','simple-para','paragraph','p')
            if is_para and not inside and not restricted:
                paragraphs.append({'heading':chain[-1] if chain else '', 'ancestors':chain,'text':text(words(node)), 'native_id':node.get('$',{}).get('id') or path,'source_format':'JSON','native_type':''})
            if kind in ('supplementary-material','supplement','attachment','e-component'):
                label=next((text(words(c)) for c in children if isinstance(c,dict) and name(c) in ('label','title')),'')
                caption=next((text(words(c)) for c in children if isinstance(c,dict) and name(c) in ('caption','description')),'')
                refs=[]
                def links(v):
                    if isinstance(v,dict):
                        for k,x in v.items():
                            if k.lower() in ('href','xlink:href','filename','file-name') and isinstance(x,str):refs.append(x)
                            elif isinstance(x,(dict,list)):links(x)
                    elif isinstance(v,list):
                        for x in v:links(x)
                links(node)
                for ref in dict.fromkeys(refs or ['']):
                    materials.append({'label':label,'description':caption,'url':safe_url(ref),'native_reference':native_reference(ref),'native_id':node.get('$',{}).get('id') or path,'source_format':'JSON'})
            for key,value in node.items():
                if isinstance(value,(dict,list)) and not re.search(r'cookie|token|session|password|credential|profile',key,re.I):
                    walk(value,path+'.'+key,chain,inside or is_para,restricted,depth+1)
        elif isinstance(node,list):
            if len(node)>5000:notes.add('JSON array limit')
            for i,value in enumerate(node[:5000]):walk(value,f'{path}[{i}]',chain,inside,restricted,depth+1)
    walk(payload,'$',[])
    return paragraphs,materials,sorted(notes)


def xml_sections(body):
    """Read publisher XML sections and supplementary elements without body search."""
    root=ET.fromstring(body)
    for n in root.iter():n.tag=n.tag.split('}')[-1]
    paragraphs=[];materials=[];dois=[]
    for n in root.iter('article-id'):
        if n.get('pub-id-type')=='doi':dois.append(normalize_doi(''.join(n.itertext())))
    def walk(node,chain,native_type='',restricted=False,path='/'):
        if node.tag in ('sec','section'):
            title=node.find('title')
            if title is not None:chain=chain+[text(''.join(title.itertext()))]
            native_type=node.get('sec-type',native_type)
        restricted=restricted or node.tag in ('fig','table-wrap','ref-list','abstract')
        if node.tag=='p' and not restricted:
            paragraphs.append({'heading':chain[-1] if chain else '', 'ancestors':chain,'text':text(''.join(node.itertext())),'native_id':node.get('id') or path,'native_type':native_type,'source_format':'XML'})
        if node.tag in ('supplementary-material','inline-supplementary-material'):
            label=text(''.join(node.find('label').itertext())) if node.find('label') is not None else ''
            caption=text(''.join(node.find('caption').itertext())) if node.find('caption') is not None else ''
            refs=[value for child in node.iter() for key,value in child.attrib.items() if key.endswith('href')]
            for ref in dict.fromkeys(refs or ['']):materials.append({'label':label,'description':caption,'url':safe_url(ref),'native_reference':native_reference(ref),'native_id':node.get('id') or path,'source_format':'XML'})
            return
        for i,child in enumerate(node):walk(child,chain,native_type,restricted,f'{path}/{child.tag}[{i}]')
    walk(root,[])
    return paragraphs,materials,dois


def extract(body, address, publication, kind='html', article_bound=False, max_text=60000):
    """Extract selected source records after exact article identity verification.

    Parameters
    ----------
    body : bytes
        Transient response, capped at ten MB. Never saved by this function.
    address : str
        Observed source address, without authentication query state.
    publication : dict
        Publication Index, DOI and optional Title.
    kind : str
        html, xml, or json. JSON requires an already DOI-verified, article-bound
        response observed by the browser adapter.
    article_bound : bool
        True only for a JSON route whose article identifier matches verified HTML.
    max_text : int
        Guard on selected context characters, with omitted units reported.

    Returns
    -------
    dict
        Identity outcome, selected context/support records and omission notes.
    """
    if len(body)>10_000_000:raise ValueError('Article metadata exceeds ten MB')
    expected=normalize_doi(publication.get('DOI')); notes=[]; title='';pii=None
    if kind=='html':
        parser=ArticleHTML(address);parser.feed(body.decode('utf-8',errors='replace'))
        paragraphs=parser.context;materials=parser.materials;dois=parser.dois
        title=text(''.join(parser.title_parts))
        pii=parser.pii
        for payload in parser.scripts:
            p,m,n=json_sections(payload);paragraphs+=p;materials+=m;notes+=n
        # Nature's dedicated listing parser supplies native labels/descriptions.
        # It is part of this library adapter and performs no standalone retrieval.
        if 'nature' in urlsplit(address).hostname:
            from .library_nature import extract_listing
            n=extract_listing(body.decode('utf-8',errors='replace'),address,expected)
            for item in n.get('supplements',[]):
                for ref in item.get('links',[]) or ['']:
                    materials.append({'label':text(item.get('title')),'description':text(item.get('description')),'url':safe_url(ref),'native_reference':native_reference(ref),'native_id':item.get('id',''),'source_format':'HTML'})
    elif kind=='xml':paragraphs,materials,dois=xml_sections(body)
    elif kind=='json':
        paragraphs,materials,notes=json_sections(json.loads(body));dois=[expected] if article_bound else []
    else:raise ValueError('Unsupported article representation')
    verified=bool(expected and dois and set(dois)=={expected})
    if re.search(r'captcha|verify you are human|client challenge',title,re.I):
        return {'doi_verified':verified,'outcome':'challenge','context':[],'materials':[],'notes':[]}
    if not verified:return {'doi_verified':False,'outcome':'article_identity_unverified','context':[],'materials':[],'notes':[]}
    selected=[];seen=set();total=0
    for p in paragraphs:
        value=p['text'];chain=p['ancestors']
        if not value or not section_allowed(chain):continue
        if PATHOGEN.search(publication.get('Title','')+' '+p['heading']+' '+value) and not AVAILABILITY.fullmatch(heading_key(p['heading'])):
            notes.append('Methods require separate content review');continue
        if re.search(r'copyright|all rights reserved|accept cookies|log in to|advertisement',value,re.I):continue
        if len(value)>24000 or total+len(value)>max_text:
            notes.append('Selected text size guard: '+str(p.get('native_id')));continue
        key=value
        if key in seen:continue
        seen.add(key);total+=len(value);selected.append(p)
    unique={}
    for m in materials:
        if video_material(m):continue
        for field in ('label','description'):
            if len(m[field])>24000:
                notes.append('Oversized supporting '+field+' omitted: '+str(m.get('native_id')));m[field]=''
        key=m['url'] or m['native_reference'] or m['native_id'] or m['description']
        if key and (key not in unique or len(m['description'])>len(unique[key]['description'])):unique[key]=m
    if not selected:notes.append('No qualifying methods or availability text retained')
    if not unique:notes.append('No explicit supporting listing retained')
    digest=hashlib.sha256(body).hexdigest()
    for item in selected+list(unique.values()):
        item['source_url']=safe_url(address);item['source_sha256']=digest
    return {'doi_verified':True,'outcome':'retrieved' if selected or unique else 'parser_incomplete',
            'context':selected,'materials':list(unique.values()),'notes':sorted(set(notes)),
            'source_url':safe_url(address),'representation':kind,'article_pii':pii}


def repository_references(value):
    """Yield reported accessions and recognized deposit/code URLs, without requests."""
    found={}
    for acc in ACCESSION.findall(value):
        name='GEO' if acc.upper().startswith(('GSE','GSM','GPL')) else 'BioProject' if acc.upper().startswith('PRJ') else 'BioStudies' if acc.upper().startswith(('E-','S-')) else 'Sequence Archive'
        found[acc.upper()]={'Repository':name,'Accession':acc.upper(),'Repository URL':''}
    for match in re.findall(r'https?://[^\s<>"\[\]{}]+',value):
        url=safe_url(match.rstrip('.,;)'));host=urlsplit(url).hostname or ''
        name=next((name for domain,name in REPOSITORIES.items() if host==domain or host.endswith('.'+domain)),None)
        if name:found[url]={'Repository':name,'Accession':'','Repository URL':url}
    return list(found.values())
