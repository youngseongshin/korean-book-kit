"""편집 패스 결과 검증기. 모든 편집(사람·Claude·서브에이전트)은 이걸 통과해야 다음 단계로 간다.

usage:
  python3 engine/checks.py <project_dir> <mode> <input.txt> <output.txt>
  python3 engine/checks.py <project_dir> lint <file.txt>

mode
  polish   윤문·교정·호칭 정리처럼 ‘문장만’ 고치는 패스. 줄 수와 각 줄 머리말이 입력과 같아야 하고 분량 ratio_polish.
  flavor   말맛·여운처럼 문단을 합치거나 나눌 수 있는 패스. 분량 ratio_flavor.
  rewrite  문체 다시 쓰기·장면 교체. 분량 ratio_rewrite.
  lint     형식·금지어만 검사(입력 비교 없음).

공통 검사
  - 줄 형식(@태그, N|, Q|화자|, C|, M|, V|번호|)
  - 곧은 따옴표(' ") 금지, 본문 em-dash 금지, book.toml [rules].forbidden_regex
  - 장 구조: @CH 의 num·label·special 순서와 개수, @TITLE·@BYLINE·@NOTE 는 입력과 같아야 함
  - 부별 규칙: dialogue_names(노부부가 대사에서 서로 이름 부르기 금지), forbidden(금지어)
"""
import os
import re
import sys
import tomllib

FMT = re.compile(r'^(@(PART|TITLE|SUB|BYLINE|NOTE|CAST|OPENING|CH)\b.*|N\| .+|C\| .+|M\| .+|Q\|[^|]+\| .+|V\|[^|]+\| .+)$')
ADDRESS_OK = re.compile(r'(선생님|할머님|할아버님)')   # 질문자가 ‘○○ 할머님’ 하고 부르는 건 허용


def read(p):
    return open(p, encoding='utf-8').read().rstrip('\n').split('\n')


def part_cfg(cfg, path):
    base = os.path.basename(path)
    for p in cfg.get('parts', []):
        if p['file'] == base:
            return p
    return {}


def heads(lines):
    out = []
    for l in lines:
        if l.startswith('@CH '):
            f = (l[4:].split('|') + [''] * 5)[:5]
            out.append((f[0].strip(), f[1].strip(), f[4].strip()))
    return out


def prefix(l):
    if l.startswith('@CH '):
        f = (l[4:].split('|') + [''] * 5)[:5]
        return ('@CH', f[0], f[1], f[4])
    if l.startswith(('@TITLE', '@BYLINE', '@NOTE', '@PART', '@OPENING')):
        return l
    if l.startswith('@'):
        return l.split(' ')[0]
    m = re.match(r'^(Q\|[^|]+\||V\|[^|]+\||[NCM]\|)', l)
    return m.group(1) if m else ('' if not l.strip() else 'BAD')


def body_len(lines):
    return sum(len(l) for l in lines if not l.startswith('@'))


def lint(cfg, path, lines):
    err = []
    rules = cfg.get('rules', {})
    pc = part_cfg(cfg, path)
    for i, l in enumerate(lines, 1):
        if l.strip() and not FMT.match(l):
            err.append(f'{i}: 형식 오류: {l[:70]}')
        if '"' in l or "'" in l:
            err.append(f'{i}: 곧은 따옴표 → ‘ ’ “ ”')
        if l.startswith('@CH ') and re.search(r'는가\s*\|', l):
            err.append(f'{i}: ‘~는가’ 장 제목(번역투)')
        if l.startswith('@'):
            continue
        for rx in rules.get('forbidden_regex', []):
            if re.search(rx, l):
                err.append(f'{i}: 금지 표현 /{rx}/: {l[:50]}')
        for w in pc.get('forbidden', []):
            if w in l:
                err.append(f'{i}: 이 부의 금지어 ‘{w}’')
        segs = [l.split('| ', 1)[1]] if l.startswith(('Q|', 'C|')) and '| ' in l else []
        segs += re.findall(r'“([^”]*)”', l)
        for s in segs:
            for n in pc.get('dialogue_names', []):
                if n in s and not ADDRESS_OK.search(s):
                    err.append(f'{i}: 대사 속 배우자 이름 ‘{n}’: {s[:50]}')
    return err


def compare(cfg, mode, a, b):
    err = []
    rules = cfg.get('rules', {})
    if heads(a) != heads(b):
        err.append(f'장 구조(num·label·special) 달라짐:\n  in ={heads(a)}\n  out={heads(b)}')
    for t in ('@TITLE', '@BYLINE', '@NOTE'):
        if [l for l in a if l.startswith(t)] != [l for l in b if l.startswith(t)]:
            err.append(f'{t} 줄은 바꾸지 않는다')
    if mode == 'polish':
        if len(a) != len(b):
            err.append(f'줄 수 {len(a)} → {len(b)} (polish 패스는 줄 수 유지)')
        for i, (x, y) in enumerate(zip(a, b), 1):
            if prefix(x) != prefix(y):
                err.append(f'{i}: 머리말 {prefix(x)!r} → {prefix(y)!r}')
    lo, hi = rules.get(f'ratio_{mode}', {'polish': [0.85, 1.10], 'flavor': [0.85, 1.15],
                                          'rewrite': [1.0, 1.45]}[mode])
    r = body_len(b) / max(1, body_len(a))
    print(f'분량 {body_len(a):,} → {body_len(b):,} ({r:.2f}, 허용 {lo}–{hi})')
    if not lo <= r <= hi:
        err.append(f'분량 비율 {r:.2f} 가 허용 범위 밖')
    return err


def main():
    project, mode, *files = sys.argv[1:]
    cfg = tomllib.load(open(os.path.join(project, 'book.toml'), 'rb'))
    out = files[-1]
    b = read(out)
    err = lint(cfg, out, b)
    if mode != 'lint':
        err += compare(cfg, mode, read(files[0]), b)
    if err:
        print('ERRORS'); print('\n'.join(err[:60])); sys.exit(1)
    print('OK')


if __name__ == '__main__':
    main()
