import re, html, sys, json
sys.path.insert(0, '.')
from extract import get_payload
from jobs import scalar_after

def meta(h, name):
    m = re.search(r'<meta\s+(?:name|property)="' + re.escape(name) + r'"\s+content="([^"]*)"', h)
    if not m:
        m = re.search(r'<meta\s+content="([^"]*)"\s+(?:name|property)="' + re.escape(name) + r'"', h)
    return html.unescape(m.group(1)) if m else None

def title(h):
    m = re.search(r'<title>([^<]*)</title>', h)
    return html.unescape(m.group(1)).strip() if m else None

def jsonld(h):
    out = []
    for s in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', h, flags=re.S):
        try:
            out.append(json.loads(html.unescape(s.strip())))
        except Exception:
            pass
    return out

def clean_title(t):
    if not t:
        return None
    for sep in [' • ', ' — ', ' | ', ' - ']:
        if sep in t:
            t = t.split(sep)[0]
    return t.strip()

def extract_catalog(h, url):
    """Preset / motion catalog entry: name + description + model."""
    p = get_payload(h)
    name = None
    for ld in jsonld(h):
        if isinstance(ld, dict) and ld.get('@type') in ('WebPage', 'Product', 'CreativeWork') and ld.get('name'):
            name = ld['name']; break
    if not name:
        name = clean_title(title(h))
    desc = meta(h, 'description') or meta(h, 'og:description')
    model = None
    if p:
        for f in ('model', 'jobSetType', 'motionModel'):
            v = scalar_after(p, f, 0, len(p))
            if v and v != '<obj>':
                model = v; break
    return {
        "name": clean_title(name),
        "description": (desc or '').strip() or None,
        "model": model,
        "source_url": url,
    }
