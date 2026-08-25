PARTS = [
    (1, 7, "Part One", "The Foundation of Devotion"),
    (8, 16, "Part Two", "The Internal Battle"),
    (17, 22, "Part Three", "The Offering"),
]

def build_toc_html(chapters_meta, start_pages):
    """chapters_meta: list of dicts with num,title. start_pages: dict num->page_num"""
    out = ['<div class="toc-page"><h2 class="fm-heading">Table of Contents</h2>']
    by_num = {c["num"]: c for c in chapters_meta}
    for lo, hi, part_label, part_name in PARTS:
        out.append(f'<p class="toc-part">{part_label} &middot; {part_name}</p>')
        out.append('<ul class="toc-list">')
        for n in range(lo, hi + 1):
            c = by_num[n]
            page = start_pages.get(n, "")
            out.append(
                f'<li><span class="toc-num">{n}.</span> '
                f'<span class="toc-title">{c["title"]}</span>'
                f'<span class="toc-dots"></span>'
                f'<span class="toc-page-num">{page}</span></li>'
            )
        out.append('</ul>')
    out.append('</div>')
    return "".join(out)
