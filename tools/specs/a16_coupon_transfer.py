META = {
    'id': 'A16',
    'title': '수수료 면제 쿠폰',
    'level': 3,
    'tags': ['다익스트라', '그래프', '상태 확장'],
    'params': [{'name': 'n', 'type': 'int'}, {'name': 'routes', 'type': 'int[][]'},
               {'name': 'start', 'type': 'int'}, {'name': 'end', 'type': 'int'}],
    'returnType': 'int',
    'description': '''
<p>은행 1번부터 n번 사이의 송금 경로 <code>routes</code>가 주어집니다. 각 원소 <code>[a, b, fee]</code>는 a번 은행에서 b번 은행으로 <b>한 방향으로</b> 송금할 수 있고, 수수료가 fee원이라는 뜻입니다.</p>
<p>돈을 <code>start</code>번 은행에서 <code>end</code>번 은행으로 보내려 합니다. 여러 은행을 거쳐도 되며, 거친 경로의 수수료를 모두 냅니다. 단, <b>수수료 면제 쿠폰이 1장</b> 있어서 경로 하나의 수수료를 0원으로 만들 수 있습니다. 쿠폰은 쓰지 않아도 됩니다.</p>
<p>내야 하는 수수료 합의 최솟값을 return 하도록 solution 함수를 완성해 주세요. 보낼 수 없으면 -1을 return 합니다.</p>
''',
    'constraints': [
        'n은 1 이상 20,000 이하입니다.',
        'routes의 길이는 0 이상 100,000 이하입니다.',
        'routes의 원소 [a, b, fee]는 1 ≤ a, b ≤ n, a ≠ b, 1 ≤ fee ≤ 10,000입니다. 같은 a, b 사이에 경로가 여러 개 있을 수 있습니다.',
        'start와 end는 1 이상 n 이하입니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b><br>1 → 2 → 4는 5 + 10 = 15원이고, 10원에 쿠폰을 쓰면 5원입니다. 1 → 3 → 4는 2 + 8 = 10원이고, 8원에 쿠폰을 쓰면 2원입니다. 쿠폰 없이 가장 싼 경로(1 → 3 → 4)가 아니라 "쿠폰을 쓴 뒤 가장 싼" 경로를 찾아야 합니다.</p>
<p><b>입출력 예 #2</b><br>3 → 2 경로는 반대 방향으로 쓸 수 없어서 3번 은행에 닿을 수 없습니다.</p>
''',
    'explanation': '''
<p>정점을 <code>(은행, 쿠폰 사용 여부)</code>로 늘려서 다익스트라를 돌립니다.</p>
<ul>
<li><code>(u, 0)</code> → <code>(v, 0)</code>: 비용 fee (쿠폰 안 씀)</li>
<li><code>(u, 0)</code> → <code>(v, 1)</code>: 비용 0 (이 경로에 쿠폰 사용)</li>
<li><code>(u, 1)</code> → <code>(v, 1)</code>: 비용 fee</li>
</ul>
<p>답은 <code>min(dist[end][0], dist[end][1])</code>입니다. 정점 2n개, 간선 3m개라서 O((n + m) log n)입니다.</p>
<p>"쿠폰 없는 최단 경로를 먼저 구하고 그 경로에서 가장 비싼 수수료를 뺀다"는 방법은 틀립니다. 입출력 예 #1처럼 원래는 더 비싼 경로가 쿠폰을 쓴 뒤에는 더 쌀 수 있습니다. start와 end가 같으면 0입니다.</p>
''',
    'edgeCases': [
        '경로는 한 방향입니다.',
        '쿠폰 없는 최단 경로에 쿠폰을 적용하는 그리디는 틀립니다.',
        'start = end이면 0입니다.',
        '같은 두 은행 사이에 수수료가 다른 경로가 여러 개 있을 수 있습니다.',
    ],
}

SOLUTION = '''
import heapq

def solution(n, routes, start, end):
    graph = [[] for _ in range(n + 1)]
    for a, b, fee in routes:
        graph[a].append((b, fee))

    INF = float('inf')
    dist = [[INF, INF] for _ in range(n + 1)]
    dist[start][0] = 0
    pq = [(0, start, 0)]
    while pq:
        d, u, used = heapq.heappop(pq)
        if d > dist[u][used]:
            continue
        for v, fee in graph[u]:
            if d + fee < dist[v][used]:
                dist[v][used] = d + fee
                heapq.heappush(pq, (d + fee, v, used))
            if not used and d < dist[v][1]:
                dist[v][1] = d
                heapq.heappush(pq, (d, v, 1))
    best = min(dist[end])
    return -1 if best == INF else best
'''

BRUTE = '''
def solution(n, routes, start, end):
    INF = float('inf')
    def bellman(free):
        d = [INF] * (n + 1)
        d[start] = 0
        for _ in range(n):
            changed = False
            for k, (a, b, f) in enumerate(routes):
                c = 0 if k == free else f
                if d[a] + c < d[b]:
                    d[b] = d[a] + c
                    changed = True
            if not changed:
                break
        return d[end]
    best = min([bellman(-1)] + [bellman(k) for k in range(len(routes))])
    return -1 if best == INF else best
'''

WRONG = {
    '최단 경로에서 최댓값 빼기': '''
import heapq
def solution(n, routes, start, end):
    g = [[] for _ in range(n + 1)]
    for a, b, f in routes:
        g[a].append((b, f))
    INF = float('inf')
    d = [INF] * (n + 1)
    mx = [0] * (n + 1)
    d[start] = 0
    pq = [(0, start)]
    while pq:
        x, u = heapq.heappop(pq)
        if x > d[u]:
            continue
        for v, f in g[u]:
            if x + f < d[v]:
                d[v] = x + f
                mx[v] = max(mx[u], f)
                heapq.heappush(pq, (d[v], v))
    return -1 if d[end] == INF else d[end] - mx[end]
''',
    '경로를 양방향으로 처리': SOLUTION.replace('graph[a].append((b, fee))', 'graph[a].append((b, fee))\n        graph[b].append((a, fee))'),
    '쿠폰마다 벨만-포드 O(nm)': BRUTE,
}


def examples():
    return [
        ((4, [[1, 2, 5], [2, 4, 10], [1, 3, 2], [3, 4, 8]], 1, 4), 2),
        ((3, [[1, 2, 4], [3, 2, 1]], 1, 3), -1),
    ]


def handmade():
    return [
        (1, [], 1, 1),
        (2, [], 1, 2),
        (2, [[1, 2, 7]], 1, 2),
        (3, [[1, 2, 3], [2, 3, 3], [1, 3, 5]], 1, 3),
        (3, [[1, 2, 9], [1, 2, 1], [2, 3, 9]], 1, 3),
        (4, [[1, 2, 1], [2, 3, 1], [3, 4, 1], [1, 4, 100]], 1, 4),
        (3, [[2, 1, 5], [3, 2, 5]], 1, 3),
    ]


def small(rng):
    n = rng.randint(1, 6)
    routes = []
    for _ in range(rng.randint(0, 9)):
        a, b = rng.randint(1, n), rng.randint(1, n)
        if a != b:
            routes.append([a, b, rng.randint(1, 12)])
    return (n, routes, rng.randint(1, n), rng.randint(1, n))


N_SMALL = 8


def large(rng):
    n = 20000
    routes = [[rng.randint(1, n), rng.randint(1, n), rng.randint(1, 10000)] for _ in range(99000)]
    routes = [r for r in routes if r[0] != r[1]]
    chain = [[k, k + 1, rng.randint(1, 10000)] for k in range(1, n)]
    return [
        (n, routes, 1, n),
        (n, chain + [[1, n, 10000]] * 1000, 1, n),
    ]
