import build, parse_chapter

ROMAN = ["", "I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII",
         "XIV","XV","XVI","XVII","XVIII","XIX","XX","XXI","XXII"]

def part_label_for(chap_num):
    if chap_num <= 7:
        return "Part One", "The Foundation of Devotion"
    if chap_num <= 16:
        return "Part Two", "The Internal Battle"
    return "Part Three", "The Offering"

PRAYER_LINES = 13

def render(md_text, chap_num, out_pdf):
    parsed = parse_chapter.parse_chapter(md_text, chap_num)
    part_num, part_name = part_label_for(chap_num)
    numeral = ROMAN[chap_num]
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
