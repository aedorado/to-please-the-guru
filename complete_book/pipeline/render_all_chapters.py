import glob, re, json, os
import render_chapter

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(PIPELINE_DIR, "..", ".."))  # .../to-please-the-guru
CHAPTERS_DIR = os.path.join(PROJECT_ROOT, "chapters")

files = sorted(glob.glob(os.path.join(CHAPTERS_DIR, "chapter_*-clean.md")),
               key=lambda p: int(re.search(r'chapter_(\d+)_', p).group(1)))

if not files:
    raise SystemExit(
        f"No chapter_*-clean.md files found in {CHAPTERS_DIR}\n"
        "Check that the project layout matches: <project>/chapters/chapter_N_title-clean.md "
        "and <project>/complete_book/pipeline/ (this script's location)."
    )

results = []
for f in files:
    num = int(re.search(r'chapter_(\d+)_', f).group(1))
    md = open(f).read()
    out_pdf = f"chap_{num:02d}.pdf"
    n, title, header = render_chapter.render(md, num, out_pdf)
    results.append({"num": num, "title": title, "header": header, "pages": n, "pdf": out_pdf})
    print(num, title, "->", n, "pages")

json.dump(results, open("chapters_meta.json", "w"), indent=2)
print("TOTAL PAGES", sum(r["pages"] for r in results))
