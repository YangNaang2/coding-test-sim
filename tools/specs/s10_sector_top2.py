import _sqlworld as w

META = {
    'id': 'S10',
    'title': '업종별 거래대금 TOP 2',
    'level': 3,
    'tags': ['윈도 함수', 'ROW_NUMBER', 'WITH(CTE)', '순위'],
    'ordered': True,
    'description': '''
<p><code>STOCKS</code>와 <code>DAILY_PRICES</code> 테이블에서, <b>2026년 10월</b> 종목별 거래대금 합계를 구하고 <b>업종별 상위 2개 종목</b>을 조회하려 합니다.</p>
<ul>
<li>거래대금은 하루마다 <code>CLOSE_PRICE × VOLUME</code>이며, 종목별로 10월의 거래대금을 모두 더합니다.</li>
<li>업종 안에서 합계가 큰 순서로 순위를 매기고, 합계가 같으면 종목 코드가 작은 종목이 앞 순위입니다. 순위는 1부터 빈틈없이 매깁니다.</li>
<li>업종이 NULL인 종목과 10월 시세가 없는 종목은 제외합니다. 종목이 1개뿐인 업종은 1개만 출력합니다.</li>
</ul>
<p>업종(<code>SECTOR</code>), 종목 코드(<code>CODE</code>), 종목명(<code>NAME</code>), 거래대금 합계(<code>TOTAL_VALUE</code>), 순위(<code>RANK_NO</code>)를 조회하는 SQL 문을 작성해 주세요. 결과는 업종 오름차순, 순위 오름차순으로 정렬해 주세요.</p>
''',
    'explanation': '''
<ol>
<li>WITH 절(CTE)에서 종목별 10월 거래대금 합계를 GROUP BY로 구합니다.</li>
<li><code>ROW_NUMBER() OVER (PARTITION BY SECTOR ORDER BY TOTAL_VALUE DESC, CODE)</code>로 업종 안 순위를 매깁니다.</li>
<li>바깥 쿼리에서 <code>RANK_NO &lt;= 2</code>로 거릅니다. 윈도 함수 결과는 같은 SELECT의 WHERE에서 쓸 수 없으므로 한 단계 감싸야 합니다.</li>
</ol>
<p><code>RANK()</code>는 동점이면 같은 순위를 주므로 3개 이상 나올 수 있습니다. "동점이면 코드 순"처럼 순위가 겹치지 않는다면 <code>ROW_NUMBER()</code>입니다. <code>SUM(CLOSE_PRICE) * SUM(VOLUME)</code>은 하루 단위 곱의 합이 아닙니다. MySQL 8에서 RANK는 예약어라 별칭으로 쓰면 에러가 납니다.</p>
''',
}

SCHEMA = [w.STOCKS, w.DAILY_PRICES]


def sample():
    return {
        'STOCKS': [
            ['350010', '한빛소프트', 'KOSDAQ', 'IT', '2021-04-01'],
            ['350020', '가람전자', 'KOSPI', 'IT', '2011-03-31'],
            ['350030', '다온테크', 'KOSDAQ', 'IT', '2015-08-20'],
            ['350040', '누리바이오', 'KOSDAQ', 'BIO', '2019-07-01'],
            ['350050', '하늘산업', 'KOSPI', None, '2000-01-03'],
        ],
        'DAILY_PRICES': [
            ['350010', '2026-10-01', 1000, 300], ['350010', '2026-10-02', 2000, 100],
            ['350020', '2026-10-01', 500, 1000],
            ['350030', '2026-10-01', 100, 2000], ['350030', '2026-10-02', 300, 1000], ['350030', '2026-09-30', 9000, 9000],
            ['350040', '2026-10-05', 700, 700], ['350050', '2026-10-05', 99999, 99999],
        ],
    }


def hidden(rng):
    stocks = w.stocks(rng, 90)
    prices = w.prices(rng, [s[0] for s in stocks], start='2026-09-21', end='2026-11-06', missing=0.1)
    # 같은 업종에 거래대금 합계가 같은 종목 세 개를 코드 내림차순으로 넣는다
    for k, code in enumerate(['998003', '998002', '998001']):
        stocks.append([code, '동점케미칼%d' % k, 'KOSPI', 'CHEM', '2020-01-01'])
        prices.append([code, '2026-10-14', 10 ** 7, 10 ** 6])
    stocks.append(['997001', '홀로헬스', 'KOSDAQ', 'BIO', '2020-01-01'])
    stocks = [s if s[3] != 'BIO' or s[0] == '997001' else s[:3] + ['FIN'] + s[4:] for s in stocks]
    prices.append(['997001', '2026-10-14', 100, 1])
    stocks.append(['997002', '시세없음', 'KOSDAQ', 'AUTO', '2020-01-01'])
    rng.shuffle(stocks)
    rng.shuffle(prices)
    return {'STOCKS': stocks, 'DAILY_PRICES': prices}


SOLUTION = '''
WITH T AS (
    SELECT S.SECTOR, S.CODE, S.NAME, SUM(P.CLOSE_PRICE * P.VOLUME) AS TOTAL_VALUE
    FROM STOCKS S
    JOIN DAILY_PRICES P ON S.CODE = P.CODE
    WHERE P.TRADE_DATE BETWEEN '2026-10-01' AND '2026-10-31'
      AND S.SECTOR IS NOT NULL
    GROUP BY S.SECTOR, S.CODE, S.NAME
), R AS (
    SELECT SECTOR, CODE, NAME, TOTAL_VALUE,
           ROW_NUMBER() OVER (PARTITION BY SECTOR ORDER BY TOTAL_VALUE DESC, CODE) AS RANK_NO
    FROM T
)
SELECT SECTOR, CODE, NAME, TOTAL_VALUE, RANK_NO
FROM R
WHERE RANK_NO <= 2
ORDER BY SECTOR, RANK_NO;
'''

ALT = [
    "SELECT SECTOR, CODE, NAME, TOTAL_VALUE, RANK_NO FROM (SELECT S.SECTOR, S.CODE, S.NAME, "
    "SUM(P.CLOSE_PRICE * P.VOLUME) AS TOTAL_VALUE, ROW_NUMBER() OVER (PARTITION BY S.SECTOR "
    "ORDER BY SUM(P.CLOSE_PRICE * P.VOLUME) DESC, S.CODE) AS RANK_NO FROM STOCKS S JOIN DAILY_PRICES P ON S.CODE = P.CODE "
    "WHERE DATE_FORMAT(P.TRADE_DATE, '%Y-%m') = '2026-10' AND S.SECTOR IS NOT NULL GROUP BY S.SECTOR, S.CODE, S.NAME) X "
    "WHERE RANK_NO <= 2 ORDER BY SECTOR, RANK_NO",
]

WRONG = {
    'RANK() 사용': SOLUTION.replace('ROW_NUMBER() OVER (PARTITION BY SECTOR ORDER BY TOTAL_VALUE DESC, CODE)',
                                  'RANK() OVER (PARTITION BY SECTOR ORDER BY TOTAL_VALUE DESC)'),
    'SUM(종가) * SUM(거래량)': SOLUTION.replace('SUM(P.CLOSE_PRICE * P.VOLUME)', 'SUM(P.CLOSE_PRICE) * SUM(P.VOLUME)'),
    '10월 조건 누락': SOLUTION.replace("    WHERE P.TRADE_DATE BETWEEN '2026-10-01' AND '2026-10-31'\n      AND S.SECTOR IS NOT NULL",
                                  '    WHERE S.SECTOR IS NOT NULL'),
}
