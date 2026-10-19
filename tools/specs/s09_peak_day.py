import _sqlworld as w

META = {
    'id': 'S09',
    'title': '종목별 최고 종가일',
    'level': 3,
    'tags': ['그룹별 최댓값 행', '윈도 함수', 'ROW_NUMBER', '서브쿼리'],
    'ordered': True,
    'description': '''
<p><code>DAILY_PRICES</code> 테이블에서 <b>2026년 10월</b> 한 달 동안 종목별로 종가(<code>CLOSE_PRICE</code>)가 가장 높았던 날을 조회하려 합니다. 최고 종가를 기록한 날이 여러 날이면 <b>가장 이른 날짜</b> 하나만 출력합니다.</p>
<p>종목 코드(<code>CODE</code>), 거래일(<code>TRADE_DATE</code>), 종가(<code>CLOSE_PRICE</code>)를 조회하는 SQL 문을 작성해 주세요. 10월에 시세가 없는 종목은 출력하지 않으며, 결과는 종목 코드 오름차순으로 정렬해 주세요.</p>
''',
    'explanation': '''
<p>"그룹별로 최댓값을 가진 <b>행 전체</b>"를 구하는 대표 유형입니다. <code>SELECT CODE, TRADE_DATE, MAX(CLOSE_PRICE) ... GROUP BY CODE</code>는 MySQL(ONLY_FULL_GROUP_BY)과 Oracle에서 에러이고, 허용되는 환경에서도 TRADE_DATE가 최댓값 행의 날짜라는 보장이 없습니다.</p>
<ol>
<li><b>윈도 함수</b>: <code>ROW_NUMBER() OVER (PARTITION BY CODE ORDER BY CLOSE_PRICE DESC, TRADE_DATE)</code>로 순번을 매기고 1번만 남깁니다. 동점에서 하나만 남겨야 하므로 <code>RANK()</code>가 아니라 <code>ROW_NUMBER()</code>를 씁니다.</li>
<li><b>서브쿼리</b>: 종목별 최고가를 구해 JOIN한 뒤, 그 안에서 다시 <code>MIN(TRADE_DATE)</code>로 가장 이른 날을 고릅니다.</li>
</ol>
<p>10월 조건은 순번을 매기기 <b>전에</b>(안쪽 쿼리에서) 걸어야 합니다.</p>
''',
}

SCHEMA = [w.DAILY_PRICES]


def sample():
    return {'DAILY_PRICES': [
        ['340010', '2026-10-01', 50000, 100], ['340010', '2026-10-02', 52000, 100], ['340010', '2026-10-05', 51000, 100],
        ['340020', '2026-10-06', 9000, 100], ['340020', '2026-10-01', 9000, 100], ['340020', '2026-10-02', 8000, 100],
        ['340030', '2026-09-30', 70000, 100], ['340030', '2026-10-01', 65000, 100],
        ['340040', '2026-09-29', 1000, 100], ['340010', '2026-11-02', 99000, 100],
    ]}


def hidden(rng):
    codes = ['%06d' % (340100 + k * 7) for k in range(60)]
    rows = w.prices(rng, codes, start='2026-09-14', end='2026-11-13', missing=0.1)
    # 동점 최고가를 늦은 날짜부터 넣는다
    for k, code in enumerate(codes[:12]):
        top = max(r[2] for r in rows if r[0] == code and r[1].startswith('2026-10')) + 100 * (k + 1)
        for d in ['2026-10-29', '2026-10-15', '2026-10-08']:
            rows = [r for r in rows if not (r[0] == code and r[1] == d)]
            rows.append([code, d, top, 1000])
    rows.append(['399999', '2026-09-30', 1000, 1])        # 10월 시세가 없는 종목
    rows.append([codes[20], '2026-11-02', 99999900, 1])    # 11월 최고가는 무시
    rng.shuffle(rows)
    rows.sort(key=lambda r: r[1], reverse=True)            # 늦은 날짜가 먼저 저장되도록
    return {'DAILY_PRICES': rows}


SOLUTION = '''
SELECT CODE, TRADE_DATE, CLOSE_PRICE
FROM (
    SELECT CODE, TRADE_DATE, CLOSE_PRICE,
           ROW_NUMBER() OVER (PARTITION BY CODE ORDER BY CLOSE_PRICE DESC, TRADE_DATE) AS RN
    FROM DAILY_PRICES
    WHERE TRADE_DATE >= '2026-10-01'
      AND TRADE_DATE <= '2026-10-31'
) T
WHERE RN = 1
ORDER BY CODE;
'''

ALT = [
    "SELECT P.CODE, MIN(P.TRADE_DATE) AS TRADE_DATE, P.CLOSE_PRICE FROM DAILY_PRICES P "
    "JOIN (SELECT CODE, MAX(CLOSE_PRICE) AS MX FROM DAILY_PRICES WHERE TRADE_DATE BETWEEN '2026-10-01' AND '2026-10-31' "
    "GROUP BY CODE) M ON P.CODE = M.CODE AND P.CLOSE_PRICE = M.MX "
    "WHERE P.TRADE_DATE BETWEEN '2026-10-01' AND '2026-10-31' GROUP BY P.CODE, P.CLOSE_PRICE ORDER BY P.CODE",
    "SELECT CODE, TRADE_DATE, CLOSE_PRICE FROM (SELECT D.*, ROW_NUMBER() OVER (PARTITION BY CODE "
    "ORDER BY CLOSE_PRICE DESC, TRADE_DATE ASC) RN FROM DAILY_PRICES D WHERE TO_CHAR(TRADE_DATE, 'YYYY-MM') = '2026-10') "
    "WHERE RN = 1 ORDER BY CODE",
]

WRONG = {
    'GROUP BY + MAX에 날짜 그대로': "SELECT CODE, TRADE_DATE, MAX(CLOSE_PRICE) FROM DAILY_PRICES "
                                "WHERE TRADE_DATE BETWEEN '2026-10-01' AND '2026-10-31' GROUP BY CODE ORDER BY CODE",
    'RANK() 사용(동점 여러 행)': SOLUTION.replace('ROW_NUMBER()', 'RANK()').replace(
        'ORDER BY CLOSE_PRICE DESC, TRADE_DATE)', 'ORDER BY CLOSE_PRICE DESC)'),
    '동점 날짜 기준 누락': SOLUTION.replace('ORDER BY CLOSE_PRICE DESC, TRADE_DATE)', 'ORDER BY CLOSE_PRICE DESC)'),
    '10월 조건을 바깥에': "SELECT CODE, TRADE_DATE, CLOSE_PRICE FROM (SELECT CODE, TRADE_DATE, CLOSE_PRICE, "
                     "ROW_NUMBER() OVER (PARTITION BY CODE ORDER BY CLOSE_PRICE DESC, TRADE_DATE) AS RN FROM DAILY_PRICES) T "
                     "WHERE RN = 1 AND TRADE_DATE BETWEEN '2026-10-01' AND '2026-10-31' ORDER BY CODE",
}
