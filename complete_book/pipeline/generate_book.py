#!/usr/bin/env python3
"""
Master build script for "To Please the Guru".

Regenerates the complete print-ready book PDF from the markdown chapter
sources plus the front/back cover images. Safe to re-run any time the
chapter files change -- it always reflects whatever is currently on disk.

Usage:
    cd complete_book/pipeline
    python3 generate_book.py

Requires: python3, pip packages `pypdf` and `reportlab`, and a local
Chrome/Chromium install (used headless as the HTML->PDF renderer).
See README.md in this folder for the full explanation of how this works.
"""
import os, subprocess, sys, shutil, time

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(PIPELINE_DIR, "..", ".."))   # .../to-please-the-guru
COMPLETE_BOOK_DIR = os.path.abspath(os.path.join(PIPELINE_DIR, ".."))     # .../to-please-the-guru/complete_book
BUILD_DIR = os.path.join(PIPELINE_DIR, "build")                           # scratch output, gitignore-able
FINAL_OUT = os.path.join(COMPLETE_BOOK_DIR, "to-please-the-guru-COMPLETE-print.pdf")

def _script(name):
    return os.path.join(PIPELINE_DIR, name)

STEPS = [
    ("Rendering all 22 chapters", [_script("render_all_chapters.py")]),
    ("Rendering front matter",     ["-c", "import build, front_matter; "
                                     "n = build.render_pdf(build.doc('Front Matter', front_matter.all_pages_html()), 'front_matter.pdf'); "
                                     "print('front_matter.pdf ->', n, 'pages')"]),
    ("Rendering back matter",      ["-c", "import build, back_matter; "
                                     "n = build.render_pdf(build.doc('Back Matter', back_matter.all_pages_html()), 'back_matter.pdf'); "
                                     "print('back_matter.pdf ->', n, 'pages')"]),
    ("Rendering front/back covers", [_script("render_covers.py")]),
    ("Assembling the complete book", [_script("assemble.py")]),
]

def main():
    os.makedirs(BUILD_DIR, exist_ok=True)
    # scripts import each other by bare module name (e.g. `import build`),
    # so PIPELINE_DIR must be on sys.path for every subprocess
    env = dict(os.environ)
    env["PYTHONPATH"] = PIPELINE_DIR + os.pathsep + env.get("PYTHONPATH", "")

    t0 = time.time()
    for label, args in STEPS:
        print(f"\n=== {label} ===")
        cmd = [sys.executable] + args
        result = subprocess.run(cmd, cwd=BUILD_DIR, env=env)
        if result.returncode != 0:
            sys.exit(f"\nFAILED at step: {label} (exit code {result.returncode})")

    built = os.path.join(BUILD_DIR, "complete_book.pdf")
    shutil.copy(built, FINAL_OUT)
    dt = time.time() - t0
    print(f"\nDone in {dt:.1f}s -> {FINAL_OUT}")

if __name__ == "__main__":
    main()
