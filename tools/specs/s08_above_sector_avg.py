import _sqlworld as w

META = {
    'id': 'S08',
    'title': '업종 평균보다 비싼 종목',
    'level': 2,
    'tags': ['서브쿼리', '상관 서브쿼리', 'JOIN', 'AVG'],
    'ordered': True,
    'description': '''
<p><code>STOCKS</code>와 <code>DAILY_PRICES</code> 테이블에서, <b>2026년 10월 16일</b> 종가(<code>CLOSE_PRICE</code>)가 <b>같은 업종 종목들의 그날 평균 종가보다 높은</b> 종목을 조회하려 합니다. 업종이 NULL인 종목은 제외하고, 그날 시세가 없는 종목은 평균 계산과 결과에서 모두 제외합니다.</p>
<p>업종(<code>SECTOR</code>), 종목 코드(<code>CODE</code>), 종목명(<code>NAME</code>), 종가(<code>CLOSE_PRICE</code>)를 조회하는 SQL 문을 작성해 주세요. 결과는 업종 오름차순, 종가 내림차순, 종목 코드 오름차순으로 정렬해 주세요.</p>
''',
    'explanation': '''
<p>업종별 평균은 그룹마다 다르므로 두 가지 방법이 있습니다.</p>
<ol>
<li><b>상관 서브쿼리</b>: 바깥 행의 업종을 서브쿼리 안에서 참조합니다. <code>P.CLOSE_PRICE &gt; (SELECT AVG(...) ... WHERE S2.SECTOR = S.SECTOR AND P2.TRADE_DATE = '2026-10-16')</code></li>
<li><b>인라인 뷰 JOIN</b>: 업종별 평균을 GROUP BY로 먼저 구해 FROM 절에서 JOIN합니다.</li>
</ol>
<p>서브쿼리에도 날짜 조건을 넣어야 합니다. 빠뜨리면 모든 날짜의 평균과 비교하게 됩니다. "높은"은 <code>&gt;</code>이며, 종가가 평균과 같은 종목은 제외합니다.</p>
''',
}

SCHEMA = [w.STOCKS, w.DAILY_PRICES]


def sample():
    return {
        'STOCKS': [
            ['330010', '한빛소프트', 'KOSDAQ', 'IT', '2021-04-01'],
            ['330020', '가람전자', 'KOSPI', 'IT', '2011-03-31'],
            ['330030', '다온테크', 'KOSDAQ', 'IT', '2015-08-20'],
            ['330040', '누리바이오', 'KOSDAQ', 'BIO', '2019-07-01'],
            ['330050', '새솔제약', 'KOSPI', 'BIO', '2009-09-09'],
            ['330060', '하늘산업', 'KOSPI', None, '2000-01-03'],
        ],
        'DAILY_PRICES': [
            ['330010', '2026-10-16', 30000, 1000], ['330020', '2026-10-16', 60000, 2000], ['330030', '2026-10-16', 45000, 500],
            ['330040', '2026-10-16', 20000, 800], ['330050', '2026-10-16', 20000, 900], ['330060', '2026-10-16', 999000, 10],
            ['330010', '2026-10-15', 90000, 1000], ['330040', '2026-10-15', 1000, 1000],
        ],
    }


def hidden(rng):
    stocks = w.stocks(rng, 120)
    prices = w.prices(rng, [s[0] for s in stocks], start='2026-10-12', end='2026-10-20', missing=0.15)
    # 평균과 정확히 같은 종목이 생기도록 3종목짜리 업종을 하나 만든다
    for k, p in enumerate([100000, 200000, 300000]):
        code = '99%04d' % k
        stocks.append([code, '평균테크%d' % k, 'KOSPI', 'AUTO', '2020-01-01'])
        prices.append([code, '2026-10-16', p, 1000])
    rng.shuffle(prices)
    return {'STOCKS': stocks, 'DAILY_PRICES': prices}


SOLUTION = '''
SELECT S.SECTOR, S.CODE, S.NAME, P.CLOSE_PRICE
FROM STOCKS S
JOIN DAILY_PRICES P ON S.CODE = P.CODE
WHERE P.TRADE_DATE = '2026-10-16'
  AND S.SECTOR IS NOT NULL
  AND P.CLOSE_PRICE > (
      SELECT AVG(P2.CLOSE_PRICE)
      FROM STOCKS S2
      JOIN DAILY_PRICES P2 ON S2.CODE = P2.CODE
      WHERE P2.TRADE_DATE = '2026-10-16'
        AND S2.SECTOR = S.SECTOR
  )
ORDER BY S.SECTOR, P.CLOSE_PRICE DESC, S.CODE;
'''

ALT = [
    "SELECT S.SECTOR, S.CODE, S.NAME, P.CLOSE_PRICE FROM STOCKS S JOIN DAILY_PRICES P ON S.CODE = P.CODE "
    "JOIN (SELECT S2.SECTOR, AVG(P2.CLOSE_PRICE) AS AVG_PRICE FROM STOCKS S2 JOIN DAILY_PRICES P2 ON S2.CODE = P2.CODE "
    "WHERE P2.TRADE_DATE = '2026-10-16' GROUP BY S2.SECTOR) G ON S.SECTOR = G.SECTOR "
    "WHERE P.TRADE_DATE = '2026-10-16' AND P.CLOSE_PRICE > G.AVG_PRICE ORDER BY 1, 4 DESC, 2",
    "WITH T AS (SELECT S.SECTOR, S.CODE, S.NAME, P.CLOSE_PRICE, AVG(P.CLOSE_PRICE) OVER (PARTITION BY S.SECTOR) AS A "
    "FROM STOCKS S JOIN DAILY_PRICES P ON S.CODE = P.CODE WHERE P.TRADE_DATE = '2026-10-16' AND S.SECTOR IS NOT NULL) "
    "SELECT SECTOR, CODE, NAME, CLOSE_PRICE FROM T WHERE CLOSE_PRICE > A ORDER BY SECTOR, CLOSE_PRICE DESC, CODE",
]

WRONG = {
    '서브쿼리 날짜 조건 누락': SOLUTION.replace("      WHERE P2.TRADE_DATE = '2026-10-16'\n        AND S2.SECTOR = S.SECTOR",
                                       "      WHERE S2.SECTOR = S.SECTOR"),
    '전체 평균과 비교': SOLUTION.replace('\n        AND S2.SECTOR = S.SECTOR', ''),
    '평균 이상(>=)': SOLUTION.replace('P.CLOSE_PRICE > (', 'P.CLOSE_PRICE >= ('),
}
