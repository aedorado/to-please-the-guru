# PARTS lives in render_chapter.py (single source of truth, shared with the
# chapter-opener "Part X" label) -- imported here rather than duplicated so
# the two can't drift out of sync when chapters are added/removed.
from render_chapter import PARTS

def build_toc_html(chapters_meta, start_pages):
    """chapters_meta: list of dicts with num,title. start_pages: dict num->page_num"""
    out = ['<div class="toc-page"><h2 class="fm-heading">Table of Contents</h2>']
    by_num = {c["num"]: c for c in chapters_meta}
    covered = set()
    for lo, hi, part_label, part_name in PARTS:
        nums_here = [n for n in range(lo, hi + 1) if n in by_num]
        covered.update(nums_here)
        if not nums_here:
            continue
        out.append(f'<p class="toc-part">{part_label} &middot; {part_name}</p>')
        out.append('<ul class="toc-list">')
        for n in nums_here:
            c = by_num[n]
            page = start_pages.get(n, "")
            out.append(
                f'<li><span class="toc-num">{n}.</span> '
                f'<span class="toc-title">{c["title"]}</span>'
                f'<span class="toc-dots"></span>'
                f'<span class="toc-page-num">{page}</span></li>'
            )
        out.append('</ul>')
    missing = sorted(set(by_num) - covered)
    if missing:
        print(f"WARNING: chapters not covered by any PARTS range, omitted from TOC: {missing}")
    out.append('</div>')
    return "".join(out)
