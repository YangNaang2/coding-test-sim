META = {
    'id': 'A09',
    'title': '수익률 랭킹',
    'level': 2,
    'tags': ['정렬', '해시', '문자열'],
    'params': [{'name': 'records', 'type': 'string[]'}, {'name': 'k', 'type': 'int'}],
    'returnType': 'string[]',
    'description': '''
<p>모의투자 대회의 매매 기록 <code>records</code>가 주어집니다. 각 기록은 <code>"이름 매수가 매도가 수량"</code> 형식으로, 한 종목을 매수가에 사서 매도가에 판 거래 하나를 뜻합니다. 한 참가자가 여러 번 거래할 수 있습니다.</p>
<p>참가자마다 모든 거래를 합쳐 다음 값을 계산합니다.</p>
<ul>
<li>매수 금액 = Σ(매수가 × 수량), 매도 금액 = Σ(매도가 × 수량)</li>
<li>수익 = 매도 금액 − 매수 금액</li>
<li>수익률 = 수익 ÷ 매수 금액</li>
</ul>
<p>참가자를 <b>수익률이 높은 순</b>, 수익률이 같으면 <b>수익이 큰 순</b>, 그것도 같으면 <b>이름 사전 순</b>으로 정렬해, 앞에서부터 <code>k</code>명의 이름을 return 하도록 solution 함수를 완성해 주세요. 참가자가 k명보다 적으면 모두 return 합니다.</p>
''',
    'constraints': [
        'records의 길이는 1 이상 100,000 이하입니다.',
        '이름은 영어 소문자로 이루어진 길이 1 이상 10 이하의 문자열입니다.',
        '매수가, 매도가는 1 이상 1,000,000 이하, 수량은 1 이상 10,000 이하의 정수입니다.',
        'k는 1 이상 100,000 이하의 정수입니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b><br>kim(수익 2,000, 수익률 0.2), lee(2,000, 0.2), park(−1,000, −0.2), choi(3,000, 0.1)입니다. kim과 lee는 수익률과 수익이 모두 같아 이름 순으로 kim이 앞섭니다. 상위 3명은 kim, lee, choi입니다.</p>
<p><b>입출력 예 #2</b><br>a는 두 거래를 합치면 매수 400, 매도 400으로 수익률 0입니다. b는 수익률 0.2입니다. 참가자가 2명이라 둘 다 return 합니다.</p>
''',
    'explanation': '''
<p>이름별로 매수 금액과 매도 금액을 dict에 누적한 뒤 정렬합니다.</p>
<p>수익률은 분수라서 실수로 나누면 아주 가까운 두 값의 비교가 틀어질 수 있습니다. 비교 함수에서 <code>p1 / b1 &gt; p2 / b2</code>를 <code>p1 × b2 &gt; p2 × b1</code>로 바꿔 정수끼리 비교하거나, Python에서는 <code>fractions.Fraction</code>을 정렬 키로 쓰면 안전합니다.</p>
<p>거래 기록 하나만 보고 순위를 매기거나, dict에 마지막 거래만 덮어쓰는 실수가 흔합니다.</p>
''',
    'edgeCases': [
        '같은 이름의 거래를 모두 합쳐야 합니다.',
        '수익률과 수익이 모두 같으면 이름 순입니다.',
        'k가 참가자 수보다 클 수 있습니다.',
        '손실(음수 수익률)도 순위에 들어갑니다.',
    ],
}

SOLUTION = '''
from fractions import Fraction

def solution(records, k):
    buy, sell = {}, {}
    for rec in records:
        name, b, s, q = rec.split()
        b, s, q = int(b), int(s), int(q)
        buy[name] = buy.get(name, 0) + b * q
        sell[name] = sell.get(name, 0) + s * q

    def key(name):
        profit = sell[name] - buy[name]
        return (-Fraction(profit, buy[name]), -profit, name)

    return sorted(buy, key=key)[:k]
'''

BRUTE = '''
from functools import cmp_to_key
def solution(records, k):
    names = sorted(set(r.split()[0] for r in records))
    stat = []
    for n in names:
        B = S = 0
        for r in records:
            a, b, s, q = r.split()
            if a == n:
                B += int(b) * int(q)
                S += int(s) * int(q)
        stat.append((n, S - B, B))
    def cmp(x, y):
        l, r = x[1] * y[2], y[1] * x[2]
        if l != r:
            return -1 if l > r else 1
        if x[1] != y[1]:
            return -1 if x[1] > y[1] else 1
        return -1 if x[0] < y[0] else (1 if x[0] > y[0] else 0)
    stat.sort(key=cmp_to_key(cmp))
    return [s[0] for s in stat[:k]]
'''

WRONG = {
    '마지막 거래로 덮어쓰기': '''
def solution(records, k):
    st = {}
    for r in records:
        n, b, s, q = r.split()
        st[n] = (int(b) * int(q), int(s) * int(q))
    return sorted(st, key=lambda n: (-(st[n][1] - st[n][0]) / st[n][0], -(st[n][1] - st[n][0]), n))[:k]
''',
    '수익 비교 누락': '''
def solution(records, k):
    B, S = {}, {}
    for r in records:
        n, b, s, q = r.split()
        B[n] = B.get(n, 0) + int(b) * int(q)
        S[n] = S.get(n, 0) + int(s) * int(q)
    return sorted(B, key=lambda n: (-(S[n] - B[n]) / B[n], n))[:k]
''',
    '이름 비교 누락': '''
def solution(records, k):
    B, S = {}, {}
    for r in records:
        n, b, s, q = r.split()
        B[n] = B.get(n, 0) + int(b) * int(q)
        S[n] = S.get(n, 0) + int(s) * int(q)
    return sorted(B, key=lambda n: (-(S[n] - B[n]) / B[n], -(S[n] - B[n])))[:k]
''',
}


def examples():
    return [
        ((["kim 1000 1200 10", "lee 2000 2400 5", "park 500 400 10", "choi 1000 1100 30"], 3), ["kim", "lee", "choi"]),
        ((["a 100 150 2", "b 100 120 10", "a 200 100 1"], 5), ["b", "a"]),
    ]


def handmade():
    return [
        (["z 100 110 1", "y 100 110 1", "x 1000 1100 1"], 3),       # 수익률 같고 수익 다름 → x, 그다음 y, z
        (["solo 5 5 5"], 100000),
        (["m 10 20 1", "m 20 10 1", "n 1 1 1"], 2),                  # m 합치면 수익률 0, n도 0 → 수익 같음 → 이름
        (["q 3 4 1", "w 6 8 1", "e 300 400 1", "r 1 1 1"], 2),       # 수익률 1/3 동점, 수익 큰 e 먼저
        (["dd 7 1 3", "cc 7 1 3", "bb 1 7 3"], 3),
        (["b 999999 1000000 10000", "a 999998 999999 10000", "c 1 2 1"], 3),
    ]


def small(rng):
    names = ['an', 'bo', 'cy', 'di', 'ed']
    recs = ['%s %d %d %d' % (rng.choice(names), rng.randint(1, 6), rng.randint(1, 6), rng.randint(1, 3))
            for _ in range(rng.randint(1, 10))]
    return (recs, rng.randint(1, 6))


N_SMALL = 7


def large(rng):
    letters = 'abcdefghij'
    names = [''.join(rng.choice(letters) for _ in range(rng.randint(1, 6))) for _ in range(30000)]
    recs = ['%s %d %d %d' % (rng.choice(names), rng.randint(1, 1000000), rng.randint(1, 1000000), rng.randint(1, 10000))
            for _ in range(100000)]
    return [(recs, 500), (recs[:50000], 100000)]
