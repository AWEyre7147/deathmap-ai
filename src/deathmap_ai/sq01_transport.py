"""Hard-timeout OmicsDI search-only HTTP transport, independent of Codex.

The child process bounds the whole response read, not just socket inactivity.
Redirects are disabled. Only the eleven accepted search URLs are reachable;
there is no detail, repository or enrichment request method.
"""
import base64
import json
import subprocess
import sys
from urllib.parse import parse_qs, urlsplit
from deathmap_ai.sq01_plan import ENDPOINT, LITERALS

WORKER = r'''
import base64,json,sys,urllib.request,urllib.error
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
opener=urllib.request.build_opener(NoRedirect)
request=urllib.request.Request(sys.argv[1], headers={'Accept':'application/json','User-Agent':'deathmap-ai/0.1 sq01-search'})
try:
    response=opener.open(request,timeout=float(sys.argv[2]))
except urllib.error.HTTPError as error:
    response=error
with response:
    result={'http_status':response.code,'headers':dict(response.headers.items()),'body':base64.b64encode(response.read()).decode('ascii')}
print(json.dumps(result))
'''


def validate_url(url):
    """Reject every endpoint or parameter outside the accepted search contract."""
    parts = urlsplit(url)
    params = parse_qs(parts.query, keep_blank_values=True)
    if (parts.scheme+'://'+parts.netloc+parts.path != ENDPOINT or parts.fragment or
        set(params) != {'query','start','size'} or any(len(v)!=1 for v in params.values()) or
        params['query'][0] not in [q[1] for q in LITERALS] or params['size'] != ['50'] or
        not params['start'][0].isdigit()):
        raise ValueError('Only accepted SQ01 OmicsDI search-page requests are allowed')


def fetch_search(url, timeout=20):
    """Return status, headers and complete body bytes; exceptions are uncertain."""
    validate_url(url)
    if timeout != 20:
        raise ValueError('Accepted timeout is 20 seconds')
    result = subprocess.run([sys.executable, '-B', '-c', WORKER, url, str(timeout)],
                            capture_output=True, timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError('Uncertain transport outcome: '+result.stderr.decode('utf-8',errors='replace')[-1500:])
    envelope = json.loads(result.stdout)
    envelope['body'] = base64.b64decode(envelope['body'], validate=True)
    return envelope
