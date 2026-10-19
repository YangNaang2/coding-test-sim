import _sqlworld as w

META = {
    'id': 'S01',
    'title': '신규 상장 IT 종목',
    'level': 1,
    'tags': ['SELECT', 'WHERE', 'ORDER BY'],
    'ordered': True,
    'description': '''
<p><code>STOCKS</code> 테이블에서 <b>2024년 1월 1일 이후(당일 포함)</b>에 상장한 <b>KOSDAQ</b> 시장의 <b>IT</b> 업종 종목을 조회하려 합니다.</p>
<p>종목 코드(<code>CODE</code>), 종목명(<code>NAME</code>), 상장일(<code>LISTED_AT</code>)을 조회하는 SQL 문을 작성해 주세요. 결과는 상장일 오름차순으로, 상장일이 같으면 종목 코드 오름차순으로 정렬해 주세요.</p>
''',
    'explanation': '''
<p>세 조건을 AND로 묶고 정렬 기준을 두 개 씁니다.</p>
<ul>
<li>"이후(당일 포함)"는 <code>&gt;=</code>입니다. <code>&gt;</code>를 쓰면 2024-01-01에 상장한 종목이 빠집니다.</li>
<li>정렬 기준이 두 개라고 했으면 둘 다 써야 합니다. 상장일이 같은 종목은 두 번째 기준이 없으면 순서가 정해지지 않습니다.</li>
<li>DATE 컬럼은 <code>'2024-01-01'</code> 같은 문자열과 비교할 수 있습니다(MySQL·Oracle 모두. Oracle은 <code>DATE '2024-01-01'</code>도 가능).</li>
</ul>
''',
}

SCHEMA = [w.STOCKS]


def sample():
    return {'STOCKS': [
        ['310010', '한빛소프트', 'KOSDAQ', 'IT', '2024-01-01'],
        ['310020', '누리바이오', 'KOSDAQ', 'BIO', '2024-02-15'],
        ['310030', '다온테크', 'KOSDAQ', 'IT', '2023-12-31'],
        ['310040', '가람전자', 'KOSPI', 'IT', '2024-03-02'],
        ['310070', '새솔소프트', 'KOSDAQ', 'IT', '2025-06-10'],
        ['310050', '푸른테크', 'KOSDAQ', 'IT', '2025-06-10'],
        ['310060', '미래금융', 'KOSDAQ', None, '2024-07-01'],
        ['310080', '은빛화학', 'KOSPI', 'CHEM', '2022-11-11'],
    ]}


def hidden(rng):
    rows = w.stocks(rng, 400)
    # 경계일과 같은 날 상장한 종목들을 코드 내림차순으로 넣어 정렬 기준 누락을 걸러낸다
    for k, code in enumerate(['999990', '999970', '999950', '999930']):
        rows.append([code, '경계테크%d' % k, 'KOSDAQ', 'IT', '2024-01-01'])
    for k, code in enumerate(['999980', '999960']):
        rows.append([code, '동일소프트%d' % k, 'KOSDAQ', 'IT', '2025-03-03'])
    rows.append(['999940', '직전전자', 'KOSDAQ', 'IT', '2023-12-31'])
    rows.append(['999920', '코스피테크', 'KOSPI', 'IT', '2024-01-01'])
    rng.shuffle(rows)
    return {'STOCKS': rows}


SOLUTION = '''
SELECT CODE, NAME, LISTED_AT
FROM STOCKS
WHERE MARKET = 'KOSDAQ'
  AND SECTOR = 'IT'
  AND LISTED_AT >= '2024-01-01'
ORDER BY LISTED_AT, CODE;
'''

ALT = [
    "SELECT CODE, NAME, LISTED_AT FROM STOCKS WHERE SECTOR = 'IT' AND MARKET = 'KOSDAQ' "
    "AND DATE_FORMAT(LISTED_AT, '%Y-%m-%d') >= '2024-01-01' ORDER BY 3, 1",
    "SELECT CODE, NAME, LISTED_AT FROM STOCKS WHERE SECTOR = 'IT' AND MARKET = 'KOSDAQ' "
    "AND TO_CHAR(LISTED_AT, 'YYYYMMDD') >= '20240101' ORDER BY LISTED_AT ASC, CODE ASC",
]

WRONG = {
    '당일 미포함(>)': "SELECT CODE, NAME, LISTED_AT FROM STOCKS WHERE MARKET = 'KOSDAQ' AND SECTOR = 'IT' "
                   "AND LISTED_AT > '2024-01-01' ORDER BY LISTED_AT, CODE",
    '시장 조건 누락': "SELECT CODE, NAME, LISTED_AT FROM STOCKS WHERE SECTOR = 'IT' AND LISTED_AT >= '2024-01-01' "
                 "ORDER BY LISTED_AT, CODE",
    '두 번째 정렬 누락': "SELECT CODE, NAME, LISTED_AT FROM STOCKS WHERE MARKET = 'KOSDAQ' AND SECTOR = 'IT' "
                   "AND LISTED_AT >= '2024-01-01' ORDER BY LISTED_AT",
}
