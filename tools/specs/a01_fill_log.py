META = {
    'id': 'A01',
    'title': '체결 로그 정리',
    'level': 1,
    'tags': ['해시', '구현', '정렬', '후기 유형: 해시+구현'],
    'params': [{'name': 'logs', 'type': 'string[]'}],
    'returnType': 'string[]',
    'description': '''
<p>증권사 주문 시스템은 체결이 일어날 때마다 <code>"주문번호 종목코드 수량"</code> 형식의 체결 로그를 남깁니다. 그런데 네트워크 재전송 때문에 <b>같은 주문번호의 로그가 여러 번</b> 들어오기도 하고, 체결 취소를 뜻하는 로그도 섞여 있습니다.</p>
<p>로그는 들어온 순서대로 아래 규칙에 따라 처리합니다.</p>
<ul>
<li>수량이 1 이상인 로그는 체결 로그입니다. 처음 보는 주문번호면 그 체결을 인정합니다. <b>이미 한 번 등장했던 주문번호</b>(취소된 주문 포함)의 체결 로그는 재전송으로 보고 무시합니다.</li>
<li>수량이 0인 로그는 해당 주문번호의 체결 취소입니다. 현재 인정된 체결이 있으면 그 체결을 없앱니다. 인정된 체결이 없는 주문번호(처음 보거나 이미 취소된 주문번호)의 취소 로그는 무시합니다.</li>
</ul>
<p>모든 로그를 처리한 뒤 남아 있는 체결을 종목코드별로 더해, <code>"종목코드 총수량"</code> 형식의 문자열 배열을 return 하도록 solution 함수를 완성해 주세요. 총수량이 많은 순서로 정렬하고, 총수량이 같으면 종목코드 사전 순으로 정렬합니다. 남은 체결이 하나도 없으면 빈 배열을 return 합니다.</p>
''',
    'constraints': [
        'logs의 길이는 1 이상 100,000 이하입니다.',
        'logs의 원소는 <code>"주문번호 종목코드 수량"</code> 형식이며, 세 값은 공백 하나로 구분됩니다.',
        '주문번호는 영어 대문자와 숫자로 이루어진 길이 1 이상 10 이하의 문자열입니다.',
        '종목코드는 숫자 6자리 문자열이며, 0으로 시작할 수 있습니다.',
        '수량은 0 이상 10,000 이하의 정수입니다.',
        '같은 주문번호의 로그라도 종목코드가 다를 수 있습니다. 이 경우에도 규칙은 같습니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b><br>A1(005930, 10), A2(000660, 5)가 인정됩니다. 세 번째 로그는 A1의 재전송이라 무시합니다. A3(005930, 3)이 인정되고, 마지막 로그로 A2가 취소됩니다. 005930은 13주, 000660은 0주라서 000660은 결과에 넣지 않습니다.</p>
<p><b>입출력 예 #2</b><br>B7이 인정된 뒤 취소됩니다. 그 뒤에 들어온 B7의 9주 로그는 이미 등장한 주문번호이므로 무시합니다. Z9는 인정된 체결이 없는 주문번호의 취소라 무시합니다. 남은 체결은 C1의 035720 4주뿐입니다.</p>
<p><b>입출력 예 #3</b><br>000660과 005930이 7주로 같으므로 종목코드 사전 순으로 정렬합니다.</p>
''',
    'explanation': '''
<p>주문번호를 두 가지로 관리하면 됩니다. 한 번이라도 체결로 등장한 주문번호를 담는 <b>set</b>과, 현재 인정된 체결을 담는 <b>dict</b>(주문번호 → (종목코드, 수량))입니다.</p>
<ul>
<li>체결 로그: set에 있으면 무시하고, 없으면 set과 dict에 모두 넣습니다.</li>
<li>취소 로그: dict에 있을 때만 dict에서 지웁니다. set에서는 지우지 않아야 이후 재전송을 계속 무시할 수 있습니다.</li>
</ul>
<p>마지막에 dict를 종목코드별로 합산하고 <code>(-총수량, 종목코드)</code>를 키로 정렬합니다. 각 로그를 O(1)에 처리하므로 전체 O(n log n)입니다.</p>
''',
    'edgeCases': [
        '취소된 주문번호로 다시 들어온 체결 로그도 무시해야 합니다(취소 후 재등록 아님).',
        '처음 보는 주문번호의 취소 로그는 아무 일도 일으키지 않고, 그 뒤의 같은 주문번호 체결은 정상으로 인정됩니다.',
        '모든 체결이 취소된 종목은 "종목코드 0"으로 넣지 않고 아예 뺍니다.',
        '총수량이 같을 때 종목코드 정렬을 빠뜨리면 입력 순서에 따라 답이 달라집니다.',
        '리스트로 주문번호를 저장하고 in으로 찾으면 O(n²)이 되어 시간 초과가 납니다.',
    ],
}

SOLUTION = '''
def solution(logs):
    seen = set()       # 체결 로그로 한 번이라도 등장한 주문번호
    alive = {}         # 현재 인정된 체결: 주문번호 -> (종목코드, 수량)
    for log in logs:
        oid, code, qty = log.split()
        qty = int(qty)
        if qty == 0:
            if oid in alive:
                del alive[oid]
            continue
        if oid in seen:
            continue
        seen.add(oid)
        alive[oid] = (code, qty)

    total = {}
    for code, qty in alive.values():
        total[code] = total.get(code, 0) + qty
    items = sorted(total.items(), key=lambda x: (-x[1], x[0]))
    return ['{} {}'.format(code, qty) for code, qty in items]
'''

BRUTE = '''
def solution(logs):
    events = []   # (주문번호, 종목코드, 수량, 살아있음)
    for log in logs:
        oid, code, qty = log.split()
        qty = int(qty)
        if qty == 0:
            for e in events:
                if e[0] == oid and e[3]:
                    e[3] = False
            continue
        if any(e[0] == oid for e in events):
            continue
        events.append([oid, code, qty, True])
    codes = sorted(set(e[1] for e in events if e[3]))
    res = [(c, sum(e[2] for e in events if e[3] and e[1] == c)) for c in codes]
    res.sort(key=lambda x: -x[1])
    return ['%s %d' % x for x in res]
'''

WRONG = {
    '재전송 무시 안 함': '''
def solution(logs):
    alive = {}
    for log in logs:
        oid, code, qty = log.split()
        qty = int(qty)
        if qty == 0:
            alive.pop(oid, None)
        else:
            alive[oid] = (code, alive.get(oid, (code, 0))[1] + qty)
    total = {}
    for code, qty in alive.values():
        total[code] = total.get(code, 0) + qty
    return ['%s %d' % x for x in sorted(total.items(), key=lambda x: (-x[1], x[0]))]
''',
    '취소 후 재체결 허용': '''
def solution(logs):
    alive = {}
    for log in logs:
        oid, code, qty = log.split()
        qty = int(qty)
        if qty == 0:
            alive.pop(oid, None)
        elif oid not in alive:
            alive[oid] = (code, qty)
    total = {}
    for code, qty in alive.values():
        total[code] = total.get(code, 0) + qty
    return ['%s %d' % x for x in sorted(total.items(), key=lambda x: (-x[1], x[0]))]
''',
    '동점 정렬 누락': '''
def solution(logs):
    seen, alive = set(), {}
    for log in logs:
        oid, code, qty = log.split()
        qty = int(qty)
        if qty == 0:
            alive.pop(oid, None)
            continue
        if oid in seen:
            continue
        seen.add(oid)
        alive[oid] = (code, qty)
    total = {}
    for code, qty in alive.values():
        total[code] = total.get(code, 0) + qty
    return ['%s %d' % x for x in sorted(total.items(), key=lambda x: -x[1])]
''',
    '리스트 탐색 O(n²)': '''
def solution(logs):
    seen, alive = [], {}
    for log in logs:
        oid, code, qty = log.split()
        qty = int(qty)
        if qty == 0:
            alive.pop(oid, None)
            continue
        if oid in seen:
            continue
        seen.append(oid)
        alive[oid] = (code, qty)
    total = {}
    for code, qty in alive.values():
        total[code] = total.get(code, 0) + qty
    return ['%s %d' % x for x in sorted(total.items(), key=lambda x: (-x[1], x[0]))]
''',
}


def examples():
    return [
        ((["A1 005930 10", "A2 000660 5", "A1 005930 10", "A3 005930 3", "A2 000660 0"],), ["005930 13"]),
        ((["B7 035420 4", "C1 035720 4", "B7 035420 0", "B7 035420 9", "Z9 000270 0"],), ["035720 4"]),
        ((["K1 000660 7", "K2 005930 7", "K3 000270 2"],), ["000660 7", "005930 7", "000270 2"]),
    ]


def handmade():
    return [
        (["X1 111111 0"],),                                             # 취소만 → 빈 배열
        (["Q1 222222 5", "Q1 222222 0", "Q1 222222 5", "Q1 222222 0"],),  # 취소 후 재전송 무시
        (["N1 333333 0", "N1 333333 8"],),                              # 처음 보는 취소는 무시 → 8 인정
        (["M1 999999 3", "M2 100000 3", "M3 555555 3", "M1 999999 3"],),  # 동점 3개, 입력 순서와 다른 정렬
        (["P1 000001 2", "P1 000002 9"],),                              # 같은 주문번호, 다른 종목 재전송
    ]


CODES = ['005930', '000660', '035420', '035720', '000270', '207940']


def small(rng):
    n = rng.randint(1, 14)
    logs = []
    for _ in range(n):
        oid = 'A%d' % rng.randint(1, 6)
        qty = 0 if rng.random() < 0.3 else rng.randint(1, 5)
        logs.append('%s %s %d' % (oid, rng.choice(CODES), qty))
    return (logs,)


def large(rng):
    out = []
    # 서로 다른 주문번호 10만 개: 리스트 탐색 풀이는 시간 초과
    logs = []
    for k in range(100000):
        qty = 0 if rng.random() < 0.1 else rng.randint(1, 10000)
        oid = 'O%d' % (k if qty else rng.randint(0, k))
        logs.append('%s %06d %d' % (oid, rng.randint(0, 2000), qty))
    out.append((logs,))
    logs = ['R%d %06d %d' % (rng.randint(0, 30000), rng.randint(0, 50), rng.choice([0, 1, 2, 3])) for _ in range(100000)]
    out.append((logs,))
    return out
