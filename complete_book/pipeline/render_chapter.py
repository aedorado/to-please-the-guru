import build, parse_chapter

_ROMAN_TABLE = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
    (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
]

def to_roman(n):
    """Converts any positive int to a roman numeral. Not limited to a fixed
    chapter count -- the source has been renumbered/expanded mid-project
    before (22 -> 24 chapters), so this must never hardcode an upper bound."""
    out = []
    for value, symbol in _ROMAN_TABLE:
        count, n = divmod(n, value)
        out.append(symbol * count)
    return "".join(out)

# Part groupings, by chapter-number range. THE SINGLE SOURCE OF TRUTH for
# this -- toc.py imports PARTS from here rather than keeping its own copy,
# so the two can never drift out of sync again. Update this list (not a
# copy elsewhere) if chapters are added/removed/reordered.
PARTS = [
    (1, 7,   "Part One",   "The Foundation of Devotion"),
    (8, 18,  "Part Two",   "The Internal Battle"),
    (19, 24, "Part Three", "The Offering"),
]

def part_label_for(chap_num):
    for lo, hi, part_num, part_name in PARTS:
        if lo <= chap_num <= hi:
            return part_num, part_name
    # chapter number falls outside every configured range (book grew again) --
    # fail loudly rather than silently mislabeling it into the wrong part.
    raise ValueError(
        f"Chapter {chap_num} doesn't fall into any range in PARTS "
        f"(currently {PARTS[0][0]}-{PARTS[-1][1]}). Update PARTS in "
        f"render_chapter.py to cover the new chapter count."
    )

PRAYER_LINES = 13

def render(md_text, chap_num, out_pdf):
    parsed = parse_chapter.parse_chapter(md_text, chap_num)
    part_num, part_name = part_label_for(chap_num)
    numeral = to_roman(chap_num)
    lines_html = '<span class="fill-rule"></span>' * PRAYER_LINES

    hc_block = parsed['hc_html'] if parsed['has_hc'] else ""
    title_html = f'<div class="prayer-title">{parsed["prayer_title"]}</div>' if parsed.get('prayer_title') else ""
    prayer_block = f"""
<div class="prayer-page">
 <div class="prayer-frame">
  <div class="prayer-eyebrow">My Personal Prayer</div>
  {title_html}
  <p class="prayer-prompt">{parsed['prayer_prompt']}</p>
  <p class="prayer-salut">{parsed['salut']}</p>
  <div class="prayer-lines">
    {lines_html}
  </div>
  <div class="prayer-close">&mdash; your aspiring servant</div>
 </div>
</div>
""" if parsed['has_prayer'] else ""

    body = f"""
<div class="opener">
  <div class="part-label">{part_num} &middot; {part_name}</div>
  <div class="chap-num">{numeral}</div>
  <div class="chap-rule"></div>
  <div class="chap-title">{parsed['title']}</div>
  {parsed['opener_html']}
</div>
{parsed['sections_html']}
{parsed['refs_html']}
{hc_block}
{prayer_block}
"""
    html = build.doc(f"Chapter {chap_num}", body)
    n = build.render_pdf(html, out_pdf)
    return n, parsed['title'], f"CHAPTER {numeral}  ·  {parsed['title'].upper()}"
