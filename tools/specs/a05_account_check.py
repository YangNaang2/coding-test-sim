META = {
    'id': 'A05',
    'title': '계좌번호 검증',
    'level': 1,
    'tags': ['문자열', '해시', '구현'],
    'params': [{'name': 'accounts', 'type': 'string[]'}],
    'returnType': 'string[]',
    'description': '''
<p>고객이 입력한 계좌번호 목록 <code>accounts</code>에서 올바른 계좌번호만 골라내려고 합니다. 계좌번호는 숫자 11자리이며, 아래 조건을 <b>모두</b> 만족해야 올바른 계좌번호입니다.</p>
<ol>
<li><b>형식</b>: 하이픈 없이 숫자 11자리(<code>"12345678906"</code>)이거나, 숫자 3자리·2자리·6자리를 하이픈으로 이은 형태(<code>"123-45-678906"</code>)여야 합니다. 그 밖의 문자나 다른 위치의 하이픈이 있으면 올바르지 않습니다.</li>
<li><b>지점 번호</b>: 앞 3자리가 <code>"000"</code>이면 올바르지 않습니다.</li>
<li><b>검증 숫자</b>: 앞 10자리 숫자에 차례로 가중치 2, 3, 4, 5, 6, 7, 8, 9, 2, 3을 곱해 더한 값을 S라고 할 때, 마지막 자리 숫자는 <code>(11 − S % 11) % 10</code>과 같아야 합니다.</li>
</ol>
<p>올바른 계좌번호를 <code>"XXX-XX-XXXXXX"</code> 형태로 바꿔, 처음 나온 순서대로 담은 배열을 return 하도록 solution 함수를 완성해 주세요. 하이픈 유무와 상관없이 숫자 11자리가 같으면 같은 계좌이므로 한 번만 담습니다. 올바른 계좌번호가 없으면 빈 배열을 return 합니다.</p>
''',
    'constraints': [
        'accounts의 길이는 1 이상 10,000 이하입니다.',
        'accounts의 원소는 길이 1 이상 20 이하이며, 숫자·하이픈(-)·영어 알파벳·공백으로 이루어져 있습니다.',
    ],
    'exampleNotes': '''
<p><b>입출력 예 #1</b><br>"123-45-678906": S = 1×2 + 2×3 + 3×4 + 4×5 + 5×6 + 6×7 + 7×8 + 8×9 + 9×2 + 0×3 = 258, 258 % 11 = 5, (11 − 5) % 10 = 6이 마지막 자리와 같으므로 올바릅니다. "12345678906"은 같은 계좌라 다시 담지 않습니다. "123-45-678905"는 검증 숫자가 다르고, "000-12-345672"는 지점 번호가 000이며, "12-345-678906"은 하이픈 위치가 틀렸습니다.</p>
<p><b>입출력 예 #2</b><br>"110-23-456785"와 "987-65-432107"은 올바릅니다. "98765432107"은 두 번째 계좌와 같습니다. 알파벳이나 공백이 들어간 문자열은 형식이 틀렸습니다.</p>
''',
    'explanation': '''
<p>각 문자열을 다음 순서로 검사합니다.</p>
<ol>
<li>길이 11이면 모두 숫자인지, 길이 13이면 4번째·7번째 문자만 하이픈이고 나머지가 숫자인지 확인합니다. 하이픈을 전부 지운 뒤 길이만 보면 <code>"12-345-678906"</code> 같은 잘못된 형식을 통과시킵니다.</li>
<li>숫자 11자리로 정규화한 뒤 지점 번호와 검증 숫자를 확인합니다.</li>
<li>정규화한 문자열을 <b>set</b>에 넣어 중복을 거릅니다. 원래 문자열로 중복을 거르면 하이픈 유무만 다른 같은 계좌가 두 번 들어갑니다.</li>
</ol>
<p>Python의 <code>str.isdigit()</code>은 '²' 같은 문자도 숫자로 보므로, 문자 하나하나를 <code>'0' &lt;= c &lt;= '9'</code>로 비교하는 편이 안전합니다.</p>
''',
    'edgeCases': [
        '하이픈 위치가 다른 문자열(예: "12-345-678906")은 형식이 틀렸습니다.',
        '하이픈 유무만 다른 같은 계좌는 한 번만 담습니다.',
        '(11 − S % 11) % 10에서 S % 11이 0이면 검증 숫자는 1, 1이면 0입니다.',
        '공백이나 알파벳이 섞인 문자열은 형식이 틀렸습니다.',
    ],
}

SOLUTION = '''
WEIGHTS = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3]

def normalize(s):
    if len(s) == 11:
        digits = s
    elif len(s) == 13 and s[3] == '-' and s[6] == '-':
        digits = s[:3] + s[4:6] + s[7:]
    else:
        return None
    if not all('0' <= c <= '9' for c in digits):
        return None
    return digits

def solution(accounts):
    seen = set()
    answer = []
    for s in accounts:
        d = normalize(s)
        if d is None or d[:3] == '000':
            continue
        total = sum(int(c) * w for c, w in zip(d, WEIGHTS))
        if int(d[10]) != (11 - total % 11) % 10:
            continue
        if d in seen:
            continue
        seen.add(d)
        answer.append(d[:3] + '-' + d[3:5] + '-' + d[5:])
    return answer
'''

BRUTE = '''
import re
def solution(accounts):
    out = []
    for s in accounts:
        m = re.fullmatch(r'([0-9]{3})-?([0-9]{2})-?([0-9]{6})', s)
        if not m or (('-' in s) and s.count('-') != 2):
            continue
        d = ''.join(m.groups())
        if d.startswith('000'):
            continue
        S = sum(int(d[k]) * [2, 3, 4, 5, 6, 7, 8, 9, 2, 3][k] for k in range(10))
        if (11 - S % 11) % 10 != int(d[10]):
            continue
        f = d[:3] + '-' + d[3:5] + '-' + d[5:]
        if f not in out:
            out.append(f)
    return out
'''

WRONG = {
    '하이픈을 모두 지우고 길이만 확인': '''
W = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3]
def solution(accounts):
    seen, out = set(), []
    for s in accounts:
        d = s.replace('-', '')
        if len(d) != 11 or not all('0' <= c <= '9' for c in d) or d[:3] == '000':
            continue
        if int(d[10]) != (11 - sum(int(c) * w for c, w in zip(d, W)) % 11) % 10:
            continue
        if d not in seen:
            seen.add(d)
            out.append(d[:3] + '-' + d[3:5] + '-' + d[5:])
    return out
''',
    '원래 문자열로 중복 제거': '''
W = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3]
def solution(accounts):
    seen, out = set(), []
    for s in accounts:
        if len(s) == 11:
            d = s
        elif len(s) == 13 and s[3] == '-' and s[6] == '-':
            d = s[:3] + s[4:6] + s[7:]
        else:
            continue
        if not all('0' <= c <= '9' for c in d) or d[:3] == '000':
            continue
        if int(d[10]) != (11 - sum(int(c) * w for c, w in zip(d, W)) % 11) % 10:
            continue
        if s not in seen:
            seen.add(s)
            out.append(d[:3] + '-' + d[3:5] + '-' + d[5:])
    return out
''',
    '검증 숫자에서 % 10 누락': '''
W = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3]
def solution(accounts):
    seen, out = set(), []
    for s in accounts:
        if len(s) == 11:
            d = s
        elif len(s) == 13 and s[3] == '-' and s[6] == '-':
            d = s[:3] + s[4:6] + s[7:]
        else:
            continue
        if not all('0' <= c <= '9' for c in d) or d[:3] == '000':
            continue
        if int(d[10]) != 11 - sum(int(c) * w for c, w in zip(d, W)) % 11:
            continue
        if d not in seen:
            seen.add(d)
            out.append(d[:3] + '-' + d[3:5] + '-' + d[5:])
    return out
''',
}

W = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3]


def check_digit(d10):
    return (11 - sum(int(c) * w for c, w in zip(d10, W)) % 11) % 10


def valid_number(rng, check_mod=None):
    while True:
        d = '%03d' % rng.randint(1, 999) + ''.join(rng.choice('0123456789') for _ in range(7))
        s = sum(int(c) * w for c, w in zip(d, W)) % 11
        if check_mod is None or s == check_mod:
            return d + str(check_digit(d))


def fmt(d, hyphen):
    return d[:3] + '-' + d[3:5] + '-' + d[5:] if hyphen else d


def examples():
    return [
        ((["123-45-678906", "12345678906", "123-45-678905", "000-12-345672", "12-345-678906"],), ["123-45-678906"]),
        ((["110-23-456785", "987-65-432107", "98765432107", "abc-de-fghijk", "110 23 456785"],),
         ["110-23-456785", "987-65-432107"]),
    ]


def handmade():
    import random
    rng = random.Random(5)
    a = valid_number(rng, 0)   # 검증 숫자 1
    b = valid_number(rng, 1)   # 검증 숫자 0
    c = valid_number(rng)
    return [
        ([fmt(a, True), fmt(b, False), fmt(a, False)],),
        ([c[:2] + '-' + c[2:5] + '-' + c[5:], c[:3] + '-' + c[3:9] + '-' + c[9:], c[:3] + '--' + c[3:]],),
        ([fmt(c, True) + ' ', ' ' + fmt(c, False), fmt(c, True)],),
        (['000' + '1234567' + check_digit('0001234567').__str__()],),
        ([fmt(b, True)] * 3 + [fmt(b, False)] * 3,),
        (['-' * 13, '1' * 11, '-' * 11],),
    ]


def small(rng):
    out = []
    for _ in range(rng.randint(1, 8)):
        d = valid_number(rng)
        r = rng.random()
        if r < 0.15:
            d = d[:10] + str((int(d[10]) + 1) % 10)
        elif r < 0.25:
            d = '000' + d[3:]
        s = fmt(d, rng.random() < 0.5)
        if rng.random() < 0.1:
            k = rng.randrange(len(s))
            s = s[:k] + rng.choice('a -') + s[k + 1:]
        out.append(s)
        if rng.random() < 0.3:
            out.append(fmt(d, rng.random() < 0.5))
    return (out,)


N_SMALL = 7


def large(rng):
    pool = [valid_number(rng) for _ in range(3000)]
    out = []
    for _ in range(10000):
        d = rng.choice(pool)
        if rng.random() < 0.2:
            d = d[:10] + str((int(d[10]) + 3) % 10)
        out.append(fmt(d, rng.random() < 0.5))
    return [(out,)]
