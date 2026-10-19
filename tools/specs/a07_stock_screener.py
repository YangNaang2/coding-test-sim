META = {
    'id': 'A07',
    'title': '조건 검색기',
    'level': 2,
    'tags': ['해시', '이분 탐색', '완전 탐색', '문자열', '후기 유형: 해시+이분탐색+완전탐색+구현'],
    'params': [{'name': 'info', 'type': 'string[]'}, {'name': 'queries', 'type': 'string[]'}],
    'returnType': 'int[]',
    'description': '''
<p>HTS의 조건 검색 기능을 만들려고 합니다. 종목 정보 <code>info</code>의 각 원소는 <code>"시장 업종 구분 가격"</code> 형식입니다.</p>
<ul>
<li>시장: <code>KOSPI</code> 또는 <code>KOSDAQ</code></li>
<li>업종: <code>IT</code>, <code>BIO</code>, <code>FIN</code>, <code>AUTO</code>, <code>CHEM</code> 중 하나</li>
<li>구분: 보통주 <code>C</code> 또는 우선주 <code>P</code></li>
<li>가격: 정수</li>
</ul>
<p>검색 조건 <code>queries</code>의 각 원소는 <code>"시장 업종 구분 최소가격 최대가격"</code> 형식입니다. 시장·업종·구분 자리에 <code>-</code>가 오면 그 항목은 조건을 따지지 않습니다. 가격은 <b>최소가격 이상 최대가격 이하</b>인 종목만 고릅니다.</p>
<p>각 검색 조건에 맞는 종목 수를 차례로 담은 배열을 return 하도록 solution 함수를 완성해 주세요.</p>
''',
    'constraints': [
        'info의 길이는 1 이상 50,000 이하입니다.',
        'queries의 길이는 1 이상 100,000 이하입니다.',
        '가격, 최소가격, 최대가격은 1 이상 10,000,000 이하의 정수입니다.',
        '최소가격이 최대가격보다 클 수도 있습니다. 이때 조건에 맞는 종목은 없습니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b></p>
<ul>
<li>"KOSPI - C 50000 52000": KOSPI 보통주 중 가격이 50,000~52,000인 종목은 IT 52,000과 FIN 52,000으로 2개입니다.</li>
<li>"- IT - 10000 100000": IT 종목 중 가격이 범위에 드는 것은 52,000과 41,000으로 2개입니다(9,800은 범위 밖).</li>
<li>"KOSDAQ - - 1 9800": 9,800 하나입니다. 최대가격과 같은 가격도 포함합니다.</li>
<li>"- - - 52001 1000000": 52,001 이상인 종목은 없습니다.</li>
<li>"- - - 60000 50000": 최소가격이 최대가격보다 커서 0입니다.</li>
</ul>
''',
    'explanation': '''
<p>검색마다 모든 종목을 훑으면 O(info × queries) = 최대 50억 번이라 시간 초과가 납니다. 미리 정리해 두고 검색을 빠르게 만듭니다.</p>
<ol>
<li><b>완전 탐색으로 키 만들기</b>: 종목 하나는 (시장, 업종, 구분) 각각을 "그대로" 또는 "-"로 바꾼 2³ = 8개의 검색 키에 해당합니다. 8개 키 모두에 가격을 넣습니다.</li>
<li><b>해시</b>: dict[키] = 가격 리스트로 모은 뒤 리스트를 정렬합니다.</li>
<li><b>이분 탐색</b>: 검색 조건의 키로 리스트를 찾고, <code>bisect_right(최대) − bisect_left(최소)</code>로 범위 안 개수를 셉니다.</li>
</ol>
<p>전처리 O(8n log n), 검색 하나에 O(log n)입니다.</p>
''',
    'edgeCases': [
        '최소·최대 모두 포함입니다. bisect_left/bisect_right를 바꿔 쓰면 경계 가격이 빠지거나 더해집니다.',
        '최소가격 &gt; 최대가격이면 0입니다. 그냥 빼면 음수가 나올 수 있습니다.',
        '검색 키에 해당하는 종목이 하나도 없으면 dict에 키가 없습니다.',
        '같은 가격 종목이 여러 개 있을 수 있습니다.',
    ],
}

SOLUTION = '''
from bisect import bisect_left, bisect_right
from itertools import product

def solution(info, queries):
    table = {}
    for line in info:
        market, sector, kind, price = line.split()
        price = int(price)
        for key in product((market, '-'), (sector, '-'), (kind, '-')):
            table.setdefault(key, []).append(price)
    for prices in table.values():
        prices.sort()

    answer = []
    for q in queries:
        market, sector, kind, lo, hi = q.split()
        lo, hi = int(lo), int(hi)
        prices = table.get((market, sector, kind), [])
        if lo > hi:
            answer.append(0)
        else:
            answer.append(bisect_right(prices, hi) - bisect_left(prices, lo))
    return answer
'''

BRUTE = '''
def solution(info, queries):
    rows = [l.split() for l in info]
    out = []
    for q in queries:
        m, s, k, lo, hi = q.split()
        lo, hi = int(lo), int(hi)
        out.append(sum(1 for a, b, c, p in rows
                       if m in ('-', a) and s in ('-', b) and k in ('-', c) and lo <= int(p) <= hi))
    return out
'''

WRONG = {
    '최대가격 미포함': '''
from bisect import bisect_left
from itertools import product
def solution(info, queries):
    t = {}
    for l in info:
        a, b, c, p = l.split()
        for key in product((a, '-'), (b, '-'), (c, '-')):
            t.setdefault(key, []).append(int(p))
    for v in t.values():
        v.sort()
    out = []
    for q in queries:
        a, b, c, lo, hi = q.split()
        v = t.get((a, b, c), [])
        out.append(max(0, bisect_left(v, int(hi)) - bisect_left(v, int(lo))))
    return out
''',
    '최소 > 최대 처리 누락': '''
from bisect import bisect_left, bisect_right
from itertools import product
def solution(info, queries):
    t = {}
    for l in info:
        a, b, c, p = l.split()
        for key in product((a, '-'), (b, '-'), (c, '-')):
            t.setdefault(key, []).append(int(p))
    for v in t.values():
        v.sort()
    out = []
    for q in queries:
        a, b, c, lo, hi = q.split()
        v = t.get((a, b, c), [])
        out.append(bisect_right(v, int(hi)) - bisect_left(v, int(lo)))
    return out
''',
    '검색마다 전체 훑기 O(nq)': BRUTE,
}

MARKETS = ['KOSPI', 'KOSDAQ']
SECTORS = ['IT', 'BIO', 'FIN', 'AUTO', 'CHEM']
KINDS = ['C', 'P']


def examples():
    info = ["KOSPI IT C 52000", "KOSPI IT P 41000", "KOSDAQ BIO C 15000", "KOSPI FIN C 52000", "KOSDAQ IT C 9800"]
    queries = ["KOSPI - C 50000 52000", "- IT - 10000 100000", "KOSDAQ - - 1 9800", "- - - 52001 1000000",
               "- - - 60000 50000"]
    return [((info, queries), [2, 2, 1, 0, 0])]


def handmade():
    one = ["KOSPI AUTO P 100"]
    return [
        (one, ["KOSPI AUTO P 100 100", "KOSPI AUTO C 1 1000", "- - - 101 200", "- - - 1 99", "KOSDAQ - - 1 10000000"]),
        (["KOSDAQ CHEM C 7"] * 5 + ["KOSDAQ CHEM P 7"], ["- CHEM - 7 7", "- - C 8 7", "- - P 1 7", "KOSPI - - 1 7"]),
        (["KOSPI IT C %d" % p for p in (1, 10000000)], ["- - - 1 10000000", "- - - 2 9999999", "KOSPI IT C 10000000 10000000"]),
    ]


def rand_info(rng, n, pmax):
    return ['%s %s %s %d' % (rng.choice(MARKETS), rng.choice(SECTORS), rng.choice(KINDS), rng.randint(1, pmax))
            for _ in range(n)]


def rand_query(rng, pmax):
    a = rng.choice(MARKETS + ['-'])
    b = rng.choice(SECTORS + ['-'])
    c = rng.choice(KINDS + ['-'])
    lo, hi = rng.randint(1, pmax), rng.randint(1, pmax)
    if rng.random() < 0.8:
        lo, hi = min(lo, hi), max(lo, hi)
    return '%s %s %s %d %d' % (a, b, c, lo, hi)


def small(rng):
    return (rand_info(rng, rng.randint(1, 12), 30), [rand_query(rng, 30) for _ in range(rng.randint(1, 8))])


N_SMALL = 9


def large(rng):
    return [
        (rand_info(rng, 50000, 10000000), [rand_query(rng, 10000000) for _ in range(100000)]),
        (rand_info(rng, 50000, 100), [rand_query(rng, 100) for _ in range(100000)]),
    ]
