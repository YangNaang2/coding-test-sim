import _sqlworld as w

META = {
    'id': 'S07',
    'title': '회원 등급 산정',
    'level': 2,
    'tags': ['LEFT JOIN', 'CASE', 'COALESCE', 'GROUP BY'],
    'ordered': True,
    'description': '''
<p>모든 회원의 등급을 산정하려 합니다. 회원별로 <b>해지되지 않은</b>(<code>STATUS</code>가 <code>'CLOSED'</code>가 아닌) 계좌의 잔고(<code>BALANCE</code>) 합계를 구하고, 다음 기준으로 등급을 매깁니다.</p>
<ul>
<li>합계가 100,000,000원 이상: <code>'VIP'</code></li>
<li>합계가 10,000,000원 이상: <code>'GOLD'</code></li>
<li>그 외: <code>'BASIC'</code></li>
</ul>
<p>계좌가 없거나, 해지된 계좌만 가진 회원도 합계 0원, <code>'BASIC'</code>으로 <b>반드시 포함</b>합니다.</p>
<p><code>USERS</code>와 <code>ACCOUNTS</code> 테이블에서 회원 ID(<code>USER_ID</code>), 이름(<code>NAME</code>), 잔고 합계(<code>TOTAL_BALANCE</code>), 등급(<code>TIER</code>)을 조회하는 SQL 문을 작성해 주세요. 결과는 회원 ID 오름차순으로 정렬해 주세요.</p>
''',
    'explanation': '''
<ul>
<li>모든 회원을 남기려면 <code>USERS LEFT JOIN ACCOUNTS</code>입니다.</li>
<li><b>함정</b>: 계좌 상태 조건을 WHERE에 두면(<code>WHERE A.STATUS &lt;&gt; 'CLOSED'</code>), 계좌가 없는 회원은 A.STATUS가 NULL이라 걸러지고 해지 계좌만 가진 회원도 사라집니다. LEFT JOIN의 오른쪽 테이블 조건은 <b>ON 절</b>에 넣어야 합니다.</li>
<li>매칭되는 계좌가 없으면 <code>SUM(A.BALANCE)</code>가 NULL이므로 <code>COALESCE(SUM(A.BALANCE), 0)</code>로 바꿉니다.</li>
<li>CASE는 위에서부터 판단하므로 큰 기준(VIP)을 먼저 씁니다. "이상"이므로 <code>&gt;=</code>입니다.</li>
</ul>
''',
}

SCHEMA = [w.USERS, w.ACCOUNTS]


def sample():
    return {
        'USERS': [[1, '김민준', '서울', '2020-03-01'], [2, '이서연', None, '2021-07-15'],
                  [3, '박도윤', '부산', '2019-11-30'], [4, '최하은', '대구', '2022-01-05'], [5, '정지호', '인천', '2023-03-03']],
        'ACCOUNTS': [
            [1001, 1, 'ACTIVE', 80000000, '2020-03-01'],
            [1002, 1, 'DORMANT', 20000000, '2021-01-01'],
            [1003, 2, 'ACTIVE', 10000000, '2021-07-15'],
            [1004, 3, 'CLOSED', 500000000, '2019-11-30'],
            [1005, 3, 'ACTIVE', 9999999, '2020-02-02'],
            [1006, 5, 'CLOSED', 30000, '2023-03-03'],
        ],
    }


def hidden(rng):
    users = w.users(rng, 300)
    accounts = w.accounts(rng, users[:260])
    aid = 8000
    # 경계값과 해지 계좌만 가진 회원
    for u, bals in zip(users[260:275], [[100000000], [99999999, 1], [10000000], [9999999], [50000000, 50000000]] * 3):
        for b in bals:
            accounts.append([aid, u[0], 'ACTIVE', b, '2024-01-01'])
            aid += 1
    for u in users[275:290]:
        accounts.append([aid, u[0], 'CLOSED', rng.randint(10 ** 7, 10 ** 9), '2020-01-01'])
        aid += 1
    rng.shuffle(accounts)
    return {'USERS': users, 'ACCOUNTS': accounts}


SOLUTION = '''
SELECT U.USER_ID,
       U.NAME,
       COALESCE(SUM(A.BALANCE), 0) AS TOTAL_BALANCE,
       CASE
           WHEN COALESCE(SUM(A.BALANCE), 0) >= 100000000 THEN 'VIP'
           WHEN COALESCE(SUM(A.BALANCE), 0) >= 10000000 THEN 'GOLD'
           ELSE 'BASIC'
       END AS TIER
FROM USERS U
LEFT JOIN ACCOUNTS A
       ON U.USER_ID = A.USER_ID
      AND A.STATUS <> 'CLOSED'
GROUP BY U.USER_ID, U.NAME
ORDER BY U.USER_ID;
'''

ALT = [
    "SELECT U.USER_ID, U.NAME, IFNULL(T.S, 0) AS TOTAL_BALANCE, "
    "CASE WHEN IFNULL(T.S, 0) >= 100000000 THEN 'VIP' WHEN IFNULL(T.S, 0) >= 10000000 THEN 'GOLD' ELSE 'BASIC' END AS TIER "
    "FROM USERS U LEFT JOIN (SELECT USER_ID, SUM(BALANCE) AS S FROM ACCOUNTS WHERE STATUS IN ('ACTIVE', 'DORMANT') "
    "GROUP BY USER_ID) T ON U.USER_ID = T.USER_ID ORDER BY U.USER_ID",
    "SELECT U.USER_ID, U.NAME, NVL(SUM(CASE WHEN A.STATUS <> 'CLOSED' THEN A.BALANCE END), 0) TOTAL_BALANCE, "
    "CASE WHEN NVL(SUM(CASE WHEN A.STATUS <> 'CLOSED' THEN A.BALANCE END), 0) >= 100000000 THEN 'VIP' "
    "WHEN NVL(SUM(CASE WHEN A.STATUS <> 'CLOSED' THEN A.BALANCE END), 0) >= 10000000 THEN 'GOLD' ELSE 'BASIC' END TIER "
    "FROM USERS U LEFT JOIN ACCOUNTS A ON U.USER_ID = A.USER_ID GROUP BY U.USER_ID, U.NAME ORDER BY U.USER_ID",
]

WRONG = {
    '상태 조건을 WHERE에': SOLUTION.replace("ON U.USER_ID = A.USER_ID\n      AND A.STATUS <> 'CLOSED'",
                                         "ON U.USER_ID = A.USER_ID").replace(
        'GROUP BY', "WHERE A.STATUS <> 'CLOSED'\nGROUP BY"),
    'COALESCE 누락': SOLUTION.replace('COALESCE(SUM(A.BALANCE), 0) AS TOTAL_BALANCE', 'SUM(A.BALANCE) AS TOTAL_BALANCE'),
    '경계 미포함(>)': SOLUTION.replace('>= 100000000', '> 100000000').replace('>= 10000000', '> 10000000'),
    'INNER JOIN': SOLUTION.replace('LEFT JOIN', 'JOIN'),
}
