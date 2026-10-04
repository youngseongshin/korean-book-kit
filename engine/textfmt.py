"""원고 줄 형식(.txt) <-> 구조 데이터(dict) 변환.

원고 파일 하나 = 이야기(부) 하나. 한 줄 = 한 문단(블록).

  @PART <id>                     부 식별자(숫자 또는 짧은 영문)
  @TITLE <제목>                  @SUB <부제>      @BYLINE <지은이 줄>
  @NOTE <허구 고지 등 각주>      @CAST <등장인물 소개 문단>
  @OPENING                       첫 장 앞의 머리글(제목 없는 도입부)이 이어진다
  @CH num|label|title|sub|special   장 머리. special=vows 이면 서약 목록 쪽으로 조판
  N| 서술 문단
  Q|<화자>| 대사                  화자 표시형 대사(대담·녹취)
  C| 같은 화자의 이어지는 대사
  M| 손글씨 메모(밤 메모 등)
  V|<번호>| 서약·목록 항목

빈 줄은 무시된다(장 사이 가독성용).
"""
import json
import re
import sys

LINE_RE = re.compile(r'^(N|C|M)\| .+|^(Q|V)\|[^|]+\| .+')


def parse_file(path, interviewers=()):
    part = {'id': '', 'title': '', 'sub': '', 'byline': '', 'notes': [], 'cast': [],
            'opening': [], 'chapters': [], 'file': path}
    cur = None
    for no, raw in enumerate(open(path, encoding='utf-8'), 1):
        line = raw.rstrip('\n')
        if not line.strip():
            continue
        if line.startswith('@'):
            tag, _, val = line.partition(' ')
            val = val.strip()
            if tag == '@PART': part['id'] = val
            elif tag == '@TITLE': part['title'] = val
            elif tag == '@SUB': part['sub'] = val
            elif tag == '@BYLINE': part['byline'] = val
            elif tag == '@NOTE': part['notes'].append(val)
            elif tag == '@CAST': part['cast'].append(val)
            elif tag == '@OPENING': cur = part['opening']
            elif tag == '@CH':
                f = (val.split('|') + [''] * 5)[:5]
                head = {'num': f[0].strip(), 'label': f[1].strip(), 'title': f[2].strip(), 'sub': f[3].strip()}
                if f[4].strip():
                    head['special'] = f[4].strip()
                ch = {'head': head, 'blocks': []}
                part['chapters'].append(ch)
                cur = ch['blocks']
            else:
                raise ValueError(f'{path}:{no}: 알 수 없는 태그 {tag}')
            continue
        if not LINE_RE.match(line):
            raise ValueError(f'{path}:{no}: 형식 오류: {line[:80]}')
        if cur is None:
            raise ValueError(f'{path}:{no}: @OPENING 이나 @CH 앞에 본문이 있음')
        cur.append(parse_block(line, interviewers))
    return part


def parse_block(line, interviewers=()):
    if line.startswith('Q|'):
        _, who, t = line.split('|', 2)
        who = who.strip()
        return {'k': 'q', 'who': who, 'iv': who in interviewers, 't': t.strip()}
    if line.startswith('V|'):
        _, n, t = line.split('|', 2)
        return {'k': 'vow', 'n': n.strip(), 't': t.strip()}
    kind = {'N': 'p', 'C': 'cont', 'M': 'memo'}[line[0]]
    return {'k': kind, 't': line[2:].strip()}


def line_of(b):
    k, t = b['k'], b['t']
    if k == 'q': return f"Q|{b['who']}| {t}"
    if k == 'cont': return f"C| {t}"
    if k == 'memo': return f"M| {t}"
    if k == 'vow': return f"V|{b['n']}| {t}"
    return f"N| {t}"


def write_file(part, path):
    L = [f"@PART {part['id']}", f"@TITLE {part['title']}"]
    if part.get('sub'): L.append(f"@SUB {part['sub']}")
    if part.get('byline'): L.append(f"@BYLINE {part['byline']}")
    L += [f"@NOTE {n}" for n in part.get('notes', [])]
    L += [f"@CAST {c}" for c in part.get('cast', [])]
    if part['opening']:
        L.append('@OPENING')
        L += [line_of(b) for b in part['opening']]
    for ch in part['chapters']:
        h = ch['head']
        L += ['', f"@CH {h.get('num','')}|{h.get('label','')}|{h.get('title','')}|{h.get('sub','')}|{h.get('special','')}"]
        L += [line_of(b) for b in ch['blocks']]
    open(path, 'w', encoding='utf-8').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    # python3 textfmt.py dump stories/piece1.txt  → 구조를 JSON으로 출력(디버그용)
    if sys.argv[1] == 'dump':
        print(json.dumps(parse_file(sys.argv[2]), ensure_ascii=False, indent=1))
