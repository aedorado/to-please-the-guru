import subprocess, os
import build  # for build.find_chrome() and portable CHROME path resolution

CHROME = build.CHROME
BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))  # .../to-please-the-guru
FRONT_COVER_IMG = os.path.join(PROJECT_ROOT, "front-cover.png")
BACK_COVER_IMG = os.path.join(PROJECT_ROOT, "back-cover.png")

COVER_HTML = """<!doctype html>
<html><head><meta charset="utf-8">
<style>
  @page{{ size: 6in 9in; margin:0; }}
  *{{ margin:0; padding:0; }}
  html,body{{ width:6in; height:9in; overflow:hidden; }}
  img{{ width:6in; height:9in; object-fit:cover; display:block; }}
</style></head>
<body><img src="file://{img_path}"></body></html>
"""

def render(img_path, out_pdf):
    html = COVER_HTML.format(img_path=img_path)
    html_path = out_pdf.replace(".pdf", ".html")
    with open(html_path, "w") as f:
        f.write(html)
    subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={os.path.abspath(out_pdf)}", "--print-to-pdf-no-header",
        f"file://{os.path.abspath(html_path)}"
    ], cwd=BASE, capture_output=True)
    print(out_pdf, "done")

if __name__ == "__main__":
    for img in (FRONT_COVER_IMG, BACK_COVER_IMG):
        if not os.path.exists(img):
            raise SystemExit(f"Cover image not found: {img}")
    render(FRONT_COVER_IMG, "front_cover.pdf")
    render(BACK_COVER_IMG, "back_cover.pdf")
