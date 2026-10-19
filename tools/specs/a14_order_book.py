META = {
    'id': 'A14',
    'title': '호가창 체결',
    'level': 3,
    'tags': ['힙', '시뮬레이션', '해시', '우선순위 큐'],
    'params': [{'name': 'orders', 'type': 'string[]'}],
    'returnType': 'long[]',
    'description': '''
<p>한 종목의 지정가 주문 <code>orders</code>를 들어온 순서대로 처리하는 체결 엔진을 만들려 합니다. 주문번호는 orders에서의 순서(1부터)입니다. 주문은 세 종류입니다.</p>
<ul>
<li><code>"B 가격 수량"</code>: 매수 주문. 호가창의 매도 주문 중 가격이 <b>이 매수 가격 이하</b>인 것과 체결합니다.</li>
<li><code>"S 가격 수량"</code>: 매도 주문. 호가창의 매수 주문 중 가격이 <b>이 매도 가격 이상</b>인 것과 체결합니다.</li>
<li><code>"C 주문번호"</code>: 해당 주문의 남은 수량을 호가창에서 취소합니다. 이미 모두 체결됐거나 취소된 주문, 또는 취소 주문(C)을 가리키면 아무 일도 일어나지 않습니다.</li>
</ul>
<p>체결 규칙은 다음과 같습니다.</p>
<ol>
<li>새 매수 주문은 <b>가장 싼</b> 매도 주문부터, 새 매도 주문은 <b>가장 비싼</b> 매수 주문부터 체결합니다. 가격이 같으면 <b>먼저 들어온</b> 주문부터 체결합니다.</li>
<li>체결 가격은 호가창에 <b>먼저 있던 주문의 가격</b>입니다.</li>
<li>한 번에 체결되는 수량은 두 주문의 남은 수량 중 작은 값입니다. 새 주문의 수량이 남아 있고 조건에 맞는 상대 주문이 있는 동안 체결을 반복합니다.</li>
<li>체결하고 남은 새 주문의 수량은 호가창에 올라가 다음 주문을 기다립니다.</li>
</ol>
<p>모든 주문을 처리한 뒤 <code>[총 체결 수량, 총 체결 대금, 호가창에 남은 매수 수량 합, 남은 매도 수량 합]</code>을 return 하도록 solution 함수를 완성해 주세요. 체결 대금은 체결마다 체결 가격 × 체결 수량을 더한 값입니다.</p>
''',
    'constraints': [
        'orders의 길이는 1 이상 100,000 이하입니다.',
        '가격은 1 이상 1,000,000 이하, 수량은 1 이상 10,000 이하의 정수입니다.',
        '취소 주문의 주문번호는 1 이상 orders의 길이 이하이며, 자기 자신보다 앞선 번호입니다.',
        '체결 대금은 32비트 정수 범위를 넘을 수 있습니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b></p>
<ol>
<li>매수 100원 5주, 매수 101원 3주가 호가창에 올라갑니다.</li>
<li>매도 100원 6주: 가장 비싼 매수 101원과 3주 체결(303원), 다음 매수 100원과 3주 체결(300원). 1번 주문은 2주 남습니다.</li>
<li>매도 99원 4주: 매수 100원과 2주 체결(200원). 남은 2주는 매도 99원으로 호가창에 올라갑니다.</li>
<li>C 4: 4번 주문의 남은 2주를 취소합니다.</li>
</ol>
<p>총 체결 8주, 대금 803원, 남은 수량은 없습니다.</p>
<p><b>입출력 예 #2</b><br>매수 495원 7주는 매도 490원과 5주 체결(2,450원)합니다. 매도 500원은 495원보다 비싸서 체결하지 않고, 남은 2주가 매수로 올라갑니다. C 1과 C 3으로 1번 매도와 3번 매수의 남은 수량이 취소되고, 마지막 매수 1주는 상대 주문이 없어 그대로 남습니다.</p>
''',
    'explanation': '''
<p>매수 호가는 최고가, 매도 호가는 최저가를 빠르게 꺼내야 하므로 <b>힙</b> 두 개를 씁니다.</p>
<ul>
<li>매도 힙: <code>(가격, 주문번호)</code> → 가장 싸고 먼저 들어온 주문이 위에 옵니다.</li>
<li>매수 힙: <code>(-가격, 주문번호)</code> → 가장 비싸고 먼저 들어온 주문이 위에 옵니다.</li>
<li>남은 수량은 배열 <code>remain[주문번호]</code>에 따로 둡니다.</li>
</ul>
<p>취소는 힙 중간에서 원소를 지우기 어려우므로 <code>remain</code>만 0으로 만들고, 힙에서 꺼낼 때 남은 수량이 0인 주문을 건너뜁니다(<b>지연 삭제</b>). 주문마다 힙 연산이 O(log n)이므로 전체 O(n log n)입니다. 매번 호가창 리스트에서 최고가를 찾으면 O(n²)이라 시간 초과가 납니다.</p>
''',
    'edgeCases': [
        '체결 가격은 새 주문이 아니라 먼저 있던 주문의 가격입니다.',
        '가격이 같으면 먼저 들어온 주문부터 체결해야, 이후 취소 결과가 맞습니다.',
        '이미 다 체결된 주문이나 취소 주문을 가리키는 취소는 무시합니다.',
        '취소된 주문이 힙에 남아 있으므로 꺼낼 때 건너뛰어야 합니다.',
        '체결 대금 합계는 long이 필요합니다(Java·C++).',
    ],
}

SOLUTION = '''
import heapq

def solution(orders):
    n = len(orders)
    remain = [0] * (n + 1)
    side = [''] * (n + 1)
    bids, asks = [], []          # bids: (-가격, 번호), asks: (가격, 번호)
    total_qty = total_amount = 0

    for no, order in enumerate(orders, 1):
        parts = order.split()
        if parts[0] == 'C':
            remain[int(parts[1])] = 0
            continue
        price, qty = int(parts[1]), int(parts[2])
        side[no] = parts[0]
        book = asks if parts[0] == 'B' else bids
        while qty and book:
            key, other = book[0]
            if remain[other] == 0:          # 취소되었거나 다 체결된 주문
                heapq.heappop(book)
                continue
            other_price = key if parts[0] == 'B' else -key
            if (parts[0] == 'B' and other_price > price) or (parts[0] == 'S' and other_price < price):
                break
            q = min(qty, remain[other])
            total_qty += q
            total_amount += q * other_price
            qty -= q
            remain[other] -= q
            if remain[other] == 0:
                heapq.heappop(book)
        if qty:
            remain[no] = qty
            if parts[0] == 'B':
                heapq.heappush(bids, (-price, no))
            else:
                heapq.heappush(asks, (price, no))

    buy_left = sum(remain[i] for i in range(1, n + 1) if side[i] == 'B')
    sell_left = sum(remain[i] for i in range(1, n + 1) if side[i] == 'S')
    return [total_qty, total_amount, buy_left, sell_left]
'''

BRUTE = '''
def solution(orders):
    book = []    # [주문번호, 종류, 가격, 남은 수량]
    tq = ta = 0
    for no, o in enumerate(orders, 1):
        p = o.split()
        if p[0] == 'C':
            for e in book:
                if e[0] == int(p[1]):
                    e[3] = 0
            book = [e for e in book if e[3] > 0]
            continue
        price, qty = int(p[1]), int(p[2])
        while qty:
            if p[0] == 'B':
                cand = [e for e in book if e[1] == 'S' and e[2] <= price]
                if not cand:
                    break
                best = min(cand, key=lambda e: (e[2], e[0]))
            else:
                cand = [e for e in book if e[1] == 'B' and e[2] >= price]
                if not cand:
                    break
                best = min(cand, key=lambda e: (-e[2], e[0]))
            q = min(qty, best[3])
            tq += q
            ta += q * best[2]
            qty -= q
            best[3] -= q
            book = [e for e in book if e[3] > 0]
        if qty:
            book.append([no, p[0], price, qty])
    return [tq, ta, sum(e[3] for e in book if e[1] == 'B'), sum(e[3] for e in book if e[1] == 'S')]
'''

WRONG = {
    '새 주문 가격으로 체결': SOLUTION.replace('total_amount += q * other_price', 'total_amount += q * price'),
    '같은 가격이면 나중 주문 먼저': SOLUTION.replace('(-price, no)', '(-price, -no)').replace('(price, no)', '(price, -no)')
                                         .replace('key, other = book[0]', 'key, other = book[0]\n            other = abs(other)'),
    '호가창 리스트 선형 탐색 O(n²)': BRUTE,
}


def examples():
    return [
        ((["B 100 5", "B 101 3", "S 100 6", "S 99 4", "C 4"],), [8, 803, 0, 0]),
        ((["S 500 10", "S 490 5", "B 495 7", "C 1", "C 3", "B 600 1"],), [5, 2450, 1, 0]),
    ]


def handmade():
    return [
        (["B 10 1"],),
        (["S 10 5", "C 1", "C 1", "B 20 5"],),
        (["B 10 2", "B 10 3", "S 10 2", "C 1", "S 9 10"],),          # 시간 우선: 1번이 먼저 다 체결
        (["B 10 2", "B 10 3", "S 10 2", "C 2", "S 9 10"],),
        (["S 7 1", "S 5 1", "S 6 1", "B 100 3"],),                  # 5, 6, 7 순서로 체결
        (["B 1000000 10000", "S 1 10000", "C 2", "C 1"],),
        (["S 10 5", "B 9 5", "C 3", "B 10 2", "C 1", "B 10 9"],),
    ]


def small(rng):
    orders = []
    for _ in range(rng.randint(1, 12)):
        if orders and rng.random() < 0.25:
            orders.append('C %d' % rng.randint(1, len(orders)))
        else:
            orders.append('%s %d %d' % (rng.choice('BS'), rng.randint(5, 9), rng.randint(1, 4)))
    return (orders,)


N_SMALL = 8


def large(rng):
    # 먼저 매수 5만 건을 쌓아 두면 선형 탐색 풀이는 매도 주문마다 5만 개를 훑는다
    a = ['B %d %d' % (rng.randint(1, 500000), rng.randint(1, 10000)) for _ in range(50000)]
    a += ['S %d %d' % (rng.randint(1, 1000000), rng.randint(1, 100)) for _ in range(50000)]
    b = []
    for k in range(100000):
        if k and rng.random() < 0.2:
            b.append('C %d' % rng.randint(1, k))
        else:
            b.append('%s %d %d' % (rng.choice('BS'), rng.randint(990, 1010), rng.randint(1, 10000)))
    return [(a,), (b,)]
