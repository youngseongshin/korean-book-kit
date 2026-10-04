"""book.toml + stories/*.txt + art.py + book.css  →  build/book.html (Paged.js)

usage: python3 engine/build.py <project_dir> [--stories <dir>]
"""
import html
import os
import re
import sys
import tomllib

sys.path.insert(0, os.path.dirname(__file__))
import art  # noqa: E402
import textfmt  # noqa: E402

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def esc(t):
    return html.escape(t, quote=False)


def br(lines):
    return '<br>'.join(esc(x) for x in lines) if isinstance(lines, list) else esc(lines)


def load(project, stories=None):
    cfg = tomllib.load(open(os.path.join(project, 'book.toml'), 'rb'))
    sdir = stories or os.path.join(project, cfg.get('paths', {}).get('stories', 'stories'))
    iv = set(cfg.get('text', {}).get('interviewers', []))
    parts = []
    for p in cfg['parts']:
        data = textfmt.parse_file(os.path.join(sdir, p['file']), iv)
        parts.append((p, data))
    return cfg, parts


# ------------------------------------------------------------------ blocks
def block_html(bl, pc, first, cfg):
    k = bl['k']
    inline = pc.get('speakers', 'hanging') == 'inline'
    if k == 'q':
        cls = 'q iv' if bl['iv'] else 'q'
        if inline:
            cls += ' inl'
        return f'<p class="{cls}"><span class="who">{esc(bl["who"])}</span>{esc(bl["t"])}</p>'
    if k == 'cont':
        return f'<p class="cont{" inl" if inline else ""}">{esc(bl["t"])}</p>'
    if k == 'memo':
        rx = cfg.get('text', {}).get('memo_head_regex', r'^(그날 밤 메모\.)\s*(.*)$')
        m = re.match(rx, bl['t'])
        head, body = (m.group(1), m.group(2)) if m else ('', bl['t'])
        return f'<aside class="memo"><span class="memo-head">{esc(head)}</span> {esc(body)}</aside>'
    if k == 'vow':
        return f'<li><span class="vn">{esc(bl["n"])}</span><span class="vt">{esc(bl["t"])}</span></li>'
    t = bl['t']
    cls = 'n first' if first else 'n'
    lead = pc.get('lead_bold_regex')  # 문단 첫머리를 굵게(예: ‘김순자(81)와 박영철(83).’)
    if lead:
        m = re.match(lead, t)
        if m:
            return f'<p class="{cls}"><strong>{esc(m.group(1))}</strong> {esc(m.group(2))}</p>'
    return f'<p class="{cls}">{esc(t)}</p>'


def blocks_html(blocks, pc, cfg):
    out, in_list, first = [], False, True
    for bl in blocks:
        if bl['k'] == 'vow' and not in_list:
            out.append('<ol class="vows">'); in_list = True
        if bl['k'] != 'vow' and in_list:
            out.append('</ol>'); in_list = False
        out.append(block_html(bl, pc, first, cfg))
        first = False
    if in_list:
        out.append('</ol>')
    return '\n'.join(out)


# ------------------------------------------------------------------ build
def build(project, stories=None):
    cfg, parts = load(project, stories)
    book, front_c, back_c = cfg['book'], cfg.get('front', {}), cfg.get('back', {})
    text_c = cfg.get('text', {})
    title = book['title']
    H, toc = [], []
    for pi, (pc, part) in enumerate(parts):
        pid = f'part{pi + 1}'
        acc = art.color(pc['accent'])
        vigs = pc.get('vignettes', ['cup'])
        entry = {'id': pid, 'name': pc['name'], 'title': part['title'], 'chs': []}
        # 간지(부 표지)
        H.append(f'''
<section class="divider" id="{pid}" style="--tint:{pc['tint']};--acc:{acc}">
  <div class="arch">{art.COMPOSITIONS[pc.get('art', 'part1')]()}</div>
  <div class="pnum">{esc(pc['name'])}</div>
  <h1 class="ptitle">{esc(part['title'])}</h1>
  {f'<div class="psub">{esc(part["sub"])}</div>' if part['sub'] else ''}
  {f'<div class="pbyline">{esc(part["byline"])}</div>' if part['byline'] else ''}
  {f'<div class="pstyle">{esc(pc["style"])}</div>' if pc.get('style') else ''}
</section>''')
        # 등장인물 쪽
        notes = list(pc['notes']) if 'notes' in pc else list(part['notes'])
        opening = list(part['opening'])
        if pc.get('opening_to_notes'):
            notes += [b['t'] for b in opening]
            opening = []
        if 'cast' in pc:
            cast_html = ''.join(f'<p class="bio"><span class="cname">{esc(n)}</span>{esc(d)}</p>' for n, d in pc['cast'])
        else:
            cast_html = ''.join(f'<p class="bio">{esc(c)}</p>' for c in part['cast'])
        notes_html = ''.join(f'<p>{esc(n)}</p>' for n in notes)
        if cast_html or notes_html:
            H.append(f'''
<section class="castpage" style="--acc:{acc}">
  <div class="cast-inner">
    <div class="cast-h">{esc(text_c.get('cast_heading', '등장인물'))}</div>
    {cast_html}
  </div>
  {f'<div class="fiction">{notes_html}</div>' if notes_html else ''}
</section>''')
        # 머리글
        if opening:
            H.append(f'<section class="chapter opening" style="--acc:{acc}">'
                     f'<div class="ornament">{art.vignette(vigs[0])}</div>'
                     f'<div class="text">{blocks_html(opening, pc, cfg)}</div></section>')
        # 장
        for ci, ch in enumerate(part['chapters']):
            head = ch['head']
            cid = f'{pid}-c{ci + 1}'
            label = head['num'] if pc.get('chapter_label', 'label') == 'num' else head['label']
            entry['chs'].append({'id': cid, 'label': label, 'title': head['title']})
            vig = vigs[(ci + (1 if opening else 0)) % len(vigs)]
            body = blocks_html(ch['blocks'], pc, cfg)
            if head.get('special') == 'vows':
                H.append(f'''
<section class="chapter vowpage" id="{cid}" style="--acc:{acc}">
  <div class="ornament">{art.vignette(pc.get('vows_vignette', 'notebook'))}</div>
  <h2 class="vow-title">{esc(head['title'])}</h2>
  <div class="text">{body}</div>
</section>''')
                continue
            numcls = 'cnum' if re.fullmatch(r'\d+(장)?', label or '') else 'cword'
            H.append(f'''
<section class="chapter" id="{cid}" style="--acc:{acc}">
  <header class="chead">
    <div class="{numcls}">{esc(label)}</div>
    <h2 class="ctitle">{esc(head['title'])}</h2>
    {f'<div class="csub">{esc(head["sub"])}</div>' if head.get('sub') else ''}
    <div class="ornament">{art.vignette(vig)}</div>
  </header>
  <div class="text">{body}</div>
</section>''')
        toc.append(entry)

    # 맺음 쪽(선택): 독자가 손으로 쓰는 답장 쪽
    end = cfg.get('ending')
    if end:
        acc = art.color(end.get('accent', parts[-1][0]['accent']))
        H.append(f'''
<section class="answer" style="--acc:{acc}">
  <div class="ans-h">{esc(end['heading'])}</div>
  <div class="ans-q">{esc(end.get('question', ''))}</div>
  <div class="ans-date">{esc(end.get('date', '____년 ____월 ____일'))}</div>
  <div class="ruled">{''.join('<div class="rl"></div>' for _ in range(end.get('lines', 12)))}</div>
  <div class="ans-foot">{esc(end.get('foot', ''))}</div>
</section>''')

    # 차례
    toc_html = ''
    for e in toc:
        toc_html += (f'<div class="toc-part"><a class="tp" href="#{e["id"]}"><span class="tpn">{esc(e["name"])}</span>'
                     f'<span class="tpt">{esc(e["title"])}</span><span class="dots"></span></a><ul>')
        for c in e['chs']:
            toc_html += (f'<li><a href="#{c["id"]}"><span class="tl">{esc(c["label"] or "")}</span>'
                         f'<span class="tt">{esc(c["title"])}</span><span class="dots"></span></a></li>')
        toc_html += '</ul></div>'

    colophon = ''
    for i, line in enumerate(front_c.get('colophon', [])):
        if i == 0:
            colophon += f'<p class="cr-t">{esc(line)}</p>'
        elif line.startswith('+'):  # '+' 로 시작하면 앞에 여백
            colophon += f'<p class="sp">{esc(line[1:].strip())}</p>'
        else:
            colophon += f'<p>{esc(line)}</p>'

    front = f'''
<section class="cover">
  <div class="cover-art">{art.COMPOSITIONS[cfg.get('art', {}).get('cover', 'cover')]()}</div>
  <div class="cover-text">
    <div class="cover-kicker">{esc(book.get('kicker', ''))}</div>
    <div class="cover-title">{esc(title)}</div>
    <div class="cover-sub">{esc(book.get('subtitle', ''))}</div>
  </div>
  <div class="cover-ed">{esc(book.get('editor', ''))}</div>
</section>
<section class="endpaper">{art.COMPOSITIONS[cfg.get('art', {}).get('endpaper', 'endpaper')]()}</section>
<section class="titlepage">
  <div class="tp-vig">{art.vignette(front_c.get('title_vignette', 'teapot'))}</div>
  <div class="tp-title">{esc(title)}</div>
  <div class="tp-sub">{esc(book.get('subtitle', ''))}</div>
  <div class="tp-ed">{esc(book.get('editor', ''))}</div>
</section>
<section class="copyright"><div class="cr">{colophon}</div></section>
{f'<section class="dedication"><p>{br(front_c["dedication"])}</p></section>' if front_c.get('dedication') else ''}
{f'<section class="epigraph"><blockquote>{br(front_c["epigraph"])}</blockquote><div class="epi-src">{esc(front_c.get("epigraph_src", ""))}</div></section>' if front_c.get('epigraph') else ''}
<section class="toc">
  <div class="toc-h">차례</div>
  {toc_html}
</section>
'''
    back = f'''
<section class="endpaper back-end">{art.COMPOSITIONS[cfg.get('art', {}).get('endpaper', 'endpaper')]()}</section>
<section class="backcover">
  <div class="bc-quote">{br(back_c.get('quote', ''))}</div>
  <div class="bc-src">{esc(back_c.get('src', ''))}</div>
  <div class="bc-blurb">{br(back_c.get('blurb', ''))}</div>
  <div class="bc-art">{''.join(art.vignette(v) for v in back_c.get('vignettes', []))}</div>
  <div class="bc-title">{esc(title)}</div>
</section>
'''
    css = open(os.path.join(KIT, 'assets', 'book.css'), encoding='utf-8').read()
    css = css.replace('{{RUNNING_HEAD}}', book.get('running_head', title).replace("'", '’'))
    css = css.replace('{{PAGE_SIZE}}', book.get('page_size', '148mm 210mm'))
    css = css.replace("url('fonts/", f"url('file://{KIT}/assets/fonts/")
    extra = os.path.join(project, 'extra.css')  # 책별 CSS 덮어쓰기(선택)
    if os.path.exists(extra):
        css += '\n' + open(extra, encoding='utf-8').read()
    doc = f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><title>{esc(title)}</title>
<style>{css}</style>
<script>window.PagedConfig = {{ auto: true, after: (flow) => {{ window.__pages = flow.total; window.__done = true; }} }};</script>
<script src="file://{KIT}/assets/vendor/paged.polyfill.js"></script>
</head><body>
{front}
{''.join(H)}
{back}
</body></html>'''
    os.makedirs(os.path.join(project, 'build'), exist_ok=True)
    out = os.path.join(project, 'build', 'book.html')
    open(out, 'w', encoding='utf-8').write(doc)
    print('built', out, f'{len(doc):,} bytes,', sum(len(p["chapters"]) for _, p in parts), 'chapters')
    return out


if __name__ == '__main__':
    args = sys.argv[1:]
    st = None
    if '--stories' in args:
        i = args.index('--stories'); st = args[i + 1]; del args[i:i + 2]
    build(args[0], st)
