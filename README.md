# 코딩테스트 모의 응시 프로그램

알고리즘 2문제 + SQL 1문제 형식의 온라인 코딩테스트를 내 PC에서 실전처럼 연습하는 프로그램입니다. 화면 구성과 채점 방식은 `solution()` 함수의 반환값으로 채점하는 일반적인 코딩테스트 플랫폼 방식을 따릅니다.

## 실행

```
python app.py
```

또는 `실행하기.bat`을 더블클릭하면 브라우저가 열립니다(기본 주소 http://localhost:8765). 종료하려면 실행 창에서 Ctrl+C를 누릅니다.

- 필요: Python 3.8 이상. 추가 설치는 없습니다(표준 라이브러리만 사용).
- 선택: `node`(JavaScript), `javac`/`java`(Java), `g++`(C++)가 PATH에 있으면 해당 언어가 자동으로 켜집니다.
- 에디터(Monaco)는 인터넷에서 불러옵니다. 인터넷이 막혀 있으면 자동으로 기본 에디터로 바뀌고, 설정에서 기본 에디터를 고정할 수도 있습니다.

## 기능

| 구분 | 내용 |
|---|---|
| 실전 모의고사 | 보통 알고리즘 1 + 보통~어려움 알고리즘 1 + SQL 1을 무작위로 출제. 기본 70분(설정에서 변경). 10분·5분 전 경고, 시간이 끝나면 마지막 코드를 자동 제출 |
| 문제별 연습 | 시간 제한 없이 한 문제씩. 최고 점수 기록, 언제든 해설 보기 |
| 코드 실행 | 입출력 예 + 직접 추가한 테스트 케이스로 실행. 케이스별 통과 여부, 실행 시간, 기댓값과 실행 결과 비교, print 출력 |
| 제출 후 채점하기 | 숨겨진 정확성 테스트 전체로 채점. 케이스별 통과/실패/시간 초과/런타임 에러와 실행 시간만 공개, 점수는 통과 비율 |
| SQL | MySQL/Oracle 선택. 스키마·예시 데이터·예시 결과 표시, 실행 결과 표, 숨겨진 채점용 데이터로 정답 판정 |
| 레퍼런스 | Python, SQL(MySQL↔Oracle 대응표), JavaScript, Java 요약 |
| 결과·해설 | 문제별 점수, 제출 횟수, 머문 시간. 모범 답안, 핵심 아이디어, 엣지 케이스, 통과하지 못한 숨김 테스트 공개 |
| 기록 | 회차별 총점 추이 그래프(`data/history.json`) |
| 자동 저장 | 문제별·언어별 코드, 진행 중인 시험, 설정을 `data/state.json`에 저장. 새로고침이나 재실행 후에도 이어서 풀기 |
| 실전 모드 | 자동완성·힌트 기본 꺼짐(설정에서 켜기 가능), 글자 크기·테마 설정 |

## 문제 은행

알고리즘 16문제(쉬움 5, 보통 8, 어려움 3), SQL 10문제(쉬움 3, 보통 5, 어려움 2). 모두 금융·증권 소재이며, 후기에서 나온 "해시 + 구현에 조건 함정", "해시 + 이분 탐색 + 완전 탐색 + 구현 복합" 유형을 각각 2문제 이상 넣었습니다.

| 번호 | 제목 | 난이도 | 유형 |
|---|---|---|---|
| A01 | 체결 로그 정리 | 쉬움 | 해시, 구현, 정렬 (후기 유형) |
| A02 | 수수료와 세금 | 쉬움 | 구현, 정수 연산(실수 오차 함정) |
| A03 | 최장 상승 구간 | 쉬움 | 구현 |
| A04 | 주문 되돌리기 | 쉬움 | 스택, 시뮬레이션 |
| A05 | 계좌번호 검증 | 쉬움 | 문자열, 해시 |
| A06 | 이상 거래 탐지 | 보통 | 해시, 정렬, 시각 파싱 (후기 유형) |
| A07 | 조건 검색기 | 보통 | 해시, 이분 탐색, 완전 탐색 (후기 복합 유형) |
| A08 | 두 업종 분산 투자 | 보통 | 해시, 이분 탐색, 완전 탐색 (후기 복합 유형) |
| A09 | 수익률 랭킹 | 보통 | 다중 조건 정렬, 집계 |
| A10 | 최단 기간 거래량 | 보통 | 투 포인터 |
| A11 | 결재 서류 전달 | 보통 | BFS(격자) |
| A12 | 명의자 계좌 묶기 | 보통 | Union-Find / 그래프 탐색 |
| A13 | 결제 배치 묶기 | 보통 | 그리디, 투 포인터 |
| A14 | 호가창 체결 | 어려움 | 힙, 시뮬레이션 |
| A15 | 쿨다운이 있는 매매 | 어려움 | DP |
| A16 | 수수료 면제 쿠폰 | 어려움 | 다익스트라(상태 확장) |
| S01 | 신규 상장 IT 종목 | 쉬움 | WHERE, ORDER BY |
| S02 | 시장별 종목 수 | 쉬움 | GROUP BY, COUNT와 NULL |
| S03 | 휴면 계좌 보유 회원 | 쉬움 | JOIN, DISTINCT, COALESCE |
| S04 | 10월 매수 체결 상위 회원 | 보통 | 다중 JOIN, HAVING, 날짜 범위 |
| S05 | 주문 이력 없는 계좌 | 보통 | LEFT JOIN, NOT EXISTS, NOT IN 함정 |
| S06 | 월별 체결 통계 | 보통 | 연월 집계 |
| S07 | 회원 등급 산정 | 보통 | LEFT JOIN 조건 위치, CASE |
| S08 | 업종 평균보다 비싼 종목 | 보통 | 상관 서브쿼리 |
| S09 | 종목별 최고 종가일 | 어려움 | 그룹별 최댓값 행, ROW_NUMBER |
| S10 | 업종별 거래대금 TOP 2 | 어려움 | CTE, 윈도 함수 순위 |

## SQL 엔진 안내

채점은 Python에 들어 있는 SQLite로 합니다. 문제는 MySQL·Oracle·SQLite에서 똑같이 동작하는 표준 문법으로 풀리게 만들었고, 자주 쓰는 MySQL·Oracle 함수(`DATE_FORMAT`, `IFNULL`, `IF`, `YEAR`, `MONTH`, `DATEDIFF`, `TO_CHAR`, `TO_DATE`, `NVL`, `NVL2`, `DECODE`, `TRUNC`, `MOD`, `LPAD` 등)와 Oracle의 `FETCH FIRST n ROWS ONLY`, `FROM DUAL`을 흉내 내어 지원합니다.

실제 DB와 다른 점:

- 날짜·시각이 문자열이라 `ORDERED_AT <= '2026-11-01'`이 11월 1일 0시를 포함하지 않습니다(MySQL은 포함).
- 정수 ÷ 정수는 몫만 남습니다(MySQL은 소수).
- `GROUP BY`에 없는 컬럼을 SELECT에 써도 에러가 나지 않습니다(MySQL ONLY_FULL_GROUP_BY·Oracle은 에러).
- `EXTRACT`는 지원하지 않습니다.

## 폴더 구조

```
coding-test-sim/
  app.py              서버(표준 라이브러리 http.server)
  judge.py            채점기: 언어별 하네스 실행, 반환값 비교, SQL 실행·비교
  runners/            언어별 하네스 (py_runner.py, js_runner.js, Main.java, ct_head.hpp)
  static/             화면 (index.html, app.js, style.css, reference.html)
  problems/algo/      알고리즘 문제 JSON (A01~A16)
  problems/sql/       SQL 문제 JSON (S01~S10)
  tools/specs/        출제 명세: 지문, 모범 답안, 완전 탐색 풀이, 오답 풀이, 테스트 생성기
  tools/build.py      명세 → 문제 JSON 생성
  tools/verify.py     전체 검증
  data/               자동 저장(state.json), 응시 기록(history.json)
  실행하기.bat
```

## 문제 추가하기

`problems/algo/` 또는 `problems/sql/`에 JSON 파일을 넣고 프로그램을 다시 실행하면 목록에 나타납니다.

알고리즘 문제:

```json
{
  "id": "A17", "type": "algo", "title": "제목", "level": 2,
  "tags": ["해시", "구현"],
  "description": "<p>문제 설명(HTML)</p>",
  "constraints": ["제한사항 1", "제한사항 2"],
  "params": [{"name": "orders", "type": "string[]"}, {"name": "k", "type": "int"}],
  "returnType": "int[]",
  "examples": [{"input": [["a b"], 3], "output": [1, 2]}],
  "exampleNotes": "<p>입출력 예 설명(HTML)</p>",
  "tests": [{"input": [["a b"], 3], "output": [1, 2]}],
  "timeLimit": 10,
  "solution": "def solution(orders, k):\n    ...",
  "explanation": "<p>해설(HTML)</p>",
  "edgeCases": ["놓치기 쉬운 경우"]
}
```

- 타입: `int`, `long`, `double`, `bool`, `string`과 그 배열(`int[]`, `string[][]` 등). 언어별 기본 코드는 타입에서 자동으로 만들어집니다.
- 반환값 비교: 정수·문자열·불리언은 정확히, `double`은 1e-6 오차까지 허용, 배열은 순서까지 비교합니다.

SQL 문제는 `schema`(테이블·컬럼 정의), `data.sample`/`data.hidden`(행 배열), `expected.sample`/`expected.hidden`(기댓값), `ordered`(행 순서 비교 여부)가 필요합니다. 직접 쓰기보다 `tools/specs/s01_new_listings.py`를 복사해 명세를 만든 뒤 `python tools/build.py sql`로 생성하는 편이 쉽습니다.

## 검증

```
python tools/build.py          # 명세로 문제 JSON 다시 만들기 (입출력 예가 모범 답안과 맞는지 확인)
python tools/verify.py         # 전체 검증 (몇 분 걸림)
```

`verify.py`가 확인하는 항목:

1. 모범 답안이 실제 채점기로 입출력 예와 정확성 테스트를 100% 통과
2. 작은 무작위 입력 200개에서 모범 답안과 완전 탐색 풀이의 결과가 일치
3. 일부러 틀린 풀이(경계 처리 누락, 동점 정렬 누락, 비효율 풀이 등)가 실제로 실패
4. SQL 모범 답안과 다른 방식의 정답(MySQL·Oracle 함수 사용)이 기댓값과 일치하고, 흔한 오답 쿼리가 실패
5. 무한 루프·예외·잘못된 반환값이 시간 초과·런타임 에러·실패로 판정되고 서버가 멈추지 않음
6. JavaScript·Java로 실제 문제를 풀었을 때 통과

C++ 하네스는 코드만 포함되어 있고, 작성 시점의 PC에 g++가 없어 실행 검증은 하지 못했습니다. g++를 설치한 뒤 `python tools/verify.py harness`로 확인할 수 있습니다.
