META = {
    'id': 'A12',
    'title': '명의자 계좌 묶기',
    'level': 2,
    'tags': ['그래프', 'Union-Find', 'DFS/BFS'],
    'params': [{'name': 'n', 'type': 'int'}, {'name': 'balances', 'type': 'int[]'}, {'name': 'links', 'type': 'int[][]'}],
    'returnType': 'long[]',
    'description': '''
<p>계좌 1번부터 n번까지의 잔고 <code>balances</code>가 주어집니다. <code>balances[i]</code>는 (i + 1)번 계좌의 잔고입니다.</p>
<p>본인 인증 기록 <code>links</code>의 각 원소 <code>[a, b]</code>는 a번 계좌와 b번 계좌가 <b>같은 사람의 계좌</b>라는 뜻입니다. 같은 사람 관계는 이어집니다. 즉 a와 b가 같은 사람이고 b와 c가 같은 사람이면 a와 c도 같은 사람입니다. 어떤 기록에도 나오지 않는 계좌는 혼자서 한 사람의 계좌입니다.</p>
<p>사람별로 계좌 잔고를 모두 더한 값을 <b>큰 순서대로</b> 담은 배열을 return 하도록 solution 함수를 완성해 주세요.</p>
''',
    'constraints': [
        'n은 1 이상 100,000 이하입니다.',
        'balances의 길이는 n이고, 원소는 0 이상 1,000,000,000 이하의 정수입니다.',
        'links의 길이는 0 이상 200,000 이하입니다.',
        'links의 원소 [a, b]는 1 ≤ a, b ≤ n입니다. a = b인 기록이나 같은 기록이 여러 번 나올 수도 있습니다.',
        '합계는 32비트 정수 범위를 넘을 수 있습니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b><br>1·2·3번은 한 사람(600), 4번은 자기 자신과의 기록뿐이라 혼자(400), 5번도 혼자(500)입니다.</p>
<p><b>입출력 예 #2</b><br>세 계좌가 모두 이어져 한 사람입니다.</p>
''',
    'explanation': '''
<p>계좌를 정점, 기록을 간선으로 보면 사람 = <b>연결 요소</b>입니다. 두 가지 방법이 있습니다.</p>
<ul>
<li><b>Union-Find</b>: 기록마다 <code>union(a, b)</code>를 하고, 마지막에 <code>find(i)</code>가 같은 계좌끼리 잔고를 더합니다. 경로 압축을 쓰면 거의 O(n + m)입니다.</li>
<li><b>BFS/반복 DFS</b>: 인접 리스트를 만들고 방문하지 않은 계좌에서 탐색을 시작합니다.</li>
</ul>
<p>Python에서 <b>재귀 DFS</b>를 쓰면 계좌 10만 개가 한 줄로 이어진 입력에서 재귀 한도(기본 1,000)를 넘어 런타임 에러가 납니다. <code>sys.setrecursionlimit</code>을 올리거나 반복문으로 탐색하세요. 기록이 하나도 없는 계좌도 결과에 넣어야 합니다.</p>
''',
    'edgeCases': [
        '긴 사슬 입력에서 재귀 DFS는 재귀 한도를 넘습니다.',
        '자기 자신과의 기록, 중복 기록이 있습니다.',
        '기록에 없는 계좌도 혼자서 한 사람입니다.',
        'links가 빈 배열일 수 있습니다.',
        '합계는 long이 필요합니다(Java·C++).',
    ],
}

SOLUTION = '''
def solution(n, balances, links):
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]   # 경로 압축(절반)
            x = parent[x]
        return x

    for a, b in links:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    total = {}
    for i in range(1, n + 1):
        r = find(i)
        total[r] = total.get(r, 0) + balances[i - 1]
    return sorted(total.values(), reverse=True)
'''

BRUTE = '''
def solution(n, balances, links):
    group = list(range(n + 1))
    changed = True
    while changed:
        changed = False
        for a, b in links:
            g = min(group[a], group[b])
            if group[a] != g or group[b] != g:
                group[a] = group[b] = g
                changed = True
    sums = {}
    for i in range(1, n + 1):
        sums[group[i]] = sums.get(group[i], 0) + balances[i - 1]
    return sorted(sums.values(), reverse=True)
'''

WRONG = {
    '재귀 DFS': '''
def solution(n, balances, links):
    adj = [[] for _ in range(n + 1)]
    for a, b in links:
        adj[a].append(b)
        adj[b].append(a)
    seen = [False] * (n + 1)
    def dfs(v):
        seen[v] = True
        s = balances[v - 1]
        for w in adj[v]:
            if not seen[w]:
                s += dfs(w)
        return s
    return sorted((dfs(i) for i in range(1, n + 1) if not seen[i]), reverse=True)
''',
    '기록에 나온 계좌만 계산': '''
def solution(n, balances, links):
    p = list(range(n + 1))
    def f(x):
        while p[x] != x:
            x = p[x]
        return x
    used = set()
    for a, b in links:
        used.update((a, b))
        ra, rb = f(a), f(b)
        if ra != rb:
            p[ra] = rb
    t = {}
    for i in used:
        t[f(i)] = t.get(f(i), 0) + balances[i - 1]
    return sorted(t.values(), reverse=True)
''',
}


def examples():
    return [
        ((5, [100, 200, 300, 400, 500], [[1, 2], [2, 3], [4, 4]]), [600, 500, 400]),
        ((3, [5, 5, 5], [[1, 3], [3, 1], [2, 3]]), [15]),
    ]


def handmade():
    return [
        (1, [7], []),
        (4, [0, 0, 0, 0], []),
        (4, [1, 2, 3, 4], [[1, 1], [2, 2], [3, 3]]),
        (6, [10, 20, 30, 40, 50, 60], [[1, 6], [6, 1], [2, 5], [3, 4], [4, 3]]),
        (3, [1000000000, 1000000000, 1000000000], [[1, 2], [2, 3]]),
    ]


def small(rng):
    n = rng.randint(1, 9)
    links = [[rng.randint(1, n), rng.randint(1, n)] for _ in range(rng.randint(0, 8))]
    return (n, [rng.randint(0, 50) for _ in range(n)], links)


N_SMALL = 7


def large(rng):
    n = 100000
    chain = [[k, k + 1] for k in range(1, n)]
    rng.shuffle(chain)
    rand_links = [[rng.randint(1, n), rng.randint(1, n)] for _ in range(70000)]
    return [
        (n, [rng.randint(0, 1000000000) for _ in range(n)], chain),
        (n, [rng.randint(0, 1000000000) for _ in range(n)], rand_links),
        (n, [1000000000] * n, [[1, k] for k in range(2, n + 1)] * 2),
    ]
