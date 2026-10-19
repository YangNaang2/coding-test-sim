META = {
    'id': 'A02',
    'title': '수수료와 세금',
    'level': 1,
    'tags': ['구현', '수학', '정수 연산'],
    'params': [{'name': 'trades', 'type': 'int[][]'}],
    'returnType': 'long[]',
    'description': '''
<p>하루 동안의 거래 내역 <code>trades</code>가 주어집니다. 각 거래는 <code>[가격, 수량, 구분]</code>이며, 구분이 0이면 매수, 1이면 매도입니다. 거래마다 거래대금(가격 × 수량)을 기준으로 다음과 같이 비용을 계산합니다.</p>
<ul>
<li><b>수수료</b>: 매수·매도 모두 거래대금의 0.015%를 받으며, 원 단위 미만은 버립니다. 이렇게 계산한 수수료가 10원보다 적으면 10원을 받습니다.</li>
<li><b>거래세</b>: 매도할 때만 거래대금의 0.18%를 받으며, 원 단위 미만은 버립니다. 최소 금액은 없습니다.</li>
</ul>
<p>수수료와 거래세는 <b>거래마다 따로</b> 계산해서 더합니다. 하루 동안의 <code>[총 수수료, 총 거래세]</code>를 return 하도록 solution 함수를 완성해 주세요.</p>
''',
    'constraints': [
        'trades의 길이는 1 이상 100,000 이하입니다.',
        '가격은 1 이상 1,000,000 이하, 수량은 1 이상 10,000 이하의 정수입니다.',
        '구분은 0 또는 1입니다.',
        '결과는 32비트 정수 범위를 넘을 수 있습니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b><br>매수 거래대금 700,000원의 수수료는 105원입니다. 매도 거래대금 710,000원의 수수료는 106.5원에서 원 미만을 버린 106원, 거래세는 1,278원입니다. 따라서 [211, 1278]입니다.</p>
<p><b>입출력 예 #2</b><br>매도 거래대금 3,000원의 수수료는 0.45원 → 0원이지만 최소 10원이고, 거래세는 5.4원 → 5원입니다. 매수 거래대금 55,500원의 수수료는 8.325원 → 8원이지만 최소 10원입니다. 따라서 [20, 5]입니다.</p>
''',
    'explanation': '''
<p>계산 자체는 단순하지만 두 군데에서 틀리기 쉽습니다.</p>
<ul>
<li><b>실수 오차</b>: <code>int(amount * 0.00015)</code>처럼 실수로 곱하면 0.00015를 이진수로 정확히 표현하지 못해서, 결과가 정수에 딱 떨어지는 거래대금에서 1원 적게 나올 수 있습니다. <code>amount * 15 // 100000</code>처럼 <b>정수 연산</b>으로 계산하세요.</li>
<li><b>합산 시점</b>: 거래대금을 다 더한 뒤 한 번에 계산하면 원 미만 절사와 최소 수수료가 거래마다 적용되지 않아 답이 달라집니다.</li>
</ul>
<p>Java·C++에서는 거래대금(최대 10<sup>10</sup>)과 합계가 int 범위를 넘으므로 long / long long을 써야 합니다.</p>
''',
    'edgeCases': [
        '실수 곱셈 후 절사하면 정확히 정수로 떨어지는 경우에 1원 차이가 납니다.',
        '최소 수수료 10원은 수수료에만 적용되고 거래세에는 적용되지 않습니다.',
        '매수에는 거래세가 없습니다.',
        '전체 합계를 먼저 구하고 계산하면 틀립니다.',
    ],
}

SOLUTION = '''
def solution(trades):
    fee_total = 0
    tax_total = 0
    for price, qty, side in trades:
        amount = price * qty
        fee_total += max(10, amount * 15 // 100000)
        if side == 1:
            tax_total += amount * 18 // 10000
    return [fee_total, tax_total]
'''

BRUTE = '''
from fractions import Fraction
import math
def solution(trades):
    fee = tax = 0
    for p, q, s in trades:
        a = Fraction(p * q)
        fee += max(10, math.floor(a * Fraction(15, 100000)))
        if s:
            tax += math.floor(a * Fraction(18, 10000))
    return [fee, tax]
'''

WRONG = {
    '실수 곱셈': '''
def solution(trades):
    fee = tax = 0
    for p, q, s in trades:
        a = p * q
        fee += max(10, int(a * 0.00015))
        if s == 1:
            tax += int(a * 0.0018)
    return [fee, tax]
''',
    '합계 후 계산': '''
def solution(trades):
    total = sum(p * q for p, q, s in trades)
    sell = sum(p * q for p, q, s in trades if s == 1)
    return [max(10, total * 15 // 100000), sell * 18 // 10000]
''',
    '최소 수수료 누락': '''
def solution(trades):
    fee = tax = 0
    for p, q, s in trades:
        a = p * q
        fee += a * 15 // 100000
        if s == 1:
            tax += a * 18 // 10000
    return [fee, tax]
''',
}


def examples():
    return [
        (([[70000, 10, 0], [71000, 10, 1]],), [211, 1278]),
        (([[1000, 3, 1], [55500, 1, 0]],), [20, 5]),
    ]


def float_traps(limit=40):
    """실수 곱셈으로 계산하면 정수 연산과 결과가 달라지는 (가격, 수량) 조합을 찾는다."""
    found = []
    for price in range(1000, 1000001, 997):
        for qty in (1, 2, 3, 5, 7, 10, 20, 100):
            a = price * qty
            if int(a * 0.00015) != a * 15 // 100000 or int(a * 0.0018) != a * 18 // 10000:
                found.append([price, qty, 1])
                if len(found) >= limit:
                    return found
    return found


def handmade():
    traps = float_traps()
    return [
        (traps[:10],),
        (traps[10:40],),
        ([[1, 1, 0]],),                          # 최소 수수료만
        ([[1, 1, 1], [1, 1, 1], [1, 1, 1]],),    # 수수료 10원씩, 세금 0
        ([[1000000, 10000, 1]],),                # 최대 금액 한 건
        ([[66667, 1, 0], [66667, 1, 0]],),       # 수수료 10.00005 → 10원씩
    ]


def small(rng):
    return ([[rng.randint(1, 200000), rng.randint(1, 50), rng.randint(0, 1)] for _ in range(rng.randint(1, 12))],)


def large(rng):
    traps = float_traps(200)
    big = [[rng.randint(1, 1000000), rng.randint(1, 10000), rng.randint(0, 1)] for _ in range(100000 - len(traps))]
    big[5000:5000] = traps
    return [(big,)]
