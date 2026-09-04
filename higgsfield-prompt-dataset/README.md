# Higgsfield.ai Prompt & Preset Dataset

A systematic crawl and prompt extraction across the public surface of **higgsfield.ai**, delivered as a
narrative report, an Excel/CSV dataset, and a print-ready PDF.

| | |
|---|---|
| **Pages crawled** | 1,481 (0 fetch errors on the sitemap corpus) |
| **URLs mapped** | 1,484 unique public URLs |
| **Records extracted** | **1,165** |
| — literal prompts | 779 |
| — presets / motion effects | 386 |
| **Total prompt text captured** | ~919,000 characters |
| **Prompt length** | 6 – 3,282 words (median 64) |
| **Crawl date** | 2026-09-04 |

---

## 1. What this dataset contains

Every record carries the four fields the brief asked for:

1. **Full prompt text** — verbatim, un-truncated, including multi-line shot breakdowns and embedded
   `HEX VALUES` colour blocks.
2. **A description of what it creates** — either the site's own effect/preset description, or (for
   generation records) the prompt itself plus derived style and subject tags.
3. **The associated model or motion effect** — e.g. `Higgsfield Soul 2.0`, `Kling 3.0`, `Seedance 2.0 4K`,
   `Wan 2.5`, `Sora 2`, or a named motion effect such as *Super Dolly Out*.
4. **The source page URL** — the exact page the record was lifted from.

Plus derived and provenance fields: tool type, generation style, visual subject, aspect ratio, duration,
quality, sample media URL, extraction method, and a confidence grade.

---

## 2. How the site was mapped

`robots.txt` advertises **eleven** sitemaps, which together enumerate the public surface:

```
sitemap-marketing.xml   sitemap-projects.xml      blog/sitemap.xml
creator-hub/sitemap.xml apps/sitemap.xml          motion/sitemap.xml
mixed-media-presets/…   viral-presets/…           contests/…
original-series/…       academy/sitemap.xml
```

Those yielded **1,138** URLs. Two further link-discovery passes over the fetched HTML — following every
internal `href` and diffing against what was already known — added **192** more real pages (129 additional
motion effects plus assorted tool, contest and help-centre pages), for a final corpus of **1,481 fetched
pages**.

**Politeness and scope.** All 37 `Disallow` rules from `robots.txt` are parsed and enforced by
`tools/crawl.py` (`/me/`, `/library/`, `/share/`, `/flow/`, `/soul/`, `/mixed-media-community/`,
`/viral-presets/use/`, the four non-English locale trees, and the rest). Requests run at six concurrent
workers with a 150 ms inter-request delay and exponential backoff. Nothing behind authentication was
touched; no login was performed. Roughly 3,000 additional discovered URLs turned out to be
per-example sub-pages (`/motion/<id>/<exampleId>`, `/viral-presets/examples/<slug>/<exampleId>`) that
merely re-render their parent — they were deliberately not fetched.

---

## 3. How prompts were extracted

Higgsfield is a **TanStack Start** application. Its pages ship a server-rendered router payload —
a `$R[n]=…` object graph in an inline `<script>` — that carries the real generation records behind
each gallery tile. That payload, not the visible DOM, is the highest-fidelity source. Six extractors
run over every page:

| Extractor | What it reads | Records | Fidelity |
|---|---|---|---|
| `jobs.py` | `prompt:{prompt:"…"}` job records in the TanStack payload, with `jobSetType`, `presetMeta`, `quality`, `seed`, `aspectRatio`, `duration` | 234 | Highest — real generation jobs |
| `pbank.py` | The Academy Prompt Bank's `{title, prompt, categoryId, media}` records, with category names resolved from the payload | 68 | Highest |
| `recreate.py` | `?recreate=<urlencoded prompt>&model=<model>` hrefs behind every "Recreate" button | 107 | Highest — prompt/model pairs |
| `figures.py` | `<figcaption>` / `aria-label` on demo `<figure>` blocks, plus platform/tier badges (TikTok, Pro, Sound Boost…) | 5,554 raw | Mixed — heavily filtered |
| `prose.py` | Long `<p>` / `<pre>` / `<blockquote>` blocks in blog and academy articles | 442 | Good — classifier-gated |
| `catalog.py` | Motion / viral / mixed-media preset pages: name, description, model | 494 | Structured metadata |

### Separating prompts from prose

Article bodies and demo captions mix genuine prompts with marketing copy and how-to advice. A
two-stage classifier (`tools/prose.py`) resolves this:

- **`looks_like_prompt()`** requires length, word density, and either an explicit structural marker
  (`Format & Style:`, `Camera:`, `HEX VALUES:`, `Sound & Foley`) or ≥3 cinematographic terms.
- **`classify()`** then separates *prompt* from *guidance* by weighing scene-opening grammar
  ("A low-angle full-body shot captures…") against second-person instructional markers
  ("Specify…", "you can…", "we recommend…").

For figure captions a **page-frequency filter** does the heavy lifting: a caption appearing on more than
three distinct pages is site boilerplate (a feature-card tagline such as *"Shots — 9 unique shots from one
image"*, repeated on 80 pages), not a prompt. That single rule removed 5,404 of 5,554 raw captions.

Every record is graded **High / Medium / Low** confidence so downstream users can filter. 1,083 of 1,165
records (93%) are High — they came from structured payload data or passed the full classifier.

---

## 4. What the corpus looks like

### By tool type

| Tool type | Records |
|---|---|
| Motion Effect Preset | 335 |
| Editorial / Tutorial Prompt | 322 |
| Video Generation | 292 |
| Image Generation | 78 |
| Viral Preset | 66 |
| Mixed Media Preset | 33 |
| Camera Movement Prompt | 24 |
| Marketing / Ad Generation | 6 |
| Audio / Voice, Cinema Studio, Lipsync | 9 |

### By model / motion engine

`Wan 2.5` (236) dominates because it powers the motion-effect catalogue. Among *generation* prompts the
spread is `Higgsfield Soul 2.0` (78, image), `MiniMax Hailuo` (66), `Viral Preset` (62),
`Seedance 2.0` (62), `Seedance 2.0 4K` (49), `Mixed Media` (33), `Seedance 2.5` (31), `Kling 3.0` (31),
`Sora 2` (26), `Cinema Studio` (18). 383 records — chiefly blog and academy prompts on model-agnostic
pages — carry no attributable model.

### By generation style (multi-label)

Cinematic / Film (307) · Product / Commercial (275) · Photorealistic (133) · UGC / Handheld (123) ·
Glitch / Experimental (92) · Fantasy / Sci-Fi (79) · Fashion / Editorial (73) · Aerial / Drone (58) ·
3D / CGI Render (56) · Retro / VHS / Analog (46)

### By visual subject (multi-label)

People / Portrait (937) · Landscape / Nature (305) · Architecture / Interior (281) ·
Abstract / Texture (228) · Product / Object (218) · Vehicles / Transport (168) · Food / Drink (112) ·
Animals / Creatures (111) · Text / Logo / Graphic (100)

### By prompt length

| Words | Prompts |
|---|---|
| 1–25 | 137 |
| 26–75 | 282 |
| 76–200 | 191 |
| 201–500 | 93 |
| 500+ | 76 |

The bimodality is real and deliberate — Higgsfield's own Sora 2 guide teaches "two formulas": short
high-signal prompts that let the model direct, and high-control prompts that specify every shot. The
longest record in the corpus is a 20,515-character Seedance 2.0 4K scene breakdown using `@character`
reference tokens across a full multi-shot sequence.

---

## 5. Observed prompt conventions

Patterns that recur across the high-fidelity records, useful to anyone writing for these models:

- **Shot-first grammar.** Prompts overwhelmingly open by naming the shot, not the subject:
  *"A low-angle full-body shot captures…"*, *"Head-tracking flight shot of a peregrine falcon."*
- **Labelled blocks for long prompts.** Long-form prompts use explicit sections —
  `Format & Style:`, `Camera:`, `Lens:`, `Main Subject(s):`, `Wardrobe and Props`, `Location`,
  `Lighting & Palette`, `Actions & Camera Beats (0–12 s)`, `Dialogue (full)`, `Sound & Foley`,
  `Montage Plan` — which the Sora 2 guide presents as the high-control formula.
- **Timecoded beats.** Video prompts frequently script action against time: `• 0–4 s — …`,
  `[0–2s] – CUT 1 / OPEN.`
- **Palette pinning via hex.** Soul image prompts append a literal `HEX VALUES: ["#1c3633", …]` array —
  typically 15 colours — to lock the grade.
- **Bracketed slots.** Camera-movement prompts in the Prompt Bank are templates with fill-in slots:
  *"…starting on [composition A] and sweeping across [the environment]…"* — the move is written to stay
  separate from the scene so it survives a frame swap.
- **Negative constraints.** Motion prompts lean hard on exclusions to stop drift: *"no sideways travel,
  no dolly, no truck, no arc, no slide, no zoom, no tilt."*
- **Reference tokens.** Multi-shot Seedance prompts bind entities with `@truck1`, `@woman`,
  `@fantasy-dragon`, and video-to-video prompts use `<<<video_1>>>`.

---

## 6. Deliverables

All files are in [`data/`](data/).

| File | Format | Contents |
|---|---|---|
| `higgsfield_prompt_dataset.xlsx` | Excel | 4 sheets — All Records, Prompts, Presets and Effects, Summary. Frozen headers, styled tables, wrapped prompt columns. |
| `higgsfield_prompts_full.csv` | CSV | All 1,165 records, 21 columns, UTF-8 BOM + fully quoted (opens cleanly in Excel). |
| `higgsfield_prompts_only.csv` | CSV | The 779 literal prompts. |
| `higgsfield_presets_effects.csv` | CSV | The 386 presets / motion effects. |
| `higgsfield_summary.csv` | CSV | Cross-tab counts by tool type, model, style, subject, section, source, confidence. |
| `higgsfield_prompt_dataset.pdf` | PDF | 83-page formatted export — summary tables, then the full catalogue grouped by tool type with prompt, "Creates:" description, model, style/subject tags and source URL. |
| `higgsfield_prompt_dataset.json` | JSON | The dataset as structured records, for programmatic use. |
| `all_urls.txt`, `known3.txt` | Text | The sitemap URL list and the final crawl frontier. |

### Column reference

`record_type` · `name` · `prompt_text` · `description` · `model_or_effect` · `tool_type` ·
`generation_style` · `visual_subject` · `category` · `preset_name` · `aspect_ratio` · `duration_sec` ·
`quality` · `badges` · `word_count` · `char_count` · `confidence` · `site_section` ·
`extraction_source` · `media_url` · `source_url`

---

## 7. Reproducing

```bash
cd tools
python3 crawl.py all_urls.txt     # fetch sitemap corpus  -> pages/
python3 discover.py               # link discovery        -> discovered.txt
python3 master.py                 # run all 6 extractors  -> raw_rows.json
python3 clean.py                  # dedupe + categorise   -> dataset.json
python3 build_csv.py && python3 build_xlsx.py && python3 build_pdf.py
```

Requires `openpyxl` and `reportlab` for the Excel and PDF builders; the crawl and extraction stages use
only the standard library.

---

## 8. Known limitations

These are real gaps, stated plainly rather than papered over:

1. **Client-side pagination was not fully drained.** The Academy Prompt Bank advertises **46** camera
   movements; **24** ship in the server-rendered payload and the remaining 22 load from a client-side
   API on scroll. Headless Chromium is installed in this environment but every navigation to
   higgsfield.ai failed with `ERR_CONNECTION_RESET` — the sandbox's egress proxy closes the browser's
   tunnels mid-exchange (`ws_closed_mid_exchange`), while plain `curl` succeeds. `?category=` query
   variants do not change the server-rendered slice, so those 22 could not be reached. The same ceiling
   applies to infinite-scroll community feeds: `soul-community` exposes `total: 148` items and 78
   survived extraction and dedup.
2. **Seedance 2.5 community items carry no prompt in SSR.** That feed ships `jobId`/`media` only;
   prompt text is fetched per item client-side, so those records appear via other pages instead.
3. **33 mixed-media presets have only boilerplate descriptions.** The site serves a generic
   "Generate unique AI videos and images with creative presets…" string for them; rather than pass that
   off as a real description, it is nulled out.
4. **383 records have no attributable model.** These come from model-agnostic blog and academy pages.
   Where the URL names a model (`/blog/seedance-2-5-prompting-guide`) it is inferred; otherwise the
   field is left empty rather than guessed.
5. **63 Low-confidence records remain** after an explicit marketing-copy filter. They are retained
   rather than silently dropped, and are flagged in the `confidence` column.

---

## 9. Provenance

All content was retrieved from publicly accessible pages on higgsfield.ai on 2026-09-04, honouring
`robots.txt`. Prompt text, preset names and effect descriptions are Higgsfield's and their creators';
this dataset is a structured index of public material, assembled for research and analysis. Community
prompts were authored by the site's users and appear on public community pages.
