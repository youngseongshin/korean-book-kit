#!/usr/bin/env python3
"""소설책 PDF 키트 명령어 모음.

  python3 bookkit.py setup                         필요한 파이썬 패키지 확인·설치 안내
  python3 bookkit.py new <project_dir>             빈 프로젝트(설정 견본 + 원고 견본) 만들기
  python3 bookkit.py ingest <원고> <project_dir> [--speakers 이름,…]   원고 → 줄 형식 초안
  python3 bookkit.py snapshot <project_dir> <이름>  stories/ 를 history/<이름>/ 으로 보관(편집 패스 전후)
  python3 bookkit.py check <project_dir> <mode> [in] <out>   편집 결과 검증(polish|flavor|rewrite|lint)
  python3 bookkit.py lint <project_dir>             stories/ 전체 lint
  python3 bookkit.py build <project_dir>            HTML 조립
  python3 bookkit.py render <project_dir>           PDF 렌더
  python3 bookkit.py verify <project_dir> [...]     PDF 최종 점검 + 견본 쪽 이미지
  python3 bookkit.py all <project_dir>              lint → build → render → verify
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tomllib
import urllib.request

KIT = os.path.dirname(os.path.abspath(__file__))
E = os.path.join(KIT, 'engine')

GOOGLE_FONTS_REV = '9710da1eacb3be272583c3224dcb70f9da6eadbb'
PAGEDJS_URL = 'https://unpkg.com/pagedjs@0.4.3/dist/paged.polyfill.js'
PAGEDJS_SHA256 = 'f59f361802416c770d549a647958649af2cf6601999924bc00e4f507dad5269f'

FONT_FILES = {
    'GowunBatang-Regular.ttf': ('ofl/gowunbatang/GowunBatang-Regular.ttf', 'f466518a681280c0d8ee1b35de520c4ea3127630'),
    'GowunBatang-Bold.ttf': ('ofl/gowunbatang/GowunBatang-Bold.ttf', '5c89211eaffc15f718f050269e0ee8f76eefd644'),
    'GowunDodum-Regular.ttf': ('ofl/gowundodum/GowunDodum-Regular.ttf', '2d87cc83583a37bd7828c638eb9bab6df3cf596c'),
    'NanumMyeongjo-Regular.ttf': ('ofl/nanummyeongjo/NanumMyeongjo-Regular.ttf', '8c1bb666acfac3668c6b433b8419cd70d9140045'),
    'NanumMyeongjo-ExtraBold.ttf': ('ofl/nanummyeongjo/NanumMyeongjo-ExtraBold.ttf', '563257513ddac64b1fe1d4423bbd9cacb85bbeb3'),
    'NanumPenScript-Regular.ttf': ('ofl/nanumpenscript/NanumPenScript-Regular.ttf', '565747d0573126bb057d0675151c894bf019d7a5'),
}



def git_blob_sha(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def ensure_fonts():
    font_dir = os.path.join(KIT, 'assets', 'fonts')
    os.makedirs(font_dir, exist_ok=True)
    base = f'https://raw.githubusercontent.com/google/fonts/{GOOGLE_FONTS_REV}'
    for name, (source, expected_sha) in FONT_FILES.items():
        dst = os.path.join(font_dir, name)
        if os.path.exists(dst):
            data = open(dst, 'rb').read()
            if git_blob_sha(data) == expected_sha:
                print('ok font', name)
                continue
        url = f'{base}/{source}'
        print('download font', name)
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
        actual = git_blob_sha(data)
        if actual != expected_sha:
            raise RuntimeError(f'font checksum mismatch: {name} {actual}')
        tmp = dst + '.tmp'
        with open(tmp, 'wb') as f:
            f.write(data)
        os.replace(tmp, dst)


def ensure_pagedjs():
    dst = os.path.join(KIT, 'assets', 'vendor', 'paged.polyfill.js')
    if os.path.exists(dst):
        data = open(dst, 'rb').read()
        if hashlib.sha256(data).hexdigest() == PAGEDJS_SHA256:
            print('ok pagedjs 0.4.3')
            return
    print('download pagedjs 0.4.3')
    with urllib.request.urlopen(PAGEDJS_URL, timeout=60) as response:
        data = response.read()
    actual = hashlib.sha256(data).hexdigest()
    if actual != PAGEDJS_SHA256:
        raise RuntimeError(f'pagedjs checksum mismatch: {actual}')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    tmp = dst + '.tmp'
    with open(tmp, 'wb') as f:
        f.write(data)
    os.replace(tmp, dst)


def run(*a):
    r = subprocess.run([sys.executable, *a])
    if r.returncode:
        sys.exit(r.returncode)


def lint_all(project):
    cfg = tomllib.load(open(os.path.join(project, 'book.toml'), 'rb'))
    sdir = os.path.join(project, cfg.get('paths', {}).get('stories', 'stories'))
    for p in cfg['parts']:
        print(f"[{p['file']}]", end=' ', flush=True)
        run(os.path.join(E, 'checks.py'), project, 'lint', os.path.join(sdir, p['file']))


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    cmd, *rest = sys.argv[1:]
    if cmd == 'setup':
        ensure_fonts()
        ensure_pagedjs()
        for mod, pkg in (('pymupdf', 'pymupdf'), ('playwright', 'playwright')):
            try:
                __import__(mod); print('ok', pkg)
            except ImportError:
                print(f'없음: pip install --break-system-packages {pkg}  (playwright는 이어서 `playwright install chromium`)')
    elif cmd == 'new':
        dst = rest[0]
        shutil.copytree(os.path.join(KIT, 'templates', 'project'), dst)
        print('만듦:', dst, '→ book.toml 과 stories/ 를 채우세요')
    elif cmd == 'ingest':
        run(os.path.join(E, 'ingest.py'), *rest)
    elif cmd == 'snapshot':
        project, name = rest
        cfg = tomllib.load(open(os.path.join(project, 'book.toml'), 'rb'))
        src = os.path.join(project, cfg.get('paths', {}).get('stories', 'stories'))
        dst = os.path.join(project, 'history', name)
        shutil.copytree(src, dst)
        print('보관:', dst)
    elif cmd == 'check':
        run(os.path.join(E, 'checks.py'), *rest)
    elif cmd == 'lint':
        lint_all(rest[0])
    elif cmd == 'build':
        run(os.path.join(E, 'build.py'), *rest)
    elif cmd == 'render':
        run(os.path.join(E, 'render.py'), *rest)
    elif cmd == 'verify':
        run(os.path.join(E, 'verify_pdf.py'), *rest)
    elif cmd == 'all':
        p = rest[0]
        lint_all(p)
        run(os.path.join(E, 'build.py'), p)
        run(os.path.join(E, 'render.py'), p)
        run(os.path.join(E, 'verify_pdf.py'), p, *rest[1:])
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
