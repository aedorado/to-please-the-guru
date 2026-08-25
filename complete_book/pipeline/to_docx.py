"""
Quick-and-simple DOCX export of the book (content-focused, not a pixel copy
of the print PDF design). Reads the same raw markdown chapter files as the
PDF pipeline, converts headings/bold/italic/lists/blockquotes to native Word
styles, and inserts a real auto-updating Word Table of Contents field.

Usage:
    cd complete_book/pipeline
    python3 to_docx.py
Output:
    ../to-please-the-guru-COMPLETE.docx
"""
import os, re, glob
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(PIPELINE_DIR, "..", ".."))
CHAPTERS_DIR = os.path.join(PROJECT_ROOT, "chapters")
OUT_PATH = os.path.abspath(os.path.join(PIPELINE_DIR, "..", "to-please-the-guru-COMPLETE.docx"))

TOKEN_RE = re.compile(r'(\*\*\*.+?\*\*\*|\*\*.+?\*\*|\*.+?\*)')

def clean_text(t):
    t = re.sub(r'(?mi)^\s*(?:\\?newpage|ewpage)\s*$', '', t)
    t = re.sub(r'[✀-➿☀-⛿\U0001F300-\U0001FAFF]', '', t)
    t = re.sub(r'''\\(['"])''', r'\1', t)
    t = re.sub(r'`?_{6,}`?', '_' * 30, t)  # keep "write here" blanks, just tidy them
    return t

def add_runs(paragraph, text):
    for part in TOKEN_RE.split(text):
        if not part:
            continue
        if part.startswith('***') and part.endswith('***'):
            r = paragraph.add_run(part[3:-3]); r.bold = True; r.italic = True
        elif part.startswith('**') and part.endswith('**'):
            r = paragraph.add_run(part[2:-2]); r.bold = True
        elif part.startswith('*') and part.endswith('*'):
            r = paragraph.add_run(part[1:-1]); r.italic = True
        else:
            paragraph.add_run(part)

def add_toc_field(doc):
    p = doc.add_paragraph()
    run = p.add_run()
    fld_begin = OxmlElement('w:fldChar'); fld_begin.set(qn('w:fldCharType'), 'begin')
    instr = OxmlElement('w:instrText'); instr.set(qn('xml:space'), 'preserve')
    instr.text = 'TOC \\o "1-2" \\h \\z \\u'
    fld_sep = OxmlElement('w:fldChar'); fld_sep.set(qn('w:fldCharType'), 'separate')
    fld_text = OxmlElement('w:t'); fld_text.text = "Right-click and choose Update Field to build the Table of Contents."
    fld_end = OxmlElement('w:fldChar'); fld_end.set(qn('w:fldCharType'), 'end')
    r_element = run._r
    r_element.append(fld_begin); r_element.append(instr); r_element.append(fld_sep)
    r_element.append(fld_text); r_element.append(fld_end)

def process_body(doc, text, base_heading_level=2):
    text = clean_text(text)
    lines = text.split("\n")
    i = 0
    buf = []

    def flush():
        if buf:
            para_text = " ".join(l.strip() for l in buf if l.strip())
            if para_text:
                p = doc.add_paragraph()
                add_runs(p, para_text)
            buf.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush(); i += 1; continue

        if stripped == "---":
            flush(); i += 1; continue

        m = re.match(r'^(#{1,4})\s*\*{0,2}(.+?)\*{0,2}\s*$', stripped)
        if m:
            flush()
            level = len(m.group(1))
            heading_text = re.sub(r'\*+', '', m.group(2)).strip()
            style_level = min(base_heading_level + level - 1, 4) if level >= 2 else 1
            h = doc.add_heading(heading_text, level=style_level if level > 1 else 1)
            i += 1; continue

        if stripped.startswith("> "):
            flush()
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip().lstrip("> ").strip())
                i += 1
            p = doc.add_paragraph(style="Intense Quote")
            add_runs(p, clean_text(" ".join(quote_lines)))
            continue

        if re.match(r'^\*\s+', stripped):
            flush()
            p = doc.add_paragraph(style="List Bullet")
            add_runs(p, re.sub(r'^\*\s+', '', stripped))
            i += 1; continue

        if re.match(r'^\d+\.\s+', stripped):
            flush()
            p = doc.add_paragraph(style="List Number")
            add_runs(p, re.sub(r'^\d+\.\s+', '', stripped))
            i += 1; continue

        if re.match(r'^\[\d+\]\s', stripped):
            flush()
            p = doc.add_paragraph(style="List Number")
            add_runs(p, re.sub(r'^\[\d+\]\s*', '', stripped))
            i += 1; continue

        buf.append(stripped)
        i += 1
    flush()

def main():
    doc = Document()

    normal = doc.styles["Normal"]
    normal.font.name = "Georgia"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(8)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    section = doc.sections[0]
    section.page_height, section.page_width = Inches(9), Inches(6)
    section.top_margin = section.bottom_margin = Inches(0.75)
    section.left_margin = section.right_margin = Inches(0.75)

    # --- Title page ---
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(180)
    r = title_p.add_run("To Please the Guru")
    r.bold = True; r.font.size = Pt(30)
    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = sub_p.add_run("Straight Talk on Surrender, Purity, and the Sweet Burn of Devotion")
    r2.italic = True; r2.font.size = Pt(14)
    doc.add_page_break()

    # --- Front matter (Acknowledgements / Preface / Introduction) ---
    fm_path = os.path.join(CHAPTERS_DIR, "to_please_the_guru_front_matter-v4.md")
    if os.path.exists(fm_path):
        fm_text = open(fm_path).read()
        # keep only Acknowledgements..Introduction; skip the markdown TOC block
        # (we generate a real Word TOC field instead) and any trailing \newpage
        toc_split = re.split(r'###\s*\*{0,2}TABLE OF CONTENTS\*{0,2}', fm_text)
        fm_text = toc_split[0]
        fm_text = re.sub(r'^#.*\n#.*\n', '', fm_text)  # drop title/subtitle lines (title page already added)
        process_body(doc, fm_text, base_heading_level=1)
        doc.add_page_break()

    # --- Table of Contents (native Word field, updates on open/F9) ---
    doc.add_heading("Table of Contents", level=1)
    add_toc_field(doc)
    doc.add_page_break()

    # --- Chapters ---
    files = sorted(
        glob.glob(os.path.join(CHAPTERS_DIR, "chapter_*-clean.md")),
        key=lambda p: int(re.search(r'chapter_(\d+)_', p).group(1)),
    )
    for f in files:
        text = open(f).read()
        m = re.match(r'#\s*Chapter\s*\d+:\s*(.+)', text.strip())
        title = m.group(1).strip() if m else os.path.basename(f)
        rest = text[m.end():] if m else text
        doc.add_heading(clean_text(title), level=1)
        process_body(doc, rest, base_heading_level=2)
        doc.add_page_break()

    # --- Back matter (Author Bio / In Memoriam only, skip jacket-flap/praise) ---
    bm_path = os.path.join(CHAPTERS_DIR, "to_please_the_guru_back_matter-v4.md")
    if os.path.exists(bm_path):
        bm_text = open(bm_path).read()
        m = re.search(r'###.*?AUTHOR BIOGRAPHY.*', bm_text, re.S)
        if m:
            bm_text = m.group(0)
            bm_text = re.split(r'###.*?PRAISE FOR', bm_text, flags=re.S)[0]
            doc.add_heading("About the Author", level=1)
            process_body(doc, bm_text, base_heading_level=2)

    doc.save(OUT_PATH)
    print("wrote", OUT_PATH)

if __name__ == "__main__":
    main()
