"""완성 PDF 최종 점검 + 눈으로 볼 견본 쪽 이미지.

usage: python3 engine/verify_pdf.py <project_dir> [--pages 1,9,14,96] [--every 40]

- 쪽수, 장 수(차례 기준) 출력
- [rules].retired (바꾼 옛 이름 등)가 PDF 텍스트에 남았는지
- 곧은 따옴표, 본문 em-dash 개수
- 견본 쪽을 build/proof/ 에 PNG로 저장하고 한 장짜리 모음(contact.png)을 만든다
  → Claude는 Read 도구로 contact.png 를 열어 조판(넘침, 빈 쪽, 끝줄 양쪽맞춤, 그림 위치)을 눈으로 확인한다.
"""
import os
import sys
import tomllib

import pymupdf


def main():
    args = sys.argv[1:]
    project = args[0]
    pages, every = None, 40
    if '--pages' in args:
        pages = [int(x) for x in args[args.index('--pages') + 1].split(',')]
    if '--every' in args:
        every = int(args[args.index('--every') + 1])
    cfg = tomllib.load(open(os.path.join(project, 'book.toml'), 'rb'))
    pdf = os.path.join(project, 'build', 'book.pdf')
    d = pymupdf.open(pdf)
    texts = [p.get_text() for p in d]
    full = '\n'.join(texts)
    open(os.path.join(project, 'build', 'book.txt'), 'w', encoding='utf-8').write(full)
    print(f'쪽수 {len(d)}')
    problems = 0
    for s in cfg.get('rules', {}).get('retired', []):
        hits = [i + 1 for i, t in enumerate(texts) if s in t]
        if hits:
            problems += 1
            print(f'  남아 있음 ‘{s}’: {len(hits)}쪽 {hits[:10]}')
    sq = [i + 1 for i, t in enumerate(texts) if '"' in t or "'" in t]
    if sq:
        problems += 1
        print(f'  곧은 따옴표: {sq[:10]}')
    em = [i + 1 for i, t in enumerate(texts) if '—' in t]
    print(f'  em-dash가 있는 쪽: {em} (앞뒤 인용 출처 표기면 정상)')
    print('OK' if not problems else f'확인 필요 {problems}건')

    # 견본 쪽
    pages = pages or sorted(set([1, 2, 3, len(d)] + list(range(every, len(d), every))))
    out = os.path.join(project, 'build', 'proof')
    os.makedirs(out, exist_ok=True)
    shots = []
    for n in pages:
        if 1 <= n <= len(d):
            pm = d[n - 1].get_pixmap(dpi=60)
            fn = os.path.join(out, f'p{n:03d}.png')
            pm.save(fn)
            shots.append(fn)
    # 모음 이미지
    if shots:
        imgs = [pymupdf.Pixmap(f) for f in shots]
        w, h = imgs[0].width, imgs[0].height
        cols = min(5, len(imgs))
        rows = (len(imgs) + cols - 1) // cols
        sheet = pymupdf.open()
        page = sheet.new_page(width=w * cols, height=h * rows)
        for k, f in enumerate(shots):
            r, c = divmod(k, cols)
            page.insert_image(pymupdf.Rect(c * w, r * h, (c + 1) * w, (r + 1) * h), filename=f)
        page.get_pixmap(dpi=72).save(os.path.join(out, 'contact.png'))
        print('견본', len(shots), '쪽 →', os.path.join(out, 'contact.png'))


if __name__ == '__main__':
    main()
