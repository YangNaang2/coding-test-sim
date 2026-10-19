META = {
    'id': 'A15',
    'title': '쿨다운이 있는 매매',
    'level': 3,
    'tags': ['DP', '상태 머신'],
    'params': [{'name': 'prices', 'type': 'int[]'}, {'name': 'fee', 'type': 'int'}],
    'returnType': 'long',
    'description': '''
<p>한 종목의 일별 가격 <code>prices</code>가 주어집니다. 처음에는 주식이 없고 돈은 충분합니다. 매일 아래 셋 중 하나만 할 수 있습니다.</p>
<ul>
<li>주식이 없으면 그날 가격에 <b>1주</b>를 산다.</li>
<li>주식이 있으면 그날 가격에 그 1주를 판다. 팔 때마다 수수료 <code>fee</code>원을 낸다.</li>
<li>아무것도 하지 않는다.</li>
</ul>
<p>한 번에 최대 1주만 가질 수 있습니다. 또 주식을 판 <b>다음 날에는 살 수 없습니다</b>(쿨다운 1일). 마지막 날이 지나면 들고 있는 주식은 가치가 없다고 봅니다.</p>
<p>얻을 수 있는 최대 이익을 return 하도록 solution 함수를 완성해 주세요. 이익을 낼 수 없으면 0을 return 합니다.</p>
''',
    'constraints': [
        'prices의 길이는 1 이상 100,000 이하입니다.',
        'prices의 원소는 1 이상 1,000,000 이하의 정수입니다.',
        'fee는 0 이상 1,000,000 이하의 정수입니다.',
        '답은 32비트 정수 범위를 넘을 수 있습니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b><br>1일에 1원에 사서 6일에 9원에 팔면 이익 8 − 2 = 6입니다. 4일에 8원에 팔면 5인데, 5일이 쿨다운이라 6일에 다시 사도 팔 날이 없습니다. 2일에 팔고(0) 다시 사는 조합도 6보다 작습니다. 최대 이익은 6입니다.</p>
<p><b>입출력 예 #2</b><br>가격이 계속 내려가므로 아무것도 하지 않는 것이 최선입니다.</p>
<p><b>입출력 예 #3</b><br>1일 매수 → 2일 매도(+3) → 3일 쿨다운 → 4일 매수 → 5일 매도(+3). 수수료가 0이므로 6입니다.</p>
''',
    'explanation': '''
<p>하루가 끝났을 때 가능한 상태는 셋입니다.</p>
<ul>
<li><code>hold</code>: 주식을 들고 있음</li>
<li><code>sold</code>: 오늘 팔았음(내일은 쿨다운)</li>
<li><code>rest</code>: 주식이 없고 오늘 팔지도 않았음(내일 살 수 있음)</li>
</ul>
<pre>hold' = max(hold, rest - p)        # 계속 들고 있거나, 살 수 있는 상태에서 오늘 산다
sold' = hold + p - fee              # 들고 있던 것을 오늘 판다
rest' = max(rest, sold)             # 어제 판 날의 다음 날(쿨다운)도 rest가 된다</pre>
<p>초깃값은 <code>hold = -∞, sold = -∞, rest = 0</code>이고, 답은 <code>max(sold, rest)</code>입니다. O(n), 추가 공간 O(1)입니다.</p>
<p>오른 날마다 차익을 더하는 그리디는 수수료와 쿨다운 때문에 틀립니다. 매도일마다 이전 모든 매수일을 보는 DP는 O(n²)이라 시간 초과가 납니다.</p>
''',
    'edgeCases': [
        '판 다음 날에는 살 수 없지만, 판 날 바로 다음 다음 날에는 살 수 있습니다.',
        '수수료는 매도할 때만 한 번 냅니다(매수 때 또 빼면 틀림).',
        '이익을 낼 수 없으면 0입니다.',
        '답은 long이 필요합니다(Java·C++).',
    ],
}

SOLUTION = '''
def solution(prices, fee):
    NEG = float('-inf')
    hold, sold, rest = NEG, NEG, 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p), hold + p - fee, max(rest, sold)
    return int(max(sold, rest, 0))
'''

BRUTE = '''
from functools import lru_cache
def solution(prices, fee):
    n = len(prices)
    @lru_cache(maxsize=None)
    def go(i, state):           # state 0: 살 수 있음, 1: 보유, 2: 쿨다운
        if i == n:
            return 0
        p = prices[i]
        if state == 0:
            return max(go(i + 1, 0), go(i + 1, 1) - p)
        if state == 1:
            return max(go(i + 1, 1), go(i + 1, 2) + p - fee)
        return go(i + 1, 0)
    return go(0, 0)
'''

WRONG = {
    '쿨다운 무시': '''
def solution(prices, fee):
    hold, free = float('-inf'), 0
    for p in prices:
        hold, free = max(hold, free - p), max(free, hold + p - fee)
    return int(free)
''',
    '수수료를 매수·매도 양쪽에 적용': '''
def solution(prices, fee):
    hold, sold, rest = float('-inf'), float('-inf'), 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p - fee), hold + p - fee, max(rest, sold)
    return int(max(sold, rest, 0))
''',
    '매도일마다 모든 매수일 보기 O(n²)': '''
def solution(prices, fee):
    n = len(prices)
    best = [0] * (n + 2)          # best[i]: i일 이전까지 끝낸 최대 이익(i일에 살 수 있음)
    for i in range(n):
        best[i + 1] = max(best[i + 1], best[i])
        for j in range(i + 1, n):
            gain = best[i] + prices[j] - prices[i] - fee
            if gain > best[min(n, j + 2)]:
                best[min(n, j + 2)] = gain
    return max(best)
''',
}


def examples():
    return [
        (([1, 3, 2, 8, 4, 9], 2), 6),
        (([5, 4, 3], 0), 0),
        (([1, 4, 2, 1, 4], 0), 6),
    ]


def handmade():
    return [
        ([7], 0),
        ([1, 2], 0),
        ([1, 2], 1),
        ([1, 1000000], 0),
        ([3, 3, 3, 3], 0),
        ([1, 5, 1, 5, 1, 5], 0),
        ([1, 5, 1, 5, 1, 5], 3),
    ]


def small(rng):
    return ([rng.randint(1, 10) for _ in range(rng.randint(1, 11))], rng.randint(0, 3))


N_SMALL = 7


def large(rng):
    zig = [1 if k % 3 == 0 else 1000000 for k in range(100000)]
    return [
        ([rng.randint(1, 1000000) for _ in range(100000)], 1000),
        (zig, 0),
    ]
