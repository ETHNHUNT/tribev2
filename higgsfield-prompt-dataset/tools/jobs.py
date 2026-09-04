import re, sys
sys.path.insert(0, '.')
from extract import get_payload, js_strings

def read_string_at(p, k):
    """If p[k]=='\"', return (value, end_index_after_closing_quote)."""
    if k >= len(p) or p[k] != '"':
        return None, k
    j = k + 1; buf = []
    while j < len(p):
        d = p[j]
        if d == '\\':
            nxt = p[j+1] if j+1 < len(p) else ''
            if nxt == 'u':
                try:
                    buf.append(chr(int(p[j+2:j+6], 16))); j += 6; continue
                except Exception:
                    buf.append(nxt); j += 2; continue
            buf.append({'n':'\n','t':'\t','r':'\r','"':'"','\\':'\\','/':'/','b':'\b','f':'\f'}.get(nxt, nxt))
            j += 2; continue
        if d == '"':
            return "".join(buf), j + 1
        buf.append(d); j += 1
    return "".join(buf), j

def scalar_after(p, field, start, end, back=False):
    """Find `field:` within [start,end) and return its string/number value."""
    rx = re.compile(r'(?<![A-Za-z0-9_$])' + re.escape(field) + r'\s*:\s*')
    seg = p[start:end]
    ms = list(rx.finditer(seg))
    if not ms:
        return None
    m = ms[-1] if back else ms[0]
    k = start + m.end()
    if k < len(p) and p[k] == '"':
        v, _ = read_string_at(p, k)
        return v
    m2 = re.match(r'(-?\d+(?:\.\d+)?|null|!0|!1|void 0|true|false)', p[k:k+24])
    if m2:
        t = m2.group(1)
        return {'null': None, 'void 0': None, '!0': True, '!1': False}.get(t, t)
    # field:$R[n]={ ...  -> nested, return marker
    if p[k:k+2] == '$R':
        return '<obj>'
    return None

def nested_name(p, field, start, end):
    """For `field:$R[n]={id:"..",name:"..."}` return the name."""
    rx = re.compile(r'(?<![A-Za-z0-9_$])' + re.escape(field) + r'\s*:\s*\$R\[\d+\]=\{')
    m = rx.search(p, start, end)
    if not m:
        return None
    return scalar_after(p, 'name', m.end(), min(m.end() + 400, len(p)))

PROMPT_RX = re.compile(r'(?<![A-Za-z0-9_$])prompt\s*:\s*(?:\$R\[\d+\]=)?\{\s*prompt\s*:\s*"')

def extract_jobs(htmltext, url):
    p = get_payload(htmltext)
    if not p:
        return []
    out = []
    for m in PROMPT_RX.finditer(p):
        qpos = p.index('"', m.end() - 1)
        text, endq = read_string_at(p, qpos)
        if not text or not text.strip():
            continue
        back = p[max(0, m.start() - 6000):m.start()]
        boff = max(0, m.start() - 6000)
        fwd_end = min(len(p), endq + 4000)
        rec = {
            "prompt": text.strip(),
            "source_url": url,
            "job_set_type": scalar_after(p, 'jobSetType', boff, m.start(), back=True),
            "asset_layer": scalar_after(p, 'assetTypeLayer', boff, m.start(), back=True),
            "preset_name": nested_name(p, 'presetMeta', boff, m.start()),
            "quality": scalar_after(p, 'quality', endq, fwd_end),
            "seed": scalar_after(p, 'seed', endq, fwd_end),
            "aspect_ratio": scalar_after(p, 'aspectRatio', endq, fwd_end),
            "duration": scalar_after(p, 'duration', endq, fwd_end),
            "username": scalar_after(p, 'username', endq, fwd_end),
            "enhanced": scalar_after(p, 'enhance', endq, min(endq + 200, len(p))),
        }
        m2 = re.search(r'(?<![A-Za-z0-9_$])(?:source|url)\s*:\s*"(https://[^"]+\.(?:mp4|webp|jpg|jpeg|png))"', p[endq:fwd_end])
        rec["media_url"] = m2.group(1) if m2 else None
        out.append(rec)
    return out
