META = {
    'id': 'A03',
    'title': '최장 상승 구간',
    'level': 1,
    'tags': ['구현', '배열'],
    'params': [{'name': 'prices', 'type': 'int[]'}],
    'returnType': 'int[]',
    'description': '''
<p>어떤 종목의 일별 종가 <code>prices</code>가 주어집니다. <code>prices[i]</code>는 (i + 1)일째의 종가입니다. 종가가 0인 날은 <b>거래 정지일</b>입니다.</p>
<p>연속한 날들의 종가가 <b>매일 직전 날보다 엄격하게 커지는</b> 구간을 상승 구간이라고 합니다. 하루짜리 구간도 상승 구간입니다. 단, 거래 정지일은 어떤 상승 구간에도 포함될 수 없습니다. 종가가 직전 날과 같으면 상승이 끊깁니다.</p>
<p>가장 긴 상승 구간의 <code>[시작일, 길이]</code>를 return 하도록 solution 함수를 완성해 주세요. 시작일은 1부터 셉니다. 가장 긴 구간이 여러 개면 시작일이 가장 빠른 구간을 고릅니다. 모든 날이 거래 정지일이면 <code>[0, 0]</code>을 return 합니다.</p>
''',
    'constraints': [
        'prices의 길이는 1 이상 200,000 이하입니다.',
        'prices의 원소는 0 이상 1,000,000 이하의 정수입니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b><br>1~3일(100, 101, 103)은 길이 3, 4~7일(102, 104, 105, 106)은 길이 4입니다. 따라서 [4, 4]입니다.</p>
<p><b>입출력 예 #2</b><br>1일과 2일은 종가가 같아서 각각 길이 1입니다. 3일과 6일은 거래 정지일입니다. 4~5일(3, 4)과 7~8일(1, 2)이 길이 2로 가장 긴데, 시작일이 빠른 [4, 2]를 return 합니다.</p>
<p><b>입출력 예 #3</b><br>모든 날이 거래 정지일입니다.</p>
''',
    'explanation': '''
<p>배열을 한 번 훑으면서 현재 상승 구간의 시작일과 길이를 들고 다닙니다.</p>
<ul>
<li>오늘 종가가 0이면 현재 구간을 끊습니다(길이 0).</li>
<li>현재 구간이 있고 오늘 종가가 어제보다 크면 길이를 1 늘리고, 아니면 오늘부터 새 구간(길이 1)을 시작합니다.</li>
<li>현재 길이가 최댓값보다 <b>클 때만</b> 답을 갱신해야 시작일이 가장 빠른 구간이 남습니다.</li>
</ul>
<p>O(n)입니다. 시작점마다 끝까지 늘려 보는 풀이는 가격이 계속 오르는 입력에서 O(n²)이 되어 시간 초과가 납니다.</p>
''',
    'edgeCases': [
        '같은 가격은 상승이 아닙니다(≥로 비교하면 틀림).',
        '거래 정지일 직후의 날은 새 구간의 시작입니다. 0에서 양수로 오른 것을 상승으로 세면 안 됩니다.',
        '길이가 같으면 먼저 나온 구간을 유지해야 합니다(≥로 갱신하면 틀림).',
        '모든 날이 0이면 [0, 0]입니다.',
    ],
}

SOLUTION = '''
def solution(prices):
    best_start, best_len = 0, 0
    start, length = 0, 0
    for i, p in enumerate(prices):
        if p == 0:
            length = 0
            continue
        if length > 0 and p > prices[i - 1]:
            length += 1
        else:
            start, length = i + 1, 1
        if length > best_len:
            best_start, best_len = start, length
    return [best_start, best_len]
'''

BRUTE = '''
def solution(prices):
    n = len(prices)
    best = [0, 0]
    for s in range(n):
        for e in range(s, n):
            seg = prices[s:e + 1]
            if 0 in seg:
                break
            if any(seg[k] <= seg[k - 1] for k in range(1, len(seg))):
                break
            if e - s + 1 > best[1]:
                best = [s + 1, e - s + 1]
    return best
'''

WRONG = {
    '같은 가격도 상승으로 셈': '''
def solution(prices):
    bs, bl, s, l = 0, 0, 0, 0
    for i, p in enumerate(prices):
        if p == 0:
            l = 0
            continue
        if l > 0 and p >= prices[i - 1]:
            l += 1
        else:
            s, l = i + 1, 1
        if l > bl:
            bs, bl = s, l
    return [bs, bl]
''',
    '동점이면 나중 구간': '''
def solution(prices):
    bs, bl, s, l = 0, 0, 0, 0
    for i, p in enumerate(prices):
        if p == 0:
            l = 0
            continue
        if l > 0 and p > prices[i - 1]:
            l += 1
        else:
            s, l = i + 1, 1
        if l >= bl:
            bs, bl = s, l
    return [bs, bl]
''',
    '시작점마다 늘려 보기 O(n²)': '''
def solution(prices):
    n = len(prices)
    bs, bl = 0, 0
    for s in range(n):
        if prices[s] == 0:
            continue
        e = s
        while e + 1 < n and prices[e + 1] > prices[e]:
            e += 1
        if e - s + 1 > bl:
            bs, bl = s + 1, e - s + 1
    return [bs, bl]
''',
}


def examples():
    return [
        (([100, 101, 103, 102, 104, 105, 106],), [4, 4]),
        (([5, 5, 0, 3, 4, 0, 1, 2],), [4, 2]),
        (([0, 0],), [0, 0]),
    ]


def handmade():
    return [
        ([7],),
        ([0],),
        ([0, 1, 2, 3],),
        ([3, 2, 1],),
        ([1, 2, 2, 3, 4],),
        ([1, 2, 0, 3, 4, 5, 0, 6, 7, 8],),
        ([5, 0, 6],),
    ]


def small(rng):
    return ([rng.choice([0, 1, 2, 3, 4, 5]) for _ in range(rng.randint(1, 12))],)


N_SMALL = 7


def large(rng):
    return [
        (list(range(1, 200001)),),
        ([rng.randint(0, 1000000) for _ in range(200000)],),
    ]
