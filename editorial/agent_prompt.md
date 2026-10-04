# 서브에이전트 지시문 견본

편집 패스는 **이야기 1편 = 에이전트 1개**로 나눠 한 메시지에서 동시에 띄운다. 에이전트는 이 대화를 모르므로 지시문만으로 일할 수 있어야 한다.

## 견본

```
『{{book_title}}』의 {{part_name}}({{file}}) 원고에 {{pass_name}} 패스를 적용한다.

1. 먼저 아래 두 파일을 끝까지 읽는다.
   - 공통 원칙: {{kit}}/editorial/house_rules.md
   - 이번 패스 지침: {{kit}}/editorial/passes/{{pass_file}}
2. 이 이야기에만 해당하는 내용:
   {{part_specific}}   ← 작가·문체 특징, 맛 노트, 이름 표, 금지어, 특정 독자 등
3. 입력: {{project}}/history/{{prev}}/{{file}}
   출력: {{project}}/stories/{{file}}  (긴 글은 {{project}}/work/ 에 장별로 쓰고 Bash로 이어 붙인다)
4. 출력을 쓴 뒤 반드시 실행하고 OK가 날 때까지 고친다:
   python3 {{kit}}/bookkit.py check {{project}} {{mode}} {{project}}/history/{{prev}}/{{file}} {{project}}/stories/{{file}}
5. 끝나면 보고: 검증 결과 마지막 줄, 분량 비율, 고친 곳의 성격 3줄, 사실 관계(숫자·연도·이름)를 바꾼 곳 목록.
```

## 운영 규칙
- 패스 전: `python3 bookkit.py snapshot <project> vNN_패스이름` 으로 입력을 보관한다. 에이전트 입력은 항상 보관본이다.
- 동시에 띄우되 서로 다른 파일만 쓰게 한다(같은 파일을 두 에이전트가 쓰지 않는다).
- 에이전트 보고를 믿지 말고 메인 작업자가 검증 명령을 다시 돌린다.
- 패스가 끝나면 `bookkit.py all <project>` → `build/proof/contact.png` 를 눈으로 본다.
- 높은 위험도의 패스(내용 교체, 문체 다시 쓰기)는 다른 에이전트가 원고와 결과를 대조하는 리뷰 패스를 한 번 더 돈다(만든 쪽이 스스로 채점하지 않게).
- 3회독 윤문은 회독마다 초점을 바꿔 순차로 돈다(1회독 결과가 2회독 입력).
