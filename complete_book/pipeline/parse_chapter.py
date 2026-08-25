import re

def md_inline(text):
    text = text.strip()
    # bold+italic ***text***
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = text.replace('--', '&mdash;')
    text = re.sub(r'\[(\d+(?:,\s*\d+)*)\]', lambda m: ''.join(f'<sup class="cite">{n.strip()}</sup>' for n in m.group(1).split(',')), text)
    return text

BLANK_RE = re.compile(r'`?_{8,}`?\s*')

def split_blank(text):
    """Return (before, after, had_blank)."""
    m = BLANK_RE.search(text)
    if not m:
        return text, None, False
    before = text[:m.start()].rstrip()
    after = text[m.end():].strip()
    return before, after, True

def strip_label(before):
    """If `before` is a short bold label ending in ':' return (label_html, rest) else (None, before)."""
    m = re.match(r'^\*\*(.+?):\*\*\s*(.*)$', before)
    if m:
        label, rest = m.group(1), m.group(2).strip()
        return label, rest
    return None, before

def classify_bullet(raw):
    """raw = bullet text without leading '* ' """
    before, after, had_blank = split_blank(raw)
    label, rest = strip_label(before)
    if had_blank and after:
        # inline blank with trailing text, e.g. "Total: ___ hours."
        width = "0.9in" if len(after) < 12 else "1.6in"
        html = ""
        if label:
            html += f'<span class="commitment">{md_inline(label)}:</span> '
            if rest:
                html += md_inline(rest) + ' '
        else:
            html += md_inline(before) + ' '
        html += f'<span class="inline-blank" style="width:{width};"></span> {md_inline(after)}'
        return ("inline", html)
    if had_blank and not after:
        word_count = len(re.sub(r'[^\w\s]', '', rest if label else before).split())
        if label and word_count <= 3:
            html = f'<span class="commitment">{md_inline(label)}:</span> <span class="inline-blank" style="width:2.4in;"></span>'
            return ("inline", html)
        # long blank -> full lines, blank discarded
        if label:
            html = f'<span class="commitment">{md_inline(label)}:</span> {md_inline(rest)}'.strip()
            if html.endswith(':</span>'):
                html = html
        else:
            html = md_inline(before)
        return ("lines", html)
    # no blank at all -> question/statement
    if label:
        html = f'<span class="commitment">{md_inline(label)}:</span> {md_inline(rest)}'
        # "commitment"-style instructions (non-question, e.g. "The Commitment:") get no lines
        is_question = rest.rstrip().endswith('?')
        return ("lines" if is_question else "plain", html)
    return ("lines", md_inline(before))

def render_bullet(raw):
    kind, html = classify_bullet(raw)
    if kind == "inline":
        return f'<p class="hc-item plain">{html}</p>\n'
    if kind == "plain":
        return f'<p class="hc-item plain">{html}</p>\n'
    # lines
    return f'<p class="hc-item">{html}</p>\n<ol class="hc-lines"><li></li><li></li></ol>\n'

def parse_heartcheck(hc_text, chap_num):
    out = [f'<div class="hc-block">\n<p class="hc-eyebrow">Chapter {chap_num} &middot; Heart Check</p>\n']
    # split into subsections by ### headings
    parts = re.split(r'\n###\s*\*{0,2}(.+?)\*{0,2}\s*\n', hc_text)
    # parts[0] is anything before first heading (usually empty)
    i = 1
    while i < len(parts):
        heading = parts[i]
        body = parts[i+1] if i+1 < len(parts) else ""
        out.append(f'<h4>{md_inline(heading)}</h4>\n')
        lines = [l for l in body.split("\n")]
        buf_intro = []
        j = 0
        num_counter = 0
        while j < len(lines):
            line = lines[j].strip()
            if not line:
                j += 1
                continue
            if re.match(r'^(?:newpage|ewpage)$', line, re.I) or not re.search(r'[A-Za-z]', line):
                j += 1
                continue
            if line.startswith("* "):
                out.append(render_bullet(line[2:].strip()))
            elif re.match(r'^\d+\.\s', line):
                num_counter += 1
                raw = re.sub(r'^\d+\.\s*', '', line)
                before, after, had_blank = split_blank(raw)
                if before:
                    out.append(f'<p class="hc-item numbered" data-n="{num_counter}">{md_inline(before)}</p>\n<ol class="hc-lines one"><li></li></ol>\n')
                else:
                    out.append(f'<p class="hc-item numbered" data-n="{num_counter}"></p>\n<ol class="hc-lines one"><li></li></ol>\n')
            else:
                out.append(f'<p style="font-size:10.2pt; margin-bottom:8pt;">{md_inline(line)}</p>\n')
            j += 1
        i += 2
    out.append('</div>\n')
    return "".join(out)

def parse_prayer(text):
    # title wording varies: "My Personal Prayer: X" / "My Sincere Prayer: X" /
    # sometimes no title at all, just a plain instruction line
    m = re.search(r'\*\*My (?:Personal|Sincere) Prayer:\s*(.+?)\*\*', text)
    title = m.group(1).strip() if m else None
    rest = text[m.end():] if m else text
    lines = [l.strip() for l in rest.split("\n") if l.strip()]
    # first non-empty line(s) until salutation "My Dear ...," is the prompt
    prompt_lines = []
    salut = None
    for l in lines:
        if re.match(r'^My Dear .+,\s*$', l):
            salut = l.strip()
            break
        prompt_lines.append(l)
    prompt = " ".join(prompt_lines).strip("*").strip()
    return title, md_inline(prompt), (salut or "My Dear Gurudev,")

def parse_references(text):
    items = []
    # try "[n] text" blocks separated by blank lines
    bracket_items = re.findall(r'\[\d+\]\s*(.+?)(?=\n\[\d+\]|\Z)', text, re.S)
    if bracket_items:
        items = [i.strip().replace("\n", " ") for i in bracket_items]
    else:
        # numbered list "1. text"
        items = re.findall(r'^\d+\.\s*(.+)$', text, re.M)
    html = ['<div class="refs">\n<p class="refs-label">References</p>\n<ol>\n']
    for it in items:
        it = it.replace("(http", " &mdash; <span class=\"url\">http").rstrip()
        if '<span class="url">' in it:
            it = it.rstrip(')') + '</span>'
        html.append(f'<li>{md_inline(it)}</li>\n')
    html.append('</ol>\n</div>\n')
    return "".join(html)

def parse_body_sections(body_text):
    """Split into opener paragraphs + list of (heading, html) sections."""
    # normalize heading markers: allow ## or ### with ** **
    heading_re = re.compile(r'\n#{2,3}\s*\*{0,2}(.+?)\*{0,2}\s*\n')
    pieces = heading_re.split(body_text)
    opener_raw = pieces[0]
    sections = []
    i = 1
    while i < len(pieces):
        heading = pieces[i]
        content = pieces[i+1] if i+1 < len(pieces) else ""
        sections.append((heading.strip(), content))
        i += 2
    return opener_raw, sections

def render_paragraphs(raw, drop_first=False):
    raw = raw.replace("---", "")
    blocks = [b.strip() for b in raw.split("\n\n") if b.strip()]
    out = []
    for idx, b in enumerate(blocks):
        lines = b.split("\n")
        if all(l.strip().startswith(">") for l in lines):
            verse_lines = [md_inline(l.strip().lstrip("> ").strip()) for l in lines]
            out.append(f'<div class="verse">{"<br>".join(verse_lines)}</div>\n')
            continue
        if re.match(r'^\d+\.\s', lines[0]):
            items = []
            for l in lines:
                l = l.strip()
                m = re.match(r'^\d+\.\s*(.+)$', l)
                if m:
                    items.append(f'<li>{md_inline(m.group(1))}</li>')
            out.append('<ol class="content-list">' + "".join(items) + '</ol>\n')
            continue
        text = " ".join(l.strip() for l in lines)
        cls = ' class="drop"' if (drop_first and idx == 0) else ""
        out.append(f'<p{cls}>{md_inline(text)}</p>\n')
    return "".join(out)

def _clean(text):
    text = re.sub(r'(?mi)^\s*(?:\\?newpage|ewpage)\s*$', '', text)
    text = re.sub(r'[✀-➿☀-⛿\U0001F300-\U0001FAFF]', '', text)
    # stray markdown escape sequences left over from source cleanup, e.g. Guru\'s -> Guru's
    # (deliberately narrow: only quote marks, not \* or \_ which could be genuine
    # escaped emphasis markers that must NOT be unescaped before md_inline runs)
    text = re.sub(r'''\\(['"])''', r'\1', text)
    return text

def parse_chapter(md_text, chap_num):
    # title
    m = re.match(r'#\s*Chapter\s*\d+:\s*(.+)', md_text.strip())
    title = m.group(1).strip() if m else f"Chapter {chap_num}"
    md_text = md_text[m.end():] if m else md_text

    # locate heart check heading
    hc_m = re.search(r'##\s*\*\*Chapter\s*\d+:\s*Heart Check\*\*', md_text)
    body_text = md_text[:hc_m.start()] if hc_m else md_text
    rest = md_text[hc_m.end():] if hc_m else ""

    # locate references independently first -- it may appear with or without
    # a prayer section before it, so pull it out before splitting hc/prayer
    ref_m = re.search(r'##\s*\*{0,2}References\*{0,2}', rest)
    rest_before_refs = rest[:ref_m.start()] if ref_m else rest
    ref_text = rest[ref_m.end():] if ref_m else ""

    # split heart-check vs. prayer on the FIRST \newpage marker (present in
    # every chapter that has a prayer section, even when wording of the
    # prayer heading itself varies chapter to chapter)
    newpage_m = re.search(r'\\?newpage|ewpage', rest_before_refs, re.I)
    hc_text = rest_before_refs[:newpage_m.start()] if newpage_m else rest_before_refs
    prayer_text = rest_before_refs[newpage_m.end():] if newpage_m else ""

    body_text, hc_text, prayer_text, ref_text = (
        _clean(body_text), _clean(hc_text), _clean(prayer_text), _clean(ref_text)
    )

    opener_raw, sections = parse_body_sections(body_text)
    opener_html = render_paragraphs(opener_raw, drop_first=True)

    section_html = []
    for heading, content in sections:
        section_html.append(f'<div class="divider">&#10022;</div>\n<h3>{md_inline(heading)}</h3>\n')
        section_html.append(render_paragraphs(content))

    hc_html = parse_heartcheck(hc_text, chap_num)
    prayer_title, prayer_prompt, salut = parse_prayer(prayer_text)
    refs_html = parse_references(ref_text) if ref_text.strip() else ""

    return {
        "title": title,
        "opener_html": opener_html,
        "sections_html": "".join(section_html),
        "hc_html": hc_html,
        "has_hc": bool(hc_m),
        "refs_html": refs_html,
        "prayer_title": prayer_title,
        "prayer_prompt": prayer_prompt,
        "salut": salut,
        "has_prayer": bool(newpage_m) and len(prayer_text.strip()) > 5,
    }
