# korean-book-kit

원고(PDF·DOCX·TXT)를 **편집 패스로 다듬고**, 표지·간지·삽화·차례를 갖춘 **한국어 A5 소설책 PDF로 조판**하는 키트.
사람 편집자나 Claude 같은 AI 에이전트가 함께 쓰도록 만들었다. 편집 지침과 검증기가 같이 들어 있다.

![데모 책 견본 쪽](docs/preview.png)

데모: [`docs/demo.pdf`](docs/demo.pdf) (24쪽, `examples/demo`에서 그대로 생성)

- 책마다 바뀌는 것은 **`book.toml` 하나와 `stories/*.txt`**(한 줄 = 한 문단)뿐이다. 엔진·스타일·삽화는 공용.
- 편집은 **6가지 패스**(내용 교체, 윤문, 작가 문체, 말맛·여운, 교정, 호칭) 지침과 검증기로 돌린다.
- 매 패스 뒤 `checks.py`가 OK여야 다음으로 간다. 마지막엔 `verify`가 만든 견본 쪽 이미지를 눈으로 본다.

---

## 1. 빠른 시작

```bash
git clone https://github.com/youngseongshin/korean-book-kit.git
cd korean-book-kit
pip install -r requirements.txt
playwright install chromium
python3 bookkit.py setup                  # 고정 버전 서체·Paged.js 내려받기 + 의존성 확인

python3 bookkit.py all examples/demo        # → examples/demo/build/book.pdf
python3 bookkit.py new mybook               # 새 책 폴더
```
Python 3.11 이상(tomllib). Node는 필요 없다(`setup`이 Paged.js 0.4.3을 고정 해시로 검증해 받는다).

## 2. 폴더 구조

```
korean-book-kit/
├─ bookkit.py               명령어 모음
├─ engine/
│  ├─ ingest.py             원고 → 줄 형식 초안 (PDF 좌표로 문단 복원, 화자 감지, 따옴표 정리)
│  ├─ textfmt.py            줄 형식 파서/작성기
│  ├─ build.py              book.toml + stories → build/book.html (Paged.js)
│  ├─ render.py             HTML → PDF (Chromium, Playwright)
│  ├─ checks.py             편집 패스 검증기 (polish | flavor | rewrite | lint)
│  ├─ verify_pdf.py         완성 PDF 점검 + 견본 쪽 모음 이미지
│  └─ art.py                손으로 짠 SVG 삽화 (표지·면지·간지 7종, 소품 18종)
├─ assets/
│  ├─ book.css              조판 스타일 (A5, 서체, 쪽 종류별 규칙)
│  ├─ fonts/                OFL 전문 + setup이 받는 고정 버전 서체 (바이너리는 Git 제외)
│  └─ vendor/               Paged.js 라이선스 + setup이 받는 0.4.3 바이너리
├─ editorial/
│  ├─ house_rules.md        모든 패스에 붙는 공통 편집 원칙
│  ├─ passes/01~06_*.md     패스별 지침
│  ├─ agent_prompt.md       서브에이전트 지시문 견본과 운영 규칙
│  └─ feedback_log.md       지적 → 원인 → 대응 기록 양식
├─ templates/project/       새 책 견본 (book.toml + stories/story1.txt)
├─ examples/demo/           데모 책 (두 편, 모든 쪽 종류 포함)
└─ docs/                    견본 이미지와 데모 PDF
```

## 3. 명령어

| 명령 | 하는 일 |
|---|---|
| `bookkit.py setup` | 고정 버전 OFL 서체·Paged.js 내려받기 + 필요한 패키지 확인 |
| `bookkit.py new <dir>` | 새 책 폴더 만들기 |
| `bookkit.py ingest <원고> <dir> [--speakers 이름,…]` | 원고 → `draft.txt`, `draft_review.txt` |
| `bookkit.py snapshot <dir> <vNN_이름>` | `stories/`를 `history/vNN_이름/`으로 보관 |
| `bookkit.py check <dir> <mode> <입력> <출력>` | 편집 결과 검증 |
| `bookkit.py lint <dir>` | 원고 전체 형식·금지어 검사 |
| `bookkit.py build / render / verify <dir>` | 조립 / PDF / 점검 |
| `bookkit.py all <dir>` | lint → build → render → verify |

---

## 4. 작업 흐름

```
원고 ─▶ ① 수집 ─▶ ② 구조 잡기 ─▶ ③ 첫 조판(디자인 확정) ─▶ ④ 편집 패스 루프 ─▶ ⑤ 최종 검수 ─▶ ⑥ 전달
          ingest      stories/*.txt     book.toml + all          passes + check         verify + 눈       PDF
                                                            ▲            │
                                                            └─ 피드백 → house_rules 갱신
```

### ① 수집
`bookkit.py ingest 원고.pdf mybook --speakers 할머니,할아버지,나`
- PDF는 줄 좌표로 문단을 다시 잇는다. 본문 글자보다 1.2배 큰 줄은 장 제목 후보 `@CH |||제목|`이 된다.
- `draft_review.txt`(쪽 번호·제목 표시가 붙은 문단 목록)를 훑어 잘못 이어진 문단을 찾는다.
- 화자 표기가 제각각인 원고는 1회용 변환 스크립트를 따로 쓰는 편이 빠르다.

### ② 구조 잡기
`draft.txt`를 이야기(부)별 파일로 나눠 `stories/`에 둔다.
- 각 파일 머리: `@PART`, `@TITLE`, `@SUB`, `@NOTE`(허구 고지), `@OPENING`(첫 장 앞 도입부)
- 장 머리 `@CH num|label|title|sub|special`: num은 차례·검증용 번호, label은 찍히는 꼬리표(`1`, `1장`, `프롤로그`), special=`vows`면 목록 한 쪽짜리 면.
- 대담형은 `Q|화자|`, 소설형은 `N| “대사”`. 질문자 이름을 book.toml `interviewers`에 넣으면 회색으로 조판된다.
- 장 제목의 번역투(“~는가”)는 이 단계에서 미리 고친다.
- `bookkit.py lint mybook`이 OK가 날 때까지.

### ③ 첫 조판: 디자인 먼저
편집이 길어질수록 디자인 변경이 비싸진다. 원고를 다듬기 전에 한 번 찍는다.
- 부마다 `tint`(간지 바탕), `accent`(장 번호·화자 색), `art`(간지 그림), `vignettes`(장 머리 소품 순환)를 고른다. 그림 목록: `python3 engine/art.py gallery.html`.
- `bookkit.py all mybook` → `build/proof/contact.png`로 표지·간지·차례·본문·목록 쪽 확인.
- 스타일 조정은 프로젝트 폴더의 `extra.css`로 덮어쓴다(키트의 book.css는 고치지 않는다).

### ④ 편집 패스 루프
| 패스 | 지침 | check mode | 분량 | 실행 |
|---|---|---|---|---|
| 01 내용 교체 | passes/01_content_swap.md | rewrite | 조정 | 메인 작업자가 직접(의뢰인과 범위 합의) |
| 02 윤문 3회독 | passes/02_polish.md | polish | 0.85~1.10 | 편당 에이전트, 회독은 순차 |
| 03 작가 문체 | passes/03_author_style.md | rewrite | 1.00~1.45 | 편당 에이전트 → 대조 리뷰 → 02 |
| 04 말맛·여운 | passes/04_flavor.md | flavor | 0.85~1.15 | 편당 에이전트 → 05 |
| 05 교정 | passes/05_proof.md | polish | 0.85~1.10 | 편당 에이전트, 사실 수정은 보고 |
| 06 호칭·이름 | passes/06_naming.md | polish | 0.85~1.10 | 편당 에이전트 + 화자 표시는 스크립트 |

**권장 순서:** 01 → 06 → 03(선택) → 02×3 → 04 → 05. 이름·호칭은 일찍 잡아야 뒤 패스를 다시 돌리지 않는다.

**한 패스의 절차**
1. `bookkit.py snapshot mybook v03_윤문1` — 입력 보관
2. 지침의 `{{…}}`를 채워 `editorial/agent_prompt.md` 형식으로 이야기 1편당 에이전트 1개를 동시에 띄운다.
3. 에이전트 보고가 오면 메인 작업자가 `bookkit.py check`를 다시 돌린다.
4. `bookkit.py all mybook` → 견본 쪽 확인 → 의뢰인에게 전달.
5. 지적은 `editorial/feedback_log.md`에 적고, 규칙이면 `house_rules.md`, 기계로 잡을 수 있으면 book.toml `[rules]`로.

### ⑤ 최종 검수 체크리스트
- [ ] `bookkit.py verify` OK: 바꾼 옛 이름(`retired`) 0, 곧은 따옴표 0
- [ ] `contact.png`와 문제 쪽 확대: 표지, 간지 그림과 바탕 대비, 차례 한 쪽·꼬리표 줄바꿈, 장 첫 쪽, 화자 칸 넘침, 메모 상자, 목록 쪽 넘침, 맺음 쪽
- [ ] 판권면의 숫자·목록이 실제 구성과 맞는가(“다섯 이야기” 등)
- [ ] 제사·뒤표지 인용 문구가 최종 본문에 실제로 있는가
- [ ] 특정 독자용이면 해당 부 `forbidden`이 0건이고 그 사람을 가리키는 문장을 직접 읽었는가
- [ ] 쪽수 변화가 예상 범위인가(갑자기 늘면 빈 쪽·넘침)

---

## 5. 원고 줄 형식

| 줄 | 뜻 |
|---|---|
| `@PART 1` | 부 식별자 |
| `@TITLE` `@SUB` `@BYLINE` | 부 제목·부제·지은이 줄 (간지) |
| `@NOTE` | 허구 고지 등 각주 (등장인물 쪽 아래) |
| `@CAST` | 등장인물 소개 문단 (book.toml에 `cast`가 없을 때) |
| `@OPENING` | 첫 장 앞 도입부 시작 |
| `@CH num\|label\|title\|sub\|special` | 장 머리 |
| `N\| …` | 서술 문단 (소설식 대사 “…” 포함) |
| `Q\|화자\| …` / `C\| …` | 화자 표시형 대사 / 같은 화자의 이어지는 문단 |
| `M\| …` | 손글씨 메모 상자 (`memo_head_regex`에 맞는 머리는 붉게) |
| `V\|번호\| …` | 목록 항목 (special=vows 장) |

한 줄 = 한 문단. 빈 줄은 무시. 따옴표 ‘ ’ “ ”, 말줄임 … . 예: [`examples/demo/stories`](examples/demo/stories)

## 6. book.toml 항목

| 표 | 항목 | 설명 |
|---|---|---|
| `[book]` | title, subtitle, kicker, editor, running_head, page_size | 표지·속표지·머리글 |
| `[paths]` | stories | 원고 폴더 |
| `[art]` | cover, endpaper | `art.COMPOSITIONS` 이름 |
| `[front]` | title_vignette, dedication, epigraph[], epigraph_src, colophon[] | 판권면: 첫 줄은 제목, `+`로 시작하면 앞 여백 |
| `[back]` | quote[], src, blurb[], vignettes[] | 뒤표지 |
| `[text]` | interviewers[], cast_heading, memo_head_regex | |
| `[ending]` | heading, question, date, lines, foot, accent | 독자가 손으로 쓰는 맺음 쪽(선택) |
| `[rules]` | forbidden_regex[], retired[], ratio_polish/flavor/rewrite | 검증 규칙 |
| `[[parts]]` | file, name, tint, accent, art, vignettes[], style | 읽는 순서대로. accent는 art.py 팔레트 이름이나 #hex |
| | chapter_label | `label`(기본) 또는 `num` |
| | speakers | `hanging`(이름 칸 3.3em, 기본) / `inline`(화자 표시가 4자를 넘을 때) |
| | cast[[이름, 소개]], notes[], opening_to_notes | 등장인물 쪽 |
| | lead_bold_regex | 문단 첫머리 굵게(예: ‘김순자(81)와 박영철(83).’) |
| | dialogue_names[], forbidden[] | 부별 검증 규칙 |

## 7. 디자인

- **판형:** A5 148×210mm. 여백 19/16/21/19mm, 펼침면 좌우 대칭. 왼쪽 머리글 책 제목, 오른쪽 부 제목, 쪽번호 아래 가운데.
- **서체:** 본문 고운바탕 9.3pt/1.8, 제목 나눔명조 ExtraBold, 라벨·화자·쪽번호 고운돋움, 메모·답장 나눔손글씨 펜.
- **색:** 종이 #FDF9F1, 먹 #2B2620. 부마다 간지 바탕(tint)과 강조색(accent) 한 쌍.
- **쪽 순서:** 표지 → 면지 → 속표지 → 판권 → 헌사 → 제사 → 차례 → [부마다: 간지 → 등장인물 → 도입부 → 장들] → 맺음 쪽 → 면지 → 뒤표지.
- **삽화:** 납작한 과슈 색면에 살짝 어긋난 먹선(리소 인쇄 느낌)을 얹은 SVG. 소품은 이야기 속 물건(귤, 찻잔, 우산, 라디오, 녹음기, 안경, 실패…)이다.

### 확장
- **새 소품:** `art.py`에 함수 하나(기존 `ink()`, `circ()`, `ell()`, `g()` 조합) → `vignette()`의 `parts`와 `VIGNETTE_NAMES`에 추가.
- **새 간지 그림:** `def part6_art(): return svg(470, 500, …)` → `COMPOSITIONS`에 등록.
- **판형 변경:** `page_size`와 book.css의 표지·간지 `148mm/210mm`를 함께 바꾼다.
- **새 쪽 종류:** build.py에 section, book.css에 `@page` 이름 추가.

## 8. 편집 원칙 요약

[`editorial/house_rules.md`](editorial/house_rules.md) 전문 참고.
- 번역투 금지(~에 대해, ~을 가지다, 이중 피동, 추상명사 주어, 직역 비유). 장 제목에 `~는가` 금지.
- 따옴표 ‘ ’ “ ”, 말줄임 …, 본문 em-dash 금지.
- 노년 인물: 부부는 대사에서 서로 이름을 부르지 않고, 서술도 이름 대신 할머니·할아버지. 이름은 출생 연대에 맞게.
- 반복 윤문은 문장을 평균으로 깎는다. 말맛을 살리고 장의 절반 정도만 교훈을 숨겨 여운을 준다. 획일화 금지.
- 작가 문체를 빌릴 때 실제 작품 문장·작품명은 쓰지 않는다.

## 9. 겪은 문제와 해법

| 증상 | 원인 | 해법 |
|---|---|---|
| 본문 문단 마지막 줄이 양쪽으로 벌어짐 | Paged.js가 나눈 문단에 text-align-last 상속 | `.text p {text-align-last:left}`, 쪽 넘김 조각만 `[data-split-to]{justify}` |
| 차례 꼬리표(“프롤로그”) 줄바꿈 | 꼬리표 칸 폭 부족 | `.tl {white-space:nowrap; width:11.5mm}` |
| 간지 그림이 바탕에 묻힘 | 그림 배경색 = tint | 그림 바탕을 tint와 다른 톤으로 |
| 목록·답장 쪽이 두 쪽으로 넘침 | 항목·줄 수 과다 | 글자 8.2pt, 항목 간격 1.3mm, 줄 12개 이하 |
| 화자 이름이 대사와 겹침 | ‘상길 할아버지’처럼 긴 화자 표시 | `speakers = "inline"` |
| 윤문 뒤 서술이 대사 줄에 붙음 | 에이전트가 줄을 합침 | polish 모드로 줄 수·머리말 고정 검사 |
| 매끈한데 맛이 없다 | 윤문을 반복할수록 평균 문장 | 04 말맛·여운 패스, 이후 교정은 ‘맛을 지키는 교정’ |

## 10. 라이선스

- 코드·지침·삽화: MIT ([LICENSE](LICENSE))
- 서체: 고운바탕·고운돋움·나눔명조·나눔손글씨 펜. `setup`이 Google Fonts의 고정 리비전에서 받아 Git blob SHA로 검증한다. 라이선스는 SIL Open Font License 1.1 ([assets/fonts](assets/fonts))
- Paged.js: MIT ([assets/vendor/LICENSE-pagedjs.md](assets/vendor/LICENSE-pagedjs.md))
