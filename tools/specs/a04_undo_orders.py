META = {
    'id': 'A04',
    'title': '주문 되돌리기',
    'level': 1,
    'tags': ['스택', '구현', '시뮬레이션'],
    'params': [{'name': 'cash', 'type': 'long'}, {'name': 'commands', 'type': 'string[]'}],
    'returnType': 'long[]',
    'description': '''
<p>모의투자 앱에서 한 종목을 사고팔며 연습하고 있습니다. 처음 현금은 <code>cash</code>원이고, 보유 주식은 0주입니다. 명령 <code>commands</code>를 순서대로 처리합니다.</p>
<ul>
<li><code>"BUY p q"</code>: 한 주에 p원으로 q주를 삽니다. 현금이 p × q원 이상일 때만 성공하고, 부족하면 아무 일도 일어나지 않습니다.</li>
<li><code>"SELL p q"</code>: 한 주에 p원으로 q주를 팝니다. 보유 주식이 q주 이상일 때만 성공하고, 부족하면 아무 일도 일어나지 않습니다.</li>
<li><code>"UNDO"</code>: 아직 되돌리지 않은 <b>성공한 거래</b> 중 가장 최근 거래를 되돌려 현금과 보유 주식을 그 거래 직전으로 돌립니다. 되돌릴 거래가 없으면 아무 일도 일어나지 않습니다. 되돌린 것을 다시 실행하는 기능은 없습니다.</li>
</ul>
<p>모든 명령을 처리한 뒤 <code>[현금, 보유 주식 수]</code>를 return 하도록 solution 함수를 완성해 주세요.</p>
''',
    'constraints': [
        'cash는 0 이상 1,000,000,000 이하의 정수입니다.',
        'commands의 길이는 1 이상 100,000 이하입니다.',
        'p는 1 이상 1,000,000 이하, q는 1 이상 1,000 이하의 정수입니다.',
        '현금은 32비트 정수 범위를 넘을 수 있습니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b><br>BUY로 현금 5,000원·5주 → SELL로 7,400원·3주 → UNDO로 SELL을 되돌려 5,000원·5주 → BUY 3000×3은 현금 부족으로 실패(되돌릴 목록에도 들어가지 않음) → UNDO로 첫 BUY를 되돌려 10,000원·0주 → 마지막 UNDO는 되돌릴 거래가 없어 무시합니다.</p>
<p><b>입출력 예 #2</b><br>첫 SELL은 보유 주식이 없어 실패합니다. BUY 2500×2로 0원·2주, SELL 2600×1로 2,600원·1주, BUY 100×10으로 1,600원·11주가 되고, UNDO로 마지막 BUY를 되돌려 2,600원·1주입니다.</p>
''',
    'explanation': '''
<p>성공한 거래만 <b>스택</b>에 쌓고, UNDO가 오면 스택에서 꺼내 반대로 적용합니다. 거래가 LIFO 순서로 되돌려지므로, 되돌리는 시점의 현금과 주식은 항상 그 거래 직후 상태와 같습니다. 그래서 되돌리기가 실패할 일은 없습니다.</p>
<p>실패한 거래까지 스택에 넣거나, 빈 스택에서 pop해 에러가 나는 경우를 조심하세요. 명령마다 처음부터 다시 계산하면 O(n²)이 되어 시간 초과가 납니다.</p>
''',
    'edgeCases': [
        '실패한 BUY/SELL은 되돌릴 대상이 아닙니다.',
        '스택이 비었을 때의 UNDO는 무시합니다(pop 에러 주의).',
        '현금이 정확히 p × q원이면 매수에 성공합니다.',
        '현금 합계가 int 범위를 넘을 수 있어 Java·C++는 long이 필요합니다.',
    ],
}

SOLUTION = '''
def solution(cash, commands):
    shares = 0
    done = []   # 성공한 거래: (종류, 가격, 수량)
    for cmd in commands:
        parts = cmd.split()
        if parts[0] == 'UNDO':
            if done:
                kind, p, q = done.pop()
                if kind == 'BUY':
                    cash += p * q
                    shares -= q
                else:
                    cash -= p * q
                    shares += q
            continue
        p, q = int(parts[1]), int(parts[2])
        if parts[0] == 'BUY':
            if cash >= p * q:
                cash -= p * q
                shares += q
                done.append(('BUY', p, q))
        else:
            if shares >= q:
                cash += p * q
                shares -= q
                done.append(('SELL', p, q))
    return [cash, shares]
'''

BRUTE = '''
def solution(cash, commands):
    # 매 UNDO마다 남아 있는 거래 목록으로 처음부터 다시 계산한다.
    applied = []
    def state(lst):
        c, s = cash, 0
        for k, p, q in lst:
            if k == 'BUY':
                c, s = c - p * q, s + q
            else:
                c, s = c + p * q, s - q
        return c, s
    for cmd in commands:
        parts = cmd.split()
        c, s = state(applied)
        if parts[0] == 'UNDO':
            if applied:
                applied = applied[:-1]
            continue
        p, q = int(parts[1]), int(parts[2])
        if parts[0] == 'BUY' and c >= p * q:
            applied.append(('BUY', p, q))
        elif parts[0] == 'SELL' and s >= q:
            applied.append(('SELL', p, q))
    return list(state(applied))
'''

WRONG = {
    '실패한 거래도 스택에 넣음': '''
def solution(cash, commands):
    shares, done = 0, []
    for cmd in commands:
        parts = cmd.split()
        if parts[0] == 'UNDO':
            if done:
                k, p, q, ok = done.pop()
                if ok and k == 'BUY':
                    cash, shares = cash + p * q, shares - q
                elif ok:
                    cash, shares = cash - p * q, shares + q
            continue
        p, q = int(parts[1]), int(parts[2])
        ok = (cash >= p * q) if parts[0] == 'BUY' else (shares >= q)
        if ok and parts[0] == 'BUY':
            cash, shares = cash - p * q, shares + q
        elif ok:
            cash, shares = cash + p * q, shares - q
        done.append((parts[0], p, q, True))
    return [cash, shares]
''',
    '빈 스택 pop': '''
def solution(cash, commands):
    shares, done = 0, []
    for cmd in commands:
        parts = cmd.split()
        if parts[0] == 'UNDO':
            k, p, q = done.pop()
            if k == 'BUY':
                cash, shares = cash + p * q, shares - q
            else:
                cash, shares = cash - p * q, shares + q
            continue
        p, q = int(parts[1]), int(parts[2])
        if parts[0] == 'BUY' and cash >= p * q:
            cash, shares = cash - p * q, shares + q
            done.append(('BUY', p, q))
        elif parts[0] == 'SELL' and shares >= q:
            cash, shares = cash + p * q, shares - q
            done.append(('SELL', p, q))
    return [cash, shares]
''',
    '처음부터 다시 계산 O(n²)': BRUTE,
}


def examples():
    return [
        ((10000, ["BUY 1000 5", "SELL 1200 2", "UNDO", "BUY 3000 3", "UNDO", "UNDO"]), [10000, 0]),
        ((5000, ["SELL 100 1", "BUY 2500 2", "SELL 2600 1", "BUY 100 10", "UNDO"]), [2600, 1]),
    ]


def handmade():
    return [
        (0, ["UNDO", "UNDO"]),
        (100, ["BUY 100 1"]),                         # 정확히 같은 금액
        (100, ["BUY 101 1", "UNDO"]),                 # 실패 후 UNDO는 무시
        (1000, ["BUY 10 10", "SELL 50 10", "BUY 10 50", "SELL 1000 50", "UNDO", "UNDO", "UNDO"]),
        (1000000000, ["BUY 1 1000", "BUY 1 1000"] + ["SELL 1000000 1"] * 2000),   # 현금이 int 범위를 넘음
        (50, ["SELL 1 1", "BUY 5 10", "SELL 6 10", "UNDO", "SELL 7 5", "UNDO", "UNDO"]),
    ]


def small(rng):
    cmds = []
    for _ in range(rng.randint(1, 12)):
        r = rng.random()
        if r < 0.3:
            cmds.append('UNDO')
        else:
            cmds.append('%s %d %d' % ('BUY' if r < 0.65 else 'SELL', rng.randint(1, 20), rng.randint(1, 5)))
    return (rng.randint(0, 100), cmds)


N_SMALL = 7


def large(rng):
    cmds = []
    for k in range(100000):
        r = rng.random()
        if r < 0.25:
            cmds.append('UNDO')
        else:
            cmds.append('%s %d %d' % ('BUY' if r < 0.6 else 'SELL', rng.randint(1, 1000000), rng.randint(1, 1000)))
    # 앞쪽은 성공하는 거래만 길게 이어지도록 해서 처음부터 다시 계산하는 풀이를 느리게 만든다
    head = ['BUY 1 1'] * 40000 + ['UNDO'] * 10
    return [(1000000000, head + cmds[:60000])]
