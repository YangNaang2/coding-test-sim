META = {
    'id': 'A11',
    'title': '결재 서류 전달',
    'level': 2,
    'tags': ['BFS', '격자', '그래프 탐색'],
    'params': [{'name': 'maps', 'type': 'string[]'}],
    'returnType': 'int',
    'description': '''
<p>본사 층 평면도 <code>maps</code>가 주어집니다. 각 문자는 다음을 뜻합니다.</p>
<ul>
<li><code>S</code>: 출발 지점(정확히 1개)</li>
<li><code>E</code>: 서류를 제출할 출구(정확히 1개)</li>
<li><code>A</code>: 결재를 받을 수 있는 책상(1개 이상)</li>
<li><code>#</code>: 지나갈 수 없는 벽, <code>.</code>: 빈 통로</li>
</ul>
<p>직원은 S에서 출발해 상하좌우로 한 칸씩 움직이며, 한 칸 움직이는 데 1초가 걸립니다. 서류를 제출하려면 <b>A 중 아무 곳이나 한 곳</b>에 먼저 들러 결재를 받은 뒤 E에 도착해야 합니다. 결재를 받기 전에 E 칸을 지나가는 것은 괜찮지만, 그때는 제출이 되지 않습니다. 이미 지난 칸을 다시 지나갈 수 있습니다.</p>
<p>서류를 제출하는 데 걸리는 최소 시간을 return 하도록 solution 함수를 완성해 주세요. 제출할 수 없으면 -1을 return 합니다.</p>
''',
    'constraints': [
        'maps의 길이(행 수)는 1 이상 100 이하입니다.',
        'maps의 원소 길이(열 수)는 1 이상 100 이하이며, 모두 같습니다. 전체 칸 수는 3 이상입니다.',
        'maps는 S, E, A, #, . 로만 이루어져 있습니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b><br>오른쪽 위 A는 벽을 돌아가야 해서 S에서 8초, 거기서 E까지 2초로 합계 10초입니다. 왼쪽 아래 A는 S에서 2초, E까지 4초로 합계 6초라 6을 return 합니다. S에서 가장 가까운 A가 아니라 전체 합이 가장 작은 A를 골라야 합니다.</p>
<p><b>입출력 예 #2</b><br>A가 벽으로 둘러싸여 있어 결재를 받을 수 없습니다.</p>
<p><b>입출력 예 #3</b><br>E를 지나 A에 들른 뒤 E로 돌아옵니다. S에서 A까지 5초, A에서 E까지 2초로 7초입니다.</p>
''',
    'explanation': '''
<p>A가 여러 개라도 BFS를 두 번만 돌리면 됩니다.</p>
<ol>
<li>S에서 BFS를 돌려 모든 칸까지의 최단 거리 <code>dS</code>를 구합니다.</li>
<li>E에서 BFS를 돌려 <code>dE</code>를 구합니다. 상하좌우 이동은 되돌아가도 거리가 같으므로, "A에서 E까지의 거리"는 "E에서 A까지의 거리"와 같습니다.</li>
<li>모든 A 칸에 대해 <code>dS[A] + dE[A]</code>의 최솟값이 답입니다. 둘 중 하나라도 닿지 않으면 그 A는 건너뜁니다.</li>
</ol>
<p>칸 수를 N이라 하면 O(N)입니다. A마다 BFS를 새로 돌리면 A가 많을 때 O(N²)이 되어 느려집니다.</p>
''',
    'edgeCases': [
        'A를 들르지 않고 S → E 최단 거리를 구하면 틀립니다.',
        'A가 여러 개면 가장 가까운 A가 아니라 dS + dE가 가장 작은 A를 골라야 합니다.',
        'E를 지나쳐 A로 가는 경로도 허용됩니다(E를 벽으로 처리하면 틀림).',
        'S나 E에서 닿지 않는 A는 건너뜁니다.',
    ],
}

SOLUTION = '''
from collections import deque

def bfs(maps, sr, sc):
    n, m = len(maps), len(maps[0])
    dist = [[-1] * m for _ in range(n)]
    dist[sr][sc] = 0
    q = deque([(sr, sc)])
    while q:
        r, c = q.popleft()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < n and 0 <= nc < m and maps[nr][nc] != '#' and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return dist

def solution(maps):
    desks = []
    for r, row in enumerate(maps):
        for c, ch in enumerate(row):
            if ch == 'S':
                start = (r, c)
            elif ch == 'E':
                end = (r, c)
            elif ch == 'A':
                desks.append((r, c))
    ds = bfs(maps, *start)
    de = bfs(maps, *end)
    best = -1
    for r, c in desks:
        if ds[r][c] >= 0 and de[r][c] >= 0:
            total = ds[r][c] + de[r][c]
            if best == -1 or total < best:
                best = total
    return best
'''

BRUTE = '''
from collections import deque
def solution(maps):
    n, m = len(maps), len(maps[0])
    for r in range(n):
        for c in range(m):
            if maps[r][c] == 'S':
                s = (r, c)
    seen = {(s[0], s[1], False): 0}
    q = deque([(s[0], s[1], False)])
    while q:
        r, c, ok = q.popleft()
        d = seen[(r, c, ok)]
        if ok and maps[r][c] == 'E':
            return d
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < n and 0 <= nc < m and maps[nr][nc] != '#':
                st = (nr, nc, ok or maps[nr][nc] == 'A')
                if st not in seen:
                    seen[st] = d + 1
                    q.append(st)
    return -1
'''

WRONG = {
    'A를 거치지 않음': '''
from collections import deque
def solution(maps):
    n, m = len(maps), len(maps[0])
    s = next((r, c) for r in range(n) for c in range(m) if maps[r][c] == 'S')
    d = {s: 0}
    q = deque([s])
    while q:
        r, c = q.popleft()
        if maps[r][c] == 'E':
            return d[(r, c)]
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < n and 0 <= nc < m and maps[nr][nc] != '#' and (nr, nc) not in d:
                d[(nr, nc)] = d[(r, c)] + 1
                q.append((nr, nc))
    return -1
''',
    'S에서 가장 가까운 A만 사용': '''
from collections import deque
def bfs(maps, s):
    n, m = len(maps), len(maps[0])
    d = {s: 0}
    q = deque([s])
    while q:
        r, c = q.popleft()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < n and 0 <= nc < m and maps[nr][nc] != '#' and (nr, nc) not in d:
                d[(nr, nc)] = d[(r, c)] + 1
                q.append((nr, nc))
    return d
def solution(maps):
    n, m = len(maps), len(maps[0])
    cells = {maps[r][c]: (r, c) for r in range(n) for c in range(m) if maps[r][c] in 'SE'}
    ds, de = bfs(maps, cells['S']), bfs(maps, cells['E'])
    desks = [(r, c) for r in range(n) for c in range(m) if maps[r][c] == 'A' and (r, c) in ds]
    if not desks:
        return -1
    a = min(desks, key=lambda x: ds[x])
    return ds[a] + de[a] if a in de else -1
''',
    'E를 벽으로 처리': '''
from collections import deque
def bfs(maps, s, block):
    n, m = len(maps), len(maps[0])
    d = {s: 0}
    q = deque([s])
    while q:
        r, c = q.popleft()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < n and 0 <= nc < m and maps[nr][nc] not in block and (nr, nc) not in d:
                d[(nr, nc)] = d[(r, c)] + 1
                q.append((nr, nc))
    return d
def solution(maps):
    n, m = len(maps), len(maps[0])
    cells = {maps[r][c]: (r, c) for r in range(n) for c in range(m) if maps[r][c] in 'SE'}
    ds, de = bfs(maps, cells['S'], '#E'), bfs(maps, cells['E'], '#')
    best = -1
    for r in range(n):
        for c in range(m):
            if maps[r][c] == 'A' and (r, c) in ds and (r, c) in de:
                t = ds[(r, c)] + de[(r, c)]
                best = t if best == -1 else min(best, t)
    return best
''',
}


def examples():
    return [
        ((["S.#.A", "..#..", "A...E"],), 6),
        ((["S#A#", ".###", "...E"],), -1),
        ((["S..E.A"],), 7),
    ]


def handmade():
    return [
        (["SA", "#E"],),
        (["SE", "A#"],),
        (["S#E", "A#A"],),
        (["S...", "####", "A..E"],),
        (["SAAAAAAAAE"],),
        (["S.........", ".########.", ".#......#.", ".#.####.#.", ".#.#A..#.#", ".#.####.#.", ".#......#E", ".########.", "..........", "A........."],),
    ]


def make_grid(rng, n, m, wall, desks):
    g = [['#' if rng.random() < wall else '.' for _ in range(m)] for _ in range(n)]
    cells = [(r, c) for r in range(n) for c in range(m)]
    rng.shuffle(cells)
    (sr, sc), (er, ec) = cells[0], cells[1]
    g[sr][sc], g[er][ec] = 'S', 'E'
    for r, c in cells[2:2 + desks]:
        g[r][c] = 'A'
    return [''.join(row) for row in g]


def small(rng):
    return (make_grid(rng, rng.randint(2, 6), rng.randint(2, 6), 0.3, rng.randint(1, 3)),)


N_SMALL = 8


def large(rng):
    open_grid = ['.' * 100 for _ in range(100)]
    g = [list(r) for r in open_grid]
    g[0][0], g[99][99] = 'S', 'E'
    for k in range(1, 99):
        g[k][50] = 'A'
    return [
        ([''.join(r) for r in g],),
        (make_grid(rng, 100, 100, 0.25, 3000),),
        (make_grid(rng, 100, 100, 0.45, 5),),
    ]
