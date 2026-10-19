META = {
    'id': 'A08',
    'title': '두 업종 분산 투자',
    'level': 2,
    'tags': ['해시', '이분 탐색', '완전 탐색', '구현', '후기 유형: 해시+이분탐색+완전탐색+구현'],
    'params': [{'name': 'stocks', 'type': 'string[]'}, {'name': 'budget', 'type': 'int'}],
    'returnType': 'int',
    'description': '''
<p>예산 <code>budget</code>원으로 <b>서로 다른 업종</b>의 두 종목을 한 주씩 사려고 합니다. 두 종목 가격의 합은 예산 이하여야 하고, 그중 합이 가장 큰 경우를 찾으려 합니다.</p>
<p>시세 피드 <code>stocks</code>의 각 원소는 <code>"종목코드 업종 가격"</code> 형식이며, 들어온 순서대로 적용됩니다. <b>같은 종목코드가 다시 나오면 그 종목의 업종과 가격을 새 값으로 바꿉니다.</b> 모든 피드를 적용한 뒤의 종목들만 살 수 있습니다.</p>
<p>살 수 있는 두 종목 가격 합의 최댓값을 return 하도록 solution 함수를 완성해 주세요. 조건에 맞는 두 종목이 없으면 -1을 return 합니다.</p>
''',
    'constraints': [
        'stocks의 길이는 2 이상 100,000 이하입니다.',
        '종목코드는 영어 대문자와 숫자로 이루어진 길이 1 이상 6 이하의 문자열입니다.',
        '업종은 영어 대문자로 이루어진 길이 1 이상 6 이하의 문자열이며, 서로 다른 업종은 10개 이하입니다.',
        '가격은 1 이상 1,000,000,000 이하의 정수입니다.',
        'budget은 1 이상 2,000,000,000 이하의 정수입니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b><br>서로 다른 업종 조합 중 A02(45,000) + B01(50,000) = 95,000은 예산을 넘습니다. A01(30,000) + B01(50,000) = 80,000이 예산과 같아 최댓값입니다.</p>
<p><b>입출력 예 #2</b><br>모두 IT 업종이라 고를 수 없습니다.</p>
<p><b>입출력 예 #3</b><br>세 번째 피드로 K1이 BIO 업종, 100원으로 바뀝니다. 남은 종목 K1(BIO)과 K2(BIO)는 업종이 같아 -1입니다.</p>
''',
    'explanation': '''
<ol>
<li><b>해시</b>: dict[종목코드] = (업종, 가격)으로 피드를 적용해 최신 상태만 남깁니다.</li>
<li>업종별 가격 리스트를 만들어 정렬합니다.</li>
<li><b>완전 탐색</b>: 업종이 10개 이하이므로 업종 쌍(최대 45개)을 모두 봅니다.</li>
<li><b>이분 탐색</b>: 쌍 (A, B)마다 작은 쪽 업종의 가격 x를 하나씩 보면서, 큰 쪽 리스트에서 <code>budget − x</code> 이하인 가장 큰 값을 <code>bisect_right</code>로 찾습니다.</li>
</ol>
<p>각 종목은 최대 9개 쌍에서 쓰이므로 O(9 n log n)입니다. 모든 두 종목을 비교하는 O(n²)은 n = 100,000에서 시간 초과입니다.</p>
''',
    'edgeCases': [
        '같은 종목코드가 다시 나오면 업종도 바뀔 수 있습니다. 피드를 그대로 종목 목록으로 쓰면 틀립니다.',
        '가격 합이 예산과 정확히 같아도 됩니다.',
        '같은 업종 두 종목은 고를 수 없습니다.',
        '최종 종목이 1개뿐이거나 업종이 1개뿐이면 -1입니다.',
    ],
}

SOLUTION = '''
from bisect import bisect_right

def solution(stocks, budget):
    latest = {}
    for line in stocks:
        code, sector, price = line.split()
        latest[code] = (sector, int(price))

    by_sector = {}
    for sector, price in latest.values():
        by_sector.setdefault(sector, []).append(price)
    for prices in by_sector.values():
        prices.sort()

    sectors = list(by_sector)
    best = -1
    for i in range(len(sectors)):
        for j in range(i + 1, len(sectors)):
            a, b = by_sector[sectors[i]], by_sector[sectors[j]]
            if len(a) > len(b):
                a, b = b, a
            for x in a:
                k = bisect_right(b, budget - x)
                if k > 0:
                    best = max(best, x + b[k - 1])
    return best
'''

BRUTE = '''
def solution(stocks, budget):
    latest = {}
    for l in stocks:
        c, s, p = l.split()
        latest[c] = (s, int(p))
    items = list(latest.values())
    best = -1
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i][0] != items[j][0] and items[i][1] + items[j][1] <= budget:
                best = max(best, items[i][1] + items[j][1])
    return best
'''

WRONG = {
    '시세 갱신 무시': '''
from bisect import bisect_right
def solution(stocks, budget):
    by = {}
    for l in stocks:
        c, s, p = l.split()
        by.setdefault(s, []).append(int(p))
    for v in by.values():
        v.sort()
    ks, best = list(by), -1
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            for x in by[ks[i]]:
                k = bisect_right(by[ks[j]], budget - x)
                if k:
                    best = max(best, x + by[ks[j]][k - 1])
    return best
''',
    '예산 미만만 허용': '''
from bisect import bisect_left
def solution(stocks, budget):
    latest = {}
    for l in stocks:
        c, s, p = l.split()
        latest[c] = (s, int(p))
    by = {}
    for s, p in latest.values():
        by.setdefault(s, []).append(p)
    for v in by.values():
        v.sort()
    ks, best = list(by), -1
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            for x in by[ks[i]]:
                k = bisect_left(by[ks[j]], budget - x)
                if k:
                    best = max(best, x + by[ks[j]][k - 1])
    return best
''',
    '모든 쌍 비교 O(n²)': BRUTE,
}


def examples():
    return [
        ((["A01 IT 30000", "A02 IT 45000", "B01 BIO 50000", "C01 FIN 20000"], 80000), 80000),
        ((["X1 IT 10", "X2 IT 20", "X3 IT 30"], 100), -1),
        ((["K1 IT 500", "K2 BIO 300", "K1 BIO 100"], 700), -1),
    ]


def handmade():
    return [
        (["A IT 5", "B BIO 5"], 10),
        (["A IT 5", "B BIO 6"], 10),
        (["A IT 1000000000", "B FIN 1000000000"], 2000000000),
        (["A IT 1", "A BIO 2", "B BIO 3", "B IT 4"], 100),          # 갱신 후 A(BIO 2), B(IT 4)
        (["S1 X 1", "S2 X 2", "S3 Y 100", "S4 Z 3"], 5),            # X+Z
    ]


def small(rng):
    codes = ['C%d' % k for k in range(8)]
    secs = ['IT', 'BIO', 'FIN']
    feed = ['%s %s %d' % (rng.choice(codes), rng.choice(secs), rng.randint(1, 40)) for _ in range(rng.randint(2, 12))]
    return (feed, rng.randint(1, 80))


N_SMALL = 8


def large(rng):
    secs = ['S%d' % k for k in range(10)]
    feed = ['%06d %s %d' % (k, rng.choice(secs), rng.randint(1, 1000000000)) for k in range(100000)]
    feed2 = ['%d %s %d' % (rng.randint(0, 60000), rng.choice(secs[:2]), rng.randint(1, 1000000)) for _ in range(100000)]
    return [(feed, 1234567890), (feed2, 1000001)]
