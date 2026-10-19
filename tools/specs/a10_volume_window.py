META = {
    'id': 'A10',
    'title': '최단 기간 거래량',
    'level': 2,
    'tags': ['투 포인터', '누적 합', '슬라이딩 윈도'],
    'params': [{'name': 'volumes', 'type': 'int[]'}, {'name': 'target', 'type': 'long'}],
    'returnType': 'int[]',
    'description': '''
<p>어떤 종목의 일별 거래량 <code>volumes</code>가 주어집니다. <code>volumes[i]</code>는 (i + 1)일째의 거래량입니다.</p>
<p><b>연속한 기간</b> 동안의 거래량 합이 <code>target</code> 이상이 되는 기간 중 가장 짧은 기간을 찾으려 합니다. 가장 짧은 기간이 여러 개면 시작일이 가장 빠른 기간을 고릅니다.</p>
<p>그 기간의 <code>[시작일, 기간 길이]</code>를 return 하도록 solution 함수를 완성해 주세요. 시작일은 1부터 셉니다. 그런 기간이 없으면 <code>[-1, -1]</code>을 return 합니다.</p>
''',
    'constraints': [
        'volumes의 길이는 1 이상 200,000 이하입니다.',
        'volumes의 원소는 1 이상 1,000,000 이하의 정수입니다.',
        'target은 1 이상 200,000,000,000 이하의 정수입니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b><br>길이 1인 기간 중 7 이상은 없습니다. 길이 2인 기간의 합은 5, 4, 3, 6, 7이고, 5~6일(4 + 3 = 7)이 처음으로 7 이상입니다.</p>
<p><b>입출력 예 #2</b><br>2일과 3일 모두 거래량이 4로 길이 1짜리 답이 되지만, 시작일이 빠른 2일을 고릅니다.</p>
<p><b>입출력 예 #3</b><br>전체 합이 3이라 5에 닿지 않습니다.</p>
''',
    'explanation': '''
<p>거래량이 모두 양수이므로 <b>투 포인터</b>를 쓸 수 있습니다. 오른쪽 끝 r을 한 칸씩 늘리며 합에 더하고, 합이 target 이상인 동안 왼쪽 끝 l을 줄여 가며 길이를 기록합니다.</p>
<p>길이가 <b>더 짧을 때만</b> 답을 바꿔야 시작일이 빠른 기간이 남습니다. 각 포인터가 한 방향으로만 움직이므로 O(n)입니다.</p>
<p>모든 시작점에서 끝을 늘려 보는 O(n²)은 n = 200,000에서 시간 초과입니다. Java·C++에서는 target과 합이 int 범위를 넘으므로 long이 필요합니다.</p>
''',
    'edgeCases': [
        '길이가 같은 기간이 여러 개면 시작일이 가장 빠른 것을 고릅니다.',
        '하루 거래량만으로 target 이상이면 길이 1입니다.',
        '전체 합이 target보다 작으면 [-1, -1]입니다.',
        '합이 정확히 target이어도 됩니다.',
    ],
}

SOLUTION = '''
def solution(volumes, target):
    best_start, best_len = -1, -1
    total = 0
    left = 0
    for right, v in enumerate(volumes):
        total += v
        while total >= target:
            length = right - left + 1
            if best_len == -1 or length < best_len:
                best_start, best_len = left + 1, length
            total -= volumes[left]
            left += 1
    return [best_start, best_len]
'''

BRUTE = '''
def solution(volumes, target):
    n = len(volumes)
    for length in range(1, n + 1):
        s = sum(volumes[:length])
        for st in range(n - length + 1):
            if st:
                s += volumes[st + length - 1] - volumes[st - 1]
            if s >= target:
                return [st + 1, length]
    return [-1, -1]
'''

WRONG = {
    '동점이면 나중 기간': '''
def solution(volumes, target):
    bs, bl, t, l = -1, -1, 0, 0
    for r, v in enumerate(volumes):
        t += v
        while t >= target:
            if bl == -1 or r - l + 1 <= bl:
                bs, bl = l + 1, r - l + 1
            t -= volumes[l]
            l += 1
    return [bs, bl]
''',
    '합이 target 초과만 인정': '''
def solution(volumes, target):
    bs, bl, t, l = -1, -1, 0, 0
    for r, v in enumerate(volumes):
        t += v
        while t > target:
            if bl == -1 or r - l + 1 < bl:
                bs, bl = l + 1, r - l + 1
            t -= volumes[l]
            l += 1
    return [bs, bl]
''',
    '시작점마다 늘려 보기 O(n²)': '''
def solution(volumes, target):
    n, bs, bl = len(volumes), -1, -1
    for s in range(n):
        t = 0
        for e in range(s, n):
            t += volumes[e]
            if t >= target:
                if bl == -1 or e - s + 1 < bl:
                    bs, bl = s + 1, e - s + 1
                break
    return [bs, bl]
''',
}


def examples():
    return [
        (([2, 3, 1, 2, 4, 3], 7), [5, 2]),
        (([1, 4, 4], 4), [2, 1]),
        (([1, 1, 1], 5), [-1, -1]),
    ]


def handmade():
    return [
        ([5], 5),
        ([5], 6),
        ([1, 2, 3, 3, 2, 1], 5),
        ([3, 3, 3, 3], 6),
        ([1000000] * 10, 10000000),
        ([1, 1, 1, 1, 10], 11),
    ]


def small(rng):
    v = [rng.randint(1, 6) for _ in range(rng.randint(1, 10))]
    return (v, rng.randint(1, 25))


N_SMALL = 7


def large(rng):
    return [
        ([1] * 200000, 150000),
        ([rng.randint(1, 1000000) for _ in range(200000)], 200000000000),
    ]
