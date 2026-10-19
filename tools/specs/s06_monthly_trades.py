import _sqlworld as w

META = {
    'id': 'S06',
    'title': '월별 체결 통계',
    'level': 2,
    'tags': ['GROUP BY', '연월 추출', '날짜 범위', '집계'],
    'ordered': True,
    'description': '''
<p><code>TRADES</code> 테이블에서 <b>2026년</b>에 체결된 내역을 월별로 집계하려 합니다. 체결 시각은 <code>TRADED_AT</code>입니다.</p>
<p>월(<code>MONTH</code>, <code>'YYYY-MM'</code> 형식 문자열), 체결 건수(<code>TRADE_COUNT</code>), 총 체결 수량(<code>TOTAL_QTY</code>), 총 체결 대금(<code>TOTAL_AMOUNT</code>, 체결마다 <code>PRICE × QTY</code>를 더한 값)을 조회하는 SQL 문을 작성해 주세요. 체결이 없는 월은 출력하지 않으며, 결과는 월 오름차순으로 정렬해 주세요.</p>
''',
    'explanation': '''
<ul>
<li>연월 문자열: <code>SUBSTR(TRADED_AT, 1, 7)</code>(공통), <code>DATE_FORMAT(TRADED_AT, '%Y-%m')</code>(MySQL), <code>TO_CHAR(TRADED_AT, 'YYYY-MM')</code>(Oracle). GROUP BY에도 같은 식을 씁니다.</li>
<li>총 체결 대금은 <code>SUM(PRICE * QTY)</code>입니다. <code>SUM(PRICE) * SUM(QTY)</code>는 전혀 다른 값입니다.</li>
<li>2026년만 보려면 <code>TRADED_AT &gt;= '2026-01-01' AND TRADED_AT &lt; '2027-01-01'</code>로 거릅니다. <code>BETWEEN ... AND '2026-12-31'</code>은 12월 31일 0시 이후가 빠집니다.</li>
</ul>
''',
}

SCHEMA = [w.TRADES]


def sample():
    return {'TRADES': [
        [1, 11, 50000, 10, '2025-12-31 15:20:00'],
        [2, 12, 51000, 5, '2026-01-02 09:00:01'],
        [3, 13, 52000, 3, '2026-01-15 10:30:00'],
        [4, 14, 9900, 100, '2026-03-03 11:11:11'],
        [5, 15, 10000, 20, '2026-12-31 14:59:59'],
        [6, 16, 10100, 1, '2027-01-01 00:00:00'],
    ]}


def hidden(rng):
    rows = []
    for k in range(1200):
        rows.append([k + 1, 5000 + k, rng.randint(10, 5000) * 100, rng.randint(1, 300),
                     w.moment(rng, '2025-11-01', '2027-02-28')])
    rows += [[90001, 1, 1000, 1, '2026-12-31 15:30:00'], [90002, 2, 1000, 1, '2027-01-01 00:00:00'],
             [90003, 3, 1000, 1, '2025-12-31 23:59:59'], [90004, 4, 1000, 1, '2026-01-01 00:00:00']]
    # 2026년 2월은 체결이 없도록 지운다
    rows = [r for r in rows if not r[4].startswith('2026-02')]
    rng.shuffle(rows)
    return {'TRADES': rows}


SOLUTION = '''
SELECT SUBSTR(TRADED_AT, 1, 7) AS MONTH,
       COUNT(*) AS TRADE_COUNT,
       SUM(QTY) AS TOTAL_QTY,
       SUM(PRICE * QTY) AS TOTAL_AMOUNT
FROM TRADES
WHERE TRADED_AT >= '2026-01-01'
  AND TRADED_AT < '2027-01-01'
GROUP BY SUBSTR(TRADED_AT, 1, 7)
ORDER BY MONTH;
'''

ALT = [
    "SELECT DATE_FORMAT(TRADED_AT, '%Y-%m') AS MONTH, COUNT(*), SUM(QTY), SUM(PRICE * QTY) FROM TRADES "
    "WHERE YEAR(TRADED_AT) = 2026 GROUP BY DATE_FORMAT(TRADED_AT, '%Y-%m') ORDER BY 1",
    "SELECT TO_CHAR(TRADED_AT, 'YYYY-MM') MONTH, COUNT(*) TRADE_COUNT, SUM(QTY) TOTAL_QTY, SUM(PRICE * QTY) TOTAL_AMOUNT "
    "FROM TRADES WHERE TO_CHAR(TRADED_AT, 'YYYY') = '2026' GROUP BY TO_CHAR(TRADED_AT, 'YYYY-MM') ORDER BY MONTH",
]

WRONG = {
    'SUM(PRICE) * SUM(QTY)': SOLUTION.replace('SUM(PRICE * QTY)', 'SUM(PRICE) * SUM(QTY)'),
    "BETWEEN '2026-01-01' AND '2026-12-31'": SOLUTION.replace(
        "TRADED_AT >= '2026-01-01'\n  AND TRADED_AT < '2027-01-01'", "TRADED_AT BETWEEN '2026-01-01' AND '2026-12-31'"),
    '연도 조건 누락': SOLUTION.replace("WHERE TRADED_AT >= '2026-01-01'\n  AND TRADED_AT < '2027-01-01'\n", ''),
    '월만 추출(MM)': SOLUTION.replace('SUBSTR(TRADED_AT, 1, 7)', 'SUBSTR(TRADED_AT, 6, 2)'),
}
