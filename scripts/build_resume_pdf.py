#!/usr/bin/env python3
"""
build_resume_pdf.py - render the web resume (assets/pages/resume-page.html)
to static/resume/jason-wacker-resume.pdf, so the PDF never drifts from
the /resume/ page again.

The PDF gets a light print theme, no download button and no scripts.
The email is written out in full (a recruiter needs it), but there is
no phone number or street/city line, same as the web page.

Setup (once):  pip install playwright && python -m playwright install chromium
Run from the repo root:  python3 scripts/build_resume_pdf.py
"""
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/pages/resume-page.html"
OUT = ROOT / "static/resume/jason-wacker-resume.pdf"

PRINT_CSS = """
<style>
  @page { size: Letter; margin: 0.5in 0.55in; }
  :root { --accent: #c25e00; --in-progress: #b45309; --text: #1f2933;
          --muted: #52606d; --border: #d9dee3; --card-bg: #f7f8fa; }
  html, body { background: #fff !important; }
  .resume-wrap { margin: 0 auto !important; max-width: none !important; font-size: 9.8pt !important; }
  .r-header h1 { color: #111 !important; }
  .dl-btn { display: none !important; }
  a { color: inherit !important; text-decoration: none !important; }
  .r-job, .r-skill-card, .r-cert-item, .r-vol { break-inside: avoid; }
  .r-section-label { break-after: avoid; }
  .r-job-title, .r-project-name, .r-edu-degree, .r-vol-role { color: #111 !important; }
  .r-homelab-grid li { background: #f7f8fa !important; color: var(--text) !important; }
  .resume-wrap { line-height: 1.4 !important; }
  .r-header { margin-bottom: 1.2rem !important; padding-bottom: 1rem !important; }
  .r-section-label { margin-top: 1.1rem !important; margin-bottom: 0.6rem !important; }
  .r-job, .r-skill-card, .r-project, .r-edu-item, .r-vol { margin-bottom: 0.6rem !important; padding-top: 0.7rem !important; padding-bottom: 0.7rem !important; }
</style>
"""


def main():
    html = SRC.read_text(encoding="utf-8")

    # Write the email out in plain text for the PDF.
    m = re.search(r'<a href="#" class="js-email" data-u="([^"]+)" data-d="([^"]+)">[^<]*</a>', html)
    if not m:
        sys.exit("Couldn't find the js-email link in resume-page.html")
    email = m.group(1)[::-1] + "@" + m.group(2)[::-1]
    html = html.replace(m.group(0), f'<a href="mailto:{email}">{email}</a>')

    # No scripts in the PDF.
    html = re.sub(r"<script\b.*?</script>", "", html, flags=re.S)
    # Print theme goes last so it wins over the page's own dark styles.
    html = html.replace("</head>", PRINT_CSS + "</head>", 1) if "</head>" in html else PRINT_CSS + html

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="load")
        page.pdf(path=str(OUT), format="Letter", print_background=True,
                 prefer_css_page_size=True)
        browser.close()
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
