import subprocess, os, sys, shutil
import pypdf

BASE = os.path.dirname(os.path.abspath(__file__))

def find_chrome():
    env = os.environ.get("CHROME_PATH")
    if env and os.path.exists(env):
        return env
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    found = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome")
    if found:
        return found
    raise RuntimeError(
        "Could not find a Chrome/Chromium binary. Set the CHROME_PATH environment "
        "variable to its full path, e.g.:\n"
        '  export CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"'
    )

CHROME = find_chrome()

CSS = r"""
  @page{
    size: 6in 9in;
    margin: 0.7in 0.6in 0.75in 0.6in;
  }
  *{ box-sizing:border-box; }
  html,body{
    margin:0; padding:0;
    background: #ffffff;
    color:#1a1a1a;
    font-family:"Noto Serif", Georgia, "Times New Roman", serif;
    font-size: 11pt;
    line-height: 1.55;
  }
  .sanskrit{ font-style:italic; color:#1a1a1a; }

  .opener{ padding-top: 0.6in; }
  .part-label{
    font-family:"Cinzel", serif;
    font-size: 9.5pt; letter-spacing: 0.2em; text-transform: uppercase;
    color: #4d4d4d; text-align:center; margin: 0 0 20pt;
  }
  .chap-num{
    font-family:"Noto Serif Display", serif;
    font-style: italic; font-size: 52pt; line-height:1;
    text-align:center; color:#1a1a1a; margin: 0 0 4pt;
  }
  .chap-rule{
    width: 0.7in; height: 1.4pt; margin: 0 auto 20pt;
    background: linear-gradient(90deg, transparent, #1a1a1a, transparent);
  }
  .chap-title{
    font-family:"Noto Serif Display", serif;
    font-weight:600; font-size: 22pt; line-height:1.25;
    text-align:center; margin: 0 0 34pt;
  }
  p{ margin: 0 0 10pt; text-align: justify; hyphens:auto; }
  .drop::first-letter{
    font-family:"Noto Serif Display", serif;
    font-weight:600; font-size: 40pt; line-height: 0.72;
    float:left; padding: 3pt 6pt 0 0; color:#1a1a1a;
  }

  h3{
    font-family:"Noto Serif Display", serif;
    font-weight:600; font-style:italic; font-size: 14pt;
    color:#1a1a1a; margin: 22pt 0 10pt; page-break-after: avoid;
  }
  .divider{
    width: 100%; text-align:center; color:#8a8a8a;
    letter-spacing: 0.4em; font-size: 9pt; margin: 16pt 0;
  }
  .verse{
    text-align:center; font-style:italic; font-size:10.3pt;
    line-height:1.5; margin: 14pt 0; color:#1a1a1a;
  }
  .inline-blank{
    display:inline-block; border-bottom:0.8pt solid #999999;
    height:1em; margin:0 2pt; vertical-align:-2pt;
  }
  sup.cite{ font-size:7pt; color:#666666; margin-left:1pt; }
  .content-list{
    margin: 0 0 10pt; padding-left:1.4em; text-align:justify;
  }
  .content-list li{ margin-bottom:6pt; }

  .fm-page-break{ page-break-before: always; }

  .fm-title-page{ padding-top:1.6in; text-align:center; }
  .fm-title-eyebrow{
    font-family:"Cinzel", serif; font-size:10pt; letter-spacing:0.28em;
    text-transform:uppercase; color:#8a8a8a; margin-bottom:0.5in;
  }
  .fm-title{
    font-family:"Noto Serif Display", serif; font-weight:600; font-size:44pt;
    line-height:1.15; margin:0 0 0.3in;
  }
  .fm-subtitle{
    font-family:"Noto Serif Display", serif; font-style:italic; font-size:14pt;
    color:#333333; line-height:1.5; margin-bottom:0.4in;
  }
  .fm-rule{ width:0.9in; height:1.4pt; background:#1a1a1a; margin:0 auto 0.4in; }
  .fm-author{
    font-family:"Cinzel", serif; font-size:11pt; letter-spacing:0.1em;
    color:#333333;
  }

  .fm-copyright-wrap{ padding-top:2.2in; }
  .fm-copyright{ text-align:center; font-size:9.5pt; line-height:1.7; color:#333333; }
  .fm-copyright p{ text-align:center; margin-bottom:14pt; }
  .fm-copyright .fm-small{ font-size:8.3pt; color:#666666; line-height:1.6; }

  .fm-dedication-wrap{ padding-top:1.8in; }
  .fm-dedication{ text-align:center; }
  .fm-ded-label{
    font-family:"Noto Serif Display", serif; font-style:italic; font-size:13pt;
    margin-bottom:0.35in; text-align:center;
  }
  .fm-ded-name{
    font-family:"Noto Serif Display", serif; font-weight:600; font-size:15pt;
    line-height:1.4; margin-bottom:8pt; text-align:center;
  }
  .fm-ded-desc{ font-style:italic; font-size:10.5pt; color:#444444; line-height:1.6; margin-bottom:0.3in; text-align:center; }
  .fm-ded-and{ font-style:italic; font-size:11pt; color:#8a8a8a; margin-bottom:0.3in; text-align:center; }
  .fm-ded-close{ font-size:10pt; color:#555555; line-height:1.7; margin-top:0.4in; text-align:center; }

  .fm-page{ padding-top:0.3in; }
  .fm-heading{
    font-family:"Cinzel", serif; font-size:13pt; letter-spacing:0.1em;
    text-transform:uppercase; text-align:center; color:#1a1a1a; margin-bottom:0.35in;
  }
  .fm-page h4{
    font-family:"Noto Serif Display", serif; font-weight:600; font-style:italic;
    font-size:12.5pt; margin:18pt 0 8pt;
  }

  .toc-page{ padding-top:0.2in; }
  .toc-part{
    font-family:"Cinzel", serif; font-size:9.5pt; letter-spacing:0.14em;
    text-transform:uppercase; color:#7a7a7a; margin:20pt 0 8pt;
    border-bottom:0.8pt solid #cccccc; padding-bottom:5pt;
  }
  .toc-part:first-of-type{ margin-top:6pt; }
  .toc-list{ list-style:none; margin:0 0 4pt; padding:0; }
  .toc-list li{
    display:flex; align-items:baseline; font-size:10.3pt; line-height:1.7;
    page-break-inside: avoid;
  }
  .toc-num{ color:#999999; width:1.4em; flex:none; font-variant-numeric:tabular-nums; }
  .toc-title{ white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .toc-dots{
    flex:1; border-bottom:1px dotted #b3b3b3; margin:0 6pt 3pt; min-width:8pt;
  }
  .toc-page-num{ color:#555555; font-variant-numeric:tabular-nums; flex:none; }

  /* Heart Check */
  .hc-block{
    border-top: 1.6pt solid #1a1a1a; padding-top: 12pt; margin: 26pt 0 16pt;
  }
  .hc-eyebrow{
    font-family:"Cinzel", serif;
    font-size: 9pt; letter-spacing:0.16em; text-transform:uppercase;
    color:#4d4d4d; margin: 0 0 10pt; page-break-after: avoid;
  }
  .hc-block h4{
    font-family:"Noto Serif Display", serif;
    font-weight:600; font-size:13pt; margin: 14pt 0 8pt; page-break-after: avoid;
  }
  .hc-block h4:first-of-type{ margin-top:0; }
  .hc-item{
    font-size: 10.2pt; line-height:1.55; color:#333333;
    margin: 0 0 8pt; padding-left:12pt; position:relative;
    page-break-inside: avoid;
  }
  .hc-item::before{
    content:"◆"; position:absolute; left:0; top:1.5pt;
    font-size:6pt; color:#4d4d4d;
  }
  .hc-item.numbered::before{
    content: attr(data-n) "."; font-size:9pt; font-weight:600; top:0; color:#1a1a1a;
  }
  .hc-item.plain{ padding-left:0; }
  .hc-item.plain::before{ content:none; }
  .fill-rule{
    display:block; border-bottom:0.8pt solid #999999;
    margin-top:4pt; width:96%;
  }
  .commitment{ font-weight:600; }

  .hc-lines{
    margin: 8pt 0 10pt 12pt; padding:0; list-style:none;
    width:88%; page-break-inside: avoid;
  }
  .hc-lines li{ height:0; margin-bottom: 13pt; border-bottom: 0.8pt solid #999999; }
  .hc-lines li:last-child{ margin-bottom:0; }

  /* References */
  .refs{ margin-top: 22pt; padding-top: 10pt; border-top: 0.8pt solid #cccccc; }
  .refs-label{
    font-family:"Cinzel", serif;
    font-size: 8.5pt; letter-spacing:0.16em; text-transform:uppercase;
    color:#999999; margin: 0 0 10pt;
  }
  .refs ol{ margin:0; padding:0 0 0 1.3em; font-size: 8.3pt; line-height:1.5; color:#555555; }
  .refs li{ margin-bottom: 7pt; padding-left: 2pt; }
  .refs em{ font-style:italic; }
  .refs .url{ color:#7a7a7a; word-break: break-all; }

  /* Personal Prayer — full page, bleeds into the unused margin since it
     carries no running header/footer, to maximize writing room */
  .prayer-page{
    page-break-before: always;
    margin: 0;
    padding: 0.04in;
  }
  .prayer-frame{
    border-top: 1.4pt solid #1a1a1a;
    border-bottom: 1.4pt solid #1a1a1a;
    padding: 0.1in 0.55in 0.08in;
  }
  .prayer-eyebrow{
    font-family:"Cinzel", serif;
    font-size: 9.5pt; letter-spacing:0.16em; text-transform:uppercase;
    color:#4d4d4d; text-align:center; margin: 0 0 5pt;
  }
  .prayer-title{
    font-family:"Noto Serif Display", serif;
    font-weight:600; font-size:14pt; text-align:center; margin:0 0 7pt;
  }
  .prayer-prompt{
    font-style:italic; font-size:8.7pt; line-height:1.35; color:#333333;
    text-align:center; margin: 0 auto 9pt;
  }
  .prayer-salut{ font-size:10.5pt; margin: 0 0 7pt; }
  .prayer-lines{ margin:0; padding:0; list-style:none; }
  .prayer-lines .fill-rule{ display:block; width:100%; height:23pt; border-bottom:0.8pt solid #b3b3b3; }
  .prayer-close{
    text-align:right; font-style:italic; font-size:9.5pt; color:#4d4d4d; margin-top:5pt;
  }
"""

def doc(title, body_html):
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Display:ital,wght@0,400;0,600;1,400;0,700&family=Noto+Serif:ital,wght@0,400;0,600;1,400;1,600&family=Cinzel:wght@500;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
{body_html}
</body>
</html>"""

def render_pdf(html_str, out_path):
    html_path = os.path.abspath(out_path.replace(".pdf", ".html"))
    out_path = os.path.abspath(out_path)
    with open(html_path, "w") as f:
        f.write(html_str)
    subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={out_path}", "--print-to-pdf-no-header",
        f"file://{html_path}"
    ], cwd=BASE, capture_output=True)
    n = len(pypdf.PdfReader(out_path).pages)
    print(out_path, "->", n, "pages")
    return n
