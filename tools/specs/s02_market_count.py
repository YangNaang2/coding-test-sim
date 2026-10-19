import _sqlworld as w

META = {
    'id': 'S02',
    'title': '시장별 종목 수',
    'level': 1,
    'tags': ['GROUP BY', 'COUNT', 'NULL'],
    'ordered': True,
    'description': '''
<p><code>STOCKS</code> 테이블에서 시장별로 전체 종목 수와, 그중 업종이 아직 분류되지 않은(<code>SECTOR</code>가 NULL인) 종목 수를 구하려 합니다.</p>
<p>시장(<code>MARKET</code>), 전체 종목 수(<code>STOCK_COUNT</code>), 미분류 종목 수(<code>NO_SECTOR_COUNT</code>)를 조회하는 SQL 문을 작성해 주세요. 결과는 전체 종목 수 내림차순으로, 같으면 시장 이름 오름차순으로 정렬해 주세요.</p>
''',
    'explanation': '''
<ul>
<li><code>COUNT(*)</code>는 모든 행을, <code>COUNT(컬럼)</code>은 그 컬럼이 NULL이 아닌 행만 셉니다. 그래서 미분류 종목 수는 <code>COUNT(*) - COUNT(SECTOR)</code>입니다.</li>
<li><code>SUM(CASE WHEN SECTOR IS NULL THEN 1 ELSE 0 END)</code>로도 셀 수 있습니다. <code>SECTOR = NULL</code>은 항상 참이 아니므로(UNKNOWN) 0이 나옵니다.</li>
<li>ORDER BY에서는 SELECT의 별칭(<code>STOCK_COUNT</code>)을 쓸 수 있습니다.</li>
</ul>
''',
}

SCHEMA = [w.STOCKS]


def sample():
    return {'STOCKS': [
        ['320010', '한빛소프트', 'KOSDAQ', 'IT', '2021-04-01'],
        ['320020', '누리바이오', 'KOSDAQ', None, '2024-02-15'],
        ['320030', '다온증권', 'KOSPI', 'FIN', '2010-03-31'],
        ['320040', '가람모터스', 'KOSPI', 'AUTO', '2015-08-20'],
        ['320050', '하늘산업', 'KOSDAQ', None, '2025-06-10'],
        ['320060', '바른화학', 'KOSPI', None, '2019-07-01'],
    ]}


def hidden(rng):
    rows = w.stocks(rng, 300)
    kospi = sum(1 for r in rows if r[2] == 'KOSPI')
    kosdaq = len(rows) - kospi
    # 두 시장의 종목 수를 같게 맞춰 동점 정렬을 확인한다
    for k in range(abs(kospi - kosdaq)):
        rows.append(['9%05d' % k, '보정산업%d' % k, 'KOSDAQ' if kospi > kosdaq else 'KOSPI', None, '2026-01-02'])
    rng.shuffle(rows)
    return {'STOCKS': rows}


SOLUTION = '''
SELECT MARKET,
       COUNT(*) AS STOCK_COUNT,
       COUNT(*) - COUNT(SECTOR) AS NO_SECTOR_COUNT
FROM STOCKS
GROUP BY MARKET
ORDER BY STOCK_COUNT DESC, MARKET;
'''

ALT = [
    "SELECT MARKET, COUNT(*) AS STOCK_COUNT, SUM(CASE WHEN SECTOR IS NULL THEN 1 ELSE 0 END) AS NO_SECTOR_COUNT "
    "FROM STOCKS GROUP BY MARKET ORDER BY COUNT(*) DESC, MARKET ASC",
    "SELECT MARKET, COUNT(*) STOCK_COUNT, SUM(NVL2(SECTOR, 0, 1)) NO_SECTOR_COUNT FROM STOCKS GROUP BY MARKET "
    "ORDER BY 2 DESC, 1",
]

WRONG = {
    'COUNT(SECTOR)로 전체 수': "SELECT MARKET, COUNT(SECTOR), COUNT(*) - COUNT(SECTOR) FROM STOCKS GROUP BY MARKET "
                           "ORDER BY 2 DESC, 1",
    'SECTOR = NULL 비교': "SELECT MARKET, COUNT(*), SUM(CASE WHEN SECTOR = NULL THEN 1 ELSE 0 END) FROM STOCKS "
                        "GROUP BY MARKET ORDER BY 2 DESC, 1",
    '동점 정렬 누락(시장 내림차순)': "SELECT MARKET, COUNT(*), COUNT(*) - COUNT(SECTOR) FROM STOCKS GROUP BY MARKET "
                         "ORDER BY 2 DESC, 1 DESC",
}
