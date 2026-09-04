import json, collections, html, re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, PageBreak, KeepTogether)
from reportlab.lib.enums import TA_LEFT

d = json.load(open("dataset.json"))
INK = colors.HexColor("#111827"); MUT = colors.HexColor("#6B7280")
ACC = colors.HexColor("#4F46E5"); LINE = colors.HexColor("#E5E7EB")
BG = colors.HexColor("#F9FAFB")

ss = getSampleStyleSheet()
S = {
 "h1": ParagraphStyle("h1", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=24,
                      leading=28, textColor=INK, spaceAfter=6, alignment=TA_LEFT),
 "sub": ParagraphStyle("sub", fontName="Helvetica", fontSize=10.5, leading=15,
                       textColor=MUT, spaceAfter=14),
 "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=15, leading=19,
                      textColor=INK, spaceBefore=16, spaceAfter=7),
 "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11, leading=14,
                      textColor=ACC, spaceBefore=10, spaceAfter=3),
 "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.5, leading=13.5,
                        textColor=INK, spaceAfter=6),
 "prompt": ParagraphStyle("prompt", fontName="Helvetica", fontSize=8.5, leading=12,
                          textColor=INK, backColor=BG, borderPadding=6,
                          leftIndent=2, rightIndent=2, spaceAfter=4),
 "meta": ParagraphStyle("meta", fontName="Helvetica-Oblique", fontSize=7.5, leading=10,
                        textColor=MUT, spaceAfter=10),
 "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=8, leading=10.5, textColor=INK),
 "cellb": ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=8, leading=10.5,
                         textColor=colors.white),
}

def esc(t, limit=None):
    t = re.sub(r'\s+', ' ', str(t or "")).strip()
    if limit and len(t) > limit:
        t = t[:limit].rsplit(" ", 1)[0] + " …"
    return html.escape(t)

class Doc(BaseDocTemplate):
    def __init__(self, fn):
        BaseDocTemplate.__init__(self, fn, pagesize=A4,
                                 leftMargin=17*mm, rightMargin=17*mm,
                                 topMargin=17*mm, bottomMargin=17*mm,
                                 title="Higgsfield.ai Prompt Dataset",
                                 author="Prompt extraction crawl")
        f = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="n")
        self.addPageTemplates([PageTemplate(id="all", frames=[f], onPage=self.deco)])
    def deco(self, c, doc):
        c.saveState()
        c.setStrokeColor(LINE); c.setLineWidth(0.5)
        c.line(self.leftMargin, A4[1]-13*mm, A4[0]-self.rightMargin, A4[1]-13*mm)
        c.setFont("Helvetica", 7.5); c.setFillColor(MUT)
        c.drawString(self.leftMargin, A4[1]-11.4*mm, "Higgsfield.ai — Prompt & Preset Dataset")
        c.drawRightString(A4[0]-self.rightMargin, A4[1]-11.4*mm, "higgsfield.ai")
        c.line(self.leftMargin, 13*mm, A4[0]-self.rightMargin, 13*mm)
        c.drawString(self.leftMargin, 9.5*mm, "Extracted from public pages")
        c.drawRightString(A4[0]-self.rightMargin, 9.5*mm, "Page %d" % doc.page)
        c.restoreState()

story = []
A = story.append
A(Paragraph("Higgsfield.ai Prompt &amp; Preset Dataset", S["h1"]))
A(Paragraph(f"A structured extraction of <b>{len(d):,}</b> prompts, presets and motion effects "
            f"gathered from public pages on higgsfield.ai. Each record carries its full prompt text, "
            f"a description of what it produces, the associated model or motion effect, and the "
            f"source page URL.", S["sub"]))

def ctab(title, key, split=False, top=None):
    c = collections.Counter()
    for r in d:
        v = r.get(key)
        if not v: c["(unspecified)"] += 1; continue
        if split:
            for p in str(v).split("; "): c[p] += 1
        else: c[str(v)] += 1
    items = c.most_common(top)
    rows = [[Paragraph(f"<b>{esc(title)}</b>", S["cellb"]), Paragraph("<b>Count</b>", S["cellb"])]]
    for k, v in items:
        rows.append([Paragraph(esc(k), S["cell"]), Paragraph(str(v), S["cell"])])
    t = Table(rows, colWidths=[125*mm, 20*mm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), INK),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, BG]),
        ("GRID", (0,0), (-1,-1), 0.4, LINE),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return t

A(Paragraph("1. Dataset at a glance", S["h2"]))
A(ctab("Tool type", "tool_type")); A(Spacer(1, 9))
A(ctab("Model / motion effect", "model_or_effect", top=18)); A(Spacer(1, 9))
A(ctab("Generation style", "generation_style", True)); A(Spacer(1, 9))
A(ctab("Visual subject", "visual_subject", True)); A(Spacer(1, 9))
A(ctab("Extraction source", "extraction_source"))
A(PageBreak())

# ---- catalogue section ----
A(Paragraph("2. Prompt catalogue", S["h2"]))
A(Paragraph("Records are grouped by tool type, then ordered by prompt length. Long prompts are "
            "truncated for print; the CSV and Excel exports carry the complete text.", S["body"]))

bytool = collections.defaultdict(list)
for r in d:
    bytool[r["tool_type"]].append(r)

for tool in sorted(bytool, key=lambda k: -len(bytool[k])):
    rows = bytool[tool]
    A(Paragraph(f"{esc(tool)} <font color='#6B7280'>({len(rows)} records)</font>", S["h2"]))
    for r in rows[:60]:
        head = r.get("name") or (r.get("model_or_effect") or "Prompt")
        bits = [b for b in [r.get("model_or_effect"), r.get("generation_style"),
                            r.get("visual_subject")] if b]
        blk = [Paragraph(esc(head, 110), S["h3"])]
        if r.get("prompt_text"):
            blk.append(Paragraph(esc(r["prompt_text"], 1400), S["prompt"]))
        if r.get("description"):
            blk.append(Paragraph("<b>Creates:</b> " + esc(r["description"], 600), S["body"]))
        meta = " &nbsp;•&nbsp; ".join(esc(b, 90) for b in bits)
        blk.append(Paragraph(f"{meta}<br/><font color='#4F46E5'>{esc(r['source_url'])}</font>",
                             S["meta"]))
        A(KeepTogether(blk))
    if len(rows) > 60:
        A(Paragraph(f"… and {len(rows)-60} further {esc(tool)} records — see the CSV / Excel export.",
                    S["body"]))
    A(PageBreak())

Doc("deliverables/higgsfield_prompt_dataset.pdf").build(story)
print("pdf written")
