"""Parse explicit Nature supporting listings inside the library enrichment stage.

Only transient HTML is inspected. Native labels, captions, links and identifiers
are preserved after a DOI check. This is an imported adapter, not a standalone
publisher service, keyword context classifier or article download command.
"""
from html.parser import HTMLParser
import re
from urllib.parse import urljoin, urlsplit, urlunsplit


class Supplements(HTMLParser):
    """Capture MOESM listing elements with their own captions and file links."""

    def __init__(self, source_url):
        super().__init__(convert_charrefs=True)
        self.source_url = source_url
        self.stack = []
        self.active = None
        self.records = []
        self.dois = []
        self.page_title = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and attrs.get('name', '').lower() == 'citation_doi':
            self.dois.append(attrs.get('content', '').lower())
        if tag in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            return
        self.stack.append(tag)
        identity = attrs.get('id', '')
        if self.active is None and re.fullmatch(r'MOESM\d+', identity):
            self.active = dict(id=identity, depth=len(self.stack), text=[], title=[], links=[])
        if self.active is not None and tag == 'a' and attrs.get('href'):
            url = urlsplit(urljoin(self.source_url, attrs['href']))
            # Only publisher supplementary-file links belong in this inventory.
            if url.scheme == 'https' and '/MediaObjects/' in url.path and (
                    url.hostname.endswith('.springer.com') or url.hostname.endswith('.springer-cdn.com')
                    or url.hostname.endswith('.proxy.lib.ohio-state.edu')):
                self.active['links'].append(urlunsplit((url.scheme, url.netloc, url.path, '', '')))

    def handle_data(self, text):
        if 'title' in self.stack:
            self.page_title.append(text)
        if self.active is not None:
            self.active['text'].append(text)
            if any(tag in self.stack[self.active['depth']:] for tag in ('h3', 'h4')):
                self.active['title'].append(text)

    def handle_endtag(self, tag):
        if tag not in self.stack:
            return
        depth = len(self.stack) - self.stack[::-1].index(tag)
        if self.active is not None and depth <= self.active['depth']:
            record = self.active
            text = ' '.join(' '.join(record['text']).split())
            title = ' '.join(' '.join(record['title']).split())
            description = text[len(title):].strip() if title and text.startswith(title) else text
            self.records.append(dict(id=record['id'], title=title or None,
                description=description, links=list(dict.fromkeys(record['links']))))
            self.active = None
        del self.stack[depth - 1:]


def extract_listing(html, source_url, expected_doi):
    """Return native supporting listings only for the expected article DOI.

    Parameters
    ----------
    html : str
        Transient article HTML already bounded by the library collector.
    source_url : str
        Observed publisher article address used to resolve supplied links.
    expected_doi : str
        Normalized DOI of the selected publication.

    Returns
    -------
    dict
        Supporting listings with original labels/descriptions; no generated
        article-context categories or inferred experimental relationships.
    """
    parser = Supplements(source_url)
    parser.feed(html)
    return {'supplements': parser.records if expected_doi.lower() in parser.dois else []}
