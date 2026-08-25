import io, json, os
import build, toc
import fitz  # PyMuPDF -- used only to locate TOC title text for clickable links
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.annotations import Link
from pypdf.generic import RectangleObject
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
pdfmetrics.registerFont(TTFont("NotoSerif-Italic", os.path.join(PIPELINE_DIR, "fonts/NotoSerif-Italic.ttf")))
pdfmetrics.registerFont(TTFont("NotoSerif-Regular", os.path.join(PIPELINE_DIR, "fonts/NotoSerif-Regular.ttf")))

BOOK_TITLE = "TO PLEASE THE GURU"
PAGE_W, PAGE_H = 432, 648
GUTTER_SHIFT = 0.15 * 72

chapters_meta = json.load(open("chapters_meta.json"))

FM_PAGES = len(PdfReader("front_matter.pdf").pages)   # 9
BM_PAGES = len(PdfReader("back_matter.pdf").pages)

def compute_start_pages(toc_pages):
    start_pages = {}
    p = FM_PAGES + toc_pages + 1
    for c in chapters_meta:
        start_pages[c["num"]] = p
        p += c["pages"]
    return start_pages, p  # p = first page after last chapter

# --- iterate TOC page count until stable ---
toc_pages_guess = 3
for _ in range(3):
    start_pages, after_chapters = compute_start_pages(toc_pages_guess)
    toc_html = toc.build_toc_html(chapters_meta, start_pages)
    html = build.doc("Table of Contents", toc_html)
    n = build.render_pdf(html, "toc.pdf")
    if n == toc_pages_guess:
        break
    toc_pages_guess = n

start_pages, after_chapters = compute_start_pages(toc_pages_guess)
print("TOC pages:", toc_pages_guess)
print("chapter start pages:", start_pages)
print("back matter starts at:", after_chapters)

def tracked(c, text, x, y, font, size, tracking, align="left"):
    c.setFont(font, size)
    widths = [c.stringWidth(ch, font, size) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1 if text else 0)
    if align == "center":
        cx = x - total / 2
    elif align == "right":
        cx = x - total
    else:
        cx = x
    for ch, w in zip(text, widths):
        c.drawString(cx, y, ch)
        cx += w + tracking

def make_overlay(page_num, is_recto, chapter_header=None):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    c.setFillColorRGB(0.30, 0.30, 0.30)
    if chapter_header is not None:
        header_y = PAGE_H - 0.5 * 72
        if is_recto:
            tracked(c, chapter_header, PAGE_W - 0.6 * 72 + GUTTER_SHIFT, header_y, "NotoSerif-Regular", 7.3, 1.3, align="right")
        else:
            tracked(c, BOOK_TITLE, 0.6 * 72 - GUTTER_SHIFT, header_y, "NotoSerif-Regular", 7.3, 1.3, align="left")
    footer_y = 0.45 * 72
    c.setFont("NotoSerif-Italic", 9)
    num = str(page_num)
    w = c.stringWidth(num, "NotoSerif-Italic", 9)
    c.drawString(PAGE_W / 2 - w / 2, footer_y, num)
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]

writer = PdfWriter()

def add_plain_pages(reader, start_num):
    """front-matter-style pages: gutter shift + page number only, no header text."""
    p = start_num
    for page in reader.pages:
        is_recto = (p % 2 == 1)
        shift = GUTTER_SHIFT if is_recto else -GUTTER_SHIFT
        page.add_transformation(Transformation().translate(tx=shift, ty=0))
        page.merge_page(make_overlay(p, is_recto, chapter_header=None))
        writer.add_page(page)
        p += 1
    return p

def add_chapter_pages(reader, chap_header, start_num):
    p = start_num
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        is_prayer_page = "aspiring servant" in text
        if not is_prayer_page:
            is_recto = (p % 2 == 1)
            shift = GUTTER_SHIFT if is_recto else -GUTTER_SHIFT
            page.add_transformation(Transformation().translate(tx=shift, ty=0))
            show_header = (i != 0)
            page.merge_page(make_overlay(p, is_recto, chap_header if show_header else None))
        writer.add_page(page)
        p += 1
    return p

# 1. front cover (no stamping)
for page in PdfReader("front_cover.pdf").pages:
    writer.add_page(page)

# 2. front matter (pages 1..FM_PAGES)
add_plain_pages(PdfReader("front_matter.pdf"), 1)

# 3. TOC
toc_writer_start = len(writer.pages)
add_plain_pages(PdfReader("toc.pdf"), FM_PAGES + 1)

# 4. chapters
chapter_writer_start = {}
for c in chapters_meta:
    chapter_writer_start[c["num"]] = len(writer.pages)
    add_chapter_pages(PdfReader(c["pdf"]), c["header"], start_pages[c["num"]])

# 5. back matter
add_plain_pages(PdfReader("back_matter.pdf"), after_chapters)

# 6. back cover
for page in PdfReader("back_cover.pdf").pages:
    writer.add_page(page)

# --- PDF outline (sidebar bookmarks): Part > Chapter, nested ---
for lo, hi, part_label, part_name in toc.PARTS:
    parent = writer.add_outline_item(f"{part_label}: {part_name}", chapter_writer_start[lo])
    for n in range(lo, hi + 1):
        c = next(x for x in chapters_meta if x["num"] == n)
        writer.add_outline_item(f"Chapter {n}: {c['title']}", chapter_writer_start[n], parent=parent)

# --- clickable TOC links: find each chapter title's text box on the
# rendered toc.pdf (via PyMuPDF) and place a pypdf Link annotation over
# the matching page, spanning the full row width, pointing at that
# chapter's first page in the final assembled document ---
toc_doc = fitz.open("toc.pdf")
for c in chapters_meta:
    target_index = chapter_writer_start[c["num"]]
    found = False
    for toc_page_i in range(len(toc_doc)):
        rects = toc_doc[toc_page_i].search_for(c["title"])
        if rects:
            r = rects[0]
            # fitz rects are top-left-origin; PDF/pypdf rects are bottom-left-origin
            pdf_y0 = PAGE_H - r.y1 - 2
            pdf_y1 = PAGE_H - r.y0 + 2
            link = Link(
                rect=RectangleObject((0.55 * 72, pdf_y0, PAGE_W - 0.45 * 72, pdf_y1)),
                target_page_index=target_index,
            )
            writer.add_annotation(page_number=toc_writer_start + toc_page_i, annotation=link)
            found = True
            break
    if not found:
        print("WARNING: could not locate TOC row for linking:", c["title"])
toc_doc.close()

with open("complete_book.pdf", "wb") as f:
    writer.write(f)

print("TOTAL PAGES IN FINAL PDF:", len(PdfReader("complete_book.pdf").pages))
