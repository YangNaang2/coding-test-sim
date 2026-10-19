META = {
    'id': 'A13',
    'title': '결제 배치 묶기',
    'level': 2,
    'tags': ['그리디', '정렬', '투 포인터'],
    'params': [{'name': 'amounts', 'type': 'int[]'}, {'name': 'limit', 'type': 'int'}],
    'returnType': 'int',
    'description': '''
<p>대량 결제 요청 <code>amounts</code>를 은행으로 보내려 합니다. 은행 전송은 배치 단위로 하는데, 배치 하나에는 결제를 <b>최대 2건</b>까지 담을 수 있고, 담긴 결제 금액의 합이 <code>limit</code>을 넘으면 안 됩니다.</p>
<p>모든 결제를 보내기 위해 필요한 배치 수의 최솟값을 return 하도록 solution 함수를 완성해 주세요.</p>
''',
    'constraints': [
        'amounts의 길이는 1 이상 100,000 이하입니다.',
        'amounts의 원소는 1 이상 limit 이하의 정수입니다.',
        'limit은 1 이상 1,000,000,000 이하의 정수입니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b><br>50 + 50을 한 배치로 묶고, 70과 80은 각각 따로 보냅니다. 70 + 50 = 120처럼 다른 조합은 limit을 넘습니다.</p>
<p><b>입출력 예 #2</b><br>어떤 두 건을 묶어도 100을 넘어서 3개 배치가 필요합니다.</p>
''',
    'explanation': '''
<p>금액을 정렬한 뒤 <b>가장 큰 결제</b>부터 처리합니다. 가장 큰 결제와 함께 묶을 수 있는 후보 중에서는 가장 작은 결제가 가장 유리하므로, 양 끝 포인터를 씁니다.</p>
<ul>
<li>가장 작은 것 + 가장 큰 것 ≤ limit이면 둘을 묶고 양쪽 포인터를 모두 옮깁니다.</li>
<li>아니면 가장 큰 것은 누구와도 묶일 수 없으므로 혼자 보내고 오른쪽 포인터만 옮깁니다.</li>
</ul>
<p>정렬 O(n log n) + 투 포인터 O(n)입니다. 작은 것끼리 먼저 묶는 그리디는 틀립니다(예: [1, 2, 9, 10], limit 11이면 1+10, 2+9로 2개가 최적).</p>
''',
    'edgeCases': [
        '작은 금액끼리 먼저 묶으면 최적이 아닙니다.',
        '합이 limit과 정확히 같아도 묶을 수 있습니다.',
        '결제가 1건이면 1입니다.',
        '짝을 찾을 때마다 앞에서부터 다시 훑으면 O(n²)입니다.',
    ],
}

SOLUTION = '''
def solution(amounts, limit):
    a = sorted(amounts)
    lo, hi = 0, len(a) - 1
    batches = 0
    while lo <= hi:
        if lo < hi and a[lo] + a[hi] <= limit:
            lo += 1
        hi -= 1
        batches += 1
    return batches
'''

BRUTE = '''
from functools import lru_cache
def solution(amounts, limit):
    a = tuple(sorted(amounts))
    @lru_cache(maxsize=None)
    def best(rest):
        if not rest:
            return 0
        first, others = rest[0], rest[1:]
        res = 1 + best(others)
        for k in range(len(others)):
            if first + others[k] <= limit:
                res = min(res, 1 + best(others[:k] + others[k + 1:]))
        return res
    return best(a)
'''

WRONG = {
    '작은 것끼리 묶기': '''
def solution(amounts, limit):
    a = sorted(amounts)
    i, cnt = 0, 0
    while i < len(a):
        if i + 1 < len(a) and a[i] + a[i + 1] <= limit:
            i += 2
        else:
            i += 1
        cnt += 1
    return cnt
''',
    '합이 limit 미만만 허용': '''
def solution(amounts, limit):
    a = sorted(amounts)
    lo, hi, cnt = 0, len(a) - 1, 0
    while lo <= hi:
        if lo < hi and a[lo] + a[hi] < limit:
            lo += 1
        hi -= 1
        cnt += 1
    return cnt
''',
    '짝을 매번 처음부터 찾기 O(n²)': '''
def solution(amounts, limit):
    a = sorted(amounts)
    used = [False] * len(a)
    cnt = 0
    for i in range(len(a) - 1, -1, -1):
        if used[i]:
            continue
        used[i] = True
        for j in range(i):
            if not used[j]:
                if a[j] + a[i] <= limit:
                    used[j] = True
                break
        cnt += 1
    return cnt
''',
}


def examples():
    return [
        (([70, 50, 80, 50], 100), 3),
        (([70, 80, 50], 100), 3),
    ]


def handmade():
    return [
        ([5], 5),
        ([1, 2, 9, 10], 11),
        ([5, 5, 5, 5], 10),
        ([5, 5, 5, 5, 5], 10),
        ([10, 10, 10], 10),
        ([1, 1, 1, 1, 1, 1], 1),
        ([3, 7, 3, 7, 5, 5], 10),
    ]


def small(rng):
    limit = rng.randint(2, 20)
    return ([rng.randint(1, limit) for _ in range(rng.randint(1, 8))], limit)


N_SMALL = 7


def large(rng):
    return [
        ([rng.randint(1, 1000000000) for _ in range(100000)], 1000000000),
        ([rng.randint(400, 600) for _ in range(100000)], 1000),
    ]
