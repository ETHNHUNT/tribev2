import sys, os, re, glob, json, html
sys.path.insert(0, '.')
from jobs import extract_jobs
from figures import extract_figures
from prose import extract_prose
from recreate import extract_recreate, srcurl
from pbank import extract_prompt_bank
from catalog import extract_catalog, meta, title, clean_title

GENERIC_DESC = [
    "generate unique ai videos and images with creative presets built for creators on higgsfield",
    "preview ai motion presets and explore dynamic animations to bring your video projects to life",
    "explore ai video presets",
]

def is_generic(d):
    if not d: return True
    dl = d.lower()
    return any(g in dl for g in GENERIC_DESC)

def section_of(url):
    p = url.replace("https://higgsfield.ai", "").strip("/")
    if not p: return "home"
    seg = p.split("/")[0].split("?")[0]
    if seg.startswith("@"): return "creator-profile"
    return seg

rows = []
files = sorted(glob.glob("pages/*.html")) + sorted(glob.glob("probe/*.html"))
seen_files = set()
for f in files:
    h = open(f, encoding="utf-8", errors="replace").read()
    url = srcurl(h)
    if not url:
        continue
    if url in seen_files:
        continue
    seen_files.add(url)
    sec = section_of(url)

    for j in extract_jobs(h, url):
        rows.append({**j, "record_type": "prompt", "extraction_source": "job_payload",
                     "model_or_effect": j.get("job_set_type"), "site_section": sec})
    for r in extract_recreate(h, url):
        rows.append({"prompt": r["prompt"], "source_url": url, "record_type": "prompt",
                     "extraction_source": "recreate_link", "model_or_effect": r.get("model"),
                     "preset_name": r.get("preset"), "target_path": r.get("target_path"),
                     "site_section": sec})
    for fg in extract_figures(h, url):
        rows.append({"prompt": fg["prompt"], "source_url": url, "record_type": "prompt",
                     "extraction_source": "figure_caption", "media_url": fg.get("media_url"),
                     "badges": fg.get("badges"), "site_section": sec})
    for pb in extract_prompt_bank(h, url):
        rows.append({"prompt": pb["prompt"], "source_url": url, "record_type": "prompt",
                     "extraction_source": "prompt_bank", "name": pb.get("name"),
                     "model_or_effect": pb.get("name"), "category": pb.get("category"),
                     "section": pb.get("section"), "media_url": pb.get("media_url"),
                     "site_section": sec})
    for pr in extract_prose(h, url):
        if pr["kind"] != "prompt":
            continue
        rows.append({"prompt": pr["prompt"], "source_url": url, "record_type": "prompt",
                     "extraction_source": "article_body", "site_section": sec})

    if sec in ("motion", "viral-presets", "mixed-media-presets"):
        c = extract_catalog(h, url)
        if c.get("name"):
            rows.append({"name": c["name"], "prompt": None,
                         "description": None if is_generic(c.get("description")) else c.get("description"),
                         "model_or_effect": c.get("model"), "source_url": url,
                         "record_type": "preset_effect", "extraction_source": "catalog_page",
                         "site_section": sec})

json.dump(rows, open("raw_rows.json", "w"), ensure_ascii=False)
print("raw rows:", len(rows))
import collections
print("by source:", dict(collections.Counter(r["extraction_source"] for r in rows)))
print("by type:", dict(collections.Counter(r["record_type"] for r in rows)))
