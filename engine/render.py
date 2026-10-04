"""build/book.html → build/book.pdf  (Chromium + Paged.js)

usage: python3 engine/render.py <project_dir> [out.pdf]
"""
import os, sys, time
from playwright.sync_api import sync_playwright

project = sys.argv[1]
src = os.path.abspath(os.path.join(project, 'build', 'book.html'))
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(project, 'build', 'book.pdf')
with sync_playwright() as p:
    b = p.chromium.launch(args=['--allow-file-access-from-files'])
    pg = b.new_page()
    pg.on('console', lambda m: print('console:', m.text) if m.type in ('error', 'warning') else None)
    pg.goto('file://' + src)
    t = time.time()
    pg.wait_for_function('window.__done === true', timeout=600000)
    print('pages', pg.evaluate('window.__pages'), 'in', round(time.time() - t, 1), 's')
    pg.pdf(path=out, prefer_css_page_size=True, print_background=True,
           margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'})
    b.close()
print('wrote', out)
