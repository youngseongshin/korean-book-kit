"""원고(PDF/DOCX/TXT/MD) → 줄 형식 초안(draft.txt) + 검토용 목록(draft_review.txt)

usage:
  python3 engine/ingest.py <원고파일> <project_dir> [--speakers 이름1,이름2,...]

- PDF: 줄 좌표로 문단을 다시 잇는다(줄 끝이 오른쪽 여백에 닿았고 다음 줄이 들여쓰기 없이 시작하면 같은 문단).
  본문보다 1.2배 이상 큰 글자는 장 제목 후보(@CH)로 표시한다.
- 화자 감지: ‘이름:’ 또는 ‘**이름**’ 또는 굵은 첫 단어(4자 이하)로 시작하는 문단 → Q|이름|
- 따옴표를 ‘ ’ “ ”로, ...를 …로 바꾼다.

결과는 초안이다. 부(이야기)별 파일로 나누고 @PART/@TITLE/@CH 칸을 채우는 일은
README의 ‘2단계 구조 잡기’를 따라 사람이(또는 Claude가) 마무리한다.
"""
import collections
import os
import re
import sys


def smart_quotes(t):
    t = t.replace('...', '…').replace('​', '')
    out = []
    for i, c in enumerate(t):
        prev = t[i - 1] if i else ' '
        if c == '"':
            out.append('“' if prev in ' (\n[‘' or i == 0 else '”')
        elif c == "'":
            out.append('‘' if prev in ' (\n[“' or i == 0 else '’')
        else:
            out.append(c)
    return ''.join(out)


def char_w(ch, size):
    o = ord(ch)
    if 0xAC00 <= o <= 0xD7A3 or 0x3000 <= o <= 0x9FFF or ch in '‘’“”':
        return size
    return size * (0.28 if ch == ' ' else 0.55)


def pdf_paragraphs(path):
    import pymupdf
    d = pymupdf.open(path)
    lines = []
    for pno, page in enumerate(d):
        for b in page.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                spans = [s for s in l['spans'] if s['text']]
                if not spans:
                    continue
                text = ''.join(s['text'] for s in spans)
                size = round(max(spans, key=lambda s: len(s['text'].strip()))['size'], 1)
                bold_first = bool(spans[0]['flags'] & 16) and len(spans[0]['text'].strip().rstrip(':')) <= 4
                first = text.strip().split(' ')[0] if text.strip() else ''
                lines.append(dict(page=pno + 1, x0=round(l['bbox'][0]), x1=l['bbox'][2], size=size, text=text,
                                  blank=not text.strip(), bold_first=bold_first,
                                  fw=sum(char_w(c, size) for c in first)))
    body = [l for l in lines if not l['blank']]
    by_size = collections.Counter()
    for l in body:
        by_size[l['size']] += len(l['text'])
    body_size = by_size.most_common(1)[0][0]
    left = collections.Counter(l['x0'] for l in body if l['size'] == body_size).most_common(1)[0][0]
    x1s = sorted(l['x1'] for l in body if l['size'] == body_size)
    right = x1s[int(len(x1s) * 0.95)]
    paras, prev = [], None
    for ln in lines:
        if ln['blank']:
            prev = None
            continue
        heading = ln['size'] >= body_size * 1.2
        new = True
        if prev is not None and prev['size'] == ln['size']:
            reached = prev['x1'] + 3 + ln['fw'] > right
            new = not (reached and ln['x0'] <= left + 2) or ln['bold_first']
        if new:
            paras.append(dict(page=ln['page'], size=ln['size'], heading=heading, text=ln['text'],
                              bold_first=ln['bold_first']))
        else:
            p = paras[-1]
            sep = '' if p['text'].endswith(' ') or ln['text'].startswith(' ') else ' '
            p['text'] += sep + ln['text']
        prev = ln
    for p in paras:
        p['text'] = re.sub(r'\s+', ' ', p['text']).strip()
    return paras


def docx_paragraphs(path):
    import docx  # pip install python-docx
    out = []
    for para in docx.Document(path).paragraphs:
        t = para.text.strip()
        if not t:
            continue
        heading = para.style.name.lower().startswith(('heading', 'title', '제목'))
        bold_first = bool(para.runs and para.runs[0].bold and len(para.runs[0].text.strip().rstrip(':')) <= 4)
        out.append(dict(page=0, heading=heading, text=t, bold_first=bold_first))
    return out


def text_paragraphs(path):
    out = []
    for block in re.split(r'\n\s*\n', open(path, encoding='utf-8').read()):
        t = re.sub(r'\s+', ' ', block).strip()
        if not t:
            continue
        heading = t.startswith('#')
        out.append(dict(page=0, heading=heading, text=t.lstrip('#').strip(), bold_first=False))
    return out


def to_lines(paras, speakers):
    names = '|'.join(map(re.escape, speakers)) if speakers else r'[가-힣]{1,4}'
    spk = re.compile(r'^\*{0,2}(' + names + r')\*{0,2}\s*[:：]\s*(.*)$')
    spk_bold = re.compile(r'^\*\*(' + names + r')\*\*\s+(.*)$')
    out = []
    for p in paras:
        t = smart_quotes(p['text'])
        if p['heading']:
            out += ['', f'@CH |||{t}|']
            continue
        m = spk.match(t) or spk_bold.match(t)
        if not m and p.get('bold_first') and speakers:
            first, _, rest = t.partition(' ')
            if first.rstrip(':') in speakers:
                out.append(f'Q|{first.rstrip(":")}| {rest.strip()}')
                continue
        if m:
            out.append(f'Q|{m.group(1)}| {m.group(2).strip()}')
        else:
            out.append(f'N| {t.replace("**", "")}')
    return out


if __name__ == '__main__':
    args = sys.argv[1:]
    speakers = []
    if '--speakers' in args:
        i = args.index('--speakers'); speakers = args[i + 1].split(','); del args[i:i + 2]
    src, project = args
    ext = os.path.splitext(src)[1].lower()
    paras = {'.pdf': pdf_paragraphs, '.docx': docx_paragraphs}.get(ext, text_paragraphs)(src)
    os.makedirs(project, exist_ok=True)
    lines = ['@PART 1', '@TITLE (제목)', '@OPENING'] + to_lines(paras, speakers)
    open(os.path.join(project, 'draft.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    with open(os.path.join(project, 'draft_review.txt'), 'w', encoding='utf-8') as f:
        for p in paras:
            f.write(f"[p{p['page']}{' H' if p['heading'] else ''}] {p['text']}\n")
    print(f'{len(paras)} paragraphs → {project}/draft.txt  (장 제목 후보 {sum(p["heading"] for p in paras)}개)')
