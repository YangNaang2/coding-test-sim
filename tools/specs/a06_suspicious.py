META = {
    'id': 'A06',
    'title': '이상 거래 탐지',
    'level': 2,
    'tags': ['해시', '정렬', '문자열', '구현', '후기 유형: 해시+구현'],
    'params': [{'name': 'records', 'type': 'string[]'}, {'name': 'limit', 'type': 'int'}],
    'returnType': 'string[]',
    'description': '''
<p>이상 거래 탐지 시스템이 하루 동안의 이체 기록 <code>records</code>를 검사합니다. 각 기록은 <code>"HH:MM:SS 사용자ID 금액"</code> 형식이며, <b>시각 순서대로 정렬되어 있지 않습니다.</b></p>
<p>다음 중 하나라도 해당하는 사용자를 이상 거래 사용자로 봅니다.</p>
<ol>
<li>금액이 <code>limit</code>원 <b>이상</b>인 이체가 한 번이라도 있다.</li>
<li>같은 사용자의 이체 3건이 짧은 시간에 몰려 있다. 즉 어떤 3건을 시각 순으로 놓았을 때 첫 번째와 세 번째의 시각 차이가 <b>60초 미만</b>이다. 시각이 같은 이체도 각각 한 건으로 셉니다.</li>
</ol>
<p>단, 금액이 0인 기록은 잔액 조회 기록이므로 <b>모든 판단에서 제외</b>합니다.</p>
<p>이상 거래 사용자의 ID를 사전 순으로 정렬해 return 하도록 solution 함수를 완성해 주세요. 해당하는 사용자가 없으면 빈 배열을 return 합니다.</p>
''',
    'constraints': [
        'records의 길이는 1 이상 100,000 이하입니다.',
        '시각은 00:00:00 이상 23:59:59 이하이며 항상 두 자리씩 씁니다.',
        '사용자ID는 영어 소문자와 숫자로 이루어진 길이 1 이상 10 이하의 문자열입니다.',
        '금액은 0 이상 1,000,000,000 이하의 정수입니다.',
        'limit은 1 이상 1,000,000,000 이하의 정수입니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b><br>kim의 이체 시각을 정렬하면 09:00:00, 09:00:10, 09:00:59입니다. 첫 번째와 세 번째의 차이가 59초라서 이상 거래입니다. park은 2,000,000원 이체가 limit 이상이라 이상 거래입니다.</p>
<p><b>입출력 예 #2</b><br>금액 0인 기록을 빼면 a1의 이체 시각은 10:00:00, 10:00:20, 10:01:00입니다. 차이가 정확히 60초라서 이상 거래가 아닙니다.</p>
''',
    'explanation': '''
<ol>
<li>각 기록을 공백으로 나누고 시각을 초 단위 정수 <code>h * 3600 + m * 60 + s</code>로 바꿉니다.</li>
<li>금액이 0이면 건너뜁니다. 금액이 limit 이상이면 바로 표시합니다.</li>
<li>사용자별로 시각을 dict에 모은 뒤 <b>정렬</b>하고, 연속한 3개 <code>t[i]</code>, <code>t[i + 2]</code>의 차이가 60 미만인지 확인합니다. 정렬된 상태에서는 3건이 60초 안에 몰려 있다면 연속한 3개 중에도 반드시 그런 묶음이 있습니다.</li>
</ol>
<p>사용자 전체 이체 수가 n이면 정렬 때문에 O(n log n)입니다. 입력이 시각순이라고 가정하고 정렬을 빠뜨리는 실수가 가장 흔합니다.</p>
''',
    'edgeCases': [
        '입력이 시각순이 아니므로 사용자별로 정렬해야 합니다.',
        '차이가 정확히 60초면 해당하지 않습니다(< 60).',
        '금액 0 기록은 3건 세기에서도 빠집니다.',
        '금액이 limit과 같으면 이상 거래입니다(≥).',
        '같은 시각의 이체 3건도 해당합니다.',
    ],
}

SOLUTION = '''
def solution(records, limit):
    times = {}
    flagged = set()
    for rec in records:
        hms, user, amount = rec.split()
        amount = int(amount)
        if amount == 0:
            continue
        if amount >= limit:
            flagged.add(user)
        h, m, s = map(int, hms.split(':'))
        times.setdefault(user, []).append(h * 3600 + m * 60 + s)
    for user, ts in times.items():
        if user in flagged:
            continue
        ts.sort()
        for i in range(len(ts) - 2):
            if ts[i + 2] - ts[i] < 60:
                flagged.add(user)
                break
    return sorted(flagged)
'''

BRUTE = '''
from itertools import combinations
def solution(records, limit):
    rows = []
    for r in records:
        t, u, a = r.split()
        a = int(a)
        if a == 0:
            continue
        h, m, s = map(int, t.split(':'))
        rows.append((u, h * 3600 + m * 60 + s, a))
    bad = set(u for u, t, a in rows if a >= limit)
    for x, y, z in combinations(rows, 3):
        if x[0] == y[0] == z[0]:
            ts = sorted([x[1], y[1], z[1]])
            if ts[2] - ts[0] < 60:
                bad.add(x[0])
    return sorted(bad)
'''

WRONG = {
    '시각 정렬 누락': '''
def solution(records, limit):
    times, bad = {}, set()
    for r in records:
        t, u, a = r.split()
        a = int(a)
        if a == 0:
            continue
        if a >= limit:
            bad.add(u)
        h, m, s = map(int, t.split(':'))
        times.setdefault(u, []).append(h * 3600 + m * 60 + s)
    for u, ts in times.items():
        for i in range(len(ts) - 2):
            if abs(ts[i + 2] - ts[i]) < 60:
                bad.add(u)
    return sorted(bad)
''',
    '60초 이하로 비교': '''
def solution(records, limit):
    times, bad = {}, set()
    for r in records:
        t, u, a = r.split()
        a = int(a)
        if a == 0:
            continue
        if a >= limit:
            bad.add(u)
        h, m, s = map(int, t.split(':'))
        times.setdefault(u, []).append(h * 3600 + m * 60 + s)
    for u, ts in times.items():
        ts.sort()
        if any(ts[i + 2] - ts[i] <= 60 for i in range(len(ts) - 2)):
            bad.add(u)
    return sorted(bad)
''',
    '금액 0 포함': '''
def solution(records, limit):
    times, bad = {}, set()
    for r in records:
        t, u, a = r.split()
        a = int(a)
        if a >= limit:
            bad.add(u)
        h, m, s = map(int, t.split(':'))
        times.setdefault(u, []).append(h * 3600 + m * 60 + s)
    for u, ts in times.items():
        ts.sort()
        if any(ts[i + 2] - ts[i] < 60 for i in range(len(ts) - 2)):
            bad.add(u)
    return sorted(bad)
''',
    '모든 쌍 비교 O(n²)': '''
def solution(records, limit):
    rows, bad = [], set()
    for r in records:
        t, u, a = r.split()
        a = int(a)
        if a == 0:
            continue
        if a >= limit:
            bad.add(u)
        h, m, s = map(int, t.split(':'))
        rows.append((u, h * 3600 + m * 60 + s))
    for u, t in rows:
        if u in bad:
            continue
        cnt = sum(1 for v, x in rows if v == u and t <= x < t + 60)
        if cnt >= 3:
            bad.add(u)
    return sorted(bad)
''',
}


def examples():
    return [
        ((["09:00:00 kim 5000", "09:00:30 lee 100", "09:00:59 kim 3000", "09:00:10 kim 1000", "09:05:00 park 2000000"], 1000000),
         ["kim", "park"]),
        ((["10:00:00 a1 10", "10:01:00 a1 10", "10:00:30 a1 0", "10:00:20 a1 10"], 100), []),
    ]


def ts(sec):
    return '%02d:%02d:%02d' % (sec // 3600, sec % 3600 // 60, sec % 60)


def handmade():
    return [
        (["12:00:00 x 1", "12:00:00 x 1", "12:00:00 x 1"], 10),          # 같은 시각 3건
        (["00:00:00 y 5", "23:59:59 y 5", "00:00:59 y 5"], 10),          # 정렬하면 0, 59, 86399
        (["08:00:00 z 10", "08:00:59 z 0", "08:00:30 z 10", "08:00:50 z 0"], 100),  # 0 제외하면 2건
        (["01:00:00 big 100"], 100),                                     # limit과 같은 금액
        (["01:00:00 m1 99", "01:00:01 m2 99", "01:00:02 m3 99"], 100),   # 서로 다른 사용자
        (["10:00:00 b 1", "10:00:40 b 1", "10:01:10 b 1", "10:01:39 b 1"], 50),  # 두 번째 묶음에서 59초
    ]


def small(rng):
    users = ['u%d' % k for k in range(3)]
    base = rng.randint(0, 80000)
    recs = []
    for _ in range(rng.randint(1, 9)):
        recs.append('%s %s %d' % (ts(base + rng.randint(0, 150)), rng.choice(users),
                                  rng.choice([0, 0, rng.randint(1, 120)])))
    return (recs, rng.randint(60, 130))


N_SMALL = 7


def large(rng):
    # 한 사용자에게 6만 건을 90초 간격 근처로 몰아 정렬 누락과 O(n²) 풀이를 모두 걸러낸다
    recs = []
    for k in range(60000):
        recs.append('%s heavy %d' % (ts(k * 61 % 86400), rng.randint(1, 1000)))
    for k in range(40000):
        recs.append('%s u%d %d' % (ts(rng.randint(0, 86399)), rng.randint(0, 20000), rng.randint(0, 1000000)))
    rng.shuffle(recs)
    return [(recs, 999999)]
