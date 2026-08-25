# To Please the Guru — book build pipeline

This folder turns the markdown chapter files in `../../chapters/` plus the
cover images in the project root into the complete, print-ready book PDF:
`../to-please-the-guru-COMPLETE-print.pdf`.

If you're an AI assistant picking this up on a new machine: read this whole
file before touching anything. It explains what the pipeline does, why it's
built this way (including some real bugs that were fought and worked around),
and how to safely extend it. Don't rebuild this from scratch — run it.

## Quick start

```bash
cd complete_book/pipeline
python3 generate_book.py
```

That's it. It takes about 60–90 seconds and prints progress for each stage.
The finished PDF lands at `complete_book/to-please-the-guru-COMPLETE-print.pdf`.
Re-run it any time chapter files change — it always reflects whatever is
currently on disk in `chapters/`, nothing is cached or hand-edited.

### Requirements

- **Python 3** with three pip packages: `pypdf`, `reportlab`, and `pymupdf`
  (`python3 -m pip install pypdf reportlab pymupdf`)
- **Google Chrome or Chromium installed locally.** This is the actual PDF
  renderer — see "Why Chrome" below. `build.py` auto-detects it in the usual
  install locations for macOS/Linux/Windows. If it can't find it, set:
  ```bash
  export CHROME_PATH="/path/to/chrome-or-chromium-binary"
  ```
- **Internet access at build time.** The page CSS pulls Noto Serif, Noto
  Serif Display, and Cinzel from Google Fonts via a `<link>` tag. No
  internet = fonts silently fall back to whatever's installed locally and
  the diacritics (ā, ī, ṛ, ṣ, ṇ, ś, ṭ, ḍ, ṁ, ḥ...) may not render correctly.

## What the book actually is

- Trim size: 6in × 9in, standard trade paperback.
- Print-safe: pure black/dark-gray ink on white, no color fills anywhere
  (grayscale tints are fine and used sparingly — see the Personal Prayer
  page). This was a deliberate choice: KDP/IngramSpark-style POD printers
  charge dramatically more per copy the moment *any* page has non-black
  ink, even a single tinted box. Keeping the whole interior true grayscale
  keeps it in the cheap "black & white interior" pricing tier.
- Mirrored gutter margins (bigger inner margin on the spine side, smaller
  outer margin), alternating running headers (book title on left-hand
  pages, current chapter title on right-hand pages), centered footer page
  numbers — except on Personal Prayer pages, which deliberately have
  neither, to maximize writing space (see below).
- Each chapter ends with a Heart Check (reflection questions with ruled
  writing lines) and, where the source has one, a full-page Personal
  Prayer with ruled lines for the reader to write an actual prayer by hand.

## Pipeline architecture

```
chapter_N_title-clean.md  ──┐
                             ├──► parse_chapter.py ──► render_chapter.py ──► chap_NN.pdf
front_matter.py (hardcoded  ─┘         (parser)          (HTML template)
  prose, see below)
back_matter.py  (hardcoded  ──► front_matter.pdf / back_matter.pdf
  prose, see below)
front-cover.png / back-cover.png ──► render_covers.py ──► front_cover.pdf / back_cover.pdf

chapters_meta.json (page counts per chapter, written by render_all_chapters.py)
        │
        ▼
toc.py ──► toc.pdf (page numbers computed from chapters_meta.json)
        │
        ▼
assemble.py: merges front_cover + front_matter + toc + all chap_NN.pdf +
             back_matter + back_cover into one PDF, stamping running
             headers/footers and the mirrored-gutter horizontal shift on
             every page except covers and Personal Prayer pages.
        │
        ▼
complete_book.pdf  (copied by generate_book.py to
                     ../to-please-the-guru-COMPLETE-print.pdf)
```

### File-by-file

- **`build.py`** — the shared design system. Defines `CSS` (one big
  stylesheet string used by every page type), `doc()` (wraps a body-HTML
  fragment in a full `<html>` with that CSS and the Google Fonts link),
  and `render_pdf()` (writes the HTML to disk and shells out to headless
  Chrome with `--print-to-pdf` to turn it into a PDF). Also auto-detects
  the Chrome binary (`find_chrome()`).

- **`parse_chapter.py`** — a small markdown-ish parser tailored to the
  actual (messy, inconsistent) structure of the chapter files. See
  "Source file quirks" below for exactly what it has to tolerate. Exposes
  `parse_chapter(md_text, chap_num) -> dict` with keys: `title`,
  `opener_html`, `sections_html`, `hc_html` (Heart Check), `has_hc`,
  `refs_html`, `prayer_title`, `prayer_prompt`, `salut`, `has_prayer`.

- **`render_chapter.py`** — takes that parsed dict and wraps it in the
  chapter-level HTML structure (opener with drop cap, roman-numeral
  chapter number, Part label, Heart Check block, full-page Prayer block),
  then calls `build.render_pdf()`. Also assigns each chapter to Part
  One/Two/Three by number range (`part_label_for()`) and its roman
  numeral (`ROMAN` list).

- **`render_all_chapters.py`** — loops over every
  `chapters/chapter_*-clean.md` file (sorted numerically), calls
  `render_chapter.render()` on each, and writes `chapters_meta.json`
  (list of `{num, title, header, pages, pdf}` — this is what the TOC
  page-number computation and the running-header text both read from
  later).

- **`front_matter.py`** — the title page, copyright page, dedication,
  acknowledgements, preface, and introduction. **The prose text here is
  hardcoded as Python string constants**, not parsed from a markdown
  file — it was transcribed once from
  `chapters/to_please_the_guru_front_matter-v4.md` /
  the old assembled manuscript. If you want to change this wording, edit
  the strings directly in this file (or extend it to parse from a source
  markdown file the way chapters do — nobody's built that yet).

- **`back_matter.py`** — same idea for the Author Biography and In
  Memoriam pages, hardcoded from `chapters/to_please_the_guru_back_matter-v4.md`.

- **`toc.py`** — builds the Table of Contents HTML. Deliberately
  **headings only** (chapter number + title), no sub-bullets — this was
  an explicit user preference, not an oversight. Three hardcoded Part
  ranges/labels live in `PARTS` at the top of the file: `(1,7,"Part One",
  "The Foundation of Devotion")`, `(8,16,"Part Two","The Internal
  Battle")`, `(17,22,"Part Three","The Offering")`. If the chapter count
  or part structure ever changes, update this list (and the identical
  logic in `render_chapter.py`'s `part_label_for()` — yes, it's
  duplicated in two places; see "Known rough edges" below).

- **`render_covers.py`** — takes `front-cover.png` / `back-cover.png` from
  the project root and wraps each in a zero-margin 6×9in HTML page with
  `object-fit:cover`, then renders via the same Chrome pipeline. These
  are pre-designed cover images (not generated by this pipeline) — if you
  need new cover art, replace those two PNGs and re-run.

- **`assemble.py`** — the final merge pass. Uses `pypdf` to concatenate
  every section's PDF in order, and for every non-cover, non-prayer page:
  applies a small horizontal `Transformation` (the mirrored-gutter shift,
  ±0.15in depending on whether the page number is odd/even) and stamps a
  running header + footer page number using `reportlab` drawn directly
  onto a blank overlay page, then `merge_page()`s that overlay onto the
  real content page. Computes chapter start-page numbers, iterating the
  TOC render up to 3 times because the TOC's own page count depends on
  how many digits the page numbers are, which depends on... the TOC's
  page count. It always converges in 1–2 iterations for a book this size.
  After the merge, it also adds a **PDF outline (sidebar bookmarks)** —
  Part > Chapter, nested — via `writer.add_outline_item()`, and makes the
  **Table of Contents page itself clickable**: it opens the rendered
  `toc.pdf` with PyMuPDF, searches each page for the literal chapter-title
  text to get its bounding box, converts that box from PyMuPDF's
  top-left-origin coordinates to PDF's bottom-left-origin coordinates, and
  drops a `pypdf.annotations.Link` spanning the full row width (not just
  the title text) that jumps to that chapter's first page. If a chapter's
  title text can't be found on the TOC page (e.g. it was hand-edited to
  render differently than the string in `chapters_meta.json`), this prints
  a `WARNING: could not locate TOC row for linking: ...` and just skips
  that one row's hyperlink rather than failing the whole build — the PDF
  still comes out fine, just with one non-clickable TOC row you can go
  find and fix.

## Why headless Chrome instead of a "real" PDF library

Early attempts used `weasyprint`, but it needs system-level `pango`/`cairo`/
`gobject` libraries that weren't installed and would have required a `brew
install` detour. Headless Chrome was already on the machine, understands
modern CSS (flexbox, `page-break-*`, Google Fonts) far better than most
lightweight HTML-to-PDF libraries, and "printing" a normal web page is
exactly the mental model this whole design system is built around. The
tradeoff is the print-CSS pagination quirks documented below.

## Chrome print-CSS gotchas (read this before touching page-break CSS)

These cost real debugging time. Don't reintroduce them.

1. **Negative margins near a forced page-break silently eat content.**
   The Personal Prayer page (`.prayer-page` in `build.py`) originally tried
   to reclaim the unused header/footer margin space by giving the element
   right after `page-break-before: always` a *negative* margin (to bleed
   upward/downward into the normal margin area, since that page has no
   running header to protect). Result: Chrome would silently drop that
   element's *first child* from the rendered output — no error, it just
   vanishes — regardless of which side the negative margin was on or how
   small it was. This is a genuine Chrome print-pagination bug, not
   something fixable from CSS. **Do not add negative margins to any
   element with `page-break-before`/`page-break-after` set.** The current
   code uses `margin: 0` on `.prayer-page` and instead maximizes writing
   space by shrinking the header block (small eyebrow/title/prompt) and
   picking a tight but legible line-height (23pt per ruled line) — tuned
   by literally measuring rendered PDF geometry (see next point) until 13
   lines fit on one page without overflow.

2. **Verify page-fit by measuring actual PDF geometry, not by guessing.**
   When tuning "does N lines of content fit on one page", the reliable
   method is: render, then open the PDF and inspect real coordinates.
   `pypdf`'s `page.extract_text()` is good enough to check *whether* text
   like "aspiring servant" (the prayer page's closing line) appears on the
   same page as the prayer title — if it doesn't, content overflowed to a
   second page. For precise vertical positions, PyMuPDF (`fitz`)'s
   `page.get_drawings()` returns exact rectangle coordinates for borders/
   rules, which is how the line-spacing was dialed in. This is also how
   `assemble.py` finds each chapter title's text box on the rendered
   `toc.pdf` to place a clickable link over it (see "Clickable TOC and
   bookmarks" below) — so `pymupdf` **is** a real pipeline dependency now
   (`python3 -m pip install pymupdf`), not just a debugging tool.

3. **Letter-spaced text breaks naive substring checks.** Several headings
   use `letter-spacing` + `text-transform:uppercase` (the small-caps
   running heads, "REFERENCES", "MY PERSONAL PRAYER", etc). When text is
   extracted from the resulting PDF (via `pypdf` or `fitz`), it often
   comes back with extra whitespace inserted between letters, e.g. `"M Y
   P E R S O N A L P R AY E R"`. A check like `"PERSONAL PRAYER" in
   text.upper()` will silently and wrongly return `False`. If you need to
   detect a letter-spaced heading in extracted text, strip spaces first:
   `text.upper().replace(" ", "") ` then check for the squashed substring.
   This bit twice while building this pipeline — don't repeat it.

## Source file quirks `parse_chapter.py` has to handle

The `chapters/chapter_N_title-clean.md` files were produced over a long,
messy editorial process and are **not** uniformly formatted. The parser
has to tolerate all of the following simultaneously (confirmed present
across the 22 files as of this writing):

- Body section headings are inconsistently `## **Heading**` in some
  chapters and `### **Heading**` in others — the parser treats both the
  same (`#{2,3}\s*\*\*(.+?)\*\*`).
- The page-break marker meant to be `\newpage` is sometimes literally
  spelled that way, and sometimes corrupted to `ewpage` (missing the
  leading `n` — almost certainly a literal `\n` being interpreted as an
  actual newline somewhere upstream, leaving just `ewpage` behind). The
  parser's newpage-detection regex matches `\\?newpage|ewpage` to catch
  both. There's a **separate** cleanup regex (`_clean()`) that also strips
  stray leftover `ewpage`/`newpage` lines and lone pictograph/emoji
  characters (like a stray ✍️ or 📕) that sometimes end up floating in the
  text between sections — these are source artifacts, not content.
- The Personal Prayer heading wording varies: `**My Personal Prayer:
  Title**`, `**My Sincere Prayer: Title**`, or — in several chapters —
  **no heading at all**, just a bare instruction sentence with no bold
  title. The parser tries both wordings and falls back to rendering with
  no title (just the "My Personal Prayer" eyebrow label) rather than
  inventing one.
- **Some chapters have no Heart Check and/or no Personal Prayer section
  at all** (confirmed: Chapter 4 has neither; Chapters 9, 11, 20, 22 have
  a Heart Check but no Prayer). This is a real content gap in the source,
  not a parser bug — `render_chapter.py` checks `has_hc` / `has_prayer`
  and simply omits the block rather than rendering something broken or
  fabricated. **Don't "fix" this by inventing reflection questions or
  prayer prompts** — if the source doesn't have one, the chapter is built
  without one; flag it to a human editor instead.
- References sections are inconsistently `## References` vs
  `## **References**` (the regex tolerates optional surrounding `**`), and
  are formatted either as bracketed `[1] text` blocks separated by blank
  lines, or as a plain markdown numbered list (`1. text`). Only about 9 of
  the 22 chapters currently have a References section at all — again a
  real content gap, not a bug.
- Inline citation markers like `[1]` or `[12, 13]` in body text are
  converted to small superscript numbers automatically (`md_inline()`'s
  bracket regex) — this is cosmetic only, it does not attempt to
  cross-check that the number actually matches an entry in that
  chapter's References list.
- Heart Check bullet items come in several shapes that get classified
  differently by `classify_bullet()` in `parse_chapter.py`:
  - A short bold label immediately followed by a blank
    (`**The Devotee:** ___________`) → rendered as one compact **inline**
    blank on the same line.
  - A label + explanatory sentence + blank at the very end
    (`**The Act of Service:** identify one small... : ___________`) →
    rendered as the sentence followed by **two full ruled lines**
    underneath (the blank marker itself is discarded — its only job was
    signaling "this needs real writing space").
  - A label with no question mark and no blank at all (e.g. `**The
    Commitment:** next time you offer obeisances, take five slow...`) →
    treated as an instruction, not a question — rendered as plain text
    with **no ruled lines** (nothing to answer).
  - Anything else with no blank marker (most plain questions ending in
    `?`) → two full ruled lines.
  - A bare numbered list with no label at all (`1. ___________`, as in
    "write your last three prayers") → each number becomes its own
    `hc-item.numbered` with **one** ruled line (see the `numbered` CSS
    modifier in `build.py`, which swaps the usual ◆ bullet for the
    literal number via `content: attr(data-n) "."`).
  If you add a new chapter with a Heart Check shape that doesn't fit any
  of these, extend `classify_bullet()` rather than hand-writing that
  chapter's HTML — the whole point of this pipeline is that no chapter
  is hand-transcribed.

## Design tokens (if you need to adjust the look)

Everything visual lives in the one `CSS` string at the top of `build.py`.
Notable pieces if you need to retune:

- `@page` — trim size and margins (currently 6in×9in,
  0.7in/0.6in/0.75in/0.6in top/right/bottom/left).
- `.chap-num`, `.chap-title`, `.part-label` — chapter opener typography.
- `.hc-block`, `.hc-item`, `.hc-lines` — Heart Check question/answer
  styling; `.hc-item.numbered` and `.hc-item.plain` are modifier classes.
- `.inline-blank` — the short inline fill-in blank (width is set per-use
  via an inline `style="width:...in"` on the span).
- `.prayer-page`, `.prayer-frame`, `.prayer-lines .fill-rule` — the
  full-page prayer layout. `.fill-rule` height (currently 23pt) is the
  main lever for "how much writing room per line" — see the Chrome
  negative-margin gotcha above before trying to reclaim more space by
  bleeding into the margins.
- `.toc-*`, `.fm-*` — Table of Contents and front/back-matter typography.
- Fonts: **Noto Serif** (body), **Noto Serif Display** (headings/drop
  caps — chosen together because both are from the same type family and
  guarantee full IAST diacritic coverage, unlike most display faces),
  **Cinzel** (small-caps labels/eyebrows). Loaded via Google Fonts in
  `build.doc()`. The three `.ttf` files in `fonts/` are only used for the
  reportlab-drawn running-header/footer stamps in `assemble.py` (which
  can't use webfonts) — if you change the CSS fonts, you may also want to
  download matching weights into `fonts/` for stamp consistency, though
  currently the header/footer intentionally uses plain NotoSerif-Regular
  regardless of the CSS font choice (see gotcha #3's sibling issue: the
  header text needs full diacritic coverage since chapter titles contain
  Sanskrit diacritics, so Cinzel — which doesn't cover them — was dropped
  in favor of NotoSerif-Regular for the stamped overlay text specifically).

## Known rough edges / things a future session should probably fix

- Part-number/range logic (`(1,7)`, `(8,16)`, `(17,22)`) is duplicated
  between `toc.py`'s `PARTS` and `render_chapter.py`'s `part_label_for()`.
  Should be a single shared source of truth if the part structure ever
  changes.
- Front/back matter prose is hardcoded Python strings, not parsed from a
  markdown source — if the front-matter markdown files get edited,
  `front_matter.py`/`back_matter.py` will silently go stale. Consider
  having them parse from `chapters/to_please_the_guru_front_matter-v4.md`
  the same way chapters are parsed, if that file starts being maintained.
- Page numbering is one continuous Arabic sequence from the title page
  (page 1) through the back matter — traditional print books usually use
  roman numerals for front matter and restart Arabic numbering at Chapter
  1. This was a deliberate simplification for time, not a considered
  final choice — flag to the user before shipping to a real printer.
- The whole book is regenerated every run (~60–90s) — there's no
  incremental "only re-render the chapter that changed" mode. Fine at
  this scale (22 chapters), would need restructuring if this pattern were
  reused for a much longer book.
- `complete_book.pdf` (and everything else in `pipeline/build/`) is
  build output, not source — safe to delete/regenerate any time, and
  probably belongs in a `.gitignore` if this project ever becomes a git
  repo.
